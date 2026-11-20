# IVP: an object's collisions off and on, teleports, pinning (csgo legacy vphysics.dll, 2026-11-17)

What a kart's teleport (trigger_teleport, point_teleport, the scripts' SetOrigin: SetPosition with isTeleport), a
func_wall_toggle / func_breakable going away, a parked dead kart and spawnflag 0x8's pin do to IVP. Read from the
disassembly (Ghidra `/csgo_vphysics_legacy.dll`); ported in sim/src/ivp/collide_off.rs (`Collide::enable_collisions`,
`teleport`, `beam`, `enable_motion`), the pair filter in collide_create.rs recheck_ov; checked by
scenarios/world-teleport.txt (900 ticks bit-identical: ivp_check, kart_world_check) and world-pinned.txt (what the
game reads bit-identical over 500 ticks; ivp_check's internal state to tick 399, below). Addresses are vphysics.

## 1. CPhysicsObject::EnableCollisions (vtable 0x100e2878 slot 12, 0x1001b710)

**Off** (`param == 0`):
1. If IsCollisionEnabled (slot 6, 0x1001f170: IVP object +0x44 & 0x100): CreateFrictionSnapshot (slot 80, 0x1001c050
   -> ctor 0x100184c0, vtable 0x100e1d94: +8 the IVP object, +0xc the current synapse, +0x10 its contact, +0x14 which
   side) over the object's friction-synapse list (**IVP object +0x28**, next at +0); per entry MarkContactForDelete
   (slot 10, 0x10018610: the contact's *other* object, synapse +0x10 or +0x24 by the side, appended to a CUtlVector
   unless it is the object itself: repeats kept), NextFrictionData (slot 12, 0x10018860), then
   **DeleteAllMarkedContacts(true)** (slot 11, 0x10018570): per record in order, ensure_in_simulation (0x10075060:
   Wake) of it, then **0x10073be0**(object, other): the object's list from its head, every contact whose synapse
   objects (+0x10 / +0x24) include `other` removed by 0x100810a0 (delete_friction_distance); after each visited
   contact, a system whose contact count (+0x3e, short) is 0 is deleted by its slot 7 (+0x1c, with 1) and the walk
   ends. DestroyFrictionSnapshot (slot 81).
2. If +0x44 & 0x100: the OV element (+0x8c) deleted (its vtable 0x100f2ad0 slot 4 0x1009a340 -> 0x1009a370: out of
   its OV tree node, 0x100a6bb0 on node +0x20; every environment collision listener (env +0x128, count +0x126, last
   first) slot 4 with the object: the delegator root, whose OO watchers and mindists of the object go; out of the OV
   manager env +0x14, 0x1009b400; its vector freed), +0x44 &= ~0x100, +0x8c = 0, then **0x10073ba0**: while the
   list +0x28 has a head, that contact removed by 0x100810a0, its system deleted (slot 7) when emptied.

**On** (`param != 0`): CPhysicsObject +0x1c |= 0x800 around it; if !(+0x44 & 0x100): **0x10095180** (an existing
element deleted first; a new IVP_OV_Element (0x30 bytes, ctor 0x1009a2e0: vtable 0x100f2ad0, +0x24 the object,
+0x20 -1.0, a 16-entry vector at +0x2c) into +0x8c, then recheck_ov_element 0x10094de0), +0x44 |= 0x100.

recheck_ov_element 0x10094de0 starts with `if (object +0x8c != 0)`: an object with its collisions off is left alone
by every recheck (a revival's, the hull event's).

**A contact's synapses** are head-inserted into each object's list by the contact's ctor (0x1007ec20, 0x1007ec4b..):
synapse.next = object +0x28, the old head's prev = it, object +0x28 = it. So a list runs newest contact first (the
port sorts by the contacts' creation ids, descending).

## 2. SetPosition (slot 46, 0x1001d4e0) and the beam

SetPosition(origin, angles, isTeleport): the pose made as CreatePolyObject makes it (AngleVectors 0x100b8030, the
matrix to a quaternion 0x1006d240). With isTeleport and the IVP object's collisions on (+0x44 & 0x100):
**EnableCollisions(false), beam_object_to_new_position(q, p, 0), EnableCollisions(true)**; else the beam with 1.
The shadow controller's teleport (0x10024130's 0x1002435c) runs the IVP half of the same thing (the element, the
flag, 0x10073ba0, the beam with 1, 0x10095180).

**0x10074b20** (the object's beam): the core position from the object's (unless +0x44 & 0x800: rows x -offset + p),
the object's own rotation (+0x2c, none here), then **0x10097750**(core, q, p, arg):
- env +0x108 (the time code) += 1; f = f32(env time - t_psi); 1/dt +0x138 = env's (+0xac) when f < env dt (+0xa8),
  else 1 / f (the step is then f, else dt); t_psi = env time, then env +0x100 (the last PSI); q_last and q_next = q.
- the move: d = new p - old +0xe0, |d| = sqrt((dx dx + dy dy) + dz dz) (0x10001950); +0xe0 = p, +0xf0 (delta) and
  +0xd0 (speed) zero, +0x90 = p, the rows +0x60.. from q (the 0x100723b0 formulas).
- arg 0: +0x13c = 0 and the rotation delta zero; arg 1: +0x13c = 1/dt x |d|, the rotation delta q x conj(old q).
  Then **0x100975f0**(core, the delta's vector): the axis +0x120, the rate +0x5c, +0x1a4 = +8 x rate (0 for a zero
  delta: (1, 0, 0), 0).
- per object of the core (+0x54, count +0x52; last first), its hull manager (object +0x48): next (+0x18) += (+8 x
  +0x1a4) x the step + |d|; gradient (+8) and centre gradient (+0xc) 0; hvl (+0x10) = next; cvl (+0x14) += |d| (its
  time +0 kept). An object not moving (+0x44 byte > 7: frozen): **its cache let go** (+0x40: the cache's +0x68 = 0,
  +0x40 = 0; the next use makes one at the new pose, 0x1006ccb0), each of its exact synapses (+0x20 list, next +8, the
  mindist at +0x18's offset) recalculated (0x10096400), then **0x10073a50** (its invalid mindists, +0x24 list:
  0x100980e0 each; one no longer invalid unlinked from the manager's invalid list and the object lists and
  re-inserted 0x10094a70). Arg 0: recheck_ov_element (nothing with collisions off). Then while min - hvl < 0 (the
  settings' budget, env +0x24 +0x14, then env +0x20 slot 4) the first listener's slot 1 with that value; the 10 s reset
  (0x10093bb0, next reset (int)(last + 10)).
- the core's +0x13c, +0x5c, +0x1a4 zero.

Ported: the arg-0 form (a teleport: the object's collisions are off, so no listeners or synapses are there); a beam
with an object's collisions on notes itself untraced (`Collide::beam`). TODO(trace): 0x10096400 / 0x10073a50's (0x10073a50 itself: ivp-pileup.md 5)
recheck 0x100980e0 / 0x10094a70 on a frozen object with collisions on (a SetPosition without isTeleport: nothing of
ours calls it), the hull budget's env +0x20 slot 4.

## 3. EnableMotion's collision part (0x1001bfe0 -> 0x10072af0, 0x10072c90)

0x10072af0(core's object, pinned): not for a static core (flag 2); flag 0x10 = pinned; rot +0xc0 and speed +0xd0
zero. **Pinned**: with +0x44 & 0x100 the IVP side off (as section 1's step 2: the element, the flag, 0x10073ba0: no
snapshot, no Wake), 1/I +0x30..+0x38, 1/m +0x3c, the pending changes +0xa0 / +0xb0 zero, then **0x10072c90(object,
was on)**: was on: if !(+0x44 & 0x100) 0x10095180 and the flag (back on: the object paired again as a pinned one).
**Unpinned**: 1/I and 1/m again (+0x34 first, then +0x30, +0x38; +0x3c), recheck_ov_element 0x10094de0.

## 4. The pair filter of recheck_ov_element (0x10094de0, 0x10094fd4..0x10095030)

Per element the OV collector found (the other object `o2`), a pair is made when all of:
- either object moving (+0x44 & 7, own or o2's);
- own +0x98 != o2's +0x98 (TODO(trace): what +0x98 is; never equal for ours);
- **not both cores static or pinned**: own core flags & 0x12 == 0 or o2's core flags & 0x12 == 0 (2 static, 0x10
  pinned): a pinned kart never pairs with the world or another pinned body;
- +0x44 bits 9 / 10 (0x200 / 0x400): own 0x200 needs o2 without 0x200; (own 0x400 without 0x200 and o2 0x200) or
  (own 0x200 and o2 0x400) skips the collision filter, else the environment's filter (env +0x18 slot 0: vphysics' ->
  the game's ShouldCollide, ivp-shadow.md 8) must say yes (none of ours sets either bit, as far as read: but see
  ivp-pileup.md 7 Open, a lift / pinned-kart pair the DLL makes past a filter that said 0);
- no OO watcher for the pair yet (0x100964f0).

## 5. Revivals of several cores in one PSI (stage 1, 0x10071ef0)

A unit's cores revive in turn inside stage 1 (0x10086b70 each: the object +0x44 = 1, 0x100778d0 with its recheck), so
the second core's recheck sees the first revived and at rest and a third still frozen (its old t_psi: its cache
interpolates). The port runs the revivals' collision side after the PSI (psi_collisions) and now shows each revived
object as that moment had it (`Collide::stage1`: the core before stage 1 until its own turn, the revived core after;
movement 8 / 1; the caches as stage 1 found them). World::psi_with calls its hook with `Hook::Stage1` right after
stage 1 for the revived cores' state.

**Open**: world-pinned.txt tick 400 (the kart and pinned b, one unit, woken together after both slept): the new
kart-b mindist's plane y is 8 ulp off (0x39daff22 vs 0x39daff2a); everything else, and every pose the game reads,
bit-identical. Something of one of the two cores' stage-1 state the recalc reads still differs (suspects: 0x100775f0's
part of the revival for the second core, the order the unit's cores revive in).

## 6. What the game layer does with it (kart_world.rs, csgo/physics/ivp-world.js)

- a kart's teleport: `KartWorld::teleport` (SetPosition with isTeleport);
- func_wall_toggle Toggle: TurnOff / TurnOn in CS:GO's order (ivp-pileup.md 7);
- a killed kart, mover or func_wall_toggle: DestroyObject at the kill (csgo/maps/ze_crazykart/install.js `killed`, section 7);
- a broken func_breakable: CS:GO's CBreakable::Die (section 7a), FSOLID_NOT_SOLID at once, the DestroyObject 6 ticks
  later.

## 7. DestroyObject (IPhysicsEnvironment slot 10, 0x10014760; read and ported 2026-11-18: sim/src/ivp/destroy.rs)

**DestroyObject** 0x10014760:
- It finds the object in the environment's list (env +0x10, count +0x1c), searching from the end, and fast-removes
  it: the last entry moves into its slot, so **the list's order changes**. A miss gives DevMsg "error deleting
  physics object" and the object's slot 0x5c.
- CPhysicsObject +0x1c |= 0x400 (marked for delete). RecheckCollisionFilter 0x1001b850 skips an object with this
  bit, and vphysics' filter 0x10012980 refuses it against a partner inside its own recheck (0x800).
- An index past env +0x9c (the objects made since the last Simulate's start) sets +0x14 |= 0x80: a silent delete.
- Outside a Simulate (+0xa1 == 0) with the delete queue off (+0xa2 == 0), the object leaves the sleep list (env
  +0x88) and is deleted at once (its slot 0, with 1). Otherwise it goes on the queue (env +0x24 via 0x10004150). The
  server runs EnableDeleteQueue(1), so in the game every delete is queued.

**CleanupDeleteList** 0x100149f0 is **the first thing Simulate 0x10014320 does**. It runs again after the PSIs when
the queue is off. In the queue's order, each object leaves the sleep list (+0x88: a fast-remove that renumbers the
moved entry's +0x1a) and is deleted. Then the env's +0x98 list is drained and the +0x38 list freed (collision slot
0x40 each). Simulate then sets env +0x9c = count - 1.

**CPhysicsObject's destructor** (0x1001fa40 -> 0x1001b560):
- A shadow controller (+0x10) is destroyed first (env +0x138's slot 0x68).
- Callback flags = 0, the game data = 0, and the IVP object's back pointer (+0xa0) = 0.
- A static core's listeners (core +0x142 / +0x144) are each called.
- Then the IVP object goes. It takes **delete_and_check_vicinity** 0x100739f0 when all three hold: the delete isn't
  silent (+0x14 < 0x80), env slot 79 (0x10017a20, env +0xa0: the environment's quick-delete flag) is 0, and
  **+0x14 & 0x20** is set. Otherwise it takes a plain delete.
- Bit 0x20 ("touched dynamic") is set by vphysics' friction created event 0x100123c0 (the listener vtable
  0x100e1ca0). Unless both objects are static, each side gets it when its partner IsMoveable. (0x1001f93c sets it from
  a save's restore too.)
- Last, the surface manager (+0x84) goes, unless +0x15's top bits are 0x40.

**delete_and_check_vicinity** 0x100739f0, for a dynamic core:
- When the unit's state byte (core +0x14c) is past 7, the unit is revived (0x10071ef0, at the core's environment).
  Otherwise its cores' reference times (+0x150 / +0x158) become the environment's time (0x10071f70).
- Then 0x10073b10 runs: for a dynamic core it does the same again (revive at movement 8, else 0x10071f70). For a
  static core (0x100739f0 goes straight there) it runs the static branch below.
- Then the delete itself.

**0x10073b10's static branch** (read and ported 2026-11-18):
1. The core's movement byte (core +1) and the object's (+0x44) are saved and set to 0x21. recheck_ov_element runs
   (pairs are made as if the object moved), then both bytes are put back.
2. 0x10082ce0 runs on the static core, with revive_friction.rs's rules: a static partner is skipped, and a partner in
   a friction system is skipped. A partner that would get a contact here (no unit) isn't ported; it is noted and
   fails the checks.
3. **0x100767c0** (the static core) walks each object of the core last to first, and each friction synapse (object
   +0x28) from the head:
   - The contact's system (+0x90) gets +0x44 = 1 (it may split).
   - With a dynamic partner core:
     - Each of the partner's objects (last to first) goes through **ensure_in_simulation 0x10075060**: an object
       not simulated (+0x44 == 8) has its core (+0x98) queued once for revival (env +0xd8, flag 4); else its core's
       reference times (+0x150 / +0x158) become env +0xf0. This is World::wake, and it is what wakes karts resting
       on a deleted platform.
     - Then the contact's geometry (0x1008d230) and materials (0x1008af60, the material manager env +0x98: slot 3
       the elasticity, slot 2 the friction into +0x44) are computed again, and 0x10082a60 runs.
   - With a static partner, the contact is deleted (0x10080e60, then freed). Not reached here: noted.
   - The env's temporary-memory counter (+0xa0's +0x10) is held around the walk.

## 7a. CBreakable::Die (server 0x1028c550, read 2026-11-18)

After the gibs and the break sound:
- 0x1028c400 drops the entities resting on top (UTIL_EntitiesInBox above the brush, then their ground entity:
  players and NPCs, not physics objects).
- **SetSolidFlags(flags | FSOLID_NOT_SOLID)** (0x102341d0) calls CollisionRulesChanged, so every physics object of
  the brush runs RecheckCollisionFilter, and the server's ShouldCollide now answers 0.
- Then the slot 0x270 call, and **SetThink(SUB_Remove 0x1039f430)** at curtime + 0.1. The server rounds that to
  `(int)((t + 0.1) / interval + 0.5)`, so the think runs 6 ticks later, before that tick's PhysFrame, and its
  UTIL_Remove destroys the object.
- No EnableCollisions is called. The engine here (CS2's rules) removes the entity at the Break itself, so the kart
  port (csgo/maps/ze_crazykart/install.js `killed`, BREAK_REMOVE_TICKS) sends NOT_SOLID then and the DestroyObject 6 PhysFrames later.

A func_wall_toggle's Kill is a plain UTIL_Remove: DestroyObject at once, whether it was on (still solid, still
touching) or off.

**IVP_Real_Object's destructor** (vtable 0x100f2b64 slot 0 0x10073650 -> 0x10073810):
1. +0x1c's object is deleted (null for ours).
2. Each hull listener (the hull manager at +0x48) is told the manager goes (slot 8): the OV element and the OO
   watchers, whose mindists go with them.
3. 0x10073c40: the anchors (+0x80, none here), 0x10073ba0 (the contacts), the exact mindists (+0x20, slot 4).
4. The env's object listeners (+0x11e / +0x120) are called; vphysics', no physics.
5. With +0x44 & 0x2000 / 0x1000, the object leaves the env's listener lists. 0x10086af0 takes it out of the cluster
   manager's two hashes and its cursor, then calls the env's +0x2c listener.
6. The cache's back pointer is cleared.
7. The object leaves its core's list (core +0x50, 0x10018430: the last occurrence, the rest kept in order). A core
   left empty and still simulated stops (0x10077820 -> 0x10077750: state 8, speeds zero, 0x100775f0) and is deleted
   (0x100781d0). The same happens for the +0x9c and +0x98 cores when they differ.
8. The OV vector (+0x2c) is freed, then the base destructor (0x10072a80).

**The core's deletion** 0x100781d0:
- Out of the revive queue (0x100872f0).
- Each controller in the core's list (+0x144, count +0x142) gets slot 0 (core_is_going_to_be_deleted).
- **0x10071980** takes it out of its unit:
  - Out of the unit's cores (0x10018430, order kept).
  - Per controller of its list, last to first, the core leaves that controller's entry (order kept). An emptied entry
    is deleted (0x10071b30).
  - **The unit isn't split.** A unit left with no cores is unlinked from its list: env +0x18 when its state byte is
    below 8, else +0x1a8. Then it is freed.

**Ported** (2026-11-18):
- Collide::destroy (destroy.rs) and World::destroy (sleep.rs). Collide::touched is set in friction_from_mindist.
- KartWorld::destroy (kart_world.rs): the env list's fast-remove, the silent rule (env +0x9c), the queue run at the
  next Simulate's start, and a dead thing that does nothing more. It is ABI op 12, and kart_replay / kart_world_check
  read it. The game calls it at the engine's `kill` (csgo/maps/ze_crazykart/install.js `killed`) for a kart or a mover.
- Checked against the oracle (scenarios/make-destroy.mjs; MoreKarts `destroy`, which Mindists now forgets):
  - destroy-touch.txt: a kart destroyed while another pushes it in one unit, and one destroyed asleep after
    touching only the floor. 700 ticks.
  - destroy-pile.txt: three karts of pile8. The second delete wakes the sleeping pile through the revival.
    300 ticks.
  - destroy-lift.txt: two karts on the moving lift. 260 ticks.
  - All bit-identical in ivp_check and in kart_world_check (unit lists included).
- A recorded round (kart-map-test, 156 deletes) replays natively with no trap.
- **A static's delete** (2026-11-18): Collide::static_vicinity. KartWorld::destroy takes statics. The oracle gained
  the `boxsolid <i> 0|1` event (NOT_SOLID with the filter's recheck; the oracle's solver refuses a not-solid box) and
  the `destroybox <i>` event, and ivp_check takes several boxes. scenarios/make-static-destroy.mjs builds three
  360-tick scenarios with a platform under two karts, all bit-identical in ivp_check:
  - static-kill.txt: killed while solid, under two sleeping karts, which fall;
  - static-break.txt: not solid, then destroyed 7 ticks later;
  - static-drive.txt: destroyed under a driving kart.

**Left**:
- A static's 0x10082ce0 with a partner outside a friction system, and a static-static contact. Both are noted and
  stop the world.
- kart_world_check has no static brush to destroy (the oracle makes boxes, not brush models), so the static path is
  checked through ivp_check only.
- CS:GO's UpdateOnRemove order for a parent and its children (the engine kills the children first).
- The server side's addresses (UTIL_Remove -> VPhysicsDestroyObject).
- The 0x400 mark's effect between the call and the queue's run (RecheckCollisionFilter is skipped, the filter's
  0x800 / 0x400 refusal).

On ze_crazykart_v4's I/O the destroys are func_breakable Break (15 outputs) and Kill on func_button (13),
func_physbox (8), func_door (6), func_rotating (4), func_wall_toggle (3), func_movelinear (2), func_brush and the
kart's prop_physics_override (1 each).
