# python svccall.py <dll> <0xfield> <0xslot>: a load from [reg + field] followed within 10 instructions by
# `call qword ptr [reg + slot]`: who calls a services object's virtual
import sys, pefile, capstone
pe = pefile.PE(sys.argv[1], fast_load=True)
base = pe.OPTIONAL_HEADER.ImageBase
text = next(s for s in pe.sections if s.Name.rstrip(b'\0') == b'.text')
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
md.skipdata = True
field, slot = sys.argv[2].lower(), sys.argv[3].lower()
pend = None
for ins in md.disasm(text.get_data(), base + text.VirtualAddress):
    if ins.mnemonic == 'mov' and ins.op_str.endswith(f'+ {field}]') and 'rip' not in ins.op_str:
        pend = [ins.address, 0]
    elif pend:
        pend[1] += 1
        if ins.mnemonic == 'call' and ins.op_str.endswith(f'+ {slot}]'):
            print(f'{pend[0]:#x} -> {ins.address:#x}: {ins.op_str}'); pend = None
        elif pend[1] > 10 or ins.mnemonic in ('ret', 'int3'): pend = None
