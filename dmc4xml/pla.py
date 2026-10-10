"""DMC4 DX9 placement files (`.pla`, `PLA\\0` version 17): byte-exact reader and writer, plain Python.

Layout (every DX9 file follows it, see the corpus test):

- header 0x10: magic, u16 version, u16 track count, u32 dti_table_offset, u32 name area offset
- tracks, 0x1C each: u32 type, u32 property type, u32 parent, u32 move line, u32 name offset, u32 dti, u32 data
  offset
- value area: one value per value track, in track order, each at the next 16-byte boundary (4 bytes, 16 for
  vectors)
- name area at the next 4-byte boundary after the values (if any, else after the tracks): NUL-terminated track
  names and resource entries (u32 dti + path); the file ends with the last string

Track types: 1 root, 3 group, 4 unit (dti = class hash, move line), 5 object (a class member holding values), 6 bool,
7 int, 8 float, 9 vector, 10 ref (a track index, e.g. a unit's mGroupLV* pointing at a group), 11 resource. Value tracks
use `dti` as the array index (several tracks with one name form an array).
"""
import struct

from .sdl import _Pool, _cstring, _align, _resource_entry

MAGIC = b"PLA\0"
VERSION = 17
HEADER = struct.Struct("<4sHHII")
TRACK = struct.Struct("<7I")
VALUE_ALIGN = 16

ROOT, GROUP, UNIT, OBJECT = 1, 3, 4, 5
BOOL, INT, FLOAT, VECTOR, REF, RESOURCE = 6, 7, 8, 9, 10, 11
CONTAINERS = (ROOT, GROUP, UNIT, OBJECT)
VALUE_TYPES = (BOOL, INT, FLOAT, VECTOR, REF, RESOURCE)

# property types read as signed ints by INT tracks
SIGNED = (0x8, 0x9, 0xA, 0xB)


class PlaError(ValueError):
    pass


class Track:
    """`value`: bool tracks an int (0/1), int / ref tracks an int, float a float, vector a tuple of 4 floats,
    resource None or (dti, path). `name_ofs` / `ref_ofs` are source offsets kept to reproduce the string order."""
    __slots__ = ("type", "prop_type", "parent", "move_line", "name", "dti", "value", "name_ofs", "ref_ofs",
                 "encoding")

    def __init__(self, type, prop_type=0, parent=0, move_line=0, name="", dti=0, value=None, name_ofs=None,
                 ref_ofs=None, encoding="utf-8"):
        self.type, self.prop_type, self.parent, self.move_line = type, prop_type, parent, move_line
        self.name, self.dti, self.value = name, dti, value
        self.name_ofs, self.ref_ofs, self.encoding = name_ofs, ref_ofs, encoding

    def __repr__(self):
        return f"Track({self.type}, {self.prop_type:#x}, parent={self.parent}, {self.name!r}, value={self.value!r})"


class Pla:
    def __init__(self, tracks=None, version=VERSION, dti_table_offset=0):
        self.tracks = tracks if tracks is not None else []
        self.version, self.dti_table_offset = version, dti_table_offset


def _unpack(track, data, at):
    t, p = track.type, track.prop_type
    if t == VECTOR:
        return struct.unpack_from("<4f", data, at)
    if t == FLOAT:
        return struct.unpack_from("<f", data, at)[0]
    if t == BOOL:
        return data[at]
    if t == INT:
        return struct.unpack_from("<i" if p in SIGNED else "<I", data, at)[0]
    return struct.unpack_from("<I", data, at)[0]


def _pack(track):
    t, p, v = track.type, track.prop_type, track.value
    if t == VECTOR:
        v = tuple(v) + (0.0,) * (4 - len(v))
        return struct.pack("<4f", *v[:4])
    if t == FLOAT:
        return struct.pack("<f", v)
    if t == BOOL:
        return struct.pack("<B", v)
    if t == INT:
        return struct.pack("<I", int(v) & 0xFFFFFFFF)    # signed or unsigned range, the bytes are the same
    return struct.pack("<I", int(v) & 0xFFFFFFFF)


def read(data):
    """bytes -> Pla"""
    data = bytes(data)
    if len(data) < HEADER.size or data[:4] != MAGIC:
        raise PlaError(f"not a PLA file ({data[:4]!r})")
    magic, version, count, dti_table_offset, names = HEADER.unpack_from(data, 0)
    if version != VERSION:
        raise PlaError(f"PLA version {version} isn't supported (DX9 files are {VERSION})")
    pla = Pla(version=version, dti_table_offset=dti_table_offset)
    for i in range(count):
        ttype, prop, parent, move_line, name_ofs, dti, at = TRACK.unpack_from(data, HEADER.size + TRACK.size * i)
        name, enc = _cstring(data, names + name_ofs)
        track = Track(ttype, prop, parent, move_line, name, dti, name_ofs=name_ofs, encoding=enc)
        if ttype in VALUE_TYPES:
            if not at:
                raise PlaError(f"value track {i} ({name}) has no value")
            if ttype == RESOURCE:
                ofs = struct.unpack_from("<I", data, at)[0]
                if ofs:
                    dti_ref = struct.unpack_from("<I", data, names + ofs)[0]
                    track.value = (dti_ref, _cstring(data, names + ofs + 4)[0])
                    track.ref_ofs = ofs
            else:
                track.value = _unpack(track, data, at)
        elif at:
            raise PlaError(f"container track {i} ({name}) has a value")
        pla.tracks.append(track)
    return pla


def _value_bytes(track, ref_offset=0):
    if track.type == RESOURCE:
        return struct.pack("<I", ref_offset)
    raw = _pack(track)
    return raw if track.type == VECTOR else raw + bytes(4 - len(raw))     # a bool takes a 4-byte slot too


def write(pla):
    """Pla -> bytes"""
    tracks = pla.tracks
    problems = []
    for i, t in enumerate(tracks):
        if t.type not in CONTAINERS and t.type not in VALUE_TYPES:
            problems.append(f"track {i} ({t.name}): unknown track type {t.type}")
        elif t.type in VALUE_TYPES and t.value is None and t.type != RESOURCE:
            problems.append(f"track {i} ({t.name}): no value")
    if len(tracks) > 0xFFFF:
        problems.append(f"{len(tracks)} tracks (65,535 at most)")
    if problems:
        raise PlaError("\n".join(problems))

    pool = _Pool()
    name_keys, ref_keys = [], {}
    for t in tracks:
        name_keys.append(pool.want(t.name.encode(t.encoding) + b"\0", t.name_ofs))
        if t.type == RESOURCE and t.value is not None:
            ref_keys[id(t)] = pool.want(_resource_entry(t.value), t.ref_ofs)
    names = pool.build()

    base = HEADER.size + TRACK.size * len(tracks)
    values = bytearray()
    refs = []
    for t in tracks:
        if t.type not in VALUE_TYPES:
            refs.append(0)
            continue
        pos = base + len(values)
        at = _align(pos, VALUE_ALIGN)
        values += bytes(at - pos)
        values += _value_bytes(t, pool.offset(ref_keys[id(t)]) if id(t) in ref_keys else 0)
        refs.append(at)
    end = base + len(values)
    name_area = _align(end, 4)

    out = bytearray(HEADER.pack(MAGIC, pla.version, len(tracks), pla.dti_table_offset, name_area))
    for t, key, at in zip(tracks, name_keys, refs):
        out += TRACK.pack(t.type, t.prop_type, t.parent, t.move_line, pool.offset(key), t.dti, at)
    out += values
    out += bytes(name_area - end)
    out += names
    return bytes(out)
