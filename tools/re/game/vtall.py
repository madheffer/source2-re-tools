# vtall.py <dll> <ClassName> [slots]: every vtable of a class (any sub-object offset) through its RTTI, with its first slots
import struct, sys
d = open(sys.argv[1], 'rb').read()
pe = struct.unpack_from('<I', d, 0x3c)[0]
nsec = struct.unpack_from('<H', d, pe + 6)[0]; opt = struct.unpack_from('<H', d, pe + 20)[0]
base = struct.unpack_from('<Q', d, pe + 24 + 24)[0]
secs = []
for i in range(nsec):
    o = pe + 24 + opt + i * 40
    vs, va, rs, raw = struct.unpack_from('<IIII', d, o + 8)
    secs.append((va, vs, raw, rs))
def off2rva(off):
    for va, vs, raw, rs in secs:
        if raw <= off < raw + rs: return va + off - raw
name = sys.argv[2]
n = int(sys.argv[3]) if len(sys.argv) > 3 else 10
s = b'.?AV' + name.encode() + b'@@\0'
i = d.find(s)
if i < 0: sys.exit('no RTTI for ' + name)
td = off2rva(i - 0x10)
pat = struct.pack('<I', td)
j = 0
while True:
    j = d.find(pat, j + 1)
    if j < 0: break
    col = j - 12
    sig, offs = struct.unpack_from('<II', d, col)
    if sig != 1: continue
    colrva = off2rva(col)
    if colrva is None: continue
    k = d.find(struct.pack('<Q', base + colrva))
    while k >= 0:
        slots = [hex(struct.unpack_from('<Q', d, k + 8 + m * 8)[0]) for m in range(n)]
        print(name, 'offset', hex(offs), 'vtable', hex(base + off2rva(k) + 8), ' '.join(slots))
        k = d.find(struct.pack('<Q', base + colrva), k + 1)
