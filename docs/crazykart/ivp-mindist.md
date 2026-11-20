# CS:GO legacy IVP: collision detection up to the impact (vphysics.dll, 32-bit)

How csgo legacy's vphysics.dll (md5 d97cf2194594d7545427cdabc7376db4, the one docs/crazykart/crazykart-physics.md 8-11
reads) finds and tracks the distance between ze_crazykart's kart and the world, up to the call into the impact
code. Everything here was read from the disassembly (Ghidra /csgo_vphysics_legacy.dll, capstone); the leaked IVP
source (Havok/ipion) was used for names only and differs from this build in places (said where). All float math is
SSE scalar single unless noted; "(a + b) + c" is the disassembly's association (an add's two operands commute, so
only the grouping matters). Ported in sim/src/ivp (ledge.rs, cache.rs, mindist.rs, minimize.rs, minimize_kk.rs,
minimize_pf.rs, minimize_qkk.rs, recalc.rs, hull.rs, collide.rs, collide_create.rs, collide_events.rs,
mindist_event.rs, mindist_event_pp.rs), checked by sim/src/bin/mindist_check.rs (`IVP_TRACE=1` prints the walk's
cases, minimize::TRACE).

## 1. The oracle's collision dump and the check

rubikon/tests/KartOracle/Mindists.cs writes `<out>.md` beside `<out>.raw` (Program.cs calls Init, Psi per tick,
Write; it patches the mindist vtable's slot 0, simulate_time_event 0x10095dd0, to dump around each mindist event):

- `# settings 0x1010d130..`: ivp_mindist_settings as the DLL left it (section 7's constants);
- `# objects`: each object's IVP_Real_Object +0..+0xa4, its core +0..+0x1a8, its compact surface +0..+0x30;
- `ledge L<n> <owner> <n_tri> <n_pts>: <header + triangles> | <points>`: each ledge once, when first seen;
- `psi <tick> <env time f64> <next PSI f64>` after each Simulate, `ev <n> <env time> before|after md<i>` around each
  mindist time event, each followed by: `md` lines (vtable, +4 event index, +0x14 bits, each synapse's object /
  ledge / triangle / edge / status / hull index, +0x50..+0x7c, the time event's element and base), `hm <obj>`
  (the hull manager +0..+0x34 and its listeners in order: value, who), `ov <obj>`, `core <obj>` (+0x5c, +0x120,
  +0x13c, +0x1a4), `mm` (the mindist manager +0..+0x14), `tm` (the time manager's base and its events in order).

Run (Windows): build and run the oracle as crazykart-physics.md 8 says (its `.md` lands beside the out file), then
`cargo run --release -p ze-sim --bin mindist_check -- <scenario> <oracle out> <the kart's .phy>`. It checks: the two
ledges against the DLL's bytes; the creation's recalc_mindist; then every tick (and every mindist event's before /
after) the mindist's bits, synapses, +0x50..+0x6c, both hull managers (fields and every listener's value and kind),
the core's collision fields and the time manager's mindist events, until the first do_impact.

**Checked (2026-11-17)**, bit-identical with the DLL up to the first impact: scenarios/flat-drive.txt (the drop: 8
ticks, an edge-edge contact, the KK event solver, impact at t = 0.147446 in tick 8), drop-flip.txt (upside down,
rolled: 23 ticks, the OO watcher's events, a point-face contact, the PF solver, impact in tick 23), drop-tilt.txt
(tilted, the upright spinning it: 21 ticks, the OO watcher, an OV recheck, three mindist events before the impact in
tick 21), drop-high.txt (87 ticks: paired at the OV recheck, the ledge radius test, section 10), drop-edge.txt,
drop-corner.txt (the PK event solver's 0x32), corner-roll.txt (KK's K-inside branch), corner-roll-left.txt (Leave_PF's
two-sided exit, calc_qlen_KK), corner-pierce.txt (recalc_mindist's pierce). Section 10 lists them and what is left.

## 2. Compact ledges (sim/src/ivp/ledge.rs)

IVP_Compact_Ledge: +0 c_point_offset (from the ledge), +4 ledgetree_node_offset / client data, +8 flags (has_children
2 bits, is_compact 2, dummy 4, size_div_16 24), +0xc n_triangles (i16), +0xe unused; then 16-byte triangles: +0
tri_index:12 pierce_index:12 material:7 is_virtual:1, +4 / +8 / +0xc the three edges: start_point_index:16
opposite_index:15 (signed, in edges: dwords) is_virtual:1. Points 16 bytes (x, y, z, pad), IVP metres. An edge
pointer's low bits (& 0xc) are 4 / 8 / 0xc for edges 0 / 1 / 2: next = edge + table 0x1010a988[& 0xc] (+4, +4, -8:
0 -> 1 -> 2 -> 0), prev = + 0x1010a998[& 0xc] (+8, -4, -4), opposite = edge + ((int)(word x 2) >> 17) x 4, the
triangle = edge & ~0xf, the ledge = triangle - (tri_index + 1) x 16 (init_mindist 0x10094150's form). The port keeps
the edge as a dword index into the ledge's words.

- The kart's ledge: the .phy's first solid (VPHY header 28 bytes, compact surface +0x20 the ledge tree root offset;
  the root is a leaf: +0 == 0, +4 the ledge's offset). Words and points copied as they are.
- **BBoxToCollide** (collision slot 29, 0x1000ad00): equal mins / maxs -> NULL; the cache lookup 0x1000adf0; else
  (the unit box made once by 0x1000ab60: ConvexFromVerts 0x10008b50 of (-16, -16, 0)..(16, 16, 72), then each point's
  nearest corner within 0.1 u into the byte map at +0x1c, ConvertConvexToCollide slot 0x38) **0x1000a860**: the 8
  corners (bit 0 x max, 1 y max, 2 z max), the unit box's ledge copied (size_div_16 x 16 bytes; +4 zeroed when the
  flags' low bits are 0), each point = corner(map[i]) as (k x, -(z k), y k), k = 0x10106930 (0.0254f), w 0; then
  slot 0x38 builds the compact surface. The template's twelve triangles and its map ([7, 2, 6, 3, 5, 4, 0, 1]) are
  in ledge.rs, read from the DLL's own copy (stand-in: ConvexFromVerts = qhull + IVP's ledge builder isn't ported;
  every BBoxToCollide box copies this one).
- The box's compact surface (mass centre (0, 0.8128, 0) for the scenario's box, upper radius 146.13, deviation byte
  0xfa) and its static core come from the dump (stand-in: ConvertConvexToCollide's ledge soup and the static core's
  creation; the game's world is the BSP's own .phy anyway).

## 3. The object's pose at a time (sim/src/ivp/cache.rs)

IVP_Cache_Object (object +0x40, made on first use by the cache manager 0x1006ccb0, refcount +0x64): +0 the core's
position at t, +0x10 the quaternion, +0x20 rows (stride 0x10), +0x50 the object's origin (rows +0x20..+0x58 =
m_world_f_object, an IVP_U_Matrix: rows then the position at +0x30), +0x60 the time code it was made at, +0x68 the
object. **0x1006cd90** (the update): the time code from env+0x108; dt = f32(env+0xf0 - core+0x130); dt == 0 (ucomiss,
parity: equal only): q = core+0x100 (q_last), position = core+0xe0; else q = 0x1006ca90 (object.rs quat_at) and
position = core+0xf0 x dt + core+0xe0 per axis; the rows by the 0x100723b0 formulas (x2 = x + x ...: [1 - (zz + yy),
xy - wz, wy + xz; wz + xy, 1 - (zz + xx), yz - wx; xz - wy, wx + yz, 1 - (yy + xx)]); unless object+0x44 & 0x800 the
origin += rows x object+0x30 with ((r0 o0 + r1 o1) + r2 o2) + p; object+0x2c (a rotation) not read (NULL here). A
moving object's cache (object +0x44 byte < 8) is renewed when its time code is older than env+0x108
(minimize_default_poly_poly 0x10099850, 0x100a53e0); a static object's stays as made.

**0x10074000** (get_m_world_f_object_AT, the event solvers' samples): object.rs pose_at (the lerp / slerp even at
f = 0: not the cache's formula).

Inlined transforms used everywhere (cache.rs world / object / world_vec / object_vec): to world ((m00 p0 + m01 p1) +
m02 p2) + pos per row; into an object d = w - pos, ((m0i d0 + m1i d1) + m2i d2) per column.

## 4. Mindists and how one is made

**IVP_Mindist** (vtable 0x100f2914: [0] simulate_time_event 0x10095dd0, [4] the deleting destructor 0x10093fb0, [5]
mindist_rescue_push 0x100980a0, [7] exact_mindist_went_invalid 0x10094bc0, [8] do_impact 0x1008b020): +4 the time
manager's event index (0xffff none), +0x14 bits: coll_type 0-7, synapse_sort_flag 8-9, is_in_phantom_set 10-11,
mindist_function 12-13 (0x1000 phantom), recalc_result 14-15 (0 OK, 0x4000 intrusion), disable_halfspace 16-17,
mindist_status 18-21 (3 exact, 4 hull recursive, 5 hull), coll_dist_selector 22-29 (starts 63). Synapses at +0x18
and +0x34 (0x1c each, vtable 0x100f2900: [1] hull_limit_exceeded 0x10095780, [2] hull manager deleted 0x100957a0,
[3] hull_manager_is_reset 0x10095750): +4 the hull manager's element index, +8 / +0xc next / prev in the object's
exact (object +0x20) or invalid list, +0x10 the object, +0x14 the edge, +0x18 (i16) mindist - synapse, +0x1a status
(0 point, 1 edge, 2 triangle, 3 ball, 5 backside). +0x50 sum_extra_radius, +0x54 contact_dot_diff_center, +0x58
sum_angular_hull_time (f32 in this build), +0x5c len_numerator (get_length), +0x60 contact_plane (x, y, z, w), +0x70
recalc_time_stamp, +0x74 / +0x78 next / prev in the manager's lists, +0x7c last_visited_triangle. The sorted synapse
0 is synapse[flag], 1 is synapse[flag ^ 1] (bits >> 8 & 3, times 7 dwords + 6).

**IVP_Mindist_Manager** (env+0x10): +0 scanning_universe, +4 the environment, +8 exact_mindists (newest first),
+0xc the wheel vector (u16 size, u16 n, elements), +0x14 invalid_mindists.

Object fields: +0x18 env, +0x20 exact synapses, +0x40 cache, +0x44 movement byte (1 moving, 8 static; 0x21 during a
revival), +0x48 the hull manager (6), +0x84 the surface manager (+4 the compact surface), +0x8c the OV element, +0x90
extra radius, +0x94 the core. Core: +4 radius, +8 the deviation radius, +0x44 0.5 / radius, +0x5c spin rate, +0x120
the rotation axis (world), +0x13c |speed|, +0x1a4 max_surface_rot_speed (core.rs).

**Creation** (at the kart's revival, stage 1 via 0x100778d0 with the core's and object's movement bytes forced to
0x21): **recheck_ov_element 0x10094de0** (this = the manager): the OV element out of the tree (0x1009b400), its
centre = core+0x90; real_check_sphere = f32(range manager slot 1(object)) + core+4; the universe manager (env+0x2c,
NULL here); insert_ov_element 0x1009b200 (the tree, collecting the elements it meets; returns the radius: with min
== max radius its node finder 0x1009a660 returns that radius) and add_to_hull_manager 0x1009a420 at (radius -
core+4); the collisions already in the element's vector kept (a diff hash 0x10096620 / 0x100964f0), the stale ones
deleted (slot 4), each new pair offered to the delegator roots (env+0x128, count +0x126, slot 5 until one takes it).
The root makes an **OO watcher** (IVP_Collision, vtable 0x100f2f2c; its two IVP_Synapse_OO at +0x18 / +0x28, vtable
0x100f2f40, objects at +0x20 / +0x30, the mindists' vector at +0x38): synapses at the range manager's split (slot 0)
and **create_exact_mindists 0x10094300** (single ledges: one mindist from the two ledges' first triangles' first
edges, status point; `new IVP_Mindist` sets vtables 0x100f2914 / 0x100f2900) -> **init_mindist 0x10094150**
(synapses: object, edge, offset, status; the surface manager's add_reference_to_ledge (slot 7); sum_extra_radius =
the objects' +0x90 sum; insert_and_recalc_phantom 0x10094cf0 when an object has a phantom, else) ->
**insert_and_recalc_exact_mindist 0x10094be0**: status exact (bits & 0xffcfffff | 0xc0000), at the head of +8, each
synapse at the head of its object's +0x20 list, recalc_mindist, a car-wheel core into the wheel vector, then
recalc_result OK: update_exact_mindist_events(allow = (core0 movement | core1 movement) < 0x21, NOW) (so never a hull
conversion at a revival), else slot 7.

**The range manager** (env+0x1c, vtable 0x100f2b70, ctor 0x100a10c0: intra 0.5 / 0.9 / 0.8 / 10 / 0.06, world 1 / 5
/ 0.5 / 15 / 0.06; the leaked source's 0.1 is 0.06 here). minss / maxss as SSE (a < b ? a : b):
- slot 0 **0x100a1150** (intra(obj0, obj1, &r0, &r1)): s0 = (msrs0 + speed0) + 1e-10, s1 likewise; r = minss(radius1,
  radius0) x 0.9; sum = s1 + s0; a = s1 x 0.2 + s0; d = minss(r, 0.5 sum); b = a x 0.18 + s1; d = maxss(d, 0.8); d =
  minss(d, 10); d -= env dt x sum; d = maxss(d, 0.06 sum); inv = 1 / (b + a); r0 = (d a) inv, r1 = (d b) inv.
- slot 1 **0x100a1240** (in_world(obj), x87 return of a stored f32): s = (msrs + speed) + 1e-10; d = minss(1 s, 5
  radius); maxss 0.5; minss 15; -= dt s; maxss(d, 0.06 s + radius).

## 5. The closest-feature walk (minimize.rs, minimize_kk.rs, minimize_pf.rs, recalc.rs)

**recalc_mindist 0x100982d0**: time stamp == env+0x108 -> 4 (already); else stamp it; the solver on the stack (+0
the mindist, +4 P_Finish_Counter = 20, +0x10 pos_opposite_BacksideOs, +0x20 the loop list (256 pairs), +0x820 its
length, a pierce counter); loop: r = table 0x10110a28[sorted0.status x 4 + sorted1.status] (filled by 0x1009a140:
P x {P, K, F} and K x K, F x F 0x10099850 default; K x P, F x P 0x10099c90 swapped (flip the sort flag, then the
default); P x B 0x10099a60, K x B 0x10099c10, F x B 0x10099c50, B x {P, K, F} 0x10099aa0, B x B 0x10099cb0; the
rest 0x1009a120 illegal). 1 (OK): recalc_result 0, return 1. Else recalc_result 0x4000; 2 (endless loop) -> end; 3
(backside): the backside synapse's edge = minimize_on_other_side 0x10099e60, status triangle, retried while the
pierce count < 2; end: unless phantom or hull-recursive, slot 5 (rescue push). TODO(trace): 0x10099e60 and slot 5.

**minimize_default_poly_poly 0x10099850**: both caches (made / refreshed, section 3), m_cache = {points, ledge,
cache, object, synapse}; by (sorted0.status, sorted1.status): (0, 0) PP 0x100b4e20, (0, 1) PK 0x100b6070, (0, 2) PF
0x100b1ca0, (1, 1) KK 0x100b3070, else FF 0x100984c0 (ported 2026-11-18: section 14).

**check_loop_hash 0x10098020** (the list variant): (status | edge address) pairs, canonical order, looked up from
the newest; full (256) counts as a loop. Called only once P_Finish_Counter goes below 0 (the counter -= 1 at each
PP / Leave_PK / Leave_KK / Leave_PF entry).

The s / qr values (inlined everywhere, minimize.rs s_vals / qr_vals): s(k0, k1, p): k = k1 - k0, [-((k0 - p).k) +
FLT_MIN, (k1 - p).k + FLT_MIN]; outside = either sign bit. qr(F, p): the triangle's P0 P1 P2 (its edges 0-2), a =
P0 - P1, b = P2 - P1, c = p - P1, aa, bb, ab = b.a, ca, cb (each (x + y) + z), t = cb aa - ca ab, s = ca bb - cb ab,
D = bb aa - ab ab; (t, (D - s) - t, s) + FLT_MIN placed by the bytes 0x100f1b08.. by F's edge index (0: [0, 2, 1],
1: [2, 1, 0], 2: [1, 0, 2]) so checks[j] is F's j-th edge from F.

- **PP 0x100b4e20** (a loop): both points to world and into each other's frame; d = wA - wB, q = d.d; q <= 1e-6 ->
  2; len = (1 / sqrtf(q)) q - sum_extra_radius, plane = d x inv, contact_dot_diff_center = plane.(coreA - coreB) (the
  caches' +0); the neighbours of A (against B's point in A's frame), then of B: Pm_P = P - Pm, dist = Pm.Pm_P; for e
  = prev(opp(prev(Pm))) .. prev(Pm) (each next e = prev(opp(e))): grad = tp.Pm_P - dist > 0: grad x (1 / sqrtf((tp
  - Pm)^2 + 1e-18)) > best: keep. None: both synapses points, 1. Else s of the edge for its point: s1 <= 0 -> the
  same end ("epsilon problem"); s0 < 0: sort to the edge's cache, PP(edge, point); else sort to the point's,
  Leave_PK(point, edge).
- **PK 0x100b6070**: the point into K's frame, s: s0 < 0 PP(P, K), s1 < 0 PP(P, next K), else Leave_PK.
- **Leave_PK 0x100b62d0**: loop check (0, P, 1, K); vk, vP, vt (K's triangle's third point), vo (prev(opp K)'s
  start); hesse_tri = vk x vt, hesse_oppo = vo x vk (products as the code forms them); vert0 / vert1 = their dots
  with vP; qr of K's and opp(K)'s triangles; qr0[0] > 0: (qr1[0] > 0 and vert1 > 0 ? PF(P, opp K) : PF(P, K)); qr1[0]
  > 0: PF(P, opp K); vert0 < 0 and vert1 < 0: point / backside, pos_opposite = P in K's frame, 3. lot = vk x vP, iqk
  = 1 / vk.vk, q = lot.lot x iqk; q > 1e-10: len = (1 / sqrtf(q)) q - sum_r, plane = world(vk x lot) x -(inv iqk);
  else len = -sum_r and plane = normize(v x vk) with v = vk's largest |component| (from z down, strictly larger)
  negated and swapped with the one before it (normize 0x100755c0: unchanged below 1e-10). cddc; max = q x 1e-6; lot
  (world, or the raw one in the else) into P's frame; P's edges as in PP: angle = v.lot > 0: angle / sqrtf(v.v) >
  max: keep. Found: if 0.003 > max, the KK values of (K, found) (KK input with cK, cP): a fault or checks_L[0] < 0 ->
  end; KK(found, K, cP, cK). End: point / edge, 1.
- **IVP_KK_Input 0x100794a0**: K's direction to world and into L's frame (+0x30), K's two points into L's frame
  (+0x10 / +0x20), L's points (pointers, +0 / +4), L's direction (+0x40), cross (+0x60: (Lz Ky - Kz Ly, Kz Lx - Lz
  Kx, Kx Ly - Lx Ky)), +0x50.. K, L, cK, cL. **calc_unscaled_KK_vals 0x100799d0**: |cross|^2 <= 1e-6 -> a sampled
  fallback that returns 0 (TODO(trace): its writes, which KK reads anyway); A = Kv x c, B = Lv x c; checks_L = ((sl0 -
  sk0)(sl0 - sl1), (sk0 - sl1)(sl0 - sl1)) (A dots, no FLT_MIN), checks_K = ((tk0 - tl0)(tk0 - tk1) + FLT_MIN, (tl0 -
  tk1)(tk0 - tk1) + FLT_MIN) (B dots). 1.
- **KK 0x100b3070**: L inside (both checks_L sign bits clear): checks_K[0] < 0 PK(K, L), [1] < 0 PK(next K, L), else
  Leave_KK. K inside: sort to L; **checks_L[0] < 0** PK(L, K) else PK(next L, K) (as the source; round 1 read [1], which
  corner-roll's walk disproved: it cycled PP -> Leave_PK -> PF -> Leave_PF -> KK -> PK until the counter ran out). Both outside:
  pkp / pkm by checks_K[1] > checks_K[0], plp / plm by checks_L; pkp against L inside: PK(pkp, L); plp against K
  inside: sort L, PK(plp, K); s_kL[0] x checks_L[0] < 0: PP(pkp, plm); s_lK[0] x checks_K[0] < 0: sort L, PP(plp,
  pkm); else PP(pkp, plp).
- **Leave_KK 0x100b36f0**: loop check (1, K, 1, L); val = (L0 - K0).c, side = its sign bit, iHQ = 1 / sqrtf(c.c);
  H world (L's rows), into K's frame; len = fabsf(iHQ val) - sum_r; plane = ((f32(side) - 0.5) doubled x iHQ) x H_ws;
  cddc; L's points into K's frame; the four cases (+0 F, +4 P, +8 P_Fos, +0xc cP, +0x10 cF, +0x14 H_Fos, +0x20 the
  hesse; stride 0x30): [opp K, L, L_Kos0, cL, cK, H_Kos], [K, opp L, L_Kos1, ...], [opp L, K, K_Los0, cK, cL, H_Los],
  [L, opp K, K_Los1, ...]; hesse = (next - start) x (prev - start); reverse[i] = signbit(H.hesse) ^ side for 0, 1,
  (1 - signbit) ^ side for 2, 3; best grad (from -4e-6): ce = cases[(i ^ side) ^ reverse[i]], e = P_Fos(i ^ side) -
  P_Fos(i ^ side ^ 1), delta = e.hesse_i < 0: grad = (delta / sqrtf(e.e)) x (1 / sqrtf(h.h)); smaller and qr(F_i,
  ce.P_Fos)[0] > 0: keep (ce's P and cache, F_i and its cache, the qr). None: both edges; reverse[0] + [1] == 2: K
  backside, L triangle, pos = sl L_Kos1 + (1 - sl) L_Kos0 (sl = checks_L[0] / (checks_L[1] + checks_L[0])), 3;
  reverse[2] + [3] == 2: K triangle, pos from K's points by sk, L backside, 3; else 1. Found: sort to the edge's;
  qr inside: Leave_PF(edge, its point in F's frame, F); qr[2] >= 0: KK(edge, next F); qr[1] >= 0: KK(edge, prev F);
  else (100b48de) q1 = calc_qlen_KK(edge, next F), q2 = calc_qlen_KK(edge, opp(prev F)) (both with the edge's and
  F's caches): q1 > q2: KK(edge, prev F), else KK(edge, next F) (no scenario reaches it yet).
- **PF 0x100b1ca0**: P into F's frame; qr inside: Leave_PF; else the nearest of F's edges by calc_qlen_PK_K_space
  **0x1007a9b0** (outside the edge: |p - nearer end|^2; inside: |(p - a) x (b - a)|^2 / (|a - b|^2 + 1e-18)), from
  1e20, strictly smaller; PK(P, it).
- **Leave_PF 0x100b26d0**: loop check (0, P, 2, F); h = hesse(F), fast-normized when >= 1e-10; plane = world(h);
  h_Pos = into P's frame; len = h.P_Fos - h.F0; negative: h_Pos x -1; len -= sum_r; cddc; P's edges: dist = v.h_Pos <
  0: dist / sqrtf(v.v) < min (from 0): keep. None: point / triangle; len + sum_r < 0: pos = P_Fos, F backside, 3;
  else 1. Found P2: qr(F, P2's point): inside: Leave_PF(P2); one negative check (not >= 0): KK(P2, that edge); else
  (100b2fbf) over F's edges from F (next) whose qr is not > 0: calc_qlen_KK(P2, e, cP, cF), the strictly
  smallest from 1e20 wins: KK(P2, it).
- **calc_qlen_KK 0x1007ac30** (ecx K, edx L, K's cache, L's; minimize_qkk.rs): the KK input and calc_unscaled_KK_vals;
  checks_L both sign bits clear: 0 >= checks_K[0]: calc_qlen_PK_K_space(L's ledge, L, K_Los0); 0 >= checks_K[1]: the
  same with K_Los1; else **0x10079920**: c = cross (+0x60), q = (cx cx + cy cy) + cz cz; q > 1e-12: (k - l)^2 / q
  with k = (K_Los0y cy + K_Los0x cx) + K_Los0z cz and l the same of L0, else PK_K_space(L's ledge, L, K_Los0). checks_K both
  clear: 0 >= checks_L[0]: L's start point world (L's cache) then into K's frame, PK_K_space(K's ledge, K, it); 0 >=
  checks_L[1]: next L's; else IVP_ASSERT (line 0x2a2) and on. General: from 1e20, for L's two points (L, next L) in
  K's frame: d = PK_K_space(K, it), min = d < min ? d : min (minss d, min); then d2 = PK_K_space(L, K_Los_i), min =
  min < d2 ? min : d2.
- **recalc_mindist 0x100982d0**: the table's case; 1 (OK): bits &= 0xffff3fff, 1, no rescue; else bits = (bits &
  0xffff7fff) | 0x4000; 2 (endless): the rescue check; 3 (backside): **pierce** (0x100983ee): the synapse sorted 0
  unless its status (+0x1a) isn't 5, then sorted 1: its edge = **minimize_on_other_side 0x10099e60**(edge, &the
  walk's backside position (+0x10 of the minimize struct)), its status 2, the walk again with the same counter (the
  struct's +4 isn't reset); a second backside: the rescue check, 3. Anything else asserts (lines 0x136 / 0x139) and
  walks again. The rescue check: not a phantom (bits & 0x3000 != 0x1000) and not hull recursive (bits & 0x3c0000 !=
  0x100000): slot 5, mindist_rescue_push 0x100980a0 (section 10).
- **minimize_on_other_side 0x10099e60**: a byte per triangle (alloca'd, n = the ledge's +0xc i16, zeroed by
  0x100bdae0); the start = the first edge of triangle pierce_index (the backside triangle's word 0 bits 12..23: ledge
  + 0x14 + 16 index); loop: mark the triangle (its index, word 0 & 0xfff), qr of the point against it (qr_vals' sums
  and its edge-index tables 0x100f1b07..), for its edges from the start (next): qr <= 0 (not > 0) and opp(e)'s
  triangle unmarked: start = opp(e), loop; none: return the start.

## 6. Hull managers (hull.rs, collide.rs)

**IVP_Hull_Manager** (object +0x48): +0 last_vpsi_time (f64), +8 gradient, +0xc center_gradient, +0x10
hull_value_last_vpsi, +0x14 hull_center_value_last_vpsi, +0x18 hull_value_next_psi, +0x1c time_of_next_reset
(int), +0x20 **IVP_U_Min_List** (+0 u16 malloced, +2 u16 free list, +4 elements of 16 bytes: u16 long next / long
prev / next / prev, +8 f32 value, +0xc the listener; +8 the minimum, +0xc the long list's first, +0x10 the first,
+0x14 an insert counter). **0x100a68e0** add: a value <= the minimum goes first, else before the first element with
value >= it (a value goes before its equals); 0x100a6bb0 removes.

Listener values are "the hull value now + a distance": f32(t - last) x gradient + hull_value_last_vpsi + d
(0x1009a420 for the OV element, 0x100b77f0 for the OO synapses, 0x10095fc0 for a mindist's).

**The PSI's part** (IVP_Core's next PSI 0x100970f0 after the quaternion): **0x100975f0**(core, the step's rotation
quaternion's vector part v; the rows are stage 2's): n = |v|^2 > 1e-10: a = (1 / sqrtf(n)) n, rate = (((a^3 a^2)
0x3eceeb70 (0.40414)) + (a^3 0.16666667 + a)) doubled x core+0x138, the axis +0x120 = rows v x (1 / sqrtf(n)); else
(1, 0, 0) and 0; +0x5c = rate, +0x1a4 = core+8 x rate (core.rs surface_speed). Then (0x100974e3) g = (+0x1a4 + +0x13c)
x 1.00001 (0x3f800054) for each of the core's objects (last first): d = f32(t - last), last = t, hvl += gradient d,
gradient = g, cvl += center_gradient d, center_gradient = +0x13c, next = g dt + hvl; due when min - next < 0 (the
manager pushed on the PSI's list).

**Stage 4** (**0x10097db0**, each due manager from the list's end): while min - next < 0 (at most the settings' budget,
env+0x24+0x14, more from env+0x20 slot 4: not reached), the first listener's slot 1 with that (negative) value; then
when (double)time_of_next_reset < last: **reset 0x10093bb0** (a = -hvl, b = -cvl: every value a + value, each
listener's slot 3 (a, b): a mindist's sum_angular_hull_time += a - b (0x10095750); the OV / OO listeners' are stubs),
minimum and next + a, hvl = cvl = 0) and time_of_next_reset = (int)(last + 10).

**The mindist's hull event 0x100957c0** (hull recursive: 0x100b1b30, not ported): sorted cores c0 / c1; speed_i =
(+0x1a4 + +0x13c) + 1e-10, speed = speed1 + speed0; unless disable_halfspace: the centres at t (pos + delta f32(t -
t_psi)), new cddc = (c0 - c1).plane, the angular hull times (gradient - center_gradient) f32(t - last) + (hvl - cvl)
of both (sum = a1 + a0), est = ((len - (sum - sum_angular)) - (cddc - new cddc)) + value; est > (env dt x speed) x 6:
sum_angular = sum, cddc = new, len = est - value, f = est / speed, each sorted synapse re-inserted at its object's
hull now + f x its speed; return. Else both synapses out of their managers, insert_and_recalc_exact_mindist (or the
phantom one).

**insert_hull_mindist(md, h) 0x100960d0**: synapse 0's object not moving (+0x44 & 7 == 0): (0, h); synapse 1's not:
(h, 0); else s_i = (+0x1a4 + +0x13c) + 1e-10, k0 = s1 0.1 + s0, k1 = s0 0.1 + s1, f = h / (k1 + k0), (f k0, f k1).
**0x10095fc0**(md, t0, t1): status hull (bits & 0xffd7ffff | 0x140000); synapse 0 into its object's manager at hull
now + t0, synapse 1 at + t1; sum_angular_hull_time = angular1 + angular0.

**The OO watcher's event 0x100b77f0** (IVP_Synapse_OO slot 1 0x100b77e0): env+0x7c += 1; the range manager's split;
create_exact_mindists(obj0, obj1, r0 + r1, the watcher's vector) (single ledges: the pair's mindist kept, see 9); both
synapses re-inserted at hull now + r0 / r1. **The OV element's event** (0x1009a4c0): recheck_ov_element (section 4).

## 7. update_exact_mindist_events 0x10095310 (collide.rs)

(md, allow_hull_conversion, hint 0 NOW / 1 SMALL_DELAY / 2 BIG_DELAY.) Sorted cores c0 / c1; the event solver's
inputs on the stack (ebp-0x40: +0 sum = msrs0 + msrs1, +4 projected centre speed, +8 max collision speed, +0xc
worst = (speed0 + sum) + speed1, +0x10 md, +0x14 env, +0x18 t_now, +0x20 t_max (env+0xf8), +0x28 type out, +0x30
time out). A queued event is removed. coll = coll_dists[selector] (0x1010d138); len > (env dt x worst) x 2.1 + coll:
allowed -> remove_exact_mindist 0x10095e60 and insert_hull_mindist(len - coll); return either way. pcs = plane.v1 -
plane.v0 (core +0xd0), rot_i = sqrtf(1.001 - (axis_i.plane)^2) x msrs_i, mcs = (rot0 + rot1) + pcs; speed_after_keeper
> mcs and 1e-10 > mcs: return; f32(t_max - t_now) x mcs + coll <= len: return; phantom: return; selector != 0: the
counter env+0xc4 (+1; past 2: selector - 1, counter 0); calc_time_of_next_event; no type: return. f32(time - t_now) <
1e-6: NOW -> time = t_now; else d = len - real_coll_dist: BIG or (type & 0xf) != 0: d >= 1e-6 ? ((double)(d / worst)
+ t_now) + (double)((base x 1e-4) dt) : (double)((base x 0.001) dt) + t_now; else d >= 1e-6 ? ((double)((d 0.1) /
worst) + t_now) + (double)((base 1e-7) dt) : (double)((base 1e-5) dt) + t_now; f32(time - t_max) >= 0: return.
Queued at f32(time - the time manager's base) (0x100a68e0 on the time manager's list), +4 = its index, the low byte
of +0x14 = the type.

**ivp_mindist_settings** (0x1010d130.., the DLL's runtime values; collision tolerance 0.00635 m): +0 real_coll_dist
0x3a266515, +4 min_coll_dists and +8.. coll_dists[64] 0x3bcffe5a, +0x108 minimum_friction_dist 0x3bcffe5a, friction
0x3c4ffe5a, keeper 0x3c6f314e, speed_after_keeper 0x3f143f75 (+0x114), keepers_safety 0x38851daa, max_friction
0x3ce9fe25 (+0x11c), max_impact_system 0x3e0efede, mindist_change_force_dist 0x3a266515 (+0x124), min_vertical_speed
0x3c4ffe5a, max_spawned 1000, event_queue_min_delta_time_base 1.0f (+0x130). TODO(trace): the call that sets the
tolerance (the values are taken as the DLL holds them).

## 8. The event solvers (mindist_event.rs)

**calc_time_of_next_event 0x10093ce0**: table 0x10110bb0[sorted0 status x 4 + sorted1 status] (0x100a5610):
polygon pairs 0x100a53e0, balls 0x100a51b0 / 0x100a5330, the rest 0x100a55f0. **0x100a53e0**: both m_caches (made /
refreshed), type out = 0; by the statuses: PP **0x100a35c0**, PK **0x100a3f40** (mindist_event_pp.rs, transcribed from the
disassembly; PK's 0x32 checked by drop-corner, PP's types 0x10 / 0x11 not reached by any scenario yet: no hunt found
one), PF **0x100a2160**, KK **0x100a2d90**.

**The samplers 0x100a12c0** (0x5b0 bytes each): +0 object, +4 core, +0x10 the cache's time code, +0x14 21 matrix
pointers (t_now + 0.005 i), +0x70 storage (64 bytes each); a static object: every slot the cache's matrix; a moving
one: slot 0 the cache's, the others made on demand by 0x10074000 at their time.

**IVP_3D_Solver** objects: +0 vtable (slot 0 get_value(A matrix, B matrix), an x87 return of a stored f32), +4 the
max deviation, +8 its inverse, then the case's data.
- **find_first_t_for_value_max_dev 0x100b72a0**(value, index, A, B, opt start value, out, t0, t_max): v (given or
  sampled at the index); value >= v: out = t0, 1. d = (v - value) x inv; (double)f32(t0 - t_max) + d > 0: 0. Loop: d
  doubled; past t_max -> f32((double)f32(t_max - t) + 0.003); n = (int)(d x 200) (at least 1); index += n; t' =
  (double)(f32(n) x 0.005) + t; sample; value >= v': **0x100b7130**(out, v', A, B, t, t') then f32(out - t_max) > 0 ->
  0, else 1; index 20: 0; else v = v', t = t', d = (v' - value) inv, the same past-t_max test.
- **0x100b7130** (regula falsi): t = ((double)f32(t1 - t0) x (double)(value - v0)) / (double)f32(v1 - v0) + t0; every
  fourth step (n & 3 == 3; past 64 steps: t0) t = (double)((f32(t0 - t) + f32(t1 - t)) x 0.375) + t; both poses by
  0x10074000; |v - value| < 0.003: t; v >= value: (t0, v0) = (t, v), else (t1, v1).
- **find_first_t_for_value_coll 0x100b7510**(value, lower, A, B, opt, out, t_now, t_max): v0 > value: the max-dev
  search from slot 0; else (0 > f32(t_now - t_max), else 0) step from t_now with d = (v - lower) / max_dev (past t_max
  as above, else maxss(d, 0)), the same n / index / t'; v' > value: f32(t' - t_max) > 0 ? 0 : the max-dev search from
  that slot, v', t'; v0 >= v': out = the previous time, 1; else continue while 0 > f32(t' - t_max).

**KK 0x100a2d90**: spin = core0 +0x5c + core1's; K / L's start points, unit directions ((1 / sqrtf(q)) x when q >=
1e-10); the side at t_now: c = K_w x L_w (the caches' rows), s = -(c.plane) > 0 -> sign -1, flag 0, else 1, 1.
KK_COLL (vtable 0x100f2bc4, value 0x100a2930: c = K_w x L_w, ((inv (c.Kp_w - c.Lp_w)) x sign), +4 = mcs, +8 = 1 /
mcs) through 0x100b7510 (coll_dists[selector], real_coll_dist) up to t_max: type 0x40. KK_PARALLEL (0x100f2bb0,
0x100a2c30: |K_w x L_w|^2; max dev (spin + spin) + 1e-10) through 0x100b72a0 for 1e-10, up to the time found: 0x41.
Four KK_PF (0x100f2ba8, 0x100a1520: A's direction.B's normal (both world), max dev spin + 1e-10): i = 0..3 the
faces opp K, K (K's ledge; A = L's sampler with L's direction) and opp L, L (L's; A = K's with K's direction), the
direction negated when the flag (flag, 1 - flag, flag, 1 - flag) is 0, the normal = unit hesse; value -(the edge
object's core +0x44 x mindist_change_force_dist): 0x42.

**PF 0x100a2160**: spin; PF_COLL (0x100f2ba4, 0x100a1330: (P_w - F0_w).n_w; +4 mcs) through 0x100b7510 for coll +
sum_r (lower sum_r 0.5 + real_coll_dist), started from len + sum_r (no sample): 0x20. PF_NPF (0x100f2bb4, 0x100a2040:
the edge's unit direction (P's frame) . the face normal brought into P's frame; max dev spin + 1e-10): target
(-(F's core +0x44 x change_force) x (sum_r 0.1 + minss(len, coll))) / coll; for P's edges e = opp(prev P), then
opp(prev e) until e == P: d = next(e)'s point - P's, c = (d.n_P) / sqrtf(d.d); f32(t_out - t_now) x max dev > c: the
max-dev search from c up to t_out: 0x21.

## 9. Time, the PSI's collision stages, the hand-off

**Time codes**: env+0x108 (1 at the environment's ctor 0x1008441e) += 1 for each time event the loop **0x10085440**
runs (the PSI is one) and once when the loop ends (it also sets env+0xf0 = the end); IVP_Core::set_matrix 0x10097750
and 0x10014614 / 0x10084c1a also count (not reached here). The time manager (env+4): +8 a pointer to its min list,
+0x18 the base (the PSI's time once it runs): an event runs at base + (double)value while f32(until - base) > the
minimum.

**A PSI** (crazykart-physics.md 9) with collisions: stage 1 the revivals (section 4's creation), stage 3 each core's
next PSI and its objects' hull managers, stage 4 the due managers, **stage 5 recalc_all_exact_mindists 0x100952d0**
(each exact mindist from the head: recalc_exact_mindist 0x10096400: recalc, a failure -> slot 7), **stage 6**
update_exact_mindist_events(1, SMALL_DELAY) for each exact one. 0x100951f0 (stage 1's end) is
recalc_all_exact_wheel_mindist (the wheel vector: empty).

**simulate_time_event 0x10095dd0** (the mindist's slot 0): env+0x28 slot 1 (8); recalc_mindist; recalc OK:
coll_type & 0xf == 0 (a collision type: 0x20, 0x40): len < coll_dists[selector] + mindist_change_force_dist ->
**do_impact (slot 8, 0x1008b020)**; else update_exact_mindist_events(0, BIG_DELAY); other types (0x21, 0x41, 0x42):
update_exact_mindist_events(0, SMALL_DELAY); env+0x28 slot 1 (0xe).

**The hand-off** (for the impact / friction port): `ecx = the mindist; call [vtable + 0x20]` (do_impact 0x1008b020, no
arguments), inside the time event at env+0xf0 = the event's time and env+0x108 just incremented, right after the
recalc. What it can read, as collide.rs leaves it (Collide.impacts = {md, time}): the mindist's sorted synapses
(syn[sorted(0 / 1)]: object, edge, status) and their ledges, len_numerator (+0x5c, < coll + change_force),
contact_plane (+0x60, unit, from synapse 1's side toward synapse 0's: d = A - B in PP), contact_dot_diff_center
(+0x54), sum_extra_radius (+0x50), coll_type (the event's), coll_dist_selector; both objects' caches at that time
(Collide::objs[o].cache: rows, origin, core position; time code = env+0x108); the cores (speed +0xd0, rot +0xc0,
+0x13c, +0x1a4, +0x120, +0x5c, the PSI pose). In the DLL do_impact then pushes both cores, makes a friction contact or
not, and itself re-plans the mindist's event (flat-drive's ev 0: type 0x42 queued at base + 0x3c0443da): the
contacts port must do that update (update_exact_mindist_events) and Collide::simulate continue the loop
(collide.rs stops at the first impact today).

**Ported since** (ivp-impact.md): do_impact and everything after it; Collide::simulate carries on past an impact
when the contacts side is on (Collide::friction), and stops at the first one without it (mindist_check's hand-off).

**Not ported / not read**: section 10.

## 10. Round 2: the OV pairing, the ledge tree test, the walk's leftovers; what is left

**The OV element and its pairs** (collide_create.rs, recheck_ov): recheck_ov_element 0x10094de0 re-inserts the element
with real_check_sphere = f32(range slot 1) + core radius; insert_ov_element 0x1009b200 places it in the cube tree
(the node 0x1009a660 for that one radius: with min == max it returns the radius) and the collector 0x1009aff0 /
0x1009af10 walks the tree's nodes, testing each element by its sphere: ((dy^2 + dx^2) + dz^2) <= (r + r')^2. A node's
cube contains every element sphere in it, so the walk is exhaustive and the port tests every other element's sphere
directly (the grid's cell sizes, the powers of two at 0x10110b0c, never change which pairs come out; the tree's own
layout isn't modelled). The pairs: filtered by movement (either object's +0x44 & 7) and ShouldCollide (yes here);
an existing OO watcher kept, a new one made (ctor 0x100b7930: synapses at hull now + 1e20, then its event 0x100b77f0:
the range split, create_exact_mindists with r0 + r1, both synapses at hull now + their range), one no longer met
deleted (its mindists ~IVP_Mindist 0x10093fb0). The element's own synapse at hull now + (rcs - radius) (0x1009a420).
The box's OV value is no longer read from the dump.

**create_exact_mindists 0x10094300** with get_all_ledges_within_radius (compact surface manager slot 4 0x10078bc0 ->
the ledge tree walk 0x100789b0): the visitor = the other core's position at t (pos + delta f32(t - t_psi)) in this
object's frame; radius (extra0 + core1 radius) + scan and (core0 radius + extra1) + scan; a node is in when ((dy^2 +
dx^2) + dz^2) <= (node radius + r)^2 and on each axis |d| < f32(size byte) x (node radius x 0.004) + r
(ledge.rs TreeNode: +8 centre, +0x14 radius, +0x18 three size bytes; the kart's from its .phy, the box's from the
dump's tree root). drop-high needed it (the kart's ledge is out of the floor's radius for 86 ticks).

**exact_mindist_went_invalid 0x10094bc0** (slot 7): remove_exact_mindist 0x10095e60, insert_invalid_mindist
0x10094b40: status (bits & 0xffcbffff) | 0x80000, at the head of the manager's +0x14 (mindist +0x74 / +0x78), both
synapses at the head of their objects' +0x24 synapse lists (synapse +8 / +0xc; not modelled). Called by
insert_and_recalc_exact_mindist and recalc_exact_mindist 0x10096400 (non-phantom: bits & 0x3000 == 0; recalc_result
bits & 0xc000 set). c10 (hunt) reaches it at the creation: bits now match.

**mindist_rescue_push 0x100980a0** (slot 5): the environment's anomaly manager (env+0x20): speed = slot 7 (+0x1c)
(object 0 (+0x28), object 1 (+0x44)), x87; then slot 2 (+8) (mindist, object 0, object 1, f32 speed): the
inter-penetration push, which changes the cores' velocities (the impact side's code: not ported, reported). No RTTI
in this build to name the manager's class; its vtable is unread.

**Scenarios** (rubikon/tests/KartOracle/scenarios, the floor box -4096..4096 x -64..0): drop-edge (the kart at the
box's edge), drop-corner (4115 4115 18, 30 45 20: PK's 0x32), corner-roll (4108 4108 24, 0 45 35: KK's K-inside
branch), corner-roll-left (0 45 -35: Leave_PF's two-sided exit), corner-pierce (35 45 180: the creation's pierce).
Hunts kept out of the repo (scratchpad): 22 more corner poses, all bit-identical to the first impact or 90 ticks
without one, except one (4095 4115 24, -80 120 10) that reaches the rescue push at the creation.

**Left** (each reported by `Collide::untraced` when reached):
- mindist_rescue_push's anomaly manager (above); (ported 2026-11-18: section 14) FF 0x100984c0;
  KK_vals' parallel fallback 0x10079be4 (ported 2026-11-17: 12 below); the PP event
  solver's paths (no scenario); Leave_KK's two-sided exit (ported, no scenario); the balls, phantoms (0x10094cf0).
- (ported 2026-11-17: ivp-pileup.md 5) the invalid list's recheck: 0x10073a50 in every PSI's stage 2, 0x100980e0, 0x10094a70.
- (ported 2026-11-17: 13 below) IVP_Mindist_Recursive 0x100b18a0 / 0x100b14f0 and its hull event 0x100b1b30 /
  0x100b1a00, create_exact_mindists' fixed-ledge arguments; the delegator roots' choice (OO watcher vs a direct mindist); the stage-4 budget; deletions beyond
  ~IVP_Mindist (hull_manager_is_going_to_be_deleted 0x100957a0).

## 11. Ledge trees: the map's own world (ported 2026-11-17: ledge.rs Surface, collide_create.rs)

The world is a compact surface with a ledge tree of many convex ledges (ze_crazykart_v4's BSP model 0: two solids,
1.3 MB and 30 KB; crazykart-physics.md 14). **IVP_Compact_Ledgetree_Node** (0x1c bytes): +0 offset_right_node (0: a
leaf), +4 offset_compact_ledge (0: none), +8 centre, +0x14 radius, +0x18 box sizes (3 bytes, units of radius x
0.004), +0x1b unused; the left child is the next node (+0x1c). A compact ledge's +0 c_point_offset reaches one point
array every ledge of the surface shares (so point indices are global: the port shares it, `Ledge::points` an Arc).
+8 bits 0-1 has_children: an inner node's hull of everything below it.

**get_all_ledges_within_radius** (the compact surface manager's slot 4 **0x10078bc0**: from the root when its node
argument is 0) -> the walk **0x100789b0** (thiscall-like, xmm3 the radius, its stack (node, visitor, list)),
from the disassembly: d = centre - visitor; ((dy^2 + dx^2) + dz^2) > (R + r)^2 -> out; k = R x 0.004
(0x100f3be0); per axis |d| (0x10001930) >= f32(size) k + r -> out; a node with a ledge (+4 != 0) adds it
(0x1002bed0, the vector's push) and stops (an inner node's hull too: no descent); else the left child
recursively, then the right in the same loop. A leaf without a ledge (0x10078b37) would read the node as a ledge:
the port refuses such data at load.

**create_exact_mindists 0x10094300** (fastcall object 0, object 1; stack: the collision's mindist vector, a fixed
ledge for side 0 / 1 (0 here; IVP_Mindist_Recursive passes them), the two visitor flags, the delegator (md+8)):
side 0's ledges within (obj0 +0x90 + core1 +4) + scan of core 1's position at t in object 0's frame (the cache
refreshed when movement < 8 and its stamp < env+0x108), then side 1's likewise. The diff hash **0x10096850**
(over the collision's vector, last to first: key = l1 x 0x4b ^ l0 of each mindist's slot 2 **0x10094110** (the
ledges of its synapses at +0x18 / +0x34, from the edges: edge & ~0xf - (tri_index + 1) x 16), h = ((key >> 8
signed) x 0x3ff + key) & mask, linear probing; size: n = (len0 x len1 + count) x 2 + 2, s = 0x400 halved while n <
s) and its lookup **0x10096710**: found at index j, the mindist is swapped with the vector's entry at `kept`
(this+0x10) when kept < j (the hash slots and both mindists' back indices +0xc / +0x10 fixed), kept += 1. So the
kept ones end at the front in lookup order and the pointers only steer the probes: the port searches the vector.
The pairs run side 0's list last to first, side 1's last to first inside; a pair not found becomes a new mindist
(both ledges terminal: new 0x80 bytes, init_mindist 0x10094150 from the two first edges, which itself calls
insert_and_recalc_exact_mindist 0x10094be0 (0x100942c5), so it is inserted at once, inside the loop; then +0x50 +=
0 (a recursive one: 4 x real_coll_dist); either a hull: new 0xa0 IVP_Mindist_Recursive 0x100b18a0, panics in the
port). Then the vector's mindists from the end down to `kept` are deleted (slot 4 (1), ~IVP_Mindist 0x10093fe0,
which takes itself out through the delegator's slot 0: OO watcher +0x14's vtable 0x100f2f1c, 0x100b7b10 ->
**0x1009b470**: swapped with the vector's last, here always the last), and the new ones appended last to first
(+0xc, or +0x10 when +0xc is set, takes the index).

**The revival's speeds** (collide.rs simulate): the creation at a revival runs in stage 1, before the
controllers; the core it reads has the speeds from before the PSI (probe 0x1009552b: mcs 0 for a kart woken on the
floor, so update_exact_mindist_events returns before the selector counter). The port's snapshot used to carry the
PSI's gravity in its speed (no box scenario made a mindist close enough at a revival to notice).

**Checked** (ivp_check's world mode, ivp_ground.rs pairs every mindist with the dump's by its synapses' objects and
ledges, the ledges matched by their words): world-hub (400 ticks: the drop at the spawn hub, the drive into a wall,
the turn, the brake, the jump; 9 mindists at the creation) and world-drive (1200 ticks: long hard turns into the
hub's walls, a shove, two jumps, asleep on the floor and woken) bit-identical every tick; the DLL's call sequence at
the creation (KART_ORACLE_CALLS=10094300,10094be0,10095310: two watchers, nine insert + update pairs, the stage-6
updates) matches the port's.

## 12. calc_unscaled_KK_vals' parallel fallback 0x10079be4 (ported 2026-11-17: minimize_kk.rs kk_parallel)

When |K_vec x L_vec|^2 <= 1e-6 (0x100f3bac, the cross at KK input +0x60, ((c0^2 + c1^2) + c2^2)) the function
samples instead and returns 0 (IVP_FAULT), its four checks written all the same (p_minimize_KK and calc_qlen_KK read
them; the one caller that tests the return, minimize.rs's edge step past 0.003, takes the fault as a no:
TODO(trace) that caller's address in this note). Samples: the floats at
0x100f4150 / 0x100f4220 / 0x100f4230 (on the stack at ebp-0xd8): -1, 0.5, 2, 0, 1, -0.001, 0.001, 0.999, 1.001,
-1e-6, 1e-6 (and 0.999999 0x3f7fffef, 1.0000005 0x3f800008, never read). The best starts at 1e20 (0x100f4010) and is
shared by both loops; a sample is taken only when best > q.
- **Along K** (11): s, u = 1 - s; P = (k1.x s + k0.x u, u k0.y + k1.y s, k1.z s + u k0.z) (K's points in L's frame,
  input +0x10 / +0x20); A = L1 - L0, D = P - L0 (L's points, its ledge's own); c = (D.y A.z - D.z A.y, D.z A.x - D.x
  A.z, D.x A.y - D.y A.x); q = (1 / ((((L0 - L1).x^2 + (L0 - L1).y^2) + (L0 - L1).z^2) + 1e-18 (0x100f3b84))) x
  ((c.y^2 + c.x^2) + c.z^2). Taken: checks_K = (s, u), checks_L = (-(((L0 - P).y A.y + (L0 - P).x A.x) + (L0 -
  P).z A.z) + FLT_MIN, (((L1 - P).y A.y + (L1 - P).x A.x) + (L1 - P).z A.z) + FLT_MIN) (the sign by xorps
  0x100f4310).
- **Along L** (9): L's points into K's frame once (world by L's cache (+0x5c's matrix, ((m0 x + m1 y) + m2 z) +
  t), then object by K's (+0x58's: the columns, d = w - t)), P = (b.x s + u a.x, b.y s + u a.y, b.z s + u a.z); the
  same q against K's own points; taken: checks_L = (s, u), checks_K = the ends of K against P as above.
Reached by world-hub's first PSI (a kart edge parallel to a brush edge) and checked by its ticks.

- ConvexFromVerts / ConvertConvexToCollide 0x1000a640 (the ledge soup: ctor 0x10044a30, insert 0x10044be0, compile
  0x10044c40) and set_collision_tolerance: the box's compact surface (mass centre (0, 0.8128, 0), inertia 0x46292145,
  radius 0x4313227f, dev byte 0xfa, tree root sizes (177, 2, 177)) is still read from the dump.
- the impact (do_impact 0x1008b020) and everything after it: ported, ivp-impact.md (with the freeze's collision side,
  0x10077820, and the revival's creation every time).

## 13. IVP_Mindist_Recursive: a ledge tree node's hull against a ledge (ported 2026-11-17: recursive.rs)

Reached when a moving ledge tree meets a kart: a mover's brush (docs/crazykart/ivp-shadow.md; kart-lift.txt). The
world's pairs never made one (its walk reaches terminal ledges near the kart). A 0xa0-byte mindist, vtable
**0x100f2ef8** (slots 0-3 the base's, 4 the dtor 0x100b1950, **5 0x10004410: no rescue push**, 6 0x10003fd0, **7
0x100b16e0**, **8 0x100b14f0**, 9 / 10 0x100b7b10 / 0x100b7b57) with an IVP_Collision_Delegator at **+0x80** (vtable
0x100f2ee8: 0 0x100b19f0 a child leaves +0x84 by 0x1009b470; 1 0x100b1c8d its dtor; **2 0x100b1c50**: +0x90 += d, then
the owner's (mindist +8) slot 2; **3 0x100b1c70**: the owner's slot 3 when above 0, else +0x90; an OO watcher's slot 2
is 0x10004450 (nothing), its slot 3 0x10015d30 (-1)). +0x84 the vector of its own mindists (+0x86 the count, +0x88 the
array), **+0x8c the side split** (-1 at first), +0x90 the count.

- **Made** by create_exact_mindists (0x10094300) for a pair with a hull ledge (+8 & 3): new 0xa0, ctor **0x100b18a0**
  (the base's fields as a plain one's, the env's +0x70 / +0x74 counts, the vtables, +0x84..+0x90 zero, +0x8c = -1),
  then the same init 0x10094150 (two first edges; insert_and_recalc_exact_mindist at once), then **+0x50 += [0x1010d130]
  (real_coll_dist, 0x3a266515 at run time) x 4.0 (0x100f3f18)**. So it lives as an exact mindist between the hull and
  the other ledge, its events as a plain one's.
- **create_exact_mindists' arguments** (vector, fixed0, fixed1, from0, from1, delegator): a side with a fixed ledge
  takes that ledge alone (its visitor, and so that object's cache refresh, skipped); a side with a "from" ledge is
  walked by get_all_ledges_within_radius **0x10078bc0** from that ledge's tree node (ledge +4): the node's left child
  (+0x1c) then its right (+[node]), not the root.
- **Slot 7 0x100b16e0** (exact_mindist_went_invalid's place): the count (slot 3) > [0x1010d25c] (1000 at run time):
  remove_exact 0x10095e60 + insert_invalid 0x10094b40 (a plain one's); else +0x8c = 1 when side 0's ledge is terminal,
  0 when side 1's is, else (r0 <= r1) with r = the ledge's tree node radius (+0x14; 0x100f4008 1e15 without a node):
  then **the split** (0x100b17a8): remove_exact, the range manager's slot 0 (obj +0x28, obj +0x44) -> (a, b),
  **0x10096180** with a + b, status HULL RECURSIVE ((bits & 0xffd3ffff) | 0x100000), **0x100b1a00** with a + b.
- **Slot 8 0x100b14f0** (do_impact's place): count > limit: the plain do_impact 0x1008b020. Else by the synapses' statuses (+0x32 side 0,
  +0x4e side 1; tables 0x100b16b4 / 0x100b16c4) the side whose closest feature is on the hull's virtual geometry (bit 31
  of the edge's dword, or of its triangle's: edge & ~0xf): side 0 point / ball against side 1 edge / triangle: side 1
  if that is virtual; side 0 edge against side 1 point / ball, or side 0 triangle: side 0 if its triangle is virtual;
  edge against edge: the virtual one, both virtual the radius rule; nothing virtual (and point / point): **no
  split: the plain mindist's do_impact 0x1008b020** (0x100b1574; corrected 2026-11-18, it read "no impact": a hull's
  real face is collided with as the hull ledge, which a displacement's hull needs, ivp-virtualmesh.md 3); other
  statuses assert (0x32 / 0x5d / 0x65) and split with the side it had. Then the split as above (0x100b1650).
- **0x100b1a00** (its mindists): count > limit: nothing; else create_exact_mindists over +0x84 with fixed[1 - side] =
  the other synapse's ledge and from[side] = the split side's (scan = the argument), then slot 2 (new - old count).
- **0x10096180** (insert_hull_mindist's form without the angular hull times): status HULL ((bits & 0xffd7ffff) |
  0x140000); each synapse inserted (0x100a68e0) at its object's **hull_value_next_psi (+0x60)** + its share: an object
  not moving (+0x44 & 7 == 0) takes 1e-10 (0x100f3b94) and the other the whole; else s_i = (core +0x1a4 + core +0x13c)
  + 1e-10, k0 = s1 x 0.1 (0x100f3c60) + s0, k1 = s0 x 0.1 + s1, f = hull / (k1 + k0), shares f x k0 and f x k1.
- **The hull event 0x100b1b30** (mindist_hull_limit_exceeded_event 0x100957c0 sends a status-4 mindist here):
  **0x100980e0** (recalc_mindist 0x100982d0's copy but for one store: P_Finish_Counter 0 instead of 20, ebp-0x83c);
  valid (bits & 0xc000 == 0) and len (+0x5c) > [0x1010d23c] (0x3c4ffe5a at run time): **0x100b1af0**; else the ranges
  (a, b; env+0x7c += 1), 0x100b1a00 with a + b, each hull synapse out (0x100a6bb0) and back at (f32(t - hm +0x48) x
  hm +0x50 + hm +0x58) + its range.
- **0x100b1af0** (the two apart again): **0x100b1810** (its mindists deleted last to first through their slot 4 (1),
  slot 2 with -count, the array freed), both hull synapses out, **insert_exact_mindist 0x10094a70** (status EXACT
  ((bits & 0xffcfffff) | 0xc0000) at the exact list's head, the synapses into their objects' exact lists (+0x20), and
  into the manager's +0xc vector when a core has +0x48 and it isn't a phantom), bits & ~0x3000.
- **The dtor 0x100b1980**: 0x100b1810, then ~IVP_Mindist 0x10093fe0 (its status table 0x100940d8: 2 the invalid
  list 0x10095f40, 3 remove_exact 0x10095e60, **4 and 5 both hull synapses out**).

**Checked** (2026-11-17, ivp_check on kart-lift.txt: a kart dropped onto finale_elevator1, driven on it while it goes
down, turns and climbs, 420 ticks): bit-identical every tick, the recursive mindist's creation inside the mover's
revival (SetShadow's UseShadowMaterial: the object at 0x21, so its exact mindist doesn't turn hull at once), its split
and children, the contacts on the lift.

## 14. p_minimize_FF 0x100984c0: two triangles (ported 2026-11-18: minimize_ff.rs)

Reached when both synapses are on a face: two bodies through each other (world-inside.txt: a kart made inside a solid
world brush and driven on in it, from tick 491). 1363 lines of disassembly, four brute-force passes over the two
triangles (F with its m_cache, G with its; an m_cache: +0 the points, +4 the ledge, +8 the cache object with rows at
+0x20 and the origin at +0x50, +0x10 the synapse: +0x14 its edge, +0x1a its status), each writing both synapses when
it finds a nearer pair, then the pair's own case:

1. **Point pairs** (0x10098504, F's point outer, edges walked by the next table 0x1010a988): both points to world
   ((m1 y + m0 x) + m2 z + origin per row), q = (dx^2 + dy^2) + dz^2 of F - G; nearer than the best (1e20 at first,
   `comiss best, q`: plainly below): both POINT.
2. **A side's points against the other's face**, F's points against G's face first (the arrays at ebp-0x104 /
   -0xe4 / -0xd4 hold the two orders). The face in its own frame: n = (next - start) x (prev - start) (the hesse
   products of 13's helper), the offset -((ny P0.y + nx P0.x) + nz P0.z), both x 1 / sqrt((ny^2 + nx^2) + nz^2)
   (0x10001950). A point (world, then into the face's frame by the columns) inside the prism
   (calc_unscaled_qr_vals_F_space on the face's edge, no sign bit): d = ((p.y ny + p.x nx) + p.z nz) + offset, q = d
   d; **q x 1.000001 < best**: the point POINT, the face's edge TRIANGLE.
3. **A side's points against the other's edges**, G's points against F's edges first: the point in the edge's
   frame, calc_unscaled_s_val_K_space (A the edge's start, B the next's); both without a sign bit: q = (1 / (|A -
   B|^2 + 1e-18)) x |(p - A) x (B - A)|^2 ((cy^2 + cx^2) + cz^2); q x 1.000001 < best: the edge EDGE, the point
   POINT.
4. **Edge pairs** (F's outer): IVP_KK_Input 0x100794a0 (K = F's edge, L = G's), calc_unscaled_KK_vals 0x100799d0
   (its return not read: the parallel fallback's checks count too); all four without a sign bit: 0x10079920's
   line distance inlined ((K0 . c - L0 . c)^2 / |c|^2, c = K x L in L's frame; |c|^2 <= 1e-12: K0 against the edge
   L, 0x1007a9b0); q x 1.000001 < best: both EDGE.

Then (0x1009929c) F is the first side, or G when G's status is POINT and F's isn't; sort_synapses makes that side
the sorted synapse 0 (bits ^ 0x100 when it isn't), and by (first, second): (0, 0) PP 0x100b4e20, (0, 1) PK
0x100b6070, (0, 2) PF 0x100b1ca0, (1, 1) KK 0x100b3070. Anything else is the DLL's "%s in contact with %s, crash.
dist = %d, minq = %lf" Error and IVP Failed (ivp_mindist_minimize.cxx lines 0x1e6 / 499 / 0x1fd / 0x207), returning 0;
pass 1 always leaves a pair, so it isn't reached.

Read from the decompile, with pass 1's sums and the comparisons from the disassembly; the inner sums are the helpers'
that were transcribed from the same inlined code elsewhere (cache.rs world / object, qr_vals, s_vals, hesse,
kk_input / kk_vals, line_qlen). They only choose the pair: the pair's own case computes what the mindist keeps.
**Checked**: world-inside.txt 1500 ticks bit-identical in ivp_check (every core field) and kart_world_check; the
kart sinks through the brush, the FF case runs from tick 491, and it drives on below.
