"""DMC4 DX9 character tables (`.ctn` = rCharTbl, `chartbl\\pl000` / `pl006`): byte-exact reader and writer, plain
Python. One small byte script per player motion, run by cCharTblMgr while the motion plays: cancel windows, the
camera / pad vibration requests and the "contact" bytes move code waits for. Layout from the DX9 code
(`cCharTblMgr::set` 0x42BA50, `::update` 0x42B8E0, `::procCtWait` / `::procCtContact`; Vibed/RE/chartbl_ctn_hang.md),
byte-exact on the vanilla Nero and Dante files.

Offsets are u32, relative to "top" = file + 4 (the game never reads the two end markers; it indexes blindly):

- 0x00 `.CTN`; from 0x04 `bank_offset[]` (relative to top), ended by 0xFFFFFFFF; 0 = no table for that bank.
- per bank, at top + bank_offset: `slot_offset[]` (relative to the table start), ended by 0xFFFFFFFF; 0 = no
  script. Then that bank's scripts, in slot order, each ending with FF and zero-padded to 4 bytes.
- bank = `(motion_no >> 8) & 0xF` for normal motions (LMT `pl000_NN` -> bank NN - 1); Nero's Buster grabs use
  banks 10-29 (`uPlayerNero::setShortGrabEnemyReactionFunc`); slot = `motion_no & 0xFF`.

Script commands:

| bytes | command |
|---|---|
| `00 mode xx xx f32 frame` | wait until `mFrame >= frame` (frame < 0: until the motion ends); mode 0 goes on, mode 1 ends the script |
| `01 idx b0 b1 b2 b3 b4 b5` | contact: each non-zero byte is written into `mContactData[idx].info[0..5]` |
| `02 idx xx xx` | clear `mContactData[idx]` |
| `03 xx xx xx u32 back` | loop: cursor = cursor - back + 8, then wait for the next tick |
| `FF` | end |

Contact set 0 is the "contact info" (bytes: atck, free2, camVib, free1, free0, padVib; free0 / 1 / 2 are stage
triggers read by move code). Contact set 1 holds cancel instructions: byte k's low nibble picks a cancel from
`CANCEL_TABLES[k]`, its high nibble opens (0x10: mStat 2, 0x30: mStat 1) or closes (0x20) it; cancels before the
picked one in that table are reset. **A motion whose (bank, slot) has no script, or a slot past the table, hangs the
game** (the loop in `update` never advances on an unknown opcode), so every playable block needs a script; an empty
`Script()` (just FF) is the safe filler.

    c = ctn.read(data); data == ctn.write(c)
    s = c.script(bank, slot)             # Script or None
    c.ensure(bank, slot).commands[:] = [ctn.Wait(10.0), ctn.Contact(1, (0x14, 0, 0, 0, 0, 0))]
    for ev in ctn.events(s): ...         # (frame, command) with waits resolved to absolute frames
"""
import struct

MAGIC = b".CTN"
END = 0xFFFFFFFF
TOP = 4

CONTACT_INFO = ("atck", "free2", "cam_vib", "free1", "free0", "pad_vib")   # contact set 0, byte order in the file
CANCEL_NAMES = ("C_NORM0", "C_NORM1", "C_NORM2", "C_COMMAND", "C_JUMP", "C_CHOUHATSU", "C_GUN", "C_ALL")
# uPlayer::cancelNoTbl (0xC7781C): what the low nibble of contact-set-1 byte k selects
CANCEL_TABLES = (
    (0, 1, 2),             # byte 0: C_NORM0, C_NORM1, C_NORM2
    (3, 4, 5, 6, 7),       # byte 1: C_COMMAND, C_JUMP, C_CHOUHATSU, C_GUN, C_ALL
    (4, 5, 6, 7),          # byte 2
    (5, 6, 7),             # byte 3
    (6, 7),                # byte 4
    (7,),                  # byte 5
)
OPEN, CLOSE, OPEN_ALT = 0x10, 0x20, 0x30   # high nibble: mStat = 2 / off / mStat = 1


class CtnError(ValueError):
    pass


class Wait:
    """`00 mode pad f32 frame`. mode 0: continue when reached; 1: end the script when reached. `pad` keeps the two
    unused bytes."""
    __slots__ = ("frame", "mode", "pad")
    SIZE = 8

    def __init__(self, frame, mode=0, pad=0):
        self.frame, self.mode, self.pad = float(frame), mode, pad

    def pack(self):
        return struct.pack("<BBHf", 0, self.mode, self.pad, self.frame)

    def __repr__(self):
        return f"Wait({self.frame:g}{', end' if self.mode == 1 else ''}{f', mode={self.mode}' if self.mode > 1 else ''})"


class Contact:
    """`01 idx b0..b5`: write the non-zero bytes into contact set `idx`."""
    __slots__ = ("idx", "info")
    SIZE = 8

    def __init__(self, idx, info):
        info = tuple(info)
        if len(info) != 6:
            raise CtnError("a contact command carries 6 bytes")
        self.idx, self.info = idx, info

    def pack(self):
        return bytes((1, self.idx, *self.info))

    def __repr__(self):
        return f"Contact({self.idx}, {bytes(self.info).hex(' ')})"


class Clear:
    """`02 idx pad`: zero contact set `idx`."""
    __slots__ = ("idx", "pad")
    SIZE = 4

    def __init__(self, idx, pad=0):
        self.idx, self.pad = idx, pad

    def pack(self):
        return struct.pack("<BBH", 2, self.idx, self.pad)

    def __repr__(self):
        return f"Clear({self.idx})"


class Loop:
    """`03 pad u32 back`: the cursor goes back `back` bytes from this command (then + 8), and the tick ends.
    `Script.loop_target(i)` gives the command it lands on."""
    __slots__ = ("back", "pad")
    SIZE = 8

    def __init__(self, back, pad=0):
        self.back, self.pad = back, pad

    def pack(self):
        return struct.pack("<BBHI", 3, self.pad & 0xFF, (self.pad >> 8) & 0xFFFF, self.back)

    def __repr__(self):
        return f"Loop(back={self.back})"


class Script:
    """The commands of one (bank, slot); the terminating FF is implied."""
    __slots__ = ("commands",)

    def __init__(self, commands=None):
        self.commands = list(commands) if commands else []

    def size(self):
        """Unpadded size, FF included."""
        return sum(c.SIZE for c in self.commands) + 1

    def offsets(self):
        """Byte offset of each command from the script start."""
        out, at = [], 0
        for c in self.commands:
            out.append(at)
            at += c.SIZE
        return out

    def loop_target(self, i):
        """Index of the command a Loop at position i jumps to (None if it lands outside the script)."""
        offs = self.offsets()
        target = offs[i] - self.commands[i].back + 8
        return offs.index(target) if target in offs else None

    def pack(self):
        out = b"".join(c.pack() for c in self.commands) + b"\xff"
        return out + b"\0" * (-len(out) % 4)

    def __repr__(self):
        return f"Script({self.commands!r})"


class Bank:
    __slots__ = ("slots",)

    def __init__(self, slots=None):
        self.slots = list(slots) if slots else []


class Ctn:
    def __init__(self, banks=None, trailer=b""):
        self.banks = list(banks) if banks else []     # Bank or None (bank offset 0)
        self.trailer = trailer                        # bytes after the last script (padding in some files)

    def script(self, bank, slot):
        if bank >= len(self.banks) or self.banks[bank] is None:
            return None
        slots = self.banks[bank].slots
        return slots[slot] if slot < len(slots) else None

    def ensure(self, bank, slot):
        """The Script at (bank, slot), creating the bank / slots (filled with empty FF scripts) as needed."""
        while len(self.banks) <= bank:
            self.banks.append(None)
        if self.banks[bank] is None:
            self.banks[bank] = Bank()
        slots = self.banks[bank].slots
        while len(slots) <= slot:
            slots.append(Script())
        if slots[slot] is None:
            slots[slot] = Script()
        return slots[slot]


def _u32(data, at):
    if at + 4 > len(data):
        raise CtnError(f"offset {at:#x} is outside the file")
    return struct.unpack_from("<I", data, at)[0]


def _parse_script(data, at):
    cmds = []
    while True:
        if at >= len(data):
            raise CtnError("a script runs past the end of the file")
        op = data[at]
        if op == 0xFF:
            return Script(cmds), at + 1
        if op == 0:
            mode, pad, frame = struct.unpack_from("<BHf", data, at + 1)
            cmds.append(Wait(frame, mode, pad))
            at += 8
        elif op == 1:
            cmds.append(Contact(data[at + 1], data[at + 2:at + 8]))
            at += 8
        elif op == 2:
            cmds.append(Clear(data[at + 1], struct.unpack_from("<H", data, at + 2)[0]))
            at += 4
        elif op == 3:
            back = _u32(data, at + 4)
            cmds.append(Loop(back, data[at + 1] | (struct.unpack_from("<H", data, at + 2)[0] << 8)))
            at += 8
        else:
            raise CtnError(f"unknown opcode {op:#x} at {at:#x} (the game would hang here)")


def read(data):
    data = bytes(data)
    if data[:4] != MAGIC:
        raise CtnError(f"not a character table ({data[:4]!r})")
    banks, at = [], TOP
    while True:
        off = _u32(data, at)
        at += 4
        if off == END:
            break
        banks.append(off)
    ctn = Ctn()
    end = at
    cache = {}
    for off in banks:
        if off == 0:
            ctn.banks.append(None)
            continue
        table = TOP + off
        bank, k = Bank(), 0
        while True:
            e = _u32(data, table + 4 * k)
            k += 1
            if e == END:
                break
            if e == 0:
                bank.slots.append(None)
                continue
            start = (table + e) & END
            if start not in cache:
                cache[start], stop = _parse_script(data, start)
                end = max(end, stop + (-stop % 4))
            bank.slots.append(cache[start])
        end = max(end, table + 4 * k)
        ctn.banks.append(bank)
    ctn.trailer = data[end:]
    return ctn


def write(ctn):
    """Canonical layout (what the vanilla files use): header, then per bank its table and scripts in slot order.
    Slots sharing one Script object share the bytes."""
    head = bytearray(MAGIC)
    for _ in ctn.banks:
        head += b"\0\0\0\0"
    head += struct.pack("<I", END)
    body = bytearray()
    for i, bank in enumerate(ctn.banks):
        if bank is None:
            continue
        table = len(head) + len(body)
        struct.pack_into("<I", head, TOP + 4 * i, table - TOP)
        entries = bytearray()
        scripts = bytearray()
        placed = {}
        script_base = table + 4 * (len(bank.slots) + 1)
        for s in bank.slots:
            if s is None:
                entries += b"\0\0\0\0"
                continue
            if id(s) not in placed:
                placed[id(s)] = script_base + len(scripts)
                scripts += s.pack()
            entries += struct.pack("<I", (placed[id(s)] - table) & END)
        entries += struct.pack("<I", END)
        body += entries + scripts
    return bytes(head + body + ctn.trailer)


def events(script):
    """[(frame, command)] with the waits folded into absolute frames (a Wait with frame < 0 = the motion's end,
    reported as frame None). Loops are reported as commands at their frame; the frames after a loop are the
    second pass and aren't expanded."""
    out, frame = [], 0.0
    for c in script.commands:
        if isinstance(c, Wait):
            frame = c.frame if c.frame >= 0 else None
            if c.mode == 1:
                out.append((frame, c))
                break
        else:
            out.append((frame, c))
    return out


def describe_contact(c):
    """Human-readable fields of a Contact command."""
    if c.idx == 0:
        return {name: v for name, v in zip(CONTACT_INFO, c.info) if v}
    out = {}
    for k, b in enumerate(c.info):
        if not b:
            continue
        table = CANCEL_TABLES[k] if k < len(CANCEL_TABLES) else ()
        n, kind = b & 0xF, b & 0xF0
        name = CANCEL_NAMES[table[n]] if n < len(table) else f"?{n}"
        out[f"cancel{k}"] = f"{name} {'open' if kind == OPEN else 'close' if kind == CLOSE else 'open_alt' if kind == OPEN_ALT else f'{kind:#x}'}"
    return out


def bank_of(motion_no):
    return (motion_no >> 8) & 0xF


def slot_of(motion_no):
    return motion_no & 0xFF
