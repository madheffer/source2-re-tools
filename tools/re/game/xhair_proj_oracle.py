# xhair_proj_oracle.py <client.dll> <out.json> [count]: the crosshair's projections run in client.dll 2026-10-15 under
# Unicorn, for web/src/cs2web/client/settings/crosshair-proj-test.mjs (docs/game/settings.md "The crosshair's drawing"):
#   180d9e560 (the spread in pixels) with the real 180c19db0 / 180c19cd0 (world to screen through the view matrix at
#   18256b020 + slot * 0x40) and 180da17d0 (to pixels), and 181740910 (AngleVectors: the recoil point's forward).
# Stubs: the engine interface at 182560ed0 (vfunc 0x310: the view slot 0, vfunc 0x1e8: the screen's width / height),
# 1823bd0f0 set; tier0.dll itself for V_roundf / V_sincosf (tier0_link.py). The view matrix and the eye vectors are random f32 (a view-projection
# built as the client builds it: crosshair-proj.js viewCamera's rows), written to the case for the JS side to reuse.
import sys, json, random, struct, math
import pefile
import tier0_link
from unicorn import Uc, UC_ARCH_X86, UC_MODE_64, UC_HOOK_CODE
from unicorn.x86_const import *

dll, out = sys.argv[1], sys.argv[2]
count = int(sys.argv[3]) if len(sys.argv) > 3 else 500
pe = pefile.PE(dll, fast_load=True)
pe.parse_data_directories([pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_IMPORT']])
B = pe.OPTIONAL_HEADER.ImageBase
img = pe.get_memory_mapped_image()
STUB, STACK, HEAP, STOP = 0x10000000, 0x20000000, 0x30000000, 0x40000000
F_SPREAD, F_ANGVEC = 0x180d9e560, 0x181740910
G_FLAG, G_IFACE, G_MATRIX = 0x1823bd0f0, 0x182560ed0, 0x18256b020

uc = Uc(UC_ARCH_X86, UC_MODE_64)
uc.mem_map(B, (len(img) + 0xfff) & ~0xfff)
uc.mem_write(B, bytes(img))
for a in (STUB, STACK, HEAP, STOP):
    uc.mem_map(a, 0x100000)
uc.mem_write(STOP, b'\xc3')
stubs = {}
# tier0's own V_roundf / V_sincosf (tier0_link.py: the tier0 build beside the client's, same date)
tier0_link.link(uc, pe, dll.replace('client_', 'tier0_'), ['V_roundf', 'V_sincosf'])
# the engine interface: an object whose vtable's 0x310 / 0x1e8 are stubs
IFACE, VTBL = HEAP + 0x8000, HEAP + 0x9000
S310, S1E8 = STUB + 0x800, STUB + 0x810
stubs[S310], stubs[S1E8] = 'slot', 'size'
uc.mem_write(VTBL + 0x310, struct.pack('<Q', S310))
uc.mem_write(VTBL + 0x1e8, struct.pack('<Q', S1E8))
uc.mem_write(IFACE, struct.pack('<Q', VTBL))
uc.mem_write(G_IFACE, struct.pack('<Q', IFACE))
uc.mem_write(G_FLAG, struct.pack('<Q', 1))
state = {'w': 1920, 'h': 1080}


def f32(x):
    return struct.unpack('<f', struct.pack('<f', x))[0]


def xmm(i):
    return struct.unpack('<f', uc.reg_read(UC_X86_REG_XMM0 + i).to_bytes(16, 'little')[:4])[0]


def set_xmm(i, v):
    uc.reg_write(UC_X86_REG_XMM0 + i, int.from_bytes(struct.pack('<f', v) + b'\0' * 12, 'little'))


def hook(uc_, addr, size_, _):
    name = stubs.get(addr)
    if not name:
        return
    if name == 'V_roundf':
        x = xmm(0)
        set_xmm(0, f32(math.copysign(math.floor(abs(x) + 0.5), x)))
    elif name == 'V_sincosf':
        x = xmm(0)
        uc.mem_write(uc.reg_read(UC_X86_REG_RDX), struct.pack('<f', f32(math.sin(x))))
        uc.mem_write(uc.reg_read(UC_X86_REG_R8), struct.pack('<f', f32(math.cos(x))))
    elif name == 'slot':
        p = uc.reg_read(UC_X86_REG_RDX)
        uc.mem_write(p, struct.pack('<i', 0))
        uc.reg_write(UC_X86_REG_RAX, p)
    elif name == 'size':
        uc.mem_write(uc.reg_read(UC_X86_REG_RDX), struct.pack('<i', state['w']))
        uc.mem_write(uc.reg_read(UC_X86_REG_R8), struct.pack('<i', state['h']))
    rsp = uc.reg_read(UC_X86_REG_RSP)
    uc.reg_write(UC_X86_REG_RIP, struct.unpack('<Q', uc.mem_read(rsp, 8))[0])
    uc.reg_write(UC_X86_REG_RSP, rsp + 8)


uc.hook_add(UC_HOOK_CODE, hook, begin=STUB, end=STUB + 0x1000)


def call(fn, ints=(), floats=None):
    rsp = STACK + 0x80000
    uc.mem_write(rsp, struct.pack('<Q', STOP))
    for r, v in zip([UC_X86_REG_RCX, UC_X86_REG_RDX, UC_X86_REG_R8, UC_X86_REG_R9], ints):
        uc.reg_write(r, v)
    for i, v in (floats or {}).items():
        set_xmm(i, v)
    uc.reg_write(UC_X86_REG_RSP, rsp)
    uc.emu_start(fn, STOP, count=200_000)


def angvec(a):
    """Source AngleVectors in f32 (the rows the client builds its matrix from)."""
    d = math.pi / 180
    sp, cp, sy, cy = f32(math.sin(a[0] * d)), f32(math.cos(a[0] * d)), f32(math.sin(a[1] * d)), f32(math.cos(a[1] * d))
    sr, cr = f32(math.sin(a[2] * d)), f32(math.cos(a[2] * d))
    fwd = [f32(cp * cy), f32(cp * sy), f32(-sp)]
    right = [f32(f32(f32(-sr * sp) * cy) + f32(cr * sy)), f32(f32(f32(-sr * sp) * sy) - f32(cr * cy)), f32(-sr * cp)]
    up = [f32(f32(f32(cr * sp) * cy) + f32(sr * sy)), f32(f32(f32(cr * sp) * sy) - f32(sr * cy)), f32(cr * cp)]
    return fwd, right, up


rng = random.Random(64)
OBJ, CEN, MAT, ANG, VOUT = HEAP, HEAP + 0x200, HEAP + 0x300, HEAP + 0x400, HEAP + 0x500
cases = []
for n in range(count):
    W, H = rng.choice([(1920, 1080), (2560, 1440), (1280, 720), (1024, 768), (3440, 1440)])
    state['w'], state['h'] = W, H
    eye = [f32(rng.uniform(-6000, 6000)), f32(rng.uniform(-6000, 6000)), f32(rng.uniform(-500, 1500))]
    ea = [rng.uniform(-89, 89), rng.uniform(-180, 180), 0.0]
    va = [ea[0] + rng.uniform(-3, 3), ea[1] + rng.uniform(-3, 3), rng.uniform(-2, 2)]
    tv = f32(rng.choice([0.75, 0.75, 0.3, 0.1]))  # tan(vfov / 2): 90 at 4:3, zoomed
    th = f32(tv * W / H)
    ef, er, eu = angvec(ea)
    vf, vr, vu = angvec(va)
    sx, sy = f32(1 / th), f32(1 / tv)
    def dot(b):
        return f32(f32(f32(b[0] * eye[0]) + f32(b[1] * eye[1])) + f32(b[2] * eye[2]))
    def row(b, s):
        return [f32(b[0] * s), f32(b[1] * s), f32(b[2] * s), f32(-f32(dot(b) * s))]
    m = row(vr, sx) + row(vu, sy) + [0.0] * 4 + row(vf, 1.0)  # rows 0, 1, (2 unused), 3
    uc.mem_write(G_MATRIX, struct.pack('<16f', *m))
    # the crosshair object: +0x10 the eye, +0x1c forward, +0x28 right; the centre: forward x 2000 + eye on screen
    obj = struct.pack('<16x3f3f3f', *eye, *ef, *er)
    uc.mem_write(OBJ, obj.ljust(0x60, b'\0'))
    center = [f32(f32(ef[i] * 2000) + eye[i]) for i in range(3)]
    # the centre through the DLL too: 180c19db0 + 180da17d0 on forward x 2000 + eye
    uc.mem_write(CEN + 0x40, struct.pack('<3f', *center))
    call(0x180c19db0, ints=(CEN + 0x40, CEN))
    call(0x180da17d0, ints=(CEN,))
    cxy = list(struct.unpack('<3f', bytes(uc.mem_read(CEN, 12))))
    x = f32(rng.choice([0.0, 0.0006, 0.006, 0.05, 0.17, 0.3, rng.random() * 0.5]))
    uc.mem_write(HEAP + 0x700, struct.pack('<QQ', OBJ, CEN))
    call(F_SPREAD, ints=(HEAP + 0x700,), floats={1: x})
    px = xmm(0)
    # AngleVectors of a punched eye angle
    pa = [f32(ea[0] + rng.uniform(-6, 2)), f32(ea[1] + rng.uniform(-3, 3)), 0.0]
    uc.mem_write(ANG, struct.pack('<3f', *pa))
    uc.mem_write(VOUT, bytes(12))
    call(F_ANGVEC, ints=(ANG, VOUT))
    fwd = list(struct.unpack('<3f', bytes(uc.mem_read(VOUT, 12))))
    cases.append({'w': W, 'h': H, 'eye': eye, 'fwd': ef, 'right': er, 'm': m, 'x': x, 'center': cxy, 'spread': px, 'punched': pa, 'angFwd': fwd})
json.dump({'dll': dll.replace('\\', '/').split('/')[-1], 'cases': cases}, open(out, 'w', newline='\n'), indent=0)
print(f'{len(cases)} cases')
