"""Symbolic run of straight-line scalar SSE (movss / mulss / addss / subss / xorps sign / movaps) over a listing of
"<hex address>: <mnemonic> <operands>" lines (capstone Intel syntax, as tools/re/disasm.py prints): prints each
store to [<outreg> + off] as an expression of the named input pointers' fields.
usage: symss.py <listing> <out reg> <name=reg>... [start addr] [end addr]
fields print as <name>[row][col] for 4x4 float matrices (offset / 4: row = i / 4, col = i % 4)"""
import re, sys

lst, outreg = sys.argv[1], sys.argv[2]
names, rng = {}, []
for a in sys.argv[3:]:
    if '=' in a:
        k, v = a.split('='); names[v] = k
    else:
        rng.append(int(a, 16))
lo, hi = (rng + [0, 1 << 40])[:2] if len(rng) >= 2 else ((rng[0] if rng else 0), 1 << 40)

def mem(op):
    m = re.match(r'dword ptr \[(\w+)(?: \+ (0x[0-9a-f]+|\d+))?\]', op)
    if not m: return None
    reg, off = m.group(1), int(m.group(2) or '0', 0)
    if reg in names:
        i = off // 4
        return f'{names[reg]}{i // 4}{i % 4}'
    return f'[{reg}+{off:#x}]'

regs, stack = {}, {}
for line in open(lst, encoding='utf-8'):
    m = re.match(r'([0-9a-f]+): (\w+)\s+(.*)', line.strip())
    if not m: continue
    addr, ins, ops = int(m.group(1), 16), m.group(2), m.group(3)
    if addr < lo or addr >= hi: continue
    parts = [p.strip() for p in re.split(r',(?![^\[]*\])', ops)]
    def val(op):
        if op.startswith('xmm'): return regs.get(op, op)
        mm = mem(op)
        if mm and mm.startswith('['): return stack.get(mm, mm)
        return mm
    if ins in ('movss', 'movaps'):
        d, s = parts
        if d.startswith('xmm'): regs[d] = val(s)
        else:
            key = mem(d)
            m2 = re.match(r'dword ptr \[(\w+)(?: \+ (0x[0-9a-f]+|\d+))?\]', d)
            if m2 and m2.group(1) == outreg:
                i = int(m2.group(2) or '0', 0) // 4
                print(f'out{i // 4}{i % 4} = {val(s)}')
            else: stack[key] = val(s)
    elif ins in ('mulss', 'addss', 'subss'):
        d, s = parts
        op = {'mulss': '*', 'addss': '+', 'subss': '-'}[ins]
        regs[d] = f'({regs.get(d, d)} {op} {val(s)})'
    elif ins == 'xorps' and parts[0].startswith('xmm'):
        if parts[1] == parts[0]: regs[parts[0]] = '0'
        else: regs[parts[0]] = f'-{regs.get(parts[0], parts[0])}'
    elif ins == 'mov' and 'dword ptr' in parts[0]:
        m2 = re.match(r'dword ptr \[(\w+)(?: \+ (0x[0-9a-f]+|\d+))?\]', parts[0])
        if m2 and m2.group(1) == outreg:
            i = int(m2.group(2) or '0', 0) // 4
            print(f'out{i // 4}{i % 4} = {parts[1]}')
