# A class's vtable(s) in an MSVC x64 DLL, found through its RTTI (docs/game/README.md).
#   python tools/re/rtti.py <dll> <ClassName> [<ClassName> ...]
# Finds the type descriptor ".?AV<Class>@@", the complete-object locators (signature 1, offset 0) that point at it,
# and every pointer to a locator: the vtable starts 8 bytes after it. Prints "<Class> vtable 0x...".
import struct, sys
d = open(sys.argv[1], 'rb').read()
pe = struct.unpack_from('<I', d, 0x3c)[0]
nsec = struct.unpack_from('<H', d, pe + 6)[0]; opt = struct.unpack_from('<H', d, pe + 20)[0]
base = struct.unpack_from('<Q', d, pe + 24 + 24)[0]
secs = []
for i in range(nsec):
    o = pe + 24 + opt + i * 40
    vs, va, rs, raw = struct.unpack_from('<IIII', d, o + 8)
    secs.append((d[o:o+8].rstrip(b'\0'), va, vs, raw, rs))
def off2rva(off):
    for n, va, vs, raw, rs in secs:
        if raw <= off < raw + rs: return va + off - raw
for name in sys.argv[2:]:
    s = b'.?AV' + name.encode() + b'@@\0'
    i = d.find(s)
    if i < 0: print(name, 'no RTTI'); continue
    td = off2rva(i - 0x10)
    pat = struct.pack('<I', td)
    j = 0
    while True:
        j = d.find(pat, j + 1)
        if j < 0: break
        col = j - 12
        sig, offs = struct.unpack_from('<II', d, col)
        if sig != 1 or offs != 0: continue
        colrva = off2rva(col)
        k = d.find(struct.pack('<Q', base + colrva))
        while k >= 0:
            print(name, 'vtable', hex(base + off2rva(k) + 8))
            k = d.find(struct.pack('<Q', base + colrva), k + 1)
