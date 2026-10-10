"""Round-trip test for the dmc4xml XFS codec and XML conversion.

    python tests/test_xfs.py [extracted game folder ...]

Every XFS file (found by its magic, whatever the extension: .phs, .cam, .rut, .sprmap ...) under tests/ and the
given folders: file -> codec -> file and file -> XML text -> file must be byte-identical, and XML without the
layout table (as earlier versions of this tool wrote it) must keep every value. SE files (XFS 15) are reported as
unsupported.
"""
import hashlib
import os
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from dmc4xml import xfs, xfsxml  # noqa: E402


def values(obj):
    return [[values(i) if isinstance(i, xfs.Obj) else i for i in items] for items in obj.values]


def check(path, data):
    try:
        x = xfs.read(data)
    except xfs.XfsError as err:
        return "unsupported", str(err)
    problems = []
    if xfs.write(x) != data:
        problems.append("codec round trip differs")
    text = ET.tostring(xfsxml.to_xml(data, os.path.splitext(path)[1][1:]).getroot(), encoding="unicode")
    if xfsxml.from_xml(ET.fromstring(text)) != data:
        problems.append("XML round trip differs")
    bare = ET.fromstring(text)
    bare.remove(bare.find(xfsxml.LAYOUT_TAG))
    if values(xfs.read(xfsxml.from_xml(bare)).root) != values(x.root):
        problems.append("XML without the layout table loses values")
    return ("FAIL", "; ".join(problems)) if problems else ("ok", None)


def main(roots):
    seen, counts, failures = set(), {}, []
    for root in roots:
        for folder, _, names in os.walk(root):
            for name in names:
                path = os.path.join(folder, name)
                try:
                    with open(path, "rb") as f:
                        if f.read(4) != xfs.MAGIC:
                            continue
                        f.seek(0)
                        data = f.read()
                except OSError:
                    continue
                digest = hashlib.md5(data).digest()
                if digest in seen:
                    continue
                seen.add(digest)
                status, note = check(path, data)
                counts[status] = counts.get(status, 0) + 1
                if status == "FAIL":
                    failures.append(f"{path}: {note}")
    print(counts)
    for f in failures:
        print("  " + f)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main([HERE] + sys.argv[1:]))
