"""XFS <-> XML, in the element shapes earlier versions of dmc4_xml wrote (class / scalar / vector / struct / string /
resource / classref / raw), so their XML still converts back.

Exactness extras (all optional; XML without them still converts, with layouts built from the data the way the old
writer did):
- root `xfs_version="5.0"` (major.minor)
- an `xfs_layouts` element: each class layout's dti, init / reserved bits and, per property, type, attr, size,
  disable, getter / setter fields and `str_ofs` (where its name sat, to keep the string order)
- `class` elements: `meta` (the chunk's upper 16 bits) when not 0, `active="0"` when the active bit is clear,
  `layout` when two layouts share a class name
"""
import xml.etree.ElementTree as ET

from . import xfs as _xfs
from .classes import MtPropertyType, RV_MtPropertyType
from .dti import dti_id, dti_name

STRUCT_FIELDS = {0x10: ("x", "y"), 0x11: ("w", "h"), 0x12: ("l", "t", "r", "b"), 0x36: ("s", "r"), 0x38: ("s", "r"),
                 0x0F: ("r", "g", "b", "a")}
SCALAR_SIZES = {0x3: 1, 0x4: 1, 0x5: 2, 0x6: 4, 0x7: 8, 0x8: 1, 0x9: 2, 0xA: 4, 0xB: 8, 0xC: 4, 0xD: 8}
LAYOUT_TAG = "xfs_layouts"


def _type_name(t):
    return RV_MtPropertyType.get(t, f"{t:#x}")


def _type_id(s):
    return MtPropertyType[s] if s in MtPropertyType else int(s, 0)


def _float(text):
    if text.startswith("bits:"):
        import struct
        return struct.unpack("<f", bytes.fromhex(text[5:]))[0]
    return float(text)


def _scalar_text(prop, v):
    return _xfs.float_text(v) if prop.type in (0xC, 0xD) else str(v)


# ---- XFS -> XML ----------------------------------------------------------------------------------------------------

def xfs_to_xml(x, extension):
    """Xfs -> root element"""
    root = ET.Element("root", {"extension": extension, "xfs_version": f"{x.major}.{x.minor}"})
    names = [dti_name(l.dti) for l in x.layouts]
    shared = {n for n in names if names.count(n) > 1}

    def obj_element(parent, obj):
        layout = x.layouts[obj.layout]
        a = {"name": dti_name(layout.dti)}
        if a["name"] in shared:
            a["layout"] = str(obj.layout)
        if obj.meta:
            a["meta"] = str(obj.meta)
        if not obj.active:
            a["active"] = "0"
        e = ET.SubElement(parent, "class", a)
        for prop, items in zip(layout.props, obj.values):
            pa = {"type": _type_name(prop.type), "name": prop.name}
            if prop.type in _xfs.OBJECT_TYPES:
                c = ET.SubElement(e, "classref", pa)
                for item in items:
                    obj_element(c, item)
            elif prop.type == _xfs.T_STRING:
                c = ET.SubElement(e, "string", pa)
                for text, enc in items:
                    ia = {"val": text}
                    if enc != "utf-8":
                        ia["val_enc"] = enc
                    ET.SubElement(c, "item", ia)
            elif prop.type == _xfs.T_RESOURCE:
                c = ET.SubElement(e, "resource", pa)
                for flag, cls, path, enc in items:
                    ia = {"flag": str(flag)}
                    if flag:
                        ia["class"], ia["path"] = cls, path
                        if enc != "utf-8":
                            ia["class_enc"] = ia["path_enc"] = enc
                    ET.SubElement(c, "item", ia)
            else:
                decoded = [_xfs.item_value(prop, raw) for raw in items]
                kind = decoded[0][0] if decoded else _xfs.item_value(prop, bytes(prop.size))[0]
                if kind == "scalar":
                    c = ET.SubElement(e, "scalar", pa)
                    for _, v in decoded:
                        ET.SubElement(c, "item", {"val": _scalar_text(prop, v)})
                elif kind == "ints":
                    c = ET.SubElement(e, "struct", pa)
                    fields = STRUCT_FIELDS.get(prop.type, tuple(f"v{i}" for i in range(8)))
                    for _, v in decoded:
                        ET.SubElement(c, "item", {f: str(n) for f, n in zip(fields, v)})
                elif kind == "floats":
                    c = ET.SubElement(e, "vector", pa)
                    for _, v in decoded:
                        vec = ET.SubElement(c, "vec")
                        for f in v:
                            ET.SubElement(vec, "item", {"val": _xfs.float_text(f)})
                else:
                    c = ET.SubElement(e, "raw", dict(pa, bytes=str(prop.size)))
                    for _, raw in decoded:
                        ET.SubElement(c, "item", {"hex": raw.hex()})
        return e

    obj_element(root, x.root)
    lay = ET.SubElement(root, LAYOUT_TAG)
    for layout in x.layouts:
        la = {"dti": dti_name(layout.dti)}
        if layout.init:
            la["init"] = "1"
        if layout.reserved:
            la["reserved"] = str(layout.reserved)
        le = ET.SubElement(lay, "layout", la)
        for p in layout.props:
            pa = {"name": p.name, "type": _type_name(p.type), "attr": hex(p.attr), "size": str(p.size)}
            for k in ("disable", "getter", "getcount", "setter", "setcount"):
                v = getattr(p, k)
                if v:
                    pa[k] = hex(v) if k in ("getter", "setter") else str(v)
            if p.name_ofs is not None:
                pa["str_ofs"] = hex(p.name_ofs)
            if p.encoding != "utf-8":
                pa["encoding"] = p.encoding
            ET.SubElement(le, "prop", pa)
    return root


# ---- XML -> XFS ----------------------------------------------------------------------------------------------------

def _element_size(c, ptype):
    if c.tag == "scalar":
        return SCALAR_SIZES.get(ptype, 4)
    if c.tag == "vector":
        first = c.find("vec")
        return 4 * (len(first) if first is not None else 4)
    if c.tag == "struct":
        if ptype == 0x0F:
            return 4
        import struct
        return struct.calcsize("<" + _xfs.INT_RECORDS[ptype])
    if c.tag == "raw":
        return int(c.attrib["bytes"])
    return 4                                       # classref, string, resource


def xml_to_xfs(root):
    """root element (or ElementTree) -> Xfs"""
    if hasattr(root, "getroot"):
        root = root.getroot()
    major, minor = (int(v) for v in root.attrib.get("xfs_version", "5.0").split("."))
    x = _xfs.Xfs(major=major, minor=minor)
    by_name = {}
    lay = root.find(LAYOUT_TAG)
    if lay is not None:
        for le in lay.findall("layout"):
            layout = _xfs.Layout(dti_id(le.attrib["dti"]), init=int(le.attrib.get("init", "0")),
                                 reserved=int(le.attrib.get("reserved", "0")))
            for pe in le.findall("prop"):
                a = pe.attrib
                layout.props.append(_xfs.Prop(
                    a["name"], _type_id(a["type"]), int(a["size"]), int(a.get("attr", "0"), 0),
                    int(a.get("disable", "0")), int(a.get("getter", "0"), 0), int(a.get("getcount", "0")),
                    int(a.get("setter", "0"), 0), int(a.get("setcount", "0")),
                    name_ofs=int(a["str_ofs"], 0) if "str_ofs" in a else None, encoding=a.get("encoding", "utf-8")))
            by_name.setdefault(le.attrib["dti"], len(x.layouts))
            x.layouts.append(layout)

    def layout_for(ce):
        if "layout" in ce.attrib:
            return int(ce.attrib["layout"])
        name = ce.attrib["name"]
        if name not in by_name:                    # XML without a layout table: build it like the old writer
            layout = _xfs.Layout(dti_id(name))
            for c in ce:
                ptype = _type_id(c.attrib["type"])
                layout.props.append(_xfs.Prop(c.attrib["name"], ptype, _element_size(c, ptype),
                                              attr=0xA0 if c.tag == "classref" else 0))
            by_name[name] = len(x.layouts)
            x.layouts.append(layout)
        return by_name[name]

    def build(ce, depth):
        index = layout_for(ce)
        layout = x.layouts[index]
        obj = _xfs.Obj(index, active=int(ce.attrib.get("active", "1")), meta=int(ce.attrib.get("meta", "0")))
        children = {c.attrib.get("name"): c for c in ce}
        for prop in layout.props:
            c = children.get(prop.name)
            items = []
            if c is None:
                obj.values.append(items)
                continue
            if c.tag == "classref":
                items = [build(sub, depth + 1) for sub in c if sub.tag == "class"]
            elif c.tag == "string":
                items = [(i.attrib.get("val", ""), i.attrib.get("val_enc", "utf-8")) for i in c]
            elif c.tag == "resource":
                legacy = len(c) and "val" in c[0].attrib           # older XML: class and path as two items
                if legacy:
                    items = [(2, a.attrib["val"], b.attrib["val"], "utf-8") for a, b in zip(c[0::2], c[1::2])]
                else:
                    for i in c:
                        flag = int(i.attrib.get("flag", "0"))
                        items.append((flag, i.attrib.get("class"), i.attrib.get("path"),
                                      i.attrib.get("class_enc", "utf-8")) if flag else (0, None, None, "utf-8"))
            elif c.tag == "scalar":
                for i in c:
                    v = i.attrib["val"]
                    items.append(_xfs.item_bytes(prop, "scalar", _float(v) if prop.type in (0xC, 0xD) else int(v, 0)))
            elif c.tag == "struct":
                fields = STRUCT_FIELDS.get(prop.type, tuple(f"v{k}" for k in range(8)))
                for i in c:
                    items.append(_xfs.item_bytes(prop, "ints", [int(i.attrib[f], 0) for f in fields if f in i.attrib]))
            elif c.tag == "vector":
                for v in c.findall("vec"):
                    items.append(_xfs.item_bytes(prop, "floats", [_float(i.attrib["val"]) for i in v]))
            else:
                items = [bytes.fromhex(i.attrib["hex"]) for i in c]
            obj.values.append(items)
        return obj

    first = next(c for c in root if c.tag == "class")
    x.root = build(first, 0)
    return x


def to_xml(data, extension):
    return ET.ElementTree(xfs_to_xml(_xfs.read(data), extension))


def from_xml(root):
    return _xfs.write(xml_to_xfs(root))
