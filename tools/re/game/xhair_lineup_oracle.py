# xhair_lineup_oracle.py <client.dll> <out.json> [count]: CS2's grenade line-up crosshair (180da7770) and the friendly
# icon's rect run in client.dll 2026-10-15 under Unicorn, for web/src/cs2web/client/settings/crosshair-lineup-test.mjs
# (docs/game/settings.md "The grenade line-up crosshair"). tier0.dll itself for V_tanf / V_atanf / V_sincosf / V_powf /
# V_roundf (tier0_link.py); the CRT floorf (181a08ff8), 180c19db0 / 180c19cd0 / 180da17d0 / 180da8410 / 180da7640 /
# 18174a050 are client's own. Stubs: the engine interface at 182560ed0 (vfunc 0x310: view slot 0, 0x1e8: the screen
# size), the view render at 18256b9e8 (vfunc 0x88: the aspect, width / height in f32), the UtlVector allocator imports
# (a bump heap) and g_pMemAlloc's free. The crosshair object: +0 the list (64 x 0x40, the count at +0x1008), +0x10 the
# eye, +0x1c / +0x28 / +0x34 forward / right / up, +0x40 / +0x44 the centre, +0x54 the FOV, +0x58 the scale, +0xbc the
# fade; the convars' blocks at [1825c8510] (tickscaling f32), [1825c8520] (ticklabels byte), [1825c85d0 / 5e0 / 5f0 /
# 600] (cl_crosshaircolor_r / g / b / a ints), each value at +0x58.
import sys, json, random, struct, math
import pefile
import tier0_link
from unicorn import Uc, UC_ARCH_X86, UC_MODE_64, UC_HOOK_CODE
from unicorn.x86_const import *

dll, out = sys.argv[1], sys.argv[2]
count = int(sys.argv[3]) if len(sys.argv) > 3 else 300
pe = pefile.PE(dll, fast_load=True)
pe.parse_data_directories([pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_IMPORT']])
B = pe.OPTIONAL_HEADER.ImageBase
img = pe.get_memory_mapped_image()
STUB, STACK, HEAP, STOP, BUMP = 0x10000000, 0x20000000, 0x30000000, 0x40000000, 0x50000000
F_LINEUP = 0x180da7770
G_IFACE, G_MATRIX, G_VIEWRENDER = 0x182560ed0, 0x18256b020, 0x18256b9e8
CV = {'scaling': 0x1825c8510, 'labels': 0x1825c8520, 'r': 0x1825c85d0, 'g': 0x1825c85e0, 'b': 0x1825c85f0, 'a': 0x1825c8600}

uc = Uc(UC_ARCH_X86, UC_MODE_64)
uc.mem_map(B, (len(img) + 0xfff) & ~0xfff)
uc.mem_write(B, bytes(img))
for a in (STUB, STACK, HEAP, STOP):
    uc.mem_map(a, 0x100000)
uc.mem_map(BUMP, 0x1000000)
uc.mem_write(STOP, b'\xc3')
tier0_link.link(uc, pe, dll.replace('client_', 'tier0_'), ['V_tanf', 'V_atanf', 'V_sincosf', 'V_roundf', 'V_powf'])
stubs = {}


def stub(name):
    addr = STUB + 0x10 * (len(stubs) + 1)
    stubs[addr] = name
    uc.mem_write(addr, b'\xc3')
    return addr


for entry in pe.DIRECTORY_ENTRY_IMPORT:
    for imp in entry.imports:
        n = imp.name.decode() if imp.name else ''
        if n.startswith('UtlVectorMemory_'):
            uc.mem_write(imp.address, struct.pack('<Q', stub(n)))
        elif n == 'g_pMemAlloc':
            # a data import: the slot holds &g_pMemAlloc; [g_pMemAlloc] = the allocator, whose vtable +0x18 frees
            VAR, OBJA, VTA = HEAP + 0xa000, HEAP + 0xa100, HEAP + 0xa200
            uc.mem_write(VTA + 0x18, struct.pack('<Q', stub('free')))
            uc.mem_write(OBJA, struct.pack('<Q', VTA))
            uc.mem_write(VAR, struct.pack('<Q', OBJA))
            uc.mem_write(imp.address, struct.pack('<Q', VAR))
IFACE, VTBL = HEAP + 0x8000, HEAP + 0x9000
uc.mem_write(VTBL + 0x310, struct.pack('<Q', stub('slot')))
uc.mem_write(VTBL + 0x1e8, struct.pack('<Q', stub('size')))
uc.mem_write(IFACE, struct.pack('<Q', VTBL))
uc.mem_write(G_IFACE, struct.pack('<Q', IFACE))
uc.mem_write(0x1823bd0f0, struct.pack('<Q', 1))  # set, as in xhair_proj_oracle.py (180c19db0 reads the matrix then)
VR, VRT = HEAP + 0xb000, HEAP + 0xb100
uc.mem_write(VRT + 0x88, struct.pack('<Q', stub('aspect')))
uc.mem_write(VR, struct.pack('<Q', VRT))
uc.mem_write(G_VIEWRENDER, struct.pack('<Q', VR))
CVB = HEAP + 0xc000
for i, (k, g) in enumerate(CV.items()):
    uc.mem_write(g, struct.pack('<Q', CVB + 0x100 * i))
state = {'w': 1920, 'h': 1080, 'bump': BUMP}


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
    rcx, rdx, r8, r9 = (uc.reg_read(r) for r in (UC_X86_REG_RCX, UC_X86_REG_RDX, UC_X86_REG_R8, UC_X86_REG_R9))
    if name == 'slot':
        uc.mem_write(rdx, struct.pack('<i', 0))
        uc.reg_write(UC_X86_REG_RAX, rdx)
    elif name == 'size':
        uc.mem_write(rdx, struct.pack('<i', state['w']))
        uc.mem_write(r8, struct.pack('<i', state['h']))
    elif name == 'aspect':
        set_xmm(0, f32(f32(state['w']) / f32(state['h'])))
    elif name == 'UtlVectorMemory_CalcNewAllocationCount':
        uc.reg_write(UC_X86_REG_RAX, max(r8 & 0xffffffff, 2 * (rcx & 0xffffffff), 16))
    elif name == 'UtlVectorMemory_Alloc':
        # (old memory, ?, new bytes, old bytes): a fresh block, the old bytes copied
        p = state['bump']
        state['bump'] += (r8 + 15) & ~15
        if rcx and r9:
            uc.mem_write(p, bytes(uc.mem_read(rcx, r9)))
        uc.reg_write(UC_X86_REG_RAX, p)
    elif name == 'UtlVectorMemory_FailedAllocation':
        raise SystemExit('UtlVector allocation failed')
    rsp = uc.reg_read(UC_X86_REG_RSP)
    uc.reg_write(UC_X86_REG_RIP, struct.unpack('<Q', uc.mem_read(rsp, 8))[0])
    uc.reg_write(UC_X86_REG_RSP, rsp + 8)


uc.hook_add(UC_HOOK_CODE, hook, begin=STUB, end=STUB + 0x1000)
if '--debug' in sys.argv:
    def dbg(uc_, addr, size_, _):
        x = [struct.unpack('<4f', uc.reg_read(UC_X86_REG_XMM0 + i).to_bytes(16, 'little')) for i in (6, 7)]
        print(hex(addr), 'xmm6', x[0], 'xmm7', x[1], 'rsp', hex(uc.reg_read(UC_X86_REG_RSP)))
    for a in (0x180da7993, 0x180da7a05):
        uc.hook_add(UC_HOOK_CODE, dbg, begin=a, end=a)


def call(fn, ints=()):
    rsp = STACK + 0x80000
    uc.mem_write(rsp, struct.pack('<Q', STOP))
    for r, v in zip([UC_X86_REG_RCX, UC_X86_REG_RDX, UC_X86_REG_R8, UC_X86_REG_R9], ints):
        uc.reg_write(r, v)
    uc.reg_write(UC_X86_REG_RSP, rsp)
    uc.emu_start(fn, STOP, count=3_000_000)


def angvec(a):
    d = math.pi / 180
    sp, cp, sy, cy = f32(math.sin(a[0] * d)), f32(math.cos(a[0] * d)), f32(math.sin(a[1] * d)), f32(math.cos(a[1] * d))
    sr, cr = f32(math.sin(a[2] * d)), f32(math.cos(a[2] * d))
    fwd = [f32(cp * cy), f32(cp * sy), f32(-sp)]
    right = [f32(f32(f32(-sr * sp) * cy) + f32(cr * sy)), f32(f32(f32(-sr * sp) * sy) - f32(cr * cy)), f32(-sr * cp)]
    up = [f32(f32(f32(cr * sp) * cy) + f32(sr * sy)), f32(f32(f32(cr * sp) * sy) - f32(sr * cy)), f32(cr * cp)]
    return fwd, right, up


rng = random.Random(7770)
OBJ, LIST = HEAP, HEAP + 0x1000
cases = []
for n in range(count):
    W, H = rng.choice([(1920, 1080), (2560, 1440), (1280, 720), (1024, 768), (3440, 1440), (1680, 1050)])
    state['w'], state['h'] = W, H
    eye = [f32(rng.uniform(-6000, 6000)), f32(rng.uniform(-6000, 6000)), f32(rng.uniform(-500, 1500))]
    ea = [rng.uniform(-89, 89), rng.uniform(-180, 180), 0.0]
    va = [ea[0] + rng.uniform(-2, 2), ea[1] + rng.uniform(-2, 2), rng.uniform(-1, 1)]
    fov = f32(rng.choice([90.0, 90.0, 75.0, 110.0, rng.uniform(40, 120)]))
    tv = f32(math.tan(math.radians(fov) / 2) * 0.75)
    th = f32(tv * W / H)
    ef, er, eu = angvec(ea)
    vf, vr, vu = angvec(va)
    sx, sy = f32(1 / th), f32(1 / tv)

    def dot(b):
        return f32(f32(f32(b[0] * eye[0]) + f32(b[1] * eye[1])) + f32(b[2] * eye[2]))

    def row(b, s):
        return [f32(b[0] * s), f32(b[1] * s), f32(b[2] * s), f32(-f32(dot(b) * s))]
    m = row(vr, sx) + row(vu, sy) + [0.0] * 4 + row(vf, 1.0)
    uc.mem_write(G_MATRIX, struct.pack('<16f', *m))
    scale = f32(H / 1080) if rng.random() < 0.7 else f32(rng.uniform(0.3, 3.0))
    fade = f32(rng.choice([1.0, 1.0, rng.random()]))
    cx, cy = float(math.floor(W * 0.5)), float(math.floor(H * 0.5))
    cv = {'scaling': f32(rng.choice([1.1, 1.1, 0.5, 2.0, rng.uniform(0.5, 2)])), 'labels': rng.choice([1, 1, 0]),
          'r': rng.choice([rng.randint(-20, 300), 50]), 'g': rng.randint(0, 255), 'b': rng.randint(0, 255), 'a': rng.choice([255, 200, rng.randint(-5, 270)])}
    uc.mem_write(CVB + 0x58, struct.pack('<f', cv['scaling']))
    uc.mem_write(CVB + 0x100 + 0x58, bytes([cv['labels']]))
    for i, k in enumerate('rgba'):
        uc.mem_write(CVB + 0x100 * (2 + i) + 0x58, struct.pack('<i', cv[k]))
    obj = bytearray(0x100)
    struct.pack_into('<Q', obj, 0, LIST)
    struct.pack_into('<3f3f3f3f', obj, 0x10, *eye, *ef, *er, *eu)
    struct.pack_into('<ff', obj, 0x40, cx, cy)
    struct.pack_into('<ff', obj, 0x54, fov, scale)
    struct.pack_into('<f', obj, 0xbc, fade)
    uc.mem_write(OBJ, bytes(obj))
    uc.mem_write(LIST, bytes(0x1010))
    state['bump'] = BUMP
    call(F_LINEUP, ints=(OBJ,))
    nlist = struct.unpack('<I', bytes(uc.mem_read(LIST + 0x1008, 4)))[0]
    shapes = []
    for i in range(min(nlist, 64)):
        e = bytes(uc.mem_read(LIST + i * 0x40, 0x40))
        shapes.append({'type': struct.unpack_from('<I', e, 0x14)[0], 'm0': struct.unpack_from('<4f', e, 0), 'm1': struct.unpack_from('<f', e, 0x10)[0],
                       'o': struct.unpack_from('<2f', e, 0x18), 'color': struct.unpack_from('<4f', e, 0x20), 'ocolor': struct.unpack_from('<4f', e, 0x30)})
    cases.append({'w': W, 'h': H, 'eye': eye, 'fwd': ef, 'right': er, 'up': eu, 'm': m, 'fov': fov, 'scale': scale, 'fade': fade,
                  'cx': cx, 'cy': cy, 'cv': cv, 'shapes': shapes})
json.dump({'dll': dll.replace('\\', '/').split('/')[-1], 'cases': cases}, open(out, 'w', newline='\n'), indent=0)
print(f'{len(cases)} cases, {sum(len(c["shapes"]) for c in cases)} shapes')
