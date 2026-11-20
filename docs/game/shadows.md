# CS2's sun shadows: cascaded shadow maps (CSM)

Traced 2026-11-16 from scenesystem_20261015.dll, client_20261015.dll (Ghidra project, ReVa) and CS2's shaders
(shaders_vulkan_dir.vpk, `lasers-bake --shader-src csgo_environment <scratch>`: 1664 programs as GLSL through VRF's
SPIR-V reflection), CS2's FGDs (game/core/lights_base.fgd, game/csgo/csgo.fgd) and pak01's cfg/video_defaults_N.txt.
The port: web/src/world/sun-shadow-cs2.js (the numbers and the fit), sun-shadow-glsl.js (the lookup),
sun-shadows.js (the pass), wired in world/render.js and world/lighting.js.

## Where the numbers come from: the shadow quality level, not the map

CS2's csgo.fgd removes every cascade key from light_environment (`numcascades`, `shadowcascadedistance0..3`,
`shadowcascaderesolution0..3`, `cascaderenderstaticobj`, `cascadecrossfade`, `cascadedistancefade`,
`nearclipplane`: "These are controlled instead by ConVars in settings in CSGO that vary based on global shadow
settings"). de_dust2 / de_mirage / de_inferno's light_environment carry none of them (directlight 1, bakedshadowindex
0, baked_light_indexing true); ze_dark_souls' (a port) carries numcascades 3 and distances 4096 / 2048 / 1024, which
the quality level's convars override (below). The client still parses the keys (C_LightEnvironmentEntity's datamap
1801b5260: numcascades, cascaderenderstaticobj, cascadecrossfade, cascadedistancefade, shadowcascadedistance0..3,
shadowcascaderesolution0..3 -> m_nCascades, m_nCascadeRenderStaticObjects, m_flShadowCascadeCrossFade,
m_flShadowCascadeDistanceFade, m_flShadowCascadeDistance0..3, m_nShadowCascadeResolution0..3).

### The Global Shadow Quality levels (Settings > Video > Advanced: CSMQualityLevel, `videocfg_shadow_quality`)

client 180dfd3d0 builds the four level tables (KeyValues of `setting.<convar>` = value) in this order:
180df13a0 (0 Low), 180df1820 (1 Medium), 180df0f20 (2 High), 180df1ca0 (3 Very High); 180de55b0 applies a level
(the convars listed at 0x182242a90 .. 0x182242b48, 23 entries). pak01 cfg/video_defaults_0..3.txt set
videocfg_shadow_quality 0..3 and videocfg_dynamic_shadows 0 / 1 / 1 / 1.

| convar | Low | Medium | High | Very High |
|---|---|---|---|---|
| csm_max_num_cascades_override | 2 | 2 | 3 | 3 |
| csm_viewmodel_shadows | 0 | 1 | 1 | 1 |
| csm_max_shadow_dist_override | 560 | 560 | 560 | 560 |
| lb_csm_override_staticgeo_cascades | 1 | 1 | 1 | 1 |
| lb_csm_override_staticgeo_cascades_value | -1 | 1 | 2 | 2 |
| lb_csm_override_staticgeo_cascades_animated_verts | 1 | 1 | 0 | 0 |
| lb_sun_csm_size_cull_threshold_texels | 28 | 20 | 10 | 10 |
| lb_shadow_texture_width_override / height | 2560 / 2560 | 2816 / 2816 | 4352 / 5248 | 5760 / 5760 |
| lb_csm_cascade_size_override | 768 | 1024 | 1280 | 2048 |
| lb_barnlight_shadowmap_scale | 0.5 | 0.5 | 0.75 | 1.0 |
| lb_csm_draw_alpha_tested | 1 | 1 | 1 | 1 |
| lb_csm_draw_translucent | 0 | 0 | 1 | 1 |
| r_particle_cables_cast_shadows | 0 | 1 | 1 | 1 |
| lb_csm_cross_fade_override | 0.1 | 0.1 | 0.1 | 0.1 |
| lb_csm_distance_fade_override | 0.05 | 0.05 | 0.05 | 0.05 |
| lb_dynamic_shadow_resolution_base | 1536 | 1536 | 1536 | 2048 |
| lb_dynamic_shadow_resolution_base_cmp_shadowmapsize | 1 | 1 | 1 | 1 |
| sparseshadowtree_cascade_mask | 0 | 2 | 4 | 4 |
| sparseshadowtree_leaf_precision | 0.0001 | 0.0001 | 0.0001 | 0.0004 |
| sparseshadowtree_plane_max_error | 0.00004 | 0.00004 | 0.0004 | 0.0004 |
| sparseshadowtree_plane_incr_per_step | 0.00001 | 0.00001 | 0.0001 | 0.0001 |
| lb_enable_shadow_casting | 0 | 1 | 1 | 1 |
| r_particle_shadows | 0 | 0 | 0 | 1 |

So the sun's shadows reach **560 units** at every level; Low draws **no static geometry** into the cascades (the
world's static shadows are the bake's alone, players and dynamic props cast on top), Medium static geometry in
cascades 0..1, High / Very High in 0..2 (all three). `sparseshadowtree_cascade_mask` (bit per cascade) takes that
cascade's static geometry from the sparse shadow tree (SST: the static geometry's depth precomputed per map,
"static geo rendered into cascades via SST", unpacked into the atlas: CopySSTDepthToCSM_PS) instead of drawing it:
Medium's cascade 1, High's cascade 2.

### The convars' defaults (scenesystem 20261015 registrations; global = the convar object, read at + 8 -> + 0x58)

| convar | default | registration | object |
|---|---|---|---|
| csm_max_num_cascades_override | -1 (int) | 180012be0 | 180890f40 |
| csm_max_shadow_dist_override | -1.0 | 180012c90 | 180890fa0 |
| csm_max_visible_dist | 7500 | 180012d40 | 180890ff0 |
| csm_max_dist_between_caster_and_receiver | 15000 | 180012b30 | 180890f50 |
| csm_cascade0..3_override_dist | -1.0 | 1800127c0 / 870 / 920 / 9d0 | 180890e80 / f10 / f90 / f70 |
| csm_bias_override_0..3 | 1.0 (used only when <= 0) | 180012500 / 5b0 / 660 / 710 | 180890f60 / e90 / f20 / ee0 |
| csm_res_override_0..3 | 0 | 180012df0 / ea0 / f50 / 13000 | 180890fc0 / fb0 / e60 / ea0 |
| csm_viewdir_shadow_bias | 0 | 180013580 | 180890ec0 |
| csm_cascade_viewdir_shadow_bias_scale | 2.0 | 180012a80 | 180890e50 |
| csm_viewmodel_shadows | 0 | 180013840 | 180890ed0 |
| csm_viewmodel_max_shadow_dist / nearz / max_visible_dist | 21 / 0.5 / 1000 | 180013630 / 790 / 6e0 | |
| csm_sst_max_visible_dist / pushback_distance | 2000 / 1500 | 180013210 / 2c0 | 180890f80 / fe0 |
| csm_sst_shadow_focus_region_minz / maxz | -2000 / 2000 | 180013420 / 370 | |
| csm_sst_vertical_depth_shear_enable | 1 | 1800134d0 | 180890eb0 |
| csm_shadow_worldview_align_x_to_u / shear_align_z_to_v | 0 / 0 | 1800130b0 / 160 | 180890ef0 / fd0 |
| sc_shadow_slopescale_depth_bias | 2.13 (0x400851ec) | 180006d50 | 18091fa50 |
| sc_shadow_depth_bias | 256 (int; TODO(trace): the dword at the registration's default slot read as an int) | 180006ca0 | 18091fa40 |
| sc_shadow_depth_bias_clamp | 0 | 180006e00 | 18091fa60 |
| lb_csm_receiver_plane_depth_bias | 1.5e-5 (0x3780029a) | 18000fc70 | 1809239f0 |
| lb_csm_receiver_plane_depth_bias_transmissive_backface | 1.5e-4 | 18000fd20 | 180923a00 |
| lb_csm_draw_alpha_tested / draw_translucent | 1 / 1 | 18000fdd0 / fe70 | 180923a10 / a20 |
| lb_csm_cascade_size_override | -1 | 18000fbc0 | 1809239e0 |
| lb_csm_cross_fade_override / distance_fade_override | -1 / -1 | 18000ffc0 / 10070 | 180923a40 / a50 |
| lb_csm_override_staticgeo_cascades / _value / _animated_verts | 0 / -1 / 1 | 180010120 / 1d0 / 280 | 180923a60 / a70 / a80 |
| lb_sun_csm_size_cull_threshold_texels | 10 | 180010330 | 180923a90 |
| lb_csm_override_bulb_radius / fov_override | -1 / -1 | 1800103e0 / 18000ff10 | 180923aa0 / a30 |
| sparseshadowtree_cascade_mask | 4 | 18000acc0 | 180923120 |

(the type / default slots of a registration: the type code at [rsp + 0x30] .. word, the default at [rsp + 0x37];
tools: scratch cvardef.py disassembling each registration with its RIP-relative loads resolved.)

## The cascade setup (scenesystem 180496ef0, per view; called from 18008ade0 and 1801a5c00)

- The count: the light's m_nCascades (+0x3e of the light, char), capped by the view's, then
  **csm_max_num_cascades_override** when > 0 (and the view isn't flagged at bit 0 of vfn 200's >> 4), clamped 1..4.
  With csm_viewmodel_shadows one more (the viewmodel's own cascade: below).
- The splits: first the light's m_flShadowCascadeDistance0.. (+0x48, while > 0), the rest each twice the one before;
  sorted (1804945c0); then csm_cascadeN_override_dist when > 0; the valid ones counted (> 0 and increasing). The
  cascades left are computed (1804975ab .. 1804976b8):
  `near = max(0.125 (1805ffeb8), view + 0x20)`, `far = min(view + 0x24, attribute 0x7b2a64e1 (default 1000.0) or
  csm_max_shadow_dist_override when > 0)`; for cascade k (0-based) of n:
  `lin = (far - near) (k + 1) / n + near`, `log = near (far / near)^((k + 1) / n)` (V_powf), `split = (log - lin) x 0.85
  (180587c44) + lin + 0.1 (1805ffeb4)`, never below the one before. The view's +0x20 / +0x24 are read as the camera's
  near / far (TODO(trace): the view struct's fields are not named). Then per-cascade attributes (hashes at 1805ab770 /
  780 / 790 and 0x410b9880 for the fourth) may replace a split (the view's attribute list; nothing sets them in play
  as far as read).
  With CS2's camera near 6.5 and 560 units, three cascades: **53.2, 164.2, 560.1**; two: 93.9, 560.1.
- Per cascade a texture matrix (local_1e78): `[0.5, 0, 0, 0.5 + 0.5 / res; 0, -0.5, 0, 0.5 + 0.5 / res; 0, 0, 1,
  bias_k]`, bias_k = **-5e-6, -5e-6, -8e-6, -9e-5** (18066c530; the same at 18066c520 for view type 0x2d), each
  replaced by csm_bias_override_k when that is <= 0.
- The atlas rects (param_1 + 0x5f8 ..): one cascade: scale res0 / A; two: side by side (offsets 0 / 0.5 in u, scale
  x 0.5 in u); three or four: a 2 x 2 grid (offsets 0 / 0.5 each way, scale x 0.5). A = the atlas size
  (param_3[0xb]).
- 180494b40 fits the cascades (below) with: near, the splits, csm_max_visible_dist (attribute 0xb506b94b; the SST
  view: csm_sst_max_visible_dist), csm_max_dist_between_caster_and_receiver (attribute 0xb7a3d0d5; SST:
  csm_sst_pushback_distance).
- Per cascade, at the end: the view-direction bias `(k x csm_cascade_viewdir_shadow_bias_scale + 1) x
  csm_viewdir_shadow_bias` (0 by default), the cascade's depth span.
- At the end: param_1[0x5ac..] = 1 / atlas w, h and their halves; 0x5b2 = 0.35, 0x5b3 = 6.6667 (TODO: their
  consumer); 0x5b4 = D x 0.95 and 0x5b5 = 1 / (D - 0.95 D) with D = param_1[0x6a1] = 1.42 x the whole range's
  diameter (180494b40's param_5) (TODO(trace): their consumer: not the shader's distance fade, which 1801af7b0 packs).

## The fit (scenesystem 180494b40)

- The light's view (180156120 from the light's direction; 180156530 with csm_shadow_worldview_align_x_to_u);
  with csm_sst_vertical_depth_shear_enable and a steep sun (dir.z > 0.6) the SST view is sheared (not ported: SST).
- The whole range: 1804969e0(near, last split) -> its diameter D0; param_5 = 1.42 D0; the extrusion
  `E = max(1.42 D0, max(csm_max_visible_dist, last split, csm_max_dist_between_caster_and_receiver))` (15000 in play).
- Per cascade k (stopped when k > 0 and the cascade's near > csm_max_visible_dist):
  - **1804969e0(d0, d1)**: the 8 corners of the view frustum between planar depths d0 and d1 (1804a8770 twice, the
    view's tangents at + 0x5c .. 0x5f), the largest distance between two corners W (the cascade's width: the same for
    any view rotation, so the cascade's size never changes as the view turns), the corners moved to world space;
  - the corners in light space: x / y min and max, depth min and max; again with each corner pushed E along the
    light direction (the casters toward the sun); a later cascade's far depth at least the one before's (local_7d8);
  - **the texel snap** (18049520x): `pad = (W - (max - min)) x 0.5` per axis, `texel = W / res`,
    `left = floor((min - pad) / texel) x texel`, `right = floor((max + pad) / texel) x texel` (both floored), the same
    for y; depth `near = floor(0) = 0`, `far = ceil(zmax - zmin)`; the light view translated by -zmin;
    180498af0 builds the orthographic projection from (right, top, left, bottom, near, far);
  - the cascade's culling: up to 12 planes from 180495df0 (the view's region seen from the light), plus, from the
    second cascade on, the **previous cascade's box shrunk 15 % a side** (0.15) as 6 exclude planes (lVar16 + 0x174:
    a caster inside it is the higher-resolution cascade's alone; exact, since the shader picks the first cascade that
    holds a point and the cross fade is 10 % at most).

## The lookup (csgo_environment's pixel shader; every combo has it)

`PerViewLightingConstantBufferGpu_t` (lightmapped combos, s0_d3): m9 the sun's direction (toward it), m10 its colour,
m10 / m11 the baked shadow channel mask (by combo), **m11 the cascade count, m12 the receiver bias, m13[k] the cascade's
NDC limit, m14 / m15 the cross fade, m16 / m17 the distance fade, m18[k] the cascade's world -> (NDC xy, depth z)
matrix, m19[k] its atlas rect (offset xy, scale zw), m20 the atlas (bindless)**:

```
if (dot(sunDir, N) > (snow ? -0.25 : 0) && bakedVis > 0) {          // bakedVis = 1 - dot(direct_light_shadows, mask)
  k = first cascade with max(|c.x|, |c.y|) < m13[k], c = vec4(p, 1) x m18[k]
  w = sat(f.x f.y), f = 1 - sat(|c.xy| x m15 + m14)                   // the cross fade
  a = tap(k, c)  (b = tap(k + 1) when w < 1 and k < n - 1, else 1;  a = mix(b, a, w))
  tap: textureLod(sampler2DShadow(atlas, g_tShadowDepthBufferCmpSampler), (c.xy x m19.zw + m19.xy, sat(c.z + m12)))
  v = mix(a, 1, sat(distance(p, eye) x m17 + m16))                    // the distance fade
  if (PerViewConstantBufferCsgo_t m0.y) v = min(v, g_tParticleShadowBuffer(screen uv).z)
}
sun = m10 x v x bakedVis (x N.L, the BRDF)
```

So **on lightmapped geometry CS2 multiplies the cascades by the baked shadow mask** (`_24154 = _11313 x _14808`):
the static world is shadowed by both (the realtime shadow is the sharper one near the eye; past the cascades' 560
units the bake alone). Non-lightmapped combos (probe / vertex-stream lit) take the cascades x their own baked sun
visibility the same way. One hardware comparison tap: the sampler's linear filter is a 2 x 2 PCF (no wider kernel
for the sun; the barn lights' taps in the same shader are their own).

The constants (scenesystem 1801af7b0, the per-view lighting constants, from 1801b02dc):
- m12 = lb_csm_receiver_plane_depth_bias (and lb_csm_receiver_plane_depth_bias_transmissive_backface beside it),
  both negated when the global at 180922570 is 0 (read as: depth not reversed);
- the cross fade c = lb_csm_cross_fade_override if > 0, else the light's (+0xebf0); the distance fade d =
  lb_csm_distance_fade_override if > 0, else the light's (+0xebf4); each clamped 0.001 .. 0.5;
  m14 = -(1 - c) / c, m15 = 1 / c, m17 = 1 / (D d), m16 = -((1 - d) D) / (D d), D = + 0xebec (TODO(trace): its writer;
  the port takes the last split, 560.1);
- m13: not located (TODO(trace)); 1.0 in the port.

The smoke (smoke_volume_cs, docs/game/smoke.md) uses the same factor at `lerp(1, x, 0.75)` on its sun term.

## Casters

- Static objects (the world, static props) into cascades <= lb_csm_override_staticgeo_cascades_value (per level);
  with `_animated_verts` 1 (Low / Medium) only objects without SCENEOBJECTFLAG_CAN_RENDER_INTO_SST count as static
  (TODO(trace): the flag's meaning beyond the convar's help text). The SST cascades (mask) take static geometry from
  the precomputed tree.
- Dynamic objects (players, dynamic props, weapons, grenades) into every cascade.
- Objects under lb_sun_csm_size_cull_threshold_texels texels in a cascade are culled (TODO(trace): the measure).
- Alpha-tested materials cast (lb_csm_draw_alpha_tested 1); translucent at High and up; materials with
  F_DO_NOT_CAST_SHADOWS never (csgo_environment's feature "Shadows" -> BoolAttribute DoNotCastShadows).
  An alpha-tested caster is cut out by its alpha in the depth pass too (the crane jib's lattice shadow on de_vertigo
  in CS2's picture and its baked mask). The port (2026-11-20): the generated ports' S_ALPHA_TEST programs test
  texture(g_tColor, the uv through g_vTexCoordXform0 / 1).w against the material's alphaTest, and the depth variant
  samples the same (web/src/world/cs2mat/alpha-cast.js). Before, a generated material had no three `map` and cast as a
  solid sheet. The depth variant shares the cs2mat texture, so anything that walks the casters' materials reaches it:
  tex-filter.js skips cs2mat textures (a filter change re-uploads mips cs2mat has freed; BUGFIXES). TODO(trace): CS2's own depth-only combo for F_ALPHA_TEST (its reference and texcoord scroll); the
  environment shaders' blended alpha (still opaque in the cascades).
- Particles: r_particle_shadows (Very High) renders g_tParticleShadowBuffer (screen space, min'd in the lookup);
  cables with r_particle_cables_cast_shadows. Not ported.
- Raster bias: sc_shadow_slopescale_depth_bias 2.13, sc_shadow_depth_bias 256, clamp 0 (the shadow depth render
  state 18018a470, sc_shadow_depth_bias_state_override 0).

## The port (web/src/world/sun-*.js)

- Ported 1:1: the four quality levels' cascade count, distance, resolution, static-geometry cascades, size cull,
  alpha-tested / translucent casters, cross and distance fades; the split scheme; the fit (corners, diameter width,
  texel snap with both edges floored, depth from the casters 15000 units toward the sun, the far depth carried); the
  exclude-the-previous-inner-box cull; the atlas layout; the per-cascade texture bias and the receiver bias; one
  hardware 2 x 2 comparison tap, the cross fade into the next cascade, the distance fade; the product with the baked
  mask on lightmapped geometry and with the probe visibility on probe-lit models.
- Stand-ins (labelled in the code):
  - the light view's roll (180156120's choice of axes): world up projected;
  - m13 = 1, D = the last split; the half-texel term folded into the rect (m19's packer unread);
  - the static world (every cascade that takes it, not only the SST's) comes from world/sun-shadow-cache.js: per
    cascade a depth map of the static world twice the cascade's size each way on the cascade's own texel grid (the same
    light basis and texel W / res, its origin a whole number of texels: both box edges are floored and the box is
    exactly W wide, so every texel the cascade samples is a cache texel), redrawn only when the cascade's box leaves
    it, copied into the tile each frame with the depth remapped to the cascade's range, the dynamic casters drawn over
    it. Checked texel by texel against drawing the static world directly (client/dev/prof-shadows.js cacheCheck, a
    still view, ze_hold_em_p and ze_dark_souls, every level): equal to 2e-6, except texels of big triangles that reach
    the far plane, deeper by one constant-bias step (256 x 2^-24 = 1.5e-5 of depth, ~0.2 u): a float depth buffer's
    constant bias takes the primitive's largest depth's exponent, which the copy (adding the bias per texel) can't know.
    (This is CS2's own arrangement: sparseshadowtree_cascade_mask's cascades unpack precomputed static depth.)
  - casters three never drew (static meshes the PVS hid from the start, models never in view) are put through three's
    own render once first: renderBufferDirect assumes their buffers are uploaded (their attributes otherwise read as
    zeros: an instanced mesh hidden from the start wrote depth 0 over whole tiles on ze_dark_souls);
  - the size cull by the bounding sphere's diameter; the caster bounds of skinned meshes are their bind-pose spheres
    padded;
  - the atlas depth format (32-bit float), which sets what sc_shadow_depth_bias's unit is;
  - which materials skip casting: F_DO_NOT_CAST_SHADOWS when the bake keeps it, else see-through ones without depth
    writes or with additive blending;
  - the viewmodel's cascade (csm_viewmodel_shadows) and the particle shadow buffer (Very High): not built; your own
    first-person body does not cast (CS2 draws a shadow-only body for the local player: TODO(trace)).

## Unread

- 180156120 / 180156530 (the light view's basis), 180495df0's planes, 1804a8770's exact corner construction (planar
  depth assumed), 1801af7b0's m13 and 0xebec writer, 180922570's meaning, the SST build and unpack
  (sparseshadowtree_*), the viewmodel cascade's fit (csm_viewmodel_*), the transmissive backface bias' use, how the
  view's near / far reach 180496ef0's param_3 + 0x18.
