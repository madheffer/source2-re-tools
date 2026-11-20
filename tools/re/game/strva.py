# strva.py <dll> <string> [...]: the virtual address of every occurrence of an exact NUL-terminated ASCII string in a
# DLL (preceded by a NUL too), for tools/re/riprefs.py (who references it). docs/game/README.md.
import sys, pefile
pe = pefile.PE(sys.argv[1], fast_load=True)
data = pe.__data__
base = pe.OPTIONAL_HEADER.ImageBase
def va(off):
    for s in pe.sections:
        if s.PointerToRawData <= off < s.PointerToRawData + s.SizeOfRawData:
            return base + s.VirtualAddress + off - s.PointerToRawData
    return None
for name in sys.argv[2:]:
    pat = b'\0' + name.encode() + b'\0'
    i, out = 0, []
    while True:
        i = data.find(pat, i)
        if i < 0: break
        v = va(i + 1)
        if v: out.append(hex(v))
        i += 1
    print(name, ' '.join(out) or 'not found')
