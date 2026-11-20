# ze_crazykart_v4's kart in CS:GO physics

CS:GO legacy (32-bit): server.dll (md5 8048019154549052cb6dc057b76f6a85, Ghidra `/csgo_server_legacy.dll`, base 0x10000000), vphysics.dll (md5 d97cf2194594d7545427cdabc7376db4, Ghidra `/csgo_vphysics_legacy.dll`, base 0x10000000, no RTTI). The kart's model and .phy from the BSP's pakfile; surface scripts from csgo/pak01_dir.vpk.

Conventions:

- k = 0.0254f (vphysics 0x10106930, bits 3cd013a9), K = 39.370079f (0x10106934, bits 421d7af6), DEG = 57.29578f (vphysics 0x100f3fa0 / server 0x1098a204), RAD = 0.017453292f (vphysics 0x100f3bf4).
- Source <-> IVP axes (CPhysicsObject::GetVelocity 0x1001d110 and every conversion read): `ivp = (src.x*k, -(src.z*k), src.y*k)`; `src = (ivp.x*K, ivp.z*K, -(ivp.y*K))`. Angular: `ivp_w = (w.x, -w.z, w.y)` (rad), `src_w = (ivp.x, ivp.z, -ivp.y)*DEG`.
- IEEE single (SSE `mulss/addss`) unless noted; x87 where noted (atan2, fmod, sin/cos, friction products). Sum orders as written in the disassembly. The decompiler regroups sums (0x10074000's mass-centre offset shows `(a + b) + c` where the code does `c + (b + a)`): only the disassembly counts.

## Functions

| Address | Module | What |
|---|---|---|
| 0x1031a000 | server | PhysModelParseSolid |
| 0x108ac5a8 | server | g_PhysDefaultObjectParams (data) |
| 0x10357330 | server | CPhysicsProp::CreateVPhysics (vtable 0x108bc610 slot 0x268) |
| 0x102f7de0 | server | PhysSolidOverride |
| 0x10059d70 | server | a no-op SetDefaults (`ret 4`) |
| 0x102082c0 | server | VPhysicsInitNormal |
| 0x10356e70 | server | CPhysicsProp Spawn (renames prop_physics_override to prop_physics) |
| 0x1020a440 | server | SetCollisionGroup |
| 0x102ff850 | server | InputWake (only Wake) |
| 0x1031a3d0 | server | PhysModelCreate |
| 0x102ee3d0 | server | CPhysThruster Spawn |
| 0x102ee940 | server | CPhysThruster OnActivate |
| 0x102ee570 -> 0x102ee610 | server | ActivateForce -> create |
| 0x102ee730 | server | CPhysThruster Deactivate: DestroyMotionController, then the body's Wake (slot 24) |
| 0x102eea80 | server | CPhysThruster SetupForces |
| 0x102edf00 | server | CConstantForceController::Simulate |
| 0x1069af90 | server | MatrixAngles |
| 0x101fe600 | server | SetLocalAngles |
| 0x1069b0d0 / 0x1069b500 | server | matrix invert / concat |
| 0x102f0270 | server | CKeepUpright ctor |
| 0x102f0340 / 0x102f03a0 | server | CKeepUpright Spawn / Activate |
| 0x102efe80 / 0x102efe70 | server | TurnOff / TurnOn (set / clear ent+0x3bc) |
| 0x102f0500 | server | CKeepUpright::Simulate |
| 0x102f06d0 | server | ComputeRotSpeedToAlignAxes |
| 0x102f9750 | server | PhysFrame |
| 0x102f6950 | server | CPhysicsHook::FrameUpdatePostEntityThink |
| 0x1020a530 | server | (sv_alternateticks second call) |
| 0x102f5f60 | server | PhysicsInit |
| 0x102f61b0 | server | SetGravity(0, 0, -sv_gravity) |
| 0x10014cd0 | server | sv_gravity registered |
| 0x102fb9f0 | server | `air_density` console command |
| 0x102f6b10 | server | ShouldCollide |
| 0x102f78a0 | server | ShouldSolvePenetration (1 unless a pair has penetrated > 3 s, then frees it) |
| 0x102f7090 | server | ShouldFreezeObject |
| 0x102f5e00 | server | AdditionalCollisionChecksThisTick (only past 1200 checks) |
| 0x102f7250 | server | ShouldFreezeContacts |
| 0x103e5970 | server | VScript TraceLine registration (name 0x108e0c9c, binding 0x103e7d50) |
| 0x103e52a0 | server | TraceLine native |
| 0x1016cc20 | server | UTIL_TraceLine |
| 0x1016ce70 | server | the ray's build |
| 0x102a1530 | server | CGameUI::Think |
| 0x10357cb0 | server | CPhysicsProp::VPhysicsUpdate |
| 0x10207cd0 | server | CBaseEntity::VPhysicsUpdate |
| 0x107ba18a | server | CRT fmod (x87) |
| 0x101fdcd0 | server | SetAbsAngles |
| 0x10205f80 | server | VScript GetAngles native |
| 0x10206110 / 0x102060e0 / 0x102060b0 | server | GetForwardVector / GetLeftVector / GetUpVector |
| 0x101faa60 | server | CBaseEntity::GetVectors |
| 0x1031ab20 | server | PhysCreateWorld_Shared |
| 0x1031aa20 | server | the virtual terrain objects ([ivp-virtualmesh.md](ivp-virtualmesh.md)) |
| 0x106b3ce0 | server | stricmp |
| 0x100338c0 | vphysics | ParseSolid |
| 0x1001e6e0 | vphysics | the object template |
| 0x1008e1d0 | vphysics | IVP's template ctor |
| 0x1001e7a0 | vphysics | CreatePhysicsObject |
| 0x10013cb0 | vphysics | env slot 7 (CreatePolyObject) |
| 0x10074750 | vphysics | IVP_Real_Object init_object_core |
| 0x10072af0 | vphysics | core enable / disable motion |
| 0x10018ae0 / 0x10019180 | vphysics | surface props ctor / ParseSurfaceData |
| 0x1001ca30 | vphysics | CalculateVelocityOffset (vslot 0x100) |
| 0x1001c8a0 | vphysics | CalculateForceOffset (vslot 0xfc, not used by thrusters) |
| 0x1001a4f0 | vphysics | CPhysicsMotionController::do_simulation_controller (case table 0x1001aa64) |
| 0x10078650 | vphysics | the velocity clamp |
| 0x10014320 | vphysics | IPhysicsEnvironment::Simulate (env vslot 0x88) |
| 0x10014670 | vphysics | SetSimulationTimestep (env vslot 0x94) |
| 0x10084c80 | vphysics | the PSI wrapper |
| 0x10007cb0 | vphysics | gravity controller priority 1000 |
| 0x10013010 | vphysics | drag priority 500 |
| 0x1001b2fb | vphysics | sets a motion controller's priority 0x1f4 (500) |
| 0x10072170 | vphysics | the environment's gravity / damping controller (vtable 0x100e0a04) |
| 0x10076f20 | vphysics | damp_object |
| 0x10077520 | vphysics | commit pending pushes |
| 0x100d8112 | vphysics | CRT __libm_sse2_expf |
| 0x10013a70 | vphysics | SetGravity |
| 0x10012db0 | vphysics | CDragController::do_simulation_controller (vtable 0x100e1c1c) |
| 0x100134c3 | vphysics | drag ctor (air density) |
| 0x1001b3f0 | vphysics | CPhysicsObject::Init |
| 0x1001bc70 | vphysics | ComputeDragBasis |
| 0x10015070 | vphysics | SetPerformanceSettings (env vslot 0xec) |
| 0x10018970 | vphysics | get_friction_factor |
| 0x10026f60 | vphysics | the player-controller friction override (callback flag 0x40) |
| 0x10018a20 | vphysics | get_elasticity |
| 0x1008e020 / 0x1008e050 | vphysics | sums of two other per-material values (IVP base class) |
| 0x10072850 | vphysics | stage 2's unit walk |
| 0x10072540 | vphysics | a unit's stage 2 |
| 0x100723b0 | vphysics | the core's matrix at the current time |
| 0x100722d0 | vphysics | the sleep check |
| 0x10097d00 | vphysics | stage 3: the moved cores |
| 0x100970f0 | vphysics | IVP_Core's next-PSI step |
| 0x10096940 | vphysics | the step's rotation quaternion |
| 0x100975f0 | vphysics | the core's matrices / hull bookkeeping |
| 0x10097db0 | vphysics | stage 4: hull managers' synapse events |
| 0x10093bb0 | vphysics | hull manager reset (every 10 s) |
| 0x100952d0 / 0x10095310 | vphysics | stage 5 / stage 6 per object |
| 0x10074000 | vphysics | object matrix at the current PSI time |
| 0x10001b90 | vphysics | matrix -> Source angles |
| 0x1006ca90 | vphysics | the quaternion at t |
| 0x100d768b | vphysics | CRT acosf (SSE2) |
| 0x100d9542 | vphysics | CRT sinf (SSE2) |
| 0x10001930 / 0x10001950 | vphysics | fabsf / sqrtf |
| 0x100b8030 | vphysics | AngleVectors |
| 0x1006d240 | vphysics | IVP_U_Quat::set_quaternion(IVP_U_Matrix3) |
| 0x100a1030 | vphysics | new IVP_Polygon |
| 0x100734d0 | vphysics | IVP_Real_Object ctor |
| 0x10077f40 | vphysics | IVP_Core ctor |
| 0x10077e60 | vphysics | a new core's unit |
| 0x10071d40 | vphysics | a controller onto a core and unit |
| 0x10072d00 | vphysics | set_new_m_object_f_core (object slot 2) |
| 0x100760e0 | vphysics | a frame's inverse |
| 0x10078c90 / 0x10078cd0 / 0x10078cb0 | vphysics | compact surface manager slots 1 (mass centre) / 2 (radius) / 3 (rotation inertia) |
| 0x10077d40 | vphysics | calc_calc |
| 0x100c6bcd | vphysics | CRT _finite |
| 0x10075300 | vphysics | matrix product |
| 0x100775f0 | vphysics | the rest rates |
| 0x10033120 | vphysics | CollideGetAABB (collision slot 23) |
| 0x1000bbb0 | vphysics | CollideGetOrthographicAreas (slot 26) |
| 0x1002c720 / 0x1002d270 | vphysics | a ledge's support point |
| 0x1002c7d0 | vphysics | the collide transform |
| 0x10032e60 | vphysics | a ledge tree's AABB (unread) |
| 0x1001fcd0 | vphysics | (after Init, when the environment's slot 0x120 says so) |
| 0x1001b660 -> 0x10075060 | vphysics | Wake -> ensure_in_simulation |
| 0x10086b70 | vphysics | a queued core's revival |
| 0x100778d0 | vphysics | revive a core |
| 0x10082ce0 | vphysics | revive the object's friction |
| 0x10086390 | vphysics | an object's hull hash |
| 0x10087370 | vphysics | stage 1's revive queue |
| 0x10071ef0 | vphysics | revive a unit |
| 0x10071f70 | vphysics | the unit's references' times = now |
| 0x100782a0 | vphysics | a core's movement state |
| 0x10073a50 | vphysics | an object's invalid mindists rechecked ([ivp-pileup.md](ivp-pileup.md) 5) |
| 0x10071800 / 0x100713b0 / 0x10071710 / 0x100715c0 | vphysics | the unit's split / merge |
| 0x10071e40 / 0x10071dc0 / 0x10018430 | vphysics | controller list sort / unit removal / core removal |
| 0x10077820 / 0x10077750 | vphysics | freeze / the speeds zero |
| 0x10086d60 / 0x10086630 | vphysics | the frozen events to the listeners |
| 0x1001b680 | vphysics | IsAsleep (slot 2) |
| 0x10085720 | vphysics | the PSI's time event |
| 0x1001b670 -> 0x10073370 | vphysics | Sleep (slot 25) |
| 0x100872f0 | vphysics | a core out of the revive queue |
| 0x10073ba0 | vphysics | (per object, Sleep / EnableMotion) |
| 0x1001bfe0 | vphysics | EnableMotion (slot 15) |
| 0x1001ba00 | vphysics | slot 9: !(core flags & 0x10) |
| 0x10072c90 | vphysics | (pinned path) |
| 0x10094de0 | vphysics | recheck_ov_element |
| 0x1001ba50 | vphysics | EnableGravity (slot 13) |
| 0x1001d910 | vphysics | SetVelocity (slot 50) |
| 0x1001ba20 | vphysics | IsMoveable (slot 10) |
| 0x1001c700 | vphysics | ApplyForceCenter (slot 60) |
| 0x1001d4e0 / 0x1001db50 | vphysics | SetPosition (slot 46) / slot 69 called first |
| 0x10074b20 | vphysics | beam_object_to_new_position |
| 0x10097750 | vphysics | a core's teleport |
| 0x10014760 | vphysics | DestroyObject (env slot 10) |
| 0x10004150 | vphysics | into the delete queue |
| 0x10014f30 -> 0x100149f0 | vphysics | CleanupDeleteList (env slot 49) |
| 0x10013250 | vphysics | the environment's ctor (installs the anomaly manager at 0x10083fea) |
| 0x100836e0 | vphysics | IVP_Anomaly_Manager slot 1 (rot speed hook) |
| 0x10012b60 | vphysics | slot 0 (speed hook, vphysics') |
| 0x1001dc80 | vphysics | CPhysicsObject slot 71: the shadow (+0x10 ? +0x10 + 4 : 0) |
| 0x10024130 | vphysics | ComputeShadowControllerIVP ([ivp-shadow.md](ivp-shadow.md)) |
| 0x10019d00 | vphysics | material manager slot 1: world material index table |

## Fields

| Offset | Field |
|---|---|
| solid_t +0x400 | surfaceprop |
| solid_t +0x60c / +0x610 / +0x614 | index / contents / params |
| solid_t +0x618 / +0x61c / +0x620 / +0x624 | mass / inertia / damping / rotdamping |
| solid_t +0x634 / +0x638 | volume / drag |
| CPhysicsProp +0x70c / +0x710 / +0x718 | massScale / inertiaScale / overridescript |
| CPhysicsProp +0x4d4 | m_pPhysicsProp interaction (spawnflag 0x2000: vslot 100 (2)) |
| CBaseEntity +0x194 | m_rgflCoordinateFrame (rows) |
| CBaseEntity +0x1e8..+0x1f0 | abs angles |
| CBaseEntity +0x2e8 / +0x2ec | m_angRotation pitch / yaw |
| CBaseEntity +0x31c | spawnflags |
| CPhysThruster +0x390 | controller |
| CPhysThruster +0x398 / +0x39c | force / forcetime |
| CPhysThruster +0x3a0 | attached entity handle (attach1) |
| CPhysThruster +0x3a8 | integrator (CConstantForceController): +0 vtable, +4 controlType (+0x3ac), +8 linear (+0x3b0), +0x14 angular (+0x3bc) |
| CPhysThruster +0x3c8 | copies of linear / angular |
| CPhysThruster +0x3e0 | thruster local origin |
| CKeepUpright +0x390 | motion event (vtable 0x108a53c0): +4 worldGoalAxis (+0x394), +0x10 localTestAxis (+0x3a0), +0x28 angularlimit (+0x3b8), +0x2c active (+0x3bc), +0x2d dampAllRotation (+0x3bd) |
| player +0xc9c | buttons |
| trace_t +0x2c / +0x37 / +0x38 | fraction / startsolid / fractionleftsolid |
| template +4 | static |
| template +0x30 | rotInertiaLimit |
| template +0x34 | speed damping |
| template +0x40..+0x48 | rot damping |
| template +0x50 / +0x54 | extra radius / mass centre override |
| CPhysicsObject +8 | the IVP object |
| CPhysicsObject +0x10 | shadow |
| CPhysicsObject +0x15 | sleep state (& 3) |
| CPhysicsObject +0x1c | callback flags (& 2 CALLBACK_GLOBAL_FRICTION, 0x40 player controller, 0x200 CALLBACK_NEVER_DELETED, 0x400) |
| CPhysicsObject +0x24..+0x38 | drag basis (+0x24..+0x2c linear, +0x30..+0x38 angular) |
| CPhysicsObject +0x3c / +0x40 | volume / buoyancy ratio |
| CPhysicsObject +0x44 / +0x48 | drag / angular drag coefficient |
| object +0x24 / +0x30 | event table (slot 1 at `+0x24 + 0xc + 16 * +0x30`) |
| object +0x2c | rotation on the core (NULL on a prop) |
| object +0x30 | offset (-mass centre) |
| object +0x40 | cache |
| object +0x44 | state (8 not simulated, 1 simulated; +8 static; 0x100 collisions; 0x800 offset 0) |
| object +0x48..+0x70 | hull manager (+0x48 time, +0x50, +0x58 sums) |
| object +0x84 | surface manager (vtable 0x100e1064 compact) |
| object +0x8c | collision part |
| object +0x90 | extra radius |
| object +0x94 | core |
| core +0 | flags (bit 0 template +8, bit 1 static, 4 queued, 8 nearly spherical, 0x10 pinned, 0x20 alternate gravity; & 0xff3f) |
| core +1 | movement state byte (8 asleep, 1 revived; >= 2 adds 0.1 damping) |
| core +4 / +8 | radius / deviation (1000 at the ctor) |
| core +0x10..+0x18 | I |
| core +0x1c | m |
| core +0x20..+0x28 | rot damping |
| core +0x30..+0x38 / +0x3c | 1/I / 1/m |
| core +0x40 | speed damping |
| core +0x44 | 0.5 / radius |
| core +0x48 | car wheel |
| core +0x5c | spin rate |
| core +0x60 / +0x70 / +0x80 | rows of the core -> world rotation M |
| core +0x90..+0x98 | mass-centre world position (IVP m) |
| core +0xa0 / +0xb0 | pending rot speed change / speed change |
| core +0xc0 | rot speed (core-local, rad/s) |
| core +0xd0 | speed (world, m/s) |
| core +0xe0 / +0xf0 | position / delta |
| core +0x100 / +0x110..+0x11c | q_last / q_next |
| core +0x120 | (1, 0, 0) at rest |
| core +0x130 | t_psi |
| core +0x138 / +0x13c | 1/dt / `|speed|^2` |
| core +0x140 | controller list |
| core +0x150 / +0x160 / +0x180 | reference 1: t / q / pos |
| core +0x158 / +0x170 / +0x190 | reference 2: t / q / pos |
| core +0x1a4 | 0 at rest |
| unit +0 | state (< 8 active, 8 asleep), flags above it (0x300 split / merge, 0x400 / 0x800 / 0xc00 / 0x3000 speed) |
| unit +4 / +8 | prev / next |
| unit +0xe / +0x10 | cores: count / list |
| unit +0x1e / +0x20 | controllers: count / list |
| sim units manager (env+8) +0x18 / +0x1a8 | active / sleeping list heads |
| env+0 | gravity controller (with the damping) |
| env+4 | the time manager (its +4 object's slot 0) |
| env+0x10 | object list (+8, next +0x74) |
| env+0x1c | the application environment (+0x20 / +0xc) |
| env+0x20 | anomaly manager (vphysics' CCollisionSolver part, vtable 0x100e1c50) |
| env+0x24 | settings: +8 max speed, +0xc, +0x10 max angular per PSI, +0x14 (manager budget), +0x18 / +0x1c clamped [1, 50000] |
| env+0x28 | lock (slot 0 / slot 2) |
| env+0x2c / +0x94 | (stage 1: 0x100868f0 / the object's slot 0x28) |
| env+0x88 | 0.3 s (movement reference timeout) |
| env+0xa1 / +0xa2 | in a Simulate / delete queue on |
| env+0xa8 / +0xac | dt / 1/dt |
| env+0xd2 / +0xd4 | PSI listeners: count / list |
| env+0xd8: +0xda / +0xdc | the revive queue: count / array |
| env+0xf0 | the clock (f64) |
| env+0xf8 | the next PSI's time |
| env+0x100 | the last PSI's time |
| env+0x108 | time events counted |
| env+0x110 | countdown (u16, starts 10) |
| env+0x114 | PSI stage |
| env+0x118 | `expf(dt * -0.105360545)` |
| env+0x11e / +0x120 | global object listeners: count / list |
| IVP_Compact_Surface +0 / +0xc / +0x18 / +0x1c / +0x20 | mass centre / rotation inertia per unit mass / upper_limit_radius / byte radius deviation / ledge tree root |
| vcollide_t | 16 bytes: solids at +4, text at +8 |

## Constants

| Value | What |
|---|---|
| 0x10a4c7b8 | phys_timescale (server, default "1") |
| sv_gravity | "800" ("World gravity.") |
| 0x3c800000 | 0.015625 (SetSimulationTimestep) |
| 0x100f4064 | -0.105360545 (ln 0.9) |
| 0x100f3c60 | 0.1 |
| 0x100f3cf8 / 0x100f3cb0 | 0.5 / 0.25 (damping switches) |
| 0x40000000 | air density 2.0 |
| 0x41700000 | 15.0 (CKeepUpright angularlimit default) |
| 0x1098971c | 1.1920929e-07 |
| 0x10989828 | the radians factor (server) |
| 0x100f3e50 | 1.99999 |
| 0x1010a9a8 | the LCG seed (1 in a fresh process) |
| 0x4b | LCG multiplier |
| 1.5258789e-05 | 2^-16 |
| 0x100f4084 | -1 |
| 0x100f3b94 | 1e-10 |
| 0x100f3bb0 | 9e-6 |
| 0x100f3be0 | 0.004 |
| 0x100f3cc0 | 0.33333334 |
| 0x10120b04 | the zero vector |
| 0x7fffffff | andps abs mask |
| 0x1010ad20 | support directions +x, -x, +y, -y, +z, -z |
| 0x3c783e10 | f32(1/66): the environment's ctor dt (0x100841d1, 0x10084434) |
| 0x100f3b68 | 0.0 (t_psi test) |
| 0x100f3ed8 | 20.0 |
| 0x100f3d38 / 0x100f3d60 | 0.9 / 0.99 (limit hooks) |
| 0x100fc79c | 1.0 |
| 0x46b8aa3b / 0x100fc788 | 23637.115 / 23637.115549924776 |
| 0x100fc790 | 4.230634646972322e-05 |
| 0x100fc708 / 0x100fc608 / 0x100fc508 | expf tables |
| 0x42aeac4f / 0x42b17218 | 87.3366 / 88.7228 |
| 0x31800000 / 0x12000000 | expf range test |
| 0x100fd870 / 0x100fae60 | acosf tables; constants 0x100fb660..0x100fb68f |
| 0x100fdc80 | sinf: 64 (sin, cos) rows |
| 0x2000b | TraceLine mask: CONTENTS_SOLID 0x1 \| WINDOW 0x2 \| GRATE 0x8 \| MONSTERCLIP 0x20000 (MASK_NPCWORLDSTATIC by value) |
| 0x108dce68 | CTraceFilterSimple vtable |
| buttons | IN_MOVERIGHT 0x400, IN_MOVELEFT 0x200, IN_FORWARD 0x8, IN_BACK 0x10, IN_ATTACK 0x1, IN_ATTACK2 0x800 |
| 0x10ae7fe0 | the global CCollisionEvent: +0 collision events vtable 0x108a81ac, +4 solver 0x108a8188, +8 object events 0x108a81a0 |
| 0x10a4cc38 | g_SolidSetup (ParseSolid handler) |
| 0x10be50f0 / 0x10be50fc | the world's origin / angles (zero) |
| 0x10ba2574 | the engine interface (server) |
| 0x101160e8 | CIVPMaterialManager object (vtable 0x100e20cc) |
| 0x10116078 | VPhysicsSurfaceProps001 singleton |

## 1. The kart body

luffaren_kartphys.mdl (i_kart_phys): studiohdr v49, flags 0x11, 1 bone `static_prop`, pos (0,0,0), quat (0,0,0,1), poseToBone identity (the .phy vertices are entity space). hull_min (-28.743, -21.675, -8.207), hull_max (31.757, 21.689, 7.917); surfaceprop "none", $mass 1246.6388, contents 0x1.

luffaren_kartphys.phy: 1 solid, one convex ledge (is_compact 1), 56 triangles, all material 0, 30 vertices; hull x [-28.49, 31.51], y [-21.43, 21.44], z [-7.96, 7.67]. Compact surface: mass_center (IVP m) (0.023804808, 0.006797736, 0.000179228) = Source (0.93720, 0.00706, -0.26763); rotation_inertia per unit mass (IVP axes) (0.0973081, 0.2032861, 0.1793339) (IVP y = Source vertical); upper_limit_radius 0.93437 m; dragAxisAreas (0.99325, 0.96505, 0.98760). Text: `solid { "mass" "1246.638794" "surfaceprop" "none" "damping" "0" "rotdamping" "0" "inertia" "1" "volume" "38037.285156" }`, `editparams { "totalmass" "1246.638794" "concave" "1" }`; no "drag", no "rotinertialimit".

luffaren_kart.mdl (i_kart_visual, prop_dynamic parented, angles 0 270 0, solid 0): hull_min (-39.570, -46.927, -20.697), hull_max (39.570, 37.027, 29.122), 15 bones, surfaceprop "metal". Not simulated.

### Solid parameters

1. PhysModelParseSolid: memset, then the objectparams defaults (= g_PhysDefaultObjectParams): massCenterOverride 0, mass 1, inertia 1, damping 0.1, rotdamping 0.1, rotInertiaLimit 0.05, name "DEFAULT", volume 0, dragCoefficient 1.0, enableCollisions 1.
2. ParseSolid overwrites from the .phy text (solid_t fields above; "drag" key -> +0x638). Kart: mass 1246.6388, inertia 1, damping 0, rotdamping 0, volume 38037.29, drag 1.0, rotInertiaLimit 0.05.
3. CreateVPhysics: massScale > 0: mass *= it (kart: 0). inertiaScale > 0: inertia *= it, then max(inertia, 0.5) (kart 1.0). overridescript -> PhysSolidOverride builds `solid { "damping" "5" "rotdamping" "10" }` and re-parses it with the no-op SetDefaults: kart damping 5, rotdamping 10. Then VPhysicsInitNormal(SOLID_VPHYSICS 6, 0, startAsleep = spawnflags & 1, &solid).
4. Template 0x1001e6e0 (over 0x1008e1d0: mass 1, rot_inertia_is_factor 1, factors 1, rot_inertia_limit 0.03, damping 0.01): `mass = 0.1 > m ? 0.1 : minss(m, 50000)`; material = GetIVPMaterial(index < 0 ? 0 : index); inertia factor (3 axes) = `0 >= f ? 1 : f`, then minss(., 1e18); rot damping = rotdamping; speed damping = damping; rotInertiaLimit; +4 static. Drag only when dragCoefficient != 0 and not static.
5. Core: m = template mass (< 0.003 -> 1.0); `I_i = (factor_i x ri_i) x m`; limit: `L = sqrtf((I0^2 + I1^2) + I2^2) x limit`, I_i = L where L > I_i.

Kart: m = 1246.6388, 1/m = 8.02157e-4; I (IVP x, y, z) = (121.30805, 253.42433, 223.56458) kg m^2 (Source roll 121.31, yaw 253.42, pitch 223.56); L = 17.95 (not binding); 1/I = (0.008243476, 0.003945951, 0.0044729807). Mass centre (core position) = Source (0.93720, 0.00706, -0.26763) from the origin.

### Material "none"

- PhysModelCreate: GetSurfaceIndex("none") = -1 (with CS:GO's scripts parsed "default" is index 0), clamped to 0 by CreatePhysicsObject; SetContents when the model's contents differ; VPhysicsInitNormal Wakes it unless start-asleep.
- scripts/surfaceproperties_cs.txt (the manifest lists only this file) "default": density 2000, elasticity 0.25, friction 0.8, dampening 0.0.
- The map fires `i_kart_phys AddOutput "material 1001"` at start (i_kart_start): unread.

## 2. phys_thruster (CPhysThruster : CPhysForce)

Vtable base 0x108a4d40 (SetupForces slot 0x320 = 0x108a5060, OnActivate 0x108a5064, Spawn slot 0x64 = 0x108a4da4).

| Spawnflag | Where | Effect |
|---|---|---|
| 0x2 | SetupForces 0x102eecea | off: linear zeroed |
| 0x4 | SetupForces 0x102eecf9 | off: angular zeroed |
| 0x8 | Spawn, OnActivate, SetupForces | local: controlType 1 (SIM_LOCAL_ACCELERATION) else 3 (SIM_GLOBAL_ACCELERATION), `((~flags & 8) | 4) >> 2`; OnActivate converts the thruster's angles into the body's frame (MatrixAngles -> SetLocalAngles); SetupForces uses the LocalToWorld paths |
| 0x10 | SetupForces 0x102eeb3a | ignore mass: F *= GetMass (vslot 0x74): an acceleration = force |
| 0x20 | OnActivate 0x102eea56 | ignore position: local origin (0,0,0) (the body origin, not the mass centre) |

Kart: t_f 58 = 0x2|0x8|0x10|0x20; t_s 28 = 0x4|0x8|0x10 (torque only, uses its position); t_u 50 = 0x2|0x10|0x20 (world).

- OnActivate (on entity activation, not per Activate input): local origin = translation of `inverse(body EntityToWorld) x thruster transform`. Kart t_s: thruster (-13800, 14848, -15864), body (-13824, 14848, -15864) -> (24, 0, 0).
- ActivateForce: a controller present (+0x390 != 0) ignores it (a re-Activate never recomputes; the script Deactivates first). Else SetupForces once, stored in the integrator, `physenv->CreateMotionController(&integrator)` (env vslot 0x74), `AttachObject(pPhys, true)`, Wake. forcetime != 0 schedules ForceOff (the kart's: 0, stays on). Changing force / angles while active does nothing until the next Activate.
- CConstantForceController::Simulate: returns controlType, copies linear and angular out unchanged.

### SetupForces 0x102eea80

```
p = angRotation.x * RAD, y = angRotation.y * RAD     (SSE: angle x 0x10989828 as float)
fld dword; fsincos; fstp dword (cos); fstp dword (sin)   for yaw, then pitch
F = ( (cp*cy)*force, (cp*sy)*force, (-sp)*force )      (SSE)
if (flags & 0x10) F *= pPhys->GetMass()
if (flags & 0x8):
    worldPos = pPhys->LocalToWorld(localOrigin)            (vslot 0xe0)
    Fw       = pPhys->LocalToWorldVector(F)                (vslot 0xe8)
    pPhys->CalculateVelocityOffset(Fw, worldPos, &linW, &angular)   (vslot 0x100)
    linear   = pPhys->WorldToLocalVector(linW)             (vslot 0xec)
else:
    worldPos = attached entity m_rgflCoordinateFrame (ent+0x194..) * localOrigin
    pPhys->CalculateVelocityOffset(F, worldPos, &linear, &angular)
if !(flags & 2) linear = 0 ; if !(flags & 4) angular = 0
```

### CalculateVelocityOffset 0x1001ca30

core = object(+8)->core(+0x94).

```
Fx = F.x*k ; Fy = -(F.z*k) ; Fz = F.y*k
rx = P.x*k - c.x ; ry = -(P.z*k) - c.y ; rz = P.y*k - c.z
cx = (ry*Fz) - (rz*Fy) ; cy = (rz*Fx) - (rx*Fz) ; cz = (rx*Fy) - (ry*Fx)
a0 = (m70*cy + m60*cx) + m80*cz      (M^T c, core-local)
a1 = (m74*cy + m64*cx) + m84*cz
a2 = (m78*cy + m68*cx) + m88*cz
angular (Source local, deg/s) = ( (invI.x*a0)*DEG, (invI.z*a2)*DEG, -((invI.y*a1)*DEG) )
linear  (Source, u/s)         = ( (Fx*invm)*K, (Fz*invm)*K, -((Fy*invm)*K) )
```

The angular output is body-local; the linear output is in F's frame.

### do_simulation_controller 0x1001a4f0 (per PSI)

Per attached core, `ret = event->Simulate(controller, pObject, dt, &L, &A)` (dt the PSI's), by table 0x1001aa64 (1 local accel, 2 local force, 3 global accel, 4 global force):

- 1: `l = (L.x*k, -(L.z*k), L.y*k)`; `speed.y += ((m74*l.y + m70*l.x) + m78*l.z)*dt`, `speed.z += ((m84*l.y + m80*l.x) + m88*l.z)*dt`, `speed.x += ((m64*l.y + l.x*m60) + m68*l.z)*dt` (written `(sum*dt) + speed`); `rot.y(+0xc4) += (-(A.z*RAD))*dt ; rot.x(+0xc0) += (A.x*RAD)*dt ; rot.z(+0xc8) += (A.y*RAD)*dt`.
- 3: `speed += (L.x*k, -(L.z*k), L.y*k)*dt` (world); angular added in core-local axes exactly as case 1.
- 2 / 4 multiply by 1/m and 1/I.
- Then the clamp 0x10078650.

### The kart's values (identity orientation)

- t_f forward (3750, angles 0 0 0): 3750.0 u/s^2 along local +x, angular zeroed. Script value FORWARD_SPEED*max(speedmod,0.1).
- t_f back (1500, angles 0 180 0): -1500.0 u/s^2 along local x (plus -1.3e-4 on y from cos/sin(pi)).
- t_u (angles -90 0 0 / 90 0 0, force |jumpamount|): world +z / -z, force u/s^2, type 3.
- t_s (300, angles 0 90 0 / 0 270 0, at (24,0,0)): angular (-30.4995, ~0, +1258.1016) deg/s^2 for yaw 90, (+30.4995, ~0, -1258.1016) for 270: yaw +-1258.10 deg/s^2 plus a roll term from the mass centre 0.268 u below the origin. SpinOut sets force 3000.. (linear scaling; it also overwrites pitch / roll).
- Applied as `+= a*dt` each PSI while the controller exists.

## 3. Step, damping, gravity, drag, limits, friction

### The step

- PhysFrame from FrameUpdatePostEntityThink (after entity thinks) with `dt = (gpGlobals->frametime > 0) ? gpGlobals->interval_per_tick : 0`; a second call only with `sv_alternateticks` and maxclients == 1. dt clamped <= 0.1, times phys_timescale, then `physenv->Simulate(dt)`.
- PhysicsInit: SetSimulationTimestep(0.015625): ivpEnv+0xa8 = dt, +0xac = 1/dt, +0x118 = `expf(dt * -0.105360545)` (its reader unread).
- Simulate: ignores dt <= 0.0001 or > 1, clamps > 0.1 to 0.1; dt == the PSI dt: one PSI (0x10084c80), else simulate_until(time + dt). 64-tick server: one 1/64 s PSI per tick.

### Gravity and damping: 0x10072170

```
for each core in the controller's list (back to front):
    if (core.flags0 & 0x10) continue          // pinned (EnableMotion(false))
    rotD = core.rotDamp (+0x20..), linD = core.speedDamp (+0x40)
    if (core.byte1 >= 2) { rotD += 0.1 each axis; linD += 0.1 }
    damp_object(core, dt, rotD, linD)          // 0x10076f20
    commit (0x10077520): rot += rot_change, speed += speed_change, changes = 0
    g = (core.flags0 & 0x20) ? this+0x20 : this+0x10
    speed.y = g.y*dt + speed.y ; speed.z = g.z*dt + speed.z ; speed.x = dt*g.x + speed.x
```

damp_object 0x10076f20 (dt the PSI's):

```
r = (rotD.x*dt, rotD.y*dt, rotD.z*dt)
if ((r.y*r.y + r.x*r.x) + r.z*r.z  <  0.5):  fr_i = 1.0 - r_i
else:                                         fr_i = expf(-r_i)       (0x100d8112)
s = dt*linD
if (s < 0.25): fs = 1.0 - s  else fs = expf(-s)
rot.z *= fr.z ; rot.x *= fr.x ; rot.y *= fr.y ; speed.x,y,z *= fs
```

Kart (dt 1/64, damping 5, rotdamping 10): r = 0.15625, |r|^2 = 0.0732 -> rot *= 0.84375; s = 0.078125 -> speed *= 0.921875 (byte1 >= 2: 5.1 / 10.1 -> 0.9203125 / 0.8421875).

Gravity: the server's `SetGravity(0, 0, -sv_gravity)` (default 800; the map never changes it). SetGravity 0x10013a70: `g_ivp = (g.x*k, -(k*g.z), g.y*k)` = (0, 20.32, 0) m/s^2.

### Drag: 0x10012db0

Air density 2.0 (ctor `mov [eax+4], 0x40000000`; `air_density` only a console command). Per core with drag (coefficient 1.0):

```
v = speed (world) ; vl = M^T v  (vl.x = m70*v.y + v.x*m60 + m80*v.z, vl.y = col1.v, vl.z = col2.v)
f = (((|vl.y|*basis[0x28] + |vl.x|*basis[0x24]) + |vl.z|*basis[0x2c]) * dragCoef(+0x44)) * -0.5 * density * dt
f = max(f, -1); if (f < 0) speed += speed*f
fa = -((((|w.y|*abasis[0x34] + |w.x|*abasis[0x30]) + |w.z|*abasis[0x38]) * angDragCoef(+0x48)) * density * dt)
fa = max(fa, -1); if (fa < 0) rot += rot*fa
```

The kart's basis (live object): (3.4425e-4, 1.2845e-3, 4.7913e-4), angular (8.0911e-4, 4.4041e-4, 6.5126e-4); coefficients 1, 1. The builder: section 11.

### Velocity limits

The server's SetPerformanceSettings {10, 250, maxVelocity 2000, maxAngularVelocity 3600, 1.0, 0.5, minFrictionMass 10, maxFrictionMass 2500} (server 0x102f5f9c..). 0x10015070: settings +8 = `maxVelocity x k` (50.8 m/s), +0xc / +0x14 copied, +0x10 = `(maxAngularVelocity x 0.017453292) x env+0xa8` (the PSI step then: the server calls it before SetSimulationTimestep, so 1/66), +0x18 / +0x1c clamped to [1, 50000]; env+0x1c +0x20 / +0xc from +0x10 / +0x14.

The clamp 0x10078650 (after every motion controller and impulse): speed and speed change to 50.8 m/s; rot speed to `inv_dt x 0.95203` rad (settings+0x10, 3600 deg x 1/66) = 60.93 rad/s; the rot change scaled by that limit over |speed change| (IVP's slip).

### Friction and elasticity

CIVPMaterialManager (vtable 0x100e20cc):

- get_friction_factor: unless 0x10026f60 applies, `mu = mat0.friction * mat1.friction` (x87 fmul, rounded to float), clamped [0, 1]. One factor per contact.
- get_elasticity: `e = mat0.elasticity * mat1.elasticity`, clamped <= 1.0.
- Kart (default 0.8) on a `default` brush: mu = 0.64, e = 0.0625. World surfaces take each brush texture's VMT `$surfaceprop`.
- The solver: [ivp-contacts.md](ivp-contacts.md) (ivp_friction.cxx 0x10083110 / 0x100816a0, ivp_mindist_friction.cxx 0x1008d230, the friction impulse code around 0x100890a0).

## 4. phys_keepupright (CKeepUpright)

Ctor vtable 0x108a509c; angularlimit default 15.0, dampAllRotation 0.

- Spawn: localTestAxis = (0,0,1); worldGoalAxis = the entity's own up (GetVectors(0,0,&up), vslot 0x220; angles 0 0 0 -> (0,0,1)); active = !(spawnflags & 1). Kart: spawnflags 0, active at spawn; the script's TurnOff / TurnOn.
- Activate: CreateMotionController(event), AttachObject(body, false).
- "angularlimit" KeyValue / AddOutput writes +0x3b8 (the script sets 150, then 5 after 2 s; the map 15).

### Simulate 0x102f0500 (returns 1, linear 0)

```
if (!active) return 0 (SIM_NOTHING)
pPhys->GetVelocity(NULL, &w)              // local ang vel, deg/s (rot + pending rot change)
pPhys->GetPositionMatrix(&M)
G.x = (g.x*M00 + g.y*M10) + g.z*M20
G.y = (g.x*M01 + g.y*M11) + g.z*M21
G.z = (g.x*M02 + g.y*M12) + g.z*M22
invDt = 1.0 / dt
r = ComputeRotSpeedToAlignAxes(T = localTestAxis, G, w, damping = dampAll ? 0 : 1, invDt, angularlimit)
angular = dampAll ? (r - w) * invDt : r * invDt        // per component: (r.x - w.x)*invDt ...
```

### ComputeRotSpeedToAlignAxes 0x102f06d0

```
c.x = G.z*T.y - G.y*T.z ; c.y = G.x*T.z - T.x*G.z ; c.z = T.x*G.y - G.x*T.y      (T x G)
s = sqrtss((c.y*c.y + c.x*c.x) + c.z*c.z)
inv = 1.0 / (s + 1.1920929e-07)
d = (T.x*G.x + G.y*T.y) + T.z*G.z
a = c * inv
angle = fpatan(s, d) [= atan2(s, d), x87, stored float] * 57.29578
proj = (w.y*a.y + w.x*a.x) + w.z*a.z
r_i = ((a_i*invDt)*angle) - ((a_i*damping)*proj)
m = sqrtss((r.y*r.y + r.x*r.x) + r.z*r.z)
r_i = (r_i * (1.0/(m + 1.1920929e-07))) * min(m, angularlimit)
```

Each PSI adds (case 1, `rot += (A*RAD)*dt`) exactly r deg/s (damping 1: the spin about the axis replaced by angle/dt), at most `angularlimit` deg/s per step.

## 5. prop_physics_override spawnflags 13838 = 0x360E

| Bit | Where | Effect |
|---|---|---|
| 0x1 | CreateVPhysics | start asleep (kart: off) |
| 0x2 | unread | (no physics damage, by SDK naming) |
| 0x4 | Spawn 0x10356f09 | SetCollisionGroup(1 + (flags&0x1000 ? 1 : 0)): kart group 2 |
| 0x8 | CreateVPhysics | EnableMotion(false) (also when damagetoenablemotion > 0 or forcetoenablemotion > 0): pinned, 1/m and 1/I zeroed, velocities zeroed |
| 0x80 | Spawn | EFlags \|= 0x200000 (kart: off) |
| 0x200 | CreateVPhysics | physics game flags \|= 0x80 |
| 0x400 | unread | |
| 0x1000 | Spawn | the debris group variant above |
| 0x2000 | Spawn 0x10357113 | +0x4d4 vslot 100 (2): meaning unread |
| 0x200000 | CreateVPhysics | clears a byte of the solid before creation (kart: off) |

Open: with 0x8 the body is created pinned. Nothing in the kart's I/O or scripts sends EnableMotion (only the shell items do); InputWake only Wakes; ActivateForce and CKeepUpright::Activate don't enable motion. What re-enables it in-game is not found (candidates: CPhysicsProp's touch / damage paths for 0x400 / physdamagescale, the "material" keyvalue, point_template spawning of i_kart). Group 2's ShouldCollide: [ivp-pileup.md](ivp-pileup.md) 8.

## 6. VScript TraceLine and game_ui

TraceLine(start, end, ignore), native 0x103e52a0:

```
ignoreEnt = ignore ? HScript->entity : NULL
UTIL_TraceLine(start, end, MASK 0x2000b, ignoreEnt, COLLISION_GROUP 0, &tr)      (0x1016cc20)
return (tr.fractionleftsolid != 0 && tr.startsolid) ? 1.0 - tr.fractionleftsolid : tr.fraction
```

No CONTENTS_MONSTER / player bits: players aren't hit; solid props and brushes are. 0x1016cc20 builds the ray, a CTraceFilterSimple (passentity = ignore, collisionGroup 0) and calls enginetrace->TraceRay (vslot 0x14).

CGameUI::Think 0x102a1530: next think `(int)(curtime / interval_per_tick + 0.5)` ticks (SetNextThink(gpGlobals->curtime)): every tick. Buttons from the player; Pressed / Unpressed fire on change.

## 7. GetAngles and the direction vectors of a VPhysics prop

- PhysFrame -> CPhysicsProp::VPhysicsUpdate -> CBaseEntity::VPhysicsUpdate: `pPhys->GetPosition(&origin, &angles)`; bogus checks (|angle| >= 360000 -> reset; |origin| >= 16384 -> ignored); per pitch, yaw, roll `a = fmod(a, 360)` (x87), `if (a > 180) a -= 360; if (a < -180) a += 360`; SetAbsOrigin / SetAbsAngles.
- GetPosition: the kart's CPhysicsObject has vtable 0x100e2878: GetPosition 0x1001cd30, GetPositionMatrix 0x1001cdb0, both through 0x10074000 (vslot 0xc0 = 0x100201e0 is the other class's, with a cache). 0x10001b90 (IVP rows m[r][c], columns = object axes): `xy = sqrtss(m00*m00 + m20*m20)`; (double)xy > 0.001: `yaw = atan2(m20, m00)*DEG`, `pitch = atan2(m10, xy)*DEG`, `roll = atan2(m12, -m11)*DEG + 180` (x87 fpatan each, stored float); else `yaw = atan2(m02, -m22)*DEG`, `pitch = atan2(m10, xy)*DEG`, `roll = 180`.
- Raw: pitch [-90, 90], yaw [-180, 180], roll [0, 360]; after VPhysicsUpdate all in [-180, 180] (a level kart's roll 0, tilted the other way small negative, not ~359). So the script's `resang.z > 40 && resang.z < 320` triggers only on positive roll above 40; `x > 40 && x < 140` only nose-down pitch above 40.
- GetAngles: the abs angles after CalcAbsolutePosition when dirty.
- GetForwardVector = GetVectors(&v, 0, 0); GetLeftVector = GetVectors(0, &v, 0), the "right" output; GetUpVector = GetVectors(0, 0, &v). GetVectors on m_rgflCoordinateFrame: forward = column 0, "left" = -column 1 (the right vector, each sign bit flipped), up = column 2.

## 8. Interfaces and the server's setup

Slot order = the Source SDK's interfaces, which CS:GO's match bar one object slot. (cs2web's oracle, rubikon/tests/KartOracle, loads csgo legacy's bin/tier0, vstdlib, vphysics and drives IVP through these as the server does; two runs are byte-identical.)

| Interface | Where | Slots used |
|---|---|---|
| "VPhysics031" | InterfaceReg 0x1010aa50, create 0x10003d20 -> singleton 0x1010aa20, vtable 0x100e0938 | 0 Connect, 3 Init, 9 CreateEnvironment (0x10003d50: new 0xec bytes, ctor 0x10013090) |
| "VPhysicsCollision007" | 0x10007ee0 -> 0x1010aa5c, vtable 0x100e0e2c | 29 BBoxToCollide (0x1000ad00), 36 VCollideLoad (0x1000b850) |
| "VPhysicsSurfaceProps001" | 0x10018ab0 -> 0x10116078, vtable 0x100e2114 (ctor 0x10018ae0) | 1 ParseSurfaceData (0x10019180), 3 GetSurfaceIndex |
| IPhysicsEnvironment | vtable 0x100e197c | 3 SetGravity, 7 CreatePolyObject, 8 CreatePolyObjectStatic, 29 / 30 Create / DestroyMotionController (0x10014d90 / 0x10014e00), 33 SetCollisionSolver, 34 Simulate (0x10014320), 37 SetSimulationTimestep, 50 EnableDeleteQueue, 59 SetPerformanceSettings |
| IPhysicsObject | vtable 0x100e26ec (a second, 0x100e2878, differs in slots 0, 2, 46-55, 86-91) | 2 IsAsleep, 15 EnableMotion (0x1001bfe0), 24 Wake, 29 GetMass, 48 GetPosition, 49 GetPositionMatrix, 52 GetVelocity, 56 LocalToWorld, 58 LocalToWorldVector, 59 WorldToLocalVector, 64 CalculateVelocityOffset |
| IPhysicsMotionController | the controller object +4, vtable 0x100e2260 (IVP_Controller part at +0, vtable 0x100e2284) | 2 AttachObject(obj, bool) |
| IMotionEvent (the game's) | CConstantForceController vtable 0x108a5a28, CKeepUpright's 0x108a53c0 | 0 Simulate (thiscall, 5 args) |

PhysicsInit 0x102f5f60, in order: SetPerformanceSettings {10, 250, 2000, 3600, 1.0, 0.5, 10, 2500}; CreateObjectPairHash; SetDebugOverlay; EnableDeleteQueue(1); SetCollisionSolver / SetCollisionEventHandler / SetConstraintEventHandler / EnableConstraintNotify(1) / SetObjectEventHandler (the global CCollisionEvent); SetSimulationTimestep(1/64); SetGravity(0, 0, -sv_gravity). The solver's ordinary answers: ShouldCollide 1, ShouldSolvePenetration 1, ShouldFreezeObject 1, AdditionalCollisionChecksThisTick 0, ShouldFreezeContacts 1. The collision / object event handlers make sounds, damage and touch events (no velocity change: unconfirmed).

Observed on the real DLL (the kart dropped 8 u onto a default floor): it rests with its origin at z 8.45 (lowest hull point -7.96: 0.49 u above the floor, IVP's contact gap); forward thrust 3750 reaches ~650 u/s; t_s 300 turns it ~180 deg/s at speed; it sleeps ~100 ticks after it stops.

## 9. The PSI (one Simulate(1/64) = one PSI)

Simulate -> (0x1001447e) 0x10084c80: lock (env+0x28 slot 0), the time manager's event loop (with time = `psi_time + dt * 1.99999`), unlock (slot 2). The loop (0x100854c2 -> 0x100857e8) runs the queued time events, one of them the PSI 0x10084fb0 (env+0x114 the stage):

1. env+0xda != 0: 0x10087370 (delayed rechecks: a ShouldCollide comes from here); env+0x2c: 0x100868f0; the env+0x94 object's slot 0x28; every PSI listener (last to first); 0x100951f0(env+0x10).
2. 0x10072850: every unit through 0x10072540 with {dt, 1/dt, env} (section 10, 12). The gravity / damping controller, the motion controllers (thrusters, upright) and the friction system (0x10080e4c is on that path) run here.
3. 0x10097d00: each moved core through 0x100970f0 with {dt, 1/dt (1e10 if dt <= 1e-10), env}: the limit hooks (section 12); core+0x13c = |speed|^2, +0x138 = 1/dt; 0x10096940 the rotation; `core+0xe0 += core+0xf0 * (t_env - core+0x130)`, +0x130 = t_env, +0xf0 = speed; q_last = the old q_next, the new one q x dq (the Hamilton product written out mid-0x100970f0), renormalised (section 10); 0x100975f0; each object's hull manager gets its moved radius and next check time and is queued when due.
4. 0x10097db0: every queued hull manager runs its due synapse events until none is due, at most the manager's budget (env+0x24 +0x14, more from env+0x20 slot 4); 0x10093bb0 every 10 s. The collision checks (the OV tree, ShouldCollide, the mindists' creation: 0x100850b6 -> 0x10097f8c -> ... -> 0x1009501e) come from here.
5. 0x100952d0(env+0x10).
6. Every object of env+0x10's list: 0x10095310(obj, 1, 1).

Source files by their "IVP Failed at %s %d" calls: ivp_friction.cxx (0x10083110, 0x100816a0), ivp_mindist_friction.cxx (0x1008d230), ivp_friction_gaps.cxx (0x100a0580), ivp_mindist.cxx (0x10094150), ivp_mindist_minimize.cxx (0x100980e0, 0x100982d0, 0x100984c0, 0x10099a60..0x10099c50), ivp_mindist_recursive.cxx (0x100b14f0), ivp_mindist_event.cxx (0x100a51b0, 0x100a53e0), ivp_compact_ledge_solver.cxx (0x1007ac30), ivp_object.cxx (0x10073680, 0x10073c40, 0x10074750), ivp_physic_private.cxx (0x10086fb0). Impacts and contacts: [ivp-contacts.md](ivp-contacts.md).

## 10. The free body's step

All SSE single unless named.

Timing: a Simulate ends the clock (env+0xf0) at `last_psi + (double)(f32(dt) x 1.9999900f)`; PSI k runs at k/64 (the first Simulate runs PSIs 0 and 1); inside a PSI the clock reads the PSI's time and t_psi the previous PSI's. Between ticks GetPosition interpolates (t - t_psi) = 0.0156248 s past the last PSI (99.999 % of the way).

Per unit, a free core:

1. Revival (0x100778d0, movement state 8): state 1, t_psi and both references' times = t.
2. Stage 2 (0x10072540):
   - 0x100723b0: the rows (+0x60) and +0x90 at t from q_next and `pos + delta (t - t_psi)`; commit 0x10077520; flags &= 0xff3f, bytes 2-3 cleared.
   - The countdown env+0x110 - 1; at 0 `seed *= 0x4b` and reload `15 - (int)(f32(seed & 0xffff) x 2^-16 x -5)`.
   - The unit's controllers from the last entry (append + insertion sort ascending by priority 0x10071e40; removal shifts down 0x10071dc0; the kart's: [drag 500, keep-upright 500, thrusters 500 newest last, gravity 1000]).
   - When the countdown hit 0, the sleep check 0x100722d0: each core's movement state 0x100782a0 into byte 1.
   - Gravity: damping (+0.1 when byte 1 >= 2), commit, `speed += g dt`.
   - Motion: the event's answer, then the clamp.
   - Drag: `f = max(((|b1 vl.y| + |b0 vl.x|) + |b2 vl.z|) coef -0.5 density dt, -1)`, `speed += speed f`; the same on the rot speed without the 0.5.
   - Movement state 0x100782a0: reference 1 (q +0x160, pos +0x180, t +0x150) moved if `|pos - p1|^2 > 1e-4` or `2 r^2 (1 - (q1.q)^2) > 2.5e-5` (r = core+4). Unmoved and `(t - t1) <= env+0x88` (0.3 s): 2; else 3 if `|w|^2 <= (2.3561945 / 0.3)^2` or the last PSI's turn `2 r^2 (1 - (q.q_last)^2) <= 2.5e-5`. Moved: reference 1 = now, then reference 2 (+0x170, +0x190, +0x158; thresholds 0.01 and 0.04): unmoved: 3 if (t - t2) > 4 s else 1; moved: reference 2 = now, 1. All cores 3: the unit sleeps (section 12).
3. Stage 3 (0x100970f0):
   - The limit hooks; |speed| into +0x13c.
   - 0x10096940: sub-steps `n = trunc(sqrt(144 |w|^2 dt^2)) + 1` when `|w|^2 dt^2 > 1/36`; per sub-step h: the half-angle quaternion (`a - a^3 x 0.16666667` per axis, `w = sqrt(1 - ...)`) and the gyroscopic term `w_i += (w_j w_k) (I_j - I_k) / I_i h`. The other path 0x10096d56: section 12.
   - `pos += delta (t - t_psi)`, delta = speed, q_last = q_next, `q_next = q x dq`, Newton-renormalised (`y = 1.5 - n/2`, `y += (1 - y^2 n) / 2` until |error| <= 9.9999997e-7) when `|1 - n| > 9.9999997e-7`.
   - 0x100975f0: the spin axis in world and an arcsine-series spin rate, x the core radius (the hull managers' moved distance): collision bookkeeping.

### Read-back

- 0x1006ca90, the quaternion at t: `f = (t - t_psi) x core+0x138`; a lerp q_last -> q_next (sign-matched) when their dot >= 0.999, with two Newton steps on the length (`y0 = 1.5 - n/2`, `y = (0.5 - y^2 n/2) + y`); else a slerp (`theta = acosf(d)`, `inv = 1 / sqrt(1 - d^2)`, `q = (sinf(theta f) inv sign) q_next + (sinf((1 - f) theta) inv) q_last`, not renormalised).
- acosf 0x100d768b (the statically linked SSE2 libm): branches by |x|: below 2^-16, [2^-16, 0.0625), [0.0625, sqrt(3)/2) with the tables, [sqrt(3)/2, 0.9921875), [0.9921875, 1), +-1.
- sinf 0x100d9542: `k = round(x 32/pi)` in SSE, the remainder in f64 with pi/32 split into two constants scaled by the float's own bits shifted into a double (psllq 29), 64 (sin, cos) rows, degree-2 polynomials; |x| below 2^-126: `x x 0.99999999907`; large-argument path 0x100d9655.
- 0x10074000: the rows from that quaternion (0x100723b0's formulas), the position `pos + delta (t - t_psi)` plus the rows x the object's offset (+0x30; +0x2c a rotation: NULL here).
- GetPositionMatrix maps IVP rows to Source: `[r00, r02, -r01, px K; r20, r22, -r21, pz K; -r10, -r12, r11, -(py K)]`. GetPosition's angles: three x87 fpatan stored as float x 57.29578 (section 7). The transforms (0x1001c3e0 / 0x1001c580 / 0x1001c640) run on GetPositionMatrix's result.
- The game side runs the real x87 `fsincos` / `fpatan`.

server.dll's mathlib (AngleMatrix, MatrixInvert, ConcatTransforms, MatrixAngles, VectorAngles, OnActivate's thruster frame, SetupMatrixOrgAngles, MatrixMultiply, AddTemplate's inline InverseTR, a template's placement): [ivp-physbox.md](ivp-physbox.md) 7 and 8.

## 11. The body's creation from the .phy

env slot 7 0x10013cb0 -> CreatePhysicsObject 0x1001e7a0 (material index < 0 -> 0; a non-finite origin / angle zeroed with a Warning):

1. AngleVectors 0x100b8030 (ecx angles, edx forward, stack right, up): radians `angle x RAD` in SSE, `fld dword; fsincos; fstp cos; fstp sin` for yaw, pitch, roll; forward `(cp cy, cp sy, -sp)`; right `(cr sy - (sr sp) cy, (cr x -1) cy - (sr sp) sy, (sr x -1) cp)`; up `((cr sp) cy + sr sy, (cr sp) sy - sr cy, cr cp)`.
2. 0x1001e97a: the IVP matrix (rows, stride 16): `[f0, -u0, -r0; -f2, u2, r2; f1, -u1, -r1]` (columns forward, -up, left in IVP axes; u2 / r2 xor'd twice).
3. set_quaternion 0x1006d240: `trace = (m00 + m11) + m22 > 0`: `s = sqrtf(trace + 1)`, `w = s 0.5`, `k = 0.5 / s`, `x = (m21 - m12) k`, `y = (m02 - m20) k`, `z = (m10 - m01) k`; else i = argmax diagonal (m11 > m00 -> 1, m22 > m_ii -> 2), j = next[i], k = next[j] (next = 1, 2, 0), `s = sqrtf((m_ii - (m_kk + m_jj)) + 1)`, `q_i = s 0.5`, `h = 0.5 / s` unless s == 0 (then s), `w = (m_kj - m_jk) h`, `q_j = (m_ji + m_ij) h`, `q_k = (m_ki + m_ik) h`. Then `n = ((x^2 + y^2) + z^2) + w^2 > 1e-10`: `q x (1 / sqrtf(n))` (mulps).
4. The position `(x k, -(z k), y k)` (k = 0x10106930 = 0.0254).
5. The template (section 1).
6. new IVP_Polygon 0x100a1030 -> 0x100734d0 -> IVP_Core ctor 0x10077f40 (memset 0x1b0; the unit 0x10077e60: state 8 in byte 1, the gravity controller attached unless static, 0x10071d40); flags bit 1 static, bit 0 template +8 (0); the quaternion normalised as in 3; q_next = q; pos (+0xe0); delta 0; the rows from q (written out at 0x10078082); +0x90 = pos; +4 and +8 = 1000. Object +0x44 = 8 (+8 if static).
7. init_object_core 0x10074750:
   - The mass centre: template +0x54 (override) or slot 1 0x10078c90 (surface +0, IVP m).
   - set_new_m_object_f_core 0x10072d00 of [I | mass centre]: its inverse (0x100760e0: transposed rows, translation `-((r0 t0 + r1 t1) + r2 t2)` per row) is the object's frame on the core: +0x30 the offset; +0x44 |= 0x800 and offset 0 when `((o0^2 + o1^2) + o2^2) < 9e-6`; a +0x2c quaternion only when a diagonal isn't 1 (never here); every hull synapse's point moved by it.
   - Slot 2 0x10078cd0, radius about that centre: `d = sqrtf(((c1 - m1)^2 + (c0 - m0)^2) + (c2 - m2)^2)` (0 here), `radius = upper_limit_radius (+0x18) + d`, `deviation = (f32(byte +0x1c) x 0.004) x upper_limit_radius + d`; core +4 = object +0x90 + radius, +8 = deviation.
   - Mass and inertia (section 1 step 5; slot 3 0x10078cb0 = surface +0xc; without rot_inertia_is_factor the template's values); core +0x1c m, +0x40 speed damping, +0x20.. rot damping.
   - calc_calc 0x10077d40: each I not finite (_finite) or > 1e18 -> 1e18, < -1e18 -> -1e18; 1/I (+0x30), 1/m (+0x3c); flag 0x8 when `((i0^2 + i1^2) + i2^2) x 0.01 > (((i2 - i0)^2 + (i1 - i2)^2) + (i0 - i1)^2)` over the inverses (nearly spherical; the kart: no); +0x44 = 0.5 / radius.
   - 0x10075300 matrix product (out = a b, each entry `((k0 + k1) + k2)`, translation `a.t + (a.rows b.t)`): [rows | pos] x [I | mass centre] -> +0x60 / +0x90, then pos (+0xe0) = +0x90 (the core at the mass centre); q_last = set_quaternion(+0x60 rows) (re-derived, not the start quaternion), q_next = q_last.
   - `dt = f32(env+0xf8 - env+0xf0)` (cvtpd2ps), 1/dt (> 1e-10, else 1e10) into 0x100775f0: +0x138 1/dt, q_next = q_last, speed / delta / +0x13c / +0x5c / +0x1a4 zero, +0x120 (1, 0, 0). The environment's ctor leaves env+0xa8 = f32(1/66), +0xac = 66, +0xf0 = 0, +0xf8 = f64(f32(1/66)) until the first PSI (SetSimulationTimestep doesn't touch +0xf8; after a PSI it is the next PSI's time): a body made before the first Simulate gets 1/dt = 66; one made between ticks reads next - now < 0 and gets 1e10.
8. CPhysicsObject::Init 0x1001b3f0 (env, IVP object, material, volume, drag, angular drag): drag basis reset to the zero vector, then ComputeDragBasis 0x1001bc70 unless static (slot 1) or no collide (slot 74):
   - CollideGetAABB (origin / angles zero) and CollideGetOrthographicAreas (the collide's slot 8: the .phy's dragAxisAreas); `d = maxs - mins` (Source); `X = |k dx|`, `Y = |-(k dz)|`, `Z = |k dy|` (andps).
   - `basis = ((Z Y) a.x, (Z X) a.y, (Y X) a.z) x GetInvMass` (slot 30, x87 return).
   - hx, hy, hz = half of X, Y, Z; `T(w, l, h) = ((((w^2 0.5) w^2) l) + (((w^2 x 0.33333334) l) l^2)) + ((w^2 l) h^2)` (the SDK's AngDragIntegral, products left to right); angular = `((T(hz, hx, hy) iIx) a.y + (T(hy, hx, hz) iIx) a.z, (T(hz, hy, hx) iIy) a.x + (T(hx, hy, hz) iIy) a.z, (T(hy, hz, hx) iIz) a.x + (T(hx, hz, hy) iIz) a.y)` (iI = core +0x30).
   - +0x44 / +0x48 = the drag coefficients (0 when static); +0x3c volume, +0x40 buoyancy ratio `(volume / (k^3 max(volume, 5)) / the material's density)`.
   - The AABB of a single-ledge surface (root at surface +0x20 a leaf: +0 == 0): the ledge's support points over the six directions through the collide transform (rows x 39.37008, Source axes): mins / maxs = the min / max over the ledge's points of `(x K, z K, -(y K))`. A ledge tree takes 0x10032e60 (unread).
9. Slot 16 SetGameData, slot 12 EnableCollisions(1) with enableCollisions, slot 14 EnableDrag(1) when drag != 0 and not static (the drag controller, priority 500), 0x1001fcd0 when the environment's slot 0x120 says so.

Wake (slot 24) -> ensure_in_simulation 0x10075060: an object with +0x44 == 8 has its core appended to the revive queue (env+0xd8: count +0xda, array +0xdc) and flagged 0x4, once; a simulated one gets both references' times (+0x150, +0x158) = env+0xf0. Stage 1 revives the queue (section 12).

## 12. Sleeping, waking, several bodies, the game's calls, the limit hooks

Units: a new core's unit (0x10077e60: state 8, flags & ~0x3f00) goes to the sleeping list's head (core ctor 0x10077f8d); vphysics keeps one unit of its own there.

The walk 0x10072850 holds the next three units before it runs one: with n active units it runs the first n - 3 in list order, then the last three from the last back (n <= 3: all reversed). Each unit's cores go to the moved list in the order 0x10072540 ran them; stage 3 (0x10097d00) walks the moved list from its last entry.

0x10072540, per unit (after section 10's per-core part):

1. `1 - |speed|^2` of each core or'd by its bits: any core faster than 1 m/s sets unit flags 0x400 (clears 0x800); else the 0xc00 bits move up to 0x3000 (`((f << 2) ^ f) & 0x3000 ^ f`) and, if any is set (fast the PSI before), every core's references' times = now (0x10071f70); then 0xc00 off.
2. The countdown, the controllers, the cores into the moved list (a core put to sleep below still takes this PSI's stage 3), the sleep check if the countdown hit 0.
3. Per core last to first, per object 0x10073a50.
4. The 0x300 split / merge (0x10071800, 0x100713b0, 0x10071710, 0x100715c0).

The sleep check 0x100722d0 (unit, env): each core last to first, 0x100782a0's state into byte 1, and'd from 3. All 3: each core 0x10077820:

- 0x10077750: byte 1 = 8; speed +0xd0, rot +0xc0, speed change +0xb0, rot change +0xa0, delta +0xf0 zero.
- 0x100775f0 with {dt, 1/dt}: +0x138 = 1/dt, q_next = q_last (the pose goes back to the PSI before), +0x5c / speed / delta / +0x13c / +0x1a4 zero, +0x120 = (1, 0, 0).
- Each object +0x44 = 8, its hull manager's time sums (`object +0x58 += (t - +0x48) x +0x50` ...), 0x10093bb0, +0x40 unlinked.
- 0x10086d60: per object the listeners through 0x10086630 (a hash, 0x10086390) and the global object listeners (env+0x120), slot 3 = frozen: vphysics' listener sets CPhysicsObject +0x15's sleep state.
- Then the unit is unlinked and pushed at the sleeping list's head, state 8.

IsAsleep 0x1001b680: `(obj+0x15 & 3) != 0 && !(core flags & 4)` (objects start asleep: set at creation).

Stage 1's revive 0x10087370 (env+0xda != 0), the queue from its last entry:

1. A static core (flag 2) skipped; a core in state 8 revives its unit 0x10071ef0 (each core with byte 1 >= 8 through 0x10086b70; the loop restarts when it returns 1 (contacts); a unit in state 8 is unlinked from the sleeping list and pushed at the active list's head, state 1); any other core gets its unit's references' times = now (0x10071f70); flag 0x4 off; the queue emptied.
2. 0x10086b70: every object +0x44 = 1; the speeds +0xd0 and +0xc0 saved only when t_psi == 0.0 (ucomisd with 0x100f3b68; `lahf; test ah, 0x44; jp`: a core never simulated keeps a velocity set before its first PSI); 0x100778d0 (byte 1 = 1, t_psi = now (first f32(now - dt), then overwritten), both references' times = now, each object's hull re-registered 0x10094de0); `1/dt = f32(env+0xf8 - env+0xf0)` (> 1e-10, else 1e10) into 0x100775f0; the saved speeds back; 0x10082ce0 (the object's friction synapses +0x20: a free body has none, returns 0); the revived events (slot 2) to the object's and the global listeners.
3. Inside a PSI env+0xf8 is that PSI's `t + f64(dt)` (0x10085720, the PSI's time event: env+0x100 = env+0xf0, `env+0xf8 = env+0x100 + f64(env+0xa8)`), so the revive's 1/dt is 64 (stage 3 writes the environment's anyway).

### The game's calls (CPhysicsObject vtable 0x100e2878)

- Wake (24): section 11. The kart's Tick() calls it every 0.05 s, so a driven kart never sleeps while its script ticks.
- Sleep (25, 0x1001b670 -> 0x10073370): static: nothing; queued (flag 4): 0x100872f0 takes it out (shifts down, flag 4 off); byte 1 < 8: per object 0x10073ba0, reference 1 = (q_next, pos +0xe0) with time `f64(f32(now - 20.0))`, the unit's split / merge, flags & ~0x300, then the sleep check at now: it sleeps only if the movement checks say rest (a spinning body refuses: reference 1 moved back to now).
- EnableMotion (15, 0x1001bfe0): not static, not unchanged (slot 9): 0x10072af0 (pinned = !on: flag 0x10; speed and rot speed zero; pinned: the object's +0x8c / +0x44 0x100 collision part, 0x10073ba0, 1/I and 1/m zero, both pending changes zero, 0x10072c90; unpinned: `1/I_i = 1.0 / I_i` (+0x34 first, then +0x30, +0x38), 1/m, 0x10094de0); on and hinged (slot 5): slot 78; then slots 26 / 27 (RecheckCollisionFilter, RecheckContactPoints). No Wake.
- EnableGravity (13, 0x1001ba50): the environment's gravity controller (env+0, with the damping) added to the core (+0x140) and unit lists (0x10071d40: append, sort 0x10071e40) or removed (0x10018430, 0x10071dc0). Without it a body has no damping either.
- SetVelocity (50, 0x1001d910): IsMoveable (10, 0x1001ba20: !static && motion enabled) or nothing; Wake; a velocity: speed change = `(v.x k, -(v.z k), k v.y)`, speed zero; an angular one: rot change = `(w.x 0.017453292, -(w.z x it), w.y x it)`, rot zero; the clamp 0x10078650 when the object has no shadow (+0x10).
- ApplyForceCenter (60, 0x1001c700): IsMoveable; `i = ((f.x k) m^-1, (-(f.z k)) m^-1, (f.y k) m^-1)` (core +0x3c), ensure_in_simulation, speed change += i, the clamp.
- SetPosition (46, 0x1001d4e0; slot 69 0x1001db50 first): the IVP position `(o.x k, -(o.z k), o.y k)`, AngleVectors and CreatePhysicsObject's matrix, set_quaternion; with collisions on (+0x44 & 0x100) and isTeleport: EnableCollisions(0), 0x10074b20(q, p, 0), EnableCollisions(1); else 0x10074b20(q, p, 1).
  - 0x10074b20 (beam_object_to_new_position): unless +0x44 & 0x800 the core at p + rows(q) x -offset, each component `(r_i2 (-o2) + (r_i1 (-o1) + r_i0 (-o0))) + p_i` (0x100723b0's rows); a +0x2c rotation would multiply q by its conjugate (none on a prop).
  - Then 0x10097750: env+0x108 += 1; `d = f32(now - t_psi)`; d >= env dt: +0x138 = 1 / d, else the environment's 1/dt; q_next = q_last = q (the relative turn goes to the hull: 0x100975f0); t_psi = env+0x100 (the last PSI's time; 0 before the first); pos = the core position, delta and speed zero, +0x90 = pos, the rows from q; +0x13c (optimize ? 1/dt x |moved| : 0) then 0, +0x5c / +0x1a4 zero; each object's hull manager re-timed (synapse events fired while due, 0x10093bb0 every 10 s). The rot speed and the pending changes stay; no Wake.
- DestroyObject (env slot 10, 0x10014760): out of the environment's object list (+0x10, swap-remove), callback flag 0x400; with the delete queue (env+0xa2, the server's EnableDeleteQueue(1)) or inside a Simulate (env+0xa1) queued (0x10004150 into +0x24) until CleanupDeleteList (slot 49), else deleted now: the unit leaves its list, the others keep their order.

### The limit hooks (stage 3)

env+0x20 is vphysics' CCollisionSolver's IVP_Anomaly_Manager part, installed by 0x10013250 through the application environment +0x1c (0x10083fea); called thiscall (settings env+0x24, core, the vector):

- Slot 1 0x100836e0 (IVP's) when `|w|^2 > (env+0xac x settings+0x10)^2`: `f = ((env+0xac x settings+0x10) x 0.9) / sqrtf((w0^2 + w1^2) + w2^2)`, w x f.
- Slot 0 0x10012b60 (vphysics') when `|v|^2 > settings+8 ^2`: unless the object has a shadow controller (slot 71), `f = (settings+8 x 0.99) / sqrtf((v0^2 + v1^2) + v2^2)`, v x f.
- SetVelocity and thrusters are held at the limit by the clamp and drag takes the rest, so the speed hook needs a fall at the limit (gravity adds 0.3175 m/s per PSI, drag takes less); the rot hook any spin past the clamp (the clamp scales the rot change only by |speed change|).

### The damping's expf (__libm_sse2_expf 0x100d8112)

Used when `0.5 > |rd dt|^2` / `0.25 > ld dt` fail, per axis on `-(rd_i dt)` and on `-(ld dt)` (xorps sign flip):

1. `bits & 0x7fffffff - 0x31800000 >= 0x12000000` -> 0x100d81dc: |x| <= 2^-28: 1.0; finite |x| >= 256: FLT_MAX^2 or (2^-126)^2 by sign; inf: inf / 0; NaN: x + x.
2. Else `k = cvtss2si(f32(x x 23637.115))`, `r = 23637.115549924776 x f64(x) - f64(k)`, `T1 = [0x100fc708 + 8 (k & 15)]`, `p = (4.230634646972322e-05 x T1) x r`, `s = [0x100fc608 + ((k >> 1) & 0xf8)] x [0x100fc508 + ((k >> 6) & 0xf8)]`, s's high dword += `(k >> 14) << 20` (movd, psllq 52, paddd), result `f32((T1 + p) x s)`.
3. `87.3366 < |x|` and not (positive below 88.7228) takes 0x100d821a: `(p + T1) x s`, the same bits.

### Paths the kart doesn't reach

- 0x10096940's other path 0x10096d56: taken when the core's flag 0x8 is set (nearly spherical inertia) or env+0x114 == 5; per-axis sinf, no gyroscopic term ([ivp-impact.md](ivp-impact.md) 7). The kart's inertia isn't, and stage 3 runs with another stage number.
- sinf's large-argument path 0x100d9655: the slerp's angles are acosf's (<= pi) times f in [0, 1]; a body whose 1/dt is 1e10 (made between ticks) or just teleported has q_last == q_next (the lerp branch).
- The kart's scripts (cs2web's docs/crazykart 02 / 05): Wake every Tick, EnableMotion / DisableMotion, teleports (point_teleport TeleportToCurrentPos, trigger_teleport) -> CBaseEntity::Teleport -> SetPosition(isTeleport) (+ SetVelocity with a velocity).

## 13. Collision detection, contacts, impacts

- The mindists between the kart and the world (ledges, the minimize walk, hull managers, the event solvers, the time events, up to do_impact): [ivp-mindist.md](ivp-mindist.md).
- The contacts (the friction system, its controllers, the normal-pressure and complementarity solves, the impact solver, the materials): [ivp-contacts.md](ivp-contacts.md).
- do_impact 0x1008b020, the impact system, the friction system on the world, sleeping and waking on the ground: [ivp-impact.md](ivp-impact.md).
- Two karts touching (friction systems merging and splitting, units of several cores, vphysics' pair times, the rescue push): [ivp-touch.md](ivp-touch.md).

## 14. The map's world: PhysCreateWorld_Shared (server 0x1031ab20)

The BSP's PHYSCOLLIDE lump (29): per model a dphysmodel_t {modelIndex, dataSize, keydataSize, solidCount}, the solids ([int size][VPHY header, compact surface] each), the key text; ends at modelIndex -1. ze_crazykart_v4's model 0: two solids (1,314,440 and 30,664 bytes), keys `staticsolid { index 0, contents 33570819 }`, `staticsolid { index 1, contents 8 }` (CONTENTS_GRATE), `virtualterrain {}`, `materialtable { default_silent 1, sand 2, default 3, default 4, glass 5, metalgrate 6, metal 7 }`.

0x1031ab20 (EDX the vcollide_t; disassembly and decompile):

1. Solid 0: physenv slot 8 (CreatePolyObjectStatic) with physprops slot 3 ("default"), origin / angles zero, params {massCenterOverride 0, mass 1, inertia 1, damping 0.1, rotdamping 0.1, rotInertiaLimit 0.05, "world", the world entity, volume 0, drag 1, enableCollisions 1}; the object's slot 22 (SetCallbackFlags) with slot 23's | 0x200 (CALLBACK_NEVER_DELETED).
2. physcollision slot 38 VPhysicsKeyParserCreate (the push at 0x1031abe9 is EBX); while not slot 2 (Finished), slot 1's block name by stricmp:
   - "solid" / "staticsolid": a solid_t over g_PhysDefaultObjectParams ("DEFAULT"), parser slot 3 ParseSolid (handler g_SolidSetup), then pName "world", the game data, enableCollisions 1, the "default" surface; index 0 skipped (made above); an index past the solids or a null solid sets the flag below; else CreatePolyObjectStatic as above, callback flags | 0x200, object slot 41 (SetContents) the contents, slot 84 (2) when contents & 1.
   - "fluid": ParseFluid (slot 4), a static object of its solid with "fluid" and its surfaceprop, then physenv slot 11 (CreateFluidController). The map has none.
   - "materialtable": int[128] zeroed, ParseSurfaceTable (slot 6), physprops slot 8 SetWorldMaterialIndexTable(table, 128): the material manager's slot 1 (0x10019d00) maps a triangle's material index below 0x80 through it ([ivp-contacts.md](ivp-contacts.md) 7). ze_crazykart_v4: 1 -> 102, 2 -> 71 ("sand": elasticity 0.01), 5 -> 42, 6 -> 8, 7 -> 2, the rest 0.
   - "virtualterrain": the flag, SkipBlock (slot 9). Anything else: SkipBlock.
3. Collision slot 40 frees the parser; with the flag and slot 48 (SupportsVirtualMesh) 0x1031aa20: for i < 0x8000 the engine's slot 0xa4 / 4 = 41 GetCollideForVirtualTerrain(i); each a static object `vdisp_%04d` with "DEFAULT"'s numbers, callback flags | 0x200, slot 84 (2). The 56 displacements: [ivp-virtualmesh.md](ivp-virtualmesh.md).

## 15. The movers: [ivp-shadow.md](ivp-shadow.md)

func_door / func_movelinear / func_rotating / func_button / func_brush are VPhysics shadows: moving IVP bodies a CShadowController drives to the entity's pose each PSI (ComputeShadowControllerIVP 0x10024130), updated by the server after the frame's simulate with the frame time.

## Unread

- Whether `GetSurfaceIndex("none")` returning -1 is the server-side lookup's doing, and the index assignment making "default" 0 (vphysics registers "default" first in 0x10018ae0 / 0x10019180).
- The "material 1001" keyvalue on a CPhysicsProp (not a surfaceprop index change as far as read).
- Spawnflags 0x2 / 0x400 / 0x2000; what re-enables motion despite spawnflag 0x8 (section 5).
- The fields behind 0x1008e020 / 0x1008e050.
- What core byte 1 means beyond the movement state (the extra 0.1 damping at >= 2).
- env+0x118's reader (0.9^dt).
- CTraceFilterSimple's ShouldHitEntity body (0x108dce68 slot 0).
- The frame order of ServiceEventQueue vs entity thinks vs PhysFrame (the scripts' 0.00 / 0.01 delays: a 0.01 s delay fires next tick, so Deactivate(0) + Activate(0.01) leaves a thruster off one PSI if the queue runs before PhysFrame).
- CalculateForceOffset 0x1001c8a0.
- That the collision / object event handlers change no velocity.
- A ledge tree's AABB (0x10032e60).
- When the server's CleanupDeleteList (CGlobalEntityList::CleanupDeleteList -> PhysOnCleanupDeleteList) runs against PhysFrame for a kart killed by I/O.
- server.dll's CBaseEntity::Teleport for a VPhysics prop (which of SetPosition / SetVelocity, the order, the Wake).
- A parented template member's placement.
