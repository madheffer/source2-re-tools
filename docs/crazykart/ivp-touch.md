# IVP: two karts touching

CS:GO legacy vphysics.dll md5 d97cf2194594d7545427cdabc7376db4, Ghidra `/csgo_vphysics_legacy.dll` (ze_crazykart's
karts). Two dynamic bodies against each other: friction systems as a list (a static floor in several), the systems' and
the simulation units' merge and split, vphysics' pair-time listener, the rescue push of two objects through each other
(and of one through a static face).

## Functions

| Address | Module | What |
|---|---|---|
| 0x10088450 | vphysics | contact from a mindist into a friction system (ivp-impact.md 4) |
| 0x1006e4b0 / 0x1006e200 / 0x1006e340 | vphysics | static core's info hash: find by system address / insert / remove |
| 0x10076330 | vphysics | static core's info hash made on first use |
| 0x10078860 | vphysics | new friction info for a core |
| 0x100871f0 / 0x100871c0 / 0x100870c0 | vphysics | system adds a core / (with 0x100870c0) / pair found or made for a contact |
| 0x10086de0 | vphysics | new friction system |
| 0x10082a60 | vphysics | contact mass / sliding switch |
| 0x10081280 | vphysics | system T merged into S (thiscall S, T) |
| 0x10086fb0 | vphysics | contact out of its pair (pair found last to first by the two cores) |
| 0x10018430 | vphysics | vector remove: the last occurrence, the rest kept in order |
| 0x10087070 | vphysics | pair delete |
| 0x10084ee0 / 0x10084e90 | vphysics | env listeners: pair deleted / pair made |
| 0x10086e30 -> 0x10086e60 | vphysics | system slot 7: its vectors freed |
| 0x10082f60 | vphysics | priority-0 controller |
| 0x10082ed0 / 0x100a0b30 | vphysics | one-contact / many-contact normal solve |
| 0x100810a0 | vphysics | a contact removed (sets +0x44) |
| 0x100815a0 | vphysics | system split test (union-find) |
| 0x100816a0 | vphysics | system split (thiscall system, root) |
| 0x10077e60 | vphysics | simulation unit block |
| 0x10071d40 | vphysics | (core, controller) added to a unit |
| 0x10071550 / 0x100714f0 | vphysics | unit entry append / core into entry |
| 0x10071e40 | vphysics | unit entries sort |
| 0x10071dc0 | vphysics | (unit, core, controller) removed |
| 0x10071890 | vphysics | emptied entry deleted |
| 0x100713b0 | vphysics | unit rebuild |
| 0x10071800 | vphysics | unit entries freed |
| 0x100718e0 | vphysics | units merged (keep, gone) |
| 0x10071aa0 -> 0x10071ac0 | vphysics | unit freed (entries, vectors, block) |
| 0x10072540 | vphysics | a unit's PSI |
| 0x100723b0 | vphysics | a core at the PSI's time |
| 0x10077520 | vphysics | core commit |
| 0x10071f70 | vphysics | every core's references' times |
| 0x10073a50 | vphysics | an object's recheck (stage 2) |
| 0x100722d0 | vphysics | sleep check |
| 0x100782a0 | vphysics | core's sleep vote into its byte 1 |
| 0x10077820 / 0x10086d60 | vphysics | core frozen |
| 0x10071ef0 | vphysics | revive |
| 0x10086b70 | vphysics | revive a core (answer 1 restarts the walk) |
| 0x10082ce0 | vphysics | (when it answers 1: unread) |
| 0x10071710 | vphysics | unit split test |
| 0x10007ca0 -> 0x101163dc | vphysics | independent controller slot 2: one shared empty list |
| 0x10082e60 | vphysics | friction +0 face slot 2: system +0x2c |
| 0x100715c0 | vphysics | unit split (unit, root) |
| 0x10012210, 0x10012340, 0x10004450, 0x100123c0, 0x100124b0, 0x100127e0, 0x100128c0, 0x100127b0 | vphysics | CPhysicsListenerCollision slots 0-7 (vtable 0x100e1d1c-ish) |
| 0x100124b0 | vphysics | slot 4: the game's friction callback |
| 0x100127e0 | vphysics | slot 5: pair made |
| 0x100128c0 | vphysics | slot 6: pair deleted |
| 0x100127b0 | vphysics | slot 7: destructor |
| 0x10012630 | vphysics | pair-time cleanup (from Simulate's start, on env +0x8c) |
| 0x10016320 | vphysics | tree entry remove |
| 0x10014320 | vphysics | Simulate |
| 0x1008ac60 | vphysics | impact (writes pair +0x28: the event's time) |
| 0x100982d0 | vphysics | recalc_mindist |
| 0x100980a0 | vphysics | mindist slot 5 (fastcall mindist): rescue |
| 0x10013090 | vphysics | CPhysicsEnvironment ctor (builds CCollisionSolver at 0x10013265) |
| 0x10083e40 | vphysics | anomaly slot 7 (obj0, obj1): the rescue speed |
| 0x10012a10 | vphysics | anomaly slot 2 (mindist, obj0, obj1, speed) |
| 0x10012cb0 | vphysics | penetrating-pair list test (solver, obj0, obj1) |
| 0x10016240 | vphysics | list append |
| 0x100839a0 | vphysics | IVP rescue (mindist, obj0, obj1, speed) |
| 0x100839f9 | vphysics | its static branch |
| 0x10083760 | vphysics | two dynamic (obj0, obj1; speed xmm3) |
| 0x10074e10 | vphysics | async_push_core (thiscall object, world point, world impulse) |
| 0x10075060 | vphysics | ensure_in_simulation (Wake's body: an unsimulated object's core queued for revival, else its reference times set; crazykart-physics.md 12) |
| 0x10076b50 | vphysics | core's matrix at t (core, time) |
| 0x1006ca90 | vphysics | quaternion at t |
| 0x10001b50 | vphysics | object's cache |
| 0x10099850 | vphysics | cache renew |
| 0x1006ccb0 | vphysics | new cache |
| 0x10097d00 | vphysics | stage 3 |
| 0x100960d0 | vphysics | insert_hull_mindist |
| 0x102f78a0 | server | ShouldSolvePenetration |

## Fields

| Offset | Field |
|---|---|
| dynamic core +0x4c | friction info: +0 / +4 its contact vector, +8 the system |
| core +1 | movement / state byte (>= 8 frozen, 0x21 inside its revival's recheck) |
| core +0x1c / +0x3c | mass / inv_mass |
| core +0x30.. | 1 / inertia |
| core +0x60 / +0x90 | rows / pos_now |
| core +0xa0 | (rescue adds -dt / +dt) |
| core +0xb0 / +0xf0 | speed_change / delta (rescue's v) |
| core +0x140 | core's own controller list |
| core +0x14c | its unit |
| core +0x1a8 | union-find parent |
| core flags & 0x10 | pinned |
| system +0x24 / +0x28 / +0x2c | cores / cores (the split's list) / dynamic cores |
| system +0x34 / +0x3c / +0x3e | pairs / core count / contact count |
| system +0x40 | not written by the inlined ctor (the solve zeroes it) |
| system +0x44 | 1 = a contact went (may split) |
| system +0 / +8 / +0x10 | controller faces: 600 / 0 / 2000 |
| pair +0x28 | last impact time (-1000 by 0x100870c0) |
| cp +0x90 | the system |
| unit +0 | flags (state byte: 1 active, 8 sleeping) |
| unit +2 | zeroed per PSI |
| unit +4 / +8 | manager list's links |
| unit +0xc / +0xe / +0x10 | its cores |
| unit +0x1c / +0x1e / +0x20 | controller entries {controller, its cores (+4 vector)} |
| unit manager +0x18 / +0x1a8 | active / sleeping lists (by state byte >= 8) |
| IVP env +0x20 | anomaly manager (vphysics' CCollisionSolver at env +0x90's +4, vtable 0x100e1c50) |
| IVP env +0x8c | the listener cleanup's argument |
| IVP env +0x90 +0x1c | penetrating pair list count (0 at Simulate's start) |
| IVP env +0xa8 / +0xb0..+0xb8 / +0xf0 | dt / gravity / time |
| IVP env +0xca / +0xcc | collision listener count / list (each +4 flags; & 4 gets slots 5 / 6) |
| anomaly solver +8 | the game's solver |
| anomaly solver +0x10 / +0x1c | pair list (lower, higher address) |
| object +0x44 | movement byte: < 8 cache renewed; & 7 "moving" |
| object +0x40 | its cache (cleared on eviction) |
| IVP object +0xa0 | its CPhysicsObject |
| CPhysicsObject +0x1c | flags (& 0x400: no rescue push) |
| mindist +0x32 + 0x1c u | synapse u's status |
| cache +0x20 / +0x30 / +0x40 | rows |
| cache +0x50 | origin |
| cache +0x60 | 0 in a new cache |
| ledge +0xc | triangle count |
| listener (flags 0xd) +0xc | tree: +0x10 nodes of 0x18 bytes (+8 / +0xc the cores in address order, +0x10 the time), +0x1e count, +0x22 last index |

## Constants

| Value | What |
|---|---|
| 16 | pair-time tree capacity |
| 1.0 s | pair-time kept (`1.0 < f32(env+0xf0 - time)` removes) |
| -1000 | new pair's time |
| 4.0 (0x100f3f18) | rescue speed factor |
| 1e-10 (0x100f3b94) | direction floor |
| 0.01 (f64 0x100f3d80) | length floor -> d = (1, 0, 0) |
| -1e20 (0x100f40f4) | best-face start |
| 0.1 (0x100f3c60) | static branch speed factor |
| 0x5ef | IVP Failed line: contact not in the list |
| 3 s | server ShouldSolvePenetration: yes until a pair has been through each other this long |
| gravity 0x100e0a04, drag 0x100e1c1c, motion 0x100e2284, friction 0x100f1d10 / 0x100f1cf0 / 0x100f1cc8 | controller vtables (independent ones return the shared empty list) |

## 0x10088450's branches

Dynamic core first (sorted synapse 0's unless static), `other` second:
- Dynamic has an info (system S): other has an info for S -> contact into S. Else other dynamic with an info (T): 0x10081280(S, T), contact into S. Else new info for other (0x10078860), 0x100871f0(S, other), contact into S.
- Dynamic has none: other dynamic with an info (T): 0x10078860(dynamic), 0x100871f0(T, dynamic), contact into T (0x100871c0 + 0x100870c0). Else a new system (0x10086de0) with both.
- Tail: both infos take the contact; 0x10082a60; two dynamic cores on different units merge them: the other's unit keeps both when it is the third argument (core 1's unit when object 0's +0x44 < 8, else core 0's: ivp-impact.md 2), else the dynamic one's.

A static core keeps one info per system it is in, so a static floor sits in every kart's own system. Nothing walks the systems: each is found from a core.

## 0x10081280: T into S

1. T's contacts from its head: each unlinked (T +0x3e -= 1), 0x10086fb0(T, cp) (emptied pair: 0x10084ee0, out of T +0x34, 0x10087070), cp+0x90 = S, at S's head (+0x3e += 1), 0x100870c0(S, cp) (found, or new: 0x10084e90). T's pairs are rebuilt fresh (countdown 1, t -1000, energy 0); the contacts end reversed at S's head.
2. T's cores from the last: one with an info for S already (a static core in both) moves its T-info's contacts into its S-info, T-info freed, and stays in T's lists. Any other: info re-keyed to S (dynamic +0x4c; static hash remove T, insert S); a dynamic one leaves T +0x2c, and its own and its unit's lists lose T's three controllers (0x10018430 on core +0x140, then 0x10071dc0; order +0x10 (2000), +0 (600), +8 (0)); out of T +0x24 (T +0x3c -= 1); into S +0x24, a dynamic one into S +0x2c with S's controllers (0x10071d40: +8, +0, +0x10); S +0x3c += 1.
3. T's slot 7 (nothing about cores).

## The split: 0x10082f60 -> 0x100815a0 / 0x100816a0

After the solve: no contact left: system slot 7 and the event's unit marked (`& ~0x200 | 0x100`); else +0x44 set: +0x44 = 0, 0x100815a0; a root found: 0x100816a0(system, root) and the root core's unit marked the same way.

**0x100815a0**: every core (+0x28 list) +0x1a8 = 0; each pair (last to first) of two dynamic cores: core 1's root under core 0's (when they differ); r0 = root of the lowest-index dynamic core (walk from the last keeping the latest); answer = root of the lowest-index dynamic core whose root isn't r0 (another walk from the last), or 0.

**0x100816a0**, a loop:
1. New system N (0x4c, ctor inlined: vtables 0x100f1cc8 / 0x100f1d10 / 0x100f1cf0, +4 env, +0x44 = 0).
2. Cores from the last: a dynamic one of the root's group leaves +0x2c, its controllers (+0x10, +0, +8: 0x10018430 + 0x10071dc0), +0x24 (+0x3c -= 1); joins N +0x24 / +0x2c with N's controllers (+8, +0, +0x10), N +0x3c += 1, info +8 = N. Every static core gets a new info for N (N +0x24, +0x3c += 1, its hash) and keeps this system's.
3. Pairs from the last whose dynamic core (core 0 when both are) is in the group: 0x10084ee0, out of +0x34 (in order), appended to N +0x34, 0x10084e90; its contacts (from the last) unlinked (+0x3e -= 1; IVP Failed 0x5ef when not listed), cp+0x90 = N, at N's head; a static core's contact moved from its this-info to its N-info.
4. Static cores (from the last): an N-info without contacts freed and out of N's list (+0x3c -= 1); a this-info without contacts likewise.
5. N with fewer than 2 cores: its first core's info freed, N deleted, return; this system the same; else 0x100815a0 again, loop while another root.

## Simulation units of several cores

- **0x10071d40**(core, controller): appended to core +0x140 (no check); the unit's entry found last to first or appended (0x10071550), the core appended (0x100714f0), sort 0x10071e40.
- **0x10071dc0**(unit, core, controller): entry (last to first), core out (0x10018430), emptied entry deleted (0x10071890), rest shifted.
- **0x100713b0**: cores last to first, each core's own list last to first, entry found or made, core appended; then the sort. 0x10071800 frees the entries first.
- **0x100718e0**(keep, gone): gone's cores appended to keep's (+0x14c = keep); gone out of its manager list (+0x1a8 when state >= 8, else +0x18). Merge at 0x10088450's tail: 0x10071800(keep), 0x100718e0, 0x100713b0(keep), 0x10071aa0(gone).
- **0x10072540** with several cores: cores n-1 .. 1 then 0 at the PSI's time (0x100723b0), committed (0x10077520), flags & 0xff3f, +2 = 0, each's `1 - |v|^2` or-ed as bits (any sign bit: 0x400); the flags' shift and 0x10071f70; the countdown; entries from the last, each controller's slot 4 with the entry's core vector; the cores into the moved list last to first; the sleep check; each core's objects' 0x10073a50; flags & 0x300: 0x10071800, 0x100713b0, 0x10071710, a root: 0x10071800, 0x100715c0, 0x100713b0; & ~0x300.
- **0x100722d0**: every core last to first (0x100782a0 into byte 1), and-ed; all 3: every core frozen last to first (0x10077820, 0x10086d60), unit to the sleeping list's head (state 8).
- **0x10071ef0**: cores last to first, each with +1 >= 8 through 0x10086b70 (answer 1 restarts the walk); a state-8 unit to the active list's head (state 1).
- **0x10071710**: cores' +0x1a8 = 0; each entry (last to first): controller slot 2 (the cores it acts on: independent ones the shared empty list; friction's +0 face the system's dynamic cores); each list's cores (last to first) under its first one's root. Answer: the first unit core (ascending) whose root isn't core 0's.
- **0x100715c0**(unit, root), a loop: new unit (0x24 bytes: state 8, flags & ~0x300 & ~0x3c00, then state 1) at the active list's head; cores in order: the root's group moves (+0x14c), the first other root seen kept; 0x100713b0 on the new unit; again with that root while a third group was seen.

## Pair times (CPhysicsListenerCollision)

- Slot 5 0x100127e0 (made): found: a kept time later than the pair's (+0x28) is copied into the pair, else the kept one takes the pair's; not found and fewer than 16: added.
- Slot 6 0x100128c0 (deleted): found: the pair's time when later; not found and fewer than 16: added.
- 0x10012630 (Simulate 0x10014320's start): entries with `1.0 < f32(env+0xf0 - time)` removed (0x10016320). A pair rebuilt by a merge or split, or made again within about a second, keeps its last impact time.
- Pair +0x28 is otherwise written only by 0x100870c0 (-1000) and 0x1008ac60.

## The rescue push: 0x100982d0 -> 0x100980a0

1. Slot 7 0x10083e40(obj0, obj1) = `sqrtss((g.x^2 + g.y^2) + g.z^2) x 4.0 x env dt (+0xa8)` (returned through x87, stored f32).
2. Slot 2 0x10012a10(mindist, obj0, obj1, speed): with the game's solver set, both CPhysicsObjects present, neither +0x1c & 0x400, both moveable (slot 10): 0x10012cb0: pair in the list: return; else appended (0x10016240). Then ShouldSolvePenetration (slot 1, both objects, game data, dt): 0 returns.
3. Then 0x100839a0: u = core 1's static bit; obj[u] static and its synapse's status <= 2: the static branch; else 0x10083760.

Timing (checked against the DLL with a kart made inside a solid brush): the push runs inside the recalc that found the penetration. A kart's first mindists come from its own revival (stage 1, movement byte 0x21): both branches leave a core at >= 8 alone, so that recalc pushes nothing; the first push is the next invalid recheck's (0x10073a50 in stage 2: 0x10073a77 -> ... -> 0x100982a0 -> 0x100980d8 -> 0x10012ae9 -> the write at 0x10083e1a, speed_change += n x s), once a PSI while invalid, committed at the next PSI's 0x10077520.

**0x10083760**: `d = core1.pos_now - core0.pos_now`, `n = (dy dy + dx dx) + dz dz`; `1e-10 > n`: len 0, d as is; else `i = 1 / sqrtss(n)`, `d x= i`, `len = i n`; `0.01 >= f64(len)`: d = (1, 0, 0). Core 0 simulated (+1 < 8) and not pinned: m = its mass, or `minss(core1's, its)` when core 1 isn't pinned; 0x10074e10(obj0, core0.pos_now, `d x -(m s)`); 0x10075060(obj0); core0 +0xa0 += -dt. Core 1 the same with `+(m s)`, at core 0's pos_now, and +dt.

**0x10074e10**: 0x10075060; 0x10076b50(core, env+0xf0); `r = point - translation`; r in core axes per column `(m1 ry + m0 rx) + m2 rz`; the impulse `(m0 Ix + m1 Iy) + m2 Iz`; rot_change += `(r x I_core) x 1/inertia` (x = `l2 b - l1 c`, y = `l0 c - l2 a`, z = `l1 a - l0 b`, each `(cross x inv) + old`); speed_change += `inv_mass x world impulse`.

**0x10076b50**: +1 >= 8, or `f32(t - t_psi) == 0` exactly (`lahf; test ah,0x44; jnp`): rows (+0x60) and pos_now (+0x90); else 0x1006ca90's quaternion in packed form (same sums), its rows, `delta x dt + pos`.

**Static branch (0x100839f9)**:
1. The other's core (+1 >= 8: return); its pos_now in the static object's axes (cache 0x10001b50: `(m1 py + m0 px) + m2 pz` per column).
2. The synapse's ledge (`(edge & ~0xf) - (tri index + 1) x 16`); each triangle: corners A, B, C (edges 0, 1, 2's start points), `b = B - A`, `c = C - A`, `q = (by cz - bz cy, bz cx - bx cz, bx cy - by cx)`, `off = -((A.y qy + qx A.x) + qz A.z)`, `i = 1 / sqrtss((qy qy + qx qx) + qz qz)`, `dist = ((l1 qy i + l0 qx i) + l2 qz i) + off i`; the largest (> -1e20; (1, 0, 0) without triangles) gives n.
3. n in world axes (`(r.y ny + nx r.x) + r.z nz`); `v = ((delta.y + sc.y) n1 + (delta.x + sc.x) n0) + (delta.z + sc.z) n2` (+0xf0, +0xb0); `speed x 0.1 > v`: 0x10075060 and speed_change += n x speed.

## Rules one kart never showed

- Cache renew (0x10099850, 0x10001b50): only an object with +0x44 < 8 has its cache renewed when older than the time code; a frozen one (8) or one in its revival's recheck (0x21) keeps its cache. A new cache (0x1006ccb0: a ring of slots, the next with no users, its old owner's +0x40 cleared; +0x60 = 0) is updated at once only when +0x44 > 7.
- Stage 3's order (0x10097d00): moved cores from the last, each core's objects last first, into the due list.
- insert_hull_mindist 0x100960d0's "moving" is object +0x44 & 7 (a frozen body's 8 isn't).
- The revival's collision side runs in stage 1, with the caches as stage 1 finds them.

## Unread

- A friction system split down to one core (0x100816a0's end); a body destroyed out of a unit of several cores.
- 0x10086b70 / 0x10082ce0 answering 1.
- A rescue push from stages 5-6.
- The server's ShouldSolvePenetration timer (0x102f78a0).
- The cache ring's evictions.
