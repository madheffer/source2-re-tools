# CS2's entity I/O inputs per class, from server.dll (docs/game/inputs.md).
#   python tools/re/inputs.py <server.dll> [--json out.json] [--rust sim/src/game/input_table.rs] [class or designer ...]
# A class's own inputs are its entity-API bindings: 0x50-byte records { +0x00 "C<Class>_API::<Input>", +0x08 display
# name, +0x10 description, +0x18 / +0x20 the parameter / return type getters, +0x28 metadata count, +0x30 metadata,
# +0x38 flags, +0x48 the handler } in .data. The input's name is the text after "::" (the dispatch's string pool folds
# case: 18054ba10 hashes the lower-cased text, 180524c70 compares with strnicmp). The dispatch (181373b60) tries the
# class's own table, then each base class's up the chain: the base chain here is the schema binding's (+0x08 name,
# +0x38 -> { u32 offset, binding* } the first base, +0x40 the datamap whose +0x10 is the same name).
# Designer names come from the entity class constructors: `lea <designer>` then `lea <Class>` a few bytes on.
import sys, struct, re, json, pefile
pe = pefile.PE(sys.argv[1], fast_load=True); B = pe.OPTIONAL_HEADER.ImageBase
img = bytes(pe.get_memory_mapped_image())
args = sys.argv[2:]
out_json = out_rust = None
if '--json' in args:
    i = args.index('--json'); out_json = args[i + 1]; del args[i:i + 2]
if '--rust' in args:
    i = args.index('--rust'); out_rust = args[i + 1]; del args[i:i + 2]

def q(va): return struct.unpack_from('<Q', img, va - B)[0]
def cstr(va):
    o = va - B
    if not (0 <= o < len(img)): return None
    e = img.find(b'\0', o, o + 200)
    if e <= o: return None
    s = img[o:e]
    return s.decode() if all(32 <= c < 127 for c in s) else None

secs = {s.Name.rstrip(b'\0'): (B + s.VirtualAddress, B + s.VirtualAddress + s.Misc_VirtualSize) for s in pe.sections}
t0, t1 = secs[b'.text']

# 1. the binding records, by the "_API::" strings they point at
api = {}
# (CBaseEntity's table also holds three "CBaseEntity_SharedAPI::" records: AddOutput, SetScale, IsMotionEnabled)
for m in re.finditer(rb'([A-Za-z]\w*?)_(?:Shared)?API::(\w+)\x00', img):
    api[B + m.start()] = (m.group(1).decode(), m.group(2).decode())
own = {}
for name in (b'.rdata', b'.data'):
    lo, hi = secs[name]
    for o in range(lo - B, hi - B - 0x50, 8):
        v = struct.unpack_from('<Q', img, o)[0]
        if v not in api: continue
        h = struct.unpack_from('<Q', img, o + 0x48)[0]
        if not (t0 <= h < t1): continue
        cls, inp = api[v]
        flags = struct.unpack_from('<Q', img, o + 0x38)[0]
        own.setdefault(cls, []).append({'input': inp, 'record': hex(B + o), 'handler': hex(h), 'flags': hex(flags)})

# 2. schema bindings: name -> base name
names = {}
for m in re.finditer(rb'C[A-Za-z0-9_]+\x00', img):
    names[B + m.start()] = m.group()[:-1].decode()
dlo, dhi = min(secs[b'.rdata'][0], secs[b'.data'][0]), max(secs[b'.rdata'][1], secs[b'.data'][1])
def binding_at(o):
    # a schema binding at image offset o: +0x08 a class name, +0x20 its size (u32) and field count, +0x38 0 or a
    # base entry { u32 offset, binding* } whose binding names a class too. Returns (name, base name) or None
    v = struct.unpack_from('<Q', img, o + 8)[0]
    if v not in names: return None
    size = struct.unpack_from("<I", img, o + 0x20)[0]
    if not (0 < size < 0x100000): return None
    bi = struct.unpack_from('<Q', img, o + 0x38)[0]
    if not bi: return (names[v], None)
    if not (dlo <= bi < dhi): return None
    bb = q(bi + 8)
    if not (dlo <= bb < dhi): return None
    bn = q(bb + 8)
    if bn not in names: return None
    return (names[v], names[bn])
base = {}
for name in (b'.rdata', b'.data'):
    lo, hi = secs[name]
    for o in range(lo - B, hi - B - 0x48, 8):
        r = binding_at(o)
        if r and (r[0] not in base or (base[r[0]] is None and r[1])): base[r[0]] = r[1]

# 3. designer -> class, from `lea r, [rip+d]` pairs
lea = re.compile(rb'[\x48\x4c]\x8d[\x05\x0d\x15\x1d\x25\x2d\x35\x3d](....)', re.S)
# The constructor's two stores: `lea r, [designer]` ... `mov qword ptr [rip + X], r` and the class name into X + 8
# (e.g. 1806198fd: func_button into 0x18208f300, CBaseButton into 0x18208f308)
import capstone
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
designer = {}
text = img[t0 - B:t1 - B]
stored = {}   # global VA -> string stored there
classes = set(base)
for m in lea.finditer(text):
    tgt = t0 + m.end() + struct.unpack('<i', m.group(1))[0]
    if not (secs[b'.rdata'][0] <= tgt < secs[b'.rdata'][1]): continue
    s = cstr(tgt)
    if not s or not (s in classes or re.fullmatch(r'[a-z][a-z0-9_]*', s)): continue
    ins = list(md.disasm(text[m.start():m.start() + 120], t0 + m.start()))
    if not ins or ins[0].mnemonic != 'lea': continue
    reg = ins[0].op_str.split(',')[0]
    volatile = reg in ('rax', 'rcx', 'rdx', 'r8', 'r9', 'r10', 'r11')
    # every store of the register into a global until it's overwritten (a call ends a volatile one): info_particle_
    # system's constructor loads CParticleSystem into rbp and stores it a few instructions on (1800d85a8)
    for i in ins[1:16]:
        mm = re.fullmatch(r'qword ptr \[rip \+ (0x[0-9a-f]+)\], (\w+)', i.op_str) if i.mnemonic == 'mov' else None
        if mm and mm.group(2) == reg:
            stored.setdefault(i.address + i.size + int(mm.group(1), 16), s)
            continue
        if i.mnemonic in ('ret', 'jmp') or (i.mnemonic == 'call' and volatile): break
        if i.op_str.split(',')[0].strip() in (reg, 'e' + reg[1:], reg + 'd'): break   # overwritten
for x, s in stored.items():
    c = stored.get(x + 8)
    if c in classes and s not in classes and re.fullmatch(r'[a-z][a-z0-9_]*', s):
        designer.setdefault(s, set()).add(c)
# Pairs the scan can't see, each read in its constructor: info_particle_system's (1800d83f0) stores its class name
# from rbp on a branch (1800d85a8) the linear walk above doesn't follow
for d, c in {'info_particle_system': 'CParticleSystem'}.items():
    designer.setdefault(d, set()).add(c)
clash = {d: sorted(c) for d, c in designer.items() if len(c) > 1}
designer = {d: next(iter(c)) for d, c in designer.items() if len(c) == 1}
if clash: print('designer names with more than one class (left out):', clash, file=sys.stderr)

def chain(cls):
    out = []
    while cls and cls not in out:
        out.append(cls); cls = base.get(cls)
    return out

def show(cls):
    print(f'{cls}: chain {" > ".join(chain(cls))}')
    for c in chain(cls):
        for r in own.get(c, []):
            print(f'  {c:28s} {r["input"]:36s} {r["handler"]} {r["record"]} flags={r["flags"]}')

if out_json:
    json.dump({'own': {c: [r['input'] for r in rs] for c, rs in own.items()}, 'base': base, 'designer': designer},
              open(out_json, 'w', newline='\n'), indent=1, sort_keys=True)
    print(f'{len(own)} classes with inputs, {len(base)} bindings, {len(designer)} designer names -> {out_json}')
if out_rust:
    # every designer's class and the chain under it; inputs as the DLL spells them (the lookup folds case)
    used = []
    for d in sorted(designer):
        for c in chain(designer[d]):
            if c not in used: used.append(c)
    used.sort()
    idx = {c: i for i, c in enumerate(used)}
    L = ['// Generated by tools/re/inputs.py --rust from server_20261105.dll: do not edit (docs/game/inputs.md).',
         '// CS2\'s entity I/O inputs: each class\'s own (its "<Class>_API::<Input>" bindings, in table order), its base',
         '// class (the schema binding\'s first base), and the designer names (the entity class constructors).',
         '',
         'use super::inputs::Class;',
         '',
         'pub const NO_BASE: u16 = u16::MAX;',
         '',
         f'pub static CLASSES: [Class; {len(used)}] = [']
    for c in used:
        b = base.get(c)
        bi = str(idx[b]) if b in idx else 'NO_BASE'
        ins = ', '.join(f'"{r["input"]}"' for r in own.get(c, []))
        L.append(f'    Class {{ name: "{c}", base: {bi}, inputs: &[{ins}] }},')
    L.append('];')
    L.append('')
    L.append('/// (designer name, class), sorted by the name\'s bytes (all lower case)')
    L.append(f'pub static DESIGNERS: [(&str, u16); {len(designer)}] = [')
    for d in sorted(designer, key=lambda s: s.encode()):
        L.append(f'    ("{d}", {idx[designer[d]]}),')
    L.append('];')
    open(out_rust, 'w', newline='\n').write('\n'.join(L) + '\n')
    print(f'{len(used)} classes, {len(designer)} designer names -> {out_rust}')
for a in args:
    show(designer.get(a, a))
