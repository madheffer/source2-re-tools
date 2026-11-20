# World visibility: what a CS2 map stores per world object, and the LOD switch

Map files (`maps/<map>/worldnodes/*.vwnod_c`; de_dust2, de_inferno, de_nuke, de_ancient of 2026-07-09, ze_hold_em_p,
the skybox worlds of ze_dark_souls and ze_atix_panic); scenesystem_20261112 (disassembly; the installed 2026-11-19
build differs after CS2's 2026-11-18 update, not re-read).

## Functions (scenesystem_20261112)

| Address | What |
|---|---|
| 0x180004370 | registers sc_instanced_mesh_lod_bias |
| 0x180008460 | registers sc_screen_size_lod_scale_override |
| 0x180008030 | registers sc_force_lod_level |
| 0x180008190 | registers sc_dithered_lod_transition_amt |
| 0x1800699a8 (to 0x18006a26e) | view render attributes (rbp + 0xf0); mixes lod_bias / override / force_lod_level into the view's state key (rbp + 0x478, splitmix64-style hash, 0x1d883a29 in the high word) |
| 0x18006a1b7 | inside it: writes the two GPU LOD attributes |
| 0x18004da70 | (attrs, token, &vec4) attribute write |
| 0x1800f3b49 (to 0x1800f3e28) | view screen-size LOD scale (view + 0x3738, or the override when >= 0: `comiss xmm0, 0` at 0x1800f3c0c), kept in [rbp - 0x68]; reads cvar 0x180922ce0 and a flag at 0x1800f3bd2 |
| 0x1800fc2c0 | model mesh LOD (CPU): r8 / rsi view, rdx / rdi scene object, r9 mask byte out |
| 0x180499ed0 | largest axis scale of a 3x4: sqrt(max column squared length) |
| 0x1804afed0 | (L, p): level from pixels |
| 0x1804aff30 | the same walk filling [level, blend] (dithered transition input; unread) |
| 0x18007ccb1 | the same LOD code inlined in a debug-draw path (levels as colours, `call [r10 + 0xc0]`, packed RGBA) |
| 0x180045114, 0x18005ac7d, 0x18007b146, 0x18008ee3d, 0x1800f3e28 | other sc_force_lod_level reads |

## Fields

| Offset | Field |
|---|---|
| obj +0x10 | model (walked up +0x58 while byte +0x6e is 0xff; vtable 0x50 gives LOD data L) |
| obj +0x20 | box: +0x00 min, +0x10 max; [+0x28] + 0x30 the 3x4 transform |
| obj +0x78 | flags: & 2 = has mesh LOD |
| obj +0xa8 | parent; its signed byte +0x44b the level |
| view +0x10..+0x18 | camera position |
| view +0x28 | -1.0 = orthographic |
| view +0x38 | orthographic size |
| view +0x420 | perspective scale (presumably projection x LOD scale: untraced) |
| view +0xc8c | view height (int) |
| view +0x3738 | screen-size LOD scale |
| view vtable 0x270 | the view's forced level |
| view vtable +0xc8 | flags; bit 5 shadow view |
| L +0xb8 / +0xc0 | level count / switch thresholds (floats) |

## Constants

| Value | What |
|---|---|
| sc_instanced_mesh_lod_bias 1.25 (0x3fa00000) | reg 0x180004370, object 0x18089d268 (handle 0x18089d270) |
| sc_instanced_mesh_lod_bias_shadow | handle 0x18089d280 (by its place), loaded at 0x18006a1e6 |
| sc_screen_size_lod_scale_override -1.0 (0xbf800000) | reg 0x180008460, object 0x180922cd8 (0x180922ce0) |
| sc_force_lod_level -1 | reg 0x180008030, object 0x180922c78, handle 0x180922c80 (int +0x58) |
| sc_dithered_lod_transition_amt 0.075 (0x3d99999a) | reg 0x180008190, object 0x180922c98; range 0.2 (0x3e4ccccd at +0x57) |
| sc_allow_dithered_lod, r_texture_lod_scale | present, not followed |
| 0x180600800 | 0.5 x4 |
| 0x1805fff1c | 0.5 |
| 0x180600188 | -1.0 |
| 0x1805fff70 | 1.0 |
| 0x180600090 | 50.0 |
| 0x20913434 | attribute token: screen-size LOD scale / lod bias, splatted vec4 |
| 0x6e996b2f | attribute token: (float) view height, splatted |
| MurmurHash2(lowercase, seed 0x31415926) | attribute tokens |

## The world node (vwnod_c)

One node per map (`n0` or `node000`).

| Path | Content |
|---|---|
| `m_sceneObjects[]` | one model (`m_renderableModel`), 3x4 `m_vTransform`, `m_vTintColor`, `m_nObjectTypeFlags`, `m_vLightingOrigin`, `m_nOverlayRenderOrder`. de_dust2 138, de_inferno 438, de_nuke 364, de_ancient 99, ze_hold_em_p 0 |
| `.m_flFadeStartDistance` / `.m_flFadeEndDistance` | -1 or 0 / 0 everywhere, except 6 de_inferno objects with end 256 |
| `.m_nLODOverride` | -1 everywhere |
| `m_aggregateSceneObjects[]` | one model, many draw calls `m_aggregateMeshes[]`. de_dust2 379 / 3,472, de_inferno 346 / 6,176, de_nuke 352 / 8,239, de_ancient 273 / 4,733, ze_hold_em_p 7 / 58 |
| `m_aggregateMeshes[]` | `m_nDrawCallIndex`, `m_bHasTransform` (a row in `m_fragmentTransforms`, 12 floats), `m_vTintColor` (3 bytes), `m_objectFlags`, `m_nLightProbeVolumePrecomputedHandshake` |
| `.m_nVisClusterMemberOffset` / `.m_nVisClusterMemberCount` | 0 / 0 everywhere |
| `m_visClusterMembership` (node and aggregate) | empty everywhere: clusters must be worked out at load (untraced how) |
| `.m_nLODSetupIndex`, `.m_nLODGroupMask` | -1 / 0 on most. de_inferno 180 meshes (mask 1: 107, 2: 70, 4: 3), de_nuke 72 (24 each of 1, 2, 4), de_ancient 34 (17 each of 1, 2) |
| `m_lodSetups[]` (AggregateLODSetup_t, parsed by worldrenderer) | `m_vLODOrigin`, `m_fMaxObjectScale` (0.96 .. 1.2), `m_fSwitchDistances` (2 or 3 floats, first 0, then 8 .. 80). de_inferno 129 setups, de_nuke 24 (all 0 / 30 / 80), de_ancient 34 (all 0 / 35.446) |
| `m_clutterSceneObjects`, `m_extraVertexStreams`, `m_aggregateInstanceStreams`, `m_vertexAlbedoStreams`, `m_vertexEmissiveStreams`, `m_materialOverrides` | empty everywhere |

- A mask bit is the LOD level (1, 2, 4 = levels 0, 1, 2).
- An object's levels can sit in different aggregates (de_ancient: 17 mask 1 in one model, 17 mask 2 in another, each
  with its own setup at the same `m_vLODOrigin`); de_nuke keeps a setup's three levels in one aggregate.
- Draw-call order: each object's levels in falling triangle count.
- VRF's glTF export writes every level (de_nuke's glb 8,603 nodes = 8,239 aggregate meshes + 364 scene objects),
  named after the model per aggregate mesh (e.g. `n0_lr0_agg_prop_power_outlet_campground_1`).
- No LOD cvar in worldrenderer or engine2.
- Sizes: de_dust2's world 4,545,831 triangles, 4,096 vis clusters; ze_dark_souls 4,208,009 triangles (large clusters).

## LOD groups per map

| Map | Aggregates with LOD setups | Objects (levels falling in triangles) | Draw calls of levels 1+ | Their triangles |
|---|---|---|---|---|
| ar_baggage | 2 | 7 | 7 | 6,084 |
| ar_shoots | 2 | 34 | 34 | 5,166 |
| ar_shoots_night | 2 | 34 | 34 | 5,166 |
| cs_italy | 11 | 85 | 174 | 303,504 |
| de_ancient | 4 | 17 | 17 | 4,742 |
| de_ancient_night | 4 | 17 | 17 | 4,742 |
| de_cache | 1 | 16 | 32 | 80,160 |
| de_debris | 1 | 1 | 1 | 756 |
| de_eldorado | 14 | 242 | 243 | 178,830 |
| de_inferno | 9 | 70 | 73 | 95,378 |
| de_nuke | 2 | 24 | 48 | 16,608 |
| de_overpass | 1 | 2 | 4 | 8,754 |
| de_poseidon | 4 | 6 | 6 | 3,712 |
| de_train | 12 | 63 | 87 | 119,876 |
| warehouse_vanity | 4 | 4 | 8 | 45,308 |

785 draw calls, 878,786 triangles in all. No LOD setup: ar_pool_day, cs_office, de_anubis, de_dust2, de_dust2_vanity,
de_mirage, de_vertigo, ze_atix_panic_2017_p, ze_hold_em_p, ze_dark_souls, ze_resident_evil_3. Not read:
acknowledge_item, pet_photo_park, pet_photo_studio (world not at maps/<name>/), cs_shelter, de_boulder, de_fachwerk,
ze_crazykart_v4.

## Model mesh LOD (CPU, 0x1800fc2c0)

1. sc_force_lod_level when not -1; else the view's forced level (slot 0x270); else with a parent (+0xa8) its byte
   +0x44b; else:
2. only when `[obj + 0x78] & 2` and the model has LOD data L; otherwise level 0.
3. Sphere: `c = 0.5 x (min + max)`, `r = 0.5 x 0x180499ed0(transform)`.
4. Screen fraction s: orthographic (view +0x28 == -1.0): `s = 2r / view+0x38`, clamped [0, 1]; else
   `d² = |c - camera|²` summed `dy² + dx²`, `+ dz²` (`addss xmm4, xmm6; addss xmm4, xmm3`, xmm4 = dy², xmm6 = dx²,
   xmm3 = dz²); `s = r x view+0x420 x rsqrt(d²)` (rsqrtss, not 1 / sqrt) clamped [0, 1]; s = 1 when `r² > d²`.
5. `p = s x (float)(view +0xc8c)`.
6. 0x1804afed0: n = [L + 0xb8] (0 -> level 0); `q = 50.0 / p` (0 when p <= 0); for i = n - 1 down to 1:
   `t = [L + 0xc0][i]`; `if (t > 0 && q > t) return i`; return 0. So level i is drawn while the model covers fewer
   than 50 / t pixels of the view's height (the highest such i wins).
7. Mask byte = `1 << level`.

## World aggregates (GPU)

No CPU rule. 0x18006a1b7 writes:
- 0x20913434 = (view +0x3738, or the override when >= 0) / sc_instanced_mesh_lod_bias (the _shadow cvar when view
  flags bit 5), splatted;
- 0x6e996b2f = (float) view +0xc8c, splatted;
then the forced level as before. These are the only places in scenesystem, worldrenderer, rendersystemvulkan,
materialsystem2, engine2 or client (installed 2026-11-19) holding either token: the level is chosen in a shader. 60 of
the culling shaders' 105 attribute names occur as tokens in scenesystem; none of the 4,493 variable / Attribute names
of the 264 shaders in game/core and game/csgo shaders_vulkan_dir.vpk hashes to either token.
cull_aggregate_fragments (meshlet frustum / occlusion) and cull_instanced_meshes (size / density: g_fCullViewTanHalfFov,
g_fCullViewSizeThreshold) read neither.

## Unread

- Which function fills an object's clusters at load, and whether it uses the box or the triangles.
- View +0x420; 0x1804aff30 and the dithered transition.
- The aggregates' GPU LOD rule: the shader using 0x20913434 / 0x6e996b2f (maybe declared only in a .hlsl include),
  worldrenderer's AggregateLODSetup_t reader filling the per-draw LOD data, the pass binding the view's attributes;
  what `m_fSwitchDistances` is measured in (8 .. 80 too small for world units), `m_fMaxObjectScale`'s role.
