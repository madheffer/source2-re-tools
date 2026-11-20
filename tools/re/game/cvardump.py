# cvardump.py <dll> <name> [...]: a ConVar's registration (docs/game/README.md): the object it registers (rcx; code
# reads the value through the pointer at object + 8, the value at that block's +0x58), its flags (r8d), help text
# (r9) and the default as the setup writes it on the stack before the call: printed as the setup's stores (a bool's
# default is the byte at +0x37 of the setup, its +0x34 the "has default" 1; ints / floats: read the stores).
import sys, struct, pefile, capstone
from capstone import x86
pe = pefile.PE(sys.argv[1], fast_load=True)
base = pe.OPTIONAL_HEADER.ImageBase
img = bytes(pe.get_memory_mapped_image())
text = next(s for s in pe.sections if s.Name.rstrip(b'\0') == b'.text')
t0, tn = text.VirtualAddress, text.Misc_VirtualSize
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
md.detail = True
def cstr(va):
    o = va - base
    return img[o:o + 200].split(b'\0')[0].decode('latin1') if 0 <= o < len(img) else ''
for name in sys.argv[2:]:
    nb = name.encode() + b'\0'
    o = img.find(nb)
    while o >= 0 and img[o - 1] != 0:
        o = img.find(nb, o + 1)
    if o < 0:
        print(f"{name}: not found"); continue
    sva = base + o
    # lea rdx, [rip + d] pointing at the name
    found = False
    for i in range(t0, t0 + tn - 7):
        if img[i] == 0x48 and img[i + 1] == 0x8d and img[i + 2] == 0x15:
            d = struct.unpack_from('<i', img, i + 3)[0]
            if base + i + 7 + d == sva:
                found = True
                ins = list(md.disasm(img[i - 160:i + 40], base + i - 160))
                k = next((n for n, x in enumerate(ins) if x.address == base + i), None)
                if k is None:  # misaligned start: decode from closer
                    ins = list(md.disasm(img[i - 60:i + 40], base + i - 60)); k = next((n for n, x in enumerate(ins) if x.address == base + i), 0)
                obj = help_ = flags = None
                # the registration call after the name: rcx (the object) is the last `lea rcx` before it
                call = next((n for n in range(k, min(len(ins), k + 12)) if ins[n].mnemonic == 'call'), k + 6)
                for x in ins[max(0, k - 30):call]:
                    if x.mnemonic == 'lea' and x.op_str.startswith('rcx, [rip'):
                        obj = x.address + x.size + x.operands[1].mem.disp
                    if x.mnemonic == 'lea' and x.op_str.startswith(('r9, [rip', 'rax, [rip')):
                        h = cstr(x.address + x.size + x.operands[1].mem.disp)
                        if len(h) > 12 and ' ' in h: help_ = h
                    if x.mnemonic == 'mov' and x.op_str.startswith(('r8d', 'r9d')):
                        flags = x.op_str.split(', ')[1]
                print(f"{name}: object 0x{obj or 0:x} (value via [0x{(obj or 0) + 8:x}] + 0x58), flags {flags}\n  help: {help_!r}")
                for x in ins[max(0, k - 30):k]:
                    if 'rsp +' in x.op_str and x.mnemonic.startswith('mov') and x.op_str.startswith(('byte', 'dword', 'qword', 'word')):
                        s = f"    {x.address:x}: {x.mnemonic} {x.op_str}"
                        print(s)
                    if x.mnemonic in ('movss', 'movsd') and 'rip' in x.op_str:
                        t = x.address + x.size + x.operands[1].mem.disp - base
                        print(f"    {x.address:x}: {x.mnemonic} {x.op_str}  ; f32 {struct.unpack_from('<f', img, t)[0]!r} f64 {struct.unpack_from('<d', img, t)[0]!r}")
                break
    if not found:
        print(f"{name}: no lea rdx registration")
