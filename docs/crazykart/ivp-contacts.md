# IVP contacts: the friction system, contact points, impacts, materials

CS:GO legacy vphysics.dll md5 d97cf2194594d7545427cdabc7376db4, Ghidra `/csgo_vphysics_legacy.dll` (ze_crazykart's
karts; the free body: crazykart-physics.md 8-11). All SSE scalar single unless said. Float add and multiply are
commutative bit for bit, so only the grouping matters; the groupings below are the disassembly's. Names are guesses from
the leaked IVP source's vocabulary; the addresses are the truth. vphysics' .text: base + 0x1000, 0xd7000 bytes.

## Functions

| Address | Module | What |
|---|---|---|
| 0x10086de0 | vphysics | IVP_Friction_System ctor (0x4c bytes) |
| 0x1007ec20 | vphysics | IVP_Contact_Point ctor (new 0xa0) |
| 0x1008d230 | vphysics | a contact's geometry each PSI (thiscall cp, env; ivp_mindist_friction.cxx) |
| 0x1008c2e0 / 0x1008c490 / 0x1008bd50 | vphysics | point against point / edge / face |
| 0x1008c850 | vphysics | edge against edge |
| 0x1006dc70 | vphysics | env temporary memory alloc (env+0xa0) |
| 0x1006ccb0 / 0x1006cd90 | vphysics | cache object make (env+0x90's manager) / refresh |
| 0x10093d30 | vphysics | mindist settings set (tolerance xmm1, gravity xmm2) |
| 0x10013090 / 0x10013a70 | vphysics | environment ctor / SetGravity (both call 0x10093d30) |
| 0x10082e70 | vphysics | friction controller priority 2000 (geometry + energy) |
| 0x10086f10 | vphysics | per pair: geometry, gap-change energy |
| 0x10082130 | vphysics | zero every pair's energy |
| 0x100820b0 | vphysics | per pair: energy damping and removal |
| 0x100826d0 | vphysics | takes energy out of the cores' relative motion |
| 0x100821a0 | vphysics | builds the relative motion |
| 0x10082ff0 | vphysics | friction controller priority 600 (tangential) |
| 0x10080720 | vphysics | per pair tangential friction |
| 0x10080630 | vphysics | the pair's longest spring |
| 0x10080e20 / 0x10080840 | vphysics | pair countdowns / spring sharing between parallel contacts |
| 0x1007fb40 | vphysics | static friction |
| 0x1007f300 | vphysics | car wheel's static friction (unread) |
| 0x1007fd70 | vphysics | sliding friction (unreachable in CS:GO) |
| 0x1009c010 | vphysics | IVP_Solver_Core_Reaction: response along the two tangents |
| 0x1009b4e0 | vphysics | per dynamic core: levers, matrix terms |
| 0x1009c0c0 | vphysics | pushes straight into the cores' speeds |
| 0x10082f60 | vphysics | friction controller priority 0 (normal pressure) |
| 0x10082ed0 | vphysics | one-contact pressure |
| 0x1007e990 / 0x1007ea80 | vphysics | normal speed / push into speeds (no clamp) |
| 0x100a0b30 | vphysics | the normal-pressure solve |
| 0x10082a60 | vphysics | contact mass / sliding switch (reads each material's +8, sets +0x34) |
| 0x100815a0 / 0x100816a0 | vphysics | system split (ivp-touch.md) |
| 0x100810a0 | vphysics | delete_friction_distance |
| 0x10086fb0 | vphysics | contact out of its pair (pair searched last to first) |
| 0x10018430 | vphysics | ordered vector remove |
| 0x10087270 | vphysics | core leaves the system |
| 0x10080e60 | vphysics | contact dtor (unread) |
| 0x10077520 | vphysics | core commits its pending changes |
| 0x10078650 | vphysics | core's pending-change clamp |
| 0x1008b0e0 | vphysics | IVP_Impact_Solver_Long_Term::do_impact_long_term: this = lt (ecx), pushed cores[2] out, cp (stack, `ret 8`), rescue speed in xmm2 |
| 0x10089a50 | vphysics | IVP_Impact_Solver::do_impact |
| 0x100890a0 | vphysics | separating push along -d |
| 0x1008a2c0 | vphysics | impact write-back |
| 0x10076570 | vphysics | core's new-speed check (-0.8333333 x rescue) |
| 0x1008a4d0 / 0x10088f10 / 0x1008a570 | vphysics | push as pending changes / take new speeds / clear pending changes |
| 0x10088850 | vphysics | relative speed at the point |
| 0x10088a70 | vphysics | push direction clamped into the friction cone |
| 0x1008a990 | vphysics | cores' 1 / \|response\| |
| 0x1008a600 | vphysics | push along the direction (xmm1 = s) |
| 0x10088fb0 | vphysics | last push undone |
| 0x1008b820 / 0x10088cc0 | vphysics | sliding impact variants (unreachable; libm 0x100d7a68) |
| 0x1008a0b2 | vphysics | branch: core already in this PSI's impact list (flags & 0xc0) |
| 0x100d7e25 | vphysics | CRT SSE2 atanf (statically linked) |
| 0x100b14f0 -> 0x1008b020 -> 0x1008ac60 | vphysics | mindist collision -> impact system (ivp-mindist.md) |
| 0x1008ac60, 0x1008b590, 0x1008b2c0 / 0x1008b380 / 0x1008b4c0, 0x1008aed0 | vphysics | impact system (ivp-impact.md 2-5) |
| 0x10088450 | vphysics | IVP_Mindist::try_to_generate_managed_friction |
| 0x1008df50 / 0x1008def0 | vphysics | contact from mindist / find existing |
| 0x100870c0 / 0x100871f0 / 0x100871c0 | vphysics | system's pairs / objects / (third add) |
| 0x10078860, 0x100713b0, 0x10071800, 0x100718e0, 0x10071aa0 | vphysics | two systems merged (simulation units) |
| 0x1008af60 | vphysics | the two materials' fetch |
| 0x1008afc0 | vphysics | mu / e per new contact (material manager slots 2 / 3) |
| 0x10018970 / 0x10018a20 | vphysics | get_friction_factor / get_elasticity |
| 0x10026f60 | vphysics | player controller's override test |
| 0x10019180 | vphysics | ParseSurfaceData (surface props slot 1) |
| 0x10019d30 / 0x10019ea0 | vphysics | surface entry insert / grow |
| 0x10019d00 | vphysics | material manager slot 1 (vtable 0x100e20cc) |
| 0x10018e70 | vphysics | GetSurfaceIndex (slot 3) |
| 0x10018f50 | vphysics | GetPhysicsProperties (slot 4: index, density*, thickness*, friction*, elasticity*) |
| 0x10018dc0 | vphysics | surface count (slot 2, +0x54) |
| 0x10018dd0 | vphysics | file already parsed (+0x5c) |
| 0x10019130 | vphysics | copy an index's data from +0x10 |
| 0x1001a0c0 / 0x100ba880 | vphysics | symbol table Find / add |
| 0x1001a190 | vphysics | sound names |
| 0x10002380 | vphysics | tokenizer (ParseFile) |
| 0x10002300 | vphysics | break set select |
| 0x10036220 | vphysics | ParseKeyvalue |
| 0x100b8a70 | vphysics | stricmp (ASCII folding) |
| 0x1000bad0 | vphysics | VPhysicsKeyParserCreate |
| 0x10033800 | vphysics | key parser NextBlock |
| 0x100337c0 / 0x10035100 | vphysics | SkipBlock (slot 9) / ParseCustom (slot 7) |
| 0x10034130 | vphysics | ParseSurfaceTable (slot 6) |

## Fields

IVP_Friction_System (0x4c bytes):

| Offset | Field |
|---|---|
| +0 | vtable 0x100f1cc8 (priority 600: slot 4 0x10082ff0, slot 5 0x10086480 = 600, slot 6 0x10086470 "sys:friction") |
| +4 | environment |
| +8 / +0xc | vtable 0x100f1d10 (priority 0: slot 4 0x10082f60, slot 5 0x10003fc0 = 0) / the system |
| +0x10 / +0x14 | vtable 0x100f1cf0 (priority 2000: slot 4 0x10082e70, slot 5 0x10086460 = 2000) / the system |
| +0x20 | contact list head |
| +0x24 / +0x26 | shorts |
| +0x24..+0x30 | its cores, all and dynamic (+0x2c the dynamic list) (ivp-impact.md) |
| +0x34 / +0x36 / +0x38 | core pairs (+0x36 count, +0x38 array) |
| +0x3c / +0x3e | shorts (+0x3e contact count) |
| +0x44 | byte: 1 = may split |

IVP_Contact_Point (0xa0 bytes):

| Offset | Field |
|---|---|
| +0 / +4 | next / prev (system list) |
| +8 / +0x1c | the two IVP_Synapse_Friction (0x14 bytes each) |
| +0x30 | spring's inverse mass |
| +0x34 | byte: 1 = sliding |
| +0x38 | spring stretch (2 floats, along lt's tangents) |
| +0x40 | this PSI's long-term info |
| +0x44 | mu |
| +0x48 | energy cut off the spring |
| +0x4c | face's 1 / \|normal\|: written by the ctor (0x1007ed78) only when sorted synapse 1 is a face; else the reused block's old word stays (read by nothing; world-hub's edge-edge contacts at tick 45 carry 0x3ee5a011) |
| +0x50 | static friction's energy |
| +0x54 | normal pressure |
| +0x58 | gap |
| +0x5c | byte, 0x14 at creation |
| +0x5d | byte: 1 = re-test the features |
| +0x5e | short: the pressure solve's sort key, counted down / up by its pushes (Normal pressures 1, 4) |
| +0x60 | f64 time of the last geometry |
| +0x70 | last contact point |
| +0x7c / +0x80 / +0x84 | last normal's z / x / y |
| +0x90 | friction system |

IVP_Synapse_Friction (0x14):

| Offset | Field |
|---|---|
| +0 / +4 | object's friction-synapse list (object +0x28 the head) |
| +8 | object |
| +0xc | short: back offset to the contact |
| +0xe | short feature: 0 point, 1 edge, 2 face, 3 ball |
| +0x10 | compact edge |

IVP_Impact_Solver_Long_Term (0xe0 bytes, a new block every PSI from env+0xa0 via 0x1006dc70):

| Offset | Field |
|---|---|
| +0 | contact point (world, on object 0's surface) |
| +0x10 | surface normal (world, object 0 -> 1) |
| +0x20 | gets the relative speed (impact) |
| +0x30 / +0x34 | objects |
| +0x38 / +0x3c | edges |
| +0x40 | materials (0x1008af60) |
| +0x52 | 4 bytes; short = impact count so far |
| +0x56 | short: 1 = the closest features left |
| +0x60 | elasticity (material manager slot 3, 0x1008afc0) |
| +0x68 / +0x6c | 1 / inverse virtual mass / inverse virtual mass along the normal |
| +0x70 / +0x74 | dynamic cores (0 when static) |
| +0x80 / +0x90 | the two tangents |
| +0xa0 / +0xb0 | point in each core's axes from its centre |
| +0xc0 / +0xd0 | r x normal in each core's axes |

IVP_Friction_Core_Pair:

| Offset | Field |
|---|---|
| +2 / +4 | contact count / contacts |
| +0x20 | countdown (reloaded 5) |
| +0x28 | last impact's time (ivp-impact.md) |
| +0x2c | unread |
| +0x30 | springs' energy |
| +0x34 / +0x38 | the two cores |

Other objects:

| Offset | Field |
|---|---|
| IVP_Core +0xc / +0x10 / +0x1c | environment / inertia / mass |
| IVP_Core +0x48 | car_wheel (0x1007f300's own static friction, 0x100820b0's skip; never set on a prop) |
| IVP_Core +0x4c | core's friction info |
| IVP_Core +0x60 | rows (impact solver) |
| IVP_Core flags | upper half: impact counters; & 2 static (also & 0x12 static for 0x100821a0); & 0xc0 in this PSI's impact list |
| object +0x28 / +0x40 / +0x44 | friction-synapse head / cache object / (< 8: refresh allowed) |
| object +0x4c | read in 0x10088450 as "the object's friction system" here; ivp-impact.md reads it as the dynamic core's friction info (IVP_Core +0x4c) |
| object +0x88 / +0x90 | own material / extra radius |
| IVP_Cache_Object (0x68) +0x20 / +0x30 / +0x40 | rows of object -> world rotation |
| IVP_Cache_Object +0x50 / +0x60 / +0x64 | position / stamp (refreshed when behind env+0x108) / users |
| object dump / core dump | 0xa4 / 0x1b0 bytes |
| env +0x20 | hooks (speed limits, impacts past perf +0xc) |
| env +0x40 | energy taken (statistic) |
| env +0x84 | += 1 per long-term info |
| env +0x90 / +0x98 / +0xa0 | cache manager / material manager / temporary memory |
| env +0xa8 / +0xac / +0xc0 | solve settings (+0xc0 the energy / failure scale) |
| env +0xf0 | read for a new contact |
| env +0x108 | cache stamp |
| env +0x118 | 0.9^dt (energy damping) |
| simulation unit flags (event +0xc) | & 0x3000 resting; & 0xc00; & ~0x200 \| 0x100 after the pressure solve |
| IVP_Compact_Ledge +0 / +0xc | points' offset / short triangle count; triangles of 16 bytes after the header; an edge is a dword index into its words; the ledge of an edge: `(edge & ~0xf) - ((tri index + 1) x 16)` |
| triangle +0 | triangle index (low 12 bits); three edges: start point index (16 bits), opposite (15 bits signed, in edges), virtual (1 bit); byte 3 & 0x7f the material index |
| mindist +0x14 | bits 8-9: which synapse (+0x28 / +0x44) is first; bits 18-21 status (3 = becomes a contact) |
| mindist synapse +4 / +0xa | compact edge (dword index into the ledge's words: 4 x triangle + 5 + slot) / i16 feature (0 point, 1 edge, 2 face, 3 ball) |
| CPhysicsSurfaceProps +0x48 / +0x54 / +0x5c | entries (0xac bytes) / count / parsed file names |
| CPhysicsSurfaceProps +0x17c / +0x180 | first-file flag / fallback entry's index |
| surface entry +0..+0xf | IVP material (vtable 0x100e218c, vphysics' subclass 0x100e2154; slot 1 friction factor); +4 / +8 / +0xc (+8 the sliding switch, +0xc symbol) |
| surface entry +0x10 / +0x14 / +0x18 / +0x1c / +0x20 | friction / elasticity / density / thickness / dampening; data copied as 0x27 dwords from +0x10 |
| key parser (0x408 bytes, vtable 0x100e3cc0) +4 / +8 | text / block name |

## Constants

| Value | What |
|---|---|
| 0x1010d130..0x1010d260 | IVP_Mindist_Settings globals (0x1010d23c..0x1010d25c the ones the solve reads) |
| 0x1010d23c | collision distance (a new contact's gap) |
| 0x1010d240 | friction distance (tolerance x 0.3 past it) |
| 0x1010d24c | tolerance x 2.5 + coll_dist: contact removed past it |
| 0x1010d258 | 2 x tolerance (impact rescue) |
| 0x3c4ffe5a, 0x3c6f314e | 0x1010d23c / 0x1010d240 in the kart scenario |
| 0x1010a988 / 0x1010a998 | edge next / previous tables (+4 +4 -8 / +8 -4 -4 bytes by edge address & 0xc) |
| 0x1ba / 0x1c4 | IVP Failed lines: unknown feature |
| 20 | k, past the collision distance |
| 5 | pair countdown |
| 0.001 | parallel test \|(\|n_i . n_j\| - 1)\| |
| 1e-10 | tangent normalise / parallel / det squared / tiny normal thresholds |
| 1e-15 (0x26901d7d) | 0x100890a0's denominator add |
| 0.9 | tangent axis pick (0.9 > d0^2); damping base (0.9^dt) |
| 10000 / 1e-4 | static core's mass scaling in 0x100821a0 |
| 0x3f23d70b (0.64) | mu, kart ("none" -> default, 0.8) on a default box |
| 0x3d800000 (0.0625) | e, the two defaults' product |
| sand: e = 0.25 x 0.01 | world-hub's contacts |
| 0x3f4ccccd / 0x3a83126f | fallback entry 0xf000's friction / elasticity |
| 0xf000 | `$MATERIAL_INDEX_SHADOW`, the fallback entry |
| 0xffff | grow's +0xc |
| 0x7f / 0x80 | surface index limit / world material table slots (128) |
| 121 | entries in CS:GO's surface scripts |
| 0x3ff | token cap (bytes) |
| `{}()':` | break set (table 0x101166f8, flag 0x1010f26d never written; 0x101165f8 the same without the colon) |
| 0x100e1e3c / 0x100e1e40 / 0x100e1e44 | strings `{` / `}` / `base` |
| 0x10116078 | the global surface props |
| 0x100fbee8 / 0x100fc480 / 0x100fc488 | atanf tables |

## Controllers and the order

The unit runs its controllers from the last entry (crazykart-physics.md 10). The kart resting: [0x100f1d10 (0), drag
500, motion 500..., 0x100f1cc8 (600), gravity 1000, 0x100f1cf0 (2000)]: geometry and energy first, then gravity (commits
the pending pushes), tangential friction, motion controllers, drag, last the normal-pressure solve. +0x44 set: 0x10082f60
then 0x100815a0 / 0x100816a0.

## Geometry: 0x1008d230

1. New long-term info (zeroed normal, +0x52..+0x57 zero; env+0x84 += 1); both objects' caches made or refreshed (0x1006cd90 when stamp +0x60 < env+0x108 and object +0x44 < 8).
2. Synapse 0 a point (its edge's start through cache 0, `to_world` per row `((r0 p0 + r1 p1) + r2 p2) + t`) or a ball (cache 0's position, +0x5d = 1), against synapse 1:
   - point 0x1008c2e0: normal p1 - p0 normalised, gap `n2 x (1 / sqrt(n2))` (not sqrt), tangent from the x or y axis by `0.9 > d0^2`.
   - edge 0x1008c490: gap `|q x e| / |e|`, normal `(q x e) x e` normalised, feature test `(q.e) / |e|^2` in [0, 1].
   - face 0x1008bd50: point into the face's object axes, barycentric test with FLT_MIN added (any sign bit: left), normal `(Q - P) x (R - P) x +0x4c` through the cache, negated; gap `n.p - n.P`; tangent the edge Q - P.
   - ball: point-point with its centre.
3. Synapse 0 an edge, 0x1008c850: both edges' world ends, unit directions a, b, `c = a x b`; `|c|^2 <= 1e-10`, `|e.R - e.S|` or `|f.P - f.Q| < 1e-10`: parallel (left, gap = 0x1010d240, normal x, tangent y); else the closest points' s, t, gap `|D - C|` (0 with normal `c / |c|` below 1e-10), tangent a; feature test s, t in [0, 1].
4. Point onto object 0's surface (+ radius x normal, object +0x90); gap less both radii (>= 0); first tangent normalised (past 1e-10), second = normal x first.
5. Per dynamic core (flags & 2 clear): lever `r = M^T (p - pos)`, normal lever `r x M^T n`, inverse virtual mass `((iI1 c1) c1 + (iI0 c0) c0) + (iI2 c2) c2 + 1/m`; point speed `M (w x r) + v` (core 1 subtracted, its mass term added after core 0's); +0x68 = 1 / +0x6c.
6. `dt = f32(env time - cp+0x60)`, cp+0x60 = env time; the spring moves back by `(tangent . speed) dt`; +0x70.. point and normal kept.

## Priority 2000: 0x10082e70

- One contact: 0x1008d230 only. Else 0x10086f10: per pair last to first, its contacts last to first: geometry, and `(old gap - new gap) x pressure` into the pair's energy when positive.
- Unit flags & 0x3000: 0x10082130. & 0xc00 clear: 0x100820b0 per pair last to first: energy x env+0x118; unless negative (or a car wheel's), 0x100826d0 takes min(a tenth of the removable energy, the pair's) out by pushes into the cores' pending changes (speed_change / rot_change, committed by gravity at 1000); env+0x40 += taken; pair energy less it.
- 0x100821a0: c0 the static core when either is (flags & 0x12), its masses then the other's x 10000 / x 1e-4; speed difference's direction and length; rot speed difference in world (M w per core) as directions in each core's axes; `|I x dir|` per core.
- Kart (flat-drive): unit flags 0x401 (228 PSIs), 0x1 (98), 0x1001 (4).

## Priority 600: 0x10082ff0

- One contact: spring cut to `(((mu pressure) +0x30) dt) dt` (cut energy into +0x48, +0x5d = 1), then static friction.
- Else per pair last to first 0x10080720: longest spring 0x10080630 `(dt x sum over contacts last to first of (pressure mu) +0x30) x dt`; each spring cut to it, then its static friction (sliding: 0x1007fd70, unreachable); positive sum of energy changes into the pair's energy.
- Then 0x10080e20: each pair's countdown; at 0, 0x10080840 (contacts with `|(|n_i . n_j| - 1)| < 0.001` share springs along the line between them: projections averaged, corrections / n into per-contact sums, added back through their tangents), reload 5.

## Static friction: 0x1007fb40

1. Max push `(pressure mu) dt`; below 1e-6 nothing. Car wheel: 0x1007f300.
2. 0x1009c010: response along the two tangents; per dynamic core 0x1009b4e0: levers `M^T (d x dir)`, x 1/I, diagonal `((r1 c1 + r0 c0) + r2 c2) + 1/m` and earlier directions' cross terms without the mass, speeds `(dir.v + lever.w)` weighed +1 / -1.
3. 2x2 solve for the push that brings the spring's speed to stretch / dt (det below 1e-10 squared: nothing), clamped to the max.
4. 0x1009c0c0 pushes into the speeds (not pending). Returns `sqrt(|s|^2 (dt |i|^2) dt) / 2` less the old energy.

## Priority 0: 0x10082f60

- One contact 0x10082ed0: normal speed 0x1007e990, push `x = ((k (coll_dist - gap)) + speed) x +0x68`, k = 20, into the speeds when positive (0x1007ea80), pressure x / dt; removed past 0x1010d24c or features left.
- Else 0x100a0b30. Then a system without contacts deletes itself (slot 7), or with +0x44 may split (0x100815a0 / 0x100816a0) and marks the unit (flags & ~0x200 | 0x100).

## Normal pressures: 0x100a0b30

1. 0x100a09a0: list sorted by +0x5e ascending (insertion sort moving past strictly greater: stable). 0x100a08e0: per contact (next taken first) gap >= 0x1010d24c or lt +0x56 == 1: 0x100810a0 (both cores' movement references' times = now; out of the list; out of its pair via 0x10086fb0 / 0x10018430, order kept, an empty pair goes and +0x44 = 1; out of both cores' friction infos, a core left without any leaves via 0x10087270 and its unit is marked; dtor 0x10080e60). Gap > `tolerance x 0.01 + coll_dist` between two cores both flagged 1: contact to the head; +0x40 = 0.
2. 0x10080fe0 the solver (n = contacts - +0x40, rows aligned to 4, env temporary memory); 0x100a0370 its entries in list order (the long-term infos: +0x50 the index, +0x58 / +0x5c the cores' friction infos for this system, +0x60 = (i32) +0x5e, +0x64 the gap); 0x100a0580 with 0x100a0470: row j, column i = contact j's normal speed for a unit push at i (per dynamic core of i: response `-(rn x 1/I)`, `-(n / m)` for core 0, + for core 1, dotted with j's lever and normal, sign -1 when it is j's core 0: `((rn1 a1 + rn0 a0) + rn2 a2) + ((n1 l1 + n0 l0) + n2 l2)`); `b_i = k (coll_dist - gap) + normal speed`; flagged list (+0x5e != 0).
3. 0x100a0060: 0x1009fe20 (diagonal's maxss chain from the last row in groups of 4, scale 1 / max unless <= 1e-10, |b|'s max likewise; rows x the first, b x the second's inverse, +0x18 = the product); result zeroed; 0x1009cb60 flagged rows and columns (a prefix 0..n-1 copies whole rows); 0x1009c880 Gauss (pivot: largest |a_rk| from the last row up, strictly greater; rows below eps 1e-9 left; `row_i += row_k x (a_ik x -1 / a_kk)`); 0x1009c980 back substitution (last column down; pivot below eps: 0 when |s| < 1000 eps, else failure); 0x1009fcb0 answer into the result, failure when `env+0xc0 x 0.01 > x scale x lt +0x6c` for a flagged contact or an unflagged one's `row . x + |b x 1e-5| < b` (0x1009c5b0: ascending sum, two 4-lane sums from 8 entries). Failed: 0x1009d270 with the contacts at the head whose +0x5e < 0 active at the start; its failure means no pushes this PSI.
4. 0x1009fd90 x scale; energy 0x100a0c20 (per system core last to first: `((v0^2 + v1^2) + v2^2) m + ((I1 w1^2 + w0^2 I0) + I2 w2^2)`, halved, with the pending changes); 0x100a02a0 per contact: x > 0 pushes (0x1009fb00 into pending changes, each core clamped by 0x10078650) and counts +0x5e down (from -1); x == 0: +0x5e = 0; x < 0 (or NaN) pushes too (a pull) and counts +0x5e up (from 0, back to 0 past 9); pressure +0x54 = `1/dt x max(x, 0)`; energy again and 0x100a0d70 (per dynamic core `(perf +0x18 against its mass) x env+0xc0 x 0.1`); more than the allowance: undo 0x100a0d10 (unread), else every dynamic core (+0x2c list, last to first) commits (0x10077520).

Kart (flat-drive, 330 solves): 114 direct, 216 complementarity.

## Complementarity solve: 0x1009d270 (IVP_Linear_Constraint_Solver)

| Offset | Field |
|---|---|
| +0 / +8 / +0xc | eps 1e-7 / check tolerance 1e-4 / step limit 1e4 |
| +0x10 / +0x14 / +0x1c / +0x20 / +0x24 / +0x28 | A / b / x / dx / w (= -b at start) / dw |
| +0x2c / +0x30 | a start x / its w |
| +0x18 (= +0x88) | residual |
| +0x34 / +0x38 | order / its inverse |
| +0x3c / +0x40 / +0x44 / +0x4c | n / n aligned / actives / first unhandled |
| +0x50..+0x64 | counters (+0x54 stale-Gauss count; +0x58 / +0x5c / +0x60 / +0x64 the perturbation's) |
| +0x68 | factorisation state: 0 valid, 1 stale, 2 broken |
| +0x6c | inverse manager: +0 eps 1e-6, +4 inverse, +8 U, +0x14 b, +0x18 x, +0x1c / +0x20 scratch, +0x24 stride, +0x28 size |
| +0x98 / +0xb0 / +0xc8 / +0xe0 | great matrices (+0x98 actives' Gauss eps 1e-7; +0xb0 A with dx / dw) |

- **0x1009df60** start: first n_active active and handled; factorisation 0x1009dda0 (U from the actives' rows and columns, b, then 0x1009f270); solved 0x1009f9a0 (inverse x b, sums from the last entry 0x1009c4f0, then 0x1009f870 back substitution through U); x / w via 0x1009dec0 (`w = A x - b` by 0x1009cd00, actives' 0); an active with x < 0 leaves (0x1009dae0 swap, 0x1009f660) and the solve repeats; broken factorisation or failed setup: start from nothing.
- **0x1009d630** pivoting (a state machine): at most 250 steps (counted on a move and on each restart); every 7 steps 0x1009d0b0 (residual `A x - b` against 0 for actives, w for others, 1e-4) or a restart. Next unhandled variable: |w| < eps (and |x| < eps: handled at 0; else enters the actives); w >= 0 handled at 0; w < 0: 0x1009dbc0 actives' move for a unit step (from the factorisation, or Gauss when stale: +0x54 counts), dx[var] = 1, 0x1009cfa0 dw for the others, ratio test (own `w / dw` unless `1e4 dw <= -w` (then 1e20), each active with dx < -eps (immediate stop when its step < eps and x < eps), each handled with dw < -eps, eps slack each way), step maxss 0; past 1e4 or more than n/2 + 2 tiny steps in a row: restart. 0x1009db20 the step (`w, x += step x dw, dx`; handled w and actives' x kept >= 0). The stop leaves the actives (0x1009f660), joins them (after 0x1009d5b0 drops actives below eps, 0x1009d430 / 0x1009f3e0 grow the factorisation), or is the variable itself (joins, handled). Stale factorisation rebuilt after a move: 0x1009d4e0 perturbation (two swaps among actives by counters stepping 1 and 2 mod their count, two among unhandled likewise), then 0x1009dda0.
- **0x1009e0d0** restart: factorisation from the actives (after the perturbation), or actives sorted by x (0x1009de10, greatest first) and solved by Gauss; x / w; 0x1009e250 sends actives below eps to handled (x 0) or, negative, to the end (counted: positive count repeats the restart), handled with w < 0 to the end.
- Inverse manager: 0x1009f270 Gauss with pivoting on U and the identity (0x1009ef30 row swaps, 0x1009ee60 row over its pivot (eps 1e-6: failure), 0x1009f050 row less f x another, U[i][k] = 0), only below the diagonal; 0x1009f3e0 adds a row and column (new column = inverse x active column, new row eliminated against every earlier one, then normalised); 0x1009f660 removes one (columns k and last swapped in both, inverse's rows fixed by 0x1009fa50, pivot re-normalised or patched, last row eliminated, its inverse row normalised (failure below eps) and cleared from the others by 0x1009f1b0). Row ops keep column groups: a U row from (k + 1)'s 4-aligned group, an inverse row whole (zeros below the diagonal keep their signs).
- Direct and complementarity results go through the same pushes (step 4 above).

## Impacts

IVP_Impact_Solver (0x140 bytes on 0x1008b0e0's stack):

| Offset | Field |
|---|---|
| +0 | `(0x1010d258 + rescue speed) x 1.2` |
| +4 / +8 | each core's 1 / \|response to a unit push\| (1008a990; static: the other's x 1e5) |
| +0xc | 1 (0 after 10 impacts of a separating contact: no more friction) |
| +0x1c / +0x20 | cores' rows (core +0x60) |
| +0x30 / +0x40 | rot speeds with pending changes |
| +0x50 / +0x60 | speeds with pending changes |
| +0x70 / +0x80, +0x90 / +0xa0 | last push's rot / speed change per core |
| +0xb0 / +0xc0 / +0xd0 | relative speed at the point / push direction / second direction (sliding) |
| +0xe0 | sliding flag (1008b820) |
| +0x100 / +0x104 | cores: a static one always at +0x100, +0x104 always dynamic (below) |
| +0x108 / +0x10c | levers: lt +0xa0 / +0xb0, swapped (+0xb0 / +0xa0) when the cores are |
| +0x110 / +0x114 / +0x118 / +0x11c / +0x120 | elasticity (lt +0x60) / cone cos / sin / normal (lt +0x10, or its negation on a stack copy) / lt +0x20 |

- **0x1008b0e0** (this = lt, arg 2 = cp; checked against the disassembly 2026-11-21), the cores (lt +0x70 / +0x74: dynamic cores, 0 when static):
  - lt +0x74 == 0: +0x100 = object 1's core (`[lt+0x34] +0x94`), +0x104 = lt +0x70; normal = -(lt +0x10) (each lane `xorps` 0x80000000, 0x100f4310), levers +0xb0 / +0xa0.
  - else: +0x100 = lt +0x70, or object 0's core (`[lt+0x30] +0x94`) when that is 0; +0x104 = lt +0x74; normal lt +0x10, levers +0xa0 / +0xb0.
- Elasticity e = lt +0x60. Neither core with +0x48 set: the friction cone, mu = cp +0x44:
  `t = (sqrtss(e) + 1.0) * mu` (0x10001950 is `sqrtss`), `a = atanf(t)` (0x100d7e25), `a2 = a * a`,
  `cos = (1.0 - a2 * 0.5) + (a2 * 0.041666668) * a2` (0x3f000000, 0x3d2aaaab), `sin = cos * t`;
  then 0x1008b820 when the byte cp +0x34 is set. A core with +0x48 set: cos 1, sin 0 (1008b252).
- Then 0x10089a50.
- **0x10089a50**: `e' = 1 - (1 - e) / (n / 2 + 1)` (n = lt +0x52); rescue `(0x1010d258 + arg) x 1.2`; speeds with pending changes; rel (10088850), lt +0x20 = rel; responses (1008a990); first push `q = (((-rel.n) 2 vm1) / (vm0 + vm1)) vm0 0.1`. Separating (rel.n not below -0.0001): 0x100890a0 along -n with flag 1 (the minss). Closing: direction 10088a70, up to 100 rounds of push q / rel / direction while closing (rel's normal speed > 0), then undo (10088fb0), a unit push along -n, the elastic push `tot / (rel.n + s)` (past 1e-4) via 1008a600, and 0x100890a0 along -n / the direction. Speed limits via env+0x20 hooks (never on the kart). Then 1008a2c0.
- **0x100890a0**: (speed along -d of the point less the rescue speed) / (both cores' response along it + 1e-15), pushed as the last push.
- **0x1008a2c0**: 0x1008a570 clears both pending changes first; cores' impact counters (flags' upper half) up (+2) unless static; with +0xc set, the core with the larger 1 / response checked by 0x10076570 against the other's new speeds (-0.8333333 x rescue): it keeps its old speeds and takes the push as pending changes (0x1008a4d0), the other gets its speeds (0x10088f10); else both do. A core already in this PSI's impact list (flags & 0xc0, 0x1008a0b2) moves its speeds into the changes (the impact system's double buffer, 1008b590).
- **10088850**: `rel = (v1 + M1 (w1 x r1)) - (v0 + M0 (w0 x r0))`, each M row `((a0 + a1) + a2)`.
- **10088a70**: dir = rel normalised (past 1e-10); along the normal (d > 0): the second direction; else unless sliding (10088cc0), inside the cone (d > -cos): `t = dir + n (-d)` normalised, `dir = n (-cos) + t sin`.
- **1008a990**: per core (core 1 +n, core 0 -n): `1 / |M ((r x M^T n) x 1/I x r) + n / m|` (pinned: 1).
- **1008a600**: `p = dir s`; core 0 (unless static): rot change += `1/I (r x M^T p)`, speed change += `p / m`; core 1 with -p computed as `p x -1`: `1/I (l x r)`, `l = M^T(-p)`.
- **10088fb0**: rot / speed minus +0x70.. / +0x90.. for the dynamic cores.
- No "ivp_impact.cxx" among the DLL's IVP Failed strings (asserts compiled out).

Kart touchdown (flat-drive tick 8) call counts: 0x1008ac60 x3, 0x1008b0e0 x5, 0x10089a50 x5, 0x100890a0 x5, 0x1008a2c0 x5,
0x1008a570 x5, 0x1008a990 x5, 0x10088850 x41, 0x10088a70 x36, 0x10088f10 x10, 0x10088fb0 x5, 0x1008a600 x41,
0x1008b590 x5, 0x1008b2c0 / 0x1008b380 / 0x1008b4c0 x3, 0x1008aed0 x3, 0x1008afc0 x3, 0x10018970 x6, 0x10018a20 x6
(crazykart-physics.md 3: mu 0.64, e 0.0625), 0x10026f60 x6. Impacts at ticks 8, 45, 51, 52, 322 (13 in 400 ticks).

## Atanf: 0x100d7e25

- |x| in [2^-5, 2^64): c = |x| cut to 4 mantissa bits (or 0x0000800000000000, min 64), `t = (|x| - c) / (1 + |x| c)`, `(atan(c) + t) + t^2 (-t/3)` in f64.
- Below 2^-5: f32 `x + (x^4 (0.2 x) + (-x/3) x^2)`; below 2^-64: x; past 2^64: `+-(7.5497894e-8 + 1.5707963)`; NaN / infinity 0x100d7fae unread.

## New contact: 0x10088450

1. 0x1008df50: only a mindist with status 3; existing contact by 0x1008def0, else new 0xa0 + 0x1007ec20.
2. Geometry (0x1008d230), materials (0x1008afc0).
3. The object's system (+0x4c) or new (0x4c + 0x10086de0); contact at the head (+0x20, +0x3e += 1); 0x100870c0, 0x100871f0, 0x100871c0; two systems merged by 0x10078860 / 0x100713b0 / 0x10071800 / 0x100718e0 / 0x10071aa0.
4. Kart: x3 at the touchdown (three contacts), again at 45, 51, 52 (a fourth comes and goes) and 322 (landing after the jump).

## Materials

- 0x1008afc0 once per new contact via env+0x98 slots 2 / 3: mu into cp +0x44, e into lt +0x60. 0x1008af60: triangle byte 3 & 0x7f through the world's table (SetWorldMaterialIndexTable, crazykart-physics.md 14), else object +0x88.
- **No contact ever slides.** Every way a surface entry is made writes +8 = 0: the parser 0x10019180 (`local_d0 = 0` before each entry's keys, 0x10019215; no key writes it; "base" copies only from +0x10 on; the fallback entry at 0x10019bcd: `local_17c = 0`), insert 0x10019d30 (copies the local's +8), grow 0x10019ea0 (+8 = 0, +0xc = 0xffff). Slot 1 0x10019d00 hands out these entries (surface props slot 0x2c); an object's own material (+0x88) is the template's from the same table (crazykart-physics.md 11, step 5). So 0x10082a60 never sets +0x34; 0x1007fd70, 0x1008b820 / 0x10088cc0 never run. A sideways push is the static friction's clamp `(pressure mu) dt` (kart: 756 times in flat-drive, 1225 in 700 ticks of slide.txt: a shove at 600 in/s, a spin, a hard turn at full thrust, a shove while driving).

## Surface scripts

- Tokenizer 0x10002380: skips bytes below 0x21 as a *signed* char, so 0x80-0xff are whitespace too and end an unquoted word; `//` to newline, `/* */` block; quoted string to the next quote or NUL; break set from 0x10002300; a break char is its own token; tokens capped at 0x3ff.
- ParseKeyvalue 0x10036220: key lowercased (__strlwr); a key equal to `}` (strcmp) leaves the value empty, else the value comes next, lowercased. At text end the pointer is null and the key empty.
- ParseSurfaceData 0x10019180 (entry 0xac, symbol +0xc, data 0x27 dwords from +0x10):
  1. A file name already in +0x5c (0x10018dd0) returns 0.
  2. Per top-level key whose value is `{`: name into the symbol table (0x100ba880, +8); the entry starts as a copy of GetSurfaceIndex(name) clamped to 0 (a new name copies "default"; empty list: zeros).
  3. Keys until `}`: `base` copies the named entry when found (else DevWarn, nothing); thickness +0x1c, density +0x18, elasticity +0x14, friction +0x10, each `(float)atof`; others (sounds via 0x1001a190, gamematerial, audio*, *occlusion, dampening +0x20, penetration / damage modifiers) write past +0x20.
  4. At `}`: GetSurfaceIndex(name) < 0: inserted (0x10019d30) at the end; else overwritten in place, an index past 0x7f other than 0xf000 lands on entry 0 (0x10019b57). Text ending inside an entry drops it (0x1001940f).
  5. After the first file only (+0x17c): fallback 0xf000 = copy of entry 0 (0x10019130) with friction 0x3f4ccccd, elasticity 0x3a83126f, appended, index at +0x180. A "default" that isn't index 0: Warning "Physics materials broken!".
- GetSurfaceIndex 0x10018e70: a `$` name stricmp-equal to `$MATERIAL_INDEX_SHADOW` gives 0xf000; else symbol Find (0x1001a0c0), then a linear search of entries' +0xc; miss -1.
- GetPhysicsProperties 0x10018f50: 0xf000 -> +0x180, any other >= 0x80 -> 0; negative or out of range -> entry 0; no entries: outputs unwritten. Reads +0x10 / +0x14 / +0x18 / +0x1c.
- Key parser: NextBlock 0x10033800 reads keyvalues up to a value equal to `{` (strcmp), that key the block name. SkipBlock (slot 9, 0x100337c0) calls ParseCustom (slot 7, 0x10035100) with no handler: depth +1 for a key or value starting `{`, -1 for a key starting `}`; below 0 NextBlock.
- ParseSurfaceTable 0x10034130: keyvalues until a key starting `}`, then NextBlock; each key -> GetSurfaceIndex(key) (props 0x10116078), value atoi -> slot; slot < 0x80: `table[slot] = index`; a negative slot writes before the table.

## Unread

- Sliding friction 0x1007fd70 (unreachable); car wheel's static friction 0x1007f300.
- Undo 0x100a0d10; big-system split 0x100a0ad0 of 5.
- System split / merge 0x100815a0, 0x100816a0, 0x10081280 (read since: ivp-touch.md); 0x10082ce0's dynamic branch at revival (read since: ivp-pileup.md "Units and revivals").
- Contact dtor 0x10080e60; pair +0x2c.
- Read since (ivp-impact.md): the impact system, 0x10088450 with 0x100870c0 / 0x100871f0 / 0x100871c0, the removal's unit bookkeeping (0x10087270, 0x10071dc0), pair +0x28, system +0x24..+0x30, cache refresh 0x1006cd90 (ivp-mindist.md "The cache").
