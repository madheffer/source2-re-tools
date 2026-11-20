# CS:GO legacy IVP: two karts touching (vphysics.dll, 32-bit, 2026-11-17)

**CS:GO legacy, not CS2** (ze_crazykart's karts, docs/CRAZYKART.md). vphysics.dll md5 d97cf2194594d7545427cdabc7376db4,
Ghidra `/csgo_vphysics_legacy.dll`, capstone (`python tools/re/game/disasm.py <dll> <va>`, without `-I`). What two dynamic
bodies do to each other: friction systems as a list (a static floor in several), the systems' merge and split, the
simulation units' merge and split, vphysics' pair-time listener, the rescue push of two objects through each other (and
of one through a static face). Ported in sim/src/ivp: units.rs, friction_split.rs, rescue.rs, friction_sys.rs (merge,
the pair table), world.rs / sleep.rs (units of several cores), collide*.rs (the cache's renew rule, stage 3's order, the
revival's cache). Checked by ivp_check on scenarios touch (700 ticks) and touch-world (1000 ticks): every tick
bit-identical, and every older scenario still.

## 1. Friction systems and their infos (0x10088450, ivp-impact.md 4)

A dynamic core has at most one friction info (+0x4c: +0 / +4 its contact vector, +8 the system); a static core keeps a
hash of infos, one per system it is in (0x1006e4b0 find by the system's address, 0x1006e200 insert, 0x1006e340 remove;
made by 0x10076330 on first use). So a static floor sits in every kart's own system. Nothing walks the systems: each is
found from a core. The port: `Friction::systems` (a Vec), `sys_of(core)` = the system whose dynamic cores hold it; a
static core is "in" a system when that system's core list holds it.

0x10088450's branches, the dynamic core first (the sorted synapse 0's unless static), `other` the second:
- dynamic has an info (system S): other has an info for S -> the contact into S. Else other dynamic with an info (system
  T): **0x10081280(S, T)** (T merges into S), then the contact into S. Else a new info for other (0x10078860),
  **0x100871f0(S, other)**, the contact into S.
- dynamic has none: other dynamic with an info (T): 0x10078860(dynamic), 0x100871f0(T, dynamic), the contact into T
  (0x100871c0 + 0x100870c0). Else a new system (0x10086de0) with both.
- tail: both infos take the contact; 0x10082a60; then two dynamic cores on different units merge them (section 4):
  **the other's unit keeps both when it is the third argument** (core 1's unit when object 0's +0x44 < 8, else core 0's:
  ivp-impact.md 2), else the dynamic one's.

## 2. 0x10081280: system T merged into S (thiscall S, T)

1. T's contacts from its head: each unlinked (T +0x3e -= 1), **0x10086fb0(T, cp)** (its pair found last to first by the
   two cores, the contact out of it (0x10018430: the last occurrence, the rest kept in order); an emptied pair: env
   listener 0x10084ee0, out of T +0x34, deleted 0x10087070), then cp+0x90 = S, at S's head (+0x3e += 1),
   **0x100870c0(S, cp)** (the pair found, or a new one: env listener 0x10084e90, section 5). So T's pairs are rebuilt in
   S fresh (countdown 1, t -1000, energy 0) and the contacts end in reverse order at S's head.
2. T's cores from the last: one that has an info for S already (a static core in both) moves its T-info's contacts into
   its S-info, the T-info freed, **and stays in T's lists** (T is deleted anyway). Any other: its info re-keyed to S
   (dynamic: +0x4c; static: hash remove T, insert S); a dynamic one leaves T +0x2c and its own and its unit's lists lose
   T's three controllers (0x10018430 on core +0x140, then 0x10071dc0(unit, core, controller); +0x10 (2000), +0 (600), +8
   (0)); out of T +0x24 (T +0x3c -= 1); into S +0x24, a dynamic one into S +0x2c with S's controllers (0x10071d40: +8,
   +0, +0x10); S +0x3c += 1.
3. T's slot 7 (0x10086e30 -> 0x10086e60: its vectors freed; nothing about cores).

## 3. The split: 0x10082f60 -> 0x100815a0 / 0x100816a0

0x10082f60 (the priority-0 controller): after the solve (0x10082ed0 for one contact, else 0x100a0b30), no contact left:
the system's slot 7 and the event's unit marked (`& ~0x200 | 0x100`); else, +0x44 set (a contact went: 0x100810a0):
+0x44 = 0, **0x100815a0**; a root found: **0x100816a0(system, root)** and the root core's unit marked the same way.

**0x100815a0** (union-find over core +0x1a8, a parent pointer): every core of the system (+0x28 list) +0x1a8 = 0; each
pair (last to first) of two dynamic cores: core 1's root under core 0's (when they differ); r0 = the root of the
lowest-index dynamic core (a walk from the last keeping the latest); answer = the root of the lowest-index dynamic core
whose root isn't r0 (another walk from the last), or 0.

**0x100816a0** (thiscall system, root), a loop:
1. a new system N (0x4c bytes, the ctor inlined: vtables 0x100f1cc8 / 0x100f1d10 / 0x100f1cf0, +4 the environment, +0x44
   = 0; +0x40 isn't written: the solve zeroes it before use).
2. this system's cores from the last: a dynamic one of the root's group leaves this system's +0x2c, its controllers
   (+0x10, +0, +8: 0x10018430 + 0x10071dc0), its +0x24 (+0x3c -= 1), joins N +0x24 / +0x2c with N's controllers (+8,
   +0, +0x10), N +0x3c += 1, its info's +8 = N. **Every static core** gets a new info for N (N +0x24, +0x3c += 1, its
   hash) and keeps this system's.
3. the pairs from the last whose dynamic core (core 0 when both are; the dynamic one of a static pair) is in the group:
   env 0x10084ee0, out of +0x34 (in order), appended to N +0x34, env 0x10084e90; its contacts (the pair's from the last)
   unlinked here (+0x3e -= 1; IVP Failed 0x5ef when not in the list), cp+0x90 = N, at N's head; a static core's
   contact moved from its this-info to its N-info.
4. the static cores (this system's, from the last): an N-info without contacts freed and out of N's list (+0x3c -= 1);
   a this-info without contacts freed and out of this list.
5. N with fewer than 2 cores (+0x3c): its first core's info freed, N deleted, return; this system the same; else
   0x100815a0 again, and the loop while it finds another root. (The port panics on a system of one core: not reached.)

## 4. Simulation units of several cores (units.rs)

The unit (0x10077e60's block): +0 flags (state byte: 1 active, 8 sleeping), +4 / +8 its manager list's links, +0xc / +0xe
/ +0x10 its cores, +0x1c / +0x1e / +0x20 its controller entries {controller, its cores (+4 vector)}.
- **0x10071d40**(core, controller): appended to core +0x140 (no check), the unit's entry found last to first or appended
  (0x10071550), the core appended to it (0x100714f0), the sort 0x10071e40.
- **0x10071dc0**(unit, core, controller): the entry (last to first), the core out (0x10018430), an emptied entry deleted
  (0x10071890) and the rest shifted.
- **0x100713b0** (rebuild): cores last to first, each core's own list last to first, its entry found or made, the core
  appended; then the sort. 0x10071800 frees the entries first.
- **0x100718e0**(keep, gone): gone's cores appended to keep's (each core +0x14c = keep); gone out of its manager list
  (+0x1a8 when its state byte >= 8, else +0x18). The merge at 0x10088450's tail: 0x10071800(keep), 0x100718e0,
  0x100713b0(keep), 0x10071aa0(gone) (0x10071ac0: entries and vectors freed, the block freed).
- **0x10072540** (a unit's PSI) with several cores: the cores n-1 .. 1 then 0 at the PSI's time (0x100723b0), committed
  (0x10077520), flags & 0xff3f, +2 = 0, each's `1 - |v|^2` or-ed as bits (any sign bit: 0x400); the flags' shift and
  0x10071f70 (every core's references' times); the countdown; the entries from the last, each controller's slot 4 with
  the entry's core vector; **the cores into the moved list last to first**; the sleep check; each core's objects'
  0x10073a50; flags & 0x300: 0x10071800, 0x100713b0, **0x10071710**, a root: 0x10071800, **0x100715c0**, 0x100713b0;
  & ~0x300.
- **0x100722d0** (sleep check): every core last to first (0x100782a0 into its byte 1), and-ed; all 3: every core frozen
  last to first (0x10077820, 0x10086d60), the unit to the sleeping list's head (state 8).
- **0x10071ef0** (revive): the cores last to first, each with +1 >= 8 through 0x10086b70; its answer 1 restarts the walk
  (TODO(trace): when 0x10082ce0 answers 1; not seen); a state-8 unit to the active list's head (state 1).
- **0x10071710** (split test): the unit's cores' +0x1a8 = 0; each entry (last to first): the controller's slot 2 (the
  cores it acts on): every independent controller (gravity 0x100e0a04, drag 0x100e1c1c, motion 0x100e2284, the
  friction faces 0x100f1d10 / 0x100f1cf0) returns one shared empty list (0x10007ca0 -> 0x101163dc); the friction
  system's +0 face (0x100f1cc8, priority 600) returns the system's dynamic cores (0x10082e60: system +0x2c); each list's
  cores (last to first) under its first one's root. Answer: the first unit core (ascending) whose root isn't core 0's.
- **0x100715c0**(unit, root), a loop: a new unit (0x24 bytes: state 8, flags & ~0x300 & ~0x3c00, then state 1) at the
  active list's head; the unit's cores in order: the root's group moves (each core +0x14c = it), the first other root
  seen kept; 0x100713b0 on the new unit; again with that root while a third group was seen.

The port: `World::units` (a body's own unit has its index), `Body::unit`, `Body::ctl` (the core's own list); stage 2,
the sleep check, the revival, Wake, Sleep and EnableGravity per unit. The equal Kinds of two systems' controllers share
one port entry (the DLL has one per controller); only 0x10071710 reads the difference and Collide::unit_split gives it
one list per system. The oracle names a unit by its cores (`kart+b`, MoreKarts.UnitName).

## 5. vphysics' pair times (CPhysicsListenerCollision, vtable 0x100e1d1c-ish, slots 0-7: 0x10012210, 0x10012340,
0x10004450, 0x100123c0, 0x100124b0, 0x100127e0, 0x100128c0, 0x100127b0)

The environment's collision listeners (IVP env +0xca count, +0xcc list, each +4 flags): flags & 4 get slot 5 at a pair
made (0x10084e90) and slot 6 at a pair deleted (0x10084ee0). vphysics' listener (flags 0xd) keeps a tree at +0xc (+0x10
nodes of 0x18 bytes: +8 / +0xc the cores in address order, +0x10 the time; +0x1e the count, +0x22 the last index):
- **slot 5, 0x100127e0** (made): found: a kept time later than the pair's (+0x28) is copied into the pair, else the kept
  one takes the pair's; not found and fewer than 16: added.
- **slot 6, 0x100128c0** (deleted): found: the pair's time when later; not found and fewer than 16: added.
- **0x10012630** (from Simulate 0x10014320 at its start, on env +0x8c): every entry with 1.0 < f32(env+0xf0 - its time)
  removed (0x10016320). So a time is kept about a second: a pair rebuilt by a merge or split, or made again soon after it
  went, keeps its last impact time. Slot 4 (0x100124b0) is the game's friction callback, slot 7 the destructor.
- The pair's +0x28 is otherwise written only by 0x100870c0 (-1000) and the impact (0x1008ac60: the event's time).

Port: `Friction::pair_times` (PairTimes: created / destroyed / the cleanup in Collide::simulate); the solver's emptied
pairs reach it through `FrictionSystem::gone`.

## 6. The rescue push (recalc_mindist 0x100982d0 -> the mindist's slot 5, 0x100980a0)

0x100980a0 (fastcall mindist): the anomaly manager = IVP env +0x20 (vphysics' CCollisionSolver at env +0x90's +4,
vtable 0x100e1c50, built in CPhysicsEnvironment's ctor 0x10013090 at 0x10013265): slot 7 **0x10083e40**(obj0, obj1) =
sqrtss((g.x^2 + g.y^2) + g.z^2) x 4.0 (0x100f3f18) x env dt (+0xa8) (g: env +0xb0..+0xb8, the gravity; returned
through x87, stored f32), then slot 2 **0x10012a10**(mindist, obj0, obj1, speed):
- the game's solver (this+8) set: both CPhysicsObjects (+0xa0) present, neither's flags +0x1c & 0x400; both moveable
  (CPhysicsObject slot 10): **0x10012cb0**(the solver, obj0, obj1): the pair (lower, higher address) in the list
  +0x10 / +0x1c: return (pushed already); not in it: appended (0x10016240), go on. The list is cleared at Simulate's
  start (0x10014320: env +0x90's +0x1c = 0). Then the solver's ShouldSolvePenetration (slot 1) with both objects, their
  game data and dt: 0 returns. (The server's 0x102f78a0 answers yes until a pair has been through each other 3 s:
  TODO(trace) its timer; the oracle answers yes.)
- (2026-11-18, checked against the DLL: world-inside.txt / disp-inside.txt, a kart made inside a solid brush) the
  push runs inside the recalc that found the penetration. A kart's first mindists are made by its own revival
  (stage 1, its core's movement byte 0x21): both branches below leave a core at >= 8 alone, so that recalc pushes
  nothing; the first push is the next invalid recheck's (0x10073a50 in stage 2: 0x10073a77 -> ... -> 0x100982a0
  -> 0x100980d8 -> 0x10012ae9 -> the write at 0x10083e1a, speed_change += n x s), once a PSI while it stays
  invalid, committed at the next PSI's 0x10077520. The port queues the push with what the recalc saw of each
  core (Collide::rescue).
- then IVP's **0x100839a0**(mindist, obj0, obj1, speed): u = core 1's static bit; obj[u] static and its synapse's status
  (mindist +0x32 + 0x1c u) <= 2: **the static branch**; else **0x10083760**(obj0, obj1) (speed in xmm3).

**0x10083760** (two dynamic): d = core1.pos_now - core0.pos_now (+0x90), n = (dy dy + dx dx) + dz dz; 1e-10 (0x100f3b94)
> n: len 0 and d as is; else i = 1 / sqrtss(n), d x= i, len = i n; 0.01 (f64 0x100f3d80) >= f64(len): d = (1, 0, 0).
Core 0 simulated (+1 < 8) and not pinned (flags & 0x10): m = its mass (+0x1c), or minss(core1's, its) when core 1 isn't
pinned; **0x10074e10**(obj0, core0.pos_now, d x -(m s)); 0x10075060(obj0); core0 +0xa0 += -dt. Core 1 the same with
+(m s), **at core 0's pos_now**, and +dt.

**0x10074e10** (async_push_core: thiscall object, the world point, the world impulse): 0x10075060; **0x10076b50**(core,
env+0xf0) the core's matrix at that time (below); r = point - its translation; r in core axes per column: (m1 ry + m0 rx)
+ m2 rz; the impulse the same: (m0 Ix + m1 Iy) + m2 Iz; rot_change += (r x I_core) x 1/inertia (+0x30..; x = l2 b - l1 c,
y = l0 c - l2 a, z = l1 a - l0 b, each (cross x inv) + old); speed_change += inv_mass (+0x3c) x the world impulse.

**0x10076b50** (the core's matrix at t): +1 >= 8, or f32(t - t_psi) == 0 exactly (`lahf; test ah,0x44; jnp`): the core's
rows (+0x60) and pos_now (+0x90); else 0x1006ca90's quaternion in packed form (the same sums), its rows, delta x dt + pos.

**The static branch** (0x100839f9..): the other object's core (+1 >= 8: return); its pos_now in the static object's
axes (its cache 0x10001b50: cache +0x50 the origin, +0x20 / +0x30 / +0x40 the rows: (m1 py + m0 px) + m2 pz per
column); the synapse's ledge (edge & ~0xf, - (tri index + 1) x 16), each triangle (n at ledge +0xc): A, B, C its corners
(edges 0, 1, 2's start points), b = B - A, c = C - A, q = (by cz - bz cy, bz cx - bx cz, bx cy - by cx), off =
-((A.y qy + qx A.x) + qz A.z), i = 1 / sqrtss((qy qy + qx qx) + qz qz), dist = ((l1 qy i + l0 qx i) + l2 qz i) + off i;
the largest (> -1e20, 0x100f40f4; (1, 0, 0) without triangles) gives n; n in world axes (row . n: (r.y ny + nx r.x) +
r.z nz); v = ((delta.y + sc.y) n1 + (delta.x + sc.x) n0) + (delta.z + sc.z) n2 (+0xf0, +0xb0); speed x 0.1 (0x100f3c60)
> v: 0x10075060 and speed_change += n x speed.

Port: rescue.rs; recalc_mindist reports `rescue`, Collide::recalc queues it and md_event applies it right after (a
recalc inside a time event, as the DLL). Recalcs with only the World to read (stages 5-6, an impact's replan) apply
theirs after their stage and report it (`late_rescues`, TODO(verify) when a scenario reaches one).

## 7. Three things one kart never showed

- **The cache's renew rule** (0x10099850, 0x10001b50): only an object with +0x44 < 8 has its cache renewed when older
  than the time code; a frozen one (8) or one inside its revival's recheck (0x21) keeps the cache it had. A new cache
  (0x1006ccb0: a ring of slots, the next one with no users, its old owner's +0x40 cleared; +0x60 = 0) is updated at once
  only when +0x44 > 7. The port renewed every body's cache.
- **Stage 3's order** (0x10097d00): the moved cores from the last, each core's objects last first, into the due list.
- **insert_hull_mindist 0x100960d0**'s "moving" is object +0x44 & 7 (a frozen body's 8 isn't).
- The revival's collision side runs in stage 1 in the DLL, with the caches as stage 1 finds them; the port runs it after
  the PSI (core snapshots, and now the pre-PSI caches: Collide::pre_cache).

## 8. The oracle (rubikon/tests/KartOracle)

Mindists.cs names every kart (`kart2 <name>` and `create`); each kart's `.raw` gets its own system's `fs` / `cp` /
`pair` lines (Contacts.Fs); the env rows name units by their cores; `KART_ORACLE_CACHE=1` adds a `cache` line per cache
update (object, +0x44, its code before, the env's, the quaternion after) and the env's collision listeners at each pair
made; every tick a `ptimes` line (vphysics' pair-time table) and `pen` (the penetrating pairs, when any). ivp_check's
ground mode takes several karts (objects: kart 0, the statics, the extra karts in order) and compares each kart's system,
every mindist's queued time event, and the hull managers of every kart.

## Still untraced here

A friction system split down to one core (0x100816a0's end); a body destroyed out of a unit of several cores; 0x10086b70
answering 1; a rescue push from stages 5-6; the server's ShouldSolvePenetration timer; the cache ring's evictions (the
port never evicts: identical only while no slot is reused under a frozen object).
