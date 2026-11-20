# CS:GO (legacy, 32-bit) physics of ze_crazykart_v4's kart, traced from the binaries

Binaries: `csgo legacy/csgo/bin/server.dll` (md5 8048019154549052cb6dc057b76f6a85, Ghidra `/csgo_server_legacy.dll`)
and `csgo legacy/bin/vphysics.dll` (md5 d97cf2194594d7545427cdabc7376db4, Ghidra `/csgo_vphysics_legacy.dll`).
All addresses are VAs in those images (server base 0x10000000, vphysics base 0x10000000).
Tools: `re/tools/pe.py` (dd / f32 / dis / refs / vtable), `re/tools/scan.py` (capstone pattern scan),
`re/tools/parse_phy.py`, `re/tools/parse_mdl.py`, `re/tools/extract_kart.py`, `re/tools/vpk_get.py`,
`re/tools/kart_numbers.py` (the float32 numbers below).

Conventions used everywhere below:
- k = 0.0254f (vphysics 0x10106930, bits 3cd013a9), K = 39.370079f (0x10106934, bits 421d7af6),
  DEG = 57.29578f (vphysics 0x100f3fa0 / server 0x1098a204), RAD = 0.017453292f (vphysics 0x100f3bf4).
- Source <-> IVP axes (from CPhysicsObject::GetVelocity 0x1001d110 and every conversion read):
  `ivp = (src.x*k, -(src.z*k), src.y*k)`; `src = (ivp.x*K, ivp.z*K, -(ivp.y*K))`. Angular vectors use the same
  axis swap without k: `ivp_w = (w.x, -w.z, w.y)` (rad), `src_w = (ivp.x, ivp.z, -ivp.y)*DEG`.
- All arithmetic is IEEE single (SSE `mulss/addss`) unless noted; x87 is noted where it occurs (atan2, fmod,
  sin/cos, friction products). Sum orders are given as written in the disassembly.

---------------------------------------------------------------------------------------------------------------

## 1. The kart body (model, mass, inertia, material)

Source: BSP pakfile (`BSP.load(...).pak_zip()`), extracted by `extract_kart.py` to `re/kart/models/luffaren/`.

### luffaren_kartphys.mdl (the physics model, i_kart_phys)
- studiohdr v49, flags 0x11, 1 bone `static_prop`, pos (0,0,0), quat (0,0,0,1), poseToBone = identity, so the
  .phy vertices are model space = entity space.
- hull_min (-28.743, -21.675, -8.207), hull_max (31.757, 21.689, 7.917). surfaceprop "none", $mass 1246.6388,
  contents 0x1.
### luffaren_kartphys.phy (`parse_phy.py`)
- 1 solid, one convex ledge (is_compact 1), 56 triangles, all material index 0, 30 vertices. Vertex list (Source
  units, model space) is in the script output; the hull spans x [-28.49, 31.51], y [-21.43, 21.44], z [-7.96, 7.67].
- compact surface header: mass_center (IVP m) = (0.023804808, 0.006797736, 0.000179228) = Source
  **(0.93720, 0.00706, -0.26763)**; rotation_inertia (per unit mass, IVP axes) = **(0.0973081, 0.2032861,
  0.1793339)** (IVP y = Source vertical); upper_limit_radius 0.93437 m; dragAxisAreas (0.99325, 0.96505, 0.98760).
- text section: `solid { "mass" "1246.638794" "surfaceprop" "none" "damping" "0" "rotdamping" "0" "inertia" "1"
  "volume" "38037.285156" }`, `editparams { "totalmass" "1246.638794" "concave" "1" }`. No "drag", no
  "rotinertialimit".
### luffaren_kart.mdl (the visual, i_kart_visual, prop_dynamic parented, angles 0 270 0, solid 0)
- hull_min (-39.570, -46.927, -20.697), hull_max (39.570, 37.027, 29.122) (model space; rotated 270 yaw in the map),
  15 bones, surfaceprop "metal". Not simulated.

### Solid parameters as CS:GO builds them (server)
1. `PhysModelParseSolid` 0x1031a000: memset solid, then objectparams defaults (identical to the global
   g_PhysDefaultObjectParams at server 0x108ac5a8): massCenterOverride 0, mass 1, inertia 1, damping 0.1,
   rotdamping 0.1, rotInertiaLimit 0.05, name "DEFAULT", volume 0, dragCoefficient 1.0, enableCollisions 1.
2. vphysics ParseSolid 0x100338c0 overwrites from the .phy text: solid_t +0x618 mass, +0x61c inertia, +0x620 damping,
   +0x624 rotdamping, +0x634 volume, +0x638 drag ("drag" key), +0x400 surfaceprop. Kart: mass 1246.6388,
   inertia 1, damping 0, rotdamping 0, volume 38037.29, drag stays 1.0, rotInertiaLimit stays 0.05.
3. `CPhysicsProp::CreateVPhysics` 0x10357330 (vtable 0x108bc610 slot 0x268):
   - massScale (this+0x70c) > 0: mass *= massScale (kart: not set, 0).
   - inertiaScale (this+0x710) > 0: inertia *= inertiaScale, then max(inertia, 0.5). Kart: 1.0*1.0 = 1.0.
   - overridescript (this+0x718) -> `PhysSolidOverride` 0x102f7de0 builds `solid { "damping" "5" "rotdamping" "10" }`
     and re-parses it with a callback whose SetDefaults is a no-op (0x10059d70 `ret 4`), so only those two keys change.
     **Kart: damping 5, rotdamping 10.**
   - VPhysicsInitNormal(SOLID_VPHYSICS 6, 0, startAsleep = spawnflags & 1, &solid) (0x102082c0).
4. vphysics template (0x1001e6e0): mass = clamp(mass, 0.1, 50000); material = surfaceprops->GetIVPMaterial(index < 0
   ? 0 : index); inertia factor (all 3 axes) = clamp(inertia, <=0 -> 1, 1e18); speed damping = damping; rot damping
   (3 axes) = rotdamping; rotInertiaLimit copied. enableDrag only if dragCoefficient != 0 and not static (0x1001e7a0).
5. IVP_Real_Object core init 0x10074750 (core = object+0x94):
   - mass m (core+0x1c) = template mass (if < 0.003 -> 1.0).
   - rot inertia I_i (core+0x10..0x18) = (inertiaFactor_i * surface_rotation_inertia_i) * m.
   - rotInertiaLimit: L = sqrt((I0*I0 + I1*I1) + I2*I2) * 0.05; each I_i = max(I_i, L).
   - core+0x40 = speed damp = template+0x34 (raw), core+0x20..0x28 = rot damp = template+0x40.. (raw).
   - inverses: core+0x30..0x38 = 1/I, core+0x3c = 1/m (written by 0x10072af0 / init path).
   Kart (float32, `kart_numbers.py`): **m = 1246.6388, 1/m = 8.02157e-4; I (IVP x, y, z) = (121.30805, 253.42433,
   223.56458) kg m^2** (Source x = roll axis 121.31, Source z = yaw axis 253.42, Source y = pitch axis 223.56);
   limit L = 17.95 (not binding); 1/I = (0.008243476, 0.003945951, 0.0044729807).
- Mass centre (core position) = the .phy mass_center, Source (0.93720, 0.00706, -0.26763) from the body origin.

### Material ("none")
- vphysics clamps a negative surface index to 0 (0x1001e6e0). TODO: confirm that `GetSurfaceIndex("none")` returns
  -1 (server-side lookup of the solid's surfaceprop not read) and that index 0 is `default` (vphysics registers
  "default" first in its ctor 0x10018ae0 / parser 0x10019180, but the index assignment was not read).
- CS:GO `scripts/surfaceproperties_cs.txt` (pak01_dir.vpk; the manifest lists only this file) `"default"`:
  **density 2000, elasticity 0.25, friction 0.8, dampening 0.0**.
- The map fires `i_kart_phys AddOutput "material 1001"` at start (i_kart_start). TODO: what keyvalue "material" does
  on a CPhysicsProp in this server.dll (not read; it is not a surfaceprop index change as far as read).

---------------------------------------------------------------------------------------------------------------

## 2. phys_thruster (CPhysThruster : CPhysForce), server.dll

Entity offsets: spawnflags this+0x31c, angles this+0x2e8 (pitch) / +0x2ec (yaw) (m_angRotation, i.e. local angles;
the thrusters have no parent), force this+0x398, forcetime this+0x39c, attached entity handle this+0x3a0 and +0x3a0
(attach1), controller this+0x390, integrator (CConstantForceController) this+0x3a8: vtable, +4 controlType
(this+0x3ac), +8 linear (this+0x3b0), +0x14 angular (this+0x3bc); thruster local origin this+0x3e0.
Vtable base 0x108a4d40 (SetupForces slot 0x320 = 0x108a5060, OnActivate 0x108a5064, Spawn slot 0x64 = 0x108a4da4).

### Spawnflags (all read in the code below)
| bit | where | effect |
|---|---|---|
| 0x2 | SetupForces 0x102eecea | off -> linear result zeroed (no linear push) |
| 0x4 | SetupForces 0x102eecf9 | off -> angular result zeroed (no torque) |
| 0x8 | Spawn 0x102ee3d0, OnActivate 0x102ee940, SetupForces | local orientation: controlType = 1 (SIM_LOCAL_ACCELERATION) else 3 (SIM_GLOBAL_ACCELERATION): `((~flags & 8) | 4) >> 2`; OnActivate also converts the thruster's angles into the body's frame (MatrixAngles 0x1069af90 -> SetLocalAngles 0x101fe600); SetupForces uses LocalToWorld paths |
| 0x10 | SetupForces 0x102eeb3a | ignore mass: force vector *= body mass (GetMass, vslot 0x74), so the result is an acceleration = force |
| 0x20 | OnActivate 0x102eea56 | ignore position: local origin = (0,0,0) (= body origin, not the mass centre) |

Kart: **t_f 58 = 0x2|0x8|0x10|0x20** (linear, local, ignore mass, ignore pos); **t_s 28 = 0x4|0x8|0x10** (torque only,
local, ignore mass, uses its position); **t_u 50 = 0x2|0x10|0x20** (linear, world, ignore mass, ignore pos).

### OnActivate 0x102ee940 (called when the entity activates; not per Activate input)
local origin (this+0x3e0) = translation of (inverse(body EntityToWorld) x thruster transform)
(FUN_1069b0d0 invert, FUN_1069b500 concat). Kart t_s: thruster origin (-13800,14848,-15864) vs body (-13824,14848,
-15864) -> **local origin (24, 0, 0)**. With 0x20 it is zeroed.

### ActivateForce 0x102ee570 -> create 0x102ee610
- If a controller exists (this+0x390 != 0) the Activate is ignored (so a re-Activate never recomputes; the script
  always Deactivates first).
- Else: `SetupForces(pPhys, &linear, &angular)` (vslot 0x320) is evaluated **once**, stored in the integrator
  (+8 linear, +0x14 angular, copies at +0x3c8), `physenv->CreateMotionController(&integrator)` (env vslot 0x74),
  `AttachObject(pPhys, true)`, `pPhys->Wake()`. forcetime (this+0x39c) != 0 schedules ForceOff; the kart thrusters
  have no forcetime (0 = stays on). Changing "force"/"angles" while active has no effect until the next Activate.

### SetupForces 0x102eea80 (exact)
```
p = angRotation.x * 0.017453292 (x87), y = angRotation.y * 0.017453292
cp, sp = fcos/fsin(p) ; cy, sy = fcos/fsin(y)       (x87, results stored as float)
F = ( (cp*cy)*force, (cp*sy)*force, (-sp)*force )      force = this+0x398
if (flags & 0x10) F *= pPhys->GetMass()
if (flags & 0x8):
    worldPos = pPhys->LocalToWorld(localOrigin)            (vslot 0xe0)
    Fw       = pPhys->LocalToWorldVector(F)                (vslot 0xe8)
    pPhys->CalculateVelocityOffset(Fw, worldPos, &linW, &angular)   (vslot 0x100 = 0x1001ca30)
    linear   = pPhys->WorldToLocalVector(linW)             (vslot 0xec)
else:
    worldPos = attached entity m_rgflCoordinateFrame (ent+0x194..) * localOrigin
    pPhys->CalculateVelocityOffset(F, worldPos, &linear, &angular)
if !(flags & 2) linear = 0 ; if !(flags & 4) angular = 0
```
### CalculateVelocityOffset, vphysics 0x1001ca30 (exact sum order)
core = object(+8)->core(+0x94); core+0x90..0x98 = mass-centre world position (IVP m, float);
core+0x60/0x70/0x80 = rows of the core->world rotation M; core+0x30..0x38 = 1/I, +0x3c = 1/m.
```
Fx = F.x*k ; Fy = -(F.z*k) ; Fz = F.y*k                       (IVP force)
rx = P.x*k - c.x ; ry = -(P.z*k) - c.y ; rz = P.y*k - c.z     (IVP lever arm from the mass centre)
cx = (ry*Fz) - (rz*Fy) ; cy = (rz*Fx) - (rx*Fz) ; cz = (rx*Fy) - (ry*Fx)
a0 = (m70*cy + m60*cx) + m80*cz      (M^T c, core-local)
a1 = (m74*cy + m64*cx) + m84*cz
a2 = (m78*cy + m68*cx) + m88*cz
angular (Source local, deg/s) = ( (invI.x*a0)*DEG, (invI.z*a2)*DEG, -((invI.y*a1)*DEG) )
linear  (Source, u/s)         = ( (Fx*invm)*K, (Fz*invm)*K, -((Fy*invm)*K) )
```
(The angular output is body-local; the linear output is in the frame of F.)
CalculateForceOffset (vslot 0xfc = 0x1001c8a0) is not used by thrusters: TODO if needed.

### CConstantForceController::Simulate, server 0x102edf00
Returns `controlType` (integrator+4) and copies linear (+8) and angular (+0x14) out unchanged every step.

### How vphysics applies it per PSI: CPhysicsMotionController::do_simulation_controller, vphysics 0x1001a4f0
For each attached core, `ret = event->Simulate(controller, pObject, dt, &L, &A)` (dt = PSI delta), then:
- ret 1 (SIM_LOCAL_ACCELERATION): `l = (L.x*k, -(L.z*k), L.y*k)` (core-local);
  `speed.y += ((m74*l.y + m70*l.x) + m78*l.z)*dt`, `speed.z += ((m84*l.y + m80*l.x) + m88*l.z)*dt`,
  `speed.x += ((m64*l.y + l.x*m60) + m68*l.z)*dt` (written `(sum*dt) + speed`);
  `rot.y(+0xc4) += (-(A.z*RAD))*dt ; rot.x(+0xc0) += (A.x*RAD)*dt ; rot.z(+0xc8) += (A.y*RAD)*dt`.
- ret 3 (SIM_GLOBAL_ACCELERATION): `speed += (L.x*k, -(L.z*k), L.y*k)*dt` (world), angular **added in core-local
  axes exactly like case 1** (no world->local transform of the angular part).
- ret 2 / 4 (FORCE variants) multiply by 1/m and 1/I (not used here).
- then the velocity clamp 0x10078650 (section 3). core+0xd0 = speed (world, IVP m/s), core+0xc0 = rot speed
  (core-local, rad/s); core+0xb0 / +0xa0 are the pending speed_change / rot_speed_change.

### Values for this kart (float32, identity orientation; `kart_numbers.py`)
- **t_f forward (force 3750, angles 0 0 0)**: F = 3750*m along local +x -> linear **3750.0 u/s^2 along local +x**,
  angular zeroed (no 0x4). Script value FORWARD_SPEED*max(speedmod,0.1).
- **t_f back (1500, angles 0 180 0)**: **-1500.0 u/s^2 along local x** (plus -1.3e-4 on y from cos/sin(pi) rounding).
- **t_u (angles -90 0 0 / 90 0 0, force |jumpamount|)**: world +z / -z, **force u/s^2**, control type 3 (world).
- **t_s (300, angles 0 90 0 / 0 270 0, at local (24,0,0))**: linear zeroed (no 0x2); angular (local) =
  **(-30.4995, ~0, +1258.1016) deg/s^2 for yaw 90** and (+30.4995, ~0, -1258.1016) for 270: yaw acceleration
  +-1258.10 deg/s^2 plus a roll term from the mass centre sitting 0.268 u below the origin.
  The script's SpinOut sets force 3000..: scale linearly (it also overwrites the angles' pitch/roll).
- These are per-second accelerations applied as `+= a*dt` each PSI while the controller exists.

---------------------------------------------------------------------------------------------------------------

## 3. vphysics.dll: step, damping, gravity, drag, limits, friction

### Physics step
- Server PhysFrame 0x102f9750 is called from `CPhysicsHook::FrameUpdatePostEntityThink` 0x102f6950 (after entity
  thinks) with `dt = (gpGlobals->frametime > 0) ? gpGlobals->interval_per_tick : 0`; a second call only when
  `sv_alternateticks` and maxclients == 1 (0x1020a530). dt is clamped to <= 0.1 and multiplied by phys_timescale
  (server convar 0x10a4c7b8, default "1"), then `physenv->Simulate(dt)` (env vslot 0x88 = 0x10014320).
- Init 0x102f5f60: `SetSimulationTimestep(0.015625)` (0x3c800000, env vslot 0x94 = 0x10014670: ivpEnv+0xa8 = dt,
  +0xac = 1/dt, +0x118 = expf(dt * -0.105360545) (0x100f4064 = ln 0.9); TODO what reads +0x118).
- Simulate 0x10014320: ignores dt <= 0.0001 or > 1, clamps > 0.1 to 0.1; if dt == PSI dt: one PSI
  (0x10084c80), else simulate_until(time + dt). **64-tick server: exactly one PSI of 1/64 s per tick.**
- Order of controllers inside a PSI: priorities gravity 1000 (0x10007cb0), drag 500 (0x10013010), motion
  controllers 500 (this+0x24, default 0x1f4 set at 0x1001b2fb). TODO: the IVP controller manager's order
  (ascending/descending, ties) and where the friction solver and position integration run in the PSI.
- TODO: IVP_Core PSI integration (position/orientation from speed/rot speed) not read.

### Gravity (and damping): the environment gravity controller, vphysics 0x10072170 (vtable 0x100e0a04)
```
for each core in the controller's list (back to front):
    if (core.flags0 & 0x10) continue          // pinned = motion disabled (set by EnableMotion(false), 0x10072af0)
    rotD = core.rotDamp (+0x20..), linD = core.speedDamp (+0x40)
    if (core.byte1 >= 2) { rotD += 0.1 each axis; linD += 0.1 }   // 0x100f3c60 = 0.1; TODO what byte+1 is
    damp_object(core, dt, rotD, linD)          // 0x10076f20
    commit async pushes (0x10077520): rot += rot_change, speed += speed_change, changes = 0
    g = (core.flags0 & 0x20) ? this+0x20 : this+0x10
    speed.y = g.y*dt + speed.y ; speed.z = g.z*dt + speed.z ; speed.x = dt*g.x + speed.x
```
**damp_object 0x10076f20 (exact)** (dt = event delta_time, the PSI dt):
```
r = (rotD.x*dt, rotD.y*dt, rotD.z*dt)
if ((r.y*r.y + r.x*r.x) + r.z*r.z  <  0.5):  fr_i = 1.0 - r_i          (0x100f3cf8 = 0.5)
else:                                         fr_i = expf(-r_i)         (CRT __libm_sse2_expf 0x100d8112)
s = dt*linD
if (s < 0.25): fs = 1.0 - s  else fs = expf(-s)                          (0x100f3cb0 = 0.25)
rot.z *= fr.z ; rot.x *= fr.x ; rot.y *= fr.y ; speed.x,y,z *= fs
```
Kart (dt 1/64, damping 5, rotdamping 10): r = 0.15625 per axis, |r|^2 = 0.0732 < 0.5 -> **rot *= 0.84375** each PSI;
s = 0.078125 < 0.25 -> **speed *= 0.921875** each PSI (if byte1 >= 2: 5.1 / 10.1 -> 0.9203125 / 0.8421875).

**Gravity vector**: server sets `physenv->SetGravity(0, 0, -sv_gravity)` (0x102f61b0, and init 0x102f5f60);
`sv_gravity` registered at 0x10014cd0 with default **"800"** ("World gravity."); the map never changes it.
SetGravity 0x10013a70: g_ivp = (g.x*k, -(k*g.z), g.y*k) = **(0, 20.32, 0) m/s^2 (Source -800 u/s^2 z)**.

### Drag: CDragController::do_simulation_controller, vphysics 0x10012db0 (vtable 0x100e1c1c)
Air density default **2.0** (ctor 0x100134c3 `mov [eax+4], 0x40000000`); `air_density` is only a console command
(server 0x102fb9f0). Per core with drag enabled (prop drag coefficient 1.0, enabled because != 0):
```
v = speed (world) ; vl = M^T v  (vl.x = m70*v.y + v.x*m60 + m80*v.z, vl.y = col1.v, vl.z = col2.v)
f = (((|vl.y|*basis[0x28] + |vl.x|*basis[0x24]) + |vl.z|*basis[0x2c]) * dragCoef(+0x44)) * -0.5 * density * dt
f = max(f, -1); if (f < 0) speed += speed*f
fa = -((((|w.y|*abasis[0x34] + |w.x|*abasis[0x30]) + |w.z|*abasis[0x38]) * angDragCoef(+0x48)) * density * dt)
fa = max(fa, -1); if (fa < 0) rot += rot*fa
```
(basis/abasis/coefs are CPhysicsObject fields, object+0x24..0x48; written by 0x1001b3f0 and the drag-basis
builder 0x1001bc70 from the .phy dragAxisAreas.) The builder is traced in section 11.

### Velocity limits (0x10078650, after every motion-controller application and impulses)
Server SetPerformanceSettings (env vslot 0xec = 0x10015070) with {10, 250, maxVelocity 2000, maxAngularVelocity
3600, 1.0, 0.5, minFrictionMass 10, maxFrictionMass 2500} (server 0x102f5f9c..). vphysics stores max_velocity =
2000*k = 50.8 m/s and max angular = 3600*RAD*ivpEnv.psiTime (psiTime at that call, which precedes
SetSimulationTimestep; TODO the default). The clamp scales speed (and speed_change) to max_velocity when |v| exceeds
it. TODO: exact disassembly of the angular part of 0x10078650 (decompiler output ambiguous).

### Friction / elasticity between the kart and the world
CIVPMaterialManager (vtable 0x100e20cc, object 0x101160e8):
- get_friction_factor 0x10018970: unless the player-controller override 0x10026f60 applies (an object with
  callback flag 0x40), **mu = mat0.friction * mat1.friction** (x87 fmul, rounded to float), clamped to [0, 1].
- get_elasticity 0x10018a20: **e = mat0.elasticity * mat1.elasticity**, clamped <= 1.0.
- 0x1008e020 / 0x1008e050: sums of two other per-material values (IVP base class; TODO which fields).
Kart (default, friction 0.8) on a `default` world brush: mu = 0.64, e = 0.0625. World surfaces take their
surfaceprop from each brush texture's VMT `$surfaceprop` (TODO: list the map's ground materials).
Only one friction factor exists per contact (no separate static/dynamic coefficient in this path).
TODO: the IVP friction solver itself (ivp_friction.cxx 0x10083110 / 0x100816a0, ivp_mindist_friction.cxx 0x1008d230,
the friction impulse code around 0x100890a0) was not traced: how mu bounds the tangential impulse, the PSI order,
and the "minFrictionMass/maxFrictionMass" (10 / 2500) clamps.

---------------------------------------------------------------------------------------------------------------

## 4. phys_keepupright: CKeepUpright, server.dll

Entity: ctor 0x102f0270 (vtable 0x108a509c; motion-event subobject at this+0x390, vtable 0x108a53c0),
event fields: +4 worldGoalAxis (ent+0x394), +0x10 localTestAxis (ent+0x3a0), +0x28 angularlimit (ent+0x3b8, ctor
default 15.0 = 0x41700000), +0x2c active (ent+0x3bc), +0x2d dampAllRotation (ent+0x3bd, ctor 0).
- Spawn 0x102f0340: localTestAxis = (0,0,1); worldGoalAxis = the keepupright entity's own up vector
  (GetVectors(0,0,&up), vslot 0x220; angles 0 0 0 -> (0,0,1)); active = !(spawnflags & 1). Kart: spawnflags 0
  -> active at spawn; the script TurnOff/TurnOn (0x102efe80 / 0x102efe70 set/clear ent+0x3bc).
- Activate 0x102f03a0: physenv->CreateMotionController(event) and AttachObject(body, false).
- "angularlimit" KeyValue/AddOutput writes ent+0x3b8 directly (the script sets 150, then 5 after 2 s).

### Simulate 0x102f0500 (returns 1 = SIM_LOCAL_ACCELERATION, linear = 0)
```
if (!active) return 0 (SIM_NOTHING)
pPhys->GetVelocity(NULL, &w)              // local ang vel, deg/s (rot + pending rot change, 0x1001d110)
pPhys->GetPositionMatrix(&M)              // matrix3x4 rows
G (worldGoal -> local) : G.x = (g.x*M00 + g.y*M10) + g.z*M20
                         G.y = (g.x*M01 + g.y*M11) + g.z*M21
                         G.z = (g.x*M02 + g.y*M12) + g.z*M22
invDt = 1.0 / dt
r = ComputeRotSpeedToAlignAxes(T = localTestAxis, G, w, damping = dampAll ? 0 : 1, invDt, angularlimit)
angular = dampAll ? (r - w) * invDt : r * invDt        // per component: (r.x - w.x)*invDt ...
```
### ComputeRotSpeedToAlignAxes 0x102f06d0 (exact)
```
c.x = G.z*T.y - G.y*T.z ; c.y = G.x*T.z - T.x*G.z ; c.z = T.x*G.y - G.x*T.y      (T x G)
s = sqrtss((c.y*c.y + c.x*c.x) + c.z*c.z)
inv = 1.0 / (s + 1.1920929e-07)                    (0x1098971c)
d = (T.x*G.x + G.y*T.y) + T.z*G.z
a = c * inv
angle = fpatan(s, d) [= atan2(s, d), x87, stored float] * 57.29578
proj = (w.y*a.y + w.x*a.x) + w.z*a.z
r_i = ((a_i*invDt)*angle) - ((a_i*damping)*proj)
m = sqrtss((r.y*r.y + r.x*r.x) + r.z*r.z)
r_i = (r_i * (1.0/(m + 1.1920929e-07))) * min(m, angularlimit)
```
So each PSI the controller adds (via section 2's case 1, `rot += (A*RAD)*dt`) exactly r deg/s (damping 1: the
current spin about the correction axis is removed and replaced by angle/dt), limited to `angularlimit` deg/s per
step in magnitude. Kart: angularlimit 15 (map), 150 during ResetAngle for 2 s, then 5.

---------------------------------------------------------------------------------------------------------------

## 5. prop_physics_override spawnflags 13838 = 0x360E (0x2|0x4|0x8|0x200|0x400|0x1000|0x2000)

prop_physics_override is CPhysicsProp (Spawn 0x10356e70 renames the class to prop_physics). Bits read:
| bit | where | effect |
|---|---|---|
| 0x1 | CreateVPhysics 0x10357330 | start asleep (kart: off) |
| 0x2 | TODO | (no physics damage per SDK naming; not read) |
| 0x4 | Spawn 0x10356f09 | SetCollisionGroup(1 + (flags&0x1000 ? 1 : 0)) (0x1020a440). **Kart: 0x4 and 0x1000 -> group 2** |
| 0x8 | CreateVPhysics | **EnableMotion(false)** (also when damagetoenablemotion > 0 or forcetoenablemotion > 0); EnableMotion(false) = 0x10072af0: core flag 0x10 (pinned), 1/m and 1/I zeroed, velocities zeroed |
| 0x80 | Spawn | EFlags |= 0x200000 (kart: off) |
| 0x200 | CreateVPhysics | physics game flags |= 0x80 |
| 0x400 | TODO | not read |
| 0x1000 | Spawn | debris group variant above |
| 0x2000 | Spawn 0x10357113 | `m_pPhysicsProp interaction (+0x4d4) vslot 100 (2)`: TODO meaning |
| 0x200000 | CreateVPhysics | clears a byte of the solid before creation (kart: off) |

**Open problem (TODO, important):** with 0x8 the body is created pinned (1/m = 1/I = 0, skipped by gravity and
damping, thrusters give zero acceleration). Nothing in the kart's I/O or scripts sends EnableMotion (only the shell
items do), InputWake (0x102ff850) only calls Wake, ActivateForce and CKeepUpright::Activate do not enable motion.
What re-enables motion in-game is not found yet (candidates to read: CPhysicsProp's touch/damage paths for
flag 0x400 / physdamagescale, the "material" keyvalue, point_template spawning of i_kart).
Collision group 2: TODO CS:GO's ShouldCollide for group 2 (which objects the kart collides with).

---------------------------------------------------------------------------------------------------------------

## 6. VScript TraceLine(start, end, ignore), server.dll

Registered at 0x103e5970 (name 0x108e0c9c, binding 0x103e7d50, native **0x103e52a0**):
```
ignoreEnt = ignore ? HScript->entity : NULL
UTIL_TraceLine(start, end, MASK 0x2000b, ignoreEnt, COLLISION_GROUP 0, &tr)      (0x1016cc20)
return (tr.fractionleftsolid != 0 && tr.startsolid) ? 1.0 - tr.fractionleftsolid : tr.fraction
```
- Mask 0x2000b = CONTENTS_SOLID 0x1 | WINDOW 0x2 | GRATE 0x8 | MONSTERCLIP 0x20000 (MASK_NPCWORLDSTATIC by value):
  no CONTENTS_MONSTER / player bits, so players are not hit; solid props/brushes are.
- 0x1016cc20 builds the ray (FUN_1016ce70), a CTraceFilterSimple (vtable 0x108dce68, passentity = ignore,
  collisionGroup = 0) and calls enginetrace->TraceRay (vslot 0x14). trace_t offsets: fraction +0x2c,
  startsolid +0x37, fractionleftsolid +0x38. TODO: the filter's ShouldHitEntity body (0x108dce68 slot 0).

### CGameUI::Think 0x102a1530
Next think = `(int)(curtime / interval_per_tick + 0.5)` ticks (SetNextThink(gpGlobals->curtime)), i.e. **every
tick**. Buttons read from the player (+0xc9c): IN_MOVERIGHT 0x400 / IN_MOVELEFT 0x200 / IN_FORWARD 0x8 /
IN_BACK 0x10 / IN_ATTACK 0x1 / IN_ATTACK2 0x800; Pressed/Unpressed outputs fire on change.
TODO: frame order of ServiceEventQueue vs entity thinks vs PhysFrame (matters for the scripts' 0.00 / 0.01 delays:
a 0.01 s delay fires on the next tick, so Deactivate(0)+Activate(0.01) leaves the thruster off for one PSI if the
queue runs before PhysFrame).

---------------------------------------------------------------------------------------------------------------

## 7. self.GetAngles() / GetForwardVector / GetLeftVector / GetUpVector for the VPhysics prop

- PhysFrame -> CPhysicsProp::VPhysicsUpdate 0x10357cb0 -> CBaseEntity::VPhysicsUpdate 0x10207cd0:
  `pPhys->GetPosition(&origin, &angles)` (vslot 0xc0 = 0x100201e0), bogus checks (|angle| >= 360000 -> reset;
  |origin| >= 16384 -> ignored), then **for each of pitch, yaw, roll: `a = fmod(a, 360)` (CRT x87 fmod 0x107ba18a);
  `if (a > 180) a -= 360; if (a < -180) a += 360`**, then SetAbsOrigin / SetAbsAngles (0x101fdcd0).
- GetPosition: object matrix at the current PSI time (0x10074000) converted by 0x10001b90 (IVP matrix rows m[r][c],
  columns = object axes): `xy = sqrtss(m00*m00 + m20*m20)`;
  if (double)xy > 0.001: `yaw = atan2(m20, m00)*DEG`, `pitch = atan2(m10, xy)*DEG`,
  `roll = atan2(m12, -m11)*DEG + 180` (x87 fpatan each, stored float); else `yaw = atan2(m02, -m22)*DEG`,
  `pitch = atan2(m10, xy)*DEG`, `roll = 180`.
  Raw ranges: pitch [-90, 90], yaw [-180, 180], roll [0, 360]. **After VPhysicsUpdate's normalisation all three are
  in [-180, 180]** (roll of a level kart = 0; a kart tilted the other way reads small negative roll, not ~359).
  Consequence for the kart script's check `resang.z > 40 && resang.z < 320`: only positive roll above 40 triggers;
  pitch check `x > 40 && x < 140` only nose-down pitch above 40.
- VScript GetAngles = native 0x10205f80: returns the entity's abs angles (ent+0x1e8..0x1f0) after
  CalcAbsolutePosition when dirty.
- GetForwardVector 0x10206110 = GetVectors(&v, 0, 0); **GetLeftVector 0x102060e0 = GetVectors(0, &v, 0) = the
  second ("right") output**; GetUpVector 0x102060b0 = GetVectors(0, 0, &v). CBaseEntity::GetVectors 0x101faa60 on
  m_rgflCoordinateFrame (ent+0x194, rows): forward = column 0, **"left" = -column 1 (i.e. the RIGHT vector,
  each component's sign bit flipped)**, up = column 2.

---------------------------------------------------------------------------------------------------------------

## 8. The oracle: CS:GO's vphysics.dll run natively (rubikon/tests/KartOracle, 2026-11-16)

`rubikon/tests/KartOracle` (.NET, x86; build with the x64 SDK, run with the x86 runtime:
`DOTNET_ROOT="C:\Program Files (x86)\dotnet" bin/Release/net10.0/win-x86/KartOracle.exe <csgo legacy> <kart .phy> <scenario> <out>`)
loads csgo legacy's bin/tier0, vstdlib, vphysics and drives IVP through the interfaces exactly as the server does.
Bodies for the parts (2026-11-18): a `thruster` line takes `@<name>` after its local origin and an `upright` line
after its limit, to attach to that body (an extra kart, a mover, a physbox) instead of the kart; `upright on|off` and
`limit` events take the same `@<name>`, and a thruster's on / off / force / angles act on its own body.
Debug knobs (2026-11-18): `KART_ORACLE_SC=1` prints each ShouldCollide answer with `TICK` markers;
`KART_ORACLE_PAIRS=1` prints the kart's (and a mover's) +0x44, core flags and OV collisions at each setup step and
after each tick (Mindists.PairsAt); `KART_ORACLE_WATCH="<object> <offset hex, o prefix for the object> <from tick>
<to tick>"` (Watch.cs) puts a hardware write watchpoint on a field of that object's core (or the object itself) and
prints every write's vphysics EIP and stack: it found do_impact's revival friction (ivp-pileup.md 7). **Rebuild the
oracle (`dotnet build -c Release`) before regenerating an output after any change to it**: a stale build made
lift-pinned's first output.
Two runs of a scenario are byte-identical. `KART_ORACLE_STACKS=1` prints, once per distinct chain, the vphysics return
addresses on the stack at each callback (a raw-stack scan: dwords in vphysics' code preceded by a call), which is how
section 9's PSI chain was found. The kart's .phy and the BSP come from the map's pakfile
(`python -I docs/crazykart/tools/extract_kart.py <bsp> <out>`); the surface scripts from csgo/pak01_dir.vpk
(`docs/crazykart/tools/vpk_get.py <pak01_dir.vpk> surfaceproperties <out>`: the manifest lists only
scripts/surfaceproperties_cs.txt).

Interfaces (no RTTI in this vphysics; vtables found from the trace's known functions, slot order = the Source SDK's
interfaces, which CS:GO's match bar one object slot):
| Interface | Where | Slots used |
|---|---|---|
| CreateInterface "VPhysics031" | InterfaceReg 0x1010aa50, create 0x10003d20 -> singleton 0x1010aa20, vtable 0x100e0938 | 0 Connect, 3 Init, 9 CreateEnvironment (0x10003d50: new 0xec bytes, ctor 0x10013090) |
| "VPhysicsCollision007" | 0x10007ee0 -> 0x1010aa5c, vtable 0x100e0e2c | 29 BBoxToCollide (0x1000ad00), 36 VCollideLoad (0x1000b850: vcollide_t 16 bytes, solids at +4, text at +8) |
| "VPhysicsSurfaceProps001" | 0x10018ab0 -> 0x10116078, vtable 0x100e2114 (ctor 0x10018ae0) | 1 ParseSurfaceData (0x10019180), 3 GetSurfaceIndex |
| IPhysicsEnvironment | vtable 0x100e197c | 3 SetGravity, 7 CreatePolyObject, 8 CreatePolyObjectStatic, 29 / 30 Create / DestroyMotionController (0x10014d90 / 0x10014e00), 33 SetCollisionSolver, 34 Simulate (0x10014320), 37 SetSimulationTimestep, 50 EnableDeleteQueue, 59 SetPerformanceSettings |
| IPhysicsObject | vtable 0x100e26ec (a second one, 0x100e2878, differs in slots 0, 2, 46-55, 86-91) | 2 IsAsleep, 15 EnableMotion (0x1001bfe0: core 0x10072af0, then slots 26 / 27 RecheckCollisionFilter / RecheckContactPoints), 24 Wake, 29 GetMass, 48 GetPosition, 49 GetPositionMatrix, 52 GetVelocity, 56 LocalToWorld, 58 LocalToWorldVector, 59 WorldToLocalVector, 64 CalculateVelocityOffset |
| IPhysicsMotionController | the controller object +4, vtable 0x100e2260 (IVP_Controller part at +0, vtable 0x100e2284) | 2 AttachObject(obj, bool) |
| IMotionEvent (the game's) | CConstantForceController vtable 0x108a5a28, CKeepUpright's 0x108a53c0 | 0 Simulate (thiscall, 5 args) |

The server's setup (PhysicsInit 0x102f5f60), in order: SetPerformanceSettings {10, 250, 2000, 3600, 1.0, 0.5, 10,
2500}; CreateObjectPairHash; SetDebugOverlay; EnableDeleteQueue(1); SetCollisionSolver / SetCollisionEventHandler /
SetConstraintEventHandler / EnableConstraintNotify(1) / SetObjectEventHandler (the global CCollisionEvent 0x10ae7fe0:
+0 collision events vtable 0x108a81ac, +4 solver 0x108a8188, +8 object events 0x108a81a0); SetSimulationTimestep(1/64);
SetGravity(0, 0, -sv_gravity). The solver: ShouldCollide 0x102f6b10 (groups, pair hash, ...), ShouldSolvePenetration
0x102f78a0 (1 unless a pair has penetrated > 3 s, then frees it), ShouldFreezeObject 0x102f7090,
AdditionalCollisionChecksThisTick 0x102f5e00 (only past 1200 checks), ShouldFreezeContacts 0x102f7250. The oracle's
solver returns the ordinary path's answers (1, 1, 1, 0, 1). The collision / object event handlers are not set (they
make sounds, damage and touch events, no motion: TODO confirm none changes a velocity).

The kart (PhysModelCreate 0x1031a3d0): material = GetSurfaceIndex(solid surfaceprop) = -1 for "none" (with CS:GO's
scripts parsed "default" is index 0), clamped to 0 by CreatePolyObject; SetContents when the model's contents differ;
then VPhysicsInitNormal 0x102082c0 Wakes it unless start-asleep. CPhysThruster Deactivate 0x102ee730:
DestroyMotionController, then the attached body's Wake (slot 24).

Scenario files (one command per line): `surfaces <file>`, `box <min xyz> <max xyz>` (a static default box),
`gravity <g>`, `kart <origin xyz> <angles>`, `pinned`, `ticks <n>`, `thruster <name> <flags> <force> <angles> <local
origin>`, `upright on|off <limit>`, `at <tick> on|off <thruster>`, `at <tick> force|angles <thruster> ...`,
`at <tick> upright on|off`, `at <tick> limit <v>`, `at <tick> motion 0|1`, `at <tick> wake`. Output: a line per tick
(after its Simulate): position, angles (GetPosition), velocity, angular velocity (GetVelocity), the 3x4 matrix,
asleep; each float as value/bits.

First results (scenarios/flat-drive.txt, the kart dropped 8 u onto a default floor): it rests with its origin at
z 8.45 (the hull's lowest point -7.96: 0.49 u above the floor, IVP's contact gap); forward thrust 3750 reaches ~650 u/s;
t_s 300 turns it ~180 deg/s at speed; it falls asleep ~100 ticks after it stops.

---------------------------------------------------------------------------------------------------------------

## 9. IVP's PSI (one Simulate(1/64) = one PSI), from the oracle's stacks

`Simulate` 0x10014320 -> (0x1001447e) the PSI wrapper 0x10084c80: lock (env+0x28 slot 0), the time manager's event
loop (`*(env+4)`, its +4 object's slot 0, with time = psi_time + dt * 1.99999 (0x100f3e50)), unlock (slot 2). The
loop (0x100854c2 -> 0x100857e8) runs the queued time events, one of which is the PSI, **0x10084fb0**
(IVP_Environment's simulate PSI; env+0x114 holds the stage):
1. env+0xda != 0: 0x10087370 (delayed rechecks: a ShouldCollide came from here); env+0x2c: 0x100868f0; the env+0x94
   object's slot 0x28; every PSI listener (env+0xd4, count +0xd2, last to first); 0x100951f0(env+0x10).
2. **0x10072850**: every simulation unit (the list at sim-units-manager+0x18, walked in that order, two ahead) through
   **0x10072540** with the event {dt (env+0xa8), 1/dt (env+0xac), env}:
   - each core, last to first: 0x100723b0 (the core's matrix at the current time from its last-PSI pose: rotation
     from the next-PSI quaternion core+0x110..0x11c, position core+0xe0 + (t - core+0x130) * core+0xf0), then
     0x10077520 (pending pushes committed: rot += rot_change, speed += speed_change), flags &= 0xff3f; a unit whose
     cores all move slower than 1 (1 - |core+0xd0|^2 tested by sign) is a sleep candidate (flags 0x400 / 0x3000).
   - env+0x110 counts down; at 0 it is reloaded from an LCG (`seed *= 0x4b` at 0x1010a9a8:
     `15 - (int)((seed & 0xffff) * 1.5258789e-05 * -5)`) and the unit's sleep check 0x100722d0 runs. TODO: the seed's
     start value and 0x100722d0.
   - **every controller of the unit, last to first** (unit+0x20, count +0x1e): slot 4 do_simulation_controller(event,
     its core list). The gravity / damping controller 0x10072170, the motion controllers 0x1001a4f0 (thrusters, upright)
     and the friction system (0x10080e4c is on that path) are all here. TODO: how the unit's list is ordered (the
     priorities 1000 / 500 and insertion).
   - the unit's cores go to the moved list; per core per object 0x10073a50 (invalid mindists rechecked, ivp-pileup.md 5); unit flags 0x300: split / merge
     (0x10071800, 0x100713b0, 0x10071710, 0x100715c0).
3. **0x10097d00**: each moved core through **0x100970f0** (IVP_Core's next-PSI step) with {dt, 1/dt (1e10 if dt <=
   1e-10), env}:
   - speed limits: if |rot speed core+0xc0|^2 > (env+0xac * settings+0x10)^2 the settings' hook (env+0x20 object, slot
     1) clamps it; if |speed core+0xd0|^2 > (settings+8)^2, slot 0. (settings = env+0x24: max angular per PSI, max
     speed)
   - core+0x13c = |speed|^2, core+0x138 = 1/dt; 0x10096940 makes the step's rotation quaternion from the rot speed;
     position: core+0xe0 += core+0xf0 * (t_env - core+0x130), core+0x130 = t_env, core+0xf0 = speed; the old next
     quaternion is kept at core+0x100, the new one is q x dq (the Hamilton product written out at 0x100970f0's middle),
     renormalised by Newton steps (`y = 1.5 - n/2`, `y += (1 - y^2 n) / 2` until the error <= 1e-6) when 1 - |q|^2 >
     1e-6; 0x100975f0 then derives the core's matrices; each object's hull manager gets its moved radius and next
     check time (object+0x48 ..0x70) and is queued when due.
   - TODO: the disassembly's x87 / SSE split and sum orders (0x10001930 / 0x10001950 bracket parts: FPU control word?),
     0x10096940, 0x100975f0, the limit hooks.
4. **0x10097db0**: every queued hull manager runs its due synapse events (slot 1 of the event table at
   object+0x24 + 0xc + 16 * object+0x30) until none is due, at most the manager's budget (env+0x24+0x14, more from
   env+0x20 slot 4); then 0x10093bb0 every 10 s. The collision checks (the OV tree, ShouldCollide, the mindists'
   creation: 0x100850b6 -> 0x10097f8c -> ... -> 0x1009501e) come from here.
5. 0x100952d0(env+0x10); 6. every object of env+0x10's list (+8, next +0x74): 0x10095310(obj, 1, 1).

Impacts and contacts: **[ivp-contacts.md](ivp-contacts.md)** (2026-11-17: the friction system's three controllers, the
contact points' geometry and the tangential friction ported and checked; the normal pressures' solver and the impacts
traced at the call level). Before it: the friction system's controller (stage 2) and the mindist events (between PSIs,
in the time manager's loop) hold them; the files: ivp_friction.cxx (0x10083110, 0x100816a0), ivp_mindist_friction.cxx
(0x1008d230), ivp_friction_gaps.cxx (0x100a0580), ivp_mindist.cxx (0x10094150), ivp_mindist_minimize.cxx
(0x100980e0, 0x100982d0, 0x100984c0, 0x10099a60..0x10099c50), ivp_mindist_recursive.cxx (0x100b14f0),
ivp_mindist_event.cxx (0x100a51b0, 0x100a53e0), ivp_compact_ledge_solver.cxx (0x1007ac30), ivp_object.cxx (0x10073680,
0x10073c40, 0x10074750), ivp_physic_private.cxx (0x10086fb0) (each named by its "IVP Failed at %s %d" call).

---------------------------------------------------------------------------------------------------------------

## 10. The free body's step, exact (ported: sim/src/ivp, checked by sim/src/bin/ivp_check.rs)

All SSE scalar single precision (Rust f32 gives the same bits); 0x10001930 is fabsf, 0x10001950 sqrtf. Every sum
order is in the Rust, transcribed from the disassembly. **The decompiler regroups sums** (0x10074000's mass-centre
offset shows `(a + b) + c` where the code does `c + (b + a)`): only the disassembly was used.

Corrections to sections 2-3: the kart's CPhysicsObject has vtable **0x100e2878** (not 0x100e26ec), so GetPosition is
0x1001cd30 and GetPositionMatrix 0x1001cdb0 (both through 0x10074000; 0x100201e0 is the other class's, with a cache).
SetupForces takes the radians in SSE (`angle x 0x10989828` as float), then `fld dword; fsincos; fstp dword (cos);
fstp dword (sin)` for yaw then pitch, then F in SSE: not an x87 multiply.

Timing: the environment's clock (IVP env+0xf0) ends a Simulate at `last_psi + (double)(f32(dt) x 1.9999900f)`; PSI k
runs at k/64 (the first Simulate runs PSIs 0 and 1); inside a PSI the clock reads the PSI's time and a core's
t_psi (core+0x130) the previous PSI's. So between ticks GetPosition interpolates (t - t_psi) = 0.0156248 s past the
last PSI, 99.999 % of the way to the next pose.

A PSI for one free core (unit list order, per unit):
1. revival (0x100778d0, a core with movement state 8): state 1, t_psi and both references' times = t.
2. stage 2 (0x10072540): 0x100723b0 (the rows core+0x60 and position core+0x90 at t from q_next and pos + delta
   (t - t_psi)); commit 0x10077520; flags &= 0xff3f, bytes 2-3 cleared; the countdown env+0x110 (u16, starts 10) -1,
   at 0 `seed *= 0x4b` (0x1010a9a8, 1 in a fresh process) and `15 - (int)(f32(seed & 0xffff) x 2^-16 x -5)`; the
   unit's controllers from the last entry (the list: append + insertion sort ascending by priority 0x10071e40,
   removal shifts down 0x10071dc0; the kart's: [drag 500, keep-upright 500, thrusters 500 newest last, gravity 1000],
   seen in the DLL's own list); when the countdown hit 0 the sleep check 0x100722d0: each core's movement state
   0x100782a0 into flags byte 1.
   - gravity 0x10072170: damping (+0.1 per axis and linear when byte 1 >= 2, constant 0x100f3c60 = 0.1f),
     commit, speed += g dt (g = (0, 20.32, 0) for sv_gravity 800).
   - motion 0x1001a4f0: the event's answer (table 0x1001aa64: 1 local accel, 2 local force, 3 global accel, 4 global
     force), then the clamp 0x10078650 (speed and speed change to 50.8 m/s; rot speed to inv_dt x 0.95203 rad
     (settings+0x10: 3600 deg x the PSI time when SetPerformanceSettings ran, 1/66) = 60.93 rad/s; the rot change is
     scaled by that limit over |speed change|, IVP's slip, kept).
   - drag 0x10012db0: body-axis speed `vl`, `f = max(((|b1 vl.y| + |b0 vl.x|) + |b2 vl.z|) coef -0.5 density dt, -1)`,
     speed += speed f; the same on the rot speed without the 0.5. The kart's basis (CPhysicsObject +0x24..+0x38, read
     from the live object): (3.4425e-4, 1.2845e-3, 4.7913e-4), angular (8.0911e-4, 4.4041e-4, 6.5126e-4); coefs 1, 1;
     density 2. The basis builder 0x1001bc70: section 11.
   - movement state 0x100782a0: reference 1 (q +0x160, pos +0x180, t +0x150) moved if |pos - p1|^2 > 1e-4 or
     2 r^2 (1 - (q1.q)^2) > 2.5e-5 (r = core+4, the radius); unmoved and (t - t1) <= env+0x88 (0.3 s): 2; else 3 if
     |w|^2 <= (2.3561945 / 0.3)^2 or the last PSI's turn 2 r^2 (1 - (q.q_last)^2) <= 2.5e-5. Moved: reference 1 =
     now, then reference 2 (+0x170, +0x190, +0x158; 0.01 and 0.04): unmoved: 3 if (t - t2) > 4 s else 1; moved:
     reference 2 = now, 1. All cores 3: the unit sleeps (section 12).
3. stage 3 (0x100970f0 per moved core): the limit hooks (env+0x20 slots 0 / 1: section 12),
   |speed| into core+0x13c, the rotation step 0x10096940 (sub-steps n = trunc(sqrt(144 |w|^2 dt^2)) + 1 when
   |w|^2 dt^2 > 1/36; per sub-step h: the half-angle quaternion (a - a^3 x 0.16666667 per axis, w = sqrt(1 - ...)) and
   the gyroscopic term `w_i += (w_j w_k) (I_j - I_k) / I_i h`; the other path 0x10096d56: section 12, not the kart's); pos += delta
   (t - t_psi), delta = speed, q_last = q_next, q_next = q x dq, Newton-renormalised (`y = 1.5 - n/2`, `y += (1 - y^2
   n) / 2` until |error| <= 9.9999997e-7) when |1 - n| > 9.9999997e-7. 0x100975f0 (the spin axis in world and an
   arcsine-series spin rate, x the core radius: the hull managers' moved distance) is collision bookkeeping.

Read-back: 0x1006ca90 the quaternion at t: f = (t - t_psi) x core+0x138; a lerp q_last -> q_next (sign-matched) when
their dot >= 0.999 with two Newton steps on the length (`y0 = 1.5 - n/2`, `y = (0.5 - y^2 n/2) + y`), else a slerp
(`theta = acosf(d)`, `inv = 1 / sqrt(1 - d^2)`, `q = (sinf(theta f) inv sign) q_next + (sinf((1 - f) theta) inv)
q_last`, not renormalised) through the DLL's statically linked SSE2 libm: acosf 0x100d768b (branches by |x|: below
2^-16, [2^-16, 0.0625), [0.0625, sqrt(3)/2) with tables 0x100fd870 / 0x100fae60, [sqrt(3)/2, 0.9921875), [0.9921875,
1), +-1; constants 0x100fb660..0x100fb68f) and sinf 0x100d9542 (k = round(x 32/pi) in SSE, the remainder in f64 with
pi/32 split into two constants scaled by the float's own bits shifted into a double (psllq 29), 64 (sin, cos) rows at
0x100fdc80, degree-2 polynomials; |x| below 2^-126: x x 0.99999999907; the large-argument path 0x100d9655 not
ported). Both are transcribed instruction by instruction onto a 4-lane SSE register model (math/csgo_libm.rs), tables
generated by tools/re-csgo-libm-tables.py. 0x10074000: the rows from that quaternion (the 0x100723b0 formulas), the position
pos + delta (t - t_psi) plus the rows x the object's offset (IVP_Real_Object +0x30, -mass centre; +0x2c a rotation:
NULL here). GetPositionMatrix maps IVP rows to Source (`[r00, r02, -r01, px K; r20, r22, -r21, pz K; -r10, -r12, r11,
-(py K)]`), GetPosition's angles (0x10001b90) are three x87 fpatan stored as float x 57.29578 (yaw atan2(r20, r00),
pitch atan2(r10, sqrt(r00^2 + r20^2)), roll atan2(r12, -r11) + 180; the |xy| <= 0.001 branch yaw atan2(r02, -r22),
roll 180). The transforms (0x1001c3e0 / 0x1001c580 / 0x1001c640) run on GetPositionMatrix's result.

The oracle's game side runs the real `fsincos` / `fpatan` (machine code in the oracle) as the server does. The port's
fpatan (math/x87.rs fpatan_dword): atan2f refined by two double-double Newton steps, stored with the x87's rounding.

**Checked (2026-11-16)**: scenarios/air-free.txt (a tilted kart falling, gravity, damping, drag: 100 ticks) and
scenarios/air.txt (thrust, both turns, jump, brake, the upright on / off and its limits) bit-identical with
vphysics.dll in every core field and every GetPosition / GetVelocity / GetPositionMatrix output, all 300 ticks
(the spin-out from tick 160 runs the slerp). The math, natively against the DLL and the CPU (`KartOracle <csgo legacy>
--math <out> 2000000`, then `cargo run --release -p ze-sim --bin csgo_math_check -- <out>`): acosf 35,292,290 cases
(every 64th float in [-1, 1] and random), sinf 18,908,289 (every 64th in [0, 4], random in [-8, 8]), fpatan 4,000,000
pairs, fsincos 2,007,201 arguments: 0 differ.

server.dll's own mathlib (2026-11-18), natively too: `KartOracle <csgo legacy> --frame <out> 20000` (Frame.cs:
server.dll mapped with DONT_RESOLVE_DLL_REFERENCES, the leaves called through a register thunk, AddTemplate's
inline InverseTR copied out and run on its own stack layout), then `cargo run --release -p ze-sim --bin
csgo_frame_check -- <out>`. It checks AngleMatrix, MatrixInvert, ConcatTransforms, MatrixAngles, VectorAngles,
OnActivate's thruster frame, SetupMatrixOrgAngles, MatrixMultiply, InverseTR and a template's placement: 242,172
cases, 0 differ (math/csgo_mathlib.rs; docs/game/ivp-physbox.md 7 and 8).

---------------------------------------------------------------------------------------------------------------

## 11. The body's creation from the .phy, exact (ported: sim/src/ivp/create.rs, phy.rs; 2026-11-16)

ivp_check builds the kart from its .phy (no oracle state seeded) and compares every field the DLL leaves right after
CreatePolyObject (the oracle's `.raw` `# created` line: core +0..+0x1a8, object +0..+0xa4, the surface manager's
vtable) and after the Wake (the tick -1 row, plus env+0xf8 as `next`). All SSE scalar single; disassembly only.

The chain: env slot 7 **0x10013cb0** -> **CreatePhysicsObject 0x1001e7a0** (material index < 0 -> 0; a non-finite
origin / angle is zeroed with a Warning):
1. **AngleVectors 0x100b8030** (ecx angles, edx forward, stack right, up): radians `angle x 0x100f3bf4` in SSE, `fld
   dword; fsincos; fstp cos; fstp sin` for yaw, pitch, roll; forward (cp cy, cp sy, -sp); right (cr sy - (sr sp) cy,
   (cr x -1) cy - (sr sp) sy, (sr x -1) cp) (0x100f4084 = -1); up ((cr sp) cy + sr sy, (cr sp) sy - sr cy, cr cp).
2. 0x1001e97a: the IVP matrix (rows, stride 16): [f0, -u0, -r0; -f2, u2, r2; f1, -u1, -r1] (columns: forward, -up,
   left in IVP axes; u2 / r2 are xor'd twice).
3. **IVP_U_Quat::set_quaternion(IVP_U_Matrix3) 0x1006d240**: trace = (m00 + m11) + m22 > 0: s = sqrtf(trace +
   1), w = s 0.5, k = 0.5 / s, x = (m21 - m12) k, y = (m02 - m20) k, z = (m10 - m01) k; else i = argmax diagonal
   (m11 > m00 -> 1, m22 > m_ii -> 2), j = next[i], k = next[j] (next = 1, 2, 0), s = sqrtf((m_ii - (m_kk + m_jj)) +
   1), q_i = s 0.5, h = 0.5 / s unless s == 0 (then s), w = (m_kj - m_jk) h, q_j = (m_ji + m_ij) h, q_k = (m_ki + m_ik)
   h. Then n = ((x^2 + y^2) + z^2) + w^2 > 1e-10 (0x100f3b94): q x (1 / sqrtf(n)) (mulps).
4. The position (x k, -(z k), y k) (k = 0x10106930 = 0.0254).
5. The template **0x1001e6e0** (over IVP's template ctor 0x1008e1d0: mass 1, rot_inertia_is_factor 1, factors 1,
   rot_inertia_limit 0.03, damping 0.01): mass = 0.1 > m ? 0.1 : minss(m, 50000); the material; inertia factor (all
   three) = 0 >= f ? 1 : f, then minss(., 1e18); rot damping (+0x40..0x48) = params rotdamping; speed damping (+0x34) =
   params damping; +0x30 = params rotInertiaLimit; +4 = static.
6. `new IVP_Polygon` **0x100a1030** -> IVP_Real_Object ctor **0x100734d0** -> **IVP_Core ctor 0x10077f40** (memset
   0x1b0 and the unit 0x10077e60: movement state 8 in byte 1, the environment's gravity controller attached unless
   static, 0x10071d40); flags bit 1 = static, bit 0 = template +8 (0); the quaternion normalised as in 3; q_next = q;
   pos (+0xe0); delta 0; the rows (+0x60) from q with the 0x100723b0 formulas (written out at 0x10078082); +0x90 =
   pos; radius (+4) and +8 = 1000. Object +0x44 = 8 (+8 if static).
7. **init_object_core 0x10074750** (object +0x84 the surface manager, vtable 0x100e1064 for a compact surface):
   - the mass centre: template +0x54 (override) or slot 1 0x10078c90 (IVP_Compact_Surface +0, IVP metres);
   - set_new_m_object_f_core (object vtable slot 2, **0x10072d00**) of [I | mass centre]: its inverse (**0x100760e0**:
     the transposed rows, the translation -((r0 t0 + r1 t1) + r2 t2) per row) is the object's frame on the core:
     +0x30 the offset, +0x44 |= 0x800 and offset 0 when ((o0^2 + o1^2) + o2^2) < 9e-6 (0x100f3bb0); a rotation
     quaternion at +0x2c only when a diagonal isn't 1 (never from here); every hull synapse's point is moved by it;
   - slot 2 **0x10078cd0** radius about that centre: d = sqrtf(((c1 - m1)^2 + (c0 - m0)^2) + (c2 - m2)^2) (0 here),
     radius = upper_limit_radius (+0x18) + d, deviation = (f32(byte +0x1c) x 0.004 (0x100f3be0)) x upper_limit_radius
     + d; core +4 = object +0x90 (template +0x50, extra radius: 0) + radius, +8 = deviation;
   - mass m = template mass (< 0.003 -> 1); with rot_inertia_is_factor: slot 3 **0x10078cb0** (surface +0xc, per
     unit mass) and I_i = (factor_i x ri_i) x m (without: the template's values); a limit != 0: L = sqrtf((I0^2 + I1^2)
     + I2^2) x limit, I_i = L where L > I_i; core +0x1c m, +0x40 speed damping, +0x20.. rot damping;
   - **calc_calc 0x10077d40**: each I not finite (CRT _finite 0x100c6bcd) or > 1e18 -> 1e18, < -1e18 -> -1e18; 1/I
     (+0x30), 1/m (+0x3c); flag 0x8 when ((i0^2 + i1^2) + i2^2) x 0.01 > (((i2 - i0)^2 + (i1 - i2)^2) + (i0 - i1)^2)
     over the inverses (nearly spherical; the kart: no); +0x44 = 0.5 / radius;
   - **0x10075300** matrix product (out = a b, every entry ((k0 + k1) + k2), translation a.t + (that of a.rows b.t)):
     the core's [rows | pos] x [I | mass centre] -> +0x60 / +0x90, then pos (+0xe0) = +0x90: the core at the mass
     centre; q_last = set_quaternion(+0x60 rows) (not the start quaternion: it's re-derived), q_next = q_last;
   - dt = f32(env+0xf8 - env+0xf0) (cvtpd2ps), 1/dt (> 1e-10, else 1e10) into **0x100775f0**: +0x138 1/dt,
     q_next = q_last, speed / delta / +0x13c / +0x5c / +0x1a4 zero, +0x120 (1, 0, 0). The environment's ctor
     (0x100841d1, 0x10084434) leaves env+0xa8 = f32(1/66) = 0x3c783e10, +0xac = 66, +0xf0 = 0 and +0xf8 =
     f64(f32(1/66)) until the first PSI (SetSimulationTimestep 0x10014670 doesn't touch +0xf8; after a PSI it is the
     next PSI's time): a body made before the first Simulate gets 1/dt = 66. One made between ticks would read
     next - now < 0 and get 1e10 (checked: multi.txt's kart e, section 12).
8. **CPhysicsObject::Init 0x1001b3f0** (env, the IVP object, material, volume, drag, angular drag): drag basis
   reset to the zero vector 0x10120b04, then **ComputeDragBasis 0x1001bc70** unless static (slot 1) or no collide
   (slot 74): CollideGetAABB (collision slot 23 -> **0x10033120**, origin / angles zero) and
   CollideGetOrthographicAreas (slot 26 0x1000bbb0 -> the collide's slot 8: the .phy's dragAxisAreas); d = maxs -
   mins (Source); X = |k dx|, Y = |-(k dz)|, Z = |k dy| (andps 0x7fffffff); basis = ((Z Y) a.x, (Z X) a.y, (Y X) a.z)
   x GetInvMass (slot 30, x87 return); hx, hy, hz = half of X, Y, Z; with T(w, l, h) = ((((w^2 0.5) w^2) l) +
   (((w^2 x 0.33333334 (0x100f3cc0)) l) l^2)) + ((w^2 l) h^2) (SDK's AngDragIntegral, its products left to right):
   angular = ((T(hz, hx, hy) iIx) a.y + (T(hy, hx, hz) iIx) a.z, (T(hz, hy, hx) iIy) a.x + (T(hx, hy, hz) iIy) a.z,
   (T(hy, hz, hx) iIz) a.x + (T(hx, hz, hy) iIz) a.y) (iI = core +0x30). +0x44 / +0x48 = the drag coefficients (0
   when static); +0x3c volume, +0x40 buoyancy ratio (volume / (k^3 max(volume, 5)) / the material's density).
   The AABB for a single-ledge surface (the ledge tree root at surface +0x20 is a leaf: +0 == 0): the support point
   of the ledge (0x1002c720 / 0x1002d270 over the directions 0x1010ad20: +x, -x, +y, -y, +z, -z) through the collide
   transform 0x1002c7d0 (rows x 39.37008 (0x10106934), Source axes): each bound is a vertex's coordinate, so mins /
   maxs = the min / max over the ledge's points of (x K, z K, -(y K)). A ledge tree takes 0x10032e60: TODO(trace).
9. Then slot 16 SetGameData, slot 12 EnableCollisions(1) with enableCollisions, slot 14 EnableDrag(1) when drag !=
   0 and not static (the drag controller, priority 500), 0x1001fcd0 when the environment's slot 0x120 says so.

**Wake** (object slot 24 0x1001b660 -> **ensure_in_simulation 0x10075060**): an object with +0x44 == 8 (not
simulated) has its core appended to env+0xd8's list (count +0xda, array +0xdc) and flagged 0x4, once; a simulated one
has both movement references' times (core +0x150, +0x158) set to env+0xf0. The PSI's stage 1 revives the list:
**0x10086b70** per core (every object's +0x44 = 1; the speeds kept when t_psi (+0x130) isn't 0x100f3b68, then
revive 0x100778d0, 1/dt again from env+0xf8 - env+0xf0 into 0x100775f0, the kept speeds restored, 0x10082ce0, each
object's hull through 0x10086390): ported in section 12.

SetPerformanceSettings **0x10015070**: settings +8 = maxVelocity x k, +0xc / +0x14 copied, +0x10 =
(maxAngularVelocity x 0.017453292) x env+0xa8 (the PSI step then: the server calls it before SetSimulationTimestep,
so 1/66), +0x18 / +0x1c clamped to [1, 50000]; env+0x1c +0x20 / +0xc from +0x10 / +0x14.

**Checked (2026-11-16)**: scenarios/air.txt (300 ticks), air-free.txt (100), create-flip.txt (120: created upside
down past 120 degrees, set_quaternion's off-trace branch) and 80 more poses (16 fixed: 0 / 180 on each axis, +-90
pitch, 720 / -540 / 360, 179.9 ...; 64 random angles in [-360, 360] and origins), each created and run 40 ticks with
thrust and the upright: every created field and every tick bit-identical with vphysics.dll.

---------------------------------------------------------------------------------------------------------------

## 12. Sleeping, waking, several bodies, the game's calls between ticks, the limit hooks (ported: sim/src/ivp/sleep.rs, world.rs; 2026-11-17)

All SSE scalar single unless named; disassembly only. The oracle's MoreKarts.cs adds the scenario lines and events
(header comment there); ivp_check compares, besides section 10's fields, the core's flags, pending changes, t_psi,
+0x138 / +0x13c, IsAsleep, and for MoreKarts' karts the movement references and the unit's word, plus `<out>.env`
(env+0x110, the LCG 0x1010a9a8, the unit lists by kart).

**The simulation units manager** (env+8): the active units' list head at +0x18, the sleeping ones' at +0x1a8; a unit
links prev +4 / next +8, its state byte +0 (< 8 active, 8 asleep), flags above it, cores at +0x10 (count +0xe),
controllers at +0x20 (count +0x1e). A new core's unit (0x10077e60: state 8, flags & ~0x3f00) goes to the **sleeping
list's head** (core ctor 0x10077f8d); vphysics also keeps one unit of its own there (the oracle's `?`).

**The walk** 0x10072850 (stage 2) holds the next three units before it runs one: with n active units it runs the first
n - 3 in list order, then the last three **from the last back** (n <= 3: all reversed). Each unit's cores then go to
the moved list in the order 0x10072540 ran them; **stage 3** (0x10097d00) walks the moved list from its last entry.

**0x10072540, per unit** (after section 10's per-core part): `1 - |speed|^2` of each core is or'd by its bits: any core
faster than 1 m/s sets unit flags 0x400 (and clears 0x800); else the flags' 0xc00 move up to 0x3000 (`((f << 2) ^ f) &
0x3000 ^ f`) and, if any is set (the unit was fast the PSI before), **every core's movement references' times = now**
(0x10071f70), then 0xc00 off. Then the countdown, the controllers, the cores into the moved list (**a core put to sleep
below still takes this PSI's stage 3**), the sleep check if the countdown hit 0, per core last to first per object 0x10073a50 (the object's invalid mindists rechecked: ivp-pileup.md 5), the
0x300 split / merge.

**The sleep check 0x100722d0** (unit, env): each core last to first, 0x100782a0's state into its byte 1, and'd from 3;
all 3: each core **0x10077820** (0x10077750: byte 1 = 8; speed +0xd0, rot +0xc0, speed change +0xb0, rot change +0xa0,
delta +0xf0 zero; then **0x100775f0** with the environment's {dt, 1/dt}: +0x138 = 1/dt, **q_next = q_last** (the pose
goes back to the PSI before), +0x5c / speed / delta / +0x13c / +0x1a4 zero, +0x120 = (1, 0, 0); each object +0x44 = 8,
its hull manager's time sums (object +0x58 += (t - +0x48) x +0x50 ...), 0x10093bb0, +0x40 unlinked) and **0x10086d60**
(per object: the object's listeners through 0x10086630 (a hash, 0x10086390) and the environment's global object
listeners (env+0x120, count +0x11e), slot 3 = frozen: vphysics' sleep listener sets CPhysicsObject +0x15's sleep state);
then the unit is unlinked and pushed at the sleeping list's head, state 8. IsAsleep (slot 2, **0x1001b680**): `(obj+0x15
& 3) != 0 && !(core flags & 4)` (objects start asleep: the state is set at creation).

**Stage 1's revive 0x10087370** (env+0xda != 0): the queue env+0xdc (count +0xda) from its last entry: a static core
(flag 2) skipped; a core in state 8 revives its unit **0x10071ef0** (each core with byte 1 >= 8 through **0x10086b70**;
the loop restarts when it returns 1 (contacts); a unit in state 8 is unlinked from the sleeping list and pushed at the
**active list's head**, state 1); any other core gets its unit's references' times = now (0x10071f70); flag 0x4 off;
the queue emptied. **0x10086b70**: every object +0x44 = 1; the speeds +0xd0 and +0xc0 saved **only when t_psi == 0.0**
(ucomisd with 0x100f3b68 = 0; `lahf; test ah, 0x44; jp`: a core never simulated keeps a velocity set before its first
PSI); **0x100778d0** (byte 1 = 1, t_psi = now (first f32(now - dt), then overwritten), both references' times = now,
each object's hull re-registered 0x10094de0); 1/dt = f32(env+0xf8 - env+0xf0) (> 1e-10 (0x100f3b94), else 1e10) into
0x100775f0; the saved speeds back; **0x10082ce0** (the object's friction synapses +0x20: for a free body none, returns
0); the revived events (slot 2) to the object's and the global listeners. env+0xf8 inside a PSI is that PSI's t + f64(dt)
(**0x10085720**, the PSI's time event: env+0x100 = env+0xf0, env+0xf8 = env+0x100 + f64(env+0xa8)), so the revive's
1/dt is 64 (stage 3 writes the environment's anyway).

**The game's calls** (CPhysicsObject vtable 0x100e2878):
- Wake (24, 0x1001b660 -> 0x10075060): section 11. The kart's Tick() calls it every 0.05 s, so a driven kart never
  sleeps while its script ticks (each call resets the references' times).
- **Sleep** (25, 0x1001b670 -> **0x10073370**): a static core: nothing; queued (flag 4): **0x100872f0** takes it out
  of the queue (shifts down, flag 4 off); byte 1 < 8: per object 0x10073ba0, reference 1 = (q_next, pos +0xe0) with
  time f64(f32(now - 20.0)) (0x100f3ed8), the unit's split / merge (0x10071800, 0x100713b0, 0x10071710, 0x100715c0),
  flags & ~0x300, then the sleep check at now: it sleeps only if the movement checks say rest (a spinning body
  refuses: reference 1 is moved back to now).
- **EnableMotion** (15, 0x1001bfe0): not static, not unchanged (slot 9 0x1001ba00: !(core flags & 0x10)): **0x10072af0**
  (pinned = !on: flag 0x10; speed and rot speed zero; pinned: the object's +0x8c / +0x44 0x100 collision part,
  0x10073ba0, 1/I +0x30..+0x38 and 1/m +0x3c zero, both pending changes zero, 0x10072c90; unpinned: 1/I_i = 1.0 / I_i
  (+0x34 first, then +0x30, +0x38), 1/m, 0x10094de0); on and hinged (slot 5): slot 78; then slots 26 / 27
  (RecheckCollisionFilter, RecheckContactPoints). No Wake.
- **EnableGravity** (13, 0x1001ba50): the environment's gravity controller (env+0: with the damping) added to the core
  (+0x140) and unit lists (0x10071d40: append, sort 0x10071e40) or removed (0x10018430, 0x10071dc0). Without it a body
  has no damping either.
- **SetVelocity** (50, 0x1001d910): IsMoveable (10, 0x1001ba20: !static && motion enabled) or nothing; Wake (slot 24);
  a velocity: speed change = (v.x k, -(v.z k), k v.y), speed zero; an angular one: rot change = (w.x 0.017453292,
  -(w.z x it), w.y x it), rot zero; the clamp 0x10078650 when the object has no shadow (+0x10).
- **ApplyForceCenter** (60, 0x1001c700): IsMoveable; i = ((f.x k) m^-1, (-(f.z k)) m^-1, (f.y k) m^-1) (core +0x3c),
  ensure_in_simulation, speed change += i, the clamp.
- **SetPosition** (46, 0x1001d4e0; slot 69 0x1001db50 first): the IVP position (o.x k, -(o.z k), o.y k), AngleVectors
  and the same matrix as CreatePhysicsObject, set_quaternion 0x1006d240; with collisions on (object +0x44 & 0x100) and
  isTeleport: EnableCollisions(0), **0x10074b20**(q, p, 0), EnableCollisions(1), else 0x10074b20(q, p, 1).
  0x10074b20 (beam_object_to_new_position): unless +0x44 & 0x800 the core at p + rows(q) x -offset, each component
  `(r_i2 (-o2) + (r_i1 (-o1) + r_i0 (-o0))) + p_i` with the 0x100723b0 rows; a +0x2c rotation would multiply q by its
  conjugate (none on a prop); then the core's **0x10097750**: env+0x108 += 1; d = f32(now - t_psi); d >= env dt: +0x138
  = 1 / d, else the environment's 1/dt; q_next = q, q_last = q (the relative turn goes to the hull: 0x100975f0),
  **t_psi = env+0x100** (the last PSI's time; 0 before the first); pos = the core position, delta and speed zero,
  +0x90 = pos, the rows from q; +0x13c (optimize ? 1/dt x |moved| : 0) then 0, +0x5c / +0x1a4 zero; each object's hull
  manager re-timed (synapse events fired while due, 0x10093bb0 every 10 s). **The rot speed and the pending changes
  stay**; no Wake.
- **DestroyObject** (env slot 10, 0x10014760): out of the environment's object list (+0x10, swap-remove), callback
  flag 0x400; with the delete queue (env+0xa2, the server's EnableDeleteQueue(1)) or in a Simulate (env+0xa1) queued
  (0x10004150 into +0x24) until **CleanupDeleteList** (slot 49, 0x10014f30 -> 0x100149f0), else deleted now: the unit
  leaves its list, the others keep their order. TODO(trace): when the server's CleanupDeleteList runs against
  PhysFrame (CGlobalEntityList::CleanupDeleteList -> PhysOnCleanupDeleteList) for a kart killed by I/O; the oracle
  destroys and cleans up between the same two ticks.

**The limit hooks** (stage 3, 0x100970f0): env+0x20 is vphysics' CCollisionSolver's IVP_Anomaly_Manager part (vtable
0x100e1c50; installed by the environment's ctor 0x10013250 through the application environment +0x1c, 0x10083fea),
called thiscall (settings env+0x24, core, the vector):
- slot 1 **0x100836e0** (IVP's own) when |w|^2 > (env+0xac x settings+0x10)^2: f = ((env+0xac x settings+0x10) x 0.9
  (0x100f3d38)) / sqrtf((w0^2 + w1^2) + w2^2), w x f;
- slot 0 **0x10012b60** (vphysics') when |v|^2 > settings+8 ^2: unless the object has a shadow controller (CPhysicsObject
  slot 71 0x1001dc80: +0x10 ? +0x10 + 4 : 0), f = (settings+8 x 0.99 (0x100f3d60)) / sqrtf((v0^2 + v1^2) + v2^2), v x f.
SetVelocity / thrusters are held at the limit by the clamp 0x10078650 and drag takes the rest, so the speed hook needs
a fall at the limit (gravity adds 0.3175 m/s per PSI, drag takes less); the rot hook any spin past the clamp (the
clamp scales the rot change only by |speed change|).

**The damping's expf** (0x10076f20 past 0.5 > |rd dt|^2 / 0.25 > ld dt): the CRT's **__libm_sse2_expf 0x100d8112**
per axis on -(rd_i dt) and on -(ld dt) (the xorps sign flip): bits & 0x7fffffff - 0x31800000 >= 0x12000000 goes to
0x100d81dc (|x| <= 2^-28: 1.0 (0x100fc79c); finite |x| >= 256: FLT_MAX^2 or (2^-126)^2 by sign; inf: inf / 0; NaN:
x + x); else k = cvtss2si(f32(x x 23637.115 (0x46b8aa3b))), r = 23637.115549924776 (0x100fc788) x f64(x) - f64(k), T1
= [0x100fc708 + 8 (k & 15)], p = (4.230634646972322e-05 (0x100fc790) x T1) x r, s = [0x100fc608 + ((k >> 1) & 0xf8)] x
[0x100fc508 + ((k >> 6) & 0xf8)], s's high dword += (k >> 14) << 20 (movd, psllq 52, paddd), result f32((T1 + p) x s);
87.3366 < |x| (0x42aeac4f) and not (positive below 88.7228, 0x42b17218) takes 0x100d821a: (p + T1) x s, the same bits.
Ported as math/csgo_libm.rs expf (tables EXP_* by tools/re-csgo-libm-tables.py); `--math` section 5: 37,127,315 cases
(every 64th float in [-128, 128], the specials, 2M random in [-300, 300]), 0 differ.

**Not reached by the kart** (left unported, recorded): 0x10096940's other path **0x10096d56** (section 10 called it
hinged: it is taken when the core's flag 0x8 is set (calc_calc 0x10077d40: inertia nearly spherical) or env+0x114 ==
5; the kart's inertia isn't, and stage 3 runs with another stage number): per-axis sinf / no gyroscopic term, not read.
sinf's large-argument path 0x100d9655: the slerp's angles are acosf's (<= pi) times f in [0, 1]; a body whose 1/dt is
1e10 (made between ticks) or just teleported has q_last == q_next, the lerp branch. The kart's scripts (docs/crazykart
02 / 05): Wake every Tick, EnableMotion / DisableMotion, teleports (point_teleport TeleportToCurrentPos, trigger_teleport)
-> CBaseEntity::Teleport -> SetPosition(isTeleport) (+ SetVelocity when a velocity is given): TODO(trace) server.dll's
Teleport for a VPhysics prop (which of SetPosition / SetVelocity it calls, the order, the Wake) before wiring.

**Checked (2026-11-17)**, each created and run bit for bit with vphysics.dll (every field above, every tick):
scenarios/sleep.txt (520 ticks: falls asleep at rest, a Wake of a sleeper, SetVelocity fast (the 0x3000 reset),
ApplyForceCenter, the game's Sleep moving and at rest, EnableMotion off / on, SetPosition, EnableGravity off / on, a
thruster on a sleeper); multi.txt (460 ticks, five karts: three made after the first, one between ticks 24 and 25
(1/dt 1e10), the walk with five active units, the shared countdown and LCG, sleeps and wakes in different orders,
destroyed awake, asleep and just revived); limits.txt (180: the rot hook, the speed hook every other PSI in a fall at
the limit); damp-exp.txt (200: damping 20 / rotdamping 30 through expf, then asleep); and air.txt, air-free.txt,
create-flip.txt still identical.
## 13. Collision detection, contacts, impacts: docs/game/ivp-mindist.md, ivp-contacts.md, ivp-impact.md, ivp-touch.md

Two karts touching (friction systems merging and splitting, units of several cores, vphysics' pair times, the rescue
push; scenarios touch and touch-world): [ivp-touch.md](ivp-touch.md).

The contacts (the friction system, its controllers, the normal-pressure and complementarity solves, the impact
solver, the materials, checked by ivp_contacts_check): [ivp-contacts.md](ivp-contacts.md). Both were ported on their
own branches and merged on agent/kart-integrate (2026-11-17), on one compact-ledge / cache model (ledge.rs: edges as
dword indices; cache.rs: IVP_Cache_Object). The joint (do_impact 0x1008b020, the impact system, the friction system on
the world, its controllers in the PSI, sleeping and waking on the ground) and the end-to-end check (ivp_check's ground
mode: every box scenario bit-identical over its whole length): [ivp-impact.md](ivp-impact.md).


The mindists between the kart and the world (ledges, the minimize walk, hull managers, the event solvers, the time
events, up to do_impact): [ivp-mindist.md](ivp-mindist.md), ported in sim/src/ivp and checked by mindist_check.

## 14. The map's own world: PhysCreateWorld_Shared (server 0x1031ab20; 2026-11-17)

The BSP's PHYSCOLLIDE lump (29): per model a dphysmodel_t {modelIndex, dataSize, keydataSize, solidCount}, the
solids ([int size][VPHY header, compact surface] each), the key text; the list ends at modelIndex -1. ze_crazykart_v4's
model 0: two solids (1,314,440 and 30,664 bytes) and the keys `staticsolid { index 0, contents 33570819 }`,
`staticsolid { index 1, contents 8 }` (CONTENTS_GRATE), `virtualterrain {}` and `materialtable { default_silent 1,
sand 2, default 3, default 4, glass 5, metalgrate 6, metal 7 }` (python docs/crazykart/tools/extract_world.py <bsp>
<folder> writes it as world0.vcollide: int solidCount, the solids, the keys).

**0x1031ab20** (EDX the vcollide_t, read from the disassembly and the decompile):
- solid 0: physenv slot 8 (CreatePolyObjectStatic) with physprops slot 3 ("default"), origin / angles zero
  (0x10be50f0 / 0x10be50fc), the params {massCenterOverride 0, mass 1, inertia 1, damping 0.1, rotdamping 0.1,
  rotInertiaLimit 0.05, "world", the world entity, volume 0, drag 1, enableCollisions 1}; then the object's slot 22
  (SetCallbackFlags) with slot 23's | 0x200 (CALLBACK_NEVER_DELETED).
- physcollision slot 38 VPhysicsKeyParserCreate(the vcollide_t: the push at 0x1031abe9 is EBX), then while not
  slot 2 (Finished): slot 1's block name, by stricmp (0x106b3ce0):
  - "solid" / "staticsolid": a solid_t (index +0x60c, contents +0x610, params +0x614) over
    g_PhysDefaultObjectParams ("DEFAULT"), parser slot 3 ParseSolid (handler 0x10a4cc38: g_SolidSetup), then pName
    "world", the game data, enableCollisions 1, the "default" surface; index 0 skipped (made above); an index past the
    solids or a null solid sets the flag below; else CreatePolyObjectStatic as above, callback flags | 0x200, object
    slot 41 (SetContents) the contents, and slot 84 (2) when contents & 1.
  - "fluid": ParseFluid (slot 4) and a static object of its solid with "fluid" and its surfaceprop, then physenv
    slot 11 (CreateFluidController). This map has none.
  - "materialtable": int[128] zeroed, ParseSurfaceTable (slot 6), physprops slot 8 SetWorldMaterialIndexTable(table,
    128): the material manager's slot 1 (0x10019d00) maps a triangle's material index below 0x80 through it
    (ivp-contacts.md 7). ze_crazykart_v4: 1 -> 102, 2 -> 71 ("sand": elasticity 0.01), 5 -> 42, 6 -> 8, 7 -> 2, the
    rest 0.
  - "virtualterrain": the flag, SkipBlock (slot 9). Anything else: SkipBlock.
- collision slot 40 frees the parser; with the flag and slot 48 (SupportsVirtualMesh) **0x1031aa20**: for i < 0x8000
  the engine's (0x10ba2574) slot 0xa4 / 4 = 41 GetCollideForVirtualTerrain(i); each one a static object named
  `vdisp_%04d` with "DEFAULT"'s numbers, callback flags | 0x200, slot 84 (2). The displacements (56 on this map)
  come from engine.dll's terrain collides over vphysics' virtual mesh: traced, made in the oracle (a scenario's
  `disp <bsp>` line) and ported, **docs/game/ivp-virtualmesh.md** (2026-11-18).

**The oracle** (rubikon/tests/KartOracle/World.cs, a scenario's `world <file>` line): the same calls in the same
order through vphysics' own key parser, before the kart; the `.md` gets a `# materials` line (each table index's
surface, friction and elasticity by physprops slot 4) for the checkers. **The port** (ivp_check's world mode): each
solid's compact surface (ledge.rs surface_at: the whole tree, ivp-mindist.md 11) and its static core by create.rs
(CreatePolyObjectStatic, the world's params) compared with the DLL's (`world: 2 static solids ... bit-identical`),
the material table into Collide::materials. world-hub (400 ticks) and world-drive (1200) bit-identical every tick.

## 15. The movers (doors, lifts, rotators, buttons): docs/game/ivp-shadow.md (2026-11-17)

func_door / func_movelinear / func_rotating / func_button / func_brush are VPhysics shadows: moving IVP bodies a
CShadowController drives to the entity's pose each PSI (ComputeShadowControllerIVP 0x10024130), updated by the server
after the frame's simulate with the frame time. Ported in sim/src/ivp/shadow.rs; a lift bit-identical over 300 ticks
(shadow_check), run as World's Kind::Shadow (World::add_shadow / update_shadow).

---------------------------------------------------------------------------------------------------------------

## What is exact, what is TODO (summary)
Exact (binary): model/mass/inertia/mass centre/damping values; thruster flags, SetupForces, CalculateVelocityOffset,
the constant-force controller and its per-PSI application (local/global); PSI = one 1/64 s step per tick; damping
formula with its 0.5 / 0.25 linear-vs-exp switch; gravity -800 (20.32 m/s^2 IVP); drag formula and density 2.0;
friction/elasticity product rules; keepupright Simulate and ComputeRotSpeedToAlignAxes; TraceLine mask, filter
arguments and return; game_ui every tick; GetAngles conversion and normalisation; GetLeftVector = right vector;
OnActivate's thruster frame and SetForwardVector's VectorAngles (ivp-physbox.md 7); the templates' placement,
CPointTemplate's AddTemplate / CreateInstance (ivp-physbox.md 8); the game rules' collision groups (ivp-pileup.md 8);
the displacements as virtual meshes (ivp-virtualmesh.md: the trees engine.dll's own, through the oracle's dump).
TODO: controller order within a PSI and the PSI integrator; the friction solver;
angular velocity clamp details; core byte+1 meaning (extra 0.1 damping); surface index of "none"; the
"material 1001" keyvalue; spawnflags 0x2/0x400/0x2000; a parented template member's placement; **what re-enables motion despite
spawnflag 0x8**; ServiceEventQueue vs PhysFrame order; CTraceFilterSimple body; env+0x118 (0.9^dt) use.
