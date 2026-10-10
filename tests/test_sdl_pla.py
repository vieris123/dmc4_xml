"""Round-trip test for the dmc4xml SDL / PLA codecs and XML conversion.

    python tests/test_sdl_pla.py [extracted game folder ...]

Checks every .sdl / .pla under tests/ (and the given folders): file -> codec -> file and file -> XML text -> file must
be byte-identical ("normalized" when only the layout changes, for files another tool wrote), and XML without the
layout hints (str_ofs / ref_ofs) must keep the content. SE files (SDL version 22) are reported as unsupported.
"""
import glob
import hashlib
import os
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from dmc4xml import sdl, pla, xmlconv  # noqa: E402


def content(kind, data):
    if kind == "sdl":
        return [(t.type, t.prop_type, t.parent, t.name, t.dti, t.keys) for t in sdl.read(data).tracks]
    return [(t.type, t.prop_type, t.parent, t.move_line, t.name, t.dti, t.value) for t in pla.read(data).tracks]


def check(path):
    data = open(path, "rb").read()
    kind = xmlconv.detect(data)
    if kind is None:
        return "skip", None
    codec = sdl if kind == "sdl" else pla
    try:
        codec.read(data)
    except (sdl.SdlError, pla.PlaError) as err:
        return "unsupported", str(err)
    problems = []
    rewritten = codec.write(codec.read(data))
    text = ET.tostring(xmlconv.to_xml(data).getroot(), encoding="unicode")
    via_xml = xmlconv.from_xml(ET.fromstring(text))
    normalized = False
    for label, out in (("codec", rewritten), ("XML", via_xml)):
        if out != data:
            # a file written by another tool with a different layout comes back in the standard one
            if content(kind, out) == content(kind, data):
                normalized = True
            else:
                problems.append(f"{label} round trip changes the content")
    bare = ET.fromstring(text)
    for e in bare.iter():
        e.attrib.pop("str_ofs", None)
        e.attrib.pop("ref_ofs", None)
    if content(kind, xmlconv.from_xml(bare)) != content(kind, data):
        problems.append("XML without layout hints loses content")
    if problems:
        return "FAIL", "; ".join(problems)
    return ("normalized (same content, standard layout)" if normalized else "ok"), None


def main(roots):
    seen, counts, failures = set(), {}, []
    for root in roots:
        for ext in ("sdl", "pla"):
            for path in sorted(glob.glob(os.path.join(root, "**", "*." + ext), recursive=True)):
                digest = hashlib.md5(open(path, "rb").read()).digest()
                if digest in seen:
                    continue
                seen.add(digest)
                status, note = check(path)
                counts[status] = counts.get(status, 0) + 1
                if status == "FAIL":
                    failures.append(f"{path}: {note}")
    print(counts)
    for f in failures:
        print("  " + f)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main([HERE] + sys.argv[1:]))
