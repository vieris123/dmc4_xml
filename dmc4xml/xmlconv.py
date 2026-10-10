"""SDL / PLA <-> XML. Tracks nest under their parent (file order is always a preorder of that tree, so nesting
keeps it); the root track is implicit.

Compatible with XML written by earlier versions of dmc4_xml: `org_dti_ofs` / `org_data_ofs` are ignored, missing
attributes take their defaults. New attributes:
- `move_line` on units (SDL classref / system tracks, PLA unit tracks)
- SDL root: `floor_frame="1"` (frames word bit 24), `marker_track` (index of the cut track; older XML called it
  `dti_table_offset`)
- `dti` accepts a class name, a hex / decimal hash, or any new class name (hashed with dti.dti_hash)
- `index` on value tracks whose dti field holds an array index
- `str_ofs` / `ref_ofs`: where the name / resource entry sat in the source file. Only used to write the strings back
  in the same order (byte-identical files); delete them freely, new strings are appended.
"""
import struct
import xml.etree.ElementTree as ET

from . import sdl as _sdl
from . import pla as _pla
from .classes import MtPropertyType, RV_MtPropertyType
from .dti import dti_id as _dti_id, dti_name as _dti_name

SDL_TAGS = {1: "root_track", 2: "classref_track", 3: "system_track", 4: "class_track", 5: "object_track",
            6: "int_track", 7: "vector_track", 8: "float_track", 9: "bool_track", 10: "ref_track",
            11: "resource_track", 12: "string_track", 13: "event_track", 14: "custom_track"}
PLA_TAGS = {1: "root_track", 3: "group_track", 4: "unit_track", 5: "object_track", 6: "bool_track", 7: "int_track",
            8: "float_track", 9: "vector_track", 10: "ref_track", 11: "resource_track"}
RV_SDL_TAGS = {v: k for k, v in SDL_TAGS.items()}
RV_SDL_TAGS["group_track"] = 3          # name used by an earlier version of this module
RV_PLA_TAGS = {v: k for k, v in PLA_TAGS.items()}

# element names of a vector key's floats, by property type (same names as mt_types' classes); a vector key always
# holds 4 floats, the ones past these are written as pad<N> only when they aren't zero
VECTOR_FIELDS = {0x0F: ("r", "g", "b", "a"), 0x14: ("x", "y", "z", "padding"), 0x15: ("x", "y", "z", "w"),
                 0x16: ("x", "y", "z", "w"), 0x22: ("x", "y"), 0x23: ("x", "y", "z"), 0x24: ("x", "y", "z", "w"),
                 0x28: ("p1", "p2")}


class XmlError(ValueError):
    pass


def _prop_name(p):
    return RV_MtPropertyType.get(p, f"{p:#x}")


def _prop_id(s):
    return MtPropertyType[s] if s in MtPropertyType else int(s, 0)



def _vector_to(item, prop, value):
    fields = VECTOR_FIELDS.get(prop, ("x", "y", "z", "w"))
    for name, v in zip(fields, value):
        ET.SubElement(item, name).text = repr(float(v))
    for i in range(len(fields), 4):
        if value[i] != 0.0:
            ET.SubElement(item, f"pad{i}").text = repr(float(value[i]))


def _vector_from(item, prop):
    fields = VECTOR_FIELDS.get(prop, ("x", "y", "z", "w"))
    out = [0.0, 0.0, 0.0, 0.0]
    for c in item:
        if c.tag in fields:
            out[fields.index(c.tag)] = float(c.text)
        elif c.tag.startswith("pad") and c.tag[3:].isdigit():
            out[int(c.tag[3:])] = float(c.text)
    return tuple(out)


def _resource_to(attrib, value, ref_ofs):
    if value is not None:
        attrib["ref_dti"] = _dti_name(value[0])
        attrib["ref_path"] = value[1]
        if ref_ofs is not None:
            attrib["ref_ofs"] = hex(ref_ofs)


def _resource_from(attrib):
    if "ref_path" not in attrib:
        return None, None
    hint = int(attrib["ref_ofs"], 0) if "ref_ofs" in attrib else None
    return (_dti_id(attrib.get("ref_dti", "0")), attrib["ref_path"]), hint


def _nest(tracks, tags, top, make):
    """Track list -> XML tree (preorder nesting)."""
    elements = {0: None}
    root_children = []
    for i, t in enumerate(tracks[1:], 1):
        e = make(t)
        if top(t):
            root_children.append(e)
        else:
            parent = elements.get(t.parent)
            if parent is None:
                raise XmlError(f"track {i} ({t.name}) has parent {t.parent}, which isn't a container before it")
            parent.append(e)
        elements[i] = e
    return root_children


def _flatten(node, tags, out, parent):
    """XML tree -> [(element, parent index)] in preorder."""
    for e in node:
        if e.tag not in tags:
            continue
        index = len(out) + 1
        out.append((e, parent))
        _flatten(e, tags, out, index)


# ---- SDL ---------------------------------------------------------------------------------------------------------

def _sdl_top(t):
    return t.type in (_sdl.UNIT, _sdl.SYSTEM) or t.parent == 0


def sdl_to_xml(sdl):
    """Sdl -> ElementTree root element"""
    root = ET.Element("root", {"frames": str(sdl.frames)})
    if sdl.flags & _sdl.FLOOR_FRAME >> 24:
        root.attrib["floor_frame"] = "1"
    if sdl.flags & ~(_sdl.FLOOR_FRAME >> 24):
        root.attrib["frame_flags"] = hex(sdl.flags & ~(_sdl.FLOOR_FRAME >> 24))
    if sdl.marker_track:
        root.attrib["marker_track"] = str(sdl.marker_track)
    if not sdl.tracks or sdl.tracks[0].type != _sdl.ROOT:
        raise XmlError("the first track isn't the root track")
    if sdl.tracks[0].name != "Root" or sdl.tracks[0].name_ofs:
        root.attrib["root_name"] = sdl.tracks[0].name

    def make(t):
        if t.type not in SDL_TAGS:
            raise XmlError(f"unknown track type {t.type} ({t.name})")
        a = {"prop_type": _prop_name(t.prop_type), "name": t.name}
        if t.name_ofs is not None:
            a["str_ofs"] = hex(t.name_ofs)
        if t.encoding != "utf-8":
            a["encoding"] = t.encoding
        if t.type in (_sdl.UNIT, _sdl.SYSTEM):
            a["dti"] = _dti_name(t.dti)
            a["move_line"] = str(t.parent)
        elif t.type == _sdl.OBJECT:
            a["obj_order"] = str(t.dti)
        elif t.dti:
            a["index"] = str(t.dti)
        e = ET.Element(SDL_TAGS[t.type], a)
        if t.keys:
            data = ET.SubElement(e, "data")
            for k in t.keys:
                ia = {"timermarker": str(k.frame), "marker_type": str(k.mode)}
                if t.type == _sdl.RESOURCE:
                    _resource_to(ia, k.value, k.ref_ofs)
                elif t.type == _sdl.STRING:
                    if k.value is not None:
                        ia["value"] = k.value
                        if k.ref_ofs is not None:
                            ia["ref_ofs"] = hex(k.ref_ofs)
                elif t.type == _sdl.CUSTOM:
                    ia["hex"] = bytes(k.value).hex()
                elif t.type == _sdl.FLOAT:
                    ia["value"] = repr(float(k.value))
                elif t.type != _sdl.VECTOR:
                    ia["value"] = str(k.value)
                item = ET.SubElement(data, "item", ia)
                if t.type == _sdl.VECTOR:
                    _vector_to(item, t.prop_type, k.value)
        return e

    for e in _nest(sdl.tracks, SDL_TAGS, _sdl_top, make):
        root.append(e)
    return root


def xml_to_sdl(root):
    """ElementTree root element (or an ElementTree) -> Sdl"""
    if hasattr(root, "getroot"):
        root = root.getroot()
    frames = int(root.attrib.get("frames", "0"), 0)
    flags = (frames >> 24) | int(root.attrib.get("frame_flags", "0"), 0)
    if root.attrib.get("floor_frame") == "1":
        flags |= _sdl.FLOOR_FRAME >> 24
    marker = root.attrib.get("marker_track", root.attrib.get("dti_table_offset", "0"))
    out = _sdl.Sdl(frames=frames & 0xFFFFFF, flags=flags, marker_track=int(marker, 0))
    out.tracks.append(_sdl.Track(_sdl.ROOT, 0, 0, root.attrib.get("root_name", "Root"), name_ofs=0))
    flat = []
    _flatten(root, RV_SDL_TAGS, flat, 0)
    for e, parent in flat:
        a = e.attrib
        ttype = RV_SDL_TAGS[e.tag]
        t = _sdl.Track(ttype, _prop_id(a.get("prop_type", "TYPE_UNDEFINED")), parent, a.get("name", ""),
                       name_ofs=int(a["str_ofs"], 0) if "str_ofs" in a else None,
                       encoding=a.get("encoding", "utf-8"))
        if ttype in (_sdl.UNIT, _sdl.SYSTEM):
            t.dti = _dti_id(a["dti"]) if "dti" in a else 0
            t.parent = int(a.get("move_line", "0"))
        elif ttype == _sdl.ROOT2:
            t.parent = 0
        elif ttype == _sdl.OBJECT:
            t.dti = int(a.get("obj_order", "0"))
        else:
            t.dti = int(a.get("index", "0"))
        if ttype not in _sdl.CONTAINERS:
            for item in e.iter("item"):
                ia = item.attrib
                frame, mode = int(ia.get("timermarker", "0")), int(ia.get("marker_type", "0"))
                hint = None
                if ttype == _sdl.RESOURCE:
                    value, hint = _resource_from(ia)
                elif ttype == _sdl.STRING:
                    value = ia.get("value")
                    hint = int(ia["ref_ofs"], 0) if "ref_ofs" in ia and value is not None else None
                elif ttype == _sdl.VECTOR:
                    value = _vector_from(item, t.prop_type)
                elif ttype == _sdl.CUSTOM:
                    value = bytes.fromhex(ia.get("hex", "00" * _sdl.CUSTOM_SIZE))
                elif ttype == _sdl.FLOAT:
                    value = float(ia.get("value", "0"))
                else:
                    value = int(ia.get("value", "0"), 0)
                t.keys.append(_sdl.Key(frame, mode, value, hint))
        out.tracks.append(t)
    return out


# ---- PLA ---------------------------------------------------------------------------------------------------------

def pla_to_xml(pla):
    """Pla -> ElementTree root element"""
    root = ET.Element("root", {"format": "pla"})
    if pla.dti_table_offset:
        root.attrib["dti_table_offset"] = str(pla.dti_table_offset)
    if not pla.tracks or pla.tracks[0].type != _pla.ROOT:
        raise XmlError("the first track isn't the root track")
    if pla.tracks[0].name != "Root":
        root.attrib["root_name"] = pla.tracks[0].name

    def make(t):
        if t.type not in PLA_TAGS:
            raise XmlError(f"unknown track type {t.type} ({t.name})")
        a = {"prop_type": _prop_name(t.prop_type), "name": t.name}
        if t.name_ofs is not None:
            a["str_ofs"] = hex(t.name_ofs)
        if t.encoding != "utf-8":
            a["encoding"] = t.encoding
        if t.type == _pla.UNIT:
            a["dti"] = _dti_name(t.dti)
        elif t.dti:
            a["dti" if t.type in _pla.CONTAINERS else "index"] = (
                _dti_name(t.dti) if t.type in _pla.CONTAINERS else str(t.dti))
        if t.move_line:
            a["move_line"] = str(t.move_line)
        if t.type == _pla.RESOURCE:
            _resource_to(a, t.value, t.ref_ofs)
        elif t.type == _pla.FLOAT:
            a["value"] = repr(float(t.value))
        elif t.type in (_pla.BOOL, _pla.INT, _pla.REF):
            a["value"] = str(t.value)
        e = ET.Element(PLA_TAGS[t.type], a)
        if t.type == _pla.VECTOR:
            _vector_to(ET.SubElement(e, "value"), t.prop_type, t.value)
        return e

    for e in _nest(pla.tracks, PLA_TAGS, lambda t: t.parent == 0, make):
        root.append(e)
    return root


def xml_to_pla(root):
    """ElementTree root element (or an ElementTree) -> Pla"""
    if hasattr(root, "getroot"):
        root = root.getroot()
    out = _pla.Pla(dti_table_offset=int(root.attrib.get("dti_table_offset", "0")))
    out.tracks.append(_pla.Track(_pla.ROOT, name=root.attrib.get("root_name", "Root"), name_ofs=0))
    flat = []
    _flatten(root, RV_PLA_TAGS, flat, 0)
    for e, parent in flat:
        a = e.attrib
        ttype = RV_PLA_TAGS[e.tag]
        t = _pla.Track(ttype, _prop_id(a.get("prop_type", "TYPE_UNDEFINED")), parent, int(a.get("move_line", "0")),
                       a.get("name", ""), name_ofs=int(a["str_ofs"], 0) if "str_ofs" in a else None,
                       encoding=a.get("encoding", "utf-8"))
        if ttype in _pla.CONTAINERS:
            t.dti = _dti_id(a["dti"]) if "dti" in a else 0
        else:
            t.dti = int(a.get("index", "0"))
        if ttype == _pla.RESOURCE:
            t.value, t.ref_ofs = _resource_from(a)
        elif ttype == _pla.VECTOR:
            v = e.find("value")
            t.value = _vector_from(v, t.prop_type) if v is not None else (0.0, 0.0, 0.0, 0.0)
        elif ttype == _pla.FLOAT:
            t.value = float(a.get("value", "0"))
        elif ttype in _pla.VALUE_TYPES:
            t.value = int(a.get("value", "0"), 0)
        out.tracks.append(t)
    return out


def detect(data):
    """'sdl', 'pla' or None from the magic."""
    head = bytes(data[:4])
    return {_sdl.MAGIC: "sdl", _pla.MAGIC: "pla"}.get(head)


def to_xml(data):
    """SDL / PLA bytes -> ElementTree"""
    kind = detect(data)
    if kind == "sdl":
        return ET.ElementTree(sdl_to_xml(_sdl.read(data)))
    if kind == "pla":
        return ET.ElementTree(pla_to_xml(_pla.read(data)))
    raise XmlError(f"not an SDL or PLA file ({bytes(data[:4])!r})")


def from_xml(root, kind=None):
    """XML (root element or ElementTree) -> SDL / PLA bytes. kind defaults to the root's `format` attribute (PLA XML
    has format="pla"; XML from earlier versions of the tool has none and is SDL)."""
    if hasattr(root, "getroot"):
        root = root.getroot()
    kind = kind or root.attrib.get("format", "sdl")
    if kind == "pla":
        return _pla.write(xml_to_pla(root))
    if kind == "sdl":
        return _sdl.write(xml_to_sdl(root))
    raise XmlError(f"unknown format {kind!r}")
