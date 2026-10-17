"""Round-trip test for the dmc4xml `.ctn` (rCharTbl) codec.

    python tests/test_ctn.py [extracted game folder ...] [--show BANK:SLOT ...]

Every `.CTN` file under the given folders (default: E:\\DMC mod stuffs\\arctool) must come back byte-identical
through read -> write. `--show 3:0x15` prints that script's commands with the waits resolved, which is how a move's
cancel windows are read off.
"""
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from dmc4xml import ctn  # noqa: E402

DEFAULT_ROOT = r"E:\DMC mod stuffs\arctool"


def find(roots):
    seen = set()
    for root in roots:
        for folder, _, names in os.walk(root):
            for name in names:
                if not name.lower().endswith(".ctn"):
                    continue
                path = os.path.join(folder, name)
                with open(path, "rb") as f:
                    data = f.read()
                if data[:4] != ctn.MAGIC:
                    continue
                digest = hashlib.md5(data).digest()
                if digest in seen:
                    continue
                seen.add(digest)
                yield path, data


def show(c, bank, slot):
    s = c.script(bank, slot)
    print(f"  bank {bank} slot {slot:#x}: ", end="")
    if s is None:
        print("no script (the game hangs on this motion)")
        return
    print(f"{len(s.commands)} commands, {s.size()} bytes")
    for frame, cmd in ctn.events(s):
        when = "motion end" if frame is None else f"frame {frame:g}"
        extra = f"  {ctn.describe_contact(cmd)}" if isinstance(cmd, ctn.Contact) else ""
        print(f"    {when:>12}: {cmd!r}{extra}")


def main(argv):
    roots, shows = [], []
    it = iter(argv)
    for a in it:
        if a == "--show":
            b, s = next(it).split(":")
            shows.append((int(b, 0), int(s, 0)))
        else:
            roots.append(a)
    roots = roots or [DEFAULT_ROOT]
    failures = 0
    for path, data in find(roots):
        try:
            c = ctn.read(data)
            out = ctn.write(c)
        except ctn.CtnError as err:
            print(f"FAIL {path}: {err}")
            failures += 1
            continue
        banks = sum(1 for b in c.banks if b is not None)
        scripts = sum(1 for b in c.banks if b for s in b.slots if s is not None)
        status = "ok  " if out == data else "FAIL"
        if out != data:
            failures += 1
        print(f"{status} {path}: {len(c.banks)} banks ({banks} set), {scripts} scripts, trailer {len(c.trailer)} B")
        for bank, slot in shows:
            show(c, bank, slot)
    print("all byte-identical" if not failures else f"{failures} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
