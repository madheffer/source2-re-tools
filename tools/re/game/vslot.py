# Read vtable slots (docs/game/README.md): which function each class runs for a virtual.
#   python tools/re/vslot.py <dll> <vtable>[,<vtable>...] <slot offset>[,<slot offset>...]
# e.g. vslot.py server.dll 0x181972270,0x181972cc8 0x628,0x4f8  ->  "0x181972270 0x628:0x1802902a0 0x4f8:0x180d01630"
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
slots = [int(x, 16) for x in sys.argv[3].split(',')]
for vt in sys.argv[2].split(','):
    vt = int(vt, 16)
    print(hex(vt), ' '.join(f'{s:#x}:{struct.unpack_from("<Q", d, va2off(vt + s))[0]:#x}' for s in slots))
