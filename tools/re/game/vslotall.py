# vslotall.py <dll> <0xslot> <Class> [...]: each class's function at a vtable slot (byte offset), through its RTTI
# vtable (the first complete-object locator with offset 0), to see which classes override a vfn (docs/game/README.md)
import sys, struct, subprocess, os, pefile
pe = pefile.PE(sys.argv[1], fast_load=True)
base = pe.OPTIONAL_HEADER.ImageBase
img = bytes(pe.get_memory_mapped_image())
slot = int(sys.argv[2], 16)
here = os.path.dirname(os.path.abspath(__file__))
out = subprocess.run([sys.executable, os.path.join(here, 'rtti.py'), sys.argv[1], *sys.argv[3:]], capture_output=True).stdout.decode()
seen = set()
for line in out.splitlines():
    p = line.split()
    if len(p) >= 3 and p[1] == 'vtable' and p[0] not in seen:
        seen.add(p[0])
        vt = int(p[2], 16)
        f = struct.unpack_from('<Q', img, vt - base + slot)[0]
        print(f"{p[0]}: slot 0x{slot:x} -> 0x{f:x}")
