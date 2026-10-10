import sys
import os
import io
import argparse
import xml.etree.ElementTree as ET

import structs.xfs as xfs
from xml_parser import from_xfs, to_xfs
from dmc4xml import xmlconv
from kaitaistruct import KaitaiStream
import glob


def _out_path(fp, extension):
    """the input's name with its last extension replaced (emset001.pla.pla -> emset001.pla.xml)"""
    return os.path.splitext(os.path.basename(fp))[0] + '.' + extension


def serialize(fp):
    with open(fp, 'rb') as f:
        extension = os.path.splitext(fp)[1].lstrip('.')
        data = f.read()

        if xmlconv.detect(data):  # SDL / PLA
            xml = xmlconv.to_xml(data)
            ET.indent(xml, space="\t", level=0)
            xml.write(_out_path(fp, 'xml'))
        elif data[:3] == b'XFS':
            xfs_bytes = io.BytesIO(data)
            xfs_struct = xfs.Xfs(KaitaiStream(xfs_bytes))
            xfs_struct._read()
            xml = from_xfs(xfs_struct, extension)
            ET.indent(xml, space="\t", level=0)
            xml.write(_out_path(fp, 'xml'))

def deserialize(fp, output):
    with open(fp, 'rb') as f:
        data = f.read()
        tree = ET.fromstring(data)

        if output in ('sdl', 'pla'):
            out_data = xmlconv.from_xml(tree, output)
            with open(_out_path(fp, output), 'wb') as wf:
                wf.write(out_data)

        if output == 'xfs':
            out_data = to_xfs(tree)
            with open(_out_path(fp, tree.attrib['extension']), 'wb') as wf:
                wf.write(out_data)

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('input', nargs='?')
    # parser.add_argument('output', nargs='?')
    #parser.add_argument('-i', '--input-type', default='sdl')
    parser.add_argument('-o', '--output-type', default='xml',
                        help='xml (from .sdl, .pla or an XFS file), sdl, pla or xfs (from .xml)')
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
