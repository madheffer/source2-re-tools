# python enumtab.py <dll> <string>: find 8-byte pointers to the string in the image and print the neighbouring
# pointer/value pairs (an enum name table: {name*, value} or name*[] arrays)
import sys, struct, pefile
pe = pefile.PE(sys.argv[1], fast_load=True)
base = pe.OPTIONAL_HEADER.ImageBase
img = pe.get_memory_mapped_image()
s = sys.argv[2].encode() + b'\x00'
at = img.find(s)
while at > 0 and img[at - 1] != 0: at = img.find(s, at + 1)
va = base + at
print(f'string at {va:#x}')
needle = struct.pack('<Q', va)
i = img.find(needle)
def cstr(p):
    o = p - base
    if not (0 <= o < len(img)): return None
    e = img.find(b'\x00', o)
    t = img[o:e]
    return t.decode('ascii', 'replace') if 0 < len(t) < 80 and all(32 <= c < 127 for c in t) else None
while i >= 0:
    print(f'-- pointer at {base + i:#x}')
    for k in range(-30, 31):
        o = i + k * 8
        q = struct.unpack_from('<Q', img, o)[0]
        lo, hi = struct.unpack_from('<II', img, o)
        print(f'  {base + o:#x}: {cstr(q) or ""!s:40} lo={lo} hi={hi}')
    i = img.find(needle, i + 1)
