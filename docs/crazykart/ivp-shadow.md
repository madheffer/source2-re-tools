# IVP shadows: how CS:GO's movers push a kart (csgo legacy vphysics.dll + server.dll, 2026-11-17)

ze_crazykart_v4's doors, lifts, thwomps and walls (60 func_door, 33 func_movelinear, 5 func_rotating, 14 func_button,
1 func_brush; 14 func_wall_toggle, 20 func_breakable) are IVP objects the kart collides with. A mover is a **shadow**:
a moving IVP body (not static) whose speed a controller sets every PSI so it reaches the entity's pose. Everything
below is read from the disassembly (tools/re/game/disasm.py, now x86 too; Ghidra `/csgo_vphysics_legacy.dll`,
`/csgo_server_legacy.dll`). Addresses are vphysics unless marked server. All arithmetic SSE scalar single unless named.
Source units -> IVP: x k, -(z k), y k with k = 0.0254 (0x10106930, 0x3cd013a9); back by 39.370079 (0x10106934).

## 1. Which entity gets what (server)

- **CreateVPhysics** is CBaseEntity slot 154 (+0x268). CBaseDoor 0x1024e090, CFuncMoveLinear 0x10297c90, CFuncRotating
  0x10223660 (when solid), CFuncBrush 0x102df010, CBaseButton 0x10226ff0: **VPhysicsInitShadow(false, false, 0)**.
  CFuncWall / CFuncWallToggle 0x10221e30 and CBreakable 0x10224980: **VPhysicsInitStatic** 0x10207ff0.
- **VPhysicsInitStatic** 0x10207ff0: an entity with a move parent (+0xe8 a valid handle) is made a shadow instead
  (VPhysicsInitShadow(0, ?, 0); a parent of SOLID_BSP... sets SOLID 6 first: 0x10234040(6)); else by solid type
  (+0xf4's slot 11): 2 a box (0x10319d20 with isStatic 1), 3 (0x10319e90), else the model's collide, static (the
  world's path: physenv slot 8 CreatePolyObjectStatic, ported in create.rs). TODO(trace): the else branch's lines
  past +0x60 of the decompile, the contents / callback flags it sets.
- **VPhysicsInitShadow** 0x102083a0 (allowMove [ebp+8], allowRotate [ebp+0xc] (unused below), pSolid [ebp+0x10]):
  needs an edict (+0x1c) and not +0xd4 & 1; slot 0x270 (VPhysicsDestroyObject), +0x15c = -1.0; by solid type: 2 a box
  from the collision bounds shrunk by 0.21875 (0x10989910) each side (0x10319d20), 3 (0x10319e90), else
  **PhysModelCreate 0x1031a3d0** (the brush model's collide, the BSP's lump 29 model, not static); then
  0x10208190 (VPhysicsSetObject), with the solid_t from **PhysModelParseSolid 0x1031a270** (zeroed; each "solid"
  block parsed by vphysics' ParseSolid (parser slot 3) with the handler **g_SolidSetup** (0x10a4cc38, vtable
  0x108ac760: ParseKeyValue 0x101d38d0 does nothing, **SetDefaults 0x10319cd0 copies g_PhysDefaultObjectParams
  0x108ac5a8**: massCenterOverride 0, mass 1, inertia 1, damping 0.1, rotdamping 0.1, rotInertiaLimit 0.05, "DEFAULT",
  game data 0, volume 0, drag 1, enableCollisions 1, before the keys; without a handler ParseSolid leaves them 0);
  then game data the entity, name its classname), the surfaceprop's index and CreatePolyObject (physenv slot 7).
  ze_crazykart_v4's brush models carry `mass 50000`, a surfaceprop and a volume (finale_elevator1, model 101: "sand").
  Then **SetShadow(1e4, 1e4, allowMove, 0)** (CPhysicsObject slot 68, the push order at
  0x1020853c: allowRotation is the constant 0) and **UpdateShadow(abs origin +0x1dc, abs angles +0x1e8, false, 0.0)**
  (slot 69). TODO(trace): PhysModelCreate's params for a brush (mass, damping: the solid_t defaults) and its
  callback / contents flags.
- **UpdatePhysicsShadowToCurrentPosition(dt)** 0x101f7f40 is CBaseEntity slot 163 (+0x28c): unless movetype (+0xe6)
  is 6 (VPHYSICS) and with a physics object (+0x158): the abs position recomputed if dirty (+0xd4 bit 11,
  0x101fd3d0), then UpdateShadow(abs origin, abs angles, false, dt).
- **When a mover's shadow is updated**: PhysicsPusher (0x103053c0 -> 0x103050a0) runs a push whenever the move time
  is > 0: a linear one (0x10304f80 -> PerformLinearPush 0x10303da0) when the angular velocity is zero, a rotating one
  (0x10305010 -> PerformRotatePush 0x10303ec0) when the linear is, both otherwise. Each push ends in **FinishPush
  0x10303370**: its pushers (the 16-byte {entity, previous abs origin} list at 0x10b5b1ac) are appended to the frame's
  pusher list (0x10b5b1fc, 0x10306ab0), and every entity it pushed gets slot 0x1b4 then
  UpdatePhysicsShadowToCurrentPosition(gpGlobals->frametime (+0x14)). The frame's simulate loop 0x10306950 (every
  entity's 0x10306880), then **0x10303170**: each pusher in the frame list gets **PhysicsTouchTriggers** (slot 0x1b4,
  0x1020a580) with its previous origin, the second list (0x10b5b210: a pusher's children, 0x10355310) the same with
  null, then every one of both **UpdatePhysicsShadowToCurrentPosition(gpGlobals->frametime)**, and both lists are
  emptied. So a moving mover's shadow is told its new pose once a frame, after every entity has simulated, with
  timeOffset = the frame time (1/64). (0x101f7260's two calls with 0 are a physics-controlled entity's blocker check,
  not the pusher.) PhysicsRelinkChildren 0x101f7d40 passes its own dt to each child that isn't VPHYSICS.
  TODO(trace): where 0x10306950 sits against PhysFrame in the server frame (the controllers then run in the next
  Simulate).

## 2. CPhysicsObject's shadow calls (vtable 0x100e2878)

- **SetShadow** slot 68, 0x1001dac0 (maxSpeed, maxAngular, allowTranslation, allowRotation): a controller already
  there (+0x10) only gets MaxSpeed; else object +0x14 &= 0xe0, a 0xb0-byte CShadowController (ctor 0x10024990) at
  +0x10, its MaxSpeed, then slot 26 (RecheckCollisionFilter).
- **UpdateShadow** slot 69, 0x1001db50 (pos, angles, tempDisableGravity, timeOffset): with a controller: when the
  flag differs from object +0x14 & 0x1f the field takes it and, if the controller allows translation (its slot 5),
  EnableGravity((+0x14 & 0x1f) == 0) (slot 13); then the controller's Update (0x10024ff0, timeOffset in xmm3).
- slot 70 0x1001dbe0 GetShadowPosition, 71 0x1001dc80 GetShadowController, 72 0x1001dbb0 RemoveShadowController
  (the environment's +0x138 slot 0x68), 73 0x1001dde0 ComputeShadowControl (-> 0x100246e0; not used by movers).
- The environment's CreateShadowController is slot 25 (0x10014c20: the same 0xb0 ctor, returns +4).

## 3. CShadowController (0xb0 bytes; IVP_Controller vtable 0x100e2b80 at +0, IPhysicsShadowController 0x100e2b44 at +4)

Fields: +8 the CPhysicsObject, +0xc seconds to arrival, +0x10 (short) the object's +0x18, **+0x12 flags** (bit 0
enabled: set by the first Update; bit 1 allowTranslation, bit 2 allowRotation, bit 3 physically controlled), the
shadow params at **+0x20**: +0x20 target position (IVP), +0x30 target quaternion, +0x40 last position, +0x50 last
impulse, +0x60 maxAngular, +0x64 maxDampAngular, +0x68 maxSpeed, +0x6c maxDampSpeed, +0x70 dampFactor (1.0), +0x74
teleportDistance (IVP); +0x80 the core's mass saved, +0x84 the object's callback flags saved, +0x90 the core's +0x20..+0x2c
saved, +0xa0 the core's +0x10..+0x1c saved.

- **ctor 0x10024990** (object, allowTranslation, allowRotation): +0x40..+0x48, +0x50..+0x58, +0x20..+0x28, +0x30..
  +0x3c, +0x64, +0x6c zero; +0x70 = 1.0, +0x74 = 0; flags = ((rot & 1) << 1 | (trans & 1)) << 1 | (flags & 0xf0);
  then the attach. TODO(trace): +0xc is not written by the ctor (g_pMemAlloc doesn't zero): its first value is
  whatever the allocation held until an Update that changes the target writes it; read it from the oracle.
- **attach 0x10024a60**: core = object +8 (IVP object) +0x94. Saves core +0x20..+0x2c to +0x90, core +0x10..+0x1c to
  +0xa0, core +0x1c (mass) to +0x80, object +0x18 (u16) to +0x10. GetPosition (object slot 48) -> the target
  position (x k, -(z k), y k) and from the angles AngleVectors (0x100b8030) and the same basis as SetPosition
  (crazykart-physics.md 12) through set_quaternion 0x1006d240 -> the target quaternion. Its own slot 10
  **UseShadowMaterial(1)** (0x10024e10): material index 0xf000 ($MATERIAL_INDEX_SHADOW) unless the object has it,
  through **SetMaterialIndex** (object slot 39, 0x1001dca0): object +0x18 = the index, the IVP object's material +0x88 =
  the material manager's slot 11 (0x10116078 +0x2c) of it, then with callbacks held (+0x1c | 0x800) the core's
  **0x10076950** (calc_calc; each object's +0x44 = the core's movement byte, 0x10 when static; **a core not simulated
  (byte 1 == 8) has its unit revived now: 0x10071ef0 at the environment's time** (sleep.rs revive_unit), a simulated
  one its references' times reset (0x10071f70); then each object's friction synapses (+0x28) re-mixed for the new
  material: 0x10081280, 0x1008d230, 0x1008af60, the material's slots 3 / 2 into the contact's +0x44, 0x10082a60).
  So a new mover is simulated (byte 1 = 1, awake) right after SetShadow; its collision side pairs right there (the
  revival's recheck_ov_element with the object at 0x21). The shadow material: friction 0.8, elasticity 0.001 (8).
  **The core's rot damping +0x20..+0x28 = 100.0** (0x42c80000; +0x2c gets a stack lane:
  padding). Without allowRotation (flags & 4 == 0): **inertia +0x10..+0x18 = 1e15** (0x58635fa9) and calc_calc
  0x10077d40. Without allowTranslation (flags & 2 == 0): **SetMass(50000)** (object slot 28, 0x47435000) and
  **EnableGravity(false)** (slot 13). +0x84 = object callback flags; SetCallbackFlags((f & 0xffdd) | 0x10) (slot
  22); **EnableDrag(false)** (slot 14); calc_calc; the controller into the core's list (0x10071d40: append, sort);
  +0x40..+0x48 zero.
- **MaxSpeed** (interface slot 2, 0x10025250; ctrl = this - 4): +0x68 = +0x6c = maxSpeed, +0x60 = +0x64 = maxAngular.
  SetShadow passes 1e4, 1e4.
- **Update 0x10024ff0** (via interface slot 1, 0x100251d0; pos, angles, timeOffset): the new target p = (x k,
  -(z k), y k), q from the angles as in the attach; flags |= 1; **unchanged** when ((p.y - t.y)^2 + (p.x - t.x)^2) +
  (p.z - t.z)^2 < 1e-8 (0x100f3ba0, 0x322bcc77) and (((|q.x - t.x| + |q.y - t.y|) ... in the order
  `(|dx| + |dy|) + |dz|) + |dw|` < 1e-8: return (nothing written). Else target = (p, q), **seconds = max(timeOffset,
  0.0)** (0x100f3b60), object slot 24 (**Wake**).
- the other interface slots: 3 StepUp 0x10024e70 (beam up by height k), 4 SetTeleportDistance 0x10024ef0 (+0x74 =
  d k), 5 / 6 AllowsTranslation / Rotation (bits 1 / 2), 7 / 8 Set / IsPhysicallyControlled (bit 3), 9 GetLastImpulse
  0x10024d90, 10 UseShadowMaterial 0x10024e10, 11 ObjectMaterialChanged 0x10024e50, 12 GetTargetPosition 0x100251f0
  (returns the seconds), 13 GetTeleportDistance, 14 GetMaxSpeed 0x10025280.

## 4. The PSI step: do_simulation_controller 0x10024f20 (IVP_Controller slot 4)

The controller runs among the core's controllers (unit list order, crazykart-physics.md 9): its vtable 0x100e2b80
is 0 0x10004450, 1 0x10007e10, 2 0x10007ca0, 3 0x10004430, 4 do_simulation 0x10024f20, **5 priority 0x10013010 = 500**
(the drag controller's function; gravity's 0x10007cb0 is 1000), 6 name 0x10024d60 ("vphysics:shadow" 0x100e2d44),
7 0x10024950 (the dtor), 8 0x10025de0. With the enabled bit
off: +0x40..+0x48 zero, nothing else. Else **ComputeShadowControllerIVP 0x10024130** (ecx the IVP object, edx the
params +0x20, xmm2 the seconds +0xc, xmm3 the event's dt); then with allowTranslation only (flags & 2; not a mover):
when impulse.y +0x54 < f = gravity (env +0xb4) x dt and 0x100212d0 (the object touches something), speed.y (core
+0xd4) += f - +0x54 and +0x54 += it; then **seconds -= dt, below 0 -> 0**.

**0x10024130** (returns the seconds left, unused by the caller):
1. fraction = 1.0 (0x100f3d70); seconds > 0: fraction = min(dt / seconds, 1.0). left = max(seconds - dt, 0).
   fraction <= 0 (comiss 0, f; jae): return.
2. The object's position: core pos_now (+0x90); unless object +0x44 & 0x800 plus the rows (core +0x60 / +0x70 /
   +0x80, 16 bytes apart) times the object's offset (+0x30..+0x38): component i = pos_i + ((m_i0 o0 + m_i1 o1) + m_i2 o2).
3. delta = target - pos (each component).
4. teleportDistance (params +0x54) > 0: the distance^2 is, when last position (+0x20..+0x28) is all 0.0 (ucomiss,
   `lahf; test ah, 0x44; jp`: equal and ordered), (dy^2 + dx^2) + dz^2 of delta; else ((pos.y - l.y)^2 +
   (pos.x - l.x)^2) + (pos.z - l.z)^2. Above tele^2: **teleport**: with collisions on (object +0x44 & 0x100) the
   object's +0x8c slot 4 (1), +0x44 &= ~0x100, +0x8c = 0, 0x10073ba0, then beam_object_to_new_position 0x10074b20
   (q, p, 1) and, still off, 0x10095180 (env's +0x10, the object) and +0x44 |= 0x100; without collisions only the
   beam; delta = 0. TODO(trace): reached only past the teleport distance (0 on a mover: SetShadow sets none).
5. **Linear**: scale = (1.0 / dt) x fraction; **0x10020fa0**(the core's speed +0xd0, delta, maxSpeed +0x48 in xmm2,
   maxDampSpeed +0x4c in xmm3, scale, damping = dampFactor +0x50, out = last impulse +0x30):
   - s2 = (v0 v0 + v1 v1) + v2 v2; s2 < 1e-6 (0x100f3bac): **v = 0**; else maxDampSpeed > 0: d = v x -damping (each),
     l = sqrtss(s2) x |damping|; l > maxDampSpeed: d x= maxDampSpeed / l; v = v + d (each v_i + d_i).
   - maxSpeed > 0: a = delta x scale (each), l = sqrtss((d1^2 + d0^2) + d2^2) x scale; l > maxSpeed: a x= maxSpeed / l;
     v_i = v_i + a_i; out = a (16 bytes, its fourth lane a stack word). maxSpeed <= 0: out = 0.
   With dampFactor 1 and the 1e4 limits a mover's speed is replaced by delta / dt x fraction each PSI.
6. last position = pos + speed x dt (each: speed_i x dt + pos_i).
7. **Angular**: dq = **0x10023fb0**(target q +0x10, the core's q_next +0x110): target x conj(current) with c = -b.xyz:
   x = ((aw cx + ax bw) + az cy) - ay cz, y = ((aw cy + ay bw) + ax cz) - az cx, z = ((aw cz + az bw) + ay cx) - ax cy,
   w = ((aw bw - ax cx) - ay cy) - az cz; n = ((x^2 + y^2) + z^2) + w^2 > 1e-10 (0x100f3b94): each x (1.0 / sqrtss(n)).
   angle = acosf(dq.w) (the DLL's 0x100d768b: math/csgo_libm.rs) **+ itself** (addss); as a double > pi (0x100f3e70):
   angle = f32(f64(angle) - 2 pi (0x100f3ea0)). l = sqrtss((y^2 + x^2) + z^2) of dq; inv = 1.0 / (l + 1.1920929e-7)
   (0x100f3ba8); the axis' parts x inv then x angle (x: inv x dq.x x angle; y, z: dq x inv x angle).
   rot = core +0xc0; r2 = (r0^2 + r1^2) + r2^2: r2 < 1e-6: **rot = 0**; else maxDampAngular (+0x44) > 0: d = rot x
   -dampFactor, l = sqrtss(r2) x |dampFactor|, capped at maxDampAngular as above, rot_i = rot_i + d_i. maxAngular
   (+0x40) > 0: a = axis-angle x scale, l = sqrtss((ax^2 + ay^2) + az^2) x scale, capped at maxAngular, rot_i = a_i + rot_i.
   (core +0xc0 is the rot speed, +0xd0 the speed: both set directly, not through the pending changes.)

## 5. CPhysicsObject::SetMass (slot 28, 0x1001c100) and CollideGetAABB of a brush

- **SetMass**: not moveable (slot 10): EnableMotion(1) around it (slot 15, back off at the end); m = mass < 0 ? 0 :
  minss(mass, 50000 (0x100f3ff0)); r = m / core mass; core mass = m; inertia_i = inertia_i x r; calc_calc 0x10077d40;
  then the drag numbers: +0x3c == 0.0 -> +0x40 = 1.0, else v = maxss(+0x3c, 5.0 (0x100f3f20)), +0x40 = (slot 29's mass /
  ((k k) k) v) / the material's density (0x10116078 +0x10); ComputeDragBasis 0x1001bc70. A mover's SetMass(50000) on a
  50000 kg brush leaves the mass and inertia as they were (r = 1).
- **CollideGetAABB 0x10033120** of a ledge tree (a brush's collide: the root's +0 is not 0) takes **0x10032e60**
  (mins ecx, maxs edx from +-FLT_MAX; recursive: an inner node's left child at +0x1c first, then its right at
  +[node]; a leaf's ledge (+4) as the support object 0x1002c720, its support point along each of the six directions
  0x1010ad2c, 0x1010ad44, 0x1010ad5c, 0x1010ad20, 0x1010ad38, 0x1010ad50 (vtable slot 0), each point's three axes into
  mins (strictly greater replaced) and maxs (strictly less): the extremes of the leaves' points. CreatePolyObject's
  drag basis needs it for any dynamic brush (phy.rs now collects every leaf's points, create.rs aabb()).

## 6. Checked (2026-11-17)

rubikon/tests/KartOracle/Shadow.cs makes a mover the server's way in the oracle (a scenario's `shadow` line, `move`
events, UpdateShadow(pose, false, 1/64) each tick before the Simulate); scenarios/lift.txt (make-lift.mjs: ze_crazykart_
v4's finale_elevator1, brush model 101, standing, down at 80 u/s, still, a 2 deg/tick yaw turn and back up while
turning, 300 ticks, the pinned kart beside it). `cargo run --release -p ze-sim --bin shadow_check -- <scenario> <oracle
out> <the kart's .phy>` builds it by create.rs and shadow.rs and compares every tick: GetPosition, GetVelocity,
IsAsleep, the core's flags, speeds, pending changes, pose, rate, quaternions and movement references: **300 ticks
bit-identical**; and **a kart on the lift** (kart-lift.txt, make-kart-lift.mjs: on the map's world, dropped onto
the lift's top, carried down at 80 u/s, driven on it, then the lift turns 60 degrees and climbs 75 u with the kart
aboard; 420 ticks) bit-identical every tick through ivp_check (a `shadow` line: the mover a dynamic body after the
kart, World::add_shadow, its collision object paired at its revival, the shadow material, no friction callback;
IVP_Mindist_Recursive for its ledge tree: ivp-mindist.md 13; the solver's rule: 8). The shadow runs as World's own controller kind (Kind::Shadow, priority 500, beside the motion
controllers in psi_with's stage 2; World::add_shadow / update_shadow), the pinned kart beside it in its own unit.

## 8. What collides with a mover: CCollisionEvent::ShouldCollide (server 0x102f6b10) and the friction listener

The server's collision solver (CCollisionEvent's IPhysicsCollisionSolver part at +4: vtable 0x108a8188, 0
**ShouldCollide 0x102f6b10**, 1 ShouldSolvePenetration 0x102f78a0, 2 ShouldFreezeObject 0x102f7090, 3
AdditionalCollisionChecks 0x102f5e00, 4 ShouldFreezeContacts 0x102f7250; IPhysicsCollisionEvent at +0, vtable
0x108a81ac). ShouldCollide(obj0, obj1, game0, game1), a counter +0x158 around it: either game data null -> 1. The same
entity: by the objects' game flags (slot 19) through the entity's model's collision filter. Else, past the game
flags' 0x2 on both and the callback flags' 0x40 (0x102f6a40): slot 0x26c either way (the entities' own refusal) ->
0; both with edicts and one the other's owner (0x1014a4e0) -> 0; parented ones with the same move parent or ones the
game's pair table (0x10ba2a90 slot 3) lists -> 0. Then each entity is **fixed** when its movetype (+0xe6) is **7
(PUSH) or 0 (NONE)**, 11 (CUSTOM) with a shadow controller (object slot 71), or it has a move parent (0x1016c7a0)
and isn't VPHYSICS under a VPHYSICS parent. **A fixed one collides only with a moveable object (slot 10), two fixed
ones never, two shadows never**; both solid types non-zero (+0xf4 slot 11). Then the solid flags (slot 12: 4
FSOLID_VOLUME_CONTENTS ... 8), the game rules' ShouldCollide(collision group 0, 1) (0x10ba26a8 slot 0x70), the
contents (object slot 40) against the other entity's mask (slot 0x2a0) both ways, and the pair table for the objects
-> 0; else 1. TODO(trace): the volume-contents branch (slot 3, the solid flags' 4), the collision groups' table.

So the world (movetype NONE) never collides with a mover (PUSH): without that the lift sits on the shaft's walls.
The oracle's solver (Program.cs Solver) now answers by its game data (1 the world, 2 a kart, 3 a mover: Shadow.cs);
the port's pairing (collide_create.rs recheck_ov) asks `Collide::should_collide` by `Collide::game`.

**The friction listener** (vphysics 0x10011eb0, friction_sys.rs) clears a contact's integrated energy (+0x48) only
between two objects with CALLBACK_GLOBAL_FRICTION (+0x1c & 2), which the shadow's attach clears
(SetCallbackFlags((f & 0xffdd) | 0x10)): a kart's contacts on a mover keep theirs (`Collide::no_friction_callback`).

**The shadow material** (SetMaterialIndex 0xf000): the surfaceproperties parser's fallback entry, made the first
time it runs (0x10019ba1: +0x17c marks it; a zeroed entry, vtable 0x100e2154, named by slot 0x3c (0xf000), 0x10019130's
defaults, then **friction 0.8 (0x3f4ccccd, data +0x10) and elasticity 0.001 (0x3a83126f, +0x14)**, inserted by
0x10019d30, its index kept at +0x180): the mover's own material (Obj::material), mixed per side with the kart's.

## 7. What the kart port needs from it

A mover is one more IVP body: built by create.rs from its brush model's compact surface (the BSP's lump 29: model
N's solids, `extract_world.py <bsp> <folder> <N>`), revived by UseShadowMaterial, rot damping 100, inertia 1e15,
mass 50000, no gravity, no drag, with a shadow controller (priority 500) in its list that runs section 4.
Each server frame, after the entities simulate, every mover that moved has Update(abs origin, abs angles, 1/64).
Its contacts with a kart are two moving cores in one friction system: the karts-touching port (agent/kart-touch).
Still unread: the brush's contents and collision filter (PhysModelCreate's SetContents / slot 26), the shadow's collisions with the world and other
shadows (vphysics' CCollisionEvent ShouldCollide / the collision filter slot 26), CFuncWallToggle's TurnOff and a
breakable's Break on its object, the +0xc first value.
