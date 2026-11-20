# A schema field's offset by its name (docs/game/README.md), from CS2's schema binding tables in the DLL.
#   python tools/re/schema.py <dll> <m_fieldName> [...]           every class's field of that name: "off? 0x..."
#   python tools/re/schema.py <dll> --near <field entry va> [lo hi]  the fields of the same class (entries 0x20
#                                                                   apart), optionally only offsets lo..hi
# A field entry is { const char *name; type *; int32 offset; ... } (0x20 bytes); the name pointer is found by its
# string's address. One name gives one line per class that has it: pick the class by its neighbours (--near).
import pefile, struct, sys, re
pe = pefile.PE(sys.argv[1], fast_load=True); b = pe.OPTIONAL_HEADER.ImageBase
img = pe.get_memory_mapped_image()
def cstr(va):
    o = va - b
    if not (0 <= o < len(img)): return None
    e = img.find(b'\0', o, o + 80)
    s = img[o:e]
    return s.decode() if s and all(32 <= c < 127 for c in s) else None
if sys.argv[2] == '--near':
    ref = int(sys.argv[3], 16)
    lo, hi = (int(sys.argv[4], 16), int(sys.argv[5], 16)) if len(sys.argv) > 5 else (0, 1 << 31)
    for k in range(-80, 80):
        a = ref + k * 0x20 - b
        n = cstr(struct.unpack_from('<Q', img, a)[0])
        if n:
            off = struct.unpack_from('<i', img, a + 16)[0]
            if lo <= off <= hi: print(hex(b + a), hex(off), n)
    sys.exit(0)
for name in sys.argv[2:]:
    for m in re.finditer(re.escape(name.encode()) + b'\x00', img):
        if img[m.start() - 1] != 0: continue
        pat = struct.pack('<Q', b + m.start())
        for p in re.finditer(re.escape(pat), img):
            off = struct.unpack_from('<i', img, p.start() + 16)[0]
            print(name, 'entry', hex(b + p.start()), 'off?', hex(off & 0xffffffff))
