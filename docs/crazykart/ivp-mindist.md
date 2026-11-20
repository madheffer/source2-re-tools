# IVP: collision detection up to the impact

CS:GO legacy vphysics.dll (32-bit, md5 d97cf2194594d7545427cdabc7376db4, Ghidra `/csgo_vphysics_legacy.dll`, image
base 0x10000000), read from the disassembly (Ghidra, capstone). How it finds and tracks the distance between
ze_crazykart's kart and the world up to the impact (crazykart-physics.md 8-11 reads the same DLL). The leaked IVP
source (Havok / ipion) gave names only and differs from this build where said. Float math is SSE scalar single unless
noted; `(a + b) + c` is the disassembly's association (an add's operands commute: only the grouping matters).

## Functions

| Address | Module | What |
|---|---|---|
| 0x1000ad00 | vphysics | BBoxToCollide (collision slot 29); cache lookup 0x1000adf0 |
| 0x1000ab60 | vphysics | makes the unit box once: ConvexFromVerts 0x10008b50 of (-16, -16, 0)..(16, 16, 72), the corner byte map, ConvertConvexToCollide (slot 0x38) |
| 0x1000a860 | vphysics | a box from the unit box's ledge |
| 0x1000a640 | vphysics | ConvertConvexToCollide (ledge soup: ctor 0x10044a30, insert 0x10044be0, compile 0x10044c40) |
| 0x1006ccb0 | vphysics | cache manager: make an object's cache |
| 0x1006cd90 | vphysics | cache update |
| 0x1006ca90 | vphysics | quaternion at t (slerp) |
| 0x100723b0 | vphysics | rows from a quaternion |
| 0x10074000 | vphysics | get_m_world_f_object_AT (the event solvers' samples: lerp / slerp even at f = 0) |
| 0x100755c0 | vphysics | normize (unchanged below 1e-10) |
| 0x10001950 / 0x10001930 | vphysics | sqrt / fabs |
| 0x10093ce0 | vphysics | calc_time_of_next_event (table 0x10110bb0, filled by 0x100a5610) |
| 0x10093fb0 | vphysics | IVP_Mindist deleting destructor (slot 4) |
| 0x10093fe0 | vphysics | ~IVP_Mindist (status table 0x100940d8: 2 the invalid list 0x10095f40, 3 remove_exact 0x10095e60, 4 and 5 both hull synapses out) |
| 0x10094110 | vphysics | mindist slot 2: the ledges of its synapses |
| 0x10094150 | vphysics | init_mindist (calls insert_and_recalc_exact_mindist at 0x100942c5) |
| 0x10094300 | vphysics | create_exact_mindists (fastcall object 0, object 1) |
| 0x10094a70 | vphysics | insert_exact_mindist |
| 0x10094b40 | vphysics | insert_invalid_mindist |
| 0x10094bc0 | vphysics | exact_mindist_went_invalid (slot 7) |
| 0x10094be0 | vphysics | insert_and_recalc_exact_mindist |
| 0x10094cf0 | vphysics | insert_and_recalc_phantom (unread) |
| 0x10094de0 | vphysics | recheck_ov_element (this = the manager) |
| 0x100951f0 | vphysics | recalc_all_exact_wheel_mindist (stage 1's end) |
| 0x100952d0 | vphysics | recalc_all_exact_mindists (stage 5) |
| 0x10095310 | vphysics | update_exact_mindist_events(md, allow_hull_conversion, hint) |
| 0x1009552b | vphysics | (in it) the mcs test |
| 0x10095750 | vphysics | hull_manager_is_reset (synapse slot 3): sum_angular_hull_time += a - b |
| 0x10095780 | vphysics | hull_limit_exceeded (synapse slot 1) |
| 0x100957a0 | vphysics | hull manager deleted (synapse slot 2) |
| 0x100957c0 | vphysics | mindist_hull_limit_exceeded_event |
| 0x10095dd0 | vphysics | simulate_time_event (mindist slot 0) |
| 0x10095e60 | vphysics | remove_exact_mindist |
| 0x10095fc0 | vphysics | insert a hull mindist's synapses (md, t0, t1) |
| 0x100960d0 | vphysics | insert_hull_mindist(md, h) |
| 0x10096180 | vphysics | insert_hull_mindist without the angular hull times |
| 0x10096400 | vphysics | recalc_exact_mindist |
| 0x10073a50 | vphysics | the object's invalid list recheck, in every PSI's stage 2 (ivp-pileup.md) |
| 0x10096620 / 0x100964f0 | vphysics | recheck_ov_element's diff hash / lookup |
| 0x10096850 / 0x10096710 | vphysics | create_exact_mindists' diff hash / lookup |
| 0x10097750 | vphysics | IVP_Core::set_matrix (counts a time code) |
| 0x100970f0 | vphysics | IVP_Core next PSI |
| 0x100975f0 | vphysics | (core, rotation vector) the spin and surface speed |
| 0x100974e3 | vphysics | (in the PSI) the hull managers' update |
| 0x10097db0 | vphysics | stage 4: the due hull managers |
| 0x10098020 | vphysics | check_loop_hash (the list variant) |
| 0x100980a0 | vphysics | mindist_rescue_push (slot 5) |
| 0x100980e0 | vphysics | recalc_mindist's copy with P_Finish_Counter 0 |
| 0x100982d0 | vphysics | recalc_mindist; pierce at 0x100983ee |
| 0x100984c0 | vphysics | p_minimize_FF |
| 0x10099850 | vphysics | minimize_default_poly_poly |
| 0x10099c90 | vphysics | swapped (flip the sort flag, then the default) |
| 0x10099a60 / 0x10099c10 / 0x10099c50 / 0x10099aa0 / 0x10099cb0 | vphysics | P x B / K x B / F x B / B x {P, K, F} / B x B |
| 0x1009a120 | vphysics | illegal pair |
| 0x1009a140 | vphysics | fills the minimize table 0x10110a28 |
| 0x10099e60 | vphysics | minimize_on_other_side(edge, &backside position) |
| 0x1009a420 | vphysics | add_to_hull_manager (the OV element) |
| 0x1009a4c0 | vphysics | the OV element's event |
| 0x1009a660 | vphysics | OV node finder (min == max: returns that radius) |
| 0x1009aff0 / 0x1009af10 | vphysics | OV collector: the tree walk |
| 0x1009b200 | vphysics | insert_ov_element (returns the radius) |
| 0x1009b400 | vphysics | OV element out of the tree |
| 0x1009b470 | vphysics | vector remove (swapped with the last) |
| 0x10078bc0 | vphysics | compact surface manager slot 4: get_all_ledges_within_radius (root when node 0) |
| 0x100789b0 | vphysics | the ledge tree walk (xmm3 the radius; stack node, visitor, list); leaf without ledge 0x10078b37 |
| 0x1002bed0 | vphysics | vector push |
| 0x100794a0 | vphysics | IVP_KK_Input |
| 0x100799d0 | vphysics | calc_unscaled_KK_vals (parallel fallback 0x10079be4) |
| 0x10079920 | vphysics | KK line distance |
| 0x1007a9b0 | vphysics | calc_qlen_PK_K_space |
| 0x1007ac30 | vphysics | calc_qlen_KK (ecx K, edx L, K's cache, L's) |
| 0x100b4e20 | vphysics | PP |
| 0x100b6070 | vphysics | PK |
| 0x100b62d0 | vphysics | Leave_PK |
| 0x100b1ca0 | vphysics | PF |
| 0x100b26d0 | vphysics | Leave_PF (its edge fallback at 100b2fbf) |
| 0x100b3070 | vphysics | KK |
| 0x100b36f0 | vphysics | Leave_KK (its qlen fallback at 100b48de) |
| 0x100a10c0 | vphysics | range manager ctor (vtable 0x100f2b70) |
| 0x100a1150 | vphysics | range slot 0: intra(obj0, obj1, &r0, &r1) |
| 0x100a1240 | vphysics | range slot 1: in_world(obj) (x87 return) |
| 0x100a12c0 | vphysics | sampler setup (0x5b0 bytes each) |
| 0x100a53e0 | vphysics | event: polygon pairs (also refreshes caches) |
| 0x100a51b0 / 0x100a5330 / 0x100a55f0 | vphysics | event: balls / balls / the rest |
| 0x100a35c0 / 0x100a3f40 | vphysics | event PP / PK |
| 0x100a2160 / 0x100a2d90 | vphysics | event PF / KK |
| 0x100a2930 / 0x100a2c30 / 0x100a1520 | vphysics | KK_COLL / KK_PARALLEL / KK_PF get_value |
| 0x100a1330 / 0x100a2040 | vphysics | PF_COLL / PF_NPF get_value |
| 0x100a68e0 / 0x100a6bb0 | vphysics | min list add / remove |
| 0x100b72a0 | vphysics | find_first_t_for_value_max_dev |
| 0x100b7130 | vphysics | regula falsi |
| 0x100b7510 | vphysics | find_first_t_for_value_coll |
| 0x100b77e0 -> 0x100b77f0 | vphysics | IVP_Synapse_OO slot 1: the OO watcher's event |
| 0x100b7930 | vphysics | OO watcher ctor |
| 0x100b7b10 / 0x100b7b57 | vphysics | delegator remove (Recursive slots 9 / 10) |
| 0x10085440 | vphysics | the time event loop |
| 0x1008441e | vphysics | (env ctor) time code = 1 |
| 0x10014614 / 0x10084c1a | vphysics | also count a time code |
| 0x100778d0 | vphysics | revival creation (stage 1) |
| 0x10077820 | vphysics | freeze (collision side) |
| 0x1008b020 | vphysics | do_impact (mindist slot 8) |
| 0x100b18a0 | vphysics | IVP_Mindist_Recursive ctor |
| 0x100b1950 / 0x100b1980 | vphysics | Recursive dtor (slot 4) / its body |
| 0x100b16e0 | vphysics | Recursive slot 7 (split at 0x100b17a8) |
| 0x100b14f0 | vphysics | Recursive slot 8 (status tables 0x100b16b4 / 0x100b16c4; no split 0x100b1574; split 0x100b1650) |
| 0x100b1a00 | vphysics | Recursive: its mindists |
| 0x100b1b30 | vphysics | Recursive hull event |
| 0x100b1af0 | vphysics | Recursive: the two apart again |
| 0x100b1810 | vphysics | Recursive: delete its mindists |
| 0x10004410 / 0x10003fd0 | vphysics | Recursive slot 5 (no rescue push) / slot 6 |
| 0x100b19f0 / 0x100b1c8d / 0x100b1c50 / 0x100b1c70 | vphysics | Recursive delegator slots 0-3 |
| 0x10004450 / 0x10015d30 | vphysics | OO watcher delegator slot 2 (nothing) / slot 3 (-1) |
| 0x100bdae0 | vphysics | memset |

## Fields

| Offset | Field |
|---|---|
| IVP_Compact_Ledge +0 | c_point_offset (one point array shared by every ledge of a surface: indices global) |
| IVP_Compact_Ledge +4 | ledgetree_node_offset / client data (zeroed in a BBoxToCollide copy when the flags' low bits are 0) |
| IVP_Compact_Ledge +8 | flags: has_children 2 bits (an inner node's hull), is_compact 2, dummy 4, size_div_16 24 |
| IVP_Compact_Ledge +0xc / +0xe | n_triangles (i16) / unused; then 16-byte triangles |
| triangle +0 | tri_index:12 pierce_index:12 material:7 is_virtual:1 |
| triangle +4 / +8 / +0xc | edges: start_point_index:16 opposite_index:15 (signed, in edges: dwords) is_virtual:1 |
| point | 16 bytes (x, y, z, pad), IVP metres |
| IVP_Compact_Ledgetree_Node (0x1c) | +0 offset_right_node (0: leaf), +4 offset_compact_ledge (0: none), +8 centre, +0x14 radius, +0x18 box sizes (3 bytes, units of radius x 0.004), +0x1b unused; left child = next node (+0x1c) |
| .phy | VPHY header 28 bytes; compact surface +0x20 the ledge tree root offset (a single ledge: root a leaf, +0 == 0, +4 the ledge's offset) |
| IVP_Cache_Object (object +0x40) | +0 core position at t, +0x10 quaternion, +0x20 rows (stride 0x10; +0x20..+0x58 m_world_f_object: rows then position at +0x30), +0x50 the object's origin, +0x60 time code made at, +0x64 refcount, +0x68 the object |
| m_cache | +0 points, +4 ledge, +8 cache object, +0x10 synapse |
| IVP_Mindist (0x80) | vtable 0x100f2914: [0] simulate_time_event, [4] deleting dtor, [5] rescue push, [7] went invalid, [8] do_impact |
| mindist +4 | time manager event index (0xffff none) |
| mindist +8 | the delegator |
| mindist +0xc / +0x10 | back indices (the collision's vector) |
| mindist +0x14 | bits: coll_type 0-7, synapse_sort_flag 8-9, is_in_phantom_set 10-11, mindist_function 12-13 (0x1000 phantom), recalc_result 14-15 (0 OK, 0x4000 intrusion), disable_halfspace 16-17, mindist_status 18-21 (2 invalid, 3 exact, 4 hull recursive, 5 hull), coll_dist_selector 22-29 (starts 63) |
| mindist +0x18 / +0x34 | synapses (0x1c each); sorted 0 = synapse[flag], 1 = synapse[flag ^ 1] (`bits >> 8 & 3`, x 7 dwords + 6); +0x32 / +0x4e their statuses |
| mindist +0x50 | sum_extra_radius |
| mindist +0x54 | contact_dot_diff_center |
| mindist +0x58 | sum_angular_hull_time (f32 in this build) |
| mindist +0x5c | len_numerator (get_length) |
| mindist +0x60 | contact_plane (x, y, z, w) |
| mindist +0x70 | recalc_time_stamp |
| mindist +0x74 / +0x78 | next / prev in the manager's lists |
| mindist +0x7c | last_visited_triangle |
| synapse | vtable 0x100f2900; +4 hull manager element index, +8 / +0xc next / prev in the object's exact (+0x20) or invalid (+0x24) list, +0x10 object, +0x14 edge, +0x18 (i16) mindist - synapse, +0x1a status (0 point, 1 edge, 2 triangle, 3 ball, 5 backside) |
| IVP_Mindist_Manager (env +0x10) | +0 scanning_universe, +4 env, +8 exact_mindists (newest first), +0xc wheel vector (u16 size, u16 n, elements), +0x14 invalid_mindists |
| object +0x18 | env |
| object +0x20 / +0x24 | exact / invalid synapse lists |
| mindist +0x28 / +0x44 | the synapses' objects (object 0 / object 1) |
| object +0x30 | origin offset (unless +0x44 & 0x800) |
| object +0x2c | a rotation (not read; NULL here) |
| object +0x40 | cache |
| object +0x44 | movement byte (1 moving, 8 static / frozen; 0x21 during a revival; & 0x800 no origin offset) |
| object +0x48 | hull manager |
| object +0x84 | surface manager (+4 the compact surface; slot 7 add_reference_to_ledge) |
| object +0x8c | OV element |
| object +0x90 | extra radius |
| object +0x94 | core |
| core +4 / +8 | radius / deviation radius |
| core +0x44 | 0.5 / radius |
| core +0x5c | spin rate |
| core +0x90 | OV centre |
| core +0xd0 / +0xc0 | speed / rot speed |
| core +0xe0 / +0xf0 | position / delta (per s) |
| core +0x100 | q_last |
| core +0x120 | rotation axis (world) |
| core +0x130 | t_psi |
| core +0x138 | 1/dt |
| core +0x13c | \|speed\| |
| core +0x1a4 | max_surface_rot_speed |
| core +0x48 | car wheel |
| IVP_Hull_Manager (object +0x48) | +0 last_vpsi_time (f64), +8 gradient, +0xc center_gradient, +0x10 hull_value_last_vpsi, +0x14 hull_center_value_last_vpsi, +0x18 hull_value_next_psi, +0x1c time_of_next_reset (int), +0x20 IVP_U_Min_List |
| IVP_U_Min_List | +0 u16 malloced, +2 u16 free list, +4 elements (16 bytes: u16 long next / long prev / next / prev, +8 f32 value, +0xc listener), +8 minimum, +0xc long list's first, +0x10 first, +0x14 insert counter |
| IVP_Collision (OO watcher) | vtable 0x100f2f2c; IVP_Synapse_OO at +0x18 / +0x28 (vtable 0x100f2f40, objects +0x20 / +0x30), +0x38 the mindists' vector, +0x14 delegator (vtable 0x100f2f1c) |
| IVP_Mindist_Recursive (0xa0) | vtable 0x100f2ef8 (0-3 base, 4 0x100b1950, 5 0x10004410, 6 0x10003fd0, 7 0x100b16e0, 8 0x100b14f0, 9 / 10 0x100b7b10 / 0x100b7b57); +0x80 IVP_Collision_Delegator (vtable 0x100f2ee8); +0x84 its mindists' vector (+0x86 count, +0x88 array); +0x8c the side split (-1 at first); +0x90 the count |
| object +0x48 / +0x50 / +0x58 / +0x60 | the hull manager's last_vpsi_time / gradient / hvl / hull_value_next_psi (the Recursive code reads them so: `hm +0x48`) |
| sampler (0x5b0) | +0 object, +4 core, +0x10 cache's time code, +0x14 21 matrix pointers (t_now + 0.005 i), +0x70 storage (64 bytes each) |
| IVP_3D_Solver | +0 vtable (slot 0 get_value(A, B): x87 return of a stored f32), +4 max deviation, +8 its inverse, then the case's data |
| IVP_KK_Input | +0 / +4 L's points (pointers), +0x10 / +0x20 K's points in L's frame, +0x30 K's direction in L's frame, +0x40 L's direction, +0x50.. K, L, cK, cL, +0x60 cross |
| recalc stack | +0 mindist, +4 P_Finish_Counter (20; ebp-0x83c), +0x10 pos_opposite_BacksideOs, +0x20 loop list (256 pairs), +0x820 its length, a pierce counter |
| event stack (ebp-0x40) | +0 sum = msrs0 + msrs1, +4 projected centre speed, +8 max collision speed, +0xc worst = `(speed0 + sum) + speed1`, +0x10 md, +0x14 env, +0x18 t_now, +0x20 t_max (env+0xf8), +0x28 type out, +0x30 time out |
| time manager (env +4) | +8 its min list, +0x18 the base (the PSI's time once it runs) |
| env +0x1c | range manager |
| env +0x20 | anomaly manager (slot 7 (+0x1c) speed, slot 2 (+8) push; slot 4 more hull budget) |
| env +0x24 +0x14 | stage-4 budget |
| env +0x28 | slot 1 (8) / (0xe) around a mindist event |
| env +0x2c | universe manager (NULL here) |
| env +0x70 / +0x74 | mindist counts |
| env +0x7c | OO event counter |
| env +0xc4 | selector counter |
| env +0xf0 / +0xf8 | now / t_max |
| env +0x108 | time code |
| env +0x126 / +0x128 | delegator roots (count / list) |
| struct extents (as dumped) | object +0..+0xa4, core +0..+0x1a8, compact surface +0..+0x30, hull manager +0..+0x34, manager +0..+0x14 |

## Constants

| Value | What |
|---|---|
| 0x1010a988 | edge next table by `& 0xc`: +4, +4, -8 (0 -> 1 -> 2 -> 0) |
| 0x1010a998 | edge prev table: +8, -4, -4 |
| 0x10110a28 | minimize table `[sorted0.status x 4 + sorted1.status]` |
| 0x10110bb0 | event table, same index |
| 0x100f1b08.. (0x100f1b07..) | qr check placement by F's edge index: 0 [0, 2, 1], 1 [2, 1, 0], 2 [1, 0, 2] |
| 0x10106930 = 0.0254f | inches to metres |
| [7, 2, 6, 3, 5, 4, 0, 1] | the unit box's corner map (bit 0 x max, 1 y max, 2 z max); twelve triangles |
| 0.1 u | corner match distance (unit box) |
| intra 0.5 / 0.9 / 0.8 / 10 / 0.06, world 1 / 5 / 0.5 / 15 / 0.06 | range manager (the leaked source's 0.1 is 0.06 here) |
| 0x3eceeb70 (0.40414), 0.16666667 | spin series |
| 1.00001 (0x3f800054) | hull gradient scale |
| 1.001 | `sqrtf(1.001 - (axis.plane)^2)` |
| 2.1, 6 | hull conversion factors (`(env dt x worst) x 2.1`, `(env dt x speed) x 6`) |
| 0.003 | Leave_PK's KK threshold; regula falsi tolerance; t_max overshoot |
| 0.005, 200, 20 | sampler step (s), `(int)(d x 200)`, last index |
| 0.375 | regula falsi's every-fourth step; 64 steps limit |
| 1e-6, 1e-10, 1e-12, 1e-18, 1e20 | the walk's epsilons and start values |
| 1e15 (0x100f4008) | Recursive: radius without a node |
| 1e-10 (0x100f3b94), 0.1 (0x100f3c60) | hull shares |
| 4.0 (0x100f3f18) | Recursive +0x50 += real_coll_dist x 4.0 |
| 0.004 (0x100f3be0) | ledge tree box scale |
| 1e-6 (0x100f3bac), 1e-18 (0x100f3b84), 1e20 (0x100f4010) | KK parallel fallback |
| 0x100f4310 | sign xorps mask |
| 0x10110b0c | the OV grid's powers of two |
| 0x4b, 0x3ff, 0x400 | create_exact_mindists' hash: `key = l1 x 0x4b ^ l0`, `h = ((key >> 8 signed) x 0x3ff + key) & mask`, size s = 0x400 halved while n < s, `n = (len0 x len1 + count) x 2 + 2` |
| 1.000001 | FF's strict-improvement factor |

ivp_mindist_settings (0x1010d130.., runtime values; collision tolerance 0.00635 m):

| Offset | Value |
|---|---|
| +0 | real_coll_dist 0x3a266515 |
| +4 / +8.. | min_coll_dists / coll_dists[64] (0x1010d138) 0x3bcffe5a |
| +0x108 | minimum_friction_dist 0x3bcffe5a |
| | friction 0x3c4ffe5a ([0x1010d23c]), keeper 0x3c6f314e |
| +0x114 | speed_after_keeper 0x3f143f75 |
| | keepers_safety 0x38851daa |
| +0x11c | max_friction 0x3ce9fe25 |
| | max_impact_system 0x3e0efede |
| +0x124 | mindist_change_force_dist 0x3a266515 |
| | min_vertical_speed 0x3c4ffe5a |
| [0x1010d25c] | max_spawned 1000 |
| +0x130 | event_queue_min_delta_time_base 1.0f |

## Edges and ledges

- next = `edge + table 0x1010a988[edge & 0xc]`; prev = `+ 0x1010a998[& 0xc]`; opposite = `edge + ((int)(word x 2) >>
  17) x 4`; triangle = `edge & ~0xf`; ledge = `triangle - (tri_index + 1) x 16` (init_mindist's form). Edges 0 / 1 / 2
  have low bits 4 / 8 / 0xc.
- BBoxToCollide: equal mins / maxs -> NULL; cache lookup; else 0x1000a860: the 8 corners, the unit box's ledge copied
  (size_div_16 x 16 bytes), each point = corner(map[i]) as `(k x, -(z k), y k)`, k = 0.0254f, w 0; slot 0x38 builds the
  compact surface. Every BBoxToCollide box copies the unit box.
- A box from -4096..4096 x -64..0 (BBoxToCollide): mass centre (0, 0.8128, 0), inertia 0x46292145, upper radius
  146.13 (0x4313227f), deviation byte 0xfa, tree root sizes (177, 2, 177).
- ze_crazykart_v4's world (BSP model 0): a compact surface with a ledge tree, two solids (1.3 MB, 30 KB).

## The cache (0x1006cd90)

1. Time code from env+0x108; `dt = f32(env+0xf0 - core+0x130)`.
2. dt == 0 (ucomiss, parity: equal only): q = core+0x100, position = core+0xe0; else q = 0x1006ca90, position =
   `core+0xf0 x dt + core+0xe0` per axis.
3. Rows (0x100723b0, `x2 = x + x` ...): `[1 - (zz + yy), xy - wz, wy + xz; wz + xy, 1 - (zz + xx), yz - wx; xz - wy,
   wx + yz, 1 - (yy + xx)]`.
4. Unless object+0x44 & 0x800: origin += rows x object+0x30 as `((r0 o0 + r1 o1) + r2 o2) + p`.

- A moving object's cache (+0x44 < 8) is renewed when its time code is older than env+0x108 (0x10099850, 0x100a53e0);
  a static object's stays as made.
- Transforms: to world `((m00 p0 + m01 p1) + m02 p2) + pos` per row; into an object `d = w - pos`, `((m0i d0 + m1i
  d1) + m2i d2)` per column.

## Creation

At a revival (stage 1 via 0x100778d0, the core's and object's movement bytes forced to 0x21):
1. recheck_ov_element: element out of the tree (0x1009b400), centre = core+0x90; real_check_sphere = `f32(range slot
   1(object)) + core+4`; insert_ov_element (collects the elements it meets; returns the radius) and add_to_hull_manager
   at `(radius - core+4)`; collisions already in the element's vector kept (diff hash), stale ones deleted (slot 4),
   each new pair offered to the delegator roots (slot 5 until one takes it).
2. The root makes an OO watcher: synapses at the range manager's split (slot 0), create_exact_mindists.
3. Single ledges: one mindist from the two ledges' first triangles' first edges, status point (`new IVP_Mindist` sets
   vtables 0x100f2914 / 0x100f2900) -> init_mindist (synapses: object, edge, offset, status; add_reference_to_ledge;
   sum_extra_radius = the objects' +0x90 sum; a phantom -> 0x10094cf0, else) -> insert_and_recalc_exact_mindist:
   status exact `(bits & 0xffcfffff) | 0xc0000`, head of +8, each synapse at the head of its object's +0x20,
   recalc_mindist, a car-wheel core into the wheel vector; recalc OK: update_exact_mindist_events(allow = `(core0
   movement | core1 movement) < 0x21`, NOW) (never a hull conversion at a revival), else slot 7.
4. The creation runs before the controllers: the core's speeds are from before the PSI (a kart woken on the floor: mcs
   0, update_exact_mindist_events returns before the selector counter).

Range manager (minss / maxss as SSE `a < b ? a : b`):
- slot 0: `s0 = (msrs0 + speed0) + 1e-10`, s1 likewise; `r = minss(radius1, radius0) x 0.9`; `sum = s1 + s0`; `a = s1
  x 0.2 + s0`; `d = minss(r, 0.5 sum)`; `b = a x 0.18 + s1`; `d = maxss(d, 0.8)`; `d = minss(d, 10)`; `d -= env dt x
  sum`; `d = maxss(d, 0.06 sum)`; `inv = 1 / (b + a)`; `r0 = (d a) inv`, `r1 = (d b) inv`.
- slot 1: `s = (msrs + speed) + 1e-10`; `d = minss(1 s, 5 radius)`; maxss 0.5; minss 15; `-= dt s`; `maxss(d, 0.06 s +
  radius)`.

## recalc_mindist (0x100982d0)

1. Time stamp == env+0x108 -> 4; else stamp it.
2. Solver on the stack; r = table 0x10110a28 case (0x1009a140: P x {P, K, F}, K x K, F x F default 0x10099850; K x P,
   F x P swapped 0x10099c90; balls; the rest illegal).
3. 1 (OK): `bits &= 0xffff3fff`, return 1, no rescue.
4. Else `bits = (bits & 0xffff7fff) | 0x4000`; 2 (endless loop): the rescue check; 3 (backside): pierce (0x100983ee):
   the sorted-0 synapse unless its status (+0x1a) isn't 5, then sorted 1: its edge = minimize_on_other_side(edge, &the
   walk's backside position (+0x10)), status 2, the walk again with the same counter (+4 not reset); a second
   backside: the rescue check, 3. Anything else asserts (lines 0x136 / 0x139) and walks again.
5. Rescue check: not a phantom (`bits & 0x3000 != 0x1000`) and not hull recursive (`bits & 0x3c0000 != 0x100000`):
   slot 5.

minimize_default_poly_poly 0x10099850: both caches made / refreshed, m_cache = {points, ledge, cache, object,
synapse}; by (sorted0.status, sorted1.status): (0, 0) PP, (0, 1) PK, (0, 2) PF, (1, 1) KK, else FF.

check_loop_hash 0x10098020: (status | edge address) pairs, canonical order, looked up from the newest; full (256)
counts as a loop. Called only once P_Finish_Counter goes below 0 (counter -= 1 at each PP / Leave_PK / Leave_KK /
Leave_PF entry).

minimize_on_other_side 0x10099e60: a byte per triangle (alloca, n = ledge +0xc i16, zeroed by 0x100bdae0); start =
the first edge of triangle pierce_index (the backside triangle's word 0 bits 12..23: `ledge + 0x14 + 16 index`); loop:
mark the triangle (word 0 & 0xfff), qr of the point against it (qr_vals' sums and tables 0x100f1b07..), for its edges
from the start (next): qr <= 0 (not > 0) and opp(e)'s triangle unmarked: start = opp(e), loop; none: return the start.

## The walk's helpers

- s(k0, k1, p): `k = k1 - k0`, `[-((k0 - p).k) + FLT_MIN, (k1 - p).k + FLT_MIN]`; outside = either sign bit.
- qr(F, p): P0 P1 P2 (edges 0-2), `a = P0 - P1`, `b = P2 - P1`, `c = p - P1`, aa, bb, `ab = b.a`, ca, cb (each `(x + y)
  + z`), `t = cb aa - ca ab`, `s = ca bb - cb ab`, `D = bb aa - ab ab`; `(t, (D - s) - t, s) + FLT_MIN` placed by
  0x100f1b08.. so checks[j] is F's j-th edge from F.
- IVP_KK_Input 0x100794a0: cross +0x60 = `(Lz Ky - Kz Ly, Kz Lx - Lz Kx, Kx Ly - Lx Ky)`.
- calc_unscaled_KK_vals 0x100799d0: `|cross|^2 <= 1e-6` -> the parallel fallback (returns 0); `A = Kv x c`, `B = Lv x
  c`; checks_L = `((sl0 - sk0)(sl0 - sl1), (sk0 - sl1)(sl0 - sl1))` (A dots, no FLT_MIN), checks_K = `((tk0 - tl0)(tk0 -
  tk1) + FLT_MIN, (tl0 - tk1)(tk0 - tk1) + FLT_MIN)` (B dots). 1.
- calc_qlen_PK_K_space 0x1007a9b0: outside the edge `|p - nearer end|^2`; inside `|(p - a) x (b - a)|^2 / (|a - b|^2 +
  1e-18)`.

## The cases

- **PP 0x100b4e20** (a loop): both points to world and into each other's frame; `d = wA - wB`, `q = d.d`; q <= 1e-6 ->
  2; `len = (1 / sqrtf(q)) q - sum_extra_radius`, `plane = d x inv`, contact_dot_diff_center = `plane.(coreA - coreB)`
  (caches' +0); neighbours of A (against B's point in A's frame), then of B: `Pm_P = P - Pm`, `dist = Pm.Pm_P`; for e =
  prev(opp(prev(Pm))) .. prev(Pm) (next e = prev(opp(e))): `grad = tp.Pm_P - dist > 0`: `grad x (1 / sqrtf((tp -
  Pm)^2 + 1e-18)) > best`: keep. None: both points, 1. Else s of the edge for its point: s1 <= 0 -> the same end
  ("epsilon problem"); s0 < 0: sort to the edge's cache, PP(edge, point); else sort to the point's, Leave_PK(point,
  edge).
- **PK 0x100b6070**: the point into K's frame, s: s0 < 0 PP(P, K), s1 < 0 PP(P, next K), else Leave_PK.
- **Leave_PK 0x100b62d0**: loop check (0, P, 1, K); vk, vP, vt (K's triangle's third point), vo (prev(opp K)'s start);
  `hesse_tri = vk x vt`, `hesse_oppo = vo x vk`; vert0 / vert1 their dots with vP; qr of K's and opp(K)'s triangles;
  qr0[0] > 0: (qr1[0] > 0 and vert1 > 0 ? PF(P, opp K) : PF(P, K)); qr1[0] > 0: PF(P, opp K); vert0 < 0 and vert1 < 0:
  point / backside, pos_opposite = P in K's frame, 3. `lot = vk x vP`, `iqk = 1 / vk.vk`, `q = lot.lot x iqk`; q >
  1e-10: `len = (1 / sqrtf(q)) q - sum_r`, `plane = world(vk x lot) x -(inv iqk)`; else `len = -sum_r` and plane =
  normize(v x vk), v = vk's largest |component| (from z down, strictly larger) negated and swapped with the one before
  it. cddc; `max = q x 1e-6`; lot (world, or the raw one in the else) into P's frame; P's edges as in PP: `angle = v.lot
  > 0`: `angle / sqrtf(v.v) > max`: keep. Found: if 0.003 > max, the KK values of (K, found) (input with cK, cP): a
  fault or checks_L[0] < 0 -> end; KK(found, K, cP, cK). End: point / edge, 1.
- **KK 0x100b3070**: L inside (both checks_L sign bits clear): checks_K[0] < 0 PK(K, L), [1] < 0 PK(next K, L), else
  Leave_KK. K inside: sort to L; checks_L[0] < 0 PK(L, K) else PK(next L, K) (as the source). Both outside: pkp / pkm
  by checks_K[1] > checks_K[0], plp / plm by checks_L; pkp against L inside: PK(pkp, L); plp against K inside: sort L,
  PK(plp, K); `s_kL[0] x checks_L[0] < 0`: PP(pkp, plm); `s_lK[0] x checks_K[0] < 0`: sort L, PP(plp, pkm); else
  PP(pkp, plp).
- **Leave_KK 0x100b36f0**: loop check (1, K, 1, L); `val = (L0 - K0).c`, side = its sign bit, `iHQ = 1 / sqrtf(c.c)`; H
  world (L's rows), into K's frame; `len = fabsf(iHQ val) - sum_r`; `plane = ((f32(side) - 0.5) doubled x iHQ) x
  H_ws`; cddc; L's points into K's frame; four cases (+0 F, +4 P, +8 P_Fos, +0xc cP, +0x10 cF, +0x14 H_Fos, +0x20 the
  hesse; stride 0x30): [opp K, L, L_Kos0, cL, cK, H_Kos], [K, opp L, L_Kos1, ...], [opp L, K, K_Los0, cK, cL, H_Los],
  [L, opp K, K_Los1, ...]; `hesse = (next - start) x (prev - start)`; reverse[i] = `signbit(H.hesse) ^ side` for 0, 1,
  `(1 - signbit) ^ side` for 2, 3; best grad (from -4e-6): `ce = cases[(i ^ side) ^ reverse[i]]`, `e = P_Fos(i ^ side)
  - P_Fos(i ^ side ^ 1)`, `delta = e.hesse_i < 0`: `grad = (delta / sqrtf(e.e)) x (1 / sqrtf(h.h))`; smaller and
  `qr(F_i, ce.P_Fos)[0] > 0`: keep. None: both edges; reverse[0] + [1] == 2: K backside, L triangle, `pos = sl L_Kos1 +
  (1 - sl) L_Kos0` (`sl = checks_L[0] / (checks_L[1] + checks_L[0])`), 3; reverse[2] + [3] == 2: K triangle, pos from
  K's points by sk, L backside, 3; else 1. Found: sort to the edge's; qr inside: Leave_PF(edge, its point in F's frame,
  F); qr[2] >= 0: KK(edge, next F); qr[1] >= 0: KK(edge, prev F); else (100b48de) q1 = calc_qlen_KK(edge, next F), q2 =
  calc_qlen_KK(edge, opp(prev F)) (the edge's and F's caches): q1 > q2: KK(edge, prev F), else KK(edge, next F).
- **PF 0x100b1ca0**: P into F's frame; qr inside: Leave_PF; else the nearest of F's edges by calc_qlen_PK_K_space, from
  1e20, strictly smaller; PK(P, it).
- **Leave_PF 0x100b26d0**: loop check (0, P, 2, F); h = hesse(F), fast-normized when >= 1e-10; plane = world(h); h_Pos
  into P's frame; `len = h.P_Fos - h.F0`; negative: h_Pos x -1; `len -= sum_r`; cddc; P's edges: `dist = v.h_Pos < 0`:
  `dist / sqrtf(v.v) < min` (from 0): keep. None: point / triangle; `len + sum_r < 0`: pos = P_Fos, F backside, 3; else
  1. Found P2: qr(F, P2's point): inside: Leave_PF(P2); one negative check (not >= 0): KK(P2, that edge); else
  (100b2fbf) over F's edges from F (next) whose qr is not > 0: calc_qlen_KK(P2, e, cP, cF), the strictly smallest from
  1e20: KK(P2, it).
- **calc_qlen_KK 0x1007ac30**: KK input and vals; checks_L both clear: 0 >= checks_K[0]: PK_K_space(L's ledge, L,
  K_Los0); 0 >= checks_K[1]: the same with K_Los1; else 0x10079920: c = cross (+0x60), `q = (cx cx + cy cy) + cz cz`; q
  > 1e-12: `(k - l)^2 / q` with `k = (K_Los0y cy + K_Los0x cx) + K_Los0z cz` and l the same of L0, else PK_K_space(L's
  ledge, L, K_Los0). checks_K both clear: 0 >= checks_L[0]: L's start point world (L's cache) then into K's frame,
  PK_K_space(K's ledge, K, it); 0 >= checks_L[1]: next L's; else IVP_ASSERT (line 0x2a2) and on. General: from 1e20,
  for L's two points (L, next L) in K's frame: d = PK_K_space(K, it), `min = d < min ? d : min` (minss d, min); then
  d2 = PK_K_space(L, K_Los_i), `min = min < d2 ? min : d2`.

## calc_unscaled_KK_vals' parallel fallback (0x10079be4)

When `|K_vec x L_vec|^2 <= 1e-6` (cross at +0x60, `((c0^2 + c1^2) + c2^2)`) it samples and returns 0 (IVP_FAULT), its
four checks written all the same (p_minimize_KK and calc_qlen_KK read them; the caller that tests the return, the edge
step past 0.003, takes the fault as a no). Samples: the floats at 0x100f4150 / 0x100f4220 / 0x100f4230 (stack
ebp-0xd8): -1, 0.5, 2, 0, 1, -0.001, 0.001, 0.999, 1.001, -1e-6, 1e-6 (and 0.999999 0x3f7fffef, 1.0000005 0x3f800008,
never read). The best starts at 1e20, shared by both loops; a sample is taken only when best > q.
- Along K (11 samples): s, `u = 1 - s`; `P = (k1.x s + k0.x u, u k0.y + k1.y s, k1.z s + u k0.z)` (K's points in L's
  frame, +0x10 / +0x20); `A = L1 - L0`, `D = P - L0`; `c = (D.y A.z - D.z A.y, D.z A.x - D.x A.z, D.x A.y - D.y A.x)`;
  `q = (1 / ((((L0 - L1).x^2 + (L0 - L1).y^2) + (L0 - L1).z^2) + 1e-18)) x ((c.y^2 + c.x^2) + c.z^2)`. Taken: checks_K
  = (s, u), checks_L = `(-(((L0 - P).y A.y + (L0 - P).x A.x) + (L0 - P).z A.z) + FLT_MIN, (((L1 - P).y A.y + (L1 -
  P).x A.x) + (L1 - P).z A.z) + FLT_MIN)` (the sign by xorps 0x100f4310).
- Along L (9 samples): L's points into K's frame once (world by L's cache (+0x5c's matrix, `((m0 x + m1 y) + m2 z) +
  t`), then object by K's (+0x58's: the columns, `d = w - t`)), `P = (b.x s + u a.x, b.y s + u a.y, b.z s + u a.z)`;
  the same q against K's own points; taken: checks_L = (s, u), checks_K = the ends of K against P as above.

## p_minimize_FF (0x100984c0)

Both synapses on a face (two bodies through each other). 1363 lines of disassembly: four brute-force passes over
triangles F and G (each with its m_cache: cache object rows +0x20, origin +0x50; synapse +0x14 edge, +0x1a status), each
writing both synapses when it finds a nearer pair:
1. Point pairs (0x10098504, F's point outer, edges by the next table 0x1010a988): both points to world (`(m1 y + m0 x)
   + m2 z + origin` per row), `q = (dx^2 + dy^2) + dz^2` of F - G; below the best (1e20 at first, `comiss best, q`):
   both POINT.
2. A side's points against the other's face, F's against G's first (arrays at ebp-0x104 / -0xe4 / -0xd4): `n = (next
   - start) x (prev - start)`, offset `-((ny P0.y + nx P0.x) + nz P0.z)`, both x `1 / sqrt((ny^2 + nx^2) + nz^2)`
   (0x10001950). A point (world, then the face's frame by the columns) inside the prism (qr_vals on the face's edge, no
   sign bit): `d = ((p.y ny + p.x nx) + p.z nz) + offset`, `q = d d`; `q x 1.000001 < best`: point POINT, face's edge
   TRIANGLE.
3. A side's points against the other's edges, G's against F's first: the point in the edge's frame, s_vals (A the
   edge's start, B the next's); both without a sign bit: `q = (1 / (|A - B|^2 + 1e-18)) x |(p - A) x (B - A)|^2`
   (`(cy^2 + cx^2) + cz^2`); `q x 1.000001 < best`: edge EDGE, point POINT.
4. Edge pairs (F's outer): IVP_KK_Input (K = F's edge, L = G's), calc_unscaled_KK_vals (return not read: the fallback's
   checks count too); all four without a sign bit: 0x10079920's distance inlined (`(K0 . c - L0 . c)^2 / |c|^2`, c = K
   x L in L's frame; `|c|^2 <= 1e-12`: K0 against L, 0x1007a9b0); `q x 1.000001 < best`: both EDGE.

Then (0x1009929c) F is the first side, or G when G's status is POINT and F's isn't; sort_synapses makes it sorted 0
(`bits ^ 0x100` when it isn't); by (first, second): (0, 0) PP, (0, 1) PK, (0, 2) PF, (1, 1) KK. Anything else: the
DLL's "%s in contact with %s, crash. dist = %d, minq = %lf" Error and IVP Failed (ivp_mindist_minimize.cxx lines 0x1e6
/ 499 / 0x1fd / 0x207), returning 0; pass 1 always leaves a pair. Read from the decompile, pass 1's sums and the
comparisons from the disassembly; the passes only choose the pair.

## Hull managers

- 0x100a68e0 add: a value <= the minimum goes first, else before the first element with value >= it (a value goes
  before its equals).
- A listener's value: `f32(t - last) x gradient + hull_value_last_vpsi + d` (0x1009a420 the OV element, 0x100b77f0 the
  OO synapses, 0x10095fc0 a mindist's).

The PSI (0x100970f0, after the quaternion): 0x100975f0(core, the step's rotation quaternion's vector part v; rows are
stage 2's): `n = |v|^2 > 1e-10`: `a = (1 / sqrtf(n)) n`, `rate = (((a^3 a^2) 0x3eceeb70) + (a^3 0.16666667 + a))
doubled x core+0x138`, axis +0x120 = `rows v x (1 / sqrtf(n))`; else (1, 0, 0) and 0; +0x5c = rate, `+0x1a4 = core+8
x rate`. Then (0x100974e3) `g = (+0x1a4 + +0x13c) x 1.00001` for each of the core's objects (last first): `d = f32(t -
last)`, last = t, `hvl += gradient d`, gradient = g, `cvl += center_gradient d`, center_gradient = +0x13c, `next = g dt
+ hvl`; due when `min - next < 0` (pushed on the PSI's list).

Stage 4 (0x10097db0, each due manager from the list's end): while `min - next < 0` (at most the budget env+0x24+0x14,
more from env+0x20 slot 4), the first listener's slot 1 with that (negative) value; then when `(double)time_of_next_reset
< last`: reset 0x10093bb0 (`a = -hvl`, `b = -cvl`: every value a + value, each listener's slot 3 (a, b): a mindist's
`sum_angular_hull_time += a - b`; the OV / OO listeners' are stubs; minimum and next + a, hvl = cvl = 0) and
time_of_next_reset = `(int)(last + 10)`.

Hull event 0x100957c0 (hull recursive -> 0x100b1b30): sorted cores c0 / c1; `speed_i = (+0x1a4 + +0x13c) + 1e-10`,
`speed = speed1 + speed0`; unless disable_halfspace: centres at t (`pos + delta f32(t - t_psi)`), new cddc = `(c0 -
c1).plane`, angular hull times `(gradient - center_gradient) f32(t - last) + (hvl - cvl)` of both (`sum = a1 + a0`),
`est = ((len - (sum - sum_angular)) - (cddc - new cddc)) + value`; `est > (env dt x speed) x 6`: sum_angular = sum,
cddc = new, `len = est - value`, `f = est / speed`, each sorted synapse re-inserted at its object's hull now + f x its
speed; return. Else both synapses out, insert_and_recalc_exact_mindist (or the phantom one).

- insert_hull_mindist(md, h) 0x100960d0: synapse 0's object not moving (`+0x44 & 7 == 0`): (0, h); synapse 1's: (h,
  0); else `s_i = (+0x1a4 + +0x13c) + 1e-10`, `k0 = s1 0.1 + s0`, `k1 = s0 0.1 + s1`, `f = h / (k1 + k0)`, (f k0, f k1).
- 0x10095fc0(md, t0, t1): status hull `(bits & 0xffd7ffff) | 0x140000`; synapse 0 at hull now + t0, synapse 1 at + t1;
  `sum_angular_hull_time = angular1 + angular0`.
- OO watcher event 0x100b77f0: env+0x7c += 1; the range split; create_exact_mindists(obj0, obj1, r0 + r1, the watcher's
  vector) (single ledges: the pair's mindist kept); both synapses at hull now + r0 / r1. OV element event 0x1009a4c0:
  recheck_ov_element.

## update_exact_mindist_events (0x10095310)

(md, allow_hull_conversion, hint 0 NOW / 1 SMALL_DELAY / 2 BIG_DELAY.)
1. A queued event is removed. `coll = coll_dists[selector]`.
2. `len > (env dt x worst) x 2.1 + coll`: allowed -> remove_exact_mindist and insert_hull_mindist(len - coll); return
   either way.
3. `pcs = plane.v1 - plane.v0` (core +0xd0), `rot_i = sqrtf(1.001 - (axis_i.plane)^2) x msrs_i`, `mcs = (rot0 + rot1) +
   pcs`; speed_after_keeper > mcs and 1e-10 > mcs: return; `f32(t_max - t_now) x mcs + coll <= len`: return; phantom:
   return.
4. selector != 0: counter env+0xc4 (+1; past 2: selector - 1, counter 0).
5. calc_time_of_next_event; no type: return.
6. `f32(time - t_now) < 1e-6`: NOW -> time = t_now; else `d = len - real_coll_dist`: BIG or `(type & 0xf) != 0`: d >=
   1e-6 ? `((double)(d / worst) + t_now) + (double)((base x 1e-4) dt)` : `(double)((base x 0.001) dt) + t_now`; else d >=
   1e-6 ? `((double)((d 0.1) / worst) + t_now) + (double)((base 1e-7) dt)` : `(double)((base 1e-5) dt) + t_now`;
   `f32(time - t_max) >= 0`: return.
7. Queued at `f32(time - the time manager's base)` (0x100a68e0 on its list), +4 = its index, the low byte of +0x14 = the
   type.

## Event solvers

calc_time_of_next_event: table 0x10110bb0; 0x100a53e0: both m_caches, type out = 0; PP 0x100a35c0, PK 0x100a3f40
(PK's type 0x32; PP's types 0x10 / 0x11), PF 0x100a2160, KK 0x100a2d90.

Samplers (0x100a12c0): a static object every slot the cache's matrix; a moving one slot 0 the cache's, the others made
on demand by 0x10074000 at their time.

- find_first_t_for_value_max_dev 0x100b72a0(value, index, A, B, opt start value, out, t0, t_max): v (given or sampled);
  value >= v: out = t0, 1. `d = (v - value) x inv`; `(double)f32(t0 - t_max) + d > 0`: 0. Loop: d doubled; past t_max ->
  `f32((double)f32(t_max - t) + 0.003)`; `n = (int)(d x 200)` (at least 1); index += n; `t' = (double)(f32(n) x 0.005)
  + t`; sample; value >= v': 0x100b7130(out, v', A, B, t, t') then `f32(out - t_max) > 0` -> 0, else 1; index 20: 0;
  else v = v', t = t', `d = (v' - value) inv`, the same past-t_max test.
- 0x100b7130 (regula falsi): `t = ((double)f32(t1 - t0) x (double)(value - v0)) / (double)f32(v1 - v0) + t0`; every
  fourth step (n & 3 == 3; past 64 steps: t0) `t = (double)((f32(t0 - t) + f32(t1 - t)) x 0.375) + t`; both poses by
  0x10074000; `|v - value| < 0.003`: t; v >= value: (t0, v0) = (t, v), else (t1, v1).
- find_first_t_for_value_coll 0x100b7510(value, lower, A, B, opt, out, t_now, t_max): v0 > value: the max-dev search
  from slot 0; else (`0 > f32(t_now - t_max)`, else 0) step from t_now with `d = (v - lower) / max_dev` (past t_max as
  above, else maxss(d, 0)), the same n / index / t'; v' > value: `f32(t' - t_max) > 0` ? 0 : the max-dev search from that
  slot, v', t'; v0 >= v': out = the previous time, 1; else continue while `0 > f32(t' - t_max)`.

KK 0x100a2d90: spin = core0 +0x5c + core1's; K / L's start points, unit directions (`(1 / sqrtf(q)) x` when q >=
1e-10); side at t_now: `c = K_w x L_w` (caches' rows), `s = -(c.plane) > 0` -> sign -1, flag 0, else 1, 1.
- KK_COLL (vtable 0x100f2bc4, 0x100a2930: `c = K_w x L_w`, `((inv (c.Kp_w - c.Lp_w)) x sign)`, +4 = mcs, +8 = 1 / mcs)
  through 0x100b7510 (coll_dists[selector], real_coll_dist) up to t_max: type 0x40.
- KK_PARALLEL (0x100f2bb0, 0x100a2c30: `|K_w x L_w|^2`; max dev `(spin + spin) + 1e-10`) through 0x100b72a0 for 1e-10,
  up to the time found: 0x41.
- Four KK_PF (0x100f2ba8, 0x100a1520: A's direction . B's normal (both world), max dev `spin + 1e-10`): i = 0..3 faces
  opp K, K (K's ledge; A = L's sampler with L's direction) and opp L, L (L's; A = K's with K's direction), direction
  negated when the flag (flag, 1 - flag, flag, 1 - flag) is 0, normal = unit hesse; value `-(the edge object's core
  +0x44 x mindist_change_force_dist)`: 0x42.

PF 0x100a2160: spin.
- PF_COLL (0x100f2ba4, 0x100a1330: `(P_w - F0_w).n_w`; +4 mcs) through 0x100b7510 for coll + sum_r (lower `sum_r 0.5 +
  real_coll_dist`), started from len + sum_r (no sample): 0x20.
- PF_NPF (0x100f2bb4, 0x100a2040: the edge's unit direction (P's frame) . the face normal in P's frame; max dev `spin +
  1e-10`): target `(-(F's core +0x44 x change_force) x (sum_r 0.1 + minss(len, coll))) / coll`; for P's edges e =
  opp(prev P), then opp(prev e) until e == P: `d = next(e)'s point - P's`, `c = (d.n_P) / sqrtf(d.d)`; `f32(t_out -
  t_now) x max dev > c`: the max-dev search from c up to t_out: 0x21.

## Time and the PSI's collision stages

- env+0x108 (1 at the env ctor 0x1008441e) += 1 for each time event the loop 0x10085440 runs (the PSI is one) and once
  when the loop ends (it also sets env+0xf0 = the end); set_matrix 0x10097750 and 0x10014614 / 0x10084c1a also count.
- Time manager: an event runs at `base + (double)value` while `f32(until - base) >` the minimum.
- Stage 1 the revivals (creation), 0x100951f0 at its end; stage 3 each core's next PSI and its objects' hull managers;
  stage 4 the due managers; stage 5 0x100952d0 (each exact mindist from the head: 0x10096400: recalc, a failure -> slot
  7); stage 6 update_exact_mindist_events(1, SMALL_DELAY) for each exact one.
- simulate_time_event 0x10095dd0: env+0x28 slot 1 (8); recalc_mindist; OK and `coll_type & 0xf == 0` (0x20, 0x40): `len
  < coll_dists[selector] + mindist_change_force_dist` -> do_impact (slot 8); else update_exact_mindist_events(0,
  BIG_DELAY); other types (0x21, 0x41, 0x42): update_exact_mindist_events(0, SMALL_DELAY); env+0x28 slot 1 (0xe).
- The hand-off: `ecx = the mindist; call [vtable + 0x20]` (do_impact, no arguments) inside the time event, env+0xf0 =
  the event's time, env+0x108 just incremented, right after the recalc. It reads the sorted synapses (object, edge,
  status) and ledges, len_numerator (< coll + change_force), contact_plane (unit, from synapse 1's side toward synapse
  0's: `d = A - B` in PP), cddc, sum_extra_radius, coll_type, coll_dist_selector, both caches at that time, the cores
  (+0xd0, +0xc0, +0x13c, +0x1a4, +0x120, +0x5c, the PSI pose). do_impact pushes both cores, makes a friction contact or
  not, and re-plans the mindist's event itself (e.g. type 0x42 queued at base + 0x3c0443da). The rest: ivp-impact.md.

## OV pairing and ledge trees

- insert_ov_element 0x1009b200 places the element in the cube tree; the collector walks the nodes testing each element
  by its sphere: `((dy^2 + dx^2) + dz^2) <= (r + r')^2`. A node's cube contains every element sphere in it: the walk is
  exhaustive (the grid's cell sizes never change which pairs come out).
- Pairs: filtered by movement (either +0x44 & 7) and ShouldCollide; an existing OO watcher kept, a new one made (ctor
  0x100b7930: synapses at hull now + 1e20, then its event 0x100b77f0), one no longer met deleted (its mindists
  0x10093fb0). The element's own synapse at hull now + (rcs - radius) (0x1009a420).
- The ledge walk 0x100789b0: `d = centre - visitor`; `((dy^2 + dx^2) + dz^2) > (R + r)^2` -> out; `k = R x 0.004`; per
  axis |d| (0x10001930) `>= f32(size) k + r` -> out; a node with a ledge (+4 != 0) adds it (0x1002bed0) and stops (an
  inner node's hull too: no descent); else the left child recursively, then the right in the same loop. A leaf without
  a ledge (0x10078b37) would read the node as a ledge.

create_exact_mindists 0x10094300 (stack: the collision's mindist vector, a fixed ledge for side 0 / 1 (0 except from
IVP_Mindist_Recursive), the two visitor flags / "from" ledges, the delegator (md+8)):
1. Side 0's ledges within `(obj0 +0x90 + core1 +4) + scan` of core 1's position at t (`pos + delta f32(t - t_psi)`) in
   object 0's frame (the cache refreshed when movement < 8 and its stamp < env+0x108), then side 1's likewise (`(core0
   radius + extra1) + scan`).
2. A side with a fixed ledge takes it alone (its visitor and that object's cache refresh skipped); a side with a "from"
   ledge is walked by 0x10078bc0 from that ledge's tree node (ledge +4): its left child (+0x1c) then its right
   (+[node]), not the root.
3. Diff hash 0x10096850 over the vector, last to first (key from slot 2 0x10094110: the ledges from the edges, `edge &
   ~0xf - (tri_index + 1) x 16`; linear probing); lookup 0x10096710: found at j, swapped with the entry at `kept`
   (this+0x10) when kept < j (hash slots and both back indices +0xc / +0x10 fixed), kept += 1: the kept ones end at the
   front in lookup order.
4. Pairs: side 0's list last to first, side 1's last to first inside; not found: a new mindist (both terminal: new 0x80,
   init_mindist from the two first edges, inserted at once inside the loop; +0x50 += 0; a hull ledge (+8 & 3): new 0xa0
   IVP_Mindist_Recursive).
5. The vector's mindists from the end down to `kept` deleted (slot 4 (1), 0x10093fe0, out through the delegator's slot
   0: 0x100b7b10 -> 0x1009b470, swapped with the last), the new ones appended last to first (+0xc, or +0x10 when +0xc
   is set, takes the index).

## Invalid and rescue

- exact_mindist_went_invalid 0x10094bc0: remove_exact_mindist, insert_invalid_mindist 0x10094b40: status `(bits &
  0xffcbffff) | 0x80000`, head of the manager's +0x14 (mindist +0x74 / +0x78), both synapses at the head of their
  objects' +0x24 (synapse +8 / +0xc). Called by insert_and_recalc_exact_mindist and recalc_exact_mindist (non-phantom:
  `bits & 0x3000 == 0`; recalc_result `bits & 0xc000` set).
- mindist_rescue_push 0x100980a0: anomaly manager (env+0x20): speed = slot 7 (+0x1c)(object 0 (+0x28), object 1
  (+0x44)), x87; then slot 2 (+8)(mindist, object 0, object 1, f32 speed): the inter-penetration push (changes the
  cores' velocities). No RTTI names the manager's class.

## IVP_Mindist_Recursive (a ledge tree node's hull against a ledge)

A moving ledge tree (a mover's brush, ivp-shadow.md) meets a kart; the world's pairs reach terminal ledges near the
kart and never make one. Delegator (+0x80) slots: 0 0x100b19f0 a child leaves +0x84 by 0x1009b470; 1 0x100b1c8d its
dtor; 2 0x100b1c50: `+0x90 += d`, then the owner's (mindist +8) slot 2; 3 0x100b1c70: the owner's slot 3 when above 0,
else +0x90.
- Made by create_exact_mindists for a pair with a hull ledge: ctor 0x100b18a0 (base fields as a plain one's, env +0x70
  / +0x74 counts, vtables, +0x84..+0x90 zero, +0x8c = -1), init 0x10094150 (inserted at once), then `+0x50 +=
  [0x1010d130] (real_coll_dist) x 4.0`. It lives as an exact mindist between the hull and the other ledge.
- At a mover's revival (SetShadow's UseShadowMaterial: the object at 0x21) its exact mindist doesn't turn hull at once.
- Slot 7 0x100b16e0: count (slot 3) > [0x1010d25c] (1000): remove_exact + insert_invalid (a plain one's); else +0x8c
  = 1 when side 0's ledge is terminal, 0 when side 1's is, else `(r0 <= r1)` with r the ledge's tree node radius
  (+0x14; 1e15 without a node); then the split (0x100b17a8): remove_exact, range slot 0 (obj +0x28, obj +0x44) -> (a,
  b), 0x10096180 with a + b, status HULL RECURSIVE `(bits & 0xffd3ffff) | 0x100000`, 0x100b1a00 with a + b.
- Slot 8 0x100b14f0: count > limit: plain do_impact 0x1008b020. Else by the statuses (+0x32 side 0, +0x4e side 1;
  tables 0x100b16b4 / 0x100b16c4) the side whose closest feature is on the hull's virtual geometry (bit 31 of the
  edge's dword, or its triangle's: `edge & ~0xf`): side 0 point / ball vs side 1 edge / triangle: side 1 if virtual;
  side 0 edge vs side 1 point / ball, or side 0 triangle: side 0 if its triangle is virtual; edge vs edge: the virtual
  one, both virtual the radius rule; nothing virtual (and point / point): no split, the plain do_impact (0x100b1574: a
  hull's real face is collided with as the hull ledge, ivp-virtualmesh.md 3); other statuses assert (0x32 / 0x5d /
  0x65) and split with the side it had. Then the split (0x100b1650).
- 0x100b1a00: count > limit: nothing; else create_exact_mindists over +0x84 with fixed[1 - side] = the other synapse's
  ledge and from[side] = the split side's (scan = the argument), then slot 2 (new - old count).
- 0x10096180: status HULL `(bits & 0xffd7ffff) | 0x140000`; each synapse inserted (0x100a68e0) at its object's
  hull_value_next_psi (+0x60) + its share: an object not moving (`+0x44 & 7 == 0`) takes 1e-10 and the other the whole;
  else `s_i = (core +0x1a4 + core +0x13c) + 1e-10`, `k0 = s1 x 0.1 + s0`, `k1 = s0 x 0.1 + s1`, `f = hull / (k1 +
  k0)`, shares `f x k0` and `f x k1`.
- Hull event 0x100b1b30 (0x100957c0 sends a status-4 mindist): 0x100980e0 (0x100982d0's copy but for one store:
  P_Finish_Counter 0 instead of 20 (0x14), ebp-0x83c; asserts' lines 0xeb / 0xee); valid (`bits & 0xc000 == 0`) and len
  (+0x5c) > [0x1010d23c] (0x3c4ffe5a): 0x100b1af0; else the ranges (a, b; env+0x7c += 1), 0x100b1a00 with a + b, each
  hull synapse out (0x100a6bb0) and back at `(f32(t - hm +0x48) x hm +0x50 + hm +0x58) + its range`.
- 0x100b1af0: 0x100b1810 (its mindists deleted last to first through slot 4 (1), slot 2 with -count, array freed), both
  hull synapses out, insert_exact_mindist 0x10094a70 (EXACT `(bits & 0xffcfffff) | 0xc0000` at the exact list's head,
  synapses into their objects' +0x20, into the manager's +0xc vector when a core has +0x48 and not a phantom), `bits &
  ~0x3000`.
- Dtor 0x100b1980: 0x100b1810, then 0x10093fe0.

## Unread

- ConvexFromVerts (qhull + IVP's ledge builder), ConvertConvexToCollide's ledge soup, the static core's creation,
  set_collision_tolerance (the settings are taken as the DLL holds them).
- minimize_on_other_side's and the rescue push's callers beyond the above; the anomaly manager's vtable.
- The parallel fallback's sampled writes as KK reads them in calc_unscaled_KK_vals' early return (0x10079be4 is read;
  the caller that tests its return: its address).
- The PP event solver's types 0x10 / 0x11 paths; the balls; phantoms (0x10094cf0).
- The delegator roots' choice (OO watcher vs a direct mindist); the stage-4 budget past env+0x24+0x14 (env+0x20 slot 4);
  deletions beyond ~IVP_Mindist (0x100957a0).
