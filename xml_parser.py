
import xml.etree.ElementTree as ET
from dmc4xml import xmlconv as _xmlconv, sdl as _sdl_codec, pla as _pla_codec, xfsxml as _xfsxml


# SDL, PLA and XFS live in the dmc4xml package (byte-exact codecs shared with Albam). These wrappers keep the old
# entry points: from_sdl / from_pla / from_xfs accept file bytes or a Kaitai object from the old structs.
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


def from_xfs(xfs_file, extension):
    """XFS file bytes, or a Kaitai object from structs.xfs -> ElementTree"""
    return _xfsxml.to_xml(_file_bytes(xfs_file), extension)


def to_xfs(root):
    return _xfsxml.from_xml(root)
