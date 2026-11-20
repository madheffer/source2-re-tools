# IVP pile-ups: a core past the impacts per PSI, ShouldFreezeObject, ShouldCollide's hierarchy (2026-11-17)

What CS:GO does when a kart takes more than the performance settings' 10 impacts in one PSI, and why ze_crazykart's
64-kart grid trapped the port at the green light. Read from the disassembly (Ghidra `/csgo_vphysics_legacy.dll`,
`/csgo_server_legacy.dll`; tools/re/game/disasm.py, which reads x86 DLLs). Ported in sim/src/ivp/impact.rs (the freeze and
the frozen branch), freeze.rs (the server's debris branch), friction_sys.rs `contact_env`, collide_create.rs
`should_collide`. Checked by scenarios/pile8.txt (make-pile.mjs 8 7 20 6: eight tilted karts dropped onto each other
at the hub: cores reach 12 impacts and freeze from tick 19 on; 300 ticks bit-identical in ivp_check and
kart_world_check, all 424 impacts in ivp_contacts_check). Addresses are vphysics unless marked server.

## 1. The freeze (vphysics)

**0x10088f10** (the impact's write-back of one core's new speeds, `this` the impact block, its core at +0x100 / +0x104
by side): speed +0xd0 and rot speed +0xc0 from the block (+0x50.. / +0x30.. for side 0, +0x60.. / +0x40.. for side 1);
when the core's impact count (+2, short) is past the performance settings' +0xc (env +0x24: 10), the anomaly manager's
slot 3 (env +0x20, vtable 0x100e1c50 +0xc, **0x10012b00**) with (settings, core): with a game solver (+8) its
ShouldFreezeObject (slot 2) for the core's first object's CPhysicsObject (+0x54's first +0xa0) != 0, else true. The
answer (a short) goes into the core's flags bits 6-7: `flags ^ ((r << 6) ^ flags) & 0xc0`.

**The frozen branch** (0x10089a50's end, **0x1008a0aa..0x1008a240**): after 1008a2c0 wrote the speeds back, when either
core's flags & 0xc0: the environment's counter +0x6c += 1, the impact's pushed-cores out (param_1) rewritten with both
cores (whatever 1008a2c0's 1008a4d0 path left there), and per core (0 then 1): flags bits 6-7 = (1 - (flags >> 1 & 1))
x 0x40 (0x40 unless static), speed change +0xb0 += speed, rot change +0xa0 += rot speed, speed and rot speed zero. A
core frozen for the PSI keeps its motion in its pending changes (committed at the next PSI's stage 2, where flags &=
0xff3f clears the bits).

**Who reads the bits**: only the impact system's round (0x1008b590): a queued pair is skipped when (flags >> 5 | flags &
2) & 6 of both cores is non-zero, so a frozen core pairs no more with a static one or another frozen one this PSI. No
other test of 0x40 / 0xc0 in 0x10088000..0x1008ce20 (the response 0x1008a990 tests only pinned 0x10).

## 2. ShouldFreezeObject (server CCollisionEvent, 0x102f7090)

`pObject->GetGameData()` (slot 0x44): none -> 1. The entity's movetype (+0xe6) 7 (PUSH) or 0 (NONE) -> 0. A server
vehicle (slot 0x174) without CALLBACK_IS_VEHICLE_WHEEL (callback flags, object slot 0x5c, & 0x40) -> 0. Collision
group (+0x154) 1..3 and not slot 0x12c (CPhysicsProp: 0x1014b610, false; its slot 0x174 is 0x1014b620, null): the
**debris branch**, then 1:
- **FindMaxContact 0x102f6f80**(object, minForce = GetMass (slot 0x74) x 10.0 (0x1098a114) in x87 then f32, &other,
  &pos, &force): the object's mass; its friction snapshot (slot 0x140; vtable 0x100e1d94: IsValid 0x100185d0,
  GetObject 0x100185e0, GetContactPoint 0x100186d0, GetSurfaceNormal 0x10018720, GetNormalForce 0x100187f0, Next
  0x10018860) from the list head (newest contact first); per contact the other object (GetObject(1): the synapse that
  isn't this one's), when IsMoveable (slot 0x28) and mass < its GetMass (comiss) and GetNormalForce (pressure +0x54 x
  39.370079, x87, f32) > minForce: other, the contact point, GetSurfaceNormal x force. **The threshold isn't raised**:
  the last such contact wins. GetSurfaceNormal: the contact's +0x7c / +0x80 / +0x84 as (s +0x80, +0x7c s, -(+0x84) s), s
  = 1 when this object is synapse 0's else -1, x 1 / (sqrt((y y + x x) + z z) + 1.1920929e-07).
- found: the entity damageable (+0x24a > 1): CTakeDamageInfo (0x103a2e90 with the other's entity; 0x103a2330: the force,
  the position, damage = sqrt((fx fx + fy fy) + fz fz) x 0.1 (0x109898b0), DMG_CRUSH 1) through PhysCallbackDamage
  (0x102fb720, the entity: queued for after the physics frame); not damageable: a gib (0x10356ad0) removed
  (0x102fb830), else 0x102fc370 (the other, the entity, 1, 1.0). TODO(trace): those two and CBreakableProp's own
  OnTakeDamage for DMG_CRUSH.

The kart (prop_physics_override, spawnflags 0x4 + 0x1000: collision group 2, crazykart-physics.md 5) takes the debris
branch; its partner must be moveable and heavier, so only a mover (a shadow, 50000 kg) can crush it. Two karts (the
same mass) never do. The port: freeze answer 0 for a mover / the world, 1 otherwise (contact_env); the crush after the
impact (freeze.rs find_max_contact), handed to the game after the Simulate (kart_abi.rs ze_kart_crush; csgo/maps/ze_crazykart/install.js:
engine.damage with the partner as attacker). The oracle's solver answers 1 for every object (Program.cs), which is the
server's for karts and the world's boxes; it has no damage.

## 3. ShouldCollide's hierarchy and SOLID_NONE (server 0x102f6b10)

The grid trap was not a pile-up of karts: **each kart's own i_kart_button** (a func_button in the kart template,
parented to i_kart_phys, spawnflags 19457) is a shadow (CBaseButton::CreateVPhysics 0x10226ff0 always calls
VPhysicsInitShadow(false, false)), and the port let the kart collide with it. CS:GO doesn't, twice over:
- 0x102f6c57..0x102f6c84: when either entity has a move parent (0x1016c7a0), the root move parents (0x102087d0) of both;
  equal -> 0; then the game's pair table (0x10ba2a90 slot 0xc) on the roots and on their +0x158 (TODO(trace): what +0x158
  is). A kart and its button share the kart as root.
- CBaseButton::Spawn (vtable 0x108577d8 slot 0x64, 0x10226b10): spawnflag 0x4000 -> SetSolid(SOLID_NONE)
  (0x10234040(0)) and solid flags | 4 (FSOLID_NOT_SOLID); ShouldCollide (0x102f6e3b..) needs both GetSolid (+0xf4
  slot 0x2c) non-zero -> 0. Past it, either FSOLID_NOT_SOLID (solid flags slot 0x30 & 4) collides only through an
  object whose slot 3 (IsTrigger) says so (TODO(trace) that branch, 0x102f6e98's FSOLID_TRIGGER part).

The port: Collide::root (the entity's root's id, kart_world.rs `entity`) and Collide::solid; csgo/physics/ivp-body.js rootOf
and brushSolid (a func_button with 0x4000). With them the recorded 64-kart round (server/cs2web/csgo/maps/ze_crazykart/map-test.mjs) runs on IVP to its
end.

## 4. vphysics' friction snapshot (for the record)

CreateFrictionSnapshot (CPhysicsObject slot 80, 0x1001c050 -> 0x100184c0: +8 the IVP object, +0xc its first friction
synapse (object +0x28), +0x10 that synapse's contact, +0x14 = synapse != contact + 8 (1 on synapse 1's side)); Next
(0x10018860) follows the synapse's +0; GetObject(1) 0x100185e0 picks the contact's other synapse (+8 or +0x1c by +0x14)
and its object's CPhysicsObject (+8 -> +0xa0); MarkContactForDelete / DeleteAllMarkedContacts: ivp-collide-off.md 1.

## 5. The invalid mindists' recheck (pile12.txt, ported 2026-11-17)

pile12.txt (make-pile.mjs, twelve karts) parted at tick 60, and the backside retry was not the cause. At tick 59 a
stage-5 recalc (recalc_exact_mindist 0x10096400) of md44 (k10 / k9) fails: its rescue push runs (slot 5) and the mindist
goes invalid (slot 7; the dump's status 2, bits 0e48..., its +0x74 / +0x78 cleared). At tick 60 the DLL has it exact
again on new features (k10 triangle 13 edge 1, k9 triangle 30 edge 2, both status edge), with no time event (idx
ffff). The port never took a mindist off the invalid list. The path, every PSI:
- **0x10072540** (stage 2, per unit; crazykart-physics.md 10) at 0x100727a8, after the sleep check and before the
  0x300 split: each core of the unit (+0x10, count +0xe) last to first, each object of the core (+0x54, count +0x52)
  last to first: **0x10073a50** (thiscall object).
- **0x10073a50**: over the object's invalid synapses (+0x24, next +8; the next one read before the work), the mindist
  (synapse + its i16 +0x18) through **0x100980e0**; when (bits & 0xc000) != 0x4000: off the manager's invalid list
  (env +0x18 -> +0x10 manager, its +0x14 head; mindist +0x74 / +0x78), synapse 0 (+0x18: +0x20 / +0x24, its object
  +0x28's +0x24 head) and synapse 1 (+0x34: +0x3c / +0x40, object +0x44) off their objects' invalid lists, then
  **insert_exact_mindist 0x10094a70**(manager, mindist).
- **0x100980e0** is recalc_mindist 0x100982d0 byte for byte except ebp-0x83c (the solver's P_Finish_Counter) = 0
  instead of 0x14, and its asserts' line numbers (0xeb / 0xee vs 0x136 / 0x139). It still checks the time stamp
  (+0x70 against env +0x108) and still calls slot 5 on a failure.
- **0x10094a70**: status EXACT ((bits & 0xffcfffff) | 0xc0000); the head of the manager's exact list (+8); each synapse
  at the head of its object's exact list (+0x20); when either object's core has a car wheel (core +0x94 -> +0x48) and
  the mindist isn't a phantom (bits & 0x3000 != 0x1000), into the wheel vector (+0xc: u16 size +0xc, n +0xe, the
  elements +0x10; 0x10078930 grows it). No recalc and no events: the mindist's next ones come from stage 5.

The port: World::psi_with's Hook::Invalid (one per core, last to first, at that place), Collide::recheck_invalid
(collide_events.rs: the manager's invalid list filtered by the object, which is the object's +0x24 order since both
lists put new entries at their heads). The rescue push now runs inside the recalc that asks for it in stage 5
(stage56) and in an impact's replan (0x100730d0, impact_sys.rs replan_object; pile12 reaches it at tick 217), as in the
DLL. Stage 4 and stage 1's recalcs still push after their stage and report it (no scenario reaches them). pile12: 300
ticks bit-identical in ivp_check and kart_world_check.

## 6. A mover among several karts: a revival's contacts and collision side in stage 1 (liftpile6.txt, 2026-11-17)

scenarios/liftpile6.txt (make-liftpile.mjs 6): five karts dropped onto finale_elevator1 (brush model 101), which
settle and sleep as one unit; at 120 the lift climbs 3 u a tick for 60 ticks, at 200 drops 3 u a tick for 40. The
oracle makes the lift (Shadow.cs) before the extra karts (MoreKarts.Start), so the bodies are kart 0, lift 1, k1..k5;
ivp_check now revives the mover's collision side before it adds the extra karts.

**The walk 0x10072850** (stage 2): the list at sim units manager +0x18, a unit's +4 prev / +8 next, run three behind
(edx / edi / ebx / esi rotate; `call 0x10072540` on the oldest): the first n - 3 in order, the last three from the
last back (World::walk_order, confirmed). The revival 0x10071ef0: a state-8 unit unlinked from +0x1a8 (prev's +8 or
the head; next's +4) and linked at the head of +0x18, state 1. Oracle probe: `KART_ORACLE_UNITS=1` prints both lists
(names, state byte) at every stage 1 (0x10087370) and stage 2 (0x10072850) entry (MoreKarts.UnitLists).

**Tick 0: 0x10082ce0** (thiscall core, from 0x10086b70 at a revival, after 0x100778d0). Its stage 2 walked six units,
`kart+lift k1..k5`: the kart's revival made a contact with the lift and merged their units before the walk (a split
put the lift back at the head before the second PSI). The function: each object of the core (+0x52 count, +0x54) from
the last; each exact synapse (object +0x20, next +8, read before the work; mindist = synapse + i16 +0x18):
- mindist bits & 0x3000: skipped;
- the other core: synapse 0's object (+0x28) +0x94, or synapse 1's (+0x44) when that is this core;
- other static (byte +0 & 2): skipped, both static: the mindist's slot 4 with 1 (deleted);
- other core +0x4c != 0 (its friction info: in a system): skipped;
- recalc_mindist 0x100982d0 (thiscall mindist); bits & 0xc000: skipped; [0x1010d24c] (remove_dist, 0x3ce9fe25)
  > len (+0x5c) only: env +0xa0's +0x10 += 1, **0x10088450**(&fs [esp+0x1c], &new [esp+0x14], this core's unit +0x14c,
  the mindist; thiscall the mindist), +0x10 -= 1 (0 -> 0x1006dd90); new == 1: the answer 1 and the other core's
  +0x150 / +0x158 (both reference times, f64) = env+0xf0.
- Returns the answer (eax); 0x10071ef0 restarts its walk over the unit's cores on 1 (0x10071f11).

Ported in revive_friction.rs (friction_from_mindist now returns whether the contact is new).

**Tick 120: the revival's collision side in stage 1.** The whole pile (one unit, asleep from 110) is revived by the
lift's Wake: seven cores, k5 first. `KART_ORACLE_CACHE=1` (its `cache` lines now carry their callers, Stacks.Chain)
shows k5's revival making the cache of all seven objects at this PSI's code: k5's own at +0x44 = 0x21 from
create_exact_mindists 0x10094419, every partner's at +0x44 = 8 (still frozen) from 0x100945ec. create_exact_mindists
0x10094300 gives each object of the pair a cache when it has none (+0x40 == 0: 0x1006ccb0, which runs 0x1006cd90),
and refreshes it only when simulated (+0x44 < 8) and older than env+0x108. A frozen partner's cache is made from its
frozen core: t_psi from its freeze, so cache::update interpolates (quat_at) and renormalises, a few ulp from its
q_last. Stage 2's friction controllers (fs2000's geometry, 0x1008d230) read those caches at the same code. The port
ran the revivals' collision side after the PSI (and swapped caches around it), so stage 2 made the caches from the
revived cores instead: every contact normal (+0x7c..+0x84) a few ulp off. Now Collide::stage1_revivals runs in
stage 1's hook: each core's recheck, then its 0x10082ce0, in the queue's order. This also fixed world-pinned's 8 ulp at
tick 400 (500 ticks bit-identical now).

Also on this path: env+0xf8 = t + dt before the PSI (0x10085720) on Collide::simulate's path too, so a stage-1
revival's 1 / dt (core +0x138, 0x10086b70: 1 / (env+0xf8 - env+0xf0)) is 64, not 1e10 (the DLL's fs2000_in shows 64).

A mindist's bits 30-31 are never written: create_exact_mindists' constructor (0x1009483c: `and eax, 0xcfc000ff; or eax,
0x0fc00000` over the heap block's word) keeps them, so the DLL's are allocator garbage (liftpile6's md11 `cfd4...`);
ivp_ground masks them.

**Tick 176: the oracle's friction system is the unit's.** At 176 the DLL splits the pile's unit (k3+k4+k5 a unit of
its own at the head) and its system (k3 and k4 in a new one: +0x26 = 2 cores, 3 contacts, 1 pair; kart, lift, k1, k2
in the old: 4 cores, 8 contacts, 3 pairs). k5 shares the new unit but is in no system. The oracle's per-kart `fs` dump
finds the system through the unit (Contacts.FrictionSystem: the first controller in the unit's list with vtable
0x100f1cc8, the system's 600 controller), so k5 dumps k3 / k4's system. The port had it right; ivp_check now looks
the port's system up through the unit's Friction(600) entry the same way.

Checked: liftpile6 260 ticks bit-identical in ivp_check and kart_world_check (the climb from 120, the split at 176,
the drop 200-240); every other scenario unchanged, world-pinned fixed.

## 7. ShouldCollide's static / moveable and FSOLID_NOT_SOLID branches; the wall toggle (2026-11-18)

The rest of CCollisionEvent::ShouldCollide (server 0x102f6b10), read from the decompile:
- The same entity on both sides: when neither gameflags (object slot 0x4c) has 0x8000, the answer is the entry of
  0x10ba2a8c slot 0x3c (by the entity's model, slot 0x18) for the two objects' indices (slot 0x54), or 1 when there
  is no entry. When either has 0x8000, the answer is 0.
- Both gameflags & 2 (FVPHYSICS_CONSTRAINT_STATIC): 0. Callback flags 0x40 (a player controller) on either side goes
  through 0x102f6a40. ForceVPhysicsCollide (entity slot 0x26c) either way: 1. Both have an edict and one owns the
  other (0x1014a4e0, GetOwnerEntity): 0. Then the hierarchy of 3.
- **isStatic** per side: movetype (+0xe6) NONE (0) or PUSH (7); MOVETYPE_CUSTOM (11) with a shadow controller
  (object slot 0x11c / 4 = 71); a move parent unless both it and its root are MOVETYPE_VPHYSICS (6). A static side
  needs its partner **IsMoveable** (object slot 10, vphysics 0x1001ba20: !IsStatic (core flags & 2, 0x1001b700) &&
  IsMotionEnabled (!(core flags & 0x10), 0x1001ba00)). Two static sides: 0. Two shadow controllers: 0. Either solid
  type (CollisionProp slot 0x2c) SOLID_NONE: 0.
- **Solid flags** (slot 0x30): either FSOLID_NOT_SOLID (4) gives 1 only when one object IsTrigger (slot 3) and the other
  isn't FSOLID_NOT_SOLID. Otherwise FSOLID_TRIGGER (8) on one side needs the other solid BSP (1) / VPHYSICS (6) or
  MOVETYPE_VPHYSICS. Then the game rules' ShouldCollide(groups +0x154) (g_pGameRules 0x10ba26a8 slot 0x70). Then
  each object's contents (slot 0xa0) & the other entity's PhysicsSolidMaskForEntity (slot 0x2a0). Then the pair
  hash (0x10ba2a90 slot 0xc) on the entities: found gives 0. On the objects: found gives 0, else 1.
- The game's numbers on ze_crazykart_v4: nothing is a trigger object and nothing calls DisableCollisions, so the
  contents and pair hashes pass. **The collision groups do not**: section 8 (written here first as "every entity is
  group 0", which missed the spawnflags' groups).
- **vphysics' filter** 0x10012980 (the IVP collision filter, called from recheck_ov_element 0x1009501e): 1 without the
  solver or without both CPhysicsObjects. 0 when one object's callback flags have 0x800 (inside its
  RecheckCollisionFilter) and the other's have 0x400. Else the solver's answer.
- Ported (collide_create.rs should_collide, set_not_solid). The oracle's solver answers the same (Program.cs
  Solver; `KART_ORACLE_SC=1` prints each answer with `TICK` markers).

**func_wall_toggle** (Toggle 0x10222080: solid flags +0x114 & 4 picks): TurnOff 0x10221f70 is EnableCollisions(false)
(object slot 12), then SetSolidFlags(| 4) (0x102341d0, which calls CollisionRulesChanged 0x1020a4a0 when 0xc changes,
and that calls each physics object's RecheckCollisionFilter, slot 26 0x1001b850: callback flags 0x800 set around
recheck_ov_element when the object has an OV element, skipped with 0x400), then AddEffects(EF_NODRAW 0x20).
TurnOn 0x10221ff0 runs EnableCollisions(true) while the wall is still NOT_SOLID, so the filter pairs nothing; then
the flag is cleared and that recheck makes the pairs. The port (csgo/maps/ze_crazykart/install.js ivpStep) runs those calls in that order.
func_brush gets no TurnOff on this map (only RunScriptCode and Kill).

**Checked**: scenarios/lift-pinned.txt (make-lift-pinned.mjs: the lift climbs toward a pinned kart, it is unpinned,
lands, is pinned again and left in the air, the lift comes back under it, unpinned again). kart_world_check gives 380
ticks of what the game reads, bit-identical. Every older scenario is unchanged (66 checks), and so are the oracle's
own outputs for kart-lift, liftpile6 and lift under the new solver.
**Resolved (2026-11-18)**: the "pair past the filter" was a stale oracle. lift-pinned's first output was made before
the oracle was rebuilt with the IsMoveable solver, so the old solver (which said yes) made that pre-PSI lift / kart
mindist. Rebuilt, the oracle has no such pair: its PairsAt probe (`KART_ORACLE_PAIRS=1`) shows the kart's OV element
with no collisions through setup and tick 0.

The fresh output then showed a real port miss at tick 104: the lift's reference times. The oracle's new watchpoint
(`KART_ORACLE_WATCH="lift 150 103 104"`, Watch.cs: debug register 0 on a core field, a vectored handler printing each
write's EIP and stack) caught the write at 0x10082e06. Its chain is 0x10082ce0 <- 0x10086c8d (the core's revival
0x10086b70) <- 0x10071f11 (0x10071ef0) <- 0x1008b060 (**do_impact**). do_impact revives a frozen object's unit
first, and each revived core runs 0x10082ce0. Here that made the sleeping kart's contact with the moving lift and
set the lift's reference times to the event's time. The port's do_impact took the contacts side out before its
revivals and ran no 0x10082ce0. Now it revives first, with 0x10082ce0 (impact_sys.rs), and takes the contacts side
for the impact after. lift-pinned is 380 ticks bit-identical in ivp_check too, and ivp_check pins the kart before
the movers, as the oracle does.

## 8. The game rules' collision groups (2026-11-18)

ShouldCollide's group check calls g_pGameRules (0x10ba26a8) slot 28 with both entities' +0x154 (SetCollisionGroup
0x1020a440 writes it, then CollisionRulesChanged). CCSGameRules (RTTI .?AVCCSGameRules@@, vtable 0x108f7470) slot
28 is **0x1043c2d0**: the pair sorted (a <= b), then 8 / 0xb and 8 or 5 / 0x11 give 0, 1 / 0x11 gives 1, else
**CGameRules 0x102b56f0**. That one sorts again; its branches are in collide_create.rs game_rules_should_collide
(and the oracle's Groups.Rules), transcribed from the decompile. Among them **a == 1 or a == 2 gives 0** whatever b
is (but 0x11): DEBRIS (1) and DEBRIS_TRIGGER (2) never collide with each other or themselves.

On this map:
- **The kart** (prop_physics_override, spawnflags 13838) is group 2: CPhysicsProp::Spawn 0x10356f09 sets 1 + (0x1000 ?
  1 : 0) for spawnflag 4 (crazykart-physics.md). So **karts never collide with each other in CS:GO**: the oracle's
  pile and touch scenarios (group 0) test IVP itself, not the game.
- **Every item physbox** (spawnflag 0x4000) is group 1: CPhysBox::Spawn (vtable 0x108acf58 slot 25, 0x1031ca00)
  SetCollisionGroup(1). It never collides with a kart or another item, only with the world and the brushes (0).
- The rest (the world, movers, statics) are 0.

Ported: Collide::group, KartWorld::entity(root, solid, group) (ABI ze_kart_entity's fourth word, kart_replay's
`entity` third int), csgo/physics/ivp-body.js csgoCollisionGroup. Checked: scenarios/make-groups.mjs. touch-groups.txt has
both karts in group 2, so the first drives through b, never moving it; touch-group-mix.txt (2 and 0) equals
touch.txt. Both are 700 ticks bit-identical in ivp_check, and the oracle's solver applies the same rules.

## 9. Open

- ivp_contacts_check on a scenario with a mover reports the impacts' materials (mu 0x3f23d70b, e 0x3983126f): it
  doesn't know the shadow material (0x10019bae's fallback); the port's own run has it right.
- The crush damage isn't checked against a running server (the oracle has no game); its numbers are the disassembly's.
