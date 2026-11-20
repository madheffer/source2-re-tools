# vtowner.py <dll> <0xfunc> [...]: every vtable slot pointing at a function, as "<Class> vtable 0x... slot N (0x...)"
# (docs/game/README.md). Each 8-byte pointer to the function in the image is walked back to the vtable's start (the
# slot after the complete-object locator pointer, an RTTI COL with signature 1), and the class read from its type
# descriptor ".?AV<Class>@@".
import sys, struct, pefile
pe = pefile.PE(sys.argv[1], fast_load=True)
base = pe.OPTIONAL_HEADER.ImageBase
img = bytes(pe.get_memory_mapped_image())
def q(o): return struct.unpack_from('<Q', img, o)[0]
def d(o): return struct.unpack_from('<I', img, o)[0]
def col_class(p):
    o = p - base
    if not (0 <= o < len(img) - 24) or d(o) != 1: return None
    td = d(o + 12)
    if not (0 < td < len(img) - 16): return None
    name = img[td + 16:td + 16 + 200].split(b'\0')[0]
    return name.decode('latin1') if name.startswith(b'.?A') else None
for a in sys.argv[2:]:
    f = int(a, 16)
    pat = struct.pack('<Q', f)
    i = img.find(pat)
    while i >= 0:
        if i % 8 == 0:
            j, cls = i, None
            for _ in range(1200):
                j -= 8
                cls = col_class(q(j))
                if cls: break
            if cls:
                slot = (i - (j + 8)) // 8
                print(f"{f:x}: {cls} vtable 0x{base + j + 8:x} slot {slot} (0x{slot * 8:x})")
        i = img.find(pat, i + 1)
