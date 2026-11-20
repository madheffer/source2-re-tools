# cvardefs.py <dll> <names file> <out.json>: many ConVars' registrations at once, decoded (docs/game/settings.md).
# cvardump.py prints one convar's raw setup stores; this one reads the two forms CS2's client.dll uses and writes
# { name: { site, handle, ctor, flags, help, type, default, min, max } } for each name it finds a definition of.
#   int / bool form (ctor 0x1819a6e40 in client 2026-11-12): a setup struct on the stack, [rsp+0x35] has-min /
#     has-max bytes (0x101 both), [rsp+0x37] the default, [rsp+0x47] min, [rsp+0x57] max; r8d the flags
#   float form (ctor 0x18015a620): builder(min) then builder(max) calls, each with xmm1; the default in xmm2 (set
#     before or just after the name's lea); r9d the flags
# A `lea rdx, "name" ; lea rcx, [handle] ; call` of another DLL's convar (a ConVarRef: volume, fps_max, snd_voip...)
# matches too; those come out with no default: read them in that DLL (engine2, soundsystem).
# Values from registers are followed back to a `mov reg, imm` / `xor reg, reg` inside the registration's own static
# initializer (each is a function of its own: the block starts after the previous one's tail jmp / int3).
import sys, re, json, struct, numpy as np, pefile, capstone

pe = pefile.PE(sys.argv[1], fast_load=True)
B = pe.OPTIONAL_HEADER.ImageBase
img = pe.get_memory_mapped_image()
text = [s for s in pe.sections if s.Name.startswith(b'.text')][0]
VA = text.VirtualAddress
data = np.frombuffer(img[VA:VA + text.Misc_VirtualSize], dtype=np.uint8)
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
n = len(data) - 7
m = (data[:n] == 0x48) & (data[1:n + 1] == 0x8d) & ((data[2:n + 2] & 0xc7) == 0x05)
idx = np.nonzero(m)[0]
disp = (data[idx + 3].astype(np.int64) | (data[idx + 4].astype(np.int64) << 8) | (data[idx + 5].astype(np.int64) << 16) | (data[idx + 6].astype(np.int64) << 24))
disp = np.where(disp >= 1 << 31, disp - (1 << 32), disp)
tgt = B + VA + idx + 7 + disp
reg = (data[idx + 2] >> 3) & 7  # ModRM reg: 2 = rdx


def cstr(a):
    o = a - B
    e = img.find(b'\0', o, o + 400)
    return img[o:e].decode('latin1') if e > o else ''


def ripaddr(ins):
    mm = re.search(r'rip ([+-]) (0x[0-9a-f]+)', ins.op_str)
    return ins.address + ins.size + (int(mm.group(2), 16) * (1 if mm.group(1) == '+' else -1)) if mm else None


def f32(a):
    return struct.unpack('<f', img[a - B:a - B + 4])[0]


def s32(v):
    return v - (1 << 32) if isinstance(v, int) and v >= 1 << 31 else v


def decode(name, i):
    start = max(0, i - 320)
    for s in range(0, 16):
        insns = list(md.disasm(bytes(data[start + s:i + 90]), B + VA + start + s))
        k = next((j for j, x in enumerate(insns) if x.address == B + VA + i), None)
        if k is not None:
            break
    else:
        return None
    after = insns[k + 1:k + 12]
    ci = next((j for j, x in enumerate(after) if x.mnemonic == 'call'), None)
    if ci is None:
        return None
    call = after[ci]
    hl = [x for x in after[:ci] if x.mnemonic == 'lea' and x.op_str.startswith('rcx, ') and 'rip' in x.op_str]
    if not hl:
        return None
    before = insns[:k]
    stop = next((j for j in range(len(before) - 1, -1, -1) if before[j].mnemonic in ('int3', 'ret', 'jmp')), -1)
    block = before[stop + 1:] + after[:ci]  # the float form sets xmm2 / flags after the name too
    stores, regs, xmm, builders = {}, {}, {}, []
    flags = help_ = None
    for x in block:
        mm = re.match(r'(byte|word|dword|qword) ptr \[rsp \+ (0x[0-9a-f]+)\], (.+)$', x.op_str)
        if x.mnemonic == 'mov' and mm:
            v = mm.group(3)
            v = regs.get(v, v)
            stores[int(mm.group(2), 16)] = int(v, 0) if isinstance(v, str) and re.match(r'^(0x[0-9a-f]+|\d+)$', v) else v
        elif x.mnemonic == 'mov' and re.match(r'^e[a-z0-9]+, (0x[0-9a-f]+|\d+)$', x.op_str):
            r_, v = x.op_str.split(', ')
            regs[r_] = int(v, 0)
        elif x.mnemonic == 'xor' and re.match(r'^(e[a-z0-9]+), \1$', x.op_str):
            regs[x.op_str.split(', ')[0]] = 0
        elif x.mnemonic == 'movss' and 'rip' in x.op_str:
            xmm[x.op_str.split(',')[0]] = f32(ripaddr(x))
        elif x.mnemonic == 'xorps' and re.match(r'^(xmm\d+), \1$', x.op_str):
            xmm[x.op_str.split(',')[0]] = 0.0
        elif x.mnemonic == 'call' and x is not call:
            builders.append((x.op_str, xmm.get('xmm1')))
        if x.mnemonic == 'mov' and re.match(r'^r[89]d, ', x.op_str):
            flags = x.op_str.split(', ')[1]
        if x.mnemonic == 'lea' and re.match(r'^(r9|rax), ', x.op_str) and 'rip' in x.op_str:
            s = cstr(ripaddr(x))
            if len(s) > 3 and ' ' in s:
                help_ = s
    rec = {'site': hex(B + VA + i), 'handle': hex(ripaddr(hl[-1])), 'ctor': call.op_str, 'flags': flags, 'help': help_}
    if 'xmm2' in xmm and len(builders) >= 2:
        rec.update(type='float', default=xmm['xmm2'], min=builders[-2][1], max=builders[-1][1])
    elif 0x37 in stores:
        hm = stores.get(0x35)
        rec.update(type='int', default=s32(stores[0x37]))
        if isinstance(hm, int) and hm & 0x01: rec['min'] = s32(stores.get(0x47))
        if isinstance(hm, int) and hm & 0x100: rec['max'] = s32(stores.get(0x57))
        if not isinstance(hm, int): rec['range'] = 'none (a bool, or set from a register: read the site)'
    return rec


names = [l.strip() for l in open(sys.argv[2]) if l.strip()]
out = {}
for name in names:
    rec = None
    at = img.find(b'\0' + name.encode() + b'\0')
    while at >= 0 and not rec:
        for i in idx[(tgt == B + at + 1) & (reg == 2)]:
            rec = decode(name, int(i))
            if rec:
                break
        at = img.find(b'\0' + name.encode() + b'\0', at + 1)
    out[name] = rec
    print(name, '-' if not rec else {k: rec.get(k) for k in ('type', 'default', 'min', 'max')})
json.dump(out, open(sys.argv[3], 'w', newline=''), indent=1)
