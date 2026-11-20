# deathcam_oracle.py <client.dll> <out.json> [count]: the death cam's maths run in client.dll 2026-10-15 under Unicorn,
# for web/src/cs2web/client/core/death-cam-test.mjs (docs/game/death-cam.md):
#   180889e20 (the pull back's ease: spec_freeze_traveltime read through 180160b10 from a planted ConVar value),
#   18173cb10 (AngleDiff: tier0's V_fmodf), 181742a00 (VectorAngles: tier0's V_atan2f), 1817438a0 ((1 - V_cosf(x pi)) / 2).
# tier0.dll itself for the maths (tier0_link.py: the tier0 build beside the client's, the CRT's SSE2 path).
import sys, json, random, struct
import pefile
import tier0_link
from unicorn import Uc, UC_ARCH_X86, UC_MODE_64
from unicorn.x86_const import *

dll, out = sys.argv[1], sys.argv[2]
count = int(sys.argv[3]) if len(sys.argv) > 3 else 2000
pe = pefile.PE(dll, fast_load=True)
B = pe.OPTIONAL_HEADER.ImageBase
img = pe.get_memory_mapped_image()
STACK, HEAP, STOP = 0x20000000, 0x30000000, 0x40000000
F_TRAVEL, F_ANGDIFF, F_VECANG, F_EASE = 0x180889e20, 0x18173cb10, 0x181742a00, 0x1817438a0
CVAR_TRAVEL = 0x18252b798  # spec_freeze_traveltime's object: its value at [+8] + 0x58

uc = Uc(UC_ARCH_X86, UC_MODE_64)
uc.mem_map(B, (len(img) + 0xfff) & ~0xfff)
uc.mem_write(B, bytes(img))
for a in (STACK, HEAP, STOP):
    uc.mem_map(a, 0x100000)
uc.mem_write(STOP, b'\xc3')
tier0_link.link(uc, pe, dll.replace('client_', 'tier0_'), ['V_fmodf', 'V_atan2f', 'V_cosf'])
VALUE = HEAP + 0x1000
uc.mem_write(CVAR_TRAVEL + 8, struct.pack('<Q', VALUE))


def f32(x):
    return struct.unpack('<f', struct.pack('<f', x))[0]


def bits(x):
    return struct.unpack('<I', struct.pack('<f', x))[0]


def xmm(i):
    return struct.unpack('<f', uc.reg_read(UC_X86_REG_XMM0 + i).to_bytes(16, 'little')[:4])[0]


def set_xmm(i, v):
    uc.reg_write(UC_X86_REG_XMM0 + i, int.from_bytes(struct.pack('<f', v) + b'\0' * 12, 'little'))


def call(fn, ints=(), floats=None):
    rsp = STACK + 0x80000
    uc.mem_write(rsp, struct.pack('<Q', STOP))
    for r, v in zip([UC_X86_REG_RCX, UC_X86_REG_RDX, UC_X86_REG_R8, UC_X86_REG_R9], ints):
        uc.reg_write(r, v)
    for i, v in (floats or {}).items():
        set_xmm(i, v)
    uc.reg_write(UC_X86_REG_RSP, rsp)
    uc.emu_start(fn, STOP, count=200_000)


rng = random.Random(1458)
travel, angdiff, vecang, ease = [], [], [], []
for n in range(count):
    t = f32(rng.choice([0.3, 0.3, 0.3, rng.uniform(0.01, 2)]))
    e = f32(rng.choice([rng.uniform(-0.5, 1.0), rng.uniform(0.0625, 0.4), rng.uniform(0, 5), 0.0625, 0.3625]))
    uc.mem_write(VALUE + 0x58, struct.pack('<f', t))
    call(F_TRAVEL, floats={0: e})
    travel.append([bits(e), bits(t), bits(xmm(0))])
    a, b = f32(rng.uniform(-720, 720)), f32(rng.choice([rng.uniform(-720, 720), rng.uniform(-90, 90)]))
    call(F_ANGDIFF, floats={0: a, 1: b})
    angdiff.append([bits(a), bits(b), bits(xmm(0))])
    v = [f32(rng.uniform(-200, 200)) for _ in range(3)]
    if n % 50 == 0: v[0] = v[1] = 0.0
    if n % 77 == 0: v[2] = 0.0
    uc.mem_write(HEAP + 0x200, struct.pack('<3f', *v))
    call(F_VECANG, ints=(HEAP + 0x300, HEAP + 0x200))
    vecang.append([bits(x) for x in v] + list(struct.unpack('<3I', bytes(uc.mem_read(HEAP + 0x300, 12)))))
    x = f32(rng.choice([rng.random(), 0.0, 1.0, rng.uniform(0, 0.01)]))
    call(F_EASE, floats={0: x})
    ease.append([bits(x), bits(xmm(0))])
json.dump({'dll': dll.replace('\\', '/').split('/')[-1], 'travel': travel, 'angleDiff': angdiff, 'vectorAngles': vecang, 'ease': ease}, open(out, 'w'))
print(f'{count} cases each -> {out}')
