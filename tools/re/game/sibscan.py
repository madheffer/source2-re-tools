# sibscan.py <dll> <0xdisp> [scale]: every mov / lea / cmp with a [base + index*scale + disp32] operand
import sys, re, pefile, capstone
pe = pefile.PE(sys.argv[1], fast_load=True)
disp = int(sys.argv[2], 16)
scale = int(sys.argv[3]) if len(sys.argv) > 3 else 8
base = pe.OPTIONAL_HEADER.ImageBase
text = [s for s in pe.sections if s.Name.startswith(b'.text')][0]
data = text.get_data()
va0 = base + text.VirtualAddress
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
ss = {1: 0, 2: 1, 4: 2, 8: 3}[scale]
pat = re.compile(rb'[\x40-\x4f]?[\x8b\x8d\x89\x39\x3b\x83\x63][\x04-\xbc]' + b'[' + bytes([ss << 6]) + b'-' + bytes([(ss << 6) | 0x3f]) + b']' + disp.to_bytes(4, 'little'))
for m in pat.finditer(data):
    for back in (0,):
        ins = next(md.disasm(data[m.start():m.start() + 16], va0 + m.start()), None)
        if ins and f'*{scale} + {hex(disp)}' in ins.op_str:
            print(hex(ins.address), ins.mnemonic, ins.op_str)
