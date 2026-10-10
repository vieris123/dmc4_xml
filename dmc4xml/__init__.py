"""dmc4xml: DMC4 (DX9) scheduler (.sdl), placement (.pla), XFS (.phs / .clt chains, .cam, .rut, .sprmap ...) and
collision shape (.col hitboxes) files, byte-exact, plus XML conversion (sdl / pla / XFS).

Plain Python (no Kaitai, no Blender), so it can be vendored by other tools. Albam ships a copy in
`albam_vendor/dmc4xml` (synced by its `scripts/sync_dmc4xml.py`); make changes here, upstream.

    from dmc4xml import sdl, pla, xmlconv
    s = sdl.read(data)              # -> sdl.Sdl (tracks with keys)
    data = sdl.write(s)             # untouched files come back byte-identical
    tree = xmlconv.to_xml(data)     # SDL or PLA bytes -> ElementTree
    data = xmlconv.from_xml(tree)   # and back
    x = xfs.read(data); data = xfs.write(x); tree = xfsxml.to_xml(data, "phs"); data = xfsxml.from_xml(tree)

`classes` holds the DTI class hashes and MtPropertyType ids used by the XML (and the XFS code in xml_parser);
`dti.dti_hash(name)` computes a hash for any class name.
"""
__version__ = "1.0.0"

from . import sdl, pla, xmlconv, dti, xfs, xfsxml, col  # noqa: E402,F401
