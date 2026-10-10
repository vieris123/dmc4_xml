"""MT Framework XFS (serialized objects, `XFS\\0` version 5 in DMC4 DX9: .phs / .clt chains, .cam, .rut, .sprmap,
.msse, sound tables ...): byte-exact reader and writer, plain Python.

Layout:
- header 0x10: magic, u16 major, u16 minor, u32 class count, u32 data offset - 0x10; then u32 per class: its layout's
  offset - 0x10
- class layouts: u32 dti, u16 (property count:15, init:1), u16 reserved, then 24 bytes per property: u32 name offset
  (- 0x10), u8 type, u8 attr, u16 (size:15, disable:1), u32 getter, getcount, setter, setcount
- names (NUL-terminated, padded to 4 bytes), then the data at `data offset + 0x10`
- data: one object chunk: u32 (active:1, layout:15, meta:16), u32 size (from this field to the chunk's end), then
  for each layout property a u32 item count and the items: nested chunks for TYPE_CLASS / TYPE_CLASSREF, C strings
  for TYPE_STRING, (u8 flag [, class, path]) for resources, otherwise `size` bytes each.

Untouched files come back byte-identical: the layouts (attr, getters ...), versions, name offsets and each object's
meta bits are kept.
"""
import math
import struct

from .sdl import _Pool, _align

MAGIC = b"XFS\0"
HEADER = struct.Struct("<4sHHII")
LAYOUT = struct.Struct("<IHH")
PROP = struct.Struct("<IBBHIIII")

T_CLASS, T_CLASSREF, T_STRING, T_RESOURCE = 0x1, 0x2, 0xE, 0x3A
OBJECT_TYPES = (T_CLASS, T_CLASSREF)

# fixed-size item decoding (type -> struct format); anything else stays raw bytes
SCALARS = {0x3: "B", 0x4: "B", 0x5: "H", 0x6: "I", 0x7: "Q", 0x8: "b", 0x9: "h", 0xA: "i", 0xB: "q", 0xC: "f",
           0xD: "d"}
INT_RECORDS = {0x10: "ii", 0x11: "ii", 0x12: "iiii", 0x36: "ii", 0x38: "HH"}   # point, size, rect, range, rangeU16
FLOAT_VECTORS = {0x0F, 0x13, 0x14, 0x15, 0x16, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x29, 0x2A, 0x2B, 0x2C,
                 0x2D, 0x2E, 0x2F, 0x30, 0x31, 0x37}


class XfsError(ValueError):
    pass


class Prop:
    __slots__ = ("name", "type", "attr", "size", "disable", "getter", "getcount", "setter", "setcount", "name_ofs",
                 "encoding")

    def __init__(self, name, type, size, attr=0, disable=0, getter=0, getcount=0, setter=0, setcount=0,
                 name_ofs=None, encoding="utf-8"):
        self.name, self.type, self.size, self.attr, self.disable = name, type, size, attr, disable
        self.getter, self.getcount, self.setter, self.setcount = getter, getcount, setter, setcount
        self.name_ofs, self.encoding = name_ofs, encoding

    def key(self):
        return (self.name, self.type)


class Layout:
    __slots__ = ("dti", "props", "init", "reserved")

    def __init__(self, dti, props=None, init=0, reserved=0):
        self.dti, self.props, self.init, self.reserved = dti, props if props is not None else [], init, reserved


class Obj:
    """One serialized object: its layout (index into Xfs.layouts), meta bits and one list of items per layout
    property. Items: Obj (or None) for object properties, str / None for strings, (flag, class, path) for resources,
    bytes for everything else (decode with item_value / encode with item_bytes)."""
    __slots__ = ("layout", "active", "meta", "values")

    def __init__(self, layout, values=None, active=1, meta=0):
        self.layout, self.active, self.meta = layout, active, meta
        self.values = values if values is not None else []


class Xfs:
    def __init__(self, layouts=None, root=None, major=5, minor=0):
        self.layouts = layouts if layouts is not None else []
        self.root, self.major, self.minor = root, major, minor


def _cstring(data, pos):
    end = data.index(b"\0", pos)
    raw = data[pos:end]
    try:
        return raw.decode("utf-8"), "utf-8", end + 1
    except UnicodeDecodeError:
        return raw.decode("cp932"), "cp932", end + 1


def read(data):
    """bytes -> Xfs"""
    data = bytes(data)
    if data[:4] != MAGIC:
        raise XfsError(f"not an XFS file ({data[:4]!r})")
    magic, major, minor, count, data_ofs = HEADER.unpack_from(data, 0)
    if major not in (5, 6):
        raise XfsError(f"XFS version {major} isn't supported (DMC4 DX9 files are version 5; SE uses 15)")
    positions = struct.unpack_from(f"<{count}I", data, HEADER.size)
    xfs = Xfs(major=major, minor=minor)
    # names start right after the layouts; name offsets are kept relative to that, as string-order hints
    names_at = max((p + 0x10 + 8 + 24 * (LAYOUT.unpack_from(data, p + 0x10)[1] & 0x7FFF) for p in positions),
                   default=HEADER.size)
    for pos in positions:
        at = pos + 0x10
        dti, word, reserved = LAYOUT.unpack_from(data, at)
        layout = Layout(dti, init=word >> 15, reserved=reserved)
        for k in range(word & 0x7FFF):
            name_ofs, ptype, attr, sw, getter, getcount, setter, setcount = PROP.unpack_from(data, at + 8 + 24 * k)
            name, enc, _ = _cstring(data, name_ofs + 0x10)
            layout.props.append(Prop(name, ptype, sw & 0x7FFF, attr, sw >> 15, getter, getcount, setter, setcount,
                                     name_ofs=name_ofs + 0x10 - names_at, encoding=enc))
        xfs.layouts.append(layout)

    def chunk(pos):
        word, size = struct.unpack_from("<II", data, pos)
        end = pos + 4 + size
        obj = Obj((word >> 1) & 0x7FFF, active=word & 1, meta=word >> 16)
        if obj.layout == 0x7FFF:
            raise XfsError(f"null object at {pos:#x} (layout 0x7FFF) isn't supported")
        if obj.layout >= len(xfs.layouts):
            raise XfsError(f"object at {pos:#x} uses layout {obj.layout}, the file has {len(xfs.layouts)}")
        at = pos + 8
        for prop in xfs.layouts[obj.layout].props:
            n = struct.unpack_from("<I", data, at)[0]
            at += 4
            items = []
            for _ in range(n):
                if prop.type in OBJECT_TYPES:
                    item, at = chunk(at)
                elif prop.type == T_STRING:
                    text, enc, at = _cstring(data, at)
                    item = (text, enc)
                elif prop.type == T_RESOURCE:
                    flag = data[at]
                    at += 1
                    if flag:
                        cls, enc1, at = _cstring(data, at)
                        path, enc2, at = _cstring(data, at)
                        item = (flag, cls, path, enc1 if enc1 != "utf-8" else enc2)
                    else:
                        item = (0, None, None, "utf-8")
                else:
                    item = data[at:at + prop.size]
                    at += prop.size
                items.append(item)
            obj.values.append(items)
        if at != end:
            raise XfsError(f"object at {pos:#x}: read {at - pos} bytes, its size says {end - pos}")
        return obj, end

    xfs.root, end = chunk(data_ofs + 0x10)
    if end != len(data):
        raise XfsError(f"{len(data) - end} bytes after the root object")
    return xfs


def write(xfs):
    """Xfs -> bytes"""
    pool = _Pool()
    keys = []
    for layout in xfs.layouts:
        keys.append([pool.want(p.name.encode(p.encoding) + b"\0", p.name_ofs) for p in layout.props])
    names = pool.build()

    count = len(xfs.layouts)
    head = HEADER.size + 4 * count
    blocks, positions, at = [], [], head
    for layout in xfs.layouts:
        positions.append(at - 0x10)
        block = bytearray(LAYOUT.pack(layout.dti, len(layout.props) | (layout.init << 15), layout.reserved))
        blocks.append(block)
        at += len(block) + 24 * len(layout.props)
    names_at = at
    data_at = _align(names_at + len(names), 4)      # names padded to 4

    out = bytearray(HEADER.pack(MAGIC, xfs.major, xfs.minor, count, data_at - 0x10))
    out += struct.pack(f"<{count}I", *positions)
    for layout, block, lkeys in zip(xfs.layouts, blocks, keys):
        out += block
        for p, k in zip(layout.props, lkeys):
            out += PROP.pack(pool.offset(k) + names_at - 0x10, p.type, p.attr, p.size | (p.disable << 15),
                             p.getter, p.getcount, p.setter, p.setcount)
    out += names
    out += bytes(data_at - names_at - len(names))

    def chunk(obj):
        if not 0 <= obj.layout < count:
            raise XfsError(f"object uses layout {obj.layout}, there are {count}")
        layout = xfs.layouts[obj.layout]
        if len(obj.values) != len(layout.props):
            raise XfsError(f"object of layout {obj.layout} has {len(obj.values)} properties, its layout {len(layout.props)}")
        body = bytearray()
        for prop, items in zip(layout.props, obj.values):
            body += struct.pack("<I", len(items))
            for item in items:
                if prop.type in OBJECT_TYPES:
                    body += chunk(item)
                elif prop.type == T_STRING:
                    text, enc = item
                    body += text.encode(enc) + b"\0"
                elif prop.type == T_RESOURCE:
                    flag, cls, path, enc = item
                    body += bytes([flag])
                    if flag:
                        body += cls.encode(enc) + b"\0" + path.encode(enc) + b"\0"
                else:
                    if len(item) != prop.size:
                        raise XfsError(f"{prop.name}: item of {len(item)} bytes, the layout says {prop.size}")
                    body += item
        word = (obj.active & 1) | ((obj.layout & 0x7FFF) << 1) | ((obj.meta & 0xFFFF) << 16)
        return struct.pack("<II", word, len(body) + 4) + body

    out += chunk(xfs.root)
    return bytes(out)


# ---- typed item values (for XML / editors) -------------------------------------------------------------------------

def float_text(v):
    if math.isnan(v) or math.isinf(v):
        return "bits:" + struct.pack("<f", v).hex()
    return repr(v)


def item_value(prop, raw):
    """fixed-size item bytes -> ("scalar", number) | ("ints", tuple) | ("floats", tuple) | ("raw", bytes)"""
    t = prop.type
    if t in SCALARS and struct.calcsize("<" + SCALARS[t]) == prop.size:
        return "scalar", struct.unpack("<" + SCALARS[t], raw)[0]
    if t in INT_RECORDS and struct.calcsize("<" + INT_RECORDS[t]) == prop.size:
        return "ints", struct.unpack("<" + INT_RECORDS[t], raw)
    if t == 0x0F and prop.size == 4:                     # TYPE_COLOR as u8 r, g, b, a
        return "ints", tuple(raw)
    if t in FLOAT_VECTORS and prop.size % 4 == 0:
        return "floats", struct.unpack(f"<{prop.size // 4}f", raw)
    return "raw", raw


def item_bytes(prop, kind, value):
    t = prop.type
    if kind == "scalar":
        fmt = "<" + SCALARS[t]
        if fmt[1] in "fd":
            return struct.pack(fmt, float(value))
        size = struct.calcsize(fmt)
        return (int(value) & ((1 << (8 * size)) - 1)).to_bytes(size, "little")
    if kind == "ints":
        if t == 0x0F and prop.size == 4:
            return bytes(int(v) & 0xFF for v in value)
        return struct.pack("<" + INT_RECORDS[t], *(int(v) for v in value))
    if kind == "floats":
        return b"".join(struct.pack("<f", float(v)) for v in value)
    return bytes(value)
