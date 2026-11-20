# IVP's contacts: the friction system, its contact points, the impacts (CS:GO legacy vphysics.dll, 2026-11-17)

**CS:GO legacy, not CS2** (ze_crazykart's karts, docs/CRAZYKART.md; the free body is crazykart-physics.md 8-11).
vphysics.dll md5 d97cf2194594d7545427cdabc7376db4, Ghidra `/csgo_vphysics_legacy.dll`. All SSE scalar single
unless said; the sum orders are in the Rust (sim/src/ivp/contact.rs, friction.rs, friction_energy.rs), transcribed
from the disassembly (float add and multiply are commutative bit for bit, so only the grouping matters, and the
grouping is what the Rust keeps). Names in IVP's terms are guesses from the leaked IVP source's vocabulary; the
addresses are the truth.

## 1. The probes (rubikon/tests/KartOracle: Probes.cs, Contacts.cs, ContactProbes.cs)

The oracle now breaks inside the running vphysics.dll: `Probes.OnEnter(va, f)` puts an int3 at a function's entry,
a vectored exception handler (first in the chain) runs `f` with the thread's registers (ecx = this, the stack's
arguments, xmm lanes, st(0)), restores the byte, single-steps the instruction (TF) and re-arms it;
`Probes.OnReturn(ctx, f)` arms the call's return address once. vphysics' .text (base + 0x1000, 0xd7000 bytes) is made
writable once. Every breakpoint is disarmed before the runtime shuts down (a late hit asserts in the CLR).

- `KART_ORACLE_COVER=a-b`: every function entry (16-aligned after int3 padding, a plausible first byte, not an address
  that looks like a jump table) is counted per tick from tick a to b into `<out>.cover`. This is how the touchdown's
  and a resting PSI's function sets below were found (flat-drive: the kart lands at tick 8).
- `KART_ORACLE_PROBES=1`: the contact probes write lines into `<out>.raw` (below), which
  `cargo run --release -p ze-sim --bin ivp_contacts_check -- <out>.raw` replays through the port, each call in
  isolation from the DLL's own inputs, every output word compared bit for bit.

Every tick the `.raw` also gets the kart's friction system as `fs`, `cp` and `pair` lines (raw words).

### The oracle's lines

| Line | Where | Blocks |
|---|---|---|
| `ledge <id> <tris> <points>` | first sight of a compact ledge | `head` (16 bytes), `tris` (16 bytes each), `points` (16 bytes each, up to the highest index a triangle names) |
| `cprecalc <tick>` | 0x1008d230 return | `cp_in` / `cp_out` (0x88 bytes), `lt` (0xe0), `e0` / `e1` (ledge id, triangle, slot), `cache0` / `cache1` (0x68), `obj0` / `obj1` (0xa4), `core0` / `core1` (0x1b0), `env_t` (f64), `set` (0x1010d23c / 0x1010d240) |
| `fs2000_in` / `_out` | 0x10082e70 entry / return | `n` (contacts, pairs), `es` (dt, 1/dt, the unit's flags), `env` (time lo hi, +0x118), per contact `cpN` `ltN` `coresN`, per pair `pairN` `cpsN` `pcoresN`, per core `coreN` |
| `fs600_in` / `_out` | 0x10082ff0 entry / return | as above |
| `cpnew <tick>` | 0x1007ec20 return | `md` (the mindist +0..+0x60), `ea` / `eb` (its synapses' edges), `cores` (ab / ba), `cp` (0xa0), `set` |
| `cpmass <tick>` | 0x10082a60 return | `cp_in`, `cp_out`, `lt`, `core0`, `core1` |
| `fssolve_in` / `_out` | 0x100a0b30 entry / return | as fs2000, plus `envx` (env +0xa8, +0xac, +0xc0), `perf` (the performance settings), `mset` (0x1010d23c..0x1010d25c), `fsx` (the system +0x3c..+0x44), `allcores` / `dyncores` (its core lists), `idN` (each contact's address), `coreptrN` (each core's) |
| `impact_in` / `_out` | 0x1008b0e0 entry / return | `rescue` (xmm2), `lt`, `cp` (0xa0), `core0` / `core1` (the objects' cores), `set` (in only); recorded, not checked yet: flat-drive has 13 (ticks 8, 45, 51, 52, 322) |
| `call <tick> <va>` | KART_ORACLE_CALLS=<va>,... | one line per call |

**Checked (flat-drive.txt, 400 ticks)**: 1230 cprecalc, 330 fs2000, 330 fs600, 330 fssolve (114 direct, 216
complementarity), 9 cpnew, 9 cpmass, and the DLL's atanf over 4,452,341 arguments (`fn` lines): 0 differ.

`KART_ORACLE_FN=<va>:<x,x...|sweep>` (with `KART_ORACLE_FN_OUT=<file>`) runs one of the DLL's SSE2 libm functions
(xmm0 in and out) on the arguments and writes `fn <va> x: <bits> r: <bits>` lines (sweep: every 1021st finite float
of both signs and every 64th in [0.5, 2]).

## 2. The structures

**IVP_Friction_System** (0x4c bytes, ctor 0x10086de0; three controller faces):
+0 vtable 0x100f1cc8 (the priority-600 controller: slot 4 0x10082ff0, slot 5 priority 0x10086480 = 600, slot 6 name
0x10086470 "sys:friction"), +4 the environment, +8 vtable 0x100f1d10 (priority 0: slot 4 0x10082f60, slot 5
0x10003fc0 = 0) with +0xc = the system, +0x10 vtable 0x100f1cf0 (priority 2000: slot 4 0x10082e70, slot 5 0x10086460
= 2000) with +0x14 = the system; +0x20 the contact list's head; +0x24 / +0x26 shorts; +0x28 / +0x2c / +0x30 vectors
(the objects / cores in it, TODO(trace)); +0x34 / +0x36 / +0x38 the core pairs (count at +0x36, array at +0x38); +0x3c
/ +0x3e shorts (+0x3e the contact count); +0x44 a byte (1 = the system may split: 0x10082f60 then 0x100815a0 /
0x100816a0). The unit runs its controllers from the last entry (crazykart-physics.md 10): the kart resting is
[0x100f1d10 (0), drag 500, motion 500..., 0x100f1cc8 (600), gravity 1000, 0x100f1cf0 (2000)], so a PSI runs the
geometry and energy first, then gravity (which commits the pending pushes), the tangential friction, the motion
controllers, drag, and last the normal-pressure solve.

**IVP_Contact_Point** (0xa0 bytes, new + ctor 0x1007ec20; contact.rs ContactPoint): +0 next, +4 prev (the system's
list), +8 / +0x1c the two synapses (IVP_Synapse_Friction, 0x14 bytes: +0 / +4 the object's friction-synapse list
(object +0x28 the head), +8 the object, +0xc (short) the back offset to the contact, +0xe (short) the feature: 0 point,
1 edge, 2 face, 3 ball, +0x10 the compact edge), +0x30 the spring's inverse mass, +0x34 (byte) 1 = sliding, +0x38
the spring's stretch (2 floats, along the long-term info's tangents), +0x40 this PSI's long-term info, +0x44 mu,
+0x48 the energy cut off the spring, +0x4c a face's 1 / |normal| (the ctor writes it only when the sorted synapse 1
is a face, 0x1007ed78, and clears nothing else there: any other contact keeps the reused block's old word, read by
nothing; world-hub's edge-edge contacts at tick 45 carry 0x3ee5a011 from a freed one), +0x50 the static friction's energy, +0x54 the normal
pressure, +0x58 the gap, +0x5c (byte, 0x14 at the creation), +0x5d (byte) 1 = re-test the features, +0x5e (short),
+0x60 (f64) the time of the last geometry, +0x70 the last contact point, +0x7c / +0x80 / +0x84 the last normal's z /
x / y, +0x90 the friction system.

**IVP_Impact_Solver_Long_Term** (0xe0 bytes from the environment's temporary memory env+0xa0, 0x1006dc70, a new
block every PSI; contact.rs LongTerm): +0 the contact point (world, on object 0's surface), +0x10 the surface normal
(world, object 0 -> 1), +0x30 / +0x34 the objects, +0x38 / +0x3c the edges, +0x40 the materials (0x1008af60), +0x52
(4 bytes) / +0x56 (short: 1 = the closest features left), +0x60 the elasticity (the material manager's slot 3,
0x1008afc0), +0x68 1 / the inverse virtual mass, +0x6c the inverse virtual mass along the normal, +0x70 / +0x74 the
dynamic cores (0 when static), +0x80 / +0x90 the two tangents, +0xa0 / +0xb0 the point in each core's axes from its
centre, +0xc0 / +0xd0 r x the normal in each core's axes.

**IVP_Friction_Core_Pair** (friction.rs Pair): +2 the contact count, +4 the contacts, +0x20 the countdown (reloaded
5), +0x28 / +0x2c (TODO), +0x30 the springs' energy, +0x34 / +0x38 the two cores.

**IVP_Core** fields the contacts read beyond crazykart-physics.md 10: +0xc the environment, +0x10 the inertia, +0x1c
the mass, +0x48 car_wheel (a car's wheel: 0x1007f300's own static friction and 0x100820b0's skip; never set on a prop,
so the port has no wheels), +0x4c the core's friction info.

**IVP_Cache_Object** (object +0x40, made by 0x1006ccb0 from the environment's cache manager env+0x90, refreshed by
0x1006cd90 when its stamp +0x60 is behind env+0x108 and the object +0x44 < 8): +0x20 / +0x30 / +0x40 the rows of the
object -> world rotation, +0x50 the position, +0x60 the stamp, +0x64 the users. One model with the mindists' (cache.rs,
ivp-mindist.md 3; 0x1006cd90 ported there).

**IVP_Compact_Ledge** (ledge.rs, shared with the mindists; an edge is a dword index into its words): +0 the points' offset, +0xc (short) the triangles; triangles of 16 bytes after the
header (+0 the triangle index in the low 12 bits; three edges: start point index (16 bits), opposite (15 bits,
signed, in edges), virtual (1 bit)); an edge's next / previous in its triangle by the tables 0x1010a988 / 0x1010a998
(+4 +4 -8 / +8 -4 -4 bytes by the edge's address & 0xc). The ledge of an edge: (edge & ~0xf) - ((tri index + 1) x 16).

**IVP_Mindist_Settings** (globals 0x1010d130..0x1010d260, set by 0x10093d30(tolerance xmm1, gravity xmm2) from the
environment's ctor 0x10013090 and SetGravity 0x10013a70; ivp-mindist's): 0x1010d23c the collision distance (a new
contact's gap), 0x1010d240 the friction distance (tolerance x 0.3 past it), 0x1010d258 2 x tolerance (the impact's
rescue, 0x10089a50). The oracle's: 0x3c4ffe5a, 0x3c6f314e.

## 3. A contact's geometry each PSI: 0x1008d230 (ivp_mindist_friction.cxx; contact.rs `recalc`)

thiscall (cp, env): a new long-term info (zeroed normal, +0x52..+0x57 zero; env+0x84 += 1), both objects' caches
(made or refreshed), then by the features: synapse 0 a point (its edge's start through cache 0, `Cache::to_world`:
per row ((r0 p0 + r1 p1) + r2 p2) + t) or a ball (cache 0's position, +0x5d = 1), against synapse 1's
point **0x1008c2e0** (the normal p1 - p0 normalised, gap n2 x (1 / sqrt(n2)) (not sqrt), a tangent from the x or y
axis by 0.9 > d0^2), edge **0x1008c490** (gap |q x e| / |e|, the normal (q x e) x e normalised, the feature test
(q.e) / |e|^2 in [0, 1]), face **0x1008bd50** (the point into the face's object axes, the barycentric test with
FLT_MIN added (any sign bit: left), the normal (Q - P) x (R - P) x +0x4c through the cache, negated; gap n.p - n.P;
the tangent the edge Q - P) or ball (point-point with its centre); synapse 0 an edge: **0x1008c850** (both edges'
world ends, unit directions a, b, c = a x b; |c|^2 <= 1e-10, |e.R - e.S| or |f.P - f.Q| < 1e-10: parallel (left, gap =
the friction distance 0x1010d240, normal x, tangent y); else the closest points' parameters s, t, gap |D - C| (or 0
with the normal c / |c| below 1e-10), the tangent a; the feature test s, t in [0, 1]). An unknown feature: IVP Failed
at lines 0x1ba / 0x1c4. Then the point onto object 0's surface (+ radius x normal: object +0x90), the gap less both
radii (>= 0), the first tangent normalised (past 1e-10), the second normal x first, per dynamic core (flags & 2 clear)
its lever r = M^T (p - pos), the normal's lever r x M^T n, the inverse virtual mass ((iI1 c1) c1 + (iI0 c0) c0) +
(iI2 c2) c2 + 1/m, the point's speed M (w x r) + v (core 1's subtracted, its mass term added after core 0's), +0x68 =
1 / +0x6c; dt = f32(env time - cp+0x60), cp+0x60 = env time; the spring moves back by (tangent . speed) dt; +0x70..
the point and normal kept.

## 4. The friction system's controllers

**Priority 2000, 0x10082e70** (friction_energy.rs): one contact: 0x1008d230 only. Else **0x10086f10** (per pair last
to first, its contacts last to first: the geometry, and (old gap - new gap) x pressure summed into the pair's energy
when positive), then the unit's flags (the event's +0xc: the simulation unit): & 0x3000 (resting) zero every pair's
energy (0x10082130); & 0xc00 clear: **0x100820b0** per pair last to first: energy x env+0x118 (0.9^dt); unless
negative (or a car wheel's), **0x100826d0** takes min(a tenth of the removable energy, the pair's) out of the two
cores' relative motion by pushes into their pending changes (speed_change / rot_change: gravity at 1000 commits them
this PSI); env+0x40 += the energy taken (a statistic, not kept); the pair's energy less it. **0x100821a0** builds the
relative motion (c0 the static core when either is (flags & 0x12), its masses then the other's x 10000 / x 1e-4): the
speed difference's direction and length, the rot speed difference in world (M w per core) as directions in each
core's axes, |I x dir| per core. On flat-drive the unit's flags were 0x401 (228 PSIs), 0x1 (98), 0x1001 (4).

**Priority 600, 0x10082ff0** (friction.rs `tangential`): one contact: the spring cut to (((mu pressure) +0x30) dt) dt
(the cut energy into +0x48, +0x5d = 1), then the static friction. Else per pair last to first **0x10080720**: the
longest spring **0x10080630** (dt x sum over the pair's contacts last to first of (pressure mu) +0x30) x dt, each
contact's spring cut to it, then its static friction (sliding contacts: 0x1007fd70, unreachable in
vphysics: 7), the positive sum of the energy changes into the pair's energy; then **0x10080e20**: each pair's
countdown, at 0 **0x10080840** (the springs of contacts with |(|n_i . n_j| - 1)| < 0.001 shared along the line
between them: each pair's projections averaged, the corrections / n into per-contact sums, added back to the springs
through their tangents) and 5 again.

**Static friction 0x1007fb40** (friction.rs `static_friction`): the most the friction can push is (pressure mu) dt
(below 1e-6: nothing); a car wheel's path 0x1007f300 aside, **0x1009c010** (IVP_Solver_Core_Reaction: the
response at the contact point along the two tangents; per dynamic core **0x1009b4e0**: its levers M^T (d x dir), x
1/I, the matrix's diagonal ((r1 c1 + r0 c0) + r2 c2) + 1/m and the earlier directions' cross terms without the mass,
the directions' speeds (dir.v + lever.w) weighed +1 / -1); the 2x2 solve for the push that brings the spring's
speed to stretch / dt (det below 1e-10 squared: nothing), clamped to the most; **0x1009c0c0** pushes straight into the
cores' speeds (not the pending changes); returns the new spring energy sqrt(|s|^2 (dt |i|^2) dt) / 2 less the old.

**Priority 0, 0x10082f60** (solver.rs `pressure_controller`): one contact **0x10082ed0** (its normal speed 0x1007e990,
the push x = ((k (coll_dist - gap)) + speed) x the virtual mass +0x68, k = 20 past the collision distance, straight
into the speeds when positive (0x1007ea80, no clamp), the pressure x / dt; the contact removed past 0x1010d24c or
when its features left), else **0x100a0b30**; then a system without contacts deletes itself (slot 7: the caller's,
`After::Empty`), or, its +0x44 set, may split (0x100815a0 / 0x100816a0: TODO(port), `After::MaySplit`) and marks the
unit (flags & ~0x200 | 0x100). The one-contact path never ran on flat-drive (not checked).

## 5. The normal pressures: 0x100a0b30 (ported: solver.rs, lcs.rs; 2026-11-17)

Every function below is transcribed from its disassembly; **checked**: flat-drive's 330 solves (fssolve_in / _out:
every contact's fields, the order of the list, both cores' speeds, rot speeds and pending changes) bit-identical, 114
by the direct solve and 216 by the complementarity solve (the same split as the DLL's).

1. **0x100a09a0**: the list sorted by +0x5e ascending (an insertion sort that moves past strictly greater ones: the
   stable order). **0x100a08e0**: per contact (the next taken first) gap >= 0x1010d24c (tolerance x 2.5 + coll_dist)
   or the features left (lt +0x56 == 1): **0x100810a0** delete_friction_distance (both cores' movement references'
   times = now, out of the list, out of its pair (0x10086fb0: the pair searched last to first, the contact out by
   0x10018430 which keeps the order; an empty pair goes and +0x44 = 1), out of both cores' friction infos, a core left
   without any leaves the system (0x10087270) and its unit is marked, the contact's dtor 0x10080e60); gap > tolerance x
   0.01 + coll_dist between two cores both flagged 1: the contact to the head; +0x40 = 0.
2. **0x10080fe0** the solver (n = contacts - +0x40, rows aligned to 4, the env's temporary memory); **0x100a0370** its
   entries in list order (the long-term infos: +0x50 the index, +0x58 / +0x5c the cores' friction infos for this system,
   +0x60 = (i32) +0x5e, +0x64 the gap); **0x100a0580** with **0x100a0470**: row j, column i = contact j's normal speed
   for a unit push at i (per dynamic core of i: its response -(rn x 1/I), -(n / m) for core 0, + for core 1, dotted
   with j's lever and normal, sign -1 when it is j's core 0; ((rn1 a1 + rn0 a0) + rn2 a2) + ((n1 l1 + n0 l0) + n2 l2));
   b_i = k (coll_dist - gap) + normal speed; the flagged list (+0x5e != 0).
3. **0x100a0060**: **0x1009fe20** (the diagonal's maxss chain from the last row in groups of 4, the scale 1 / max
   unless <= 1e-10, |b|'s max likewise; rows x the first, b x the second's inverse, +0x18 = the product); the result
   zeroed; **0x1009cb60** the flagged rows and columns (a prefix 0..n-1 copies whole rows); **0x1009c880** Gauss (the
   pivot: the largest |a_rk| from the last row up, strictly greater; rows below eps 1e-9 left; row_i += row_k x (a_ik x
   -1 / a_kk)); **0x1009c980** back substitution (from the last column down; a pivot below eps: 0 when |s| < 1000 eps,
   else failure); **0x1009fcb0**: the answer into the result, failure when env+0xc0 x 0.01 > x scale x lt +0x6c for a
   flagged contact or an unflagged one's row . x + |b x 1e-5| < b (**0x1009c5b0**: ascending sum, two 4-lane sums from
   8 entries). Failed: **0x1009d270** with the contacts at the head whose +0x5e < 0 active at the start; its failure
   means no pushes this PSI.
4. **0x1009fd90** x scale; the energy **0x100a0c20** (per system core last to first: ((v0^2 + v1^2) + v2^2) m +
   ((I1 w1^2 + w0^2 I0) + I2 w2^2), halved, with the pending changes); **0x100a02a0** per contact: x > 0 pushes
   (**0x1009fb00**: into the cores' pending changes, each core clamped by 0x10078650) and counts +0x5e down (from -1);
   x == 0: +0x5e = 0; x < 0 (or NaN) pushes too (a pull) and counts +0x5e up (from 0, back to 0 past 9); the pressure
   +0x54 = 1/dt x max(x, 0); the energy again and **0x100a0d70** (per dynamic core (perf +0x18 against its mass) x
   env+0xc0 x 0.1); more energy than the allowance: the undo 0x100a0d10 (TODO(port): never on flat-drive, panics),
   else every dynamic core of the system (+0x2c list, last to first) commits (0x10077520).

**The complementarity solve 0x1009d270** (IVP_Linear_Constraint_Solver, lcs.rs). Fields: +0 eps 1e-7, +8 the check
tolerance 1e-4, +0xc the step limit 1e4, +0x10 A, +0x14 b, +0x1c x, +0x20 dx, +0x24 w (= -b at the start), +0x28 dw,
+0x2c / +0x30 a start x and its w, +0x18 (= +0x88) the residual, +0x34 / +0x38 the order and its inverse, +0x3c n,
+0x40 n aligned, +0x44 the actives, +0x4c the first unhandled, +0x50..+0x64 counters (+0x58 / +0x5c / +0x60 / +0x64
the perturbation's), +0x68 the factorisation's state (0 valid, 1 stale, 2 broken), +0x6c the inverse manager (+0 eps
1e-6, +4 the inverse, +8 U, +0x14 b, +0x18 x, +0x1c / +0x20 scratch, +0x24 stride, +0x28 size), +0x98 / +0xb0 / +0xc8
/ +0xe0 great matrices (+0x98: the actives' Gauss with eps 1e-7; +0xb0: A with dx / dw).
- **0x1009df60** the start: the first n_active active and handled; their factorisation (**0x1009dda0**: U from the
  actives' rows and columns, b, then **0x1009f270**); solved (**0x1009f9a0**: the inverse x b (sums from the last
  entry, 0x1009c4f0), then **0x1009f870**'s back substitution through U); x / w from it (**0x1009dec0**: w = A x - b
  by 0x1009cd00, the actives' 0); an active with x < 0 leaves (0x1009dae0 swap, 0x1009f660) and the solve repeats;
  a broken factorisation or a failed setup starts from nothing.
- **0x1009d630** the pivoting (a transcribed state machine: `Lcs::run`): at most 250 steps (counted when a move
  happened, and on each restart); every 7 steps **0x1009d0b0** (the residual A x - b against 0 for the actives and w
  for the others, 1e-4) or a restart; the next unhandled variable: |w| < eps (and |x| < eps: handled at 0; else it
  enters the actives), w >= 0: handled at 0, w < 0: **0x1009dbc0** the actives' move for a unit step (from the
  factorisation, or Gauss when it is stale: +0x54 counts), dx[var] = 1, **0x1009cfa0** dw for the others, the ratio
  test (the variable's own w / dw unless 1e4 dw <= -w (then 1e20), each active with dx < -eps (an immediate stop
  when its step is below eps and x < eps), each handled one with dw < -eps, eps slack each way), the step maxss 0,
  past 1e4 or more than n/2 + 2 tiny steps in a row: a restart; **0x1009db20** the step (w, x += step x dw, dx; the
  handled ones' w and the actives' x kept >= 0); the stop leaves the actives (**0x1009f660**), joins them (after
  **0x1009d5b0** dropped actives below eps, **0x1009d430** / **0x1009f3e0** grow the factorisation), or is the
  variable itself (it joins and is handled). A stale factorisation is rebuilt (**0x1009d4e0** the perturbation: two
  swaps among the actives by counters stepping 1 and 2 mod their count, two among the unhandled likewise; then
  0x1009dda0) after a move.
- **0x1009e0d0** the restart: the factorisation from the actives (after the perturbation), or the actives sorted by
  x (**0x1009de10**, greatest first) and solved by Gauss; x / w from it; **0x1009e250** sends actives below eps to the
  handled ones (x 0) or, negative, to the end (counted: a positive count repeats the restart), and handled ones with
  w < 0 to the end.
- The factorisation (inverse manager): **0x1009f270** Gauss with pivoting on U and the identity (**0x1009ef30** row
  swaps, **0x1009ee60** a row over its pivot (eps 1e-6: failure), **0x1009f050** a row less f x another, U[i][k] =
  0), only below the diagonal; **0x1009f3e0** adds a row and column (the new column = inverse x the active column,
  the new row eliminated against every earlier one, then normalised); **0x1009f660** removes one (columns k and last
  swapped in both, the inverse's rows fixed by **0x1009fa50**, the pivot re-normalised or patched, the last row
  eliminated, its inverse row normalised (failure below eps) and cleared from the others by **0x1009f1b0**). The row
  operations keep the DLL's column groups: a U row from (k + 1)'s 4-aligned group, an inverse row whole, so the zeros
  below the diagonal keep their signs.

The direct-path and complementarity results reach the system through the same pushes (step 4).

## 6. The impacts (0x1008b0e0 and below ported: impact.rs; the impact system above it traced at the call level)

**Checked (2026-11-17)**: flat-drive's 13 impacts (impact_in / _out: the long-term info, the contact, both cores, the
mindist / performance settings in; both cores' speeds, rot speeds, pending changes and flags word, lt +0x20 out)
bit-identical, and their materials (mu 0x3f23d70b, e 0x3d800000) as the products of the two defaults.

Ported from the disassembly: **0x1008b0e0** (the cores in order, a static one first, the normal then negated; the
cone below), **0x10089a50** (the eased elasticity, the rescue speed, the speeds with their pending changes, rel,
the responses, the first push q = (((-rel.n) 2 vm1) / (vm0 + vm1)) vm0 0.1; separating: 0x100890a0 along -n with
the minss; closing: up to 100 rounds of push q / rel / direction while closing, then along -n a unit push, the
elastic one (tot / (rel.n + s) past 1e-4) after undoing it, and 0x100890a0 along -n), **0x100890a0** (the speed
along -d of the point less the rescue speed over both cores' response along it + 1e-15 (0x26901d7d), pushed as the
last push), **0x1008a2c0** (the cores' impact counters (flags' upper half) up unless static; with +0xc set, the core
with the larger 1 / response checked by **0x10076570** against the other's new speeds (-0.8333333 x rescue): it then
keeps its old speeds and takes the push as pending changes (**0x1008a4d0**), the other gets its speeds
(**0x10088f10**), else both do; **0x1008a570** clears both cores' pending changes first). Not ported: the env+0x20
hooks (speed limits, impacts past perf +0xc: they panic), a core already in this PSI's impact list (flags & 0xc0:
0x1008a0b2, panics), the sliding variants (1008b820 / 10088cc0 / libm 0x100d7a68). **0x1008af60** the materials'
fetch (contact.rs `tri_material`: the triangle's byte 3 & 0x7f, else the object's +0x88) and the products
(`friction_factor` / `elasticity`). The impact system above (0x1008ac60, 0x1008b590, 0x1008b2c0..0x1008b4c0,
0x1008aed0) and the friction system's creation from a mindist (0x10088450): ported 2026-11-17, ivp-impact.md.

**The friction angle**: 0x1008b0e0 takes atan(mu (1 + sqrt(e))) through the DLL's statically linked SSE2 atanf
**0x100d7e25** (ported: sim/src/math/csgo_atan.rs, tables 0x100fbee8 / 0x100fc480 / 0x100fc488 by the scratch script
atantab.py into csgo_atan_tables.rs: |x| in [2^-5, 2^64) c = |x| cut to 4 mantissa bits (or 0x0000800000000000,
min 64), t = (|x| - c) / (1 + |x| c), (atan(c) + t) + t^2 (-t/3) in f64; below 2^-5 the f32 x + (x^4 (0.2 x) +
(-x/3) x^2); below 2^-64 x; past 2^64 +-(7.5497894e-8 + 1.5707963); NaN / infinity 0x100d7fae unread), then
cos = (1 - a^2 / 2) + (a^2 / 24) a^2 and sin = cos x tan. The impact solver itself (0x10089a50 and below) is read
below to the call level and partly to the instruction (10088850 the relative speed at the point, 10088a70 the push
direction clamped into the friction cone, 1008a990 the cores' 1 / |response|, 1008a600 a push along the direction,
10088fb0 the pushes undone, 1008a2c0 the write-back): TODO(port) with 100890a0, 1008a2c0's 10076570 / 1008a570 /
10088f10 / 1008a4d0, and the sliding variants 1008b820 / 10088cc0 (another libm call 0x100d7a68).

There is no "ivp_impact.cxx" in the DLL's IVP Failed strings (its asserts are compiled out). The impact runs where a
mindist reports a collision (ivp-mindist's side: 0x100b14f0 -> 0x1008b020 -> **0x1008ac60**), at flat-drive's
touchdown (tick 8): 0x1008ac60 x3, 0x1008b0e0 x5, 0x10089a50 x5, 0x100890a0 x5, 0x1008a2c0 x5, 0x1008a570 x5,
0x1008a990 x5, 0x10088850 x41, 0x10088a70 x36, 0x10088f10 x10, 0x10088fb0 x5, 0x1008a600 x41, 0x1008b590 x5,
0x1008b2c0 / 0x1008b380 / 0x1008b4c0 x3, 0x1008aed0 x3, 0x1008afc0 x3, the material manager's get_friction_factor
0x10018970 x6 and get_elasticity 0x10018a20 x6 (crazykart-physics.md 3: mu 0.64, e 0.0625), 0x10026f60 x6 (the
player controller's override test).
- **0x10088450** (IVP_Mindist::try_to_generate_managed_friction): the contact from the mindist (**0x1008df50**: only
  a mindist whose status (+0x14 bits 18-21) is 3; an existing contact found by 0x1008def0, else new 0xa0 + 0x1007ec20),
  its geometry (0x1008d230) and materials (0x1008afc0), then the friction system: the object's (+0x4c) or a new one
  (new 0x4c + 0x10086de0), the contact linked at the head (+0x20, +0x3e += 1), 0x100870c0 (the pairs), 0x100871f0 (the
  objects), 0x100871c0; two systems merged (0x10078860 / 0x100713b0 / 0x10071800 / 0x100718e0 / 0x10071aa0: the
  simulation units). Ran x3 at the touchdown (the three contacts), again at 45, 51, 52 (a fourth contact comes and
  goes) and 322 (the landing after the jump).
- **0x1008b0e0** (IVP_Impact_Solver_Long_Term::do_impact_long_term(cores, rescue speed, cp)): the cores in order (a
  static one second), the elasticity (+0x60), with both cores without a car wheel a rotation of the impact (sqrt and
  0x100d7e25: a CRT call, then 1 - x^2/2 + x^4/24) and 0x1008b820 when the contact's +0x34; then **0x10089a50**
  (IVP_Impact_Solver::do_impact: the elasticity eased by the impact count n (1 - (1 - e) / (n/2 + 1)), the rescue speed
  (0x1010d258 + arg) x 1.2, both cores' speeds and pending changes summed, the relative speed along the normal; below
  -0.0001 an iterative impact (0x10088a70 / 0x1008a600 / 0x10088850, at most 100 rounds), else the separating push
  0x100890a0 and, past 10 impacts, no more friction).
- The impact system around them (0x1008b590 / 0x1008ac60's queue, 0x1008b2c0..0x1008b4c0): ivp-impact.md 2-5.

**IVP_Impact_Solver as read (0x140 bytes on 0x1008b0e0's stack)**: +0 rescue x 1.2 ((0x1010d258 + the rescue
speed) x 1.2), +4 / +8 each core's 1 / |response to a unit push| (1008a990; a static core: the other's x 1e5), +0xc 1
(0 after 10 impacts of a separating contact), +0x1c / +0x20 the cores' rows (core +0x60), +0x30 / +0x40 the rot
speeds with their pending changes, +0x50 / +0x60 the speeds likewise, +0x70 / +0x80 and +0x90 / +0xa0 the last push's
rot / speed change per core, +0xb0 the relative speed at the point, +0xc0 the push direction, +0xd0 a second
direction (sliding), +0xe0 the sliding flag (1008b820), +0x100 / +0x104 the cores (a static core first: 0x1008b0e0
swaps so +0x104 is dynamic, the normal then negated), +0x108 / +0x10c their levers (lt +0xa0 / +0xb0), +0x110 the
elasticity (lt +0x60), +0x114 / +0x118 the cone's cos / sin, +0x11c the normal, +0x120 lt +0x20 (gets the relative
speed).
- **10088850**: rel = (v1 + M1 (w1 x r1)) - (v0 + M0 (w0 x r0)), each M row ((a0 + a1) + a2).
- **10088a70**: the direction = rel normalised (past 1e-10); along the normal (d > 0): the second direction instead;
  else, unless sliding (10088cc0: TODO), inside the cone (d > -cos): the tangent t = dir + n (-d) normalised, then
  dir = n (-cos) + t sin.
- **1008a990**: per core (core 1 with +n, core 0 with -n): 1 / |M ((r x M^T n) x 1/I x r) + n / m| (pinned: 1).
- **1008a600** (xmm1 = s): p = dir s; core 0 (unless static): its rot change += 1/I (r x M^T p), its speed change +=
  p / m; core 1 with -p (computed as p x -1): 1/I (l x r) with l = M^T(-p).
- **10088fb0**: the last push undone (rot / speed minus +0x70.. / +0x90..) for the dynamic cores.
- **10089a50**: e' = 1 - (1 - e) / (n / 2 + 1) (n = lt +0x52, the impacts so far), the speeds gathered, rel
  (10088850), lt +0x20 = rel, the responses (1008a990), the rel's normal part; separating (> -1e-4): the push 100890a0
  along -n with flag 1; else the direction (10088a70), up to 100 rounds of push / rel / direction while the rel's
  normal speed stays > 0, then a final elastic push (10088fb0, 1008a600 by the speed over the normal part) and 100890a0
  along the direction; the speed / rot speed limits (env+0x20 hooks: never on the kart); 1008a2c0 writes back: the
  pushes into the cores' pending changes and the cores' counters (+2), a core already in this PSI's impact list
  (flags & 0xc0) moves its speeds into the changes (the double buffer of the impact system, 1008b590).

## 7. The materials

`get_friction_factor` 0x10018970 / `get_elasticity` 0x10018a20 (crazykart-physics.md 3), called through the
environment's material manager (env+0x98, slots 2 / 3) by 0x1008afc0 once per new contact: mu into the contact's
+0x44, e into the long-term info's +0x60. 0x10082a60's sliding switch reads each material's +8 (0x1008af60 fetches
the two). The kart ("none" -> default, friction 0.8) on a default box: mu 0x3f23d70b (0.64). Ported per side
(friction_sys.rs cp_materials, 2026-11-17): a triangle's material index (byte 3 & 0x7f) through the world's table
(Collide::materials: SetWorldMaterialIndexTable, crazykart-physics.md 14), else the object's own (+0x88, Obj::material);
world-hub's contacts on "sand" (e = 0.25 x 0.01) checked.

**No contact ever slides (read 2026-11-17).** IVP's material (vtable 0x100e218c, vphysics' subclass 0x100e2154; slot
1 the friction factor) is the first 0x10 bytes of each 0xac-byte surfaceproperties entry (CPhysicsSurfaceProps +0x48,
count +0x54): +4 / +8 / +0xc, the data from +0x10. Every way an entry is made writes +8 = 0: the parser 0x10019180
(`local_d0 = 0` before each entry's keys, 0x10019215; no key writes it: "base" copies only from +0x10 on; the
fallback entry 0xf000 at 0x10019bcd: `local_17c = 0`), its insert 0x10019d30 (copies the local's +8) and the grow
0x10019ea0 (+8 = 0, +0xc = 0xffff). The manager's slot 1 (0x10019d00, vtable 0x100e20cc) hands out these entries
(the surface props' slot 0x2c), and an object's own material (+0x88) is the template's, which vphysics takes from
the same table (crazykart-physics.md 11, step 5). So 0x10082a60 never sets +0x34, and the sliding friction
0x1007fd70 and the sliding impacts 0x1008b820 / 0x10088cc0 never run in CS:GO: the port marks them unreachable
(friction.rs, impact.rs). A kart pushed sideways is the static friction's clamp (0x1007fb40, (pressure mu) dt):
scenario slide.txt (a shove at 600 in/s, a spin, a hard turn at full thrust, a shove while driving) runs it 1225
times in 700 ticks, bit-identical (flat-drive already ran it 756 times).

## 7a. The surface table and the world's material table (read 2026-11-17, ported: tools/kart-ivp-surfaces.mjs)

The bake makes ivp/materials.bin from the surface script itself now, not from the oracle's dump.
tools/kart-ivp-surfaces-check.mjs runs the port against the DLL (KartOracle `--surfaces`): 121 entries, every name's
GetSurfaceIndex and every index's four numbers, bit-identical. The 128-slot table equals the oracle's `# materials`
line (the bake's `--check`).

- **Tokenizer** 0x10002380 (ParseFile): skips bytes below 0x21, and the DLL reads a *signed* char, so 0x80-0xff count
  as whitespace too and end an unquoted word. `//` runs to the newline and `/* */` is a block comment. A quoted string
  runs to the next quote or to NUL. The break set comes from 0x10002300: `{}()':` (table 0x101166f8, since the flag
  0x1010f26d is never written; 0x101165f8 is the same set without the colon). A break character is a token of its own.
  Tokens are capped at 0x3ff bytes. **ParseKeyvalue** 0x10036220: the key, lowercased (__strlwr); a key equal to `}`
  (strcmp) leaves the value empty, and otherwise the value comes next, lowercased too. At the end of the text the
  pointer is null and the key is empty.
- **stricmp** 0x100b8a70: ASCII-only case folding.
- **ParseSurfaceData** 0x10019180 (slot 1; `this` is CPhysicsSurfaceProps, +0x48 entries, +0x54 count, entry size
  0xac, symbol at +0xc, data copied as 0x27 dwords from +0x10):
  1. A file name already in +0x5c (0x10018dd0) returns 0.
  2. Per top-level key whose value is `{` (strcmp with 0x100e1e3c), the name goes into the symbol table (0x100ba880,
     +8). The entry starts as a copy of GetSurfaceIndex(name) clamped to 0. Index 0 is the first entry, so a new name
     starts as a copy of "default", and while the list is empty it starts as zeros.
  3. Keys until `}` (0x100e1e40). `base` (0x100e1e44) copies the named entry when it is found; when it isn't, the DLL
     DevWarns and copies nothing. thickness +0x1c, density +0x18, elasticity +0x14, friction +0x10, each as
     `(float)atof`. The other keys (sound names via 0x1001a190, gamematerial, audio*, *occlusion, dampening +0x20,
     penetration / damage modifiers, ...) only write fields past +0x20.
  4. At `}`, GetSurfaceIndex(name): when it is < 0, the entry is inserted (0x10019d30) at the end. Otherwise it is
     overwritten in place, and an index past 0x7f other than 0xf000 lands on entry 0 (0x10019b57). If the text ends
     inside an entry, that entry is dropped (0x1001940f).
  5. After the first file only (+0x17c): the fallback entry 0xf000. It is a copy of entry 0 (0x10019130 copies an
     index's data from +0x10) with friction 0x3f4ccccd and elasticity 0x3a83126f, appended, and its index is kept at
     +0x180. Then a "default" that isn't index 0 gets a Warning ("Physics materials broken!").
- **GetSurfaceIndex** 0x10018e70 (slot 3): a name starting with `$` that stricmps equal to `$MATERIAL_INDEX_SHADOW`
  gives 0xf000. Otherwise the symbol's Find (0x1001a0c0), then a linear search of the entries' +0xc; a miss gives -1.
- **GetPhysicsProperties** 0x10018f50 (slot 4: index, density*, thickness*, friction*, elasticity*): 0xf000 maps to
  +0x180, and any other index >= 0x80 to 0. A negative or out-of-range index falls back to entry 0, and with no
  entries at all the outputs are left unwritten. It reads friction +0x10, elasticity +0x14, density +0x18, thickness
  +0x1c. Slot 2 0x10018dc0 is the count (+0x54).
- **The key parser** (VPhysicsKeyParserCreate 0x1000bad0: the text parser is 0x408 bytes, vtable 0x100e3cc0, +4 the
  text, +8 the block name):
  - NextBlock 0x10033800 reads keyvalues up to a value equal to `{` (strcmp), and that key becomes the block name.
  - SkipBlock is slot 9 (0x100337c0), which calls slot 7 ParseCustom 0x10035100 with no handler. That walks
    keyvalues and keeps a depth: a key or value whose first character is `{` is +1, a key starting with `}` is -1.
    Below 0 it calls NextBlock.
  - **ParseSurfaceTable** 0x10034130 (slot 6): keyvalues until a key starting with `}`, then NextBlock. Each key
    gives GetSurfaceIndex(key) (through the global props 0x10116078), and the value through atoi gives the slot.
    When the slot is < 0x80, `table[slot] = index`; a negative slot writes before the table (the port refuses it).

## 8. What the port expects of a mindist (for ivp-mindist)

`contact::FromMindist`: per synapse, in the mindist's order (mindist +0x14 bits 8-9 = which of the synapses at +0x28 /
+0x44 is first; the second is the other), the object's core (an index into the caller's cores, static ones included),
the feature (synapse +0xa, i16: 0 point, 1 edge, 2 face, 3 ball), the compact edge (synapse +4, as `ledge::Edge`:
the dword index into the object's `ledge::Ledge` words, 4 x triangle + 5 + slot), side 1's ledge, env+0xf0 and the mindist settings
(`MindistSettings`: 0x1010d23c, 0x1010d240). Only a mindist with status 3 (+0x14 bits 18-21) becomes a contact. Each
PSI the geometry needs per side `contact::Side`: the ledge, the object's cache (its world pose), the object's extra
radius (+0x90) and its core unless static.

## 9. Still unread (addresses)

The sliding friction 0x1007fd70 (unreachable: 7); the car wheel's static friction 0x1007f300; the undo 0x100a0d10 and the big-system
split 0x100a0ad0 of 5; the system's split / merge (0x100815a0, 0x100816a0, 0x10081280: read since, ivp-touch.md; 0x10082ce0's dynamic branch at
revival); the contact's dtor 0x10080e60; the pair's +0x2c. Read since (ivp-impact.md): the impact system, 0x10088450
with 0x100870c0 / 0x100871f0 / 0x100871c0, the removal's unit bookkeeping (0x10087270, 0x10071dc0), the pair's +0x28
(the last impact's time), the system's +0x24..+0x30 (its cores, all and dynamic), the cache refresh 0x1006cd90
(ivp-mindist.md 3).
