# IVP pile-ups: impacts per PSI, ShouldFreezeObject, ShouldCollide

CS:GO legacy vphysics.dll (md5 d97cf2194594d7545427cdabc7376db4, Ghidra `/csgo_vphysics_legacy.dll`) and server.dll
(md5 8048019154549052cb6dc057b76f6a85, `/csgo_server_legacy.dll`), image base 0x10000000, read from the disassembly
(x86). What CS:GO does when a core takes more than the performance settings' 10 impacts in one PSI, the invalid
mindists' recheck, a revival's contacts, and the server's ShouldCollide with its collision groups (ze_crazykart's
64-kart grid at the green light).

## Functions

| Address | Module | What |
|---|---|---|
| 0x10088f10 | vphysics | impact write-back of one core's new speeds (`this` the impact block) and the freeze test |
| 0x10012b00 | vphysics | anomaly manager slot 3 (vtable 0x100e1c50 +0xc): (settings, core) -> the solver's ShouldFreezeObject, else true |
| 0x10089a50 | vphysics | impact; its frozen branch 0x1008a0aa..0x1008a240, after 1008a2c0 (its 1008a4d0 path) wrote the speeds back |
| 0x1008b590 | vphysics | the impact system's round: the only reader of the freeze bits |
| 0x1008a990 | vphysics | impact response (tests only pinned 0x10) |
| 0x1008b060 | vphysics | do_impact: revives a frozen object's unit first (0x10071ef0 at 0x10071f11), each revived core runs 0x10082ce0 |
| 0x10072540 | vphysics | stage 2, per unit; at 0x100727a8 (after the sleep check, before the 0x300 split) 0x10073a50 per object |
| 0x10072850 | vphysics | stage 2's unit walk |
| 0x10087370 | vphysics | stage 1 |
| 0x10085720 | vphysics | before the PSI: env +0xf8 = t + dt |
| 0x10073a50 | vphysics | (thiscall object) recheck its invalid mindists |
| 0x100980e0 | vphysics | recalc of an invalid mindist |
| 0x100982d0 | vphysics | recalc_mindist (thiscall mindist) |
| 0x10096400 | vphysics | recalc_exact_mindist (stage 5) |
| 0x10094a70 | vphysics | insert_exact_mindist(manager, mindist) |
| 0x10078930 | vphysics | grow the wheel vector |
| 0x100730d0 | vphysics | an impact's replan of an object (runs the rescue push inside its recalc) |
| 0x10071ef0 | vphysics | revival of a unit (restarts its core walk on 0x10082ce0's 1, at 0x10071f11) |
| 0x10086b70 | vphysics | a core's revival: 0x100778d0, then 0x10082ce0 (called at 0x10086c8d) |
| 0x10082ce0 | vphysics | (thiscall core) friction from a revived core's mindists; returns 1 when a contact is new |
| 0x10088450 | vphysics | make the friction contact (thiscall mindist) |
| 0x1006dd90 | vphysics | the temporary-memory counter reaching 0 |
| 0x10094300 | vphysics | create_exact_mindists (callers 0x10094419, 0x100945ec; mindist ctor at 0x1009483c) |
| 0x1006ccb0 | vphysics | make an object's cache (runs 0x1006cd90) |
| 0x1008d230 | vphysics | friction controller (fs2000) geometry |
| 0x1001c050 -> 0x100184c0 | vphysics | CreateFrictionSnapshot (CPhysicsObject slot 80) |
| 0x100185d0 / 0x100185e0 / 0x100186d0 / 0x10018720 / 0x100187f0 / 0x10018860 | vphysics | snapshot (vtable 0x100e1d94) IsValid / GetObject / GetContactPoint / GetSurfaceNormal / GetNormalForce / Next |
| 0x10012980 | vphysics | the IVP collision filter (called from recheck_ov_element 0x10094de0 at 0x1009501e) |
| 0x1001ba20 | vphysics | IsMoveable (object slot 10): `!IsStatic && IsMotionEnabled` |
| 0x1001b700 / 0x1001ba00 | vphysics | IsStatic (core flags & 2) / IsMotionEnabled (!(core flags & 0x10)) |
| 0x1001b850 | vphysics | RecheckCollisionFilter (slot 26) |
| 0x10019bae | vphysics | the shadow material's fallback |
| 0x102f7090 | server | CCollisionEvent::ShouldFreezeObject |
| 0x102f6f80 | server | FindMaxContact(object, minForce, &other, &pos, &force) |
| 0x103a2e90 / 0x103a2330 | server | CTakeDamageInfo (with the other's entity) / its force, position, damage |
| 0x102fb720 | server | PhysCallbackDamage (queued for after the physics frame) |
| 0x10356ad0 / 0x102fb830 | server | is a gib / remove it |
| 0x102fc370 | server | (other, entity, 1, 1.0) for a non-damageable non-gib |
| 0x1014b610 / 0x1014b620 | server | CPhysicsProp slot 0x12c (false) / slot 0x174 (null) |
| 0x102f6b10 | server | CCollisionEvent::ShouldCollide |
| 0x102f6a40 | server | ShouldCollide's player-controller path |
| 0x1016c7a0 / 0x102087d0 | server | move parent / root move parent |
| 0x1014a4e0 | server | GetOwnerEntity |
| 0x10226ff0 | server | CBaseButton::CreateVPhysics: always VPhysicsInitShadow(false, false) |
| 0x10226b10 | server | CBaseButton::Spawn (vtable 0x108577d8 slot 0x64) |
| 0x10234040 | server | SetSolid |
| 0x102341d0 | server | SetSolidFlags (CollisionRulesChanged 0x1020a4a0 when 0xc changes) |
| 0x1020a440 | server | SetCollisionGroup (writes +0x154, then CollisionRulesChanged) |
| 0x1043c2d0 | server | CCSGameRules::ShouldCollide (vtable 0x108f7470 slot 28, RTTI .?AVCCSGameRules@@) |
| 0x102b56f0 | server | CGameRules::ShouldCollide |
| 0x10356f09 | server | in CPhysicsProp::Spawn: the collision group |
| 0x1031ca00 | server | CPhysBox::Spawn (vtable 0x108acf58 slot 25) |
| 0x10222080 / 0x10221f70 / 0x10221ff0 | server | func_wall_toggle Toggle / TurnOff / TurnOn |

## Fields

| Offset | Field |
|---|---|
| impact block +0x100 / +0x104 | the core by side |
| impact block +0x50.. / +0x30.. | side 0's speed / rot speed (+0x60.. / +0x40.. side 1) |
| core +0 (byte) / flags | 2 static, 0x10 pinned, bits 6-7 (0xc0) frozen for the PSI |
| core +2 (short) | impact count |
| core +0x4c | friction info (in a system) |
| core +0x52 / +0x54 | objects count / list |
| core +0x94 -> +0x48 | a car wheel |
| core +0xa0 / +0xb0 | rot change / speed change (pending) |
| core +0xc0 / +0xd0 | rot speed / speed |
| core +0x138 | 1/dt |
| core +0x150 / +0x158 | reference times (f64) |
| unit +4 / +8 | prev / next |
| unit +0xe / +0x10 | cores count / list |
| core's unit +0x14c | passed to 0x10088450 |
| friction system +0x26 | core count |
| object +0x20 | exact synapses (next +8; mindist = synapse + its i16 +0x18) |
| object +0x24 | invalid synapses (next +8) |
| object +0x28 | friction synapses (newest first) |
| object +0x40 | cache (0 = none) |
| object +0x44 | movement (< 8 simulated, 8 frozen, 0x21 at a revival) |
| object +0x94 | its core |
| object +0xa0 | its CPhysicsObject |
| mindist bits | & 0x3000 == 0x1000 phantom; & 0xc000: 0x4000 invalid; EXACT `(bits & 0xffcfffff) \| 0xc0000`; bits 30-31 never written |
| mindist +0x5c | len |
| mindist +0x70 | time stamp (vs env +0x108) |
| mindist +0x74 / +0x78 | invalid-list links |
| mindist synapse 0 +0x18 | links +0x20 / +0x24, its object +0x28 |
| mindist synapse 1 +0x34 | links +0x3c / +0x40, its object +0x44 |
| manager +0x8 / +0x14 | exact list head / invalid list head (env +0x18 -> +0x10 the manager) |
| wheel vector +0xc / +0xe / +0x10 | u16 size / n / elements |
| contact +0x7c / +0x80 / +0x84 | normal |
| contact pressure +0x54 | normal force before x 39.370079 |
| env +0x18 -> +0x10 | mindist manager |
| env +0x20 | anomaly manager |
| env +0x24 +0xc | max impacts per PSI (10) |
| env +0x6c | frozen-branch counter |
| env +0xa0 +0x10 | temporary-memory counter |
| env +0xf0 / +0xf8 | PSI time / t + dt |
| env +0x108 | time code |
| sim units manager +0x18 | the unit list (state < 8); +0x1a8 the frozen units |
| snapshot | +8 IVP object, +0xc first friction synapse (object +0x28), +0x10 its contact, +0x14 = synapse != contact + 8 (1 on synapse 1's side) |
| entity +0xe6 | movetype |
| entity +0x114 | solid flags (func_wall_toggle) |
| entity +0x154 | collision group |
| entity +0x158 | second key for the pair table (unknown) |
| entity +0x24a | m_takedamage |
| entity +0xf4 | CollisionProp: slot 0x2c GetSolid, slot 0x30 solid flags |

## Constants

| Value | What |
|---|---|
| 10 | impacts per PSI (performance settings +0xc) |
| 10.0 (0x1098a114) | FindMaxContact's minForce = GetMass x 10.0, x87 then f32 |
| 39.370079 | pressure to normal force (x87, f32) |
| 1.1920929e-07 | GetSurfaceNormal's length epsilon |
| 0.1 (0x109898b0) | crush damage scale |
| [0x1010d24c] = 0x3ce9fe25 | remove_dist |
| 64 | a stage-1 revival's 1/dt: `1 / (env+0xf8 - env+0xf0)` |
| 50000 kg | a mover's shadow mass |
| 0x10ba2a8c slot 0x3c | per-model pair table (same entity on both sides) |
| 0x10ba2a90 slot 0xc | the pair hash (entities, then objects) |
| 0x10ba26a8 | g_pGameRules (ShouldCollide slot 28 = +0x70) |
| 0x100f1cc8 | friction system's controller vtable (Friction 600 in a unit's controller list) |

## The freeze (0x10088f10)

1. Speed +0xd0 and rot speed +0xc0 from the block.
2. Core +2 past settings +0xc: 0x10012b00(settings, core): with a game solver (+8) its ShouldFreezeObject (slot 2) for
   the core's first object's CPhysicsObject (+0x54's first +0xa0) != 0, else true.
3. The answer (a short) into flags bits 6-7: `flags ^ ((r << 6) ^ flags) & 0xc0`.

Frozen branch (0x1008a0aa..0x1008a240), when either core's flags & 0xc0: env +0x6c += 1; the pushed-cores out
(param_1) rewritten with both cores; per core (0 then 1): bits 6-7 = `(1 - (flags >> 1 & 1)) x 0x40` (0x40 unless
static), `+0xb0 += speed`, `+0xa0 += rot speed`, speed and rot speed zero. Committed at the next PSI's stage 2
(`flags &= 0xff3f`).

Reader: 0x1008b590 skips a queued pair when `(flags >> 5 | flags & 2) & 6` of both cores is non-zero (a frozen core
pairs no more with a static or frozen one this PSI). No other test of 0x40 / 0xc0 in 0x10088000..0x1008ce20.

## ShouldFreezeObject (server 0x102f7090)

1. GetGameData (slot 0x44) none -> 1. Movetype 7 (PUSH) or 0 (NONE) -> 0.
2. A server vehicle (slot 0x174) without CALLBACK_IS_VEHICLE_WHEEL (callback flags, object slot 0x5c, & 0x40) -> 0.
3. Collision group 1..3 and not slot 0x12c: the debris branch, then 1.

Debris branch:
1. FindMaxContact(object, `GetMass (slot 0x74) x 10.0`): its snapshot (slot 0x140) from the head; per contact the
   other object (GetObject(1)) when IsMoveable (slot 0x28), `mass < its GetMass` (comiss) and GetNormalForce
   (`pressure x 39.370079`) > minForce: other, contact point, `GetSurfaceNormal x force`. The threshold isn't raised:
   the last such contact wins.
2. GetSurfaceNormal: `(+0x80 s, +0x7c s, -(+0x84) s)`, s = 1 when this object is synapse 0's else -1, x
   `1 / (sqrt((y y + x x) + z z) + 1.1920929e-07)`.
3. Found, damageable (+0x24a > 1): CTakeDamageInfo (force, position, damage `sqrt((fx fx + fy fy) + fz fz) x 0.1`,
   DMG_CRUSH 1) through PhysCallbackDamage. Not damageable: a gib removed, else 0x102fc370.

The kart (prop_physics_override, spawnflags 0x4 + 0x1000: group 2) takes the debris branch; only a moveable, heavier
partner (a mover's shadow, 50000 kg) crushes it; two karts never.

## ShouldCollide (server 0x102f6b10)

1. Same entity on both sides: neither gameflags (object slot 0x4c) has 0x8000: 0x10ba2a8c slot 0x3c's entry (by model,
   slot 0x18) for the two objects' indices (slot 0x54), or 1 with no entry; either has 0x8000: 0.
2. Both gameflags & 2 (FVPHYSICS_CONSTRAINT_STATIC): 0. Callback flags 0x40 (player controller) either side:
   0x102f6a40. ForceVPhysicsCollide (entity slot 0x26c): 1. Both have an edict and one owns the other: 0.
3. Hierarchy (0x102f6c57..0x102f6c84): either has a move parent: both roots; equal -> 0; then the pair table
   (0x10ba2a90 slot 0xc) on the roots and on their +0x158.
4. isStatic per side: movetype NONE (0) or PUSH (7); MOVETYPE_CUSTOM (11) with a shadow controller (object slot 0x11c,
   / 4 = 71); a move parent unless it and its root are both MOVETYPE_VPHYSICS (6). A static side needs its partner
   IsMoveable. Two static: 0. Two shadow controllers: 0. Either SOLID_NONE (CollisionProp slot 0x2c, 0x102f6e3b..): 0.
5. Solid flags (slot 0x30): either FSOLID_NOT_SOLID (4): 1 only when one object IsTrigger (slot 3) and the other isn't
   NOT_SOLID. Else FSOLID_TRIGGER (8) on one side needs the other SOLID_BSP (1) / SOLID_VPHYSICS (6) or
   MOVETYPE_VPHYSICS (0x102f6e98).
6. g_pGameRules ShouldCollide(groups +0x154).
7. Each object's contents (slot 0xa0) & the other entity's PhysicsSolidMaskForEntity (slot 0x2a0).
8. The pair hash on the entities: found 0; on the objects: found 0, else 1.

vphysics' filter 0x10012980: 1 without the solver or without both CPhysicsObjects; 0 when one's callback flags have
0x800 (inside its RecheckCollisionFilter) and the other's 0x400; else the solver's answer.

## The game rules' groups

- 0x1043c2d0: the pair sorted (a <= b); 8 / 0xb and 8 or 5 / 0x11 give 0, 1 / 0x11 gives 1, else 0x102b56f0.
- 0x102b56f0 sorts again; a == 1 or a == 2 gives 0 whatever b is (but 0x11): DEBRIS (1) and DEBRIS_TRIGGER (2) never
  collide with each other or themselves. Its other branches are transcribed from the decompile in cs2web's
  sim/src/ivp/collide_create.rs `game_rules_should_collide`.

## Buttons and walls

- CBaseButton::Spawn: spawnflag 0x4000 -> SetSolid(SOLID_NONE) (0x10234040(0)) and solid flags | 4.
- func_wall_toggle Toggle (+0x114 & 4 picks): TurnOff = EnableCollisions(false) (object slot 12), SetSolidFlags(| 4)
  (CollisionRulesChanged -> each object's RecheckCollisionFilter: callback flags 0x800 around recheck_ov_element when
  it has an OV element, skipped with 0x400), AddEffects(EF_NODRAW 0x20). TurnOn: EnableCollisions(true) while still
  NOT_SOLID (the filter pairs nothing), then the flag cleared and that recheck makes the pairs.

## The invalid mindists' recheck (every PSI)

1. 0x10072540 at 0x100727a8: each core of the unit (+0x10, count +0xe) last to first, each object (+0x54, count +0x52)
   last to first: 0x10073a50.
2. 0x10073a50: over +0x24 (next read before the work), the mindist through 0x100980e0; when `(bits & 0xc000) !=
   0x4000`: off the manager's invalid list (+0x14 head; mindist +0x74 / +0x78), synapse 0 and synapse 1 off their
   objects' invalid lists, then 0x10094a70.
3. 0x100980e0 is 0x100982d0 byte for byte except ebp-0x83c (P_Finish_Counter) = 0 instead of 0x14, and the asserts'
   lines (0xeb / 0xee vs 0x136 / 0x139). It checks the time stamp (+0x70 vs env +0x108) and calls slot 5 on a failure.
4. 0x10094a70: status EXACT; head of the manager's exact list (+8); each synapse at the head of its object's +0x20; when
   either core has a car wheel (core +0x94 -> +0x48) and not a phantom, into the wheel vector. No recalc, no events.

- A stage-5 recalc (0x10096400) that fails runs its rescue push (slot 5) and the mindist goes invalid (slot 7: status 2,
  +0x74 / +0x78 cleared). The rescue push runs inside the recalc that asks for it, in stage 5 and in 0x100730d0.
- Both the manager's invalid list and an object's +0x24 put new entries at their heads.

## Units and revivals

- 0x10072850: the list at sim units manager +0x18 run three behind (edx / edi / ebx / esi rotate; `call 0x10072540` on
  the oldest): the first n - 3 in order, the last three from the last back.
- 0x10071ef0: a state-8 unit unlinked from +0x1a8 (prev's +8 or the head; next's +4), linked at the head of +0x18,
  state 1.
- 0x10082ce0 (from 0x10086b70 after 0x100778d0): each object of the core from the last; each exact synapse (next read
  before the work):
  1. bits & 0x3000: skip.
  2. Other core: synapse 0's object (+0x28) +0x94, or synapse 1's (+0x44) when that is this core.
  3. Other static (byte +0 & 2): skip; both static: the mindist's slot 4 with 1 (deleted).
  4. Other core +0x4c != 0: skip.
  5. 0x100982d0; bits & 0xc000: skip; remove_dist > len (+0x5c) only: env +0xa0 +0x10 += 1, 0x10088450(&fs
     [esp+0x1c], &new [esp+0x14], this core's unit +0x14c, the mindist), +0x10 -= 1 (0 -> 0x1006dd90); new == 1: the
     answer 1 and the other core's +0x150 / +0x158 = env+0xf0.
  6. Returns the answer; 0x10071ef0 restarts its walk over the unit's cores on 1.
- A revival's contact merges units before stage 2's walk; do_impact's revival sets a moving partner's reference times
  to the event's time (the write at 0x10082e06).
- Collision side in stage 1: a revived core's recheck makes the cache of each pair object: its own at +0x44 = 0x21
  (0x10094419), a still-frozen partner's at +0x44 = 8 (0x100945ec). create_exact_mindists gives an object without a
  cache (+0x40 == 0) one (0x1006ccb0), and refreshes it only when simulated (+0x44 < 8) and older than env+0x108. A
  frozen partner's cache uses its frozen core (t_psi from its freeze): cache::update interpolates (quat_at) and
  renormalises, a few ulp from q_last. Stage 2's friction geometry (0x1008d230) reads those caches.
- A unit's revival: the queue's order, each core's recheck then its 0x10082ce0, inside stage 1.
- Mindist ctor 0x1009483c: `and eax, 0xcfc000ff; or eax, 0x0fc00000` over the heap word: bits 30-31 keep allocator
  garbage.
- A unit split can leave a core in the new unit but in no friction system; the system is found through the unit's
  controller list (the first with vtable 0x100f1cc8).

## ze_crazykart_v4

- Each kart's i_kart_button (func_button in the kart template, parented to i_kart_phys, spawnflags 19457) is a shadow;
  kart and button share the kart as root, and 0x4000 makes it SOLID_NONE: they never collide.
- The kart (prop_physics_override, spawnflags 13838): group 2 (CPhysicsProp::Spawn: 1 + (0x1000 ? 1 : 0) for
  spawnflag 4): karts never collide with each other.
- Every item physbox (spawnflag 0x4000): group 1 (CPhysBox::Spawn SetCollisionGroup(1)): only the world and brushes.
- The rest (world, movers, statics): group 0. Nothing is a trigger object, nothing calls DisableCollisions.
- func_brush gets no TurnOff (only RunScriptCode and Kill). finale_elevator1 is brush model 101.

## Unread

- FindMaxContact's 0x10356ad0 / 0x102fb830 / 0x102fc370, and CBreakableProp's OnTakeDamage for DMG_CRUSH; the crush
  isn't checked against a running server.
- Entity +0x158 (the pair table's second key).
- ShouldCollide's FSOLID_TRIGGER part at 0x102f6e98, the IsTrigger branch.
