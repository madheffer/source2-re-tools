# Displacements in CS:GO physics: engine.dll's terrain collides, vphysics' virtual mesh

CS:GO legacy: engine.dll (md5 9887428753ab685594450a742ec3c87d, Ghidra `/engine.dll`, image base 0x10000000, has RTTI), vphysics.dll (Ghidra `/csgo_vphysics_legacy.dll`, no RTTI), csgo/bin/server.dll. Each displacement is a static VPhysics object `vdisp_%04d` whose collide is a virtual mesh: vphysics asks the engine for the triangles near a point and makes IVP ledges from them. ze_crazykart_v4 has 56 displacements (hills, snow slopes, trash piles).

## Functions

| Address | Module | What |
|---|---|---|
| 0x1031aa20 | server | the terrain objects (from PhysCreateWorld_Shared when the vcollide has a `virtualterrain` block) |
| 0x101e6650 | engine | CollisionBSPData_LoadDispInfo (ECX the bsp data, EDX the texinfo array) |
| 0x10148d00 | engine | CMapLoadHelper |
| 0x101f52a0 | engine | DispCollTrees_Alloc (reads the count global; tree +0x10 = its index) |
| 0x101f4c60 | engine | CDispCollTree ctor |
| 0x101d7030 | engine | CCoreDispInfo ctor (thiscall) |
| 0x101d76f0 | engine | CCoreDispInfo InitDispInfo (thiscall, ret 0x18) |
| 0x101d67f0 | engine | FindSurfPointStartIndex (this = core +0x10) |
| 0x101d6930 | engine | AdjustSurfPointData (this = core +0x10) |
| 0x101d9cc0 | engine | CCoreDispInfo::Create (math unread) |
| 0x101f5150 | engine | CDispCollTree::Create (vtable slot 0, ret 8) |
| 0x101f1ea0 | engine | the tree's verts, tris |
| 0x101f23d0 | engine | the AABB tree |
| 0x101f24f0 | engine | the bounds into +4 / +0x14 |
| 0x101e7760 | engine | CM_CreateDispPhysCollide (ECX the PHYSDISP lump, EDX its size) |
| 0x101e7660 | engine | the PHYSDISP lump's parse |
| 0x101f1cd0 | engine | tree valid: no triangle edge with length^2 < 0.5, `(dy^2 + dx^2) + dz^2` |
| 0x101e7580 | engine | CVirtualTerrain slot 0 GetVirtualMesh(userData, virtualmeshlist_t*) |
| 0x101f5200 | engine | the tree's virtual mesh list (thiscall, ret 4) |
| 0x101e75d0 | engine | CVirtualTerrain slot 1 GetWorldspaceBounds |
| 0x101e7620 | engine | CVirtualTerrain slot 2 GetTrianglesInSphere(userData, center, radius, virtualmeshtrianglelist_t*) |
| 0x101f3360 | engine | AABBTree_GetTrisInSphere (ECX the tree, radius in XMM2, ret 0x10) |
| 0x10007ea0 | vphysics | IPhysicsCollision::CreateVirtualMesh (slot 47) -> 0x1002b980 |
| 0x1002b980 | vphysics | makes the CPhysCollideVirtualMesh |
| 0x1002b440 | vphysics | builds the outer hull(s) with buildOuterHull (unread) |
| 0x1002b1a0 | vphysics | CPhysCollideVirtualMesh slot 0 dtor |
| 0x1002ae50 | vphysics | slot 1 CreateSurfaceManager(short& type): type = 3, a new 8-byte surface manager {vtable 0x100e37a8, the collide} |
| 0x1002ae90 | vphysics | slot 2 GetAllLedges (the frame's ledges, 0x30 apart) |
| 0x1002aef0 | vphysics | slot 3 GetSerializationSize |
| 0x1002af00 | vphysics | slot 4 Serialize |
| 0x1002b260 | vphysics | slot 6 GetMassCenter: `(mins + maxs) x 0.5` per axis |
| 0x1002af30 | vphysics | slot 8 GetInertia = (1, 1, 1); also the surface manager's slot 3 |
| 0x1002b2d0 | vphysics | slot 10 GetSphereRadius: `|maxs - (maxs + mins) x 0.5|` |
| 0x1002b100 | vphysics | slot 11: Msg("Virtual mesh!\n") |
| 0x1002b370 | vphysics | locks the collide's frame (handle +0x14), or builds it under the mutex 0x101162ac |
| 0x1002b3e0 | vphysics | the frame's build: GetVirtualMesh, pHull = the collide's own when the list has none |
| 0x1002bdc0 | vphysics | EnsureCapacity by the estimate, then Init |
| 0x100bba50 | vphysics | the cache's EnsureCapacity |
| 0x100bb780 / 0x100bb830 | vphysics | the cache's references (keep a used frame) |
| 0x1002acf0 | vphysics | the frame's Init(list) |
| 0x1002ac70 | vphysics | the hulls' unpacked size |
| 0x10002fc0 | vphysics | a triangle's ledge (ledge, points, i0, i1, i2) |
| 0x10003240 | vphysics | unpacks each hull in turn |
| 0x10002cc0 | vphysics | a hull's ledge (ledge, points, hull, h) |
| 0x100024a0 | vphysics | finds hull h's data in the packed hull |
| 0x1002bba0 | vphysics | surface manager 0 get_single_convex |
| 0x1002bc00 | vphysics | 1 get_mass_center |
| 0x1002baf0 | vphysics | 2 get_radius_and_radius_dev_to_given_center |
| 0x1002bc50 | vphysics | 4 get_all_ledges_within_radius(center, radius, root_ledge, ..., out) |
| 0x1002b110 | vphysics | the hulls' ledges (at most 2) |
| 0x1002af50 | vphysics | the triangles' ledges within the radius |
| 0x1002ac20 | vphysics | with 2 hulls: each one's half of the ledges |
| 0x1007a3e0 | vphysics | squared distance point to a ledge's triangle -> XMM0 |
| 0x1002bcd0 | vphysics | 5 get_all_terminal_ledges: the collide's GetAllLedges |
| 0x1002ba20 | vphysics | 6 insert_all_ledges_hitting_ray (unread) |
| 0x1002ba00 / 0x1002ba10 | vphysics | 7 add_reference_to_ledge (locks the frame) / 8 remove_reference (unlocks); 10 get_type |

## Fields

| Offset | Field |
|---|---|
| dispinfo +0 | start position (0xb0 each) |
| dispinfo +0x14 / +0x18 | power / minTess |
| dispinfo +0x20 | contents |
| face +0xc | dispinfo index (short) |
| CCoreDispInfo +0x10 | the CCoreDispSurface: +0x10 face index, +0x14 point count, +0x18 the points, +0x2d8 the start index |
| CCoreDispInfo +0x2c8 | flags |
| CCoreDispInfo +0x2cc / +0x2ec | contents / start position |
| CDispCollTree +0 | vtable 0x104b4298 (0x10c bytes) |
| CDispCollTree +4 / +0x14 | mins / maxs |
| CDispCollTree +0x10 | its index |
| CDispCollTree +0x20 | contents |
| CDispCollTree +0x28 | power |
| CDispCollTree +0x2c | flags (ushort; bit 1 NOPHYSICS) |
| CDispCollTree +0x2e | the texdata's ushort +6 |
| CDispCollTree +0x6c..+0x74 | surface props (5 shorts) |
| CDispCollTree +0x78 | verts (Vector; CUtlVector: memory, alloc count, grow, count, elements; count +0x84) |
| CDispCollTree +0x8c | tris (0x18 each, count +0x98: +0 three ushorts whose low 9 bits are vert indices, then flags / plane) |
| CDispCollTree +0xa0 | AABB nodes (0x60 each, count +0xac) |
| CDispCollTree +0xb4 | leaves (4 bytes: two ushort triangle indices, count +0xc0) |
| bounds entry (0x30) +0 / +0x10 | mins / maxs (tree +4 / +0x14) |
| bounds entry +0x20 / +0x24 | tree +0x10 (index) / tree +0x20 (contents) |
| CVirtualTerrain +0 / +4 / +8 | vtable 0x104b34d8 / the hull data / the hull offsets (CUtlVector at 0x105a6ad0) |
| virtualmeshlist_t +0 | pVerts (tree +0x78) |
| virtualmeshlist_t +4 | indexCount = 3 x triangleCount |
| virtualmeshlist_t +8 | triangleCount = `2 << (2 power)` |
| virtualmeshlist_t +0xc | vertexCount (tree +0x84) |
| virtualmeshlist_t +0x10 | surfacePropsIndex = (int)(short) tree +0x6c |
| virtualmeshlist_t +0x14 | pHull (0 from 0x101f5200) |
| virtualmeshlist_t +0x18 | indices (ushort[]): each tri's three ushorts & 0x1ff, in the tris' order |
| CPhysCollideVirtualMesh (0x1c) +0 | vtable 0x100e37d4 |
| CPhysCollideVirtualMesh +4 / +8 / +0xc | the handler / userData / buildOuterHull |
| CPhysCollideVirtualMesh +0x10 | m_pHull = 0 |
| CPhysCollideVirtualMesh +0x14 | the cache handle = -1 |
| CPhysCollideVirtualMesh +0x18 | ledge count (short) = 0; triangleCount once built |
| CMeshInstance (0xc) +0 / +4 | memory size / the memory |
| CMeshInstance +8 / +0xa | the hull's offset (ushort) / the hull count (byte) |
| surface manager +4 | the collide |

## Constants

| Value | What |
|---|---|
| 0x1391cbdc | g_pDispCollTrees (CDispCollTree[count], 0x10c each) |
| 0x1391cbe0 | g_pDispBounds (0x30 each) |
| 0x1391cbe4 | g_DispCollTreeCount |
| 0x1081320c | g_TerrainList (CPhysCollide* per displacement) |
| 0x105a6ac8 | g_VirtualTerrain (CVirtualTerrain, IVirtualMeshEvent) |
| 0x104b3280 | `$surfaceprop2..4` name table |
| 0x104b3308 | the invalid-tree warning |
| 0x10116258.. | the frame LRU (CDataManager) |
| 0x101162ac | its mutex |
| 0x10106930 | k = 0.0254 |
| 0x10106934 | s = 39.37008 |
| 0x100f4010 | 1e20 |
| 0x40000000 | InitDispInfo flag when minTess has that bit |
| 0x8000 | the server's terrain index limit |
| 0x304 | a triangle ledge's flags (size_div_16 3, is_compact 4) |
| lumps | 26 dispinfo (0xb0 each), 3 vertexes, 12 edges, 13 surfedges, 7 faces (58 with HDR), 33 disp verts (0x14 each), 48 disp tris (ushort each), 63 multiblend (0x50 a vert), 28 PHYSDISP |
| IVEngineServer slot 41 (0xa4) | GetCollideForVirtualTerrain(i) |
| physcollision slot 47 (0xbc) | CreateVirtualMesh |

## 1. The server's objects (0x1031aa20)

For i in 0..0x8000, each non-null `engine->GetCollideForVirtualTerrain(i)`: objectparams {massCenterOverride 0, mass 1, inertia 1, damping 0.1, rotdamping 0.1, rotInertiaLimit 0.05, name `vdisp_%04d` (a stack buffer), gameData 0, volume 0, drag 1, enableCollisions 1}; physenv slot 8 CreatePolyObjectStatic(collide, physprops->GetSurfaceIndex("default"), origin 0, angles 0, &params); callback flags (slot 23) | 0x200 through slot 22; slot 84 (2).

## 2. engine.dll: the collision trees (LoadDispInfo 0x101e6650)

1. count = dispinfo size / 0xb0; DispCollTrees_Alloc; the bounds array.
2. Each displacement's face: the last face whose dispinfo (face +0xc) names it.
3. Per displacement with a face, in order (the vert / tri / multiblend cursors advance by each one's counts, not by the dispinfo's start fields):
   1. A CCoreDispInfo on the stack (0x101d7030): contents (dispinfo +0x20) at +0x2cc, start position (dispinfo +0) at +0x2ec.
   2. InitDispInfo (power, minTess, the disp verts, the disp tris, 0x40000000 when minTess has that bit else 0, the multiblend verts).
   3. The surface: +0x10 face index, +0x14 point count 4 (only for 4 edges; more than 4: skipped), +0x18 the points: surfedge e >= 0 -> edges[e].v[0], e < 0 -> edges[-e].v[1].
   4. FindSurfPointStartIndex (the point nearest the start by `(dy^2 + dx^2) + dz^2`, first wins, into surface +0x2d8), AdjustSurfPointData.
   5. Tree +0x28 = 0; with 4 points: Create 0x101d9cc0, then the tree's Create 0x101f5150(the core, {byte: has a 5th surface prop, float: $surfacepropalphafilter (0.5 default) x 3.0}): flags (core +0x2c8) -> tree +0x2c; 0x101f1ea0; 0x101f23d0; with verts and nodes 0x101f24f0, then each min - 1.0, max + 1.0.
   6. The bounds entry.
   7. The material (texinfo -> texdata -> name, `materials->FindMaterial(name, "World textures")`): `$surfaceprop` -> the physprops index into +0x6c, +0x6e, +0x70, +0x72 (all four); `$surfaceprop2..4` each its own slot, the 5th into +0x74; tree +0x2e = texdata ushort +6.
4. CM_CreateDispPhysCollide:
   - 0x101e7660: lump = ushort count, ushort size[count], the hull data; offset[i] = the sum of the sizes before it, -1 for size 0xffff; the data copied.
   - Per tree: NOPHYSICS -> null; 0x101f1cd0 false -> the warning and null; else CreateVirtualMesh({&g_VirtualTerrain, userData = i, buildOuterHull = (lump size <= 0)}).

ze_crazykart_v4: every displacement power 3: 81 verts, 128 tris, 21 nodes, 64 leaves. `$surfaceprop` from the pakfile's VMTs: "sand" for LUFFAREN/CK_*, "dirt" for NATURE/TRASH01A.

### CVirtualTerrain

- GetVirtualMesh 0x101e7580: the tree's 0x101f5200, then pHull = 0, or the hull data + offset[index] when there is data and the offset is >= 0.
- GetWorldspaceBounds 0x101e75d0: the bounds entry's mins (+0), maxs (+0x10).
- GetTrianglesInSphere 0x101e7620: list->triangleCount = 0x101f3360(center, -, list->triangleIndices, 0xc00), the radius in XMM2.
- 0x101f3360: `r2 = r x r`; a breadth-first queue of node numbers from 0. A number >= the node count is a leaf and ends the walk: every queue entry from there (all leaves) writes its two triangle indices while count + 2 <= max; returns the count. A node (0x60: mins x[4] y[4] z[4], maxs x[4] y[4] z[4] for its four children) tests child k: `dx = maxps(maxps(0, min.x - c.x), c.x - max.x)` (maxps a, b = a > b ? a : b), dy, dz alike; in when `(dy^2 + dx^2) + dz^2 <= r2` (cmpleps); child k in order 0..3 queues `4 x node + 1 + k`. An empty queue returns 0.

## 3. vphysics.dll: CPhysCollideVirtualMesh (0x1002b980)

With buildOuterHull: GetVirtualMesh, then 0x1002b440 builds the hull(s) into +0x10 (not ze_crazykart's path: its PHYSDISP lump has every hull).

The frame (CMeshInstance) is made on demand and kept in the LRU: 0x1002b370 locks the handle, or builds it (0x1002b3e0, 0x1002bdc0) and sets the collide's ledge count = triangleCount.

Init 0x1002acf0(list): size = `triangleCount x 0x30 + vertexCount x 0x10 + the hulls' unpacked size` (0x1002ac70: `hull count x 0x10 + each hull's triangle count (header byte +0) x 0x10`); memory 16-aligned, zeroed:

- The points, after the ledges: each vert (x, y, z) -> `(x k, -(z k), k y, 0)` (the products in that operand order).
- One ledge per triangle, 0x30 bytes (0x10002fc0): +0 the points' offset, +8 flags 0x304, +0xc 2 triangles. Triangle 0: tri_index 0, pierce_index 1, edges (i0, opposite +6), (i1, +4), (i2, +2). Triangle 1: tri_index 1, pierce_index 0, edges (i0, -2), (i2, -4), (i1, -6). Material bits 0, no virtual edges: a two-sided flat ledge whose contact takes the object's own surface ("default"), not the displacement's $surfaceprop.
- The hulls, when pHull: frame +0xa = the packed count byte, +8 = the offset; 0x10003240 unpacks each (0x10002cc0) in turn.

### The packed hull (virtualmeshhull_t, vbsp's)

- +0 hull count, 3 pad bytes; per hull 5 bytes at `+4 + 5h`: {+0 triangle count, +1 virtual triangle count, +2 edge count, +3 virtual edge count, +4 first vert}.
- Then per hull (0x100024a0: after all headers, each earlier hull taking `(edges + 2 x triangles) x 2` bytes): 4 bytes a triangle {v0 edge, v1 edge, v2 edge (edge numbers), +3 pierce index}, then 2 bytes an edge {start vert, end vert}, relative to the hull's first vert.
- 0x10002cc0: +0 the points' offset (the frame's own points), +8 flags = `(triangles + 1) << 8 | 5` (is_compact, has_children 1: a recursive hull), +0xc triangle count, +4 0. Per triangle t: tri_index t, is_virtual = (t < the virtual count: virtual ones first), pierce_index = byte +3; per edge slot j, e = the triangle's byte j: the first triangle to use e takes the edge's start vert (+ first vert) and remembers its word; the second takes the end vert and both get each other as opposite (the word distance); is_virtual = (e < the virtual edge count).
- A non-virtual hull triangle lies on the terrain itself (where it is convex: a hill's flat top). IVP_Mindist_Recursive's impact there is a plain do_impact against the hull ledge ([ivp-mindist.md](ivp-mindist.md) 13, slot 8: with no virtual feature, or over the limit, it runs do_impact 0x1008b020 at 0x100b1574), no triangle ledge involved.
- ze_crazykart_v4: one hull each, 30-158 triangles, up to 31 of them real (displacement 8, the dirt hill's top).

### The surface manager (vtable 0x100e37a8)

- 0 get_single_convex: the first hull when the hull count is 1, else null.
- 1 get_mass_center: the collide's GetMassCenter (x, y, z) -> `(k x, -(k z), k y)`.
- 2 get_radius_and_radius_dev_to_given_center: both = `sqrt((dy^2 + dx^2) + dz^2) + k x the sphere radius` (d = the mass centre - the given centre).
- 4 get_all_ledges_within_radius 0x1002bc50: root_ledge null and a hull count: the hulls (0x1002b110); else 0x1002af50: GetTrianglesInSphere(userData, `(c.x s, c.z s, -(c.y s))`, `s x r`, &list); none -> nothing. With 2 hulls (0x1002ac20): root == hull 0 takes triangles [0, n / 2), else [n / 2, n). A listed triangle in range: its ledge (frame + 0x30 x index) passes unless 0x1007a3e0(ledge, its first triangle, center)'s q > r^2 (comiss, ja).

## 5. Sums

- GetSphereRadius 0x1002b2d0: `sqrt(((ex^2 + ey^2) + ez^2))`, `e = maxs - (maxs + mins) x 0.5`.
- 0x1007a3e0(ledge, first triangle, p) -> XMM0: calc_unscaled_qr_vals_F_space of the first edge; no sign bit set: `n = (P1 - P0) x (P2 - P0)`, `q = (1.0 / ((ny^2 + nx^2) + nz^2)) x (((ny p.y + nx p.x) + nz p.z) - ((P0.y ny + nx P0.x) + P0.z nz))^2`. Else min = 1e20 and the edges 2, 1, 0 (A its start, B the next's, k = B - A):
  - `c0 = -(((A.y - p.y) k.y + (A.x - p.x) k.x) + (A.z - p.z) k.z) + FLT_MIN`
  - `c1 = (((B.y - p.y) k.y + (B.x - p.x) k.x) + (B.z - p.z) k.z) + FLT_MIN`
  - 0 > c0: `q = |p - A|^2`; else 0 > c1: nothing; else `q = (1.0 / (|A - B|^2 + 1e-18)) x |(p - A) x k|^2`; `min = minss(q, min)`.

## Unread

- CCoreDispInfo::Create and CDispCollTree::Create's own math (0x101d9cc0, 0x101f1ea0, 0x101f23d0, 0x101f24f0).
- 0x1002b440 (buildOuterHull: a map without the PHYSDISP lump).
- Two hulls on one displacement (0x1002ac20 read; no map seen with one).
- The frame cache's budget (0x100bba50) and what an eviction changes (a frame rebuilt at another address).
- The ray path (slot 6, 0x1002ba20).
- Multiblend displacements (lump 63).
