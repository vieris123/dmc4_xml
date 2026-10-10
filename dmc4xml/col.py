"""DMC4 DX9 collision shapes (`.col` = rCollisionShape, `COL\\0` version 2): byte-exact reader and writer, plain
Python. The game's hitbox format: attack / hurt / push / grab volumes on a model's joints (`collision/pl000.col`,
`wp*.col`, enemies), used by the gameplay collision (uCollisionMgr / cCollisionGroup: a group's kind is its mKind),
and by chains (`pl000_03.col`: the body capsules the coat collides with). Layout from the DX9 chain collision code
(Vibed/RE/chain_cnschain.md, chain test 0x438DB0); byte-exact on all 110 DX9 files:

- header 0x10: magic, u16 version, u16 group count, u32 a, u32 b (-1 in the files). SE files (another layout)
  are refused.
- per group, 0x10: u32 shape count, u32 kind (cCollisionGroup.mKind, 0-6 in the files), u32 flags (1 attack,
  2 damage / hurt, 4 push, 8 grab, 0x20 friendly attack), u32 pad (-1), then the shapes, 0x40 each:
  0x00 u32 type (0 sphere: pos0 in bone0's frame; 3 capsule: pos0 in bone0's frame to pos1 in bone1's frame;
  1 on 6 shapes, meaning unknown),
  0x04 u32 bone0, 0x08 u32 bone1 (joint IDs of the collision model, 255 = none), 0x0C f32 radius,
  0x10 vec4 pos0, 0x20 vec4 pos1, 0x30 u32 unk, 0x34 u32 id, 0x38 f32 shrink, 0x3C u32 unk2
"""
import struct

MAGIC = b"COL\0"
HEADER = struct.Struct("<4sHHII")
GROUP = struct.Struct("<IIII")
SHAPE = struct.Struct("<16I")      # floats kept as raw bits: some files hold signalling NaNs Python would quiet

SPHERE, CAPSULE = 0, 3
FLAG_ATTACK, FLAG_DAMAGE, FLAG_PUSH, FLAG_GRAB, FLAG_FRIEND_ATTACK = 0x1, 0x2, 0x4, 0x8, 0x20


class ColError(ValueError):
    pass


def _bits(v):
    return struct.unpack("<I", struct.pack("<f", v))[0]


def _float(bits):
    return struct.unpack("<f", struct.pack("<I", bits))[0]


class Shape:
    """Float fields (radius, pos0, pos1, shrink) are properties over raw 32-bit values, so untouched NaN payloads
    survive; assigning a float re-encodes it."""
    __slots__ = ("type", "bone0", "bone1", "radius_bits", "pos0_bits", "pos1_bits", "unk", "id", "shrink_bits",
                 "unk2")

    def __init__(self, type=CAPSULE, bone0=0, bone1=255, radius=1.0, pos0=(0.0, 0.0, 0.0, 0.0),
                 pos1=(0.0, 0.0, 0.0, 0.0), unk=0, id=0, shrink=0.0, unk2=0xFFFFFFFF):
        self.type, self.bone0, self.bone1 = type, bone0, bone1
        self.radius, self.pos0, self.pos1, self.shrink = radius, pos0, pos1, shrink
        self.unk, self.id, self.unk2 = unk, id, unk2

    radius = property(lambda self: _float(self.radius_bits), lambda self, v: setattr(self, "radius_bits", _bits(v)))
    shrink = property(lambda self: _float(self.shrink_bits), lambda self, v: setattr(self, "shrink_bits", _bits(v)))
    pos0 = property(lambda self: tuple(_float(b) for b in self.pos0_bits),
                    lambda self, v: setattr(self, "pos0_bits", tuple(_bits(x) for x in tuple(v) + (0.0,) * (4 - len(v)))))
    pos1 = property(lambda self: tuple(_float(b) for b in self.pos1_bits),
                    lambda self, v: setattr(self, "pos1_bits", tuple(_bits(x) for x in tuple(v) + (0.0,) * (4 - len(v)))))

    @classmethod
    def from_words(cls, w):
        s = cls.__new__(cls)
        s.type, s.bone0, s.bone1, s.radius_bits = w[0], w[1], w[2], w[3]
        s.pos0_bits, s.pos1_bits = tuple(w[4:8]), tuple(w[8:12])
        s.unk, s.id, s.shrink_bits, s.unk2 = w[12], w[13], w[14], w[15]
        return s

    def words(self):
        return (self.type, self.bone0, self.bone1, self.radius_bits, *self.pos0_bits, *self.pos1_bits, self.unk,
                self.id, self.shrink_bits, self.unk2)


class Group:
    __slots__ = ("kind", "flags", "pad", "shapes")

    def __init__(self, kind=0, flags=FLAG_PUSH, pad=0xFFFFFFFF, shapes=None):
        self.kind, self.flags, self.pad = kind, flags, pad
        self.shapes = shapes if shapes is not None else []


class Col:
    def __init__(self, groups=None, version=2, a=0xFFFFFFFF, b=0xFFFFFFFF):
        self.groups = groups if groups is not None else []
        self.version, self.a, self.b = version, a, b


def read(data):
    data = bytes(data)
    if data[:4] != MAGIC:
        raise ColError(f"not a collision shape file ({data[:4]!r})")
    magic, version, count, a, b = HEADER.unpack_from(data, 0)
    if version != 2:
        raise ColError(f"collision shape version {version} isn't supported (DX9 files are 2)")
    col = Col(version=version, a=a, b=b)
    at = HEADER.size
    for _ in range(count):
        if at + GROUP.size > len(data):
            raise ColError("file ends inside the group table (not a DX9 layout?)")
        n, kind, flags, pad = GROUP.unpack_from(data, at)
        if at + GROUP.size + SHAPE.size * n > len(data):
            raise ColError("file ends inside a group's shapes (not a DX9 layout?)")
        at += GROUP.size
        group = Group(kind, flags, pad)
        for _ in range(n):
            group.shapes.append(Shape.from_words(SHAPE.unpack_from(data, at)))
            at += SHAPE.size
        col.groups.append(group)
    if at != len(data):
        raise ColError(f"{len(data) - at} bytes after the last shape")
    return col


def write(col):
    out = bytearray(HEADER.pack(MAGIC, col.version, len(col.groups), col.a, col.b))
    for g in col.groups:
        out += GROUP.pack(len(g.shapes), g.kind, g.flags, g.pad)
        for s in g.shapes:
            out += SHAPE.pack(*s.words())
    return bytes(out)
