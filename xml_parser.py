
import os
import io
import struct
import xml.etree.ElementTree as ET
from ctypes import Structure, Union, c_uint32
from collections import defaultdict
from classes import DTI_HASHES, RV_DTI_HASHES, DTI_FILE_HASHES, RV_DTI_FILE_HASHES
from classes import MtPropertyType, RV_MtPropertyType
from structs import sdl
import mt_types as mt
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


SDL_TRACK_ENUM = {
    1: 'root_track',
    2: 'classref_track', #unit track ?
    4: 'class_track', #another root ?
    5: 'object_track',
    6: 'int_track',
    7: 'vector_track',
    8: 'float_track',
    9: 'bool_track',
    10: 'ref_track',
    11: 'resource_track',
    13: 'event_track'
}

RV_SDL_TRACK_ENUM = {
    'root_track': 1,
    'classref_track': 2,  # unit track ?
    'class_track': 4,
    'object_track': 5,
    'int_track': 6,
    'vector_track': 7,
    'float_track': 8,
    'bool_track': 9,
    'ref_track': 10,
    'resource_track': 11,  # 0xB in decimal
    'event_track': 13      # 0xD in decimal
}

SYMBOL_ORDER = {
    'x': 0,
    'y': 1,
    'z': 2,
    'w': 3,
    'r': 0,
    'g': 1,
    'b': 2,
    'a': 3,
}

def from_sdl(sdl_file):
    root = ET.Element('root')
    sorted_tracks = sdl_file.tracks.copy()
    sorted_tracks.sort(key=lambda x: x.parent)
    #parents = defaultdict(list)
    elements = []

    for i, track in enumerate(sdl_file.tracks[1:]):
        #parents[track.parent].append(i)
        track_type = SDL_TRACK_ENUM[track.type]
        e = ET.Element(SDL_TRACK_ENUM[track.type],attrib={})
        e.attrib['prop_type'] = RV_MtPropertyType[track.prop_type]
        e.attrib['org_dti_ofs'] = hex(track.dti_ref)
        e.attrib['org_data_ofs'] = hex(track.data_ref)
        e.attrib['name'] = track.name
        if track.type == 2:
            e.attrib['dti'] = RV_DTI_HASHES[track.dti_ref]

        if track.type == 5:
            e.attrib['obj_order'] = f'{track.dti_ref}'

        if track.num_frames > 0:
            data = ET.SubElement(e, 'data')
            for j in range(track.num_frames):
                value = ET.SubElement(data, 'item', attrib={
                    'timermarker':str(track.timing_frames[j].frame),
                    'marker_type':str(track.timing_frames[j].type)
                })
                if track.type in [6, 8, 9]:
                    value.attrib['value'] = str(track.data[j])
                if track.type == 7:
                    # if track.prop_type == 0x28:
                    #     value.attrib['vec_type'] = 'mt_easecurve'
                    #     value.attrib['P1'] = str(track.data[j].p1)
                    #     value.attrib['P2'] = str(track.data[j].p2)
                    # elif track.prop_type == 0x22:
                    #     value.attrib['vec_type'] = 'float2'
                    #     value.attrib['X'] = str(track.data[j].x)
                    #     value.attrib['Y'] = str(track.data[j].y)
                    # elif track.prop_type in [0x15, 0x16, 0x24]:
                    #     value.attrib['vec_type'] = 'vec4'
                    #     value.attrib['X'] = str(track.data[j].x)
                    #     value.attrib['Y'] = str(track.data[j].y)
                    #     value.attrib['Z'] = str(track.data[j].z)
                    #     value.attrib['W'] = str(track.data[j].w)
                    # elif track.prop_type in [0x14, 0x23]:
                    #     value.attrib['vec_type'] = 'vec3'
                    #     value.attrib['X'] = str(track.data[j].x)
                    #     value.attrib['Y'] = str(track.data[j].y)
                    #     value.attrib['Z'] = str(track.data[j].z)
                    # else:
                    #     value.attrib['vec_type'] = 'color'
                    #     value.attrib['R'] = str(track.data[j].r)
                    #     value.attrib['G'] = str(track.data[j].g)
                    #     value.attrib['B'] = str(track.data[j].b)
                    #     value.attrib['A'] = str(track.data[j].a)
                    val = mt.type_to_class[track.prop_type]()
                    val.read(track.data[j])
                    for k in val.__annotations__:
                        it = ET.SubElement(value, k, attrib={})
                        it.text = str(getattr(val, k))
                if track.type == 0xB:
                    if track.data[j].ref_ofs:
                        value.attrib['ref_path'] = track.data[j].ref_path
                        value.attrib['ref_dti'] = RV_DTI_HASHES[track.data[j].ref_dti]

        if track.type in [2, 4]:
            root.append(e)
        else:
            elements[track.parent - 1].append(e)
        elements.append(e)

    tree = ET.ElementTree(root)
    return tree

def flatten_tree(node, node_list, p_index):
  if node.tag in RV_SDL_TRACK_ENUM:
      curr_index = len(node_list)
      node_list.append((node, p_index))
      if RV_SDL_TRACK_ENUM[node.tag] > 5:
        return
      else:
        for c in node:
          flatten_tree(c, node_list, curr_index)
  else:
    node_list.append((node, len(node_list)))
    for c in node:
      flatten_tree(c, node_list, 0)

def write_name(buf, names):
    name_dict = defaultdict()
    for name in names:
        name_dict[name] = buf.tell()
        buf.write(bytes(name, 'utf-8'))
        buf.write(b'\0')
    return name_dict

def pack_timeframe(node):
    frame_time = int(node.attrib['timermarker'])
    frame_type = int(node.attrib['marker_type'])
    class TimerFrame(Structure):
        _fields_ = (
            ('frame', c_uint32, 24),
            ('type', c_uint32, 8)
        )
    class TimerFrameUnion(Union):
        _fields_ = (
            ('timeframe', TimerFrame),
            ('raw', c_uint32)
        )
    frame = TimerFrame()
    frame.type = frame_type
    frame.frame = frame_time
    frame_union = TimerFrameUnion()
    frame_union.timeframe = frame
    return struct.pack('I', frame_union.raw)

def traverse_tree(node, dst_sdl, val_buffer, name_buffer, name_dict, p_index = 0, offset = 0):
    track = dst_sdl.Track(_parent=dst_sdl, _root=dst_sdl._root)
    track.type = RV_SDL_TRACK_ENUM[node.tag]
    track.prop_type = MtPropertyType[node.attrib['prop_type']]
    track.num_frames = len(node.findall('item'))
    track.parent = p_index
    track.name_ofs = name_dict[node.attrib['name']]
    track.dti_ref = 0
    track.timing_ref = offset
    track.data_ref = offset
    track.timing_frames__to_write = False
    track.data__to_write = False
    track.name__to_write = False

    if 'dti' in node.attrib:
        track.dti_ref = DTI_HASHES[node.attrib['dti']]


    if RV_SDL_TRACK_ENUM[node.tag] > 5:
        if node.tag == 'int_track' or node.tag == 'bool_track':
            track.timing_ref += val_buffer.getbuffer().nbytes
            time_val = [pack_timeframe(x) for x in node.iter('item')]
            val_buffer.write(b''.join(bytes(x) for x in time_val))
            track.data_ref += val_buffer.getbuffer().nbytes
            if node.attrib['prop_type'][5] == 'U':
                val_buffer.write(b''.join([struct.pack('I', int(x.attrib['value'])) for x in node.iter('item')]))
            else:
                val_buffer.write(b''.join([struct.pack('i', int(x.attrib['value'])) for x in node.iter('item')]))
            track.num_frames += len(time_val)

        elif node.tag == 'float_track':
            track.timing_ref += val_buffer.getbuffer().nbytes
            time_val = [pack_timeframe(x) for x in
                        node.iter('item')]
            val_buffer.write(b''.join(bytes(x) for x in time_val))
            track.data_ref += val_buffer.getbuffer().nbytes
            val_buffer.write(b''.join([struct.pack('f', float(x.attrib['value'])) for x in node.iter('item')]))
            track.num_frames += len(time_val)

        elif node.tag == 'resource_track':
            track.timing_ref += val_buffer.getbuffer().nbytes
            time_val = [pack_timeframe(x) for x in
                        node.iter('item')]
            val_buffer.write(b''.join(bytes(x) for x in time_val))
            items = list(node.iter('item'))
            track.data_ref += val_buffer.getbuffer().nbytes
            for i in range(len(time_val)):
                val_buffer.write(struct.pack('I', name_buffer.tell()))
                name_buffer.write(struct.pack('I', DTI_HASHES[items[i].attrib['ref_dti']]))
                name_buffer.write(bytes(items[i].attrib['ref_path'], 'utf-8'))
                name_buffer.write(b'\0')
            track.num_frames += len(time_val)

        elif node.tag == 'vector_track':
            track.timing_ref += val_buffer.getbuffer().nbytes
            time_val = [pack_timeframe(x) for x in
                        node.iter('item')]
            val_buffer.write(b''.join(bytes(x) for x in time_val))
            track.data_ref += val_buffer.getbuffer().nbytes
            track.num_frames += len(time_val)
            for it in node.iter('item'):
                for c in it:
                    val_buffer.write(struct.pack('f', float(c.text)))
    return track


def to_sdl(root):
    dst_sdl = sdl.Sdl()
    name = defaultdict()

    header = dst_sdl.BaseHeader(_parent=dst_sdl, _root=dst_sdl._root)
    header.magic = b'SDL\x00'
    header.dti_table_offset = 0
    header.version = 0x10
    header.ukn = 0

    val_buffer = io.BytesIO()
    name_buffer = io.BytesIO()
    name_buffer.write(bytes('Root\x00', 'utf-8'))
    tracks = []

    node_list = []
    flatten_tree(root, node_list, 0)
    name_set = set([x[0].attrib['name'] for x in node_list[1:]])
    name_dict = write_name(name_buffer, name_set)
    num_tracks = len(node_list)
    header_size = 0x14
    tracks_size = 0x18 * num_tracks

    root_track = dst_sdl.Track(_parent=dst_sdl, _root=dst_sdl._root)
    root_track.type = 1
    root_track.prop_type = 0
    root_track.num_frames = 0
    root_track.parent = 0
    root_track.name_ofs = 0
    root_track.dti_ref = 0
    root_track.timing_ref = 0
    root_track.data_ref = 0
    root_track.timing_frames__to_write = False
    root_track.data__to_write = False
    root_track.name__to_write = False
    tracks.append(root_track)

    tracks = tracks + [traverse_tree(x[0], dst_sdl, val_buffer,
                                     name_buffer, name_dict, x[1],
                                     tracks_size + header_size)
                       for x in node_list[1:]]
    dst_sdl.tracks = tracks

    val_buffer_size = val_buffer.getbuffer().nbytes
    name_buffer_size = name_buffer.getbuffer().nbytes
    header.name_offset = header_size + tracks_size + val_buffer_size
    header.num_tracks = num_tracks
    dst_sdl.header = header
    stream = KaitaiStream(io.BytesIO(bytearray(0x14 + 0x18 * len(tracks) \
                                               + name_buffer_size + val_buffer_size)))
    dst_sdl._write(stream)
    stream.seek(0x14 + 0x18 * len(tracks))
    stream.write_bytes(val_buffer.getvalue())
    #stream.seek(header.name_offset)
    stream.write_bytes(name_buffer.getvalue())
    # for child in root:
    #     ref_track = dst_sdl.Track(_parent=dst_sdl, _root=dst_sdl._root)
    #     ref_track.type = 2
    #     ref_track.prop_type = 2/
    return stream.to_byte_array()

def from_pla(pla):
    pass

def from_xfs(xml):
    pass