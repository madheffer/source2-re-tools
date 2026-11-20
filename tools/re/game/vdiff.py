# The slots a derived class overrides (docs/game/README.md): two vtables side by side, the differing slots printed.
#   python tools/re/vdiff.py <dll> <base vtable> <derived vtable>
# Stops at the first slot that isn't a code pointer (0x18xxxxxxxx). Spawn is slot 0x48 in CS2's CBaseEntity.
import struct, sys
d = open(sys.argv[1], 'rb').read()
pe = struct.unpack_from('<I', d, 0x3c)[0]
nsec = struct.unpack_from('<H', d, pe + 6)[0]; opt = struct.unpack_from('<H', d, pe + 20)[0]
base = struct.unpack_from('<Q', d, pe + 24 + 24)[0]
secs = [struct.unpack_from('<IIII', d, pe + 24 + opt + i * 40 + 8) for i in range(nsec)]
def va2off(va):
    rva = va - base
    for vs, v, rs, raw in secs:
        if v <= rva < v + rs: return raw + rva - v
a, b = int(sys.argv[2], 16), int(sys.argv[3], 16)
for i in range(0, 0x900, 8):
    x = struct.unpack_from('<Q', d, va2off(a + i))[0]; y = struct.unpack_from('<Q', d, va2off(b + i))[0]
    if y >> 32 != 1: break
    if x != y: print(hex(i), hex(x), hex(y))
