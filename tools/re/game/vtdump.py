# vtdump.py <dll> <0xvtable> [count]: a vtable's slots (offset, function VA, and the function's size up to its first
# ret when it's short), to find a class's small virtuals (a protobuf message's Clear / ByteSize, an accessor)
import sys, struct, pefile, capstone
pe = pefile.PE(sys.argv[1], fast_load=True)
base = pe.OPTIONAL_HEADER.ImageBase
img = bytes(pe.get_memory_mapped_image())
vt = int(sys.argv[2], 16)
n = int(sys.argv[3]) if len(sys.argv) > 3 else 24
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
for k in range(n):
    f = struct.unpack_from('<Q', img, vt - base + 8 * k)[0]
    if not (base <= f < base + len(img)): break
    size = 0
    for i in md.disasm(img[f - base:f - base + 600], f):
        size = i.address + i.size - f
        if i.mnemonic in ('ret', 'int3', 'jmp'): break
    print(f"slot {k:3d} (0x{8 * k:x}): 0x{f:x}  ~{size} bytes")
