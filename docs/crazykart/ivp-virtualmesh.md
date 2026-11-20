# The displacements in CS:GO's physics: engine.dll's terrain collides, vphysics' virtual mesh

ze_crazykart_v4 has 56 displacements (hills, snow slopes, trash piles). CS:GO gives each one a static VPhysics object
`vdisp_%04d` whose collide is a **virtual mesh**: vphysics asks the engine for the triangles near a point and makes
IVP ledges from them. Traced 2026-11-18 from CS:GO legacy `bin/engine.dll` (md5 9887428753ab685594450a742ec3c87d,
Ghidra `/engine.dll`, image base 0x10000000, has RTTI), `bin/vphysics.dll` (Ghidra `/csgo_vphysics_legacy.dll`, no
RTTI) and `csgo/bin/server.dll`. Status at the end.

## 1. The server: 0x1031aa20 (from PhysCreateWorld_Shared when the vcollide has a `virtualterrain` block)

For i in 0..0x8000: `engine->GetCollideForVirtualTerrain(i)` (IVEngineServer slot 41, 0xa4); for each non-null:
objectparams {massCenterOverride 0, mass 1, inertia 1, damping 0.1, rotdamping 0.1, rotInertiaLimit 0.05, name
`vdisp_%04d` (a stack buffer), gameData 0, volume 0, drag 1, enableCollisions 1}, physenv slot 8
CreatePolyObjectStatic(collide, physprops->GetSurfaceIndex("default"), origin 0, angles 0, &params), callback flags
(slot 23) | 0x200 through slot 22, slot 84 (2).

## 2. engine.dll: the collision trees

Globals: `g_pDispCollTrees` 0x1391cbdc (CDispCollTree[count], 0x10c each), `g_pDispBounds` 0x1391cbe0 (0x30 each),
`g_DispCollTreeCount` 0x1391cbe4, `g_TerrainList` 0x1081320c (CPhysCollide* per displacement), `g_VirtualTerrain`
0x105a6ac8 (CVirtualTerrain: +0 vtable 0x104b34d8, +4 the hull data, +8 the hull offsets (a CUtlVector at
0x105a6ad0)).

**CollisionBSPData_LoadDispInfo 0x101e6650** (ECX the bsp data, EDX the texinfo array). Lumps through CMapLoadHelper
0x10148d00: 26 dispinfo (0xb0 each), 3 vertexes, 12 edges, 13 surfedges, 7 faces (58 when HDR is on), 33 disp verts
(0x14 each), 48 disp tris (ushort each), 63 multiblend (0x50 a vert), 28 PHYSDISP. Then:
- count = dispinfo size / 0xb0; `DispCollTrees_Alloc` 0x101f52a0 (reads the count global; each tree's ctor
  0x101f4c60; tree +0x10 = its index); the bounds array.
- each displacement's face: the last face whose dispinfo (face +0xc, short) names it.
- per displacement with a face, in order (the vert / tri / multiblend cursors advance by each one's counts, not by
  the dispinfo's own start fields):
  1. a CCoreDispInfo on the stack: ctor 0x101d7030 (thiscall); contents (dispinfo +0x20) at +0x2cc; the start
     position (dispinfo +0) at +0x2ec.
  2. InitDispInfo 0x101d76f0 (thiscall, ret 0x18): (power = dispinfo +0x14, minTess = +0x18, the disp verts, the
     disp tris, 0x40000000 when minTess has that bit else 0, the multiblend verts).
  3. the surface (CCoreDispSurface at +0x10): +0x10 the face index, +0x14 point count 4 (only when the face has 4
     edges; more than 4: the displacement is skipped), +0x18 the face's points: surfedge e >= 0 -> edges[e].v[0],
     e < 0 -> edges[-e].v[1].
  4. FindSurfPointStartIndex 0x101d67f0 (this = +0x10: the point nearest the start position by (dy^2 + dx^2) + dz^2,
     first wins, into surface +0x2d8) and AdjustSurfPointData 0x101d6930 (this = +0x10).
  5. tree +0x28 = 0; when the point count is 4: Create 0x101d9cc0, then the tree's Create (vtable slot 0 =
     0x101f5150, ret 8): (the CCoreDispInfo, {byte: has a 5th surface prop, float: $surfacepropalphafilter (0.5
     default) x 3.0}). 0x101f5150: flags (core +0x2c8) -> tree +0x2c; 0x101f1ea0 (verts, tris); 0x101f23d0 (the
     AABB tree); with verts and nodes, 0x101f24f0 (the bounds into +4 / +0x14) and then each min - 1.0, max + 1.0.
  6. the bounds entry: mins = tree +4.., maxs = tree +0x14.., +0x20 = tree +0x10 (the index), +0x24 = tree +0x20
     (contents).
  7. the material (texinfo -> texdata -> the name, `materials->FindMaterial(name, "World textures")`):
     `$surfaceprop` -> physprops index into tree +0x6c, +0x6e, +0x70, +0x72 (all four); `$surfaceprop2..4` (the
     name table 0x104b3280) each its own slot, the 5th into +0x74; tree +0x2e = the texdata's ushort +6.
- then the PHYSDISP lump and **CM_CreateDispPhysCollide 0x101e7760** (ECX the lump, EDX its size):
  - 0x101e7660: lump = ushort count, ushort size[count], the hull data. Offset[i] = the sum of the sizes before it,
    -1 for size 0xffff; the data copied.
  - per tree: flags (+0x2c) bit 1 (NOPHYSICS) -> null. 0x101f1cd0 (valid: no triangle edge with length^2 < 0.5,
    (dy^2 + dx^2) + dz^2) false -> a warning (0x104b3308) and null. Else physcollision slot 47 (0xbc)
    CreateVirtualMesh({&g_VirtualTerrain, userData = i, buildOuterHull = (lump size <= 0)}).

**CDispCollTree** (0x10c bytes): +0 vtable 0x104b4298, +4 mins, +0x10 its index, +0x14 maxs, +0x20 contents, +0x28
power, +0x2c flags (ushort), +0x2e the texdata value, +0x6c..+0x74 surface props (5 shorts), then CUtlVectors
(memory, alloc count, grow, count, elements): +0x78 verts (Vector, count +0x84), +0x8c tris (0x18 bytes each, count
+0x98: +0 three ushorts whose low 9 bits are vert indices, then flags / plane), +0xa0 AABB nodes (0x60 each, count
+0xac), +0xb4 leaves (4 bytes: two ushort triangle indices, count +0xc0). ze_crazykart_v4: every displacement
power 3: 81 verts, 128 tris, 21 nodes, 64 leaves.

**CVirtualTerrain** (IVirtualMeshEvent, vtable 0x104b34d8):
- slot 0 GetVirtualMesh(userData, virtualmeshlist_t*) 0x101e7580: the tree's 0x101f5200, then pHull = 0, or the
  hull data + offset[index] when there is data and the offset is >= 0.
  0x101f5200 (thiscall, ret 4): triangleCount (+8) = 2 << (2 power), indexCount (+4) = 3 x that, vertexCount (+0xc)
  = tree +0x84, pVerts (+0) = tree +0x78, surfacePropsIndex (+0x10) = (int)(short) tree +0x6c, pHull (+0x14) = 0,
  indices (+0x18, ushort[]) = each tri's three ushorts & 0x1ff in the tris' order.
- slot 1 GetWorldspaceBounds 0x101e75d0: the bounds entry's mins (+0) and maxs (+0x10).
- slot 2 GetTrianglesInSphere(userData, center, radius, virtualmeshtrianglelist_t*) 0x101e7620: list->triangleCount
  = the tree's 0x101f3360(center, -, list->triangleIndices, 0xc00) with the radius in XMM2.
  **0x101f3360** (AABBTree_GetTrisInSphere; ECX the tree, ret 0x10): r2 = r x r; a breadth-first queue of node
  numbers starting with 0. A number >= the node count is a leaf and ends the walk: every queue entry from there on
  (all leaves) writes its two triangle indices while count + 2 <= max; returns the count. A node (0x60 bytes: mins
  x[4] y[4] z[4], maxs x[4] y[4] z[4] for its four children) tests each child k: d = max(max(0, min - c), c - max)
  per axis (maxps), in when (dy^2 + dx^2) + dz^2 <= r2 (section 5); child k in order 0..3 queues 4 x node + 1 + k.
  An empty queue returns 0.

## 3. vphysics.dll: CPhysCollideVirtualMesh and its surface manager

`IPhysicsCollision::CreateVirtualMesh` (slot 47) 0x10007ea0 -> **0x1002b980**: a 0x1c-byte CPhysCollideVirtualMesh
(vtable 0x100e37d4): +4 the handler, +8 userData, +0xc buildOuterHull, +0x10 m_pHull = 0, +0x14 the cache handle
= -1, +0x18 ledge count (short) = 0. With buildOuterHull: GetVirtualMesh, then 0x1002b440 builds the hull(s) into
+0x10 (not this map's path: its PHYSDISP lump has every hull).

Its vtable: 0 dtor 0x1002b1a0; 1 CreateSurfaceManager(short& type) 0x1002ae50: type = 3, a new 8-byte surface
manager {vtable 0x100e37a8, the collide}; 2 GetAllLedges 0x1002ae90 (the frame's ledges, 0x30 apart); 3
GetSerializationSize 0x1002aef0; 4 Serialize 0x1002af00; 6 GetMassCenter 0x1002b260: the bounds' (mins + maxs) x 0.5
per axis; 8 GetInertia 0x1002af30 = (1, 1, 1); 10 GetSphereRadius 0x1002b2d0: |maxs - (maxs + mins) x 0.5|; 11
0x1002b100 Msg("Virtual mesh!\n").

**The frame** (CMeshInstance, 0xc bytes: +0 memory size, +4 the memory, +8 the hull's offset (ushort), +0xa the hull
count (byte)) is made on demand and kept in an LRU (CDataManager at 0x10116258..: 0x1002b370 locks the collide's
handle +0x14, or under the mutex 0x101162ac builds it: 0x1002b3e0 -> GetVirtualMesh, pHull = the collide's own
when the list has none, 0x1002bdc0 (the cache's EnsureCapacity 0x100bba50 by the estimate, then Init) and the
collide's ledge count +0x18 = triangleCount). TODO(trace): the cache's budget and what an eviction changes (a frame
rebuilt at another address; the references 0x100bb780 / 0x100bb830 keep a used one).

**Init 0x1002acf0**(list): size = triangleCount x 0x30 + vertexCount x 0x10 + the hulls' unpacked size
(0x1002ac70: hull count x 0x10 + each hull's triangle count (header byte +0) x 0x10); memory 16-aligned, zeroed:
- the points, after the ledges: each vert (x, y, z) -> (x k, -(z k), k y, 0), k = 0x10106930 = 0.0254 (the
  products in that operand order).
- one ledge per triangle, 0x30 bytes, **0x10002fc0**(ledge, points, i0, i1, i2): +0 the points' offset, +8 flags
  0x304 (size_div_16 3, is_compact 4), +0xc 2 triangles. Triangle 0: tri_index 0, pierce_index 1, edges (i0,
  opposite +6), (i1, +4), (i2, +2). Triangle 1: tri_index 1, pierce_index 0, edges (i0, -2), (i2, -4), (i1, -6).
  Material bits 0, no virtual edges. So a terrain triangle is a two-sided flat ledge, and its material index is 0:
  the contact takes the object's own surface ("default"), not the displacement's $surfaceprop.
- the hulls, when pHull: frame +0xa = the packed hull's count byte, +8 = the offset, **0x10003240** unpacks each
  (0x10002cc0) one after the other.

**The packed hull** (virtualmeshhull_t, vbsp's): +0 hull count, 3 pad bytes; per hull 5 bytes at +4 + 5h: {+0
triangle count, +1 virtual triangle count, +2 edge count, +3 virtual edge count, +4 first vert}; then per
hull (0x100024a0 finds it: after all headers, each earlier hull taking (edges + 2 x triangles) x 2 bytes): 4 bytes
a triangle {v0 edge, v1 edge, v2 edge: edge numbers; +3 the pierce index}, then 2 bytes an edge {start vert, end
vert}, both relative to the hull's first vert.
**0x10002cc0**(ledge, points, hull, h): +0 the points' offset (the frame's own points), +8 flags = (triangles + 1)
<< 8 | 5 (is_compact, has_children 1: a recursive hull), +0xc the triangle count, +4 0. Per triangle t: tri_index
t, is_virtual = (t < the virtual count: the virtual ones come first), pierce_index = byte +3; per edge slot j, edge
number e = the triangle's byte j: the first triangle to use e takes the edge's start vert (+ the first vert) and
remembers its word; the second takes the end vert and both get each other as opposite (the word distance);
is_virtual = (e < the virtual edge count). A hull triangle that isn't virtual lies on the terrain itself (where it
is convex: a hill's flat top): IVP_Mindist_Recursive's impact there is a plain do_impact against the hull ledge
(ivp-mindist.md 13, slot 8), no triangle ledge involved. ze_crazykart_v4: one hull each, 30-158 triangles, up to
31 of them real (displacement 8, the dirt hill's top).

**The surface manager** (vtable 0x100e37a8; +4 the collide):
- 0 get_single_convex 0x1002bba0: the first hull when the hull count is 1, else null.
- 1 get_mass_center 0x1002bc00: the collide's GetMassCenter (x, y, z) -> (k x, -(k z), k y).
- 2 get_radius_and_radius_dev_to_given_center 0x1002baf0: both = |centre' - given| + GetSphereRadius x k
  (section 5).
- 3 get_rotation_inertia 0x1002af30: (1, 1, 1).
- 4 **get_all_ledges_within_radius**(center, radius, root_ledge, ..., out) 0x1002bc50: root_ledge null and a hull
  count: the hulls (at most 2: 0x1002b110); else **0x1002af50**: GetTrianglesInSphere(userData, (c.x s, c.z s,
  -(c.y s)), radius x s, &list) with s = 0x10106934 = 39.37008; none -> nothing. With 2 hulls (0x1002ac20) only
  half of the ledges belong to each: root == hull 0 takes triangles [0, n / 2), else [n / 2, n). Each listed
  triangle in range: its ledge (frame + 0x30 x index) passes when 0x1007a3e0(ledge, its first triangle, center)
  (the squared distance from the point to the triangle) <= radius^2 (section 5).
- 5 get_all_terminal_ledges 0x1002bcd0: the collide's GetAllLedges. 6 insert_all_ledges_hitting_ray 0x1002ba20.
- 7 add_reference_to_ledge 0x1002ba00: locks the frame; 8 remove_reference 0x1002ba10: unlocks. 10 get_type.

## 4. The oracle (rubikon/tests/KartOracle/Disp.cs)

engine.dll is loaded whole into the oracle (LoadLibrary: its allocator is tier0's, no engine start) and section 2's
functions are called on the BSP's lumps in the loader's order; the oracle's own IVirtualMeshEvent calls the tree's
0x101f5200 / 0x101f3360 (a thunk puts the radius in XMM2) and vphysics does the rest, section 1's object included.
The `$surfaceprop` comes from the BSP pakfile's VMT (this map: "sand" for LUFFAREN/CK_*, "dirt" for
NATURE/TRASH01A).
- a scenario's `disp <bsp>` line (after `world`): the 56 objects, named `vdisp<index>` in the `.md` (`# vdisp:`
  line: the object and its core, no compact surface).
- `KartOracle <csgo legacy> --disp <bsp> <out.bin>`: every tree as engine.dll built it ("DSP1", count, per tree:
  the 0x10c struct, the hull offset, then counted arrays: verts 12 bytes, tris 0x18, nodes 0x60, leaves 4).
- scenarios/disp-drop.txt: the kart dropped on displacement 0 and driven over it; it lands, drives and comes to
  rest on the pile (400 ticks).

## 5. The sums (read from the disassembly for the port, sim/src/ivp/vmesh.rs)

- **0x101f3360**: r2 = r x r. Per child: dx = maxps(maxps(0, min.x - c.x), c.x - max.x) (maxps a, b = a > b ? a : b),
  dy, dz alike; in when (dy^2 + dx^2) + dz^2 <= r2 (cmpleps).
- **0x1002af50**: the centre (c.x s, c.z s, -(c.y s)), the radius s x r (s = 39.37008); a listed triangle passes
  unless 0x1007a3e0's q > r^2 (comiss, ja).
- **0x1007a3e0**(ledge, its first triangle, p) -> XMM0: calc_unscaled_qr_vals_F_space of the first edge
  (minimize.rs qr_vals); no sign bit set: n = (P1 - P0) x (P2 - P0), q = (1.0 / ((ny^2 + nx^2) + nz^2)) x (((ny
  p.y + nx p.x) + nz p.z) - ((P0.y ny + nx P0.x) + P0.z nz))^2. Else min = 1e20 (0x100f4010) and the edges 2, 1, 0 (A
  its start, B the next's, k = B - A): c0 = -(((A.y - p.y) k.y + (A.x - p.x) k.x) + (A.z - p.z) k.z) + FLT_MIN, c1 =
  (((B.y - p.y) k.y + (B.x - p.x) k.x) + (B.z - p.z) k.z) + FLT_MIN; 0 > c0: q = |p - A|^2; else 0 > c1: nothing;
  else q = (1.0 / (|A - B|^2 + 1e-18)) x |(p - A) x k|^2; min = minss(q, min).
- **0x1002b260 / 0x1002b2d0 / 0x1002bc00 / 0x1002baf0**: the centre (mins + maxs) x 0.5 per axis; the sphere radius
  sqrt(((ex^2 + ey^2) + ez^2)) with e = maxs - (maxs + mins) x 0.5; the IVP mass centre (k x, -(k z), k y); the
  radius and its deviation both sqrt((dy^2 + dx^2) + dz^2) + k x the sphere radius (d = the mass centre - the
  given centre).

## 6. The port and its checks

sim/src/ivp/vmesh.rs: `Terrain` (a tree: verts, triangles, AABB nodes, leaves, bounds, the packed hull; the "ZKT1"
blob tools/kart-terrain.mjs writes from the oracle's `--disp` dump and the BSP's PHYSDISP lump), its sphere query,
the frame as a `Surface` (the triangles' ledges, then the hulls'; `Surface::mesh`), the mesh's
get_all_ledges_within_radius (collide_create.rs ledges_within / ledges_within_from dispatch on it), the collide's
mass centre / radius for create.rs (`Solid::mesh`). KartWorld::add_terrain makes the objects after the world's solids
(no game data: Game::Unknown, as the server's null pGameData).
- `vmesh_check <blob> <oracle .md>`: every vdisp ledge the oracle's run touched (hulls and triangles, words and
  points) against the port's frame: bit-identical on all three scenarios.
- `kart_world_check` with a scenario's `disp <bsp>` line (the blob at `<KART_ORACLE_DATA>/<bsp>.terrain`):
  scenarios/disp-drop.txt (a trash pile: every hull triangle virtual, 400 ticks), disp-hill.txt (the dirt hill:
  the hull's real top, the slopes, the seams between displacements and to the brushes, 1200 ticks), disp-snow.txt
  (the snow track beside its slopes, 1500 ticks): bit-identical every tick. `KWC_MDS=<n>` prints the port's
  mindists for the first n ticks.
- Found on the way (2026-11-18): IVP_Mindist_Recursive's slot 8 with no virtual feature (or over the limit) runs
  the plain do_impact 0x1008b020 (0x100b1574); the port did nothing there, so a kart fell through a hull's real
  face (ivp-mindist.md 13 corrected).

## Status

Exact (native + bit for bit): the trees (engine.dll's own build, taken through the blob), the virtual meshes, the
query, the frame and their collisions in the three scenarios.
scenarios/disp-inside.txt (the kart made inside a solid world brush and inside displacement 33's hull) is
bit-identical over 1500 ticks since the rescue push's fix (ivp-touch.md 5, BUGFIXES 2026-11-18). TODO(trace): CCoreDispInfo::Create and
CDispCollTree::Create's own math (0x101d9cc0, 0x101f1ea0, 0x101f23d0, 0x101f24f0: the blob comes from the
oracle's dump of engine.dll's trees until the bake builds them); 0x1002b440 (buildOuterHull: a map without the
PHYSDISP lump); two hulls on one displacement (ported from 0x1002af50, no map of ours has one); the frame cache's
budget (0x100bba50; an eviction only moves a frame); the ray path (slot 6); multiblend displacements (lump 63).
