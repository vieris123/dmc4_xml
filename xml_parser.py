
import os
import io
import struct
import xml.etree.ElementTree as ET
from ctypes import Structure, Union, c_uint32
from collections import defaultdict
from classes import DTI_HASHES, RV_DTI_HASHES, DTI_FILE_HASHES, RV_DTI_FILE_HASHES
from classes import MtPropertyType, RV_MtPropertyType
from structs import xfs
from dmc4xml import xmlconv as _xmlconv, sdl as _sdl_codec, pla as _pla_codec
import mt_types as mt
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


# SDL / PLA live in the dmc4xml package (byte-exact codecs shared with Albam). These wrappers keep the old entry
# points: from_sdl / from_pla accept file bytes or a Kaitai object from the old structs.sdl / structs.pla.
SDL_TRACK_ENUM = _xmlconv.SDL_TAGS
RV_SDL_TRACK_ENUM = _xmlconv.RV_SDL_TAGS
PLA_TRACK_ENUM = _xmlconv.PLA_TAGS
RV_PLA_TRACK_ENUM = _xmlconv.RV_PLA_TAGS


def _file_bytes(src):
    if isinstance(src, (bytes, bytearray, memoryview)):
        return bytes(src)
    return src._io._io.getvalue()


def from_sdl(sdl_file):
    return ET.ElementTree(_xmlconv.sdl_to_xml(_sdl_codec.read(_file_bytes(sdl_file))))


def to_sdl(root):
    return _xmlconv.from_xml(root, 'sdl')


def from_pla(pla_file):
    return ET.ElementTree(_xmlconv.pla_to_xml(_pla_codec.read(_file_bytes(pla_file))))


def to_pla(root):
    return _xmlconv.from_xml(root, 'pla')


def write_name(buf, names):
    name_dict = defaultdict()
    for name in names:
        name_dict[name] = buf.tell()
        buf.write(bytes(name, 'utf-8'))
        buf.write(b'\0')
    buf_size = buf.getbuffer().nbytes
    if buf_size % 4 != 0:
        buf.write(b'\0' * (4 - (buf_size % 4)))
    return name_dict


class XfsMeta(Structure):
    _fields_ = (
        ('_active', c_uint32, 1),
        ('_layoutId', c_uint32, 15),
        ('_meta', c_uint32, 16)
    )
class XfsMetaUnion(Union):
    _fields_ = (
        ('_data', XfsMeta),
        ('_raw', c_uint32)
    )

def read_cstring(buffer: KaitaiStream, key):
    """{key: text} for a NUL-terminated string. Some strings are Shift-JIS rather than UTF-8,
    those also get '<key>_enc'="cp932" so they're written back the same way"""
    raw = buffer.read_bytes_term(0, False, True, None)
    try:
        return {key: raw.decode('utf-8')}
    except UnicodeDecodeError:
        return {key: raw.decode('cp932'), f'{key}_enc': 'cp932'}


def write_cstring(buffer: io.BytesIO, item, key):
    buffer.write(item.attrib[key].encode(item.attrib.get(f'{key}_enc', 'utf-8')) + b'\0')


def read_chunk(buffer: KaitaiStream, layouts, parent):
    e = ET.SubElement(parent, 'class', attrib={})
    
    meta = XfsMeta()
    io.BytesIO(buffer.read_bytes(4)).readinto(meta)
    chunk = buffer.read_u4le()
    layout = layouts[meta._layoutId]
    e.attrib['name'] = RV_DTI_HASHES[layout.data.dti]
    for prop in layout.data.prop:
        item_num = buffer.read_u4le()
        spec = mt.struct_spec(prop.type, prop.bytes)
        if spec is not None:
            fmt, fields = spec
            it = ET.SubElement(e, 'struct', attrib={
                'type': RV_MtPropertyType[prop.type],
                'name': prop.name})
            for i in range(item_num):
                values = struct.unpack(fmt, buffer.read_bytes(struct.calcsize(fmt)))
                ET.SubElement(it, 'item', attrib={f: str(v) for f, v in zip(fields, values)})
        elif prop.type in mt.type_to_class.keys():
            item_class = mt.type_to_class[prop.type]()
            item_bytes = prop.bytes
            it = ET.SubElement(e, 'vector', attrib={
                    'type':RV_MtPropertyType[prop.type],
                    'name': prop.name})
            for i in range(item_num):
                vec = ET.SubElement(it, 'vec', attrib={})
                for j in range(int(item_bytes/4)):
                    ET.SubElement(vec, 'item', attrib={'val':str(buffer.read_f4le())})
        elif prop.type in [1, 2]:
            it = ET.SubElement(e, 'classref', attrib={
                'type': RV_MtPropertyType[prop.type],
                'name': prop.name})
            for i in range(item_num):  
                # sub_bf_size = read_chunk(KaitaiStream(io.BytesIO(buffer.to_byte_array()[buffer.pos():])), layouts, e)
                # curr_pos = buffer.pos()
                # bf_seek_pos = sub_bf_size + curr_pos
                # buffer.seek(buffer.pos()+sub_bf_size+4)
                sub_bf_size = read_chunk(buffer, layouts, it)
        elif prop.type == 0xE:
            it = ET.SubElement(e, 'string', attrib={
                'type': RV_MtPropertyType[prop.type],
                'name': prop.name})
            for i in range(item_num):
                ET.SubElement(it, 'item', attrib=read_cstring(buffer, 'val'))
        elif prop.type == 0x3A:
            # resource reference: a flag byte, then (unless it's 0, no resource) class name and path
            it = ET.SubElement(e, 'resource', attrib={
                'type': RV_MtPropertyType[prop.type],
                'name': prop.name})
            for i in range(item_num):
                flag = buffer.read_u1()
                item = {'flag': str(flag)}
                if flag != 0:
                    item.update(read_cstring(buffer, 'class'))
                    item.update(read_cstring(buffer, 'path'))
                ET.SubElement(it, 'item', attrib=item)
        elif prop.type in mt.scalar_type_map:
            it = ET.SubElement(e, 'scalar', attrib={
                'type': RV_MtPropertyType[prop.type],
                'name': prop.name})
            for i in range(item_num):
                ET.SubElement(it, 'item', attrib={'val': str(mt.scalar_type_map[prop.type](buffer))})
        else:
            # a type without a reader: keep its bytes so it still round-trips
            it = ET.SubElement(e, 'raw', attrib={
                'type': RV_MtPropertyType.get(prop.type, hex(prop.type)),
                'name': prop.name,
                'bytes': str(prop.bytes)})
            for i in range(item_num):
                ET.SubElement(it, 'item', attrib={'hex': buffer.read_bytes(prop.bytes).hex()})
                
    return chunk

def from_xfs(xml, extension):
    root = ET.Element('root',attrib={'extension': extension})
    read_chunk(KaitaiStream(io.BytesIO(xml.data_buffer)), xml.objects, root)
    tree = ET.ElementTree(root)
    return tree

def deserialize_class(dst_xfs: xfs.Xfs, node, buffer: io.BytesIO, classes, names, index):
    class_def_check = False
    class_def = None
    dti = node.attrib['name']
    if dti not in classes:
        classes.append(node.attrib['name'])
        class_def_check = True
        class_def = dst_xfs.Obj(i = len(classes) - 1, _parent = dst_xfs, _root=dst_xfs._root)
        dst_xfs.objects.append(class_def)
        class_def.data = dst_xfs.ObjectData(_parent=class_def,_root=class_def._root)
        class_def.data.dti = DTI_HASHES[dti]
        class_def.data.prop_num = len(node)
        class_def.data.init = False
        class_def.data.reserved = 0
        class_def.data.prop = []
        
    meta = XfsMeta()
    meta._active = 1
    meta._layoutId = classes.index(dti)
    meta._meta = index

    meta_union = XfsMetaUnion()
    meta_union._meta = meta

    buffer.write(struct.pack('I', int.from_bytes(memoryview(meta),'little')))
    bf_size_pos = buffer.tell()
    buffer.write(struct.pack('I', 0))
    for c in node:
        prop = None
        if class_def_check:
            prop = dst_xfs.MtProperty(_parent=class_def.data,_root=class_def._root)
            #if c.tag != 'class':
            prop.type = MtPropertyType[c.attrib['type']]
            prop.attr = 0
            prop.disable = False
            prop.getter = 0
            prop.getcount = 0
            prop.setter = 0
            prop.setcount = 0
            prop.name__to_write = False
            class_def.data.prop.append(prop)
            prop.name = c.attrib['name']
            names.add(c.attrib['name'])
        # XML from older versions of this tool stores a resource as two items (class, path)
        legacy_resource = c.tag == 'resource' and len(c) > 0 and 'val' in c[0].attrib
        buffer.write(struct.pack('I', len(c) // 2 if legacy_resource else len(c)))
        if c.tag == 'classref':
            if class_def_check:
                # TYPE_CLASS or TYPE_CLASSREF, as read
                prop.type = MtPropertyType[c.attrib['type']]
                prop.bytes = 4
                prop.attr = 0xA0
            for v in c:
                deserialize_class(dst_xfs, v, buffer, classes, names, index + 1)

        else:                
            if c.tag == 'vector':
                if class_def_check:
                    prop.bytes = len(c[0]) * 4
                for v in c:
                    for i in v:
                        buffer.write(struct.pack('f',float(i.attrib['val'])))

            elif c.tag == 'struct':
                fmt, fields = mt.struct_spec(MtPropertyType[c.attrib['type']])
                if class_def_check:
                    prop.bytes = struct.calcsize(fmt)
                for v in c:
                    buffer.write(struct.pack(fmt, *(int(v.attrib[f]) for f in fields)))

            elif c.tag == 'raw':
                if class_def_check:
                    prop.bytes = int(c.attrib['bytes'])
                for v in c:
                    buffer.write(bytes.fromhex(v.attrib['hex']))

            elif c.tag == 'scalar':
                if class_def_check:
                    prop.bytes = mt.scalar_bytes_num[prop.type]
                for v in c:
                    type_id = MtPropertyType[c.attrib['type']]
                    if type_id in [0xC, 0xD]:
                        buffer.write(mt.scalar_write_map[type_id](float(v.attrib['val'])))
                    else:
                        buffer.write(mt.scalar_write_map[type_id](int(v.attrib['val'])))
            elif c.tag == 'string':
                if class_def_check:
                    prop.bytes = 4
                for v in c:
                    write_cstring(buffer, v, 'val')

            elif c.tag == 'resource':
                if class_def_check:
                    prop.bytes = 4
                if legacy_resource:
                    for class_item, path_item in zip(c[0::2], c[1::2]):
                        buffer.write(b'\x02')
                        write_cstring(buffer, class_item, 'val')
                        write_cstring(buffer, path_item, 'val')
                for v in ([] if legacy_resource else c):
                    flag = int(v.attrib['flag'])
                    buffer.write(struct.pack('B', flag))
                    if flag != 0:
                        write_cstring(buffer, v, 'class')
                        write_cstring(buffer, v, 'path')

    curr_pos = buffer.tell()
    bf_size = curr_pos - bf_size_pos
    buffer.seek(bf_size_pos)
    buffer.write(struct.pack('I',bf_size))
    buffer.seek(curr_pos)

def to_xfs(root):
    dst_xfs = xfs.Xfs()
    name_set = set()
    classes = []
    header = dst_xfs.XfsHeader(_parent=dst_xfs, _root=dst_xfs._root)
    dst_xfs.header = header
    header.magic = b'XFS\0'
    header.major_ver = 5
    header.minor_ver = 3
    header.obj_pos = []
    dst_xfs.objects = []
    dst_xfs.data_buffer__to_write = False
    name_buffer = io.BytesIO()
    data_buffer = io.BytesIO()

    for c in root:
        deserialize_class(dst_xfs, c, data_buffer, classes, name_set, 0)
    header_size = 16 + 4 * len(classes)
    header.object_num = len(classes)
    layout_size = 0
    for i in dst_xfs.objects:
        header.obj_pos.append(layout_size + header_size - 0x10)
        layout_size += 8 + i.data.prop_num * 24
    #layout_size = 8 * len(classes) + sum([len(x.data.prop) for x in dst_xfs.objects])

    name_dict = write_name(name_buffer, name_set)
    for i, c in enumerate(dst_xfs.objects):
        for prop in c.data.prop:
            prop.name_ofs = name_dict[prop.name] + header_size + layout_size - 0x10
    name_size = name_buffer.getbuffer().nbytes
    header.data_size = header_size + layout_size + name_buffer.getbuffer().nbytes - 0x10

    stream = KaitaiStream(io.BytesIO(bytearray(header_size + layout_size)))
    dst_xfs._write(stream)
    # stream.seek(header_size + layout_size)
    # stream.write_bytes(name_buffer.getbuffer())
    return b''.join(x for x in [stream.to_byte_array(), name_buffer.getbuffer(), data_buffer.getbuffer()])