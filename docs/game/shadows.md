# Sun shadows: cascaded shadow maps (CSM)

scenesystem_20261015, client_20261015, csgo_environment shaders (shaders_vulkan_dir.vpk, GLSL via VRF's SPIR-V
reflection), game/core/lights_base.fgd, game/csgo/csgo.fgd, pak01 cfg/video_defaults_N.txt.

## Functions

| Address | Module | What |
|---|---|---|
| 1801b5260 | client | C_LightEnvironmentEntity's datamap (parses the cascade keys) |
| 180dfd3d0 | client | builds the four shadow quality level tables (KeyValues `setting.<convar>` = value) |
| 180df13a0 / 180df1820 / 180df0f20 / 180df1ca0 | client | level 0 Low / 1 Medium / 2 High / 3 Very High (built in this order) |
| 180de55b0 | client | applies a level (convars listed at 0x182242a90 .. 0x182242b48, 23 entries) |
| 180496ef0 | scenesystem | cascade setup, per view (called from 18008ade0 and 1801a5c00) |
| 1804945c0 | scenesystem | sorts the splits |
| 1804975ab .. 1804976b8 | scenesystem | the computed splits |
| 180494b40 | scenesystem | fits the cascades |
| 180156120 | scenesystem | light view from the light's direction |
| 180156530 | scenesystem | light view with csm_shadow_worldview_align_x_to_u |
| 1804969e0 | scenesystem | (d0, d1): frustum corners and width W |
| 1804a8770 | scenesystem | a frustum corner set (called twice; the view's tangents at + 0x5c .. 0x5f) |
| 18049520x | scenesystem | the texel snap |
| 180498af0 | scenesystem | orthographic projection (right, top, left, bottom, near, far) |
| 180495df0 | scenesystem | up to 12 culling planes (the view's region seen from the light) |
| 1801af7b0 | scenesystem | per-view lighting constants (from 1801b02dc): packs the fades |
| 18018a470 | scenesystem | shadow depth render state |

## Fields

| Offset | Field |
|---|---|
| light +0x3e (char) | m_nCascades |
| light +0x48 .. | m_flShadowCascadeDistance0.. |
| light +0xebf0 / +0xebf4 | cross fade / distance fade |
| + 0xebec | D in the distance fade (writer unread) |
| view +0x20 / +0x24 | read as the camera's near / far (unnamed) |
| view + 0x5c .. 0x5f | the view's tangents |
| param_1 + 0x5f8 .. | atlas rects |
| param_3[0xb] | atlas size A |
| param_1[0x5ac..] | 1 / atlas w, h and their halves |
| param_1[0x5b2] / [0x5b3] | 0.35 / 6.6667 (consumer unread) |
| param_1[0x5b4] / [0x5b5] | D x 0.95 / 1 / (D - 0.95 D), D = param_1[0x6a1] = 1.42 x the whole range's diameter (180494b40's param_5; consumer unread: not the shader's distance fade) |
| lVar16 + 0x174 | the exclude planes |
| local_1e78 | per-cascade texture matrix |
| local_7d8 | carried far depth |

Keys parsed by the client: numcascades, cascaderenderstaticobj, cascadecrossfade, cascadedistancefade,
shadowcascadedistance0..3, shadowcascaderesolution0..3 -> m_nCascades, m_nCascadeRenderStaticObjects,
m_flShadowCascadeCrossFade, m_flShadowCascadeDistanceFade, m_flShadowCascadeDistance0..3, m_nShadowCascadeResolution0..3.
csgo.fgd removes them from light_environment (with `nearclipplane`: "These are controlled instead by ConVars in
settings in CSGO that vary based on global shadow settings"). de_dust2 / de_mirage / de_inferno's light_environment
carry none (directlight 1, bakedshadowindex 0, baked_light_indexing true); ze_dark_souls' carries numcascades 3 and
4096 / 2048 / 1024, overridden by the level's convars.

## Constants

| Value | What |
|---|---|
| 0.125 (1805ffeb8) | min near |
| 0.85 (180587c44) | log / lin split blend |
| 0.1 (1805ffeb4) | split offset |
| attribute 0x7b2a64e1 (default 1000.0) | shadow far |
| hashes 1805ab770 / 1805ab780 / 1805ab790, 0x410b9880 | per-cascade split attributes (nothing sets them in play as far as read) |
| attribute 0xb506b94b | csm_max_visible_dist |
| attribute 0xb7a3d0d5 | csm_max_dist_between_caster_and_receiver |
| -5e-6, -5e-6, -8e-6, -9e-5 (18066c530; same at 18066c520 for view type 0x2d) | bias_k per cascade |
| 1.42 | whole-range diameter factor |
| 0.6 | steep sun (dir.z) for the SST shear |
| 0.15 | previous cascade box shrink a side |
| 180922570 | global: 0 negates the receiver biases (read as: depth not reversed) |
| 0.001 .. 0.5 | fade clamp |

## Shadow quality levels (CSMQualityLevel, `videocfg_shadow_quality`)

video_defaults_0..3.txt set videocfg_shadow_quality 0..3 and videocfg_dynamic_shadows 0 / 1 / 1 / 1.

| Convar | Low | Medium | High | Very High |
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

- Sun shadows reach 560 units at every level. Low: no static geometry in the cascades (static shadows from the bake alone; players and dynamic props on top); Medium: static geometry in cascades 0..1; High / Very High: 0..2.
- `sparseshadowtree_cascade_mask` (bit per cascade): that cascade's static geometry from the sparse shadow tree (SST: precomputed per map, "static geo rendered into cascades via SST", unpacked by CopySSTDepthToCSM_PS) instead of drawn: Medium's cascade 1, High's cascade 2.

## Convar defaults (scenesystem registrations)

Value at the object + 8 -> + 0x58. A registration's type code at [rsp + 0x30] .. word, default at [rsp + 0x37].

| Convar | Default | Registration | Object |
|---|---|---|---|
| csm_max_num_cascades_override | -1 (int) | 180012be0 | 180890f40 |
| csm_max_shadow_dist_override | -1.0 | 180012c90 | 180890fa0 |
| csm_max_visible_dist | 7500 | 180012d40 | 180890ff0 |
| csm_max_dist_between_caster_and_receiver | 15000 | 180012b30 | 180890f50 |
| csm_cascade0..3_override_dist | -1.0 | 1800127c0 / 180012870 / 180012920 / 1800129d0 | 180890e80 / 180890f10 / 180890f90 / 180890f70 |
| csm_bias_override_0..3 | 1.0 (used only when <= 0) | 180012500 / 1800125b0 / 180012660 / 180012710 | 180890f60 / 180890e90 / 180890f20 / 180890ee0 |
| csm_res_override_0..3 | 0 | 180012df0 / 180012ea0 / 180012f50 / 13000 | 180890fc0 / 180890fb0 / e60 / ea0 |
| csm_viewdir_shadow_bias | 0 | 180013580 | 180890ec0 |
| csm_cascade_viewdir_shadow_bias_scale | 2.0 | 180012a80 | 180890e50 |
| csm_viewmodel_shadows | 0 | 180013840 | 180890ed0 |
| csm_viewmodel_max_shadow_dist / nearz / max_visible_dist | 21 / 0.5 / 1000 | 180013630 / 790 / 6e0 | |
| csm_sst_max_visible_dist / pushback_distance | 2000 / 1500 | 180013210 / 1800132c0 | 180890f80 / 180890fe0 |
| csm_sst_shadow_focus_region_minz / maxz | -2000 / 2000 | 180013420 / 180013370 | |
| csm_sst_vertical_depth_shear_enable | 1 | 1800134d0 | 180890eb0 |
| csm_shadow_worldview_align_x_to_u / shear_align_z_to_v | 0 / 0 | 1800130b0 / 180013160 | 180890ef0 / 180890fd0 |
| sc_shadow_slopescale_depth_bias | 2.13 (0x400851ec) | 180006d50 | 18091fa50 |
| sc_shadow_depth_bias | 256 (int; TODO: the dword at the default slot read as an int) | 180006ca0 | 18091fa40 |
| sc_shadow_depth_bias_clamp | 0 | 180006e00 | 18091fa60 |
| lb_csm_receiver_plane_depth_bias | 1.5e-5 (0x3780029a) | 18000fc70 | 1809239f0 |
| lb_csm_receiver_plane_depth_bias_transmissive_backface | 1.5e-4 | 18000fd20 | 180923a00 |
| lb_csm_draw_alpha_tested / draw_translucent | 1 / 1 | 18000fdd0 / fe70 | 180923a10 / 180923a20 |
| lb_csm_cascade_size_override | -1 | 18000fbc0 | 1809239e0 |
| lb_csm_cross_fade_override / distance_fade_override | -1 / -1 | 18000ffc0 / 10070 | 180923a40 / 180923a50 |
| lb_csm_override_staticgeo_cascades / _value / _animated_verts | 0 / -1 / 1 | 180010120 / 1800101d0 / 180010280 | 180923a60 / 180923a70 / 180923a80 |
| lb_sun_csm_size_cull_threshold_texels | 10 | 180010330 | 180923a90 |
| lb_csm_override_bulb_radius / fov_override | -1 / -1 | 1800103e0 / 18000ff10 | 180923aa0 / 180923a30 |
| sparseshadowtree_cascade_mask | 4 | 18000acc0 | 180923120 |
| sc_shadow_depth_bias_state_override | 0 | | |

## Cascade setup (180496ef0)

1. Count: the light's m_nCascades, capped by the view's, then csm_max_num_cascades_override when > 0 (and the view isn't flagged at bit 0 of vfn 200's >> 4), clamped 1..4. With csm_viewmodel_shadows one more (the viewmodel's own cascade).
2. Splits: the light's m_flShadowCascadeDistance0.. (while > 0), the rest each twice the one before; sorted (1804945c0); then csm_cascadeN_override_dist when > 0; the valid ones counted (> 0 and increasing).
3. The rest computed: `near = max(0.125, view + 0x20)`, `far = min(view + 0x24, attribute 0x7b2a64e1 or csm_max_shadow_dist_override when > 0)`; for cascade k (0-based) of n: `lin = (far - near) (k + 1) / n + near`, `log = near (far / near)^((k + 1) / n)` (V_powf), `split = (log - lin) x 0.85 + lin + 0.1`, never below the one before. Per-cascade attributes may replace a split.
4. Camera near 6.5 and 560 units: three cascades **53.2, 164.2, 560.1**; two: 93.9, 560.1.
5. Texture matrix per cascade: `[0.5, 0, 0, 0.5 + 0.5 / res; 0, -0.5, 0, 0.5 + 0.5 / res; 0, 0, 1, bias_k]`; bias_k replaced by csm_bias_override_k when that is <= 0.
6. Atlas rects: one cascade: scale res0 / A; two: side by side (u offsets 0 / 0.5, u scale x 0.5); three or four: 2 x 2 grid (offsets 0 / 0.5 each way, scale x 0.5).
7. 180494b40 with: near, the splits, csm_max_visible_dist (SST view: csm_sst_max_visible_dist), csm_max_dist_between_caster_and_receiver (SST: csm_sst_pushback_distance).
8. Per cascade: the view-direction bias `(k x csm_cascade_viewdir_shadow_bias_scale + 1) x csm_viewdir_shadow_bias`; the cascade's depth span.
9. End: param_1[0x5ac..], 0x5b2..0x5b5 (Fields).

## Fit (180494b40)

1. The light's view (180156120; 180156530 with csm_shadow_worldview_align_x_to_u); with csm_sst_vertical_depth_shear_enable and dir.z > 0.6 the SST view is sheared.
2. Whole range: 1804969e0(near, last split) -> diameter D0; param_5 = 1.42 D0; extrusion `E = max(1.42 D0, max(csm_max_visible_dist, last split, csm_max_dist_between_caster_and_receiver))` (15000 in play).
3. Per cascade k (stopped when k > 0 and the cascade's near > csm_max_visible_dist):
   - 1804969e0(d0, d1): the 8 frustum corners between planar depths d0 and d1; W = the largest distance between two corners (the cascade's width: independent of view rotation); corners to world space.
   - Corners in light space: x / y min and max, depth min and max; again with each corner pushed E along the light direction; a later cascade's far depth at least the one before's.
   - Texel snap: `pad = (W - (max - min)) x 0.5` per axis, `texel = W / res`, `left = floor((min - pad) / texel) x texel`, `right = floor((max + pad) / texel) x texel` (both floored), same for y; depth `near = floor(0) = 0`, `far = ceil(zmax - zmin)`; light view translated by -zmin; 180498af0.
   - Culling: up to 12 planes from 180495df0, plus from the second cascade on the previous cascade's box shrunk 15 % a side as 6 exclude planes (a caster inside it is the higher-resolution cascade's alone).

## Lookup (csgo_environment pixel shader, every combo)

`PerViewLightingConstantBufferGpu_t` (lightmapped combos, s0_d3): m9 sun direction (toward it), m10 its colour, m10 / m11
the baked shadow channel mask (by combo), m11 the cascade count, m12 the receiver bias, m13[k] the cascade's NDC limit,
m14 / m15 the cross fade, m16 / m17 the distance fade, m18[k] the cascade's world -> (NDC xy, depth z) matrix, m19[k] its
atlas rect (offset xy, scale zw), m20 the atlas (bindless).

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

- On lightmapped geometry the cascades multiply the baked shadow mask (`_24154 = _11313 x _14808`); past the cascades' 560 units the bake alone. Non-lightmapped combos (probe / vertex-stream lit): the cascades x their own baked sun visibility.
- One hardware comparison tap: the sampler's linear filter is a 2 x 2 PCF (no wider kernel for the sun).
- The smoke (smoke_volume_cs, [smoke.md](smoke.md)) uses the same factor at `lerp(1, x, 0.75)` on its sun term.

Constants (1801af7b0):
- m12 = lb_csm_receiver_plane_depth_bias (the _transmissive_backface one beside it), both negated when 180922570 is 0.
- c = lb_csm_cross_fade_override if > 0, else the light's (+0xebf0); d = lb_csm_distance_fade_override if > 0, else the light's (+0xebf4); each clamped 0.001 .. 0.5.
- `m14 = -(1 - c) / c`, `m15 = 1 / c`, `m17 = 1 / (D d)`, `m16 = -((1 - d) D) / (D d)`, D = + 0xebec.
- m13: not located.

## Casters

- Static objects (world, static props) into cascades <= lb_csm_override_staticgeo_cascades_value; with `_animated_verts` 1 (Low / Medium) only objects without SCENEOBJECTFLAG_CAN_RENDER_INTO_SST count as static. The SST cascades take static geometry from the tree.
- Dynamic objects (players, dynamic props, weapons, grenades) into every cascade.
- Objects under lb_sun_csm_size_cull_threshold_texels texels in a cascade are culled.
- Alpha-tested materials cast (cut out by their alpha in the depth pass: the crane jib's lattice shadow on de_vertigo); translucent at High and up; F_DO_NOT_CAST_SHADOWS never (csgo_environment feature "Shadows" -> BoolAttribute DoNotCastShadows).
- Particles: r_particle_shadows (Very High) renders g_tParticleShadowBuffer (screen space, min'd in the lookup); cables with r_particle_cables_cast_shadows.
- Raster bias: sc_shadow_slopescale_depth_bias 2.13, sc_shadow_depth_bias 256, clamp 0 (18018a470, sc_shadow_depth_bias_state_override 0). On a float depth buffer the constant bias takes the primitive's largest depth's exponent (256 x 2^-24 = 1.5e-5 of depth at 1.0).
- CS2 draws a shadow-only body for the local player (unread).

## Unread

- 180156120 / 180156530 (the light view's basis; its roll), 180495df0's planes, 1804a8770's exact corner construction (planar depth assumed).
- 1801af7b0's m13 and the + 0xebec writer; 180922570's meaning; m19's packer (the half-texel term).
- The view struct's fields (+0x20 / +0x24); how the view's near / far reach 180496ef0's param_3 + 0x18.
- The SST build and unpack (sparseshadowtree_*); the viewmodel cascade's fit (csm_viewmodel_*); the transmissive backface bias' use.
- param_1[0x5b2..0x5b5]'s consumer.
- SCENEOBJECTFLAG_CAN_RENDER_INTO_SST's meaning beyond the convar's help; the size-cull measure.
- CS2's depth-only combo for F_ALPHA_TEST (its reference and texcoord scroll); the environment shaders' blended alpha in the cascades.
- The local player's shadow-only body.
