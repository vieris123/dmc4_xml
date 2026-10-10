"""dmc4xml: DMC4 (DX9) scheduler (.sdl) and placement (.pla) files, byte-exact, plus XML conversion.

Plain Python (no Kaitai, no Blender), so it can be vendored by other tools. Albam ships a copy in
`albam_vendor/dmc4xml` (synced by its `scripts/sync_dmc4xml.py`); make changes here, upstream.

    from dmc4xml import sdl, pla, xmlconv
    s = sdl.read(data)              # -> sdl.Sdl (tracks with keys)
    data = sdl.write(s)             # untouched files come back byte-identical
    tree = xmlconv.to_xml(data)     # SDL or PLA bytes -> ElementTree
    data = xmlconv.from_xml(tree)   # and back

`classes` holds the DTI class hashes and MtPropertyType ids used by the XML (and the XFS code in xml_parser).
"""
__version__ = "1.0.0"

from . import sdl, pla, xmlconv  # noqa: E402,F401
