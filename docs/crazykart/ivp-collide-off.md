# IVP: collisions off and on, teleports, pinning, DestroyObject

CS:GO legacy vphysics.dll (md5 d97cf2194594d7545427cdabc7376db4, Ghidra `/csgo_vphysics_legacy.dll`) and server.dll
(md5 8048019154549052cb6dc057b76f6a85, `/csgo_server_legacy.dll`), image base 0x10000000, read from the disassembly.
What a kart's teleport (trigger_teleport, point_teleport, a script's SetOrigin: SetPosition with isTeleport), a
func_wall_toggle / func_breakable going away, a parked dead kart and spawnflag 0x8's pin do to IVP.

## Functions

| Address | Module | What |
|---|---|---|
| 0x1001b710 | vphysics | CPhysicsObject::EnableCollisions (vtable 0x100e2878 slot 12) |
| 0x1001f170 | vphysics | IsCollisionEnabled (slot 6): IVP object +0x44 & 0x100 |
| 0x1001c050 | vphysics | CreateFrictionSnapshot (slot 80) -> ctor 0x100184c0 (snapshot vtable 0x100e1d94); DestroyFrictionSnapshot slot 81 |
| 0x10018610 | vphysics | snapshot MarkContactForDelete (slot 10): the contact's other object (synapse +0x10 or +0x24 by side) appended to a CUtlVector unless it is the object itself; repeats kept |
| 0x10018860 | vphysics | snapshot NextFrictionData (slot 12) |
| 0x10018570 | vphysics | DeleteAllMarkedContacts(true) (slot 11) |
| 0x10075060 | vphysics | ensure_in_simulation (Wake) |
| 0x10073be0 | vphysics | (object, other): delete the object's contacts with `other` |
| 0x10073ba0 | vphysics | delete all the object's contacts (list +0x28) |
| 0x100810a0 | vphysics | delete_friction_distance |
| 0x1009a340 -> 0x1009a370 | vphysics | OV element delete (vtable 0x100f2ad0 slot 4) |
| 0x100a6bb0 | vphysics | out of the OV tree node (on node +0x20) |
| 0x1009b400 | vphysics | out of the OV manager (env +0x14) |
| 0x10095180 | vphysics | make the OV element (an existing one deleted first), then recheck_ov_element |
| 0x1009a2e0 | vphysics | IVP_OV_Element ctor (0x30 bytes) |
| 0x10094de0 | vphysics | recheck_ov_element (the pair filter 0x10094fd4..0x10095030) |
| 0x100964f0 | vphysics | OO watcher lookup for a pair |
| 0x1007ec20 | vphysics | contact ctor (synapse insert at 0x1007ec4b..) |
| 0x1001d4e0 | vphysics | SetPosition(origin, angles, isTeleport) (slot 46) |
| 0x100b8030 | vphysics | AngleVectors |
| 0x1006d240 | vphysics | matrix to quaternion |
| 0x10024130 | vphysics | shadow controller teleport (its IVP half at 0x1002435c) |
| 0x10074b20 | vphysics | the object's beam |
| 0x10097750 | vphysics | beam_object_to_new_position(core, q, p, arg) |
| 0x10001950 | vphysics | sqrt |
| 0x100723b0 | vphysics | rows from q |
| 0x100975f0 | vphysics | (core, rotation delta vector): axis, rate |
| 0x1006ccb0 | vphysics | make the cache at the pose |
| 0x10096400 | vphysics | recalc an exact synapse's mindist |
| 0x10073a50 | vphysics | the object's invalid mindists (ivp-pileup.md "The invalid mindists' recheck") |
| 0x100980e0 / 0x10094a70 | vphysics | recheck an invalid mindist / re-insert one |
| 0x10093bb0 | vphysics | the 10 s hull reset |
| 0x1001bfe0 | vphysics | EnableMotion -> 0x10072af0 (core's object, pinned), 0x10072c90 (object, was on) |
| 0x10071ef0 | vphysics | stage 1: revive a unit's cores |
| 0x10086b70 | vphysics | revive one core (object +0x44 = 1, 0x100778d0 with its recheck) |
| 0x100775f0 | vphysics | part of the revival / stop |
| 0x10014760 | vphysics | IPhysicsEnvironment::DestroyObject (slot 10) |
| 0x1001b850 | vphysics | RecheckCollisionFilter |
| 0x10012980 | vphysics | vphysics' collision filter |
| 0x10004150 | vphysics | the delete queue's add |
| 0x100149f0 | vphysics | CleanupDeleteList |
| 0x10014320 | vphysics | Simulate |
| 0x1001fa40 -> 0x1001b560 | vphysics | CPhysicsObject destructor |
| 0x10017a20 | vphysics | env slot 79: the quick-delete flag (env +0xa0) |
| 0x100123c0 | vphysics | friction created event (listener vtable 0x100e1ca0): sets +0x14 & 0x20 |
| 0x1001f93c | vphysics | save restore: sets +0x14 & 0x20 |
| 0x100739f0 | vphysics | delete_and_check_vicinity |
| 0x10071f70 | vphysics | a unit's cores' reference times (+0x150 / +0x158) = env time |
| 0x10073b10 | vphysics | the vicinity check (dynamic / static branch) |
| 0x10082ce0 | vphysics | revive friction on a static core |
| 0x100767c0 | vphysics | the static core's friction walk |
| 0x1008d230 / 0x1008af60 | vphysics | contact geometry / materials (material manager env +0x98: slot 3 elasticity, slot 2 friction into +0x44) |
| 0x10082a60 | vphysics | after the recompute |
| 0x10080e60 | vphysics | delete a contact |
| 0x10073650 -> 0x10073810 | vphysics | IVP_Real_Object destructor (vtable 0x100f2b64 slot 0) |
| 0x10073c40 | vphysics | anchors (+0x80), 0x10073ba0, exact mindists (+0x20, slot 4) |
| 0x10086af0 | vphysics | out of the cluster manager's two hashes and cursor, then env's +0x2c listener |
| 0x10018430 | vphysics | vector remove (the last occurrence, order kept) |
| 0x10077820 -> 0x10077750 | vphysics | stop a core: state 8, speeds zero, 0x100775f0 |
| 0x100781d0 | vphysics | delete a core |
| 0x100872f0 | vphysics | out of the revive queue |
| 0x10071980 | vphysics | core out of its unit |
| 0x10071b30 | vphysics | delete an emptied controller entry |
| 0x10072a80 | vphysics | IVP_Real_Object base destructor |
| 0x1028c550 | server | CBreakable::Die |
| 0x1028c400 | server | drop the entities resting on top |
| 0x102341d0 | server | SetSolidFlags (calls CollisionRulesChanged) |
| 0x1039f430 | server | SUB_Remove |

## Fields

| Offset | Field |
|---|---|
| CPhysicsObject +0x10 | shadow controller |
| CPhysicsObject +0x14 | flags: 0x20 touched dynamic, 0x80 silent delete |
| CPhysicsObject +0x15 | top bits 0x40: keep the surface manager |
| CPhysicsObject +0x1c | 0x400 marked for delete, 0x800 inside its own recheck |
| CPhysicsObject +0x84 | surface manager |
| IVP object +0x1c | an owned object (deleted first; null here) |
| IVP object +0x20 | exact synapses (next +8, the mindist at +0x18's offset) |
| IVP object +0x24 | invalid mindists list |
| IVP object +0x28 | friction-synapse list head (next +0), newest contact first |
| IVP object +0x2c | own rotation (none here); also the OV vector, freed in the dtor |
| IVP object +0x40 | the cache (cache +0x68 its back pointer) |
| IVP object +0x44 | movement byte (& 7 moving, > 7 frozen, 8 not simulated); bits 0x100 collisions on, 0x200 / 0x400 filter bits, 0x800 (beam: no core offset), 0x1000 / 0x2000 env listener lists |
| IVP object +0x48 | hull manager: +0 time, +8 gradient, +0xc centre gradient, +0x10 hvl, +0x14 cvl, +0x18 next |
| IVP object +0x80 | anchors |
| IVP object +0x8c | OV element |
| IVP object +0x94 | core (its flags & 0x12 tested in the pair filter) |
| IVP object +0x98 | a core pointer, compared between a pair (see Unread) |
| IVP object +0x9c / +0x98 | cores (dtor: each handled when they differ) |
| IVP object +0xa0 | back pointer to the CPhysicsObject |
| IVP_OV_Element | vtable 0x100f2ad0, +0x20 -1.0, +0x24 the object, +0x2c a 16-entry vector |
| friction snapshot | +8 the IVP object, +0xc current synapse, +0x10 its contact, +0x14 which side |
| synapse | +0x10 / +0x24 the contact's two objects |
| contact | +0x90 its system (system +0x44 = 1: may split) |
| friction system | +0x3e contact count (short); deleted by slot 7 (+0x1c, with 1) when 0 |
| core +1 | movement byte |
| core flags | 2 static, 0x10 pinned |
| core +0x30..+0x38 / +0x3c | 1/I / 1/m |
| core +0x50 / +0x52 / +0x54 | objects (count +0x52) |
| core +0x5c | rotation rate |
| core +0x60.. | rows |
| core +0x90 | position copy |
| core +0xa0 / +0xb0 | pending changes |
| core +0xc0 / +0xd0 | rot speed / speed |
| core +0xe0 / +0xf0 | position / delta |
| core +0x120 | rotation axis |
| core +0x138 | 1/dt |
| core +0x13c | 1/dt x \|d\| |
| core +0x142 / +0x144 | controllers / listeners (count +0x142) |
| core +0x14c | its unit (delete_and_check_vicinity reads the unit's state byte through it) |
| core +0x150 / +0x158 | reference times |
| core +0x1a4 | +8 x rate |
| env +0x10 / +0x1c | object list / count |
| env +0x14 | OV manager |
| env +0x18 | collision filter (slot 0); also the unit list (state < 8) |
| env +0x1a8 | unit list (state >= 8) |
| env +0x20 slot 4, env +0x24 +0x14 | hull budget |
| env +0x24 | delete queue |
| env +0x2c | listener (cluster manager) |
| env +0x38 | list freed in CleanupDeleteList (collision slot 0x40 each) |
| env +0x88 | sleep list (entry +0x1a its index) |
| env +0x98 | list drained in CleanupDeleteList; also the material manager |
| env +0x9c | count - 1 at the last Simulate's start |
| env +0xa0 | the quick-delete flag (env slot 79, 0x10017a20) |
| env +0xa0 (in 0x100767c0) | its +0x10: the temporary-memory counter, held around the static walk |
| env +0xa1 / +0xa2 | inside Simulate / delete queue on |
| env +0xa8 / +0xac | dt / 1/dt |
| env +0xd8 | revive queue (flag 4) |
| env +0xf0 | time for ensure_in_simulation |
| env +0x100 | last PSI time |
| env +0x108 | time code |
| env +0x11e / +0x120 | object listeners |
| env +0x126 / +0x128 | collision listeners (count / list) |
| env +0x138 | shadow controller owner (slot 0x68 destroys one) |

## EnableCollisions (0x1001b710)

**Off** (param 0):
1. If +0x44 & 0x100: CreateFrictionSnapshot over the list +0x28; per entry MarkContactForDelete, NextFrictionData;
   DeleteAllMarkedContacts(true): per record in order, ensure_in_simulation of it, then 0x10073be0(object, other)
   (from the head, every contact whose synapse objects include `other` removed by 0x100810a0; after each visited
   contact a system with count 0 is deleted by slot 7 and the walk ends). DestroyFrictionSnapshot.
2. If +0x44 & 0x100: the OV element deleted (out of its tree node; every env collision listener, last first, slot 4
   with the object: the delegator root, whose OO watchers and mindists of the object go; out of the OV manager; vector
   freed); +0x44 &= ~0x100, +0x8c = 0; 0x10073ba0: while +0x28 has a head, remove it (0x100810a0), its system deleted
   (slot 7) when emptied.

**On** (param != 0): CPhysicsObject +0x1c |= 0x800 around it; if !(+0x44 & 0x100): 0x10095180, +0x44 |= 0x100.

- recheck_ov_element starts `if (object +0x8c != 0)`: an object with collisions off is skipped by every recheck.
- The contact ctor head-inserts each synapse: synapse.next = object +0x28, old head's prev = it, +0x28 = it.

## SetPosition (0x1001d4e0) and the beam

- The pose as CreatePolyObject makes it (AngleVectors, matrix to quaternion). isTeleport with +0x44 & 0x100:
  `EnableCollisions(false)`, `beam(q, p, 0)`, `EnableCollisions(true)`; else the beam with 1.
- The shadow controller's teleport does the IVP half of the same (the element, the flag, 0x10073ba0, the beam with 1,
  0x10095180).

0x10074b20: core position from the object's (unless +0x44 & 0x800: `rows x -offset + p`), the object's rotation
(+0x2c), then 0x10097750(core, q, p, arg):
1. env +0x108 += 1; `f = f32(env time - t_psi)`; 1/dt +0x138 = env +0xac when `f < env +0xa8`, else `1 / f` (the step
   is then f, else dt); t_psi = env time, then env +0x100; q_last = q_next = q.
2. `d = new p - old +0xe0`, `|d| = sqrt((dx dx + dy dy) + dz dz)` (0x10001950); +0xe0 = p, +0xf0 and +0xd0 zero,
   +0x90 = p, rows +0x60.. from q (0x100723b0).
3. arg 0: +0x13c = 0, rotation delta zero; arg 1: `+0x13c = 1/dt x |d|`, delta `q x conj(old q)`. Then
   0x100975f0(core, delta vector): axis +0x120, rate +0x5c, `+0x1a4 = +8 x rate` (zero delta: (1, 0, 0), 0).
4. Per object of the core (+0x54, count +0x52; last first), its hull manager: `next += (+8 x +0x1a4) x step + |d|`;
   gradient and centre gradient 0; hvl = next; `cvl += |d|` (time kept). A frozen object (+0x44 > 7): its cache let
   go (cache +0x68 = 0, +0x40 = 0; remade at the new pose, 0x1006ccb0), each exact synapse recalculated
   (0x10096400), then 0x10073a50 (each invalid mindist 0x100980e0; one no longer invalid unlinked from the manager's
   invalid list and the object lists and re-inserted 0x10094a70). arg 0: recheck_ov_element. Then while `min - hvl < 0`
   (budget env +0x24 +0x14, then env +0x20 slot 4) the first listener's slot 1 with that value; the 10 s reset
   0x10093bb0 (next reset `(int)(last + 10)`).
5. Core +0x13c, +0x5c, +0x1a4 zero.

## EnableMotion's collision part (0x10072af0, 0x10072c90)

- Not for a static core (flag 2). Flag 0x10 = pinned; +0xc0 and +0xd0 zero.
- Pinned: with +0x44 & 0x100 the IVP side off (EnableCollisions' step 2: no snapshot, no Wake); 1/I +0x30..+0x38,
  1/m +0x3c, pending +0xa0 / +0xb0 zero; then 0x10072c90(object, was on): was on and !(+0x44 & 0x100): 0x10095180
  and the flag (paired again as a pinned object).
- Unpinned: 1/I and 1/m back (+0x34 first, then +0x30, +0x38; +0x3c), recheck_ov_element.

## The pair filter (0x10094de0, 0x10094fd4..0x10095030)

Per element the OV collector found (other object o2), a pair is made when all hold:
1. either object moving (+0x44 & 7);
2. own +0x98 != o2's +0x98;
3. not both cores static or pinned: own core flags & 0x12 == 0 or o2's & 0x12 == 0 (a pinned kart never pairs with the
   world or another pinned body);
4. +0x44 bits 0x200 / 0x400: own 0x200 needs o2 without 0x200; (own 0x400 without 0x200 and o2 0x200) or (own 0x200 and
   o2 0x400) skips the collision filter, else env +0x18 slot 0 (vphysics' -> the game's ShouldCollide, ivp-shadow.md "What collides with a mover")
   must say yes (see ivp-pileup.md "ShouldCollide": a lift / pinned-kart pair made past a filter that said 0);
5. no OO watcher for the pair yet (0x100964f0).

## Revivals in one PSI (0x10071ef0)

A unit's cores revive in turn inside stage 1 (0x10086b70 each), so the second core's recheck sees the first revived and
at rest and a third still frozen (its old t_psi: its cache interpolates).

## DestroyObject (0x10014760)

1. Find the object in env +0x10 from the end; fast-remove (the last entry into its slot: the order changes). Miss:
   DevMsg "error deleting physics object" and the object's slot 0x5c.
2. CPhysicsObject +0x1c |= 0x400. RecheckCollisionFilter skips it; vphysics' filter refuses it against a partner inside
   its own recheck (0x800).
3. An index past env +0x9c (made since the last Simulate's start): +0x14 |= 0x80 (silent delete).
4. Outside a Simulate (+0xa1 == 0) with the queue off (+0xa2 == 0): out of the sleep list, deleted at once (slot 0,
   with 1). Else queued (env +0x24, 0x10004150). The server runs EnableDeleteQueue(1): every game delete is queued.

CleanupDeleteList (0x100149f0) is the first thing Simulate (0x10014320) does, and runs again after the PSIs when the
queue is off: in queue order each object leaves the sleep list (fast-remove, the moved entry's +0x1a renumbered) and is
deleted; then env +0x98 drained and +0x38 freed (collision slot 0x40 each). Simulate then sets env +0x9c = count - 1.

## CPhysicsObject destructor (0x1001fa40 -> 0x1001b560)

1. A shadow controller (+0x10) destroyed first (env +0x138 slot 0x68).
2. Callback flags 0, game data 0, the IVP object's +0xa0 = 0.
3. A static core's listeners (core +0x142 / +0x144) each called.
4. The IVP object: delete_and_check_vicinity (0x100739f0) when the delete isn't silent (+0x14 < 0x80), env slot 79 is
   0 and +0x14 & 0x20; else a plain delete. 0x20 (touched dynamic) is set by 0x100123c0 on each side whose partner
   IsMoveable, unless both are static (0x1001f93c from a restore).
5. The surface manager (+0x84), unless +0x15's top bits are 0x40.

## delete_and_check_vicinity (0x100739f0)

- Dynamic core: unit state byte (core +0x14c) > 7: revive the unit (0x10071ef0); else 0x10071f70. Then 0x10073b10 (for
  a dynamic core: the same again, revive at movement 8 else 0x10071f70). A static core goes straight to 0x10073b10's
  static branch. Then the delete.

0x10073b10's static branch:
1. Core +1 and object +0x44 saved, set to 0x21; recheck_ov_element (pairs made as if moving); both restored.
2. 0x10082ce0 on the static core: a static partner skipped, a partner in a friction system skipped.
3. 0x100767c0: each object of the core last to first, each friction synapse (+0x28) from the head: the contact's
   system +0x44 = 1. Dynamic partner core: each of its objects (last to first) through ensure_in_simulation (+0x44 ==
   8: its core (+0x98) queued once for revival, env +0xd8 flag 4; else its core's +0x150 / +0x158 = env +0xf0: wakes
   karts resting on a deleted platform); then contact geometry 0x1008d230 and materials 0x1008af60 again, 0x10082a60.
   Static partner: contact deleted (0x10080e60, then freed). The env's temporary-memory counter (+0xa0 +0x10) held
   around the walk.

## IVP_Real_Object destructor (0x10073650 -> 0x10073810)

1. +0x1c's object deleted.
2. Each hull listener (manager +0x48) told the manager goes (slot 8): the OV element and the OO watchers, their
   mindists with them.
3. 0x10073c40: anchors (+0x80), 0x10073ba0, exact mindists (+0x20, slot 4).
4. Env object listeners (+0x11e / +0x120): vphysics', no physics.
5. With +0x44 & 0x2000 / 0x1000: out of the env's listener lists. 0x10086af0.
6. The cache's back pointer cleared.
7. Out of its core's list (core +0x50, 0x10018430). A core left empty and still simulated stops (0x10077820 ->
   0x10077750) and is deleted (0x100781d0); likewise the +0x9c and +0x98 cores when they differ.
8. OV vector (+0x2c) freed, base destructor 0x10072a80.

Core deletion 0x100781d0: out of the revive queue (0x100872f0); each controller (+0x144, count +0x142) slot 0
(core_is_going_to_be_deleted); 0x10071980: out of the unit's cores (order kept); per controller of its list, last to
first, out of that controller's entry (order kept), an emptied entry deleted (0x10071b30). The unit isn't split; a unit
with no cores is unlinked (env +0x18 when state < 8, else +0x1a8) and freed.

## CBreakable::Die (server 0x1028c550)

After the gibs and the break sound:
1. 0x1028c400: entities resting on top (UTIL_EntitiesInBox above the brush, then their ground entity: players and NPCs,
   not physics objects).
2. SetSolidFlags(flags | FSOLID_NOT_SOLID) (0x102341d0): CollisionRulesChanged, every physics object of the brush runs
   RecheckCollisionFilter, ShouldCollide now 0.
3. Slot 0x270, then SetThink(SUB_Remove 0x1039f430) at curtime + 0.1, rounded `(int)((t + 0.1) / interval + 0.5)`: 6
   ticks later, before that tick's PhysFrame; its UTIL_Remove destroys the object.
4. No EnableCollisions.

- A func_wall_toggle's Kill: plain UTIL_Remove, DestroyObject at once (on or off). Its Toggle: TurnOff / TurnOn
  (ivp-pileup.md "ShouldCollide", "Buttons and walls").
- A teleport: SetPosition with isTeleport.

## ze_crazykart_v4

Destroys on its I/O: func_breakable Break (15 outputs); Kill on func_button (13), func_physbox (8), func_door (6),
func_rotating (4), func_wall_toggle (3), func_movelinear (2), func_brush and the kart's prop_physics_override (1 each).

## Unread

- 0x10096400 / 0x10073a50's recheck (0x100980e0 / 0x10094a70) on a frozen object with collisions on (SetPosition
  without isTeleport); the hull budget's env +0x20 slot 4.
- What IVP object +0x98 is exactly: a core pointer (the destructor deletes the +0x9c / +0x98 cores, ensure_in_simulation queues +0x98; the pair filter compares +0x98 at 0x10094fc9 and tests the +0x94 core's flags & 0x12 at 0x10094fdf, checked against the disassembly). IVP's field order physical_core, friction_core, original_core would make +0x94 / +0x98 / +0x9c those three: unconfirmed.
- Who sets +0x44 bits 0x200 / 0x400.
- The order a unit's cores revive in, 0x100775f0's part for the second core.
- A static's 0x10082ce0 with a partner outside a friction system; a static-static contact.
- CS:GO's UpdateOnRemove order for a parent and its children.
- The server side's path UTIL_Remove -> VPhysicsDestroyObject (addresses).
- The 0x400 mark's effect between the call and the queue's run.
