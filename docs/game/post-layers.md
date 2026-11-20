# The post-processing layers

materialsystem2_20261023, client_20261015, rendersystemdx11, scenesystem; shaders from game/core shaders_vulkan and
shaders_vulkan_dir.vpk (VRF 20.1). Overlay .vposts: pak01 lighting/postprocessing/.

One frame's post-processing is composed from weighted .vpost layers in materialsystem2's `CPostProcessingState` (one
per view / split-screen slot). The map's post_processing_volume entities and the client mode's overlays (death cam, buy
menu, HLTV) are layers in the same state.

## Functions

| Address | Module | What |
|---|---|---|
| 18005c8e0 | materialsystem2 | CPostProcessingState ctor (+0xb8 = 1, makes the merged lookup) |
| 18005d870 / 18005d9d0 | materialsystem2 | layer hash find / insert |
| 18005ded0 | materialsystem2 | introsort of ints (groups) |
| 18005c710 | materialsystem2 | slot 0x08 tick |
| 180058500 | materialsystem2 | slot 0x30 compose |
| 180057e50 | materialsystem2 | slot 0x38 layer(resource, group) |
| 180058160 | materialsystem2 | slot 0x40 release layer |
| 18005bff0 | materialsystem2 | slot 0x48 setWeight(layer, w) |
| 18005c010 | materialsystem2 | slot 0x50 fadeTo(layer, duration, flag) |
| 18005c5c0 | materialsystem2 | slot 0x58 18005c060 with no layer (a group faded to nothing) |
| 18005c5f0 | materialsystem2 | slot 0x60 remove the group's cross-fade (swap with last) |
| 18005bf90 / 18005bfb0 | materialsystem2 | slot 0x68 / 0x70 get / set +0x90 (16 bytes) and +0xbc |
| 18005bfd0 / 18005bfe0 | materialsystem2 | slot 0x78 / 0x80 get / set +0xa0 (16 bytes) |
| 18005ce80 | materialsystem2 | slot 0x88 merge the lookups |
| 18005c060 | materialsystem2 | the cross-fade (SetColorCorrectionLookupWeight in VPROF string 0x18012eb50) |
| 180057840 | materialsystem2 | override colour correction path (unread) |
| 18005ac40 | materialsystem2 | tone curve texture (unread) |
| 18005a290 | materialsystem2 | tone map blend |
| 18005b100 / 18005aea0 | materialsystem2 | bloom blend / its accumulate |
| 18005b300 | materialsystem2 | vignette blend |
| 18005bbf0 | materialsystem2 | local contrast blend |
| 18005bd10 / 18005bea0 | materialsystem2 | fog scattering / local exposure blends (unread) |
| 18005f090 | materialsystem2 | lookup upload ("colorcorrection_%p.vtex") |
| 180a24320 / 180a380e0 | client | set 0x18254eae8 (the post-processing system interface) |
| 180d0a4d0 | client | releases the layers at shutdown |
| 18029c040 | client | C_PostProcessingVolume becomes active |
| 180275bf0 | client | (gate for the exposure control) |
| 180cf1d20 | client | ClientModeCSNormal init for a slot |
| 180d0d540 | client | ClientModeCSNormal::Update's part: overlay weights |
| 180c7c160 | client | local pawn |
| 18094dc60 | client | `mov al, 1; ret` |
| 1804ffb20 | client | a replay plays |
| 1811e88a0 | client | reads the bloom result; makes the local contrast targets |
| 18120b510 | client | compute bloom renderer's Render |
| 181211d00 | client | Gaussian bloom pass Render |
| 1800c3b90 -> 1800c2900 | scenesystem | CSceneSystem vfn 0x1b8: scratch chain ("rendertarget_scratch_16161616F_mip_%d_%d") |
| 18027aa10 | scenesystem | full mip chain (w, h, 1) |
| 1811f75a0 | client | Gaussian chain |
| 1811fd000 | client | the combine |
| 18120fc00 / 181210ab0 | client | PostProcessing pass Render / sets the blurred scale-clamp |
| 180125db0 | client | r_csgo_render_post_local_contrast (default 1) |

## Fields

RTTI vtables: `CPostProcessingState` 0x18012ed48, `CPostProcessingSystem` 0x18012ee70, `CPostProcessingTypeManager`
0x18012ef80.

| Offset | Field |
|---|---|
| state +0x08 .. +0x1c | (resource, group) -> layer hash (murmur2 constant 0x5bd1e995) |
| state +0x28 / +0x30 | layers: count, pointer array (order made) |
| state +0x40 / +0x48 | groups: count, int array (sorted ascending) |
| state +0x78 / +0x80 | cross-fades: count, 0x28-byte entries { +0 group, +4 duration f32, +8 start f64, +0x10 count, +0x18 items (0x10 each: layer, from f32, to f32), +0x20 capacity, +0x24 flags } |
| state +0xb0 | now (f64, Plat_FloatTime) |
| state +0xb8 | enabled (byte; 0: compose writes the no-op) |
| state +0xb9 | copied to result +0x128 |
| state +0xc0 | merged lookup texture (32 x 32 x 32, format code 0x450) |
| state +0xc8 / +0x108 / +0x128 | last merge's lookups (8 pointers), weights (8 floats), count (0x7fffffff at first) |
| layer (0x10) +0 | resource binding (its +0x20 ref count, > 0 loaded; its +0 the PostProcessingResource_t) |
| layer +8 / +0xc | group (int) / weight (f32, 0 when made) |
| PostProcessingResource_t +0x0 | m_bHasTonemapParams (m_toneMapParams +4 .. +0x3c) |
| +0x40 | m_bHasBloomParams (m_bloomParams; m_blendMode +0, m_flBloomStartValue +0x1c relative) |
| +0xcc | m_bHasVignetteParams (strength +0xd0, centre +0xd4 / +0xd8, radius +0xdc, roundness +0xe0, feather +0xe4, tint +0xe8..+0xf0) |
| +0xf4 | m_bHasLocalContrastParams (+0xf8 .. +0x108: strength, edge strength, vignette start, end, blur) |
| +0x120 | m_bHasColorCorrection |
| +0x121 | m_bHasFogScatteringParams |
| +0x144 | m_bHasLocalExposureParams |
| result +0 | lookup default weight |
| result +8 / +0x10 / +0x18 / +0x20 | merged lookup (0 with none) / tone curve texture / vignette cbuffer / D_VIGNETTE |
| result +0x24.. | bloom (+0x24 has bloom) |
| result +0xc0 / +0xd0 .. | from +0x90 / +0xa0 / +0xbc |
| result +0xd4 / +0xd5 | has tone map / has local contrast |
| result +0xd8.. | local contrast (+0xd8 .. +0xe8, read at 1811ea385) |
| result +0xec.. | tone map's 15 floats |
| C_PostProcessingVolume +0x1190 | m_hPostSettings |
| +0x1198 | m_flFadeDuration |
| +0x119c / +0x11a0 | exp2 min / max exposure fallback |
| +0x11a4 / +0x11a8 | min / max exposure |
| +0x11ac | 2^ it |
| +0x11b0 .. +0x11b8 | auto exposure (auto-exposure.md) |
| +0x11bd | m_bExposureControl |
| client mode +0x78 / +0x90 | cc_freeze_ct / cc_freeze_t handles |
| client mode +0xe0 + 8k / +0xa8 + 8k | overlay handles / resources |
| client mode +0x118 .. +0x130 | overlay weights (+0x118 in_buy_menu, +0x11c round_end_via_bombing, +0x12c hltv_replay_fade, +0x130 hltv_replay) |
| client mode +0x9c | == 3 for round_end_via_bombing |
| pawn +0x15ea | m_bIsBuyMenuOpen |
| compute bloom renderer (0x30, vtable 0x181d2a658) | +0x18 .. +0x28 filter size, radius, threshold, strength, effects scale; +0x2c effects-bloom flag; +0x2d result has a lookup; +0x2e local contrast |
| Gaussian bloom pass (0x98, vtable 0x181d2af20) | +0x08 .. +0x8f bloom params; +0x90 local contrast |
| view +0x1b7 / +0x1b8 / +0x188 | local contrast gates / the copy gate |

## Constants

| Value | What |
|---|---|
| 0x180164b08 (+0x58) | materialsystem2 convar gating compose (name unread) |
| 0x18014bc88 / 0x18014bc90 | override set (CPostProcessingSystem::ComputeOverrideColorCorrection) |
| 1.0 at 0x180130c80 | setWeight's max |
| 0x18012ef20 | ColorCorrectionTex0..7 attribute hashes |
| 0x180164c28 vfn 0x18 | GetNoopColorCorrection |
| 0x180154b80 vfn 0x90 | KeyValues Engine2/RenderingPipeline `Tonemapping_DefaultFilmicLinear` (gameinfo.gi: 1) |
| 0x18254eae8 | post-processing system interface (`vfn 0 ()` -> vfn 0x68 (slot)) |
| 0x18223c0e0 + 8k / 0x18223c118 + 4k | overlay names / groups |
| 0x182200068 | hltv_replay_fade weight |
| 0x1825f62e8 | client convar that must be on for 1811e88a0's local contrast targets (name not read) |
| 0x1825f5e80 | cvar: D_TENT_FILTER when > 0 |
| 0x18279cf20 vfn 0x68 | the copy into QuarterResUnthresholded (unread) |
| rendersystemdx11 0x1803f37d0 | Source 2 -> D3D11 blend table 1 2 3 4 5 6 7 8 9 10 11 14 16 17 18 19 (entry 12 = D3D11_BLEND_SRC1_COLOR) |
| rendersystemdx11 0x18042d470 | ImageFormat rows |

Hashes: scene colour 0xe2a716a1, g_tAuxInputDownSample 0x83130f4a (size 0x5b40f684 / 0x2dc82f72), D_LOCAL_CONTRAST_OUTPUT
0x800be62d, QuarterResUnthresholded 0x8386ef2a (as Gaussian input 0x20cbec6c), g_tLocalContrastOutput 0x2aee79f9,
QuarterResUnthresholdedBlurred 0xda46dde6, quarterresunthresholdedblurredscaleclamp 0xf0158634. gaussian_bloom_blur:
D_FIRST_MIP 0x6ea78d0c, D_4X_DOWNSAMPLE 0xb0ea90ef, D_TENT_FILTER 0x9aa7f59, D_BLUR_PASS 0x1927495e,
D_FRAMEBUFFER_IS_LINEAR 0x31beb995, D_MSAA_COLOR_BUFFER 0xdf6b3a95, texelsize 0xd30883e9, SourceTexture 0xb35d304b,
SourceTexture2 0xacca7602, uvscaleclamp 0xbda8932f, uvscaleclamp2 0xe69b2da4, prevmipblurtint 0x413d4db2,
currmipblurtint 0xc374e2c2; unread combo 0x77994dc.

## The state's slots

- 0x08 tick: now = Plat_FloatTime(); each cross-fade `t = clamp(f32(now - start) / duration, 0, 1)`; each item's layer
  weight = `(to - from) t + from`; t == 1 drops the entry.
- 0x38: found by the hash, or made (weight 0), group added to +0x48 (sorted), layer to +0x28.
- 0x48: layer +0xc = 0 if `0 > w` (comiss), else minss(1.0, w).
- 0x50: 18005c060(state, the layer's data if loaded else 0, layer group, layer, duration, flag).
- 18005c060: the group's entry found or appended. flag 0: duration = given, start = now (flag != 0: duration = max(0,
  duration - f32(now - start)), unused by the callers read). Items rebuilt: each layer of the group with weight > 0 and
  data not this one's -> { layer, its weight, 0 }; then, when loaded, { this layer, its weight, 1.0 }. An entry with no
  item is removed.

## Compose (180058500)

1. Convar 0x180164b08 off: the no-op result (default weight 1, no textures, each blend's no-layer defaults).
   `(param_3 & 1) == 0` with an override set: 180057840. +0xb8 == 0: the no-op lookup.
2. Seven categories, budget r = 1 each, in the code's order: colour correction, bloom, tone map, vignette, local
   contrast, fog scattering, local exposure.
3. Groups from the last (highest) to the first: the group's layers (+0x28 order) with w > 0 and data loaded go to each
   category they have, summing s per category. Then each: `w = (r / max(s, 1)) * w` (divisor 1 when s <= 1),
   `r = max(0, r - s)` (`0 <= x ? x : 0`).
4. Slot 0x88 (lookups, weights, count, the lookups' r); result +0 = that r, +8 = +0xc0 when count > 0; then the blends in
   this order: 18005a290 (tone map), 18005b100 (bloom), 18005b300 (vignette), 18005bbf0 (local contrast), 18005bd10 (fog
   scattering), 18005bea0 (local exposure).

## The blends (s = the category's weight sum)

- **Tone map 18005a290**: Σ w x the 15 floats (exposure bias, shoulder, linear strength, linear angle, toe strength, toe
  num, toe denom, white point, luminance source, exposure bias shadows / highlights, min / max shadow lum, min / max
  highlight lum). s >= 1: x (1 / s). Else + defaults x (1 - s): Tonemapping_DefaultFilmicLinear -> 0, 0, 0.001, 0.001,
  1, 1, 1, 1.5; else 0, 0.15, 0.5, 0.1, 0.2, 0.02, 0.3, 4; both then 0, 0, 0, 0, 0.5, 2, 8. +0xd4 = count > 0.
- **Bloom 18005b100**: 18005aea0 adds w x every float of m_bloomParams but m_blendMode and m_flBloomStartValue: the
  result's blend mode stays 0 (BLOOM_BLEND_ADD), start value 1.0. s > 1: x (1 / s); nothing fills the rest. +0x24 =
  count > 0 (1811e88a0 reads +0x24 / +0x28 ..).
- **Vignette 18005b300** (unrolled by four layers): Σ w x { strength, centre, radius, roundness, feather, tint }. s > 1:
  x (1 / s). s < 1: `tint = (tint - 1) s + 1`, `radius = (radius - 2) s + 2`. Count 0 or strength 0: D_VIGNETTE 0. Else
  the cbuffer (0x2c bytes, render context vfn 0x100 / 0x108), post_process's VignetteConstantBuffer_t _m0 (vec2), _m1,
  _m2, _m3 (vec3), _m4 .. _m7:
  [0] centre x, [1] -centre y, [2] `1 - clamp(-strength, 0, 1)`, [3] `3 clamp(strength, 0, 1)^2`, [4..6] tint,
  [7] `max(2 feather, 0.001)`, [8] `max(radius, 0.01)`, k = `clamp(roundness, 0, 1) 0.75 + 0.25`: [9] `2 / k`,
  [10] `-k / 2`; D_VIGNETTE = 1 + (roundness > 0.995).
- **Local contrast 18005bbf0**: Σ w x the five floats, s > 1: x (1 / s), nothing fills the rest; +0xd5 = count > 0.

## The lookups (18005ce80)

1. More than 8: "More than 8 active color correction lookup textures!", 8 kept.
2. Skipped when count, textures and every weight (within 1e-5) match the last merge.
3. Weights x `1 / (1 - r)` when r < 1. Textures to ColorCorrectionTex0..7, unused ones the no-op lookup; weights to
   g_vColorCorrectionWeights0 / 1; D_COLOR_CORRECTION_TEXTURE_COUNT = clamp(count - 1, 0, 4); dispatched 32 x 32 x 32
   into +0xc0 with materials/dev/combine_colorcorrection_lut_cs.vmat (game/core).
- combine_colorcorrection_lut_cs: out[id] = `(Σ Load(tex_i, id).rgb * w_i, 1)`: texel fetches, no filtering (variant 4
  sums all eight).
- Each .vpost's lookup is uploaded 32 x 32 x 32 (18005f090, header 0x20 / 0x20 / 0x20, format code 0x50): every CS2
  lookup is 32^3 (108 seen).
- post_process_vulkan_50_ps D_COLOR_CORRECTION_LUT: `c = mix(texture(lookup, saturate(srgb) * 0.96875 + 0.015625),
  srgb, g_flColorCorrectionDefaultWeight)` (the default weight = r). Shader order: exposure, bloom (pre), local
  contrast, tone curve, sRGB, screen bloom, the lookup, the vignette, the screen fade, the gamma.

## Who makes the layers (client)

- **C_PostProcessingVolume** (18029c040): layer = vfn 0x38 (m_hPostSettings, group 0); vfn 0x50 (layer,
  m_flFadeDuration, 0). With m_bExposureControl and no 180275bf0: vfn 0x60 -> the exposure controller, given min / max
  exposure (+0x11a4 / +0x11a8, else 2^ +0x119c / +0x11a0), 2^ +0x11ac, +0x11b0 .. +0x11b8.
- **ClientModeCSNormal** (180cf1d20): cc_freeze_ct / cc_freeze_t (lighting/postprocessing/correction/, group 4); then
  k = 0..6 `lighting/postprocessing/effects/%s.vpost`: in_buy_menu 5, round_end_via_bombing 4, death_cam_phase1 4,
  death_cam_phase1_low_violence 4, death_cam_phase2 5, hltv_replay_fade 5, hltv_replay 4 (name, group). Released in
  180d0a4d0.
- **180d0d540** (every frame, vfn 0x48): in_buy_menu = 1 when the local pawn is alive (vfn 0xab8) and m_bIsBuyMenuOpen,
  else 0; round_end_via_bombing stepped 1/64 toward 1 only when +0x9c == 3, the observed pawn exists and 18094dc60 is
  false, but 18094dc60 returns 1: the weight is 0 every frame in this build; the death cam's three (death-cam.md 4);
  hltv_replay_fade = the float at 0x182200068; hltv_replay = spec_replay_colorcorrection while 1804ffb20. All 0 under
  cl_disable_postprocessing or a menu camera.

## The overlay .vposts

| .vpost | tone map | bloom | vignette | local contrast | lookup |
|---|---|---|---|---|---|
| death_cam_phase1 | - | - | strength -0.0964, radius 0.0903, roundness 0, feather 0.4665, tint (0.533, 0.109, 0.109) | 2, 2, -0.3092, 0.9408, 0.9455 | 32^3 |
| death_cam_phase1_low_violence | - | - | strength -1, radius 0.522, roundness 1, feather 0.5, tint 0 | 0.0172, 0.0128, 0, 0.678, 1 | 32^3 |
| death_cam_phase2 | - | - | - | - | 32^3 |
| in_buy_menu | - | - | - | 0.4, 0, 32, 1, 0.5 | 32^3 |
| round_end_via_bombing | - | - | - | 0, 0, -2, 1, 1 | 32^3 |
| hltv_replay_fade, hltv_replay | - | - | - | - | 32^3 |

With phase 1 at 1 the lookup is phase 1's alone (group 4 before the volume's group 0); phase 2 (group 5) then takes the
lookup budget from both; the volume keeps its tone map and bloom.

## Local contrast's input

- **1811e88a0**, with result +0xd5, convar 0x1825f62e8 on and view +0x1b7 / +0x1b8 clear: makes "QuarterResUnthresholded"
  ((w / 4, h / 4) of the view, `(x + (x >> 31 & 3)) >> 2`, format 0x409) and "QuarterResUnthresholdedBlurred" (format
  9), and sets the compute bloom renderer's +0x2e = 1. View +0x188 clear: first a copy (0x18279cf20 vfn 0x68) into
  QuarterResUnthresholded.
- **18120b510**: the bloom's downsample loop; on pass 1 (level 0 -> 1, quarter-res) with +0x2e: binds the scene colour
  as g_tAuxInputDownSample with its size, D_LOCAL_CONTRAST_OUTPUT = 1, QuarterResUnthresholded as g_tLocalContrastOutput.
- **bloom_cs** (variant d8 = D_BLOOM_MODE 0 + D_LOCAL_CONTRAST_OUTPUT 1; d0-d3 the four modes, d4-d7 pano outputs,
  d8-d13 local contrast): besides the mode-0 downsample, stores at texel p the aux input sampled bilinearly at uv =
  `(p + 0.5) / dst size` (into the used part, clamped 1.5 texels from its edge), expanded `c / (1 - max(r, g, b))`,
  alpha 1 (undoing the scene colour's storage `c / (1 + max)`; mode 1's taps undo it the same way).
- **The blur** "Local Contrast Gaussian Blur": the Gaussian bloom pass object with +0x90 = 1 and the composed bloom
  params copied into +0x08 .. +0x8f; input QuarterResUnthresholded (0x20cbec6c) when +0x90 is set, output
  QuarterResUnthresholdedBlurred. 181211d00: chain texture from
  1800c3b90 (smallest of three size tiers holding the pass size, type 3 -> 1800c2900, RGBA16F (0xf), flags 0x409, full
  mip chain); start level by halving the chain until below the pass size (0 here); then 1811f75a0 and 1811fd000.

## The Gaussian chain (1811f75a0) and the combine (1811fd000)

materials/dev/gaussian_bloom_blur.vmat (24 programs): combos D_FIRST_MIP, D_4X_DOWNSAMPLE, D_VIGNETTE, D_TENT_FILTER,
D_BLUR_PASS, D_FRAMEBUFFER_IS_LINEAR, D_MSAA_COLOR_BUFFER, D_TONEMAP_BLEND. Every sampler: AddressU / V Border, border
colour 0, MinMagMipLinear. The VS flips y (D3D's top-down pixels).

1811f75a0 (param_3 source, param_5 chain, param_6 temp, param_8 bloom params, param_9 start level, param_10 source
already quarter-res): for each level l from the start while below `min(start + (5 - (+0x90 != 0)), chain mips)`,
viewport = pass size halved l times (int / 2):
- Downsample into level l: start level with param_10 (local contrast): a copy from the source, D_BLUR_PASS 0,
  D_FRAMEBUFFER_IS_LINEAR 1, MSAA 0, texelsize `(1 / (2 src w), 1 / (2 src h), vw - 0.5, vh - 0.5)`; later levels from
  l - 1: D_4X_DOWNSAMPLE 0, linear 1, MSAA 0, texelsize `(1 / (chain w >> (l - 1)), ..., chain w >> l, ...)`. (Without
  param_10 the start level is the 4x downsample with D_FIRST_MIP 1 and threshold / skybox from param_8 +0x10 /
  max(+0x14, 0.0001) / +0x18.) D_BLUR_PASS 0: `clamp(sample(p * 2 * texel), 0, 65504)` (twice), alpha 1.
- Across: level l -> temp, D_BLUR_PASS 1, texelsize `(1 / level w, 1 / level h, vw - 0.5, vh - 0.5)`; down: temp ->
  level l, D_BLUR_PASS 2, texelsize `(1 / temp w, 1 / temp h, vw - 0.5, vh - 0.5)`. Programs:
  `Σ sample(min(p + offset_k, texel.zw) * texel.xy) * w_k`, offsets (-2.196197, -0.430063, 1, 2.196197) along x (pass
  1) or y (pass 2), w (0.121597, 0.529213, 0.227595, 0.121597).
- Local contrast: start 0, 4 levels, copy from QuarterResUnthresholded, temp QuarterResUnthresholdedBlurred.

1811fd000 (param_5 bloom params: m_flBlurWeight +0x38, m_vBlurTint +0x4c): D_TENT_FILTER = (cvar 0x1825f5e80 > 0),
D_BLUR_PASS 3, linear 1; steps i from `min(5 - (+0x90 != 0), mips - start) - 2` down to 0, L = start + i,
k = (+0x90 != 0) + i:
- prevmipblurtint: first step `w[k + 1] t[k + 1]`, else (1, 1, 1); currmipblurtint: `w[k] t[k]`, except i = 0 with
  +0x90: `(w1 t1.x + t0.x w0, w1 t1.y + w0 t0.y, w1 t1.z + w0 t0.z)` (local contrast's level 0 stands for bloom levels 0
  and 1).
- i > 0: into level L (viewport pass size >> i), SourceTexture = level L + 1, uvscaleclamp = `(1 / (chain w >> L),
  1 / (chain h >> L), ((vw >> 1) - 0.5) / (chain w >> (L + 1)), ((vh >> 1) - 0.5) / (chain h >> (L + 1)))`.
  D_BLUR_PASS 3: `o0 = Σ4 sample(min(uvscale (p ± 1), clamp)) * prevTint * 0.25`, `o1 = currTint`, blended One + dst x
  SRC1_COLOR (VRF prints "InvBlendFactor": its enum keeps an INV_BLEND_FACTOR Source 2 lacks; table entry 12 is
  D3D11_BLEND_SRC1_COLOR).
- i = 0: into the output (param_7), D_BLUR_PASS 4, SourceTexture2 = level start, uvscaleclamp2 = `(1 / w, 1 / h,
  (vw - 0.5) / w, (vh - 0.5) / h)` of that level: `o = Σ4 / 4 + currTint * sample(SourceTexture2, min(uvscale p,
  clamp2))`, no blend.

## post_process D_LOCAL_CONTRAST

Variant d3 alone, d15 with the bloom. After exposure and the bloom's pre step, before the curve:

    uv = fragcoord / view size
    v  = smoothstep(localContrastVignetteStart, End, length(uv 2 - 1))
    s  = mix(localContrastStrength, EdgeStrength, v)
    b  = dot(sample(QuarterResUnthresholdedBlurredTexture, min(uv, sc.zw) * sc.xy), (0.2125, 0.7154, 0.0721))
    c += max(s (luma709(c) - b), step(0, s) - 1)
    c  = mix(c, b, v * localContrastBlurredVignetteStrength)

The five values: result +0xd8 .. +0xe8. The blurred sampler is DefaultSamplerState_0 (bilinear, wrap). sc
(181210ab0 in 18120fc00): q = view / the pass object's +8 (4: 1811e9d99), `(q / tex w, q / tex h, (q - 0.5) / q, ...)`.
Gate: r_csgo_render_post_local_contrast (default 1).

## Unread

- View +0x1b7 / +0x1b8 (both clear for the main view: local contrast on) and +0x188's copy.
- The non-local-contrast Gaussian path's 4x first mip (D_4X_DOWNSAMPLE, D_TONEMAP_BLEND, combo 0x77994dc).
- 18005bd10 / 18005bea0, 18005ac40, 180057840.
- Convar 0x180164b08's name.
- The merged lookup's format: 18005c8e0 fills the descriptor with 32 / 32 / 32, byte 1 at +6, 0 at +8, 0x450 at +0x10
  (flags); the format is ImageFormat 0 (RGBA8888) or 1 (ABGR8888) (0x18042d470's rows): 8-bit UNORM either way, so the
  merge clamps and quantises.
