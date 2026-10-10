"""MT Framework DTI hash (DX9 `MtCRC::getCRC` 0x8B6B40, see Vibed/RE/sdl_scheduler_runtime.md).

Not a CRC: every pair of adjacent characters (the trailing NUL counts as the last character) seeds an MT19937 with
((c0 - 32) << 6) | (c1 - 32) through the old Knuth sgenrand, and the generators' first tempered outputs are XORed
together, masked to 31 bits.
"""
from .classes import DTI_HASHES, RV_DTI_HASHES


def _first_output(seed):
    seed &= 0xFFFFFFFF
    mt = [0] * 624
    for i in range(624):                       # sgenrand: two LCG steps per state word
        mt[i] = seed & 0xFFFF0000
        seed = (69069 * seed + 1) & 0xFFFFFFFF
        mt[i] |= (seed & 0xFFFF0000) >> 16
        seed = (69069 * seed + 1) & 0xFFFFFFFF
    y = (mt[0] & 0x80000000) | (mt[1] & 0x7FFFFFFF)   # first word after the twist
    y = mt[397] ^ (y >> 1) ^ (0x9908B0DF if y & 1 else 0)
    y ^= y >> 11
    y ^= (y << 7) & 0x9D2C5680
    y ^= (y << 15) & 0xEFC60000
    y ^= y >> 18
    return y & 0xFFFFFFFF


def dti_hash(name):
    """class name -> DTI hash"""
    data = name.encode("ascii") + b"\0"
    h = 0
    for a, b in zip(data, data[1:]):
        h ^= _first_output((((a - 32) & 0xFFFFFFFF) << 6 | ((b - 32) & 0xFFFFFFFF)) & 0xFFFFFFFF)
    return h & 0x7FFFFFFF


def dti_id(text):
    """'uSe', '0x464a0bfe' or '1178209278' -> hash"""
    if text in DTI_HASHES:
        return DTI_HASHES[text]
    try:
        return int(text, 0)
    except ValueError:
        return dti_hash(text)


def dti_name(h):
    return RV_DTI_HASHES.get(h, f"{h:#010x}")
