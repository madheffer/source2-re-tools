# nearstores.py <dll> <0xfield_off> <0xbit> [0xstart 0xend]: a linear sweep of .text (or a range) for stores to
# [reg + field_off] with an `or <anything>, bit` within 8 instructions before or after: protobuf setters the compiler
# built with the has-bits in a register (docs/game/README.md). Slow over a whole client.dll: minutes.
import sys, pefile, capstone
pe = pefile.PE(sys.argv[1], fast_load=True)
base = pe.OPTIONAL_HEADER.ImageBase
img = pe.get_memory_mapped_image()
text = next(s for s in pe.sections if s.Name.rstrip(b'\0') == b'.text')
t0, tn = text.VirtualAddress, text.Misc_VirtualSize
fo, bit = int(sys.argv[2], 16), int(sys.argv[3], 16)
a = int(sys.argv[4], 16) - base if len(sys.argv) > 5 else t0
e = int(sys.argv[5], 16) - base if len(sys.argv) > 5 else t0 + tn
raw = bytes(img[a:e])
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
md.skipdata = True
want = f' + 0x{fo:x}], '
orb = f', 0x{bit:x}'
def has_bit(op):
    # an `or x, imm` whose immediate has the bit (bts: the bit's index)
    t = op.rsplit(', ', 1)[-1]
    try:
        v = int(t, 16) if t.startswith('0x') else int(t)
    except ValueError:
        return False
    return (v & bit) != 0 or (v == bit.bit_length() - 1 and v > 0 and False)
win = []
pending = []
for ins in md.disasm_lite(raw, base + a):
    addr, size, mn, op = ins
    win.append((addr, mn, op))
    if len(win) > 17: win.pop(0)
    if mn == 'mov' and want in op and op.startswith('dword ptr [') and 'rip' not in op and 'rsp' not in op and 'rbp' not in op:
        pending.append((addr, mn, op, len(win)))
    # decide a pending store once 8 more instructions have passed
    while pending and len(win) - pending[0][3] >= 8 or (pending and len(win) == 17 and win[0][0] > pending[0][0]):
        p = pending.pop(0)
        if any(m in ('or', 'bts') and has_bit(o) for (_, m, o) in win):
            print(f"{p[0]:x}: {p[1]} {p[2]}", flush=True)
