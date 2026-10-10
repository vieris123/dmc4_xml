"""DMC4 DX9 scheduler files (`.sdl`, `SDL\\0` version 16): byte-exact reader and writer, plain Python.

Layout (every DX9 file follows it, see the corpus test):

- header 0x14: magic, u16 version, u16 track count, u32 frames (bits 0-23; bit 24 = floor the frame before
  evaluating), u32 marker track (index of a track whose keys are the cut frames, usually 0 = none), u32 name area
  offset
- tracks, 0x18 each: u8 type, u8 property type, u16 key count, u32 parent, u32 name offset, u32 dti, u32 timing
  offset, u32 data offset (offsets from the file start, names from the name area)
- value area: per keyed track, in track order, the timing array (u32 per key: frame in bits 0-23, mode in 24-31) at
  the next 4-byte boundary, then the values at the next 16-byte boundary
- name area at the next 4-byte boundary: NUL-terminated track names and resource entries (u32 dti + path), each
  stored once; the file ends with the last string

Track `parent` is the owning track's index, except for units (type 2: the sUnit move line the unit is created on) and
system tracks (type 3: bound to a system singleton such as sCamera, parent unused). Object and value tracks use `dti`
as the array index when their property is an array. Ref values and the header's marker track are track indices.

Runtime (DX9 `rScheduler::keying` 0x90AF00, see Vibed/RE/sdl_scheduler_runtime.md): one frame = 1/60 s; key i's mode
governs the segment i -> i+1: 0 step, 1 / 4 counter (value + elapsed frames), 2 step written only on the tick that
reaches the key (one-shot), 3 linear, 5 uniform Catmull-Rom.
"""
import struct

MAGIC = b"SDL\0"
VERSION = 16
HEADER = struct.Struct("<4sHHIII")
TRACK = struct.Struct("<BBHIIIII")

# track types (4 is ignored by the game)
ROOT, UNIT, SYSTEM, ROOT2, OBJECT = 1, 2, 3, 4, 5
GROUP = SYSTEM      # older name
INT, VECTOR, FLOAT, BOOL, REF, RESOURCE, STRING, EVENT, CUSTOM = 6, 7, 8, 9, 10, 11, 12, 13, 14
CONTAINERS = (ROOT, UNIT, SYSTEM, ROOT2, OBJECT)
VALUE_TYPES = (INT, VECTOR, FLOAT, BOOL, REF, RESOURCE, STRING, EVENT, CUSTOM)
FLOOR_FRAME = 0x01000000    # frames word: floor the frame before evaluating

# property types (MtPropertyType)
P_CLASSREF, P_BOOL, P_U8, P_U16, P_U32, P_U64, P_S8, P_S16, P_S32, P_S64, P_F32 = 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12
P_EVENT, P_EVENT32, P_CUSTOM, P_RESOURCE = 0x18, 0x1C, 0x39, 0x3A

# int tracks keep every key in a 32-bit slot whatever the property's width (U8 / U16 included); bools are 1 byte
INT_FORMATS = {P_U8: "I", P_U16: "I", P_U32: "I", P_U64: "Q", P_S8: "i", P_S16: "i", P_S32: "i", P_S64: "q",
               P_BOOL: "I"}
VECTOR_SIZE = 16          # every vector key takes 16 bytes (4 floats), whatever the property type
CUSTOM_SIZE = 64


class SdlError(ValueError):
    pass


def value_size(track_type, prop_type):
    if track_type == VECTOR:
        return VECTOR_SIZE
    if track_type == BOOL:
        return 1
    if track_type == INT:
        return struct.calcsize("<" + INT_FORMATS[prop_type])
    if track_type == CUSTOM:
        return CUSTOM_SIZE
    return 4      # float, ref, resource, string, event


class Key:
    """frame (0..0xFFFFFF), mode (0..255) and a value: int, float, a tuple of 4 floats (vector), None or
    (dti, path) (resource), None or str (string), bytes (custom). `ref_ofs` is a resource / string's source offset."""
    __slots__ = ("frame", "mode", "value", "ref_ofs")

    def __init__(self, frame, mode, value, ref_ofs=None):
        self.frame, self.mode, self.value, self.ref_ofs = frame, mode, value, ref_ofs

    def __eq__(self, other):
        return (self.frame, self.mode, self.value) == (other.frame, other.mode, other.value)

    def __repr__(self):
        return f"Key({self.frame}, {self.mode}, {self.value!r})"


class Track:
    """`parent` is a track index (or the move line for units). `name_ofs` is the name's offset in the source file,
    kept only to reproduce its string order; new or renamed tracks leave it None."""
    __slots__ = ("type", "prop_type", "parent", "name", "dti", "keys", "name_ofs", "encoding")

    def __init__(self, type, prop_type=0, parent=0, name="", dti=0, keys=None, name_ofs=None, encoding="utf-8"):
        self.type, self.prop_type, self.parent, self.name, self.dti = type, prop_type, parent, name, dti
        self.keys = keys if keys is not None else []
        self.name_ofs, self.encoding = name_ofs, encoding

    def __repr__(self):
        return f"Track({self.type}, {self.prop_type:#x}, parent={self.parent}, {self.name!r}, keys={len(self.keys)})"


class Sdl:
    """`frames`: loop length (bits 0-23 of the header word); `flags`: its bits 24-31 (FLOOR_FRAME); `marker_track`:
    index of the track whose key frames are cuts (0 = none)."""

    def __init__(self, tracks=None, frames=0, version=VERSION, marker_track=0, flags=0):
        self.tracks = tracks if tracks is not None else []
        self.frames, self.version, self.marker_track, self.flags = frames, version, marker_track, flags


def _align(n, a):
    return (n + a - 1) & ~(a - 1)


def _cstring(data, pos):
    end = data.index(b"\0", pos)
    raw = data[pos:end]
    try:
        return raw.decode("utf-8"), "utf-8"
    except UnicodeDecodeError:
        return raw.decode("cp932"), "cp932"


def read(data):
    """bytes -> Sdl"""
    data = bytes(data)
    if len(data) < HEADER.size or data[:4] != MAGIC:
        raise SdlError(f"not an SDL file ({data[:4]!r})")
    magic, version, count, frames, marker_track, names = HEADER.unpack_from(data, 0)
    if version != VERSION:
        raise SdlError(f"SDL version {version} isn't supported (DX9 files are {VERSION})")
    sdl = Sdl(frames=frames & 0xFFFFFF, version=version, marker_track=marker_track, flags=frames >> 24)
    for i in range(count):
        ttype, prop, nkeys, parent, name_ofs, dti, timing, values = TRACK.unpack_from(data, HEADER.size + TRACK.size * i)
        name, enc = _cstring(data, names + name_ofs)
        track = Track(ttype, prop, parent, name, dti, name_ofs=name_ofs, encoding=enc)
        if ttype not in CONTAINERS and nkeys:
            size = value_size(ttype, prop)
            for k in range(nkeys):
                raw_t = struct.unpack_from("<I", data, timing + 4 * k)[0]
                at = values + size * k
                if ttype == VECTOR:
                    value = struct.unpack_from("<4f", data, at)
                elif ttype == FLOAT:
                    value = struct.unpack_from("<f", data, at)[0]
                elif ttype == BOOL:
                    value = data[at]
                elif ttype == INT:
                    value = struct.unpack_from("<" + INT_FORMATS[prop], data, at)[0]
                elif ttype == CUSTOM:
                    value = data[at:at + size]
                elif ttype == RESOURCE:
                    ofs = struct.unpack_from("<I", data, at)[0]
                    if ofs:
                        dti_ref = struct.unpack_from("<I", data, names + ofs)[0]
                        path, enc = _cstring(data, names + ofs + 4)
                        value = (dti_ref, path)
                    else:
                        value = None
                    track.keys.append(Key(raw_t & 0xFFFFFF, raw_t >> 24, value, ofs or None))
                    continue
                elif ttype == STRING:
                    ofs = struct.unpack_from("<I", data, at)[0]
                    value = _cstring(data, names + ofs)[0] if ofs else None
                    track.keys.append(Key(raw_t & 0xFFFFFF, raw_t >> 24, value, ofs or None))
                    continue
                else:     # ref, event: u32
                    value = struct.unpack_from("<I", data, at)[0]
                track.keys.append(Key(raw_t & 0xFFFFFF, raw_t >> 24, value))
        elif nkeys:
            raise SdlError(f"container track {i} ({name}) has {nkeys} keys")
        sdl.tracks.append(track)
    return sdl


def _pack_value(track, key):
    t, p, v = track.type, track.prop_type, key.value
    if t == VECTOR:
        v = tuple(v) + (0.0,) * (4 - len(v))
        return struct.pack("<4f", *v[:4])
    if t == FLOAT:
        return struct.pack("<f", v)
    if t == BOOL:
        return struct.pack("<B", v)
    if t == INT:
        size = struct.calcsize("<" + INT_FORMATS[p])
        return (int(v) & ((1 << (8 * size)) - 1)).to_bytes(size, "little")    # signed or unsigned range
    if t == CUSTOM:
        v = bytes(v)
        if len(v) != CUSTOM_SIZE:
            raise SdlError(f"{track.name}: custom value must be {CUSTOM_SIZE} bytes")
        return v
    return struct.pack("<I", v & 0xFFFFFFFF)


def _resource_entry(value):
    dti, path = value
    return struct.pack("<I", dti & 0xFFFFFFFF) + path.encode("utf-8") + b"\0"


class _Pool:
    """The name area. Strings with a source offset go back there (so untouched files come out identical; the source
    may share bytes between strings, e.g. a name that is the tail of another); the rest are appended, each once."""

    def __init__(self):
        self.placed = {}     # bytes or (bytes, source offset) -> offset
        self.area = bytearray()
        self.used = bytearray()
        self.new = []

    def _fits(self, ofs, raw):
        for i, c in enumerate(raw):
            j = ofs + i
            if j < len(self.area) and self.used[j] and self.area[j] != c:
                return False
        return True

    def want(self, raw, hint):
        """Reserve a string; returns the key that `offset` takes once `build` has run."""
        if hint is not None and (raw, hint) in self.placed:
            return (raw, hint)
        if hint is not None and self._fits(hint, raw):
            need = hint + len(raw)
            if len(self.area) < need:
                self.area += bytes(need - len(self.area))
                self.used += bytes(need - len(self.used))
            self.area[hint:need] = raw
            self.used[hint:need] = b"" * len(raw)
            self.placed[(raw, hint)] = hint
            self.placed.setdefault(raw, hint)
            return (raw, hint)
        if raw not in self.placed and raw not in self.new:
            self.new.append(raw)
        return raw

    def offset(self, key):
        return self.placed[key]

    def build(self):
        out = bytearray(self.area)
        for raw in self.new:
            self.placed[raw] = len(out)
            out += raw
        return bytes(out)


def write(sdl):
    """Sdl -> bytes"""
    tracks = sdl.tracks
    problems = []
    for i, t in enumerate(tracks):
        if t.type in CONTAINERS and t.keys:
            problems.append(f"track {i} ({t.name}): type {t.type} can't have keys")
        if t.type not in CONTAINERS and t.type not in VALUE_TYPES:
            problems.append(f"track {i} ({t.name}): unknown track type {t.type}")
        if t.type == INT and t.prop_type not in INT_FORMATS:
            problems.append(f"track {i} ({t.name}): property type {t.prop_type:#x} isn't an integer")
        for k in t.keys:
            if not 0 <= k.frame <= 0xFFFFFF or not 0 <= k.mode <= 0xFF:
                problems.append(f"track {i} ({t.name}): frame {k.frame} / mode {k.mode} out of range")
                break
    if len(tracks) > 0xFFFF:
        problems.append(f"{len(tracks)} tracks (65,535 at most)")
    if not 0 <= sdl.marker_track < max(len(tracks), 1):
        problems.append(f"marker track {sdl.marker_track} isn't a track")
    if not 0 <= sdl.frames <= 0xFFFFFF or not 0 <= sdl.flags <= 0xFF:
        problems.append(f"frames {sdl.frames} / flags {sdl.flags} out of range")
    if problems:
        raise SdlError("\n".join(problems))

    pool = _Pool()
    name_keys, ref_keys = [], {}
    for t in tracks:
        name_keys.append(pool.want(t.name.encode(t.encoding) + b"\0", t.name_ofs))
        if t.type in (RESOURCE, STRING):
            for k in t.keys:
                if k.value is not None:
                    entry = _resource_entry(k.value) if t.type == RESOURCE else k.value.encode("utf-8") + bytes(1)
                    ref_keys[id(k)] = pool.want(entry, k.ref_ofs)
    names = pool.build()

    values = bytearray()
    base = HEADER.size + TRACK.size * len(tracks)
    refs = []
    for t in tracks:
        if t.type in CONTAINERS or not t.keys:
            refs.append((0, 0))
            continue
        pos = base + len(values)
        timing = _align(pos, 4)
        values += bytes(timing - pos)
        for k in t.keys:
            values += struct.pack("<I", k.frame | (k.mode << 24))
        pos = base + len(values)
        at = _align(pos, 16)
        values += bytes(at - pos)
        for k in t.keys:
            if t.type in (RESOURCE, STRING):
                if k.value is None:
                    values += struct.pack("<I", 0)
                else:
                    values += struct.pack("<I", pool.offset(ref_keys[id(k)]))
            else:
                values += _pack_value(t, k)
        refs.append((timing, at))
    end = base + len(values)
    name_area = _align(end, 4)

    out = bytearray(HEADER.pack(MAGIC, sdl.version, len(tracks), sdl.frames | (sdl.flags << 24), sdl.marker_track,
                                name_area))
    for t, key, (timing, at) in zip(tracks, name_keys, refs):
        out += TRACK.pack(t.type, t.prop_type, len(t.keys), t.parent, pool.offset(key), t.dti, timing, at)
    out += values
    out += bytes(name_area - end)
    out += names
    return bytes(out)
