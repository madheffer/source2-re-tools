# IVP shadows: how CS:GO's movers push a kart

CS:GO legacy vphysics.dll (Ghidra `/csgo_vphysics_legacy.dll`) and server.dll (`/csgo_server_legacy.dll`). Addresses are
vphysics unless marked server. SSE scalar single unless named.

ze_crazykart_v4's movers: 60 func_door, 33 func_movelinear, 5 func_rotating, 14 func_button, 1 func_brush (shadows); 14
func_wall_toggle, 20 func_breakable (static). A shadow is a moving IVP body (not static) whose speed a controller sets
every PSI so it reaches the entity's pose. The map's brush models carry `mass 50000`, a surfaceprop and a volume
(finale_elevator1, model 101: "sand").

Source -> IVP units: `(x k, -(z k), y k)`, k = 0.0254 (0x10106930, 0x3cd013a9); back by 39.370079 (0x10106934).

## Functions

| Address | Module | What |
|---|---|---|
| 0x1024e090 | server | CBaseDoor::CreateVPhysics -> VPhysicsInitShadow(false, false, 0) |
| 0x10297c90 | server | CFuncMoveLinear::CreateVPhysics (shadow) |
| 0x10223660 | server | CFuncRotating::CreateVPhysics (shadow, when solid) |
| 0x102df010 | server | CFuncBrush::CreateVPhysics (shadow) |
| 0x10226ff0 | server | CBaseButton::CreateVPhysics (shadow) |
| 0x10221e30 | server | CFuncWall / CFuncWallToggle::CreateVPhysics -> VPhysicsInitStatic |
| 0x10224980 | server | CBreakable::CreateVPhysics -> VPhysicsInitStatic |
| 0x10207ff0 | server | VPhysicsInitStatic |
| 0x10234040 | server | set SOLID type (6) |
| 0x10319d20 | server | box object (isStatic arg) |
| 0x10319e90 | server | solid type 3 object |
| 0x102083a0 | server | VPhysicsInitShadow(allowMove [ebp+8], allowRotate [ebp+0xc] (unused), pSolid [ebp+0x10]) |
| 0x1031a3d0 | server | PhysModelCreate (brush model's collide, not static) |
| 0x10208190 | server | VPhysicsSetObject |
| 0x1031a270 | server | PhysModelParseSolid (zeroed solid_t; each "solid" block by vphysics' ParseSolid, parser slot 3) |
| 0x101d38d0 | server | g_SolidSetup ParseKeyValue (does nothing) |
| 0x10319cd0 | server | g_SolidSetup SetDefaults: copies g_PhysDefaultObjectParams |
| 0x101f7f40 | server | UpdatePhysicsShadowToCurrentPosition(dt), CBaseEntity slot 163 (+0x28c) |
| 0x101fd3d0 | server | abs position recompute |
| 0x103053c0 -> 0x103050a0 | server | PhysicsPusher |
| 0x10304f80 -> 0x10303da0 | server | linear push -> PerformLinearPush |
| 0x10305010 -> 0x10303ec0 | server | rotating push -> PerformRotatePush |
| 0x10303370 | server | FinishPush |
| 0x10306ab0 | server | append to the frame's pusher list |
| 0x10306950 / 0x10306880 | server | frame simulate loop / per entity |
| 0x10303170 | server | frame pushers: touch triggers and shadow updates |
| 0x1020a580 | server | PhysicsTouchTriggers (slot 0x1b4) |
| 0x10355310 | server | a pusher's children list |
| 0x101f7260 | server | physics-controlled entity's blocker check (two UpdateShadow-to-position calls with 0) |
| 0x101f7d40 | server | PhysicsRelinkChildren (own dt to each non-VPHYSICS child) |
| 0x102f6b10 | server | CCollisionEvent::ShouldCollide |
| 0x102f78a0 / 0x102f7090 / 0x102f5e00 / 0x102f7250 | server | ShouldSolvePenetration / ShouldFreezeObject / AdditionalCollisionChecks / ShouldFreezeContacts |
| 0x102f6a40 | server | callback flags' 0x40 test |
| 0x1014a4e0 | server | owner test |
| 0x1016c7a0 | server | move parent |
| 0x1001dac0 | vphysics | CPhysicsObject::SetShadow (slot 68) |
| 0x1001db50 | vphysics | UpdateShadow (slot 69) |
| 0x1001dbe0 / 0x1001dc80 / 0x1001dbb0 | vphysics | GetShadowPosition (70) / GetShadowController (71) / RemoveShadowController (72: env +0x138 slot 0x68) |
| 0x1001dde0 -> 0x100246e0 | vphysics | ComputeShadowControl (73; not used by movers) |
| 0x10014c20 | vphysics | env CreateShadowController (slot 25: the 0xb0 ctor, returns +4) |
| 0x10024990 | vphysics | CShadowController ctor (object, allowTranslation, allowRotation) |
| 0x10024a60 | vphysics | attach |
| 0x100b8030 | vphysics | AngleVectors |
| 0x1006d240 | vphysics | set_quaternion |
| 0x10024e10 | vphysics | UseShadowMaterial (controller slot 10) |
| 0x1001dca0 | vphysics | SetMaterialIndex (object slot 39) |
| 0x10076950 | vphysics | calc_calc (material) |
| 0x10071ef0 / 0x10071f70 | vphysics | revive unit at env time / reset references' times |
| 0x10081280, 0x1008d230, 0x1008af60, 0x10082a60 | vphysics | a friction synapse re-mixed for the new material (ivp-contacts.md) |
| 0x10077d40 | vphysics | calc_calc (inertia) |
| 0x10071d40 | vphysics | controller into the core's list (append, sort) |
| 0x10025250 | vphysics | MaxSpeed (interface slot 2; ctrl = this - 4) |
| 0x10024ff0 / 0x100251d0 | vphysics | Update / interface slot 1 |
| 0x10024e70 | vphysics | StepUp (slot 3: beam up by height k) |
| 0x10024ef0 | vphysics | SetTeleportDistance (slot 4: +0x74 = d k) |
| 0x10024d90 | vphysics | GetLastImpulse (slot 9) |
| 0x10024e50 | vphysics | ObjectMaterialChanged (slot 11) |
| 0x100251f0 | vphysics | GetTargetPosition (slot 12; returns the seconds) |
| 0x10025280 | vphysics | GetMaxSpeed (slot 14) |
| 0x10024f20 | vphysics | do_simulation_controller (IVP_Controller slot 4) |
| 0x10024130 | vphysics | ComputeShadowControllerIVP (ecx IVP object, edx params +0x20, xmm2 seconds, xmm3 dt; returns seconds left, unused) |
| 0x100212d0 | vphysics | object touches something |
| 0x10073ba0 | vphysics | teleport step |
| 0x10074b20 | vphysics | beam_object_to_new_position(q, p, 1) |
| 0x10095180 | vphysics | (env +0x10, object) after the beam |
| 0x10020fa0 | vphysics | linear speed control (speed, delta, maxSpeed xmm2, maxDampSpeed xmm3, scale, damping, out) |
| 0x10023fb0 | vphysics | quaternion difference |
| 0x100d768b | vphysics | the CRT's acosf |
| 0x1001c100 | vphysics | CPhysicsObject::SetMass (slot 28) |
| 0x1001bc70 | vphysics | ComputeDragBasis |
| 0x10033120 | vphysics | CollideGetAABB |
| 0x10032e60 | vphysics | ledge tree AABB (mins ecx, maxs edx) |
| 0x1002c720 | vphysics | ledge support object |
| 0x10011eb0 | vphysics | friction listener |
| 0x10019ba1 | vphysics | surface parser: fallback entry made |
| 0x10019130 / 0x10019d30 | vphysics | entry defaults copy / insert |

## Fields

| Offset | Field |
|---|---|
| CBaseEntity +0x1c | edict |
| CBaseEntity +0xd4 | flags: & 1 refuses a shadow; bit 11 abs position dirty |
| CBaseEntity +0xe6 | movetype (6 VPHYSICS, 7 PUSH, 0 NONE, 11 CUSTOM) |
| CBaseEntity +0xe8 | move parent handle |
| CBaseEntity +0xf4 | collision property (slot 11 solid type, slot 12 solid flags) |
| CBaseEntity +0x158 / +0x15c | physics object / set to -1.0 |
| CBaseEntity +0x1dc / +0x1e8 | abs origin / abs angles |
| CBaseEntity slots | 154 (+0x268) CreateVPhysics, 0x270 VPhysicsDestroyObject, 0x1b4, 0x26c own collide refusal, 0x2a0 mask |
| gpGlobals +0x14 | frametime |
| CPhysicsObject +8 | IVP object (its +0x94 the core) |
| CPhysicsObject +0x10 | shadow controller |
| CPhysicsObject +0x14 | & 0x1f temp gravity disable; SetShadow &= 0xe0 |
| CPhysicsObject +0x18 | u16 material index |
| CPhysicsObject +0x1c | callback flags (& 2 CALLBACK_GLOBAL_FRICTION; held with \| 0x800) |
| CPhysicsObject +0x3c / +0x40 | drag input / drag coefficient |
| IVP object +0x30..+0x38 | offset from the core |
| IVP object +0x44 | movement byte (0x10 static), & 0x100 collisions on, & 0x800 no offset |
| IVP object +0x88 / +0x8c | material / (+0x8c slot 4 on teleport) |
| core +0x10..+0x1c | inertia, +0x1c mass |
| core +0x20..+0x2c | rot damping |
| core +0x60 / +0x70 / +0x80 | rows (16 bytes apart) |
| core +0x90 | pos_now |
| core +0xc0 / +0xd0 | rot speed / speed (set directly, not pending) |
| core +0x110 | q_next |
| core byte 1 | 8 = not simulated, 1 = simulated |
| env +0xb4 | gravity |

CShadowController (0xb0 bytes; IVP_Controller vtable 0x100e2b80 at +0, IPhysicsShadowController 0x100e2b44 at +4):

| Offset | Field |
|---|---|
| +8 | CPhysicsObject |
| +0xc | seconds to arrival (not written by the ctor: g_pMemAlloc doesn't zero) |
| +0x10 | short: object's +0x18 |
| +0x12 | flags: bit 0 enabled (first Update), 1 allowTranslation, 2 allowRotation, 3 physically controlled |
| +0x20 | shadow params: target position (IVP) |
| +0x30 | target quaternion |
| +0x40 | last position (params +0x20) |
| +0x50 | last impulse (params +0x30) |
| +0x60 / +0x64 | maxAngular / maxDampAngular (params +0x40 / +0x44) |
| +0x68 / +0x6c | maxSpeed / maxDampSpeed (params +0x48 / +0x4c) |
| +0x70 | dampFactor 1.0 (params +0x50) |
| +0x74 | teleportDistance, IVP (params +0x54) |
| +0x80 / +0x84 | saved core mass / object callback flags |
| +0x90 / +0xa0 | saved core +0x20..+0x2c / +0x10..+0x1c |

## Constants

| Value | What |
|---|---|
| 0.21875 (0x10989910) | box shadow's bounds shrink per side |
| g_SolidSetup 0x10a4cc38, vtable 0x108ac760 | the solid parse handler |
| g_PhysDefaultObjectParams 0x108ac5a8 | massCenterOverride 0, mass 1, inertia 1, damping 0.1, rotdamping 0.1, rotInertiaLimit 0.05, "DEFAULT", game data 0, volume 0, drag 1, enableCollisions 1 (no handler: ParseSolid leaves 0) |
| 1e4, 1e4 | SetShadow's maxSpeed, maxAngular (push order at 0x1020853c: allowRotation the constant 0) |
| 0x10b5b1ac | push's 16-byte {entity, previous abs origin} list |
| 0x10b5b1fc / 0x10b5b210 | frame pusher list / children list |
| 1/64 | frame time (timeOffset) |
| vtable 0x100e2878 | CPhysicsObject |
| 0xf000 | $MATERIAL_INDEX_SHADOW |
| 0x10116078 +0x2c / +0x10 | material manager slot 11 / density |
| 0.8 (0x3f4ccccd) / 0.001 (0x3a83126f) | shadow material friction (data +0x10) / elasticity (+0x14), index 8 |
| 100.0 (0x42c80000) | core rot damping +0x20..+0x28 (+0x2c a stack lane) |
| 1e15 (0x58635fa9) | inertia without allowRotation |
| 50000 (0x47435000, 0x100f3ff0) | SetMass without allowTranslation; SetMass's cap |
| 1e-8 (0x100f3ba0, 0x322bcc77) | Update's unchanged test |
| 0.0 (0x100f3b60) | seconds floor |
| 1.0 (0x100f3d70) | fraction |
| 1e-6 (0x100f3bac) | speed squared floor |
| 1e-10 (0x100f3b94) | quaternion norm floor |
| pi (0x100f3e70) / 2 pi (0x100f3ea0) | angle wrap (double) |
| 1.1920929e-7 (0x100f3ba8) | axis inverse add |
| 5.0 (0x100f3f20) | drag min |
| 0x1010ad2c, 0x1010ad44, 0x1010ad5c, 0x1010ad20, 0x1010ad38, 0x1010ad50 | AABB's six directions |
| 500 (0x10013010) | shadow priority (the drag controller's function); gravity 0x10007cb0 = 1000 |
| "vphysics:shadow" (0x100e2d44) | controller name |
| 0x108a8188 / 0x108a81ac | server IPhysicsCollisionSolver (CCollisionEvent +4) / IPhysicsCollisionEvent (+0) vtables |
| 0x10ba2a90 slot 3 | pair table |
| 0x10ba26a8 slot 0x70 | game rules ShouldCollide(group 0, 1) |

Controller vtable 0x100e2b80: 0 0x10004450, 1 0x10007e10, 2 0x10007ca0, 3 0x10004430, 4 0x10024f20, 5 0x10013010, 6
0x10024d60 (name), 7 0x10024950 (dtor), 8 0x10025de0.

## Server: which entity gets what

- **VPhysicsInitStatic 0x10207ff0**: an entity with a move parent (+0xe8 valid) becomes a shadow (VPhysicsInitShadow(0, ?, 0); a SOLID_BSP... parent sets SOLID 6 first: 0x10234040(6)); else by solid type (+0xf4 slot 11): 2 a box (0x10319d20, isStatic 1), 3 (0x10319e90), else the model's collide, static (physenv slot 8 CreatePolyObjectStatic).
- **VPhysicsInitShadow 0x102083a0**: needs an edict and not +0xd4 & 1; slot 0x270; +0x15c = -1.0; by solid type: 2 a box from the collision bounds shrunk 0.21875 each side (0x10319d20), 3 (0x10319e90), else PhysModelCreate 0x1031a3d0 (BSP lump 29 model, not static); then 0x10208190 with the solid_t from 0x1031a270 (SetDefaults before the keys); game data the entity, name its classname; the surfaceprop's index; CreatePolyObject (physenv slot 7). Then SetShadow(1e4, 1e4, allowMove, 0) (slot 68) and UpdateShadow(+0x1dc, +0x1e8, false, 0.0) (slot 69).
- **0x101f7f40**: unless movetype 6 and with +0x158: abs position recomputed if dirty (0x101fd3d0), then UpdateShadow(abs origin, abs angles, false, dt).
- **When a shadow is updated**: PhysicsPusher runs a push whenever the move time > 0: linear when the angular velocity is zero, rotating when the linear is, both otherwise. FinishPush 0x10303370: its pushers (0x10b5b1ac) appended to 0x10b5b1fc (0x10306ab0); every entity it pushed gets slot 0x1b4 then 0x101f7f40(gpGlobals->frametime). After the frame's simulate loop 0x10306950, 0x10303170: each frame pusher gets PhysicsTouchTriggers (0x1020a580) with its previous origin, the children list (0x10b5b210, 0x10355310) the same with null, then every one of both 0x101f7f40(frametime); both lists emptied. So a moving mover's shadow gets its new pose once a frame after every entity simulated, timeOffset 1/64.

## CPhysicsObject shadow calls

- **SetShadow 0x1001dac0** (maxSpeed, maxAngular, allowTranslation, allowRotation): a controller already at +0x10 only gets MaxSpeed; else +0x14 &= 0xe0, new 0xb0 CShadowController (0x10024990) at +0x10, its MaxSpeed, slot 26 (RecheckCollisionFilter).
- **UpdateShadow 0x1001db50** (pos, angles, tempDisableGravity, timeOffset): with a controller, when the flag differs from +0x14 & 0x1f it takes it and, if the controller allows translation (slot 5), EnableGravity((+0x14 & 0x1f) == 0) (slot 13); then Update 0x10024ff0 (timeOffset in xmm3).

## CShadowController

- **ctor 0x10024990**: +0x40..+0x48, +0x50..+0x58, +0x20..+0x28, +0x30..+0x3c, +0x64, +0x6c zero; +0x70 = 1.0, +0x74 = 0; `flags = ((rot & 1) << 1 | (trans & 1)) << 1 | (flags & 0xf0)`; then the attach.
- **attach 0x10024a60**:
  1. core = object +8 +0x94. Save core +0x20..+0x2c -> +0x90, +0x10..+0x1c -> +0xa0, +0x1c -> +0x80, object +0x18 -> +0x10.
  2. GetPosition (object slot 48) -> target `(x k, -(z k), y k)`; angles -> AngleVectors 0x100b8030 and SetPosition's basis (crazykart-physics.md 12) -> set_quaternion 0x1006d240 -> target quaternion.
  3. UseShadowMaterial(1) 0x10024e10: index 0xf000 unless already, via SetMaterialIndex 0x1001dca0: +0x18 = index, IVP material +0x88 = manager slot 11 of it; with callbacks held (+0x1c | 0x800) the core's 0x10076950 (each object's +0x44 = the core's movement byte, 0x10 static; a core not simulated (byte 1 == 8) has its unit revived now: 0x10071ef0 at env time; a simulated one 0x10071f70); then each object's friction synapses (+0x28) re-mixed: 0x10081280, 0x1008d230, 0x1008af60, material slots 3 / 2 into the contact's +0x44, 0x10082a60. So a new mover is simulated (byte 1 = 1) right after SetShadow; its collision side pairs there (the revival's recheck_ov_element with the object at 0x21).
  4. Core rot damping +0x20..+0x28 = 100.0.
  5. No allowRotation (flags & 4 == 0): inertia +0x10..+0x18 = 1e15, calc_calc 0x10077d40.
  6. No allowTranslation (flags & 2 == 0): SetMass(50000) (slot 28), EnableGravity(false) (slot 13).
  7. +0x84 = callback flags; SetCallbackFlags(`(f & 0xffdd) | 0x10`) (slot 22); EnableDrag(false) (slot 14); calc_calc; controller into the core's list (0x10071d40); +0x40..+0x48 zero.
- **MaxSpeed 0x10025250**: +0x68 = +0x6c = maxSpeed, +0x60 = +0x64 = maxAngular.
- **Update 0x10024ff0** (pos, angles, timeOffset): new target p = `(x k, -(z k), y k)`, q as in the attach; flags |= 1; unchanged when `((p.y - t.y)^2 + (p.x - t.x)^2) + (p.z - t.z)^2 < 1e-8` and `((|dx| + |dy|) + |dz|) + |dw| < 1e-8` (quaternion): return, nothing written. Else target = (p, q), seconds = `max(timeOffset, 0.0)`, object slot 24 (Wake).
- Interface slots: 1 Update, 2 MaxSpeed, 3 StepUp, 4 SetTeleportDistance, 5 / 6 AllowsTranslation / Rotation (bits 1 / 2), 7 / 8 Set / IsPhysicallyControlled (bit 3), 9 GetLastImpulse, 10 UseShadowMaterial, 11 ObjectMaterialChanged, 12 GetTargetPosition, 13 GetTeleportDistance, 14 GetMaxSpeed.

## The PSI step: 0x10024f20

- Priority 500 among the core's controllers (unit list order, crazykart-physics.md 9).
- Enabled bit off: +0x40..+0x48 zero, nothing else.
- Else 0x10024130; then with allowTranslation only (flags & 2; not a mover): when impulse.y +0x54 < `f = gravity (env +0xb4) x dt` and 0x100212d0, speed.y (core +0xd4) += `f - +0x54` and +0x54 += it.
- Then seconds -= dt, below 0 -> 0.

**0x10024130**:
1. fraction = 1.0; seconds > 0: `fraction = min(dt / seconds, 1.0)`; left = `max(seconds - dt, 0)`. fraction <= 0 (comiss 0, f; jae): return.
2. Position: core +0x90; unless object +0x44 & 0x800, plus the rows times the offset: `pos_i + ((m_i0 o0 + m_i1 o1) + m_i2 o2)`.
3. delta = target - pos.
4. teleportDistance (+0x54) > 0: dist^2 is, when last position (+0x20..+0x28) is all 0.0 (ucomiss, `lahf; test ah, 0x44; jp`: equal and ordered), `(dy^2 + dx^2) + dz^2` of delta; else `((pos.y - l.y)^2 + (pos.x - l.x)^2) + (pos.z - l.z)^2`. Above tele^2: teleport: collisions on (+0x44 & 0x100): +0x8c slot 4 (1), +0x44 &= ~0x100, +0x8c = 0, 0x10073ba0, beam 0x10074b20(q, p, 1), 0x10095180 (env +0x10, object), +0x44 |= 0x100; without collisions only the beam; delta = 0. (A mover sets no teleport distance.)
5. Linear: `scale = (1.0 / dt) x fraction`; 0x10020fa0(core +0xd0, delta, +0x48, +0x4c, scale, damping +0x50, out +0x30):
   - `s2 = (v0 v0 + v1 v1) + v2 v2`; s2 < 1e-6: v = 0; else maxDampSpeed > 0: `d = v x -damping`, `l = sqrtss(s2) x |damping|`; l > maxDampSpeed: `d x= maxDampSpeed / l`; `v_i + d_i`.
   - maxSpeed > 0: `a = delta x scale`, `l = sqrtss((d1^2 + d0^2) + d2^2) x scale`; l > maxSpeed: `a x= maxSpeed / l`; `v_i = v_i + a_i`; out = a (16 bytes, fourth lane a stack word). maxSpeed <= 0: out = 0.
   - With dampFactor 1 and the 1e4 limits a mover's speed is replaced by delta / dt x fraction each PSI.
6. Last position = `speed_i x dt + pos_i`.
7. Angular: dq = 0x10023fb0(target q +0x10, core q_next +0x110) = target x conj(current), c = -b.xyz:
   - `x = ((aw cx + ax bw) + az cy) - ay cz`, `y = ((aw cy + ay bw) + ax cz) - az cx`, `z = ((aw cz + az bw) + ay cx) - ax cy`, `w = ((aw bw - ax cx) - ay cy) - az cz`; `n = ((x^2 + y^2) + z^2) + w^2 > 1e-10`: each x `(1.0 / sqrtss(n))`.
   - `angle = acosf(dq.w)` (0x100d768b) + itself (addss); as a double > pi: `angle = f32(f64(angle) - 2 pi)`. `l = sqrtss((y^2 + x^2) + z^2)`; `inv = 1.0 / (l + 1.1920929e-7)`; axis x: `inv x dq.x x angle`; y, z: `dq x inv x angle`.
   - rot = core +0xc0; `r2 = (r0^2 + r1^2) + r2^2` < 1e-6: rot = 0; else maxDampAngular (+0x44) > 0: `d = rot x -dampFactor`, `l = sqrtss(r2) x |dampFactor|`, capped, `rot_i = rot_i + d_i`. maxAngular (+0x40) > 0: `a = axis-angle x scale`, `l = sqrtss((ax^2 + ay^2) + az^2) x scale`, capped, `rot_i = a_i + rot_i`.

## SetMass 0x1001c100 and a brush's AABB

- SetMass: not moveable (slot 10): EnableMotion(1) around it (slot 15). `m = mass < 0 ? 0 : minss(mass, 50000)`; `r = m / core mass`; core mass = m; `inertia_i x r`; 0x10077d40. Drag: +0x3c == 0.0 -> +0x40 = 1.0, else `v = maxss(+0x3c, 5.0)`, `+0x40 = (slot 29's mass / ((k k) k) v) / density`; 0x1001bc70. SetMass(50000) on a 50000 kg brush: r = 1.
- CollideGetAABB 0x10033120 of a ledge tree (root +0 not 0): 0x10032e60 from +-FLT_MAX, recursive: inner node's left child at +0x1c first, then the right at +[node]; a leaf's ledge (+4) as 0x1002c720, its support point (vtable slot 0) along the six directions, each axis into mins (strictly greater replaced) and maxs (strictly less). CreatePolyObject's drag basis needs it for any dynamic brush.

## What collides with a mover

ShouldCollide 0x102f6b10 (obj0, obj1, game0, game1), counter +0x158 around it:
1. Either game data null -> 1.
2. Same entity: the objects' game flags (slot 19) through the model's collision filter.
3. Past game flags 0x2 on both and callback flags 0x40 (0x102f6a40): slot 0x26c either way -> 0; both with edicts and one the other's owner (0x1014a4e0) -> 0; same move parent, or listed by the pair table -> 0.
4. Fixed: movetype 7 (PUSH) or 0 (NONE), 11 (CUSTOM) with a shadow controller (object slot 71), or a move parent (0x1016c7a0) and not VPHYSICS under a VPHYSICS parent. A fixed one collides only with a moveable object (slot 10); two fixed never; two shadows never.
5. Both solid types non-zero; solid flags (slot 12: 4 FSOLID_VOLUME_CONTENTS ... 8); game rules ShouldCollide(groups); contents (object slot 40) against the other's mask (slot 0x2a0) both ways; the pair table for the objects -> 0; else 1.

So the world (NONE) never collides with a mover (PUSH).

- **Friction listener 0x10011eb0** clears a contact's integrated energy (+0x48) only between two objects with CALLBACK_GLOBAL_FRICTION (+0x1c & 2), which the attach clears: a kart's contacts on a mover keep theirs.
- **Shadow material**: the surfaceproperties parser's fallback entry, made on its first run (0x10019ba1, +0x17c marks it): zeroed, vtable 0x100e2154, named by slot 0x3c (0xf000), 0x10019130's defaults, then friction 0.8, elasticity 0.001, inserted by 0x10019d30, index at +0x180. Mixed per side with the kart's.

## Unread

- VPhysicsInitStatic's else branch past +0x60 of the decompile: the contents / callback flags it sets.
- PhysModelCreate's params for a brush (mass, damping: the solid_t defaults), its callback / contents flags (SetContents / slot 26).
- Where 0x10306950 sits against PhysFrame in the server frame (the controllers then run in the next Simulate).
- +0xc's first value (whatever the allocation held).
- Teleport path (reached only past the teleport distance).
- ShouldCollide's volume-contents branch (slot 3, solid flags' 4); the collision groups' table.
- The shadow's collisions with the world and other shadows in vphysics (collision filter slot 26); CFuncWallToggle's TurnOff and a breakable's Break on its object.
