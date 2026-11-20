# World visibility: what a CS2 map stores per world object, and what our culling does with it

Read 2026-11-18 from the maps' own files (`lasers-bake --world-nodes <map.vpk> [world]`, bake/WorldNodeBake.cs: every
key path of every `maps/<map>/worldnodes/*.vwnod_c` with counts, types, ranges and distinct values) and measured over
the baked folders (`node tools/vis-census.mjs <map folder>`). No binary was read for this note: how the engine uses
these fields is marked untraced below.

## 1. A world node (vwnod_c), as compiled today

Maps read: de_dust2, de_inferno, de_nuke, de_ancient (CS2's own, game/csgo/maps, files of 2026-07-09), ze_hold_em_p,
and the skybox worlds of ze_dark_souls and ze_atix_panic (the tool took the first map vpk of a workshop item: pass the
world's name for the main one). Every map has one node (`n0` or `node000`).

| Path | What the files hold |
|---|---|
| `m_sceneObjects[]` | One model each (`m_renderableModel`), a 3x4 `m_vTransform`, `m_vTintColor`, `m_nObjectTypeFlags`, `m_vLightingOrigin`, `m_nOverlayRenderOrder`. de_dust2 138, de_inferno 438, de_nuke 364, de_ancient 99, ze_hold_em_p 0 |
| `m_sceneObjects[].m_flFadeStartDistance` / `m_flFadeEndDistance` | -1 or 0 / 0 on every object of every map read, except 6 objects of de_inferno with an end of 256. No map-wide prop fading is compiled in |
| `m_sceneObjects[].m_nLODOverride` | -1 everywhere |
| `m_aggregateSceneObjects[]` | One model each, drawn as many draw calls: `m_aggregateMeshes[]`. de_dust2 379 aggregates / 3,472 meshes, de_inferno 346 / 6,176, de_nuke 352 / 8,239, de_ancient 273 / 4,733, ze_hold_em_p 7 / 58 |
| `m_aggregateMeshes[].m_nDrawCallIndex`, `m_bHasTransform`, `m_vTintColor` (3 bytes), `m_objectFlags`, `m_nLightProbeVolumePrecomputedHandshake` | The draw call of the model it draws, whether it has a row in `m_fragmentTransforms` (12 floats each), its tint |
| `m_aggregateMeshes[].m_nVisClusterMemberOffset` / `m_nVisClusterMemberCount` | **0 / 0 on every mesh of every map read** |
| `m_visClusterMembership` (the node's and each aggregate's) | **Empty on every map read** |
| `m_aggregateMeshes[].m_nLODSetupIndex`, `m_nLODGroupMask` | -1 / 0 on most. With a setup: de_inferno 180 meshes (masks 1: 107, 2: 70, 4: 3), de_nuke 72 (24 each of 1, 2, 4), de_ancient 34 (17 each of 1, 2); de_dust2 and the ZE maps none |
| `m_aggregateSceneObjects[].m_lodSetups[]` | `m_vLODOrigin` (3 floats), `m_fMaxObjectScale` (0.96 .. 1.2), `m_fSwitchDistances` (2 or 3 floats: the first always 0, then 8 .. 80). de_inferno 129 setups, de_nuke 24 (all 0 / 30 / 80), de_ancient 34 (all 0 / 35.446) |
| `m_clutterSceneObjects`, `m_extraVertexStreams`, `m_aggregateInstanceStreams`, `m_vertexAlbedoStreams`, `m_vertexEmissiveStreams`, `m_materialOverrides` | Empty on every map read |

What follows from the files alone:

- **No per-object cluster list is compiled.** The membership arrays exist in the format and are empty, so the engine
  must work each object's clusters out at load from its bounds and world_visibility's voxel tree. Our cells (below)
  do the same from the baked meshes. Untraced: the function that fills it and whether it uses the object's box or
  its triangles.
- **LOD groups exist on CS2's own maps** (de_inferno 180 draw calls, de_nuke 72, de_ancient 34). A mask's bit says
  which LOD level the draw call belongs to (1, 2, 4 = levels 0, 1, 2 by the counts: nuke has 24 of each for 24
  three-distance setups). Untraced: what `m_fSwitchDistances` is measured in (30 and 80 are not world units for a
  prop that switches across a map; a screen-size metric with `m_fMaxObjectScale` is likely). **VRF's glTF export
  writes every level**: de_nuke's world glb has 8,603 nodes = its 8,239 aggregate meshes + 364 scene objects, so the
  48 draw calls of levels 1 and 2 are in it and we drew them on top of level 0 (de_inferno 73, de_ancient 17). A
  bug of ours, closed as a stand-in on 2026-11-19 (section 3): the cut leaves the higher levels out. The pick
  between levels still needs scenesystem's rule traced.
- **Fade distances are not in use** on the maps read: nothing to port for them.

## 2. Our culling (ours, not CS2's code)

bake/VisBake.cs rasterises the clusters' boxes (VRF `BuildClusterChildBounds`) into cells and ships each cell's
clusters and every cluster's PVS row (vis.bin, web/src/lib/vis-table.js). tools/chunk-vis.mjs tags every world mesh
with the clusters of the cells its triangles touch; web/src/world/vis.js draws a mesh when one of its clusters is in
the union of the rows of the camera cell's clusters. A cell names a superset of a point's cluster, so nothing CS2
would draw is hidden; the bake checks that rule on every map it bakes (200,000 seeded points inside the clusters'
boxes, each asked of VRF's voxel tree: one point whose cluster its cell does not name fails the bake).

### The cell size (measured 2026-11-18)

`tools/vis-census.mjs`: over 400 camera cells picked at random (seeded), the share of the map's triangles drawn after
the PVS, and the draw calls drawn.

The census picks its camera cells from the table it is given, so a row of this table is sampled on its own grid (a
256 table weighs thin shells of clusters more than a 64 one): read it for the trend. The fair pair, the old folder
against the new one from the same 2,000 points (`tools/vis-compare.mjs`): de_dust2 70.4 % -> 57.8 % of triangles,
1,251 -> 998 draw calls drawn; over the 27 folders re-tagged on 2026-11-18, 78.8 % -> 70.0 % on average (every map
less on average; de_boulder, de_overpass, ze_resident_evil_3, de_debris and cs_shelter draw more than before from
some points: their old chunks came from an older cutter and the re-cut regrouped them).

| de_dust2 (4,545,831 triangles, 4,096 clusters) | Triangles drawn, mean | Draw calls drawn, mean | vis.bin |
|---|---|---|---|
| 256-unit cells (as shipped until now) | 69.8 % | 1,236 of 1,914 | 726 KB |
| 128 | 63.2 % | 1,095 | 776 KB |
| **64** | **57.4 %** | **983** | 855 KB |
| 32 | 56.2 % | 961 | 932 KB |
| 64, every triangle tagged on its own (the bound for any regrouping) | 43.3 % | | |

ze_dark_souls (4,208,009 triangles; its clusters are large): 4.7 % at 256, 4.7 % at 128, 4.5 % at 64, and 64 would be
10 million cells. So the cell is picked per map: the finest of 64 / 128 / 256 that keeps the map under 500,000 cells
(VisBake `Sizes`, `AutoCells`; `--cell <n>` forces one).

### Cutting the meshes smaller does not pay

The same census with every primitive cut again by the sub-cell of its triangles' centres (de_dust2, 64-unit cells):

| Cut | Draw calls | Drawn, mean | Triangles drawn, mean |
|---|---|---|---|
| as joined now (material, 1,024 sub-cell of the primitive's centre) | 1,914 | 983 | 57.4 % |
| by 1,024 per triangle | 3,784 | 1,855 | 50.8 % |
| by 512 | 5,748 | 2,804 | 49.3 % |
| by 256 | 10,210 | 4,892 | 47.8 % |

Twice the draw calls for 7 points of triangles; on ze_dark_souls nothing at all (4.4 % -> 4.2 % for 5 times the draw
calls). Not done. What could still reach the 43 % bound without more draw calls is grouping triangles by which
clusters see them instead of by where they are: open.

### A baked folder goes stale under a workshop update

ze_dark_souls' vpk changed on 2026-11-18; the folder is from 2026-11-09. Its visibility baked from today's vpk is not
the folder's vis.bin, so new tags on the old meshes would name other clusters. tools/vis-recut.mjs refuses such a
map (the visibility baked at the folder's own cell must equal its vis.bin byte for byte): it needs a full rebake.

## 3. The LOD levels in the bake (2026-11-19)

`lasers-bake --world-lods <vpk> <map dir>` (bake/WorldLodBake.cs; a part of the `chunks` step) writes
`world/lods.json`: per aggregate with a LOD setup, its `m_lodSetups` (origin, max object scale, switch distances)
and, per `m_aggregateMeshes` entry in the file's order, `[m_nLODSetupIndex, m_nLODGroupMask]`.
tools/chunk-lod.mjs matches an aggregate to the world glb's nodes (VRF names every node of an aggregate after its
model, e.g. `n0_lr0_agg_prop_power_outlet_campground_1`, one per aggregate mesh, in that order) and the cut
(tools/chunk-world.mjs) leaves out the draw calls whose mask has no level 0.

**STAND-IN: level 0 at every distance.** The pick between levels is scenesystem's and untraced (what
`m_fSwitchDistances` is measured in, `m_fMaxObjectScale`); once read, the levels are cut apart and switched in
the client instead of dropped.

Read from the files on the way:

- **An object's levels can sit in different aggregates.** de_ancient's 34 tagged draw calls are 17 with mask 1 in
  one model and 17 with mask 2 in another, each with a setup of its own at the same `m_vLODOrigin`: the origin is
  the object, not the setup's index. (de_nuke keeps a setup's three levels in one aggregate.)
- **The node order is the draw calls' order**: over every map re-cut, each object's levels come out in falling
  triangle counts (the check the cut makes before it drops anything; a map failing it is not cut).
- More maps have LOD groups than the five read before: the table.

| Map | Aggregates with LOD setups | Objects whose levels fall in triangle count | Draw calls left out | Triangles left out | Chunk triangles before -> after |
|---|---|---|---|---|---|
| ar_baggage | 2 | 7 of 7 | 7 | 6,084 | 1,824,573 -> 1,818,489 |
| ar_shoots | 2 | 34 of 34 | 34 | 5,166 | 4,489,281 -> 4,484,115 |
| ar_shoots_night | 2 | 34 of 34 | 34 | 5,166 | 4,545,897 -> 4,540,731 |
| cs_italy | 11 | 85 of 85 | 174 | 303,504 | 5,912,390 -> 5,608,886 |
| de_ancient | 4 | 17 of 17 | 17 | 4,742 | 9,189,465 -> 9,184,723 |
| de_ancient_night | 4 | 17 of 17 | 17 | 4,742 | 9,349,421 -> 9,344,679 |
| de_cache | 1 | 16 of 16 | 32 | 80,160 | 2,874,343 -> 2,794,183 |
| de_debris | 1 | 1 of 1 | 1 | 756 | 2,477,631 -> 2,476,875 |
| de_eldorado | 14 | 242 of 242 | 243 | 178,830 | 7,322,158 -> 7,143,328 |
| de_inferno | 9 | 70 of 70 | 73 | 95,378 | 8,419,800 -> 8,324,422 |
| de_nuke | 2 | 24 of 24 | 48 | 16,608 | 2,777,530 -> 2,775,454 |
| de_overpass | 1 | 2 of 2 | 4 | 8,754 | 3,851,499 -> 3,842,745 |
| de_poseidon | 4 | 6 of 6 | 6 | 3,712 | 2,046,834 -> 2,043,122 |
| de_train | 12 | 63 of 63 | 87 | 119,876 | 7,681,407 -> 7,562,779 |
| warehouse_vanity | 4 | 4 of 4 | 8 | 45,308 | 1,844,125 -> 1,798,817 |

785 draw calls, 878,786 triangles in all (tools/lod-recut.mjs: the chunks only, in scratch, then copied
in; the old ones kept in a local backup). No LOD setup: ar_pool_day, cs_office, de_anubis, de_dust2, de_dust2_vanity, de_mirage, de_vertigo, ze_atix_panic_2017_p, ze_hold_em_p, ze_dark_souls, ze_resident_evil_3. Not re-cut: acknowledge_item, pet_photo_park and pet_photo_studio (their worlds are not at maps/<name>/ in their vpk: the tool does not find them); cs_shelter (no source vpk); de_boulder (no source vpk); de_fachwerk (no source vpk); ze_crazykart_v4 (no source vpk).

## 4. CS2's LOD switch: what is read (2026-11-19, scenesystem_20261112.dll, capstone: ReVa was down)

Read with tools/re/game/xref.py / riprefs.py / disasm.py on source2-compiler's archived
`tools/re/binaries/scenesystem_20261112.dll` (the installed scenesystem.dll of 2026-11-19 differs from it: CS2's
2026-11-18 update; not re-read).

- worldrenderer.dll parses the setup (`AggregateLODSetup_t`: m_vLODOrigin, m_fMaxObjectScale, m_fSwitchDistances;
  m_nLODSetupIndex / m_nLODGroupMask on m_aggregateMeshes). No LOD cvar in worldrenderer or engine2.
- scenesystem's LOD cvars, registration function, object (the cvar handle is the object + 8), default:

| cvar | registration | object | default |
|---|---|---|---|
| sc_instanced_mesh_lod_bias | 0x180004370 | 0x18089d268 | 1.25 (0x3fa00000) |
| sc_screen_size_lod_scale_override | 0x180008460 | 0x180922cd8 | -1.0 (0xbf800000) |
| sc_force_lod_level | 0x180008030 | 0x180922c78 | -1 |
| sc_dithered_lod_transition_amt | 0x180008190 | 0x180922c98 | 0.075 (0x3d99999a; a range in the registration: 0.2 = 0x3e4ccccd at +0x57) |

  Also present: sc_allow_dithered_lod, sc_instanced_mesh_lod_bias_shadow, r_texture_lod_scale (not followed).
- 0x1800699a8 (to 0x18006a26e) reads all three of lod_bias / screen_size override / force_lod_level only to mix them
  into the view's state key (rbp + 0x478, a splitmix64-style hash with 0x1d883a29 in the high word): not the rule.
- 0x1800f3b49 (to 0x1800f3e28): the view's screen-size LOD scale is the float at view + 0x3738 (rsi = the view),
  replaced by sc_screen_size_lod_scale_override when that is >= 0 (`comiss xmm0, 0` at 0x1800f3c0c), kept in
  [rbp - 0x68]; the same function reads cvar 0x180922ce0 (the override) and a flag at 0x1800f3bd2.
- sc_force_lod_level (handle 0x180922c80) is read in 0x180045114, 0x18005ac7d, 0x18007b146, 0x18007ccb1,
  0x18008ee3d, 0x1800f3e28, 0x1800fc2c0: the per-object level choice is among these. **Unread**: the formula (how
  |camera - m_vLODOrigin|, m_fMaxObjectScale, the screen-size scale and m_fSwitchDistances give a level; the switch
  distances 8 .. 80 are too small to be world units against the camera distance alone), the dithered transition.
  Read on 2026-11-19 ("mapbake-done"): section 5.

## 5. CS2's LOD switch, read (2026-11-19 "mapbake-done", scenesystem_20261112.dll, capstone: tools/re/game/disasm.py)

Two paths, by what is drawn.

**A model's mesh LOD (CPU): 0x1800fc2c0** (r8 / rsi = the view, rdx / rdi = the scene object, r9 = the mask byte out).

1. sc_force_lod_level (cvar handle 0x180922c80, its int at +0x58) when not -1; else the view's own forced level
   (vtable slot 0x270 on the view); else, when the object has a parent at +0xa8, its signed byte +0x44b; else:
2. only when `[obj + 0x78] & 2` and the object's model (`[obj + 0x10]`, walked up `[+0x58]` while its byte
   +0x6e is 0xff; vtable slot 0x50 gives the LOD data `L`); otherwise level 0;
3. the sphere: centre c = 0.5 x (box min + box max) (`[obj + 0x20]` -> +0x00 / +0x10; the constant 0.5 x4 at
   0x180600800), radius r = 0.5 (0x1805fff1c) x 0x180499ed0(the 3x4 at `[[obj + 0x20] + 0x28] + 0x30`):
   sqrt(max over the three columns of the column's squared length), the matrix's largest axis scale;
4. the screen fraction s: when the view's float +0x28 is -1.0 (0x180600188: an orthographic view) s = 2r / view
   +0x38, clamped [0, 1]; else d² = |c - view +0x10..+0x18|², s = r x view +0x420 x rsqrt(d²) clamped [0, 1]
   (1.0 at 0x1805fff70), and s = 1 when r² > d² (the camera inside the sphere). Sum order: dy² + dx², + dz²
   (`addss xmm4, xmm6; addss xmm4, xmm3` with xmm4 = dy², xmm6 = dx², xmm3 = dz²); rsqrtss, not 1 / sqrt;
5. pixels p = s x (float)(int at view +0xc8c) (the view's height: the same int goes to the shaders as 0x6e996b2f below);
6. **0x1804afed0(L, p)**: n = `[L + 0xb8]` levels (0 -> level 0); q = 50.0 (0x180600090) / p (0 when p <= 0);
   for i = n - 1 down to 1: t = `[L + 0xc0]`[i] (floats); `if (t > 0 && q > t) return i`; return 0. So level i
   is drawn while the model covers fewer than 50 / t pixels of the view's height (the highest such i wins).
7. the mask byte = 1 << level.

0x18007ccb1 is the same code inlined in a debug-draw path (the levels as colours: `call [r10 + 0xc0]` with packed
RGBA), not another rule. Unread: what view +0x420 is (the projection's scale x the LOD scale, presumably: not traced),
0x1804aff30 (the same walk filling a [level, blend] pair: the dithered transition's input).

**World aggregates (GPU): no CPU rule.** 0x18006a1b7 (inside 0x1800699a8, the view's render attributes, rbp + 0xf0)
writes two attributes through 0x18004da70(attrs, token, &vec4):
- token **0x20913434** = (the view's screen-size LOD scale, view +0x3738, or sc_screen_size_lod_scale_override when
  >= 0) / sc_instanced_mesh_lod_bias (handle 0x18089d270; the handle 0x18089d280, sc_instanced_mesh_lod_bias_shadow by its place, loaded at
  0x18006a1e6, when bit 5 of the view's flags, vtable +0xc8, is set: a shadow view), splatted to a vec4;
- token **0x6e996b2f** = (float) view +0xc8c, the view's height, splatted;
then sc_force_lod_level / the view's forced level (slot 0x270) as before. These are the only two places any of
scenesystem, worldrenderer, rendersystemvulkan, materialsystem2, engine2 or client (installed 2026-11-19) hold either
token, so the level is chosen in a shader. Not found which: the tokens are MurmurHash2(lowercase name, seed
0x31415926) (checked: 60 of the culling shaders' 105 attribute names occur as tokens in scenesystem), and none of the
4,493 variable names / Attribute strings of the 264 shaders in game/core and game/csgo's shaders_vulkan_dir.vpk
(`lasers-bake --shader-names <out> --cs2 <game folder>`, new) hashes to either. cull_aggregate_fragments (meshlet
frustum / occlusion culling) and cull_instanced_meshes (size and density culling: g_fCullViewTanHalfFov,
g_fCullViewSizeThreshold) read neither. Next: the CPU side that fills the aggregate's per-draw LOD data
(worldrenderer's AggregateLODSetup_t reader: m_vLODOrigin, m_fMaxObjectScale, m_fSwitchDistances) and which pass
binds the view's attributes; a name list from a shader source (the attribute may be declared only in a .hlsl
include). Until then our world keeps level 0 everywhere (the STAND-IN of section 3).
