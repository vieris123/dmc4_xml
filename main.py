import sys
import os
import io
import argparse
import xml.etree.ElementTree as ET

import structs.sdl as sdl
from xml_parser import from_sdl, to_sdl
from kaitaistruct import KaitaiStream
import glob

def serialize(fp):
    with open(fp, 'rb') as f:
        file_name = os.path.basename(fp).split('.')[0]
        data = f.read()
        magic = data[:3].decode('utf-8')

        if magic == 'SDL':
            sdl_bytes = io.BytesIO(data)
            sdl_struct = sdl.Sdl(KaitaiStream(sdl_bytes))
            sdl_struct._read()
            xml = from_sdl(sdl_struct)
            ET.indent(xml, space="\t", level=0)
            xml.write(f'{file_name}.xml')

def deserialize(fp, output):
    with open(fp, 'rb') as f:
        file_name, ext = os.path.basename(fp).split('.')
        data = f.read()
        tree = ET.fromstring(data)

        if output == 'sdl':
            out_data = to_sdl(tree)
            with open(f'{file_name}.sdl', 'wb') as wf:
                wf.write(out_data)

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('input', nargs='?')
    # parser.add_argument('output', nargs='?')
    #parser.add_argument('-i', '--input-type', default='sdl')
    parser.add_argument('-o', '--output-type', default='xml')
    parser.add_argument('-d', '--debug', action='store_true')
    args = parser.parse_args()

    if args.output_type == 'xml':
        if args.input:
            p = args.input
            if os.path.isfile(p):
                serialize(p)
            else:
                for p in glob.glob(os.path.join(args.input, '*')):
                    serialize(p)
        else:
            raise Exception('No path provided')
    else:
        if args.input:
            p = args.input
            output = args.output_type
            if os.path.isfile(p):
                deserialize(p, output)

if __name__ == '__main__':
    main()
