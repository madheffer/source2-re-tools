# ze_crazykart: CS:GO legacy physics (IVP)

ze_crazykart is a CS:GO map run on the CS2 engine (a side project): its karts and items move on CS:GO's own physics, IVP inside the legacy 32-bit vphysics.dll (md5 d97cf2194594d7545427cdabc7376db4), with server.dll (md5 8048019154549052cb6dc057b76f6a85) and engine.dll for the movers, displacements and physboxes. **CS:GO, not CS2.** Other CS:GO-only notes are in [../csgo/](../csgo/README.md).

## The files

10 files.

| File | Subject |
|---|---|
| [crazykart-physics](crazykart-physics.md) | ze_crazykart_v4's kart in CS:GO physics |
| [ivp-collide-off](ivp-collide-off.md) | IVP: collisions off and on, teleports, pinning, DestroyObject |
| [ivp-contacts](ivp-contacts.md) | IVP contacts: the friction system, contact points, impacts, materials |
| [ivp-impact](ivp-impact.md) | IVP: the impact system and a kart on the ground |
| [ivp-mindist](ivp-mindist.md) | IVP: collision detection up to the impact |
| [ivp-physbox](ivp-physbox.md) | ze_crazykart's item physboxes, thruster frames, template placement |
| [ivp-pileup](ivp-pileup.md) | IVP pile-ups: impacts per PSI, ShouldFreezeObject, ShouldCollide |
| [ivp-shadow](ivp-shadow.md) | IVP shadows: how CS:GO's movers push a kart |
| [ivp-touch](ivp-touch.md) | IVP: two karts touching |
| [ivp-virtualmesh](ivp-virtualmesh.md) | Displacements in CS:GO physics: engine.dll's terrain collides, vphysics' virtual mesh |

## General helpers

Addresses are the CS:GO legacy (32-bit) DLLs' (image base 0x10000000), each row's module first.

| Address | What |
|---|---|
| vphysics.dll 0x100b8030 | AngleVectors(angles ecx, forward edx, right, up): radians in SSE, x87 fsincos stored as f32, the vectors in SSE (crazykart-physics.md 11) |
| vphysics.dll 0x1006d240 | IVP_U_Quat::set_quaternion(IVP_U_Matrix3) (trace and largest-diagonal branches, normalised past 1e-10) |
| vphysics.dll 0x10075300 / 0x100760e0 | IVP_U_Matrix product (a.rows b, a.t + a.rows b.t; sums ((0 + 1) + 2)) / inverse (transpose, -(R^T t)) |
| vphysics.dll 0x1001e7a0 / 0x10074750 / 0x1001bc70 | CreatePhysicsObject / IVP_Real_Object::init_object_core / CPhysicsObject::ComputeDragBasis (crazykart-physics.md 11) |
| server.dll 0x1031ab20 / 0x1031aa20 | PhysCreateWorld_Shared (the BSP's world solids as static objects, the key parser's blocks, SetWorldMaterialIndexTable) / the virtual-terrain displacements vdisp_%04d (crazykart-physics.md 14) |
| vphysics.dll 0x10002380 / 0x10036220 / 0x100b8a70 | ParseFile (signed-char whitespace, `{}()':` breaks, `//` and `/* */`, 0x3ff cap) / ParseKeyvalue (both lowercased, no value after `}`) / ASCII stricmp (ivp-contacts.md 7a) |
| vphysics.dll 0x10018e70 / 0x10018f50 / 0x10019130 / 0x10034130 / 0x10033800 / 0x10035100 | GetSurfaceIndex ($MATERIAL_INDEX_SHADOW -> 0xf000) / GetPhysicsProperties (0xf000 -> +0x180, else >= 0x80 -> 0, out of range -> entry 0) / copy an index's data / the key parser's ParseSurfaceTable / NextBlock / ParseCustom (SkipBlock) (ivp-contacts.md 7a; ported: tools/kart-ivp-surfaces.mjs) |
| vphysics.dll 0x100984c0 | IVP_Mindist_Minimize_Solver::p_minimize_FF: two triangles through each other, the nearest of point / point, point / face, point / edge, edge / edge by brute force (x 1.000001 margin), then that pair's case (ivp-mindist.md 14; sim/src/ivp/minimize_ff.rs) |
| engine.dll 0x101e6650 / 0x101e7760 / 0x101e7660 / 0x101f52a0 / 0x101f5150 / 0x101f1cd0 | CollisionBSPData_LoadDispInfo (the displacement trees from the lumps) / CM_CreateDispPhysCollide (a virtual mesh per tree) / the PHYSDISP lump's hull offsets / DispCollTrees_Alloc / CDispCollTree::Create / its degenerate-triangle check (ivp-virtualmesh.md 2) |
| engine.dll 0x101d7030 / 0x101d76f0 / 0x101d67f0 / 0x101d6930 / 0x101d9cc0 | CCoreDispInfo: ctor / InitDispInfo / the surface's FindSurfPointStartIndex / AdjustSurfPointData / Create (called natively by KartOracle's Disp.cs; their math TODO) (ivp-virtualmesh.md 2) |
| engine.dll 0x101e7580 / 0x101e75d0 / 0x101e7620 / 0x101f5200 / 0x101f3360 | CVirtualTerrain::GetVirtualMesh / GetWorldspaceBounds / GetTrianglesInSphere, CDispCollTree::GetVirtualMeshList, AABBTree_GetTrisInSphere (radius in XMM2; sim/src/ivp/vmesh.rs tris_in_sphere) (ivp-virtualmesh.md 2, 5) |
| vphysics.dll 0x10007ea0 / 0x1002b980 / 0x1002b370 / 0x1002b3e0 / 0x1002bdc0 / 0x1002acf0 | CreateVirtualMesh (collision slot 47) / CPhysCollideVirtualMesh's ctor / the frame's cache lock / build / cache insert / CMeshInstance::Init (ivp-virtualmesh.md 3) |
| vphysics.dll 0x10002fc0 / 0x10003240 / 0x10002cc0 / 0x100024a0 / 0x1002ac70 | a virtual mesh triangle's two-sided ledge / the packed hulls' unpack / one hull's ledge / a packed hull's data start / the hulls' unpacked size (ivp-virtualmesh.md 3) |
| vphysics.dll 0x1002bc50 / 0x1002af50 / 0x1002b110 / 0x1007a3e0 / 0x1002baf0 / 0x1002bc00 / 0x1002b260 / 0x1002b2d0 | the mesh surface manager's get_all_ledges_within_radius / its triangle query / its hull list / a point's squared distance to a ledge's first triangle / radius and deviation / mass centre / the collide's GetMassCenter / GetSphereRadius (ivp-virtualmesh.md 3, 5) |
| server.dll 0x1031ca00 / 0x1031ce60 / 0x102f7de0 / 0x1031cd80 / 0x1043c2d0 / 0x102b56f0 | CPhysBox::Spawn (0x4000 -> group 1) / CreateVPhysics / PhysSolidOverride (a no-defaults handler) / the thin-model damping test / CCSGameRules::ShouldCollide / CGameRules::ShouldCollide (ivp-physbox.md, ivp-pileup.md 8) |
| server.dll 0x1069bf80 / 0x1069b0d0 / 0x1069b500 / 0x1069af90 / 0x1069bb10 / 0x101cb0c0 | AngleMatrix (x87 fsincos, yaw pitch roll) / MatrixInvert / ConcatTransforms (SSE rows, +0.0 lanes) / MatrixAngles / VectorAngles (f64 x 1/pi) / the fpatan leaf; CPhysThruster::OnActivate 0x102ee940, ScriptSetForward 0x10206080 (ivp-physbox.md 7; sim/src/math/csgo_mathlib.rs, checked natively) |
| server.dll 0x1069f9d0 / 0x1069fbe0 / 0x10347270 / 0x10347630 / 0x10267350 | VMatrix::SetupMatrixOrgAngles (AngleMatrix + origin column) / MatrixMultiply (4x4, plain order) / CPointTemplate::AddTemplate (inline InverseTR, matEntityToTemplate) / CreateInstance / CEnvEntityMaker::SpawnEntity (ivp-physbox.md 8; sim/src/math/csgo_mathlib.rs, checked natively) |
| vphysics.dll 0x100338c0 | ParseSolid's keys (index, surfaceprop, mass, inertia, damping, rotdamping, volume, drag, massCenterOverride) (ivp-physbox.md 2; sim/src/ivp/solid_keys.rs) |
| vphysics.dll 0x10073b10 / 0x100767c0 / 0x10075060 | delete_and_check_vicinity's second half (a static: the recheck at 0x21, 0x10082ce0, 0x100767c0) / a static core's contacts redone, their dynamic partners woken / ensure_in_simulation (Wake) (ivp-collide-off.md 7) |
| server.dll 0x1028c550 / 0x1028c400 | CBreakable::Die (NOT_SOLID now, SUB_Remove at curtime + 0.1: 6 ticks) / its drop of what rests on top (ivp-collide-off.md 7a) |
| vphysics.dll 0x100149f0 / 0x1001b560 / 0x100739f0 / 0x10073810 / 0x100781d0 / 0x10071980 / 0x100123c0 | CleanupDeleteList (Simulate's first step) / CPhysicsObject's dtor (shadow, then the vicinity wake when +0x14 & 0x20 and not silent) / delete_and_check_vicinity / IVP_Real_Object's dtor (hull listeners, contacts, out of its core) / the core's deletion (revive queue, controllers, out of its unit: no split) / the unit's core removal / the friction created event ("touched dynamic" 0x20) (ivp-collide-off.md 7) |
| vphysics.dll 0x10012980 / 0x1001ba20 / 0x1001b850 / 0x10014760 | the IVP collision filter (the solver's answer; 0 for a 0x800 / 0x400 pair) / IsMoveable / RecheckCollisionFilter / DestroyObject (fast-remove, +0x1c 0x400, the delete queue) (ivp-pileup.md 7, ivp-collide-off.md 7) |
| server.dll 0x10222080 / 0x10221f70 / 0x10221ff0 / 0x102341d0 / 0x1020a4a0 | CFuncWallToggle Toggle / TurnOff / TurnOn / CCollisionProperty::SetSolidFlags / CollisionRulesChanged (ivp-pileup.md 7) |
| vphysics.dll 0x10019180 / 0x10019d30 / 0x10019ea0 / 0x10019d00 | CPhysicsSurfaceProps::ParseSurfaceData (0xac-byte entries, the IVP material at +0, +8 always 0: no contact slides) / its insert / its grow / the material manager's slot 1 (a triangle's index through the world table) (ivp-contacts.md 7) |
| vphysics.dll 0x100722d0 / 0x10077820 / 0x10077750 | the unit's sleep check (all cores' movement state 3) / a core frozen / its speeds zeroed and q_next = q_last (crazykart-physics.md 12) |
| vphysics.dll 0x10087370 / 0x10071ef0 / 0x10086b70 | stage 1's revive of the Wake queue / a unit revived to the active list's head / a core revived (speeds kept only when t_psi == 0) |
| vphysics.dll 0x10072850 | the active units' walk: the first n - 3 in order, the last three from the last back |
| vphysics.dll 0x10073370 / 0x1001bfe0 / 0x10072af0 | IPhysicsObject::Sleep (reference 1 at now - 20 s, then the sleep check) / EnableMotion / the core's pin |
| vphysics.dll 0x1001d910 / 0x1001c700 / 0x1001d4e0 | SetVelocity / ApplyForceCenter / SetPosition (-> 0x10074b20 beam_object_to_new_position -> the core's 0x10097750) |
| vphysics.dll 0x10012b60 / 0x100836e0 | the anomaly manager's speed (0.99 x max) / rot speed (0.9 x the limit) hooks, stage 3 |
| vphysics.dll 0x100d8112 | the CRT's SSE2 expf (k = round(x 16384 / ln 2), three 2^(j/16384) tables, a degree-1 term): math/csgo_libm.rs expf |
| vphysics.dll 0x100982d0 / 0x10099850 | IVP_Mindist::recalc_mindist (time stamp, P_Finish_Counter 20, the minimize table 0x10110a28) / minimize_default_poly_poly: the closest-feature walk PP 0x100b4e20, PK 0x100b6070, Leave_PK 0x100b62d0, KK 0x100b3070, Leave_KK 0x100b36f0, PF 0x100b1ca0, Leave_PF 0x100b26d0 (ivp-mindist.md 5) |
| vphysics.dll 0x1006cd90 / 0x10074000 | IVP_Cache_Object's update (the object's pose at the environment's time; q_last when f32(t - t_psi) == 0) / get_m_world_f_object_AT (ivp-mindist.md 3) |
| vphysics.dll 0x10095310 / 0x10093ce0 | update_exact_mindist_events (the hull conversion, the max collision speed, the event's time and delays) / calc_time_of_next_event (table 0x10110bb0: KK 0x100a2d90, PF 0x100a2160 over IVP_3D_Solver 0x100b72a0 / 0x100b7510 / 0x100b7130) (ivp-mindist.md 7-8) |
| vphysics.dll 0x100957c0 / 0x10097db0 / 0x10093bb0 | the mindist's hull event (the halfspace estimate) / stage 4's synapse loop / IVP_Hull_Manager's reset (ivp-mindist.md 6) |
| vphysics.dll 0x100a68e0 / 0x100a6bb0 | IVP_U_Min_List add (ascending, a value goes before its equals) / remove: the hull managers' and the time manager's queues (ivp-mindist.md 6) |
| vphysics.dll 0x1007ac30 / 0x10079920 | IVP_Compact_Ledge_Solver::calc_qlen_KK (the squared edge-edge distance by the KK checks) / the KK input's line distance (ivp-mindist.md 5) |
| vphysics.dll 0x10099e60 | IVP_Compact_Ledge_Solver::minimize_on_other_side: from the pierce triangle over non-positive qr edges to unvisited neighbours (ivp-mindist.md 5) |
| vphysics.dll 0x10094bc0 / 0x10094b40 | exact_mindist_went_invalid / insert_invalid_mindist (the manager's +0x14 list) (ivp-mindist.md 10) |
| vphysics.dll 0x10082ce0 | a revived core's exact mindists to a dynamic core outside any friction system: recalc, below remove_dist a contact (0x10088450) and the units merged; answer 1 restarts 0x10071ef0's walk (ivp-pileup.md 6) |
| vphysics.dll 0x10072850 / 0x10071ef0 | stage 2's walk over the active list (+0x18, next +8, three behind) / a unit's revival (unlinked from +0x1a8, linked at +0x18's head) (ivp-pileup.md 6) |
| vphysics.dll 0x10094300 (0x10094419, 0x100945ec) | create_exact_mindists gives each object of the pair a cache when it has none (0x1006ccb0), a frozen one's from its frozen core (ivp-pileup.md 6) |
| vphysics.dll 0x10073a50 / 0x100980e0 / 0x10094a70 | an object's invalid mindists rechecked in stage 2 / recalc_mindist with the finish counter 0 / insert_exact_mindist (no recalc, no events) (ivp-pileup.md 5) |
| vphysics.dll 0x100789b0 | the compact ledge tree walk of get_all_ledges_within_radius: node sphere then per-axis box size bytes x radius x 0.004 (ivp-mindist.md 10) |
| vphysics.dll 0x100a1150 / 0x100a1240 | IVP_Range_Manager get_coll_range_intra_objects / get_coll_range_in_world (constants from its ctor 0x100a10c0) (ivp-mindist.md 4) |
| vphysics.dll 0x1009c010 / 0x1009b4e0 / 0x1009c0c0 | IVP_Solver_Core_Reaction: the cores' response at a point along 1-3 world directions (levers M^T (d x dir), the matrix ((r1 c1 + r0 c0) + r2 c2) + 1/m), and pushes along two of them into the speeds (ivp-contacts.md 4) |
| vphysics.dll 0x100d7fc5 / 0x100d7a68 | the CRT's SSE2 cosf (sinf's body, its own constants 0x100fc4b0, the row a quarter turn on: edx + 0x1c7610) / asinf (|x| in [0.0625, sqrt(3)/2]: asin(c) from the row 0x100fb690 + a correction; [2^-16, 0.0625): x + x^3/6 + 0.075 x^5 + 0.0446 x^7; below: x): math/csgo_libm.rs, bit for bit over the oracle's sweep (ivp-impact.md 2-3) |
| vphysics.dll 0x100779f0 / 0x1008bb40 | an impact's core synchronised to the event's time (rot, q_next saved at core+0x1ac; rot from asinf of the last step's rotation) / the impact system's end (the next PSI from now, stage 4's events, the mindists re-planned) (ivp-impact.md 3, 5) |
| vphysics.dll 0x100b18a0 / 0x100b16e0 / 0x100b14f0 / 0x100b1a00 / 0x100b1b30 / 0x100b1af0 | IVP_Mindist_Recursive (vtable 0x100f2ef8, delegator 0x100f2ee8): its ctor / slot 7 and slot 8 (split a ledge tree node's hull: the side by the terminal ledge, the virtual features, the bigger node) / its own mindists (create_exact_mindists with a fixed and a "from" ledge) / its hull event (recalc with P_Finish_Counter 0, 0x100980e0) / folded back into an exact mindist (ivp-mindist.md 13) |
| vphysics.dll 0x10096180 / 0x10094a70 / 0x10094b40 | insert_hull_mindist at the managers' next-PSI value without the angular hull times / insert_exact_mindist / insert_invalid_mindist (ivp-mindist.md 13) |
| vphysics.dll 0x1007ec20 | IVP_Contact_Point ctor: each synapse head-inserted into its object's friction-synapse list (IVP object +0x28): a list runs newest contact first (ivp-collide-off.md 1) |
| vphysics.dll 0x10094de0 (0x10094fd4..) | recheck_ov_element's pair filter: either object moving, not both cores flags & 0x12 (static / pinned), +0x44 0x200 / 0x400, the env's collision filter (ivp-collide-off.md 4) |
| vphysics.dll 0x100187f0 / 0x10018720 | the friction snapshot's GetNormalForce (contact +0x54 x 39.370079) / GetSurfaceNormal (+0x7c..+0x84 into Source axes, signed by side, over |n| + 1.1920929e-07) (ivp-pileup.md 2) |
| server.dll 0x102087d0 | an entity's root move parent (ShouldCollide's same-hierarchy test, ivp-pileup.md 3) |
| server.dll 0x102f6b10 | CCollisionEvent::ShouldCollide: two fixed entities (movetype NONE / PUSH, parented, custom with a shadow) never collide; then collision groups, contents (ivp-shadow.md 8) |
| vphysics.dll 0x10019ba1..0x10019c38 | the surfaceproperties parser's fallback entry for material index 0xf000 (the shadow material): friction 0.8, elasticity 0.001 (ivp-shadow.md 8) |
| vphysics.dll 0x10020fa0 / 0x10023fb0 | ComputeController (damp the speed by -damping capped at maxDampSpeed, add delta x scale capped at maxSpeed; the impulse out) / a quaternion's delta a x conj(b) in its sum order, normalised past 1e-10 (ivp-shadow.md 4) |
| vphysics.dll 0x10076950 | a core's objects changed (a new material, a mass): calc_calc, the objects' movement bytes, a core not simulated revived now (0x10071ef0) else its references re-timed, the friction contacts re-mixed (ivp-shadow.md 3) |
| vphysics.dll 0x10032e60 | CollideGetAABB's ledge-tree walk (left child at +0x1c first, then +[node]; a leaf's six support points into the min / max) (ivp-shadow.md 5) |
| server.dll 0x101f7f40 | CBaseEntity::UpdatePhysicsShadowToCurrentPosition (slot 163): UpdateShadow(abs origin +0x1dc, abs angles +0x1e8, false, dt) unless VPHYSICS (ivp-shadow.md 1) |
| vphysics.dll 0x100713b0 / 0x10071d40 / 0x10071dc0 | a simulation unit's controller list rebuilt from its cores' lists (each from its last controller: equal priorities reversed) / a controller attached to a core and its unit / detached (ivp-impact.md 4, 6) |
| vphysics.dll 0x100d7e25 | the CRT's SSE2 atanf (table 0x100fbee8 by c's high word; ported bit for bit: sim/src/math/csgo_atan.rs, ivp-contacts.md 6) |
| vphysics.dll 0x1009c880 / 0x1009c980 / 0x1009d270 | IVP_Great_Matrix_Many_Zero Gauss with pivoting / back substitution; IVP_Linear_Constraint_Solver (the complementarity solve) (ivp-contacts.md 5) |
| vphysics.dll 0x1006dc70 | the environment's temporary memory (env+0xa0 / +0x9c): a block per PSI (the long-term infos) |
