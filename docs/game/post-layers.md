# The post-processing layers (materialsystem2_20261023, client_20261015)

CS2 draws one frame's post-processing from weighted .vpost **layers** kept by materialsystem2's `CPostProcessingState`
(one per view / split-screen slot). The map's post_processing_volume entities and the client mode's overlays (the
death cam's, the buy menu's, HLTV's) are layers in the same state; each frame it composes them. Ported in
web/src/world/post-layers.js (the state) and web/src/world/tonemap.js (the frame); the overlay .vposts are baked by
`lasers-bake --stock-posts web/public/ze-post` (bake/LightingBake.cs StockPosts).

## 1. The state (materialsystem2_20261023)

RTTI: `CPostProcessingState` vtable **0x18012ed48**, `CPostProcessingSystem` 0x18012ee70, `CPostProcessingTypeManager`
0x18012ef80. Fields (the state):

| offset | what |
|---|---|
| +0x08 .. +0x1c | the (resource, group) -> layer hash (murmur2 constant 0x5bd1e995; find 18005d870, insert 18005d9d0) |
| +0x28 / +0x30 | the layers: count, pointer array, in the order made |
| +0x40 / +0x48 | the groups: count, int array, kept sorted ascending (18005ded0: an introsort of ints) |
| +0x78 / +0x80 | the cross-fades: count, 0x28-byte entries { +0 group, +4 duration f32, +8 start f64, +0x10 count, +0x18 items (0x10 each: layer, from f32, to f32), +0x20 capacity, +0x24 flags } |
| +0xb0 | now (f64, Plat_FloatTime, set by slot 0x08) |
| +0xb8 | enabled (byte, 1 from the constructor 18005c8e0; 0: compose writes the no-op result) |
| +0xb9 | copied to the result +0x128 |
| +0xc0 | the merged lookup texture (32 x 32 x 32, format code 0x450, made in 18005c8e0) |
| +0xc8 / +0x108 / +0x128 | the last merge's lookups (8 pointers), weights (8 floats), count (0x7fffffff at first) |

A layer (0x10 bytes, made by slot 0x38): +0 the resource binding (its +0x20: the resource's ref count, > 0 = loaded; its
+0: the PostProcessingResource_t data), +8 group (int), +0xc weight (f32, 0 when made).

Slots:

| slot | address | what |
|---|---|---|
| 0x08 | 18005c710 | tick: now = Plat_FloatTime(); each cross-fade t = clamp(f32(now - start) / duration, 0, 1); each item's layer weight = (to - from) t + from; t == 1 drops the entry |
| 0x30 | 180058500 | compose (section 2) |
| 0x38 | 180057e50 | layer(resource, group): found by the hash, or made (weight 0), its group added to +0x48 (sorted) and the layer to +0x28 |
| 0x40 | 180058160 | the layer released (client 180d0a4d0 calls it at shutdown) |
| 0x48 | 18005bff0 | setWeight(layer, w): layer +0xc = 0 if 0 > w (comiss), else minss(1.0 (0x180130c80), w) |
| 0x50 | 18005c010 | fadeTo(layer, duration, flag): 18005c060(state, the layer's data if loaded else 0, layer group, layer, duration, flag) |
| 0x58 | 18005c5c0 | 18005c060 with no layer (a group faded to nothing) |
| 0x60 | 18005c5f0 | the group's cross-fade removed (the list entry swapped with the last) |
| 0x68 / 0x70 | 18005bf90 / 18005bfb0 | get / set +0x90 (16 bytes) and +0xbc |
| 0x78 / 0x80 | 18005bfd0 / 18005bfe0 | get / set +0xa0 (16 bytes) |
| 0x88 | 18005ce80 | merge the lookups (section 3) |

**18005c060** (SetColorCorrectionLookupWeight in the VPROF string 0x18012eb50; the cross-fade): the group's entry is
found or appended. flag 0: entry duration = the given duration, start = now (flag != 0: duration = max(0, duration -
f32(now - start)), unused by the callers read). Its items are rebuilt: every layer of the group whose weight > 0 and
whose data is not this one's -> { layer, its weight, 0 }; then, when the data is loaded, { this layer, its weight,
1.0 }. An entry left with no item is removed.

## 2. Compose (180058500, slot 0x30)

Output struct (param_2): +0 the lookup default weight, +8 the merged lookup texture (0 with no lookup layer), +0x10 the
tone curve texture (18005ac40), +0x18 the vignette constant buffer, +0x20 D_VIGNETTE, +0x24.. bloom, +0xd4 has tone
map, +0xd5 has local contrast, +0xd8.. local contrast, +0xec.. the tone map's 15 floats, +0xc0 / +0xd0 .. from +0x90 /
+0xa0 / +0xbc.

- A convar at 0x180164b08 (+0x58, name unread) off: the no-op result (default weight 1, no textures, the defaults of each
  blend with no layer). `(param_3 & 1) == 0` with an override set (0x18014bc88 / 0x18014bc90, CPostProcessingSystem::
  ComputeOverrideColorCorrection): 180057840 instead (unread). +0xb8 == 0: the no-op lookup.
- Seven categories, each with a budget r = 1 (in this order of the code's flags on the resource data, field offsets
  from PostProcessingResource_t's schema): m_bHasColorCorrection +0x120, m_bHasBloomParams +0x40, m_bHasTonemapParams
  +0x0, m_bHasVignetteParams +0xcc, m_bHasLocalContrastParams +0xf4, m_bHasFogScatteringParams +0x121,
  m_bHasLocalExposureParams +0x144.
- The groups from the last (highest) to the first: the group's layers (+0x28 order) with weight w > 0 and their data
  loaded go to each category they have, summing s per category. Then each of this group's entries:
  w = (r / max(s, 1)) x w (the divisor 1 when s <= 1), and r = max(0, r - s) (`0 <= x ? x : 0`).
- Then: slot 0x88 (lookups, weights, count, r of the lookups); result +0 = that r, +8 = +0xc0 when count > 0; the
  blends 18005a290 (tone map), 18005b100 (bloom), 18005b300 (vignette), 18005bbf0 (local contrast), 18005bd10 (fog
  scattering), 18005bea0 (local exposure).

The blends (s = the sum of the category's weights):

- **18005a290** tone map: Σ w x m_toneMapParams' 15 floats (+4 .. +0x3c: exposure bias, shoulder, linear strength,
  linear angle, toe strength, toe num, toe denom, white point, luminance source, exposure bias shadows / highlights,
  min / max shadow lum, min / max highlight lum). s >= 1: x (1 / s). Else + the defaults x (1 - s): KeyValues
  Engine2/RenderingPipeline `Tonemapping_DefaultFilmicLinear` (vfn 0x90 of 0x180154b80, CS2's gameinfo.gi: 1) ->
  0, 0, 0.001, 0.001, 1, 1, 1, 1.5; else 0, 0.15, 0.5, 0.1, 0.2, 0.02, 0.3, 4; both then 0, 0, 0, 0, 0.5, 2, 8.
  +0xd4 = count > 0. The curve texture from 18005ac40 (not read: the shader's curve is ported from post_process).
- **18005b100** bloom: 18005aea0 adds w x every float of m_bloomParams but m_blendMode (+0) and m_flBloomStartValue
  (+0x1c): the result's blend mode stays the accumulator's 0 (BLOOM_BLEND_ADD) and its start value 1.0. s > 1: x (1 / s);
  nothing fills the rest. +0x24 = count > 0 (client 1811e88a0 reads the bloom from this result, its +0x24 / +0x28 ..).
- **18005b300** vignette: Σ w x { strength +0xd0, centre +0xd4 / +0xd8, radius +0xdc, roundness +0xe0, feather +0xe4,
  tint +0xe8..+0xf0 } (unrolled by four layers). s > 1: x (1 / s). s < 1: tint = (tint - 1) s + 1, radius = (radius - 2)
  s + 2. Count 0 or strength 0: D_VIGNETTE 0. Else the constant buffer (0x2c bytes, vfn 0x100 / 0x108 of the render
  context): [0] centre x, [1] -centre y, [2] 1 - clamp(-strength, 0, 1), [3] 3 clamp(strength, 0, 1)^2, [4..6] tint,
  [7] max(2 feather, 0.001), [8] max(radius, 0.01), k = clamp(roundness, 0, 1) 0.75 + 0.25: [9] 2 / k, [10] -k / 2;
  D_VIGNETTE = 1 + (roundness > 0.995). These are post_process's VignetteConstantBuffer_t _m0 (vec2), _m1, _m2, _m3
  (vec3), _m4 .. _m7 (settling tonemap.js's old reading of the shader's unnamed constants: c2 was max(strength, 0), it is
  3 clamp(strength)^2; c4 was the feather, it is twice it; c6 was 2 / roundness, it is 2 / (0.25 + 0.75 roundness)).
- **18005bbf0** local contrast: Σ w x the five floats (+0xf8 .. +0x108: strength, edge strength, vignette start, end,
  blur), s > 1: x (1 / s), nothing fills the rest; +0xd5 = count > 0.
- 18005bd10 / 18005bea0 (fog scattering, local exposure): not read (no overlay carries them).

## 3. The lookups (18005ce80, slot 0x88, and the shaders)

- More than 8: the warning "More than 8 active color correction lookup textures!", 8 kept.
- Skipped when the count, the textures and every weight (within 1e-5) match the last merge.
- Weights x 1 / (1 - r) when r < 1 (r: the lookup budget left). The textures go to ColorCorrectionTex0..7 (attribute
  hashes at 0x18012ef20), the unused ones the no-op lookup (vfn 0x18 of 0x180164c28, GetNoopColorCorrection), the
  weights to g_vColorCorrectionWeights0 / 1; D_COLOR_CORRECTION_TEXTURE_COUNT = clamp(count - 1, 0, 4); dispatched
  32 x 32 x 32 into +0xc0 with materials/dev/combine_colorcorrection_lut_cs.vmat (game/core).
- **combine_colorcorrection_lut_cs** (game/core shaders_vulkan, VRF 20.1): out[id] = (Σ Load(tex_i, id).rgb x w_i, 1):
  texel fetches, no filtering (variant 4 sums all eight).
- Each .vpost's lookup is uploaded as a 32 x 32 x 32 texture (18005f090: "colorcorrection_%p.vtex", the header
  0x20 / 0x20 / 0x20, format code 0x50): every CS2 lookup is 32^3 (all 108 in our bakes too).
- **post_process_vulkan_50_ps** D_COLOR_CORRECTION_LUT: c = mix(texture(lookup, saturate(srgb) x 0.96875 + 0.015625),
  srgb, g_flColorCorrectionDefaultWeight) (the default weight = r). The shader's order: exposure, bloom (pre), local
  contrast, tone curve, sRGB, screen bloom, the lookup, the vignette, the screen fade, the gamma.

## 4. Who makes the layers (client_20261015)

The state of a slot: `(*0x18254eae8)->vfn 0 ()` -> vfn 0x68 (slot) (0x18254eae8 is set by 180a24320 / 180a380e0: the
post-processing system interface; its vfn 0x68 hands out the slot's CPostProcessingState).

- **C_PostProcessingVolume** (18029c040, on the volume becoming the active one): layer = vfn 0x38 (m_hPostSettings
  +0x1190, group 0); vfn 0x50 (layer, m_flFadeDuration +0x1198, 0). With m_bExposureControl (+0x11bd) and no 180275bf0:
  vfn 0x60 -> the exposure controller, given min / max exposure (+0x11a4 / +0x11a8, else 2^ +0x119c / +0x11a0), 2^
  +0x11ac, +0x11b0 .. +0x11b8 (the auto exposure: auto-exposure.md, ported in world/tonemap-system.js).
- **ClientModeCSNormal** (180cf1d20, its init for a slot): cc_freeze_ct / cc_freeze_t
  (lighting/postprocessing/correction/, group 4, handles +0x78 / +0x90); then for k = 0..6 the .vpost
  `lighting/postprocessing/effects/%s.vpost` of the name at 0x18223c0e0 + 8k in the group at 0x18223c118 + 4k, handle
  at +0xe0 + 8k (resource +0xa8 + 8k): in_buy_menu 5, round_end_via_bombing 4, death_cam_phase1 4,
  death_cam_phase1_low_violence 4, death_cam_phase2 5, hltv_replay_fade 5, hltv_replay 4. Released in 180d0a4d0.
- **180d0d540** (ClientModeCSNormal::Update's part, every frame) sets the weights with vfn 0x48: +0x118 in_buy_menu = 1
  when the local pawn (180c7c160) is alive (vfn 0xab8) and m_bIsBuyMenuOpen (+0x15ea), else 0; +0x11c
  round_end_via_bombing: stepped 1/64 toward 1 only when the client mode's +0x9c == 3, the observed pawn exists and
  18094dc60 is false, but **18094dc60 is `mov al, 1; ret`**: the weight is set to 0 every frame in this build; the death
  cam's three (death-cam.md 4); +0x12c hltv_replay_fade = the float at 0x182200068; +0x130 hltv_replay =
  spec_replay_colorcorrection while 1804ffb20 (a replay plays). All 0 under cl_disable_postprocessing or a menu camera.

## 5. The overlay .vposts (pak01, baked to web/public/ze-post)

| .vpost | tone map | bloom | vignette | local contrast | lookup |
|---|---|---|---|---|---|
| death_cam_phase1 | - | - | strength -0.0964, radius 0.0903, roundness 0, feather 0.4665, tint (0.533, 0.109, 0.109) | 2, 2, -0.3092, 0.9408, 0.9455 | 32^3 |
| death_cam_phase1_low_violence | - | - | strength -1, radius 0.522, roundness 1, feather 0.5, tint 0 | 0.0172, 0.0128, 0, 0.678, 1 | 32^3 |
| death_cam_phase2 | - | - | - | - | 32^3 |
| in_buy_menu | - | - | - | 0.4, 0, 32, 1, 0.5 | 32^3 |
| round_end_via_bombing | - | - | - | 0, 0, -2, 1, 1 | 32^3 |
| hltv_replay_fade, hltv_replay | - | - | - | - | 32^3 |

So with phase 1 at 1 the lookup is phase 1's alone (group 4 before the volume's group 0), phase 2 (group 5) then takes
the lookup budget from both; the volume keeps its tone map and bloom (the overlays have none).

## 6. Local contrast's input (client_20261015, read 2026-11-17; ported: web/src/world/local-contrast.js)

- **The quarter-res unthresholded copy**: 1811e88a0, with the composed result's local contrast (+0xd5), the convar at
  0x1825f62e8 on and the view's +0x1b7 / +0x1b8 clear, makes "QuarterResUnthresholded" (size (w / 4, h / 4) of the view,
  rounded toward 0 for negatives: `(x + (x >> 31 & 3)) >> 2`, format 0x409) and "QuarterResUnthresholdedBlurred"
  (format 9), and gives the compute bloom renderer (the 0x30-byte object, vtable 0x181d2a658) +0x2e = 1 (and +0x2c the
  effects-bloom flag, +0x2d "the result has a lookup", +0x18 .. +0x28 the filter size, radius, threshold, strength,
  effects scale).
- **18120b510** (that renderer's Render): the bloom's downsample loop; on **pass 1** (the second downsample, level 0 ->
  level 1, the quarter-res level) with +0x2e set it binds the scene colour (attribute 0xe2a716a1) as
  g_tAuxInputDownSample (0x83130f4a) with its size (0x5b40f684 / 0x2dc82f72), sets **D_LOCAL_CONTRAST_OUTPUT** (combo
  hash 0x800be62d) = 1 and binds QuarterResUnthresholded (0x8386ef2a) as g_tLocalContrastOutput (0x2aee79f9).
- **bloom_cs** (shaders_vulkan_dir.vpk, VRF 20.1; variant d8 = D_BLOOM_MODE 0 + D_LOCAL_CONTRAST_OUTPUT 1; d0-d3 the
  four modes alone, d4-d7 the pano outputs, d8-d13 the local contrast ones): besides the ordinary mode-0 downsample it
  stores, at the destination texel p, the aux input sampled bilinearly at uv = (p + 0.5) / dst size (into the aux
  texture's used part, clamped 1.5 texels from its edge) and expanded c / (1 - max(r, g, b)), alpha 1. The expansion
  undoes the scene colour's storage, c / (1 + max): mode 1's taps undo it the same way (bloom.js reads our linear HDR
  target, which is never compressed, so both steps drop out together).
- **The blur**: the pass "Local Contrast Gaussian Blur" is CS2's Gaussian bloom pass object (0x98 bytes, vtable
  0x181d2af20, Render 181211d00) with +0x90 = 1 and the composed bloom parameters copied into +0x08 .. +0x8f; its input
  is QuarterResUnthresholded (0x20cbec6c) when +0x90 is set, its output QuarterResUnthresholdedBlurred (0xda46dde6).
  181211d00: the chain texture from scenesystem's CSceneSystem vfn 0x1b8 (1800c3b90: the smallest of three size tiers
  holding the pass size, type 3 -> 1800c2900: "rendertarget_scratch_16161616F_mip_%d_%d", RGBA16F (0xf), flags 0x409,
  a full mip chain 18027aa10(w, h, 1)); the start level from halving the chain until below the pass size (0 here); then
  1811f75a0 and 1811fd000 (section 7).
- When the view's +0x188 is clear, 1811e88a0 first runs a copy through 0x18279cf20 vfn 0x68 with
  QuarterResUnthresholded as its destination (not read).

## 7. The Gaussian chain and the combine (client_20261015, materials/dev/gaussian_bloom_blur.vmat)

The shader (game/core shaders_vulkan, VRF 20.1, 24 programs): combos D_FIRST_MIP (0x6ea78d0c), D_4X_DOWNSAMPLE
(0xb0ea90ef), D_VIGNETTE, D_TENT_FILTER (0x9aa7f59), D_BLUR_PASS (0x1927495e), D_FRAMEBUFFER_IS_LINEAR (0x31beb995),
D_MSAA_COLOR_BUFFER (0xdf6b3a95), D_TONEMAP_BLEND; attributes texelsize (0xd30883e9), SourceTexture (0xb35d304b, with its
mip), SourceTexture2 (0xacca7602), uvscaleclamp (0xbda8932f), uvscaleclamp2 (0xe69b2da4), prevmipblurtint (0x413d4db2),
currmipblurtint (0xc374e2c2). Every sampler: AddressU / V Border, border colour 0, MinMagMipLinear. The vertex shader
flips y (D3D's top-down pixels).

**1811f75a0** (param_3 the source, param_5 the chain, param_6 the temp, param_8 the bloom parameters, param_9 the start
level, param_10 "the source is already quarter-res"): for each level l from the start while below min(start + (5 -
(+0x90 != 0)), the chain's mips), the viewport the pass size halved l times (int / 2):
- the downsample into chain level l: at the start level with param_10 set (local contrast) a copy from the source:
  D_BLUR_PASS 0, D_FRAMEBUFFER_IS_LINEAR 1, MSAA 0, texelsize (1 / (2 src w), 1 / (2 src h), vw - 0.5, vh - 0.5); later
  levels from chain level l - 1: D_4X_DOWNSAMPLE 0, linear 1, MSAA 0, texelsize (1 / (chain w >> (l - 1)), ..., chain w >> l,
  ...). (Without param_10 the start level is the 4x downsample with D_FIRST_MIP 1 and the threshold / skybox
  attributes from param_8 +0x10 / max(+0x14, 0.0001) / +0x18.) D_BLUR_PASS 0's program: clamp(sample(p x 2 x texel), 0,
  65504) (twice), alpha 1.
- across: chain level l -> the temp, D_BLUR_PASS 1, texelsize (1 / level w, 1 / level h, vw - 0.5, vh - 0.5); down: the
  temp -> chain level l, D_BLUR_PASS 2, texelsize (1 / temp w, 1 / temp h, vw - 0.5, vh - 0.5). The programs: Σ
  sample(min(p + offset_k, texel.zw) x texel.xy) x w_k, offsets (-2.196197, -0.430063, 1, 2.196197) along x (pass 1) or
  y (pass 2), w (0.121597, 0.529213, 0.227595, 0.121597).
- Local contrast: start 0, 4 levels, the copy from QuarterResUnthresholded, the temp QuarterResUnthresholdedBlurred.

**1811fd000** (the combine; param_5 the bloom parameters: m_flBlurWeight +0x38, m_vBlurTint +0x4c): D_TENT_FILTER =
(the cvar at 0x1825f5e80 > 0), D_BLUR_PASS 3, linear 1; steps i from min(5 - (+0x90 != 0), mips - start) - 2 down to 0,
level L = start + i, k = (+0x90 != 0) + i:
- prevmipblurtint: on the first step w[k + 1] t[k + 1], else (1, 1, 1); currmipblurtint: w[k] t[k], except at i = 0 with
  +0x90 set: (w1 t1.x + t0.x w0, w1 t1.y + w0 t0.y, w1 t1.z + w0 t0.z) (local contrast's level 0 stands for bloom
  levels 0 and 1).
- i > 0: drawn into chain level L (viewport the pass size >> i), SourceTexture = chain level L + 1, uvscaleclamp =
  (1 / (chain w >> L), 1 / (chain h >> L), ((vw >> 1) - 0.5) / (chain w >> (L + 1)), ((vh >> 1) - 0.5) / (chain h >>
  (L + 1))). D_BLUR_PASS 3: o0 = Σ4 sample(min(uvscale (p ± 1), clamp)) x prevTint x 0.25, o1 = currTint, blended One +
  dst x SRC1_COLOR (VRF prints "InvBlendFactor": its enum keeps an INV_BLEND_FACTOR Source 2 lacks; rendersystemdx11's
  Source 2 -> D3D11 table 0x1803f37d0 = 1 2 3 4 5 6 7 8 9 10 11 14 16 17 18 19: entry 12 is D3D11_BLEND_SRC1_COLOR).
- i = 0: drawn into the output (param_7), D_BLUR_PASS 4, SourceTexture2 = chain level start, uvscaleclamp2 = (1 / w, 1 /
  h, (vw - 0.5) / w, (vh - 0.5) / h) of that level: o = Σ4 / 4 + currTint x sample(SourceTexture2, min(uvscale p,
  clamp2)), no blend.

**post_process D_LOCAL_CONTRAST** (variant d3 alone, d15 with the bloom): after the exposure and the bloom's pre step,
before the curve: uv = fragcoord / view size; v = smoothstep(localContrastVignetteStart, End, length(uv 2 - 1)); s =
mix(localContrastStrength, EdgeStrength, v); b = dot(sample(QuarterResUnthresholdedBlurredTexture, min(uv, sc.zw) x sc.xy),
(0.2125, 0.7154, 0.0721)); c += max(s (luma709(c) - b), step(0, s) - 1); c = mix(c, b, v x
localContrastBlurredVignetteStrength). The five values are the composed result's +0xd8 .. +0xe8 (1811e88a0 1811ea385).
The blurred image's sampler is DefaultSamplerState_0 (Source 2's defaults: bilinear, wrap; the samplers named for
differing from it say Clamp or Border). sc = quarterresunthresholdedblurredscaleclamp (0xf0158634, 181210ab0 in the
PostProcessing pass's Render 18120fc00): q = view / the pass object's +8 (4: 1811e9d99), (q / tex w, q / tex h, (q - 0.5) /
q, ...). The gate: r_csgo_render_post_local_contrast (client 180125db0, default 1).

**The port** (web/src/world/local-contrast.js, tonemap.js cs2LocalContrast, render.js): the chain's levels and the
combine's accumulation as separate half-float targets (the blend's dst read by the shader, the same sum), the border
sampler done by hand (texelFetch, black outside: WebGL has no border colour), every pass in CS2's top-down pixel space.
Checked in the browser against a JS run of the same shaders (web/src/world/dev/local-contrast-check.js): 0.58 % relative
at most over a whole frame, the half-float rounding of the intermediate targets.

## Unread

- The view's +0x1b7 / +0x1b8 flags (both clear for the main view: local contrast on) and +0x188's copy (section 6).
- The non-local-contrast Gaussian path's 4x first mip (D_4X_DOWNSAMPLE, D_TONEMAP_BLEND, the 0x77994dc combo): unused here.
- 18005bd10 / 18005bea0 (fog scattering, local exposure), 18005ac40 (the curve texture), 180057840 (the override).
- The convar at materialsystem2 0x180164b08 (its name).
- The merged lookup's format: 18005c8e0 fills its texture descriptor with 32 / 32 / 32, a byte 1 at +6, 0 at +8 and
  0x450 at +0x10 (the flags); the format field is either ImageFormat 0 (RGBA8888) or 1 (ABGR8888) (rendersystemdx11
  0x18042d470's rows): 8-bit UNORM either way, so the merge clamps and quantises (the port: an RGBA8 3D render target,
  merged on the GPU by combine_colorcorrection_lut_cs's sum).
