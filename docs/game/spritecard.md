# The spritecard: layer channel mixes, bloom-only renderers, motion-vector scale, the 1D lookup, the trail combo

particles.dll md5 b10c565480d470dbf3d606da65882870 (game 2026-11-12; in the older 63babcbf... build FUN_1802c32b0 is
1802c3250 here, 1802c0450's loop 1802c1310), client.dll of the same date. Shaders: shaders_vulkan_dir.vpk (live game
2026-11-16), dumped with ShaderDump (cs2-map-decompiler compiler/tools/re/particles/shaders/ShaderDump.Program.cs;
ValveResourceFormat 20.1.7467 + Vortice.SpirvCross 1.6.0, net10.0; `shaderdump dump <vcs> id=<n> <out>`, `combos`,
`extract <vpk> <substring> <outdir>`).

## Functions

| Address | Module | What |
|---|---|---|
| 1802c1310 | particles | packs each layer's channels / blend / type into +0x2d10 / +0x2d14 (1802c0450's loop) |
| 1802c9f00 / 1802c2470 | particles | build the renderer's scene-object layer mask |
| 1802ca022 | particles | vertex controls: picks 0x180534228 vs 0x1805341d0 for bloom-only renderers (unread) |
| 1802c3250 | particles | evaluates m_flMotionVectorScaleU / V (1802c359b / 1802c35c3) |
| 1802bdf60 | particles | input evaluator |
| 1802c4a4a | particles | writes PC c3.xy (else stays 0 at 1802c49af) |
| 1802bfc80 | particles | (this, .., 6): the ANIMMOTIONVEC group's texture (+0x2c68) |
| 1802bfd40 | particles | sets +0x2c68 (at 1802c05aa) |
| 1802d74d0 | particles | trail renderer: m_bClampV read at 1802d767d, `or [flags + 8], 0x4000` at 1802d769c; trail bit 1 of the combo word at 1802d7675 |
| 1802db280 | particles | rope renderer: m_bClampV read at 1802db42d, flag at 1802db44c; combo bit at 1802db425 |
| 180424070 | particles | F_ADDRESS_V_CLAMP off the procedural path (with the string's hash) |
| 18032a2c0 | particles | picks a sort / fill template by animation type (r9d 0 / 1 / 2) |
| 180344530 / 180346430 / 1803483b0 | particles | sorted templates (FIXED_RATE / FIT_LIFETIME / MANUAL_FRAMES) |
| 18034a320 / 18034c1c0 / 18034e0c0 | particles | unsorted templates |
| 180344eb8 | particles | FIXED_RATE: time = age |
| 180346dde | particles | FIT_LIFETIME: age / lifetime, masked to 0 where lifetime <= 0 (`cmpltps`, `divps`, `andps`) |
| 180348778 / 180348d6b | particles | MANUAL_FRAMES: attribute 38's stream loaded / stored unchanged |
| 1811cd6f0 | client | builds the "Effects Bloom" / "EffectsBloom" layers and their targets |
| 1811d1b10 | client | fills QuarterResDepth (downsample filter unread) |

## Fields

| Offset | Field |
|---|---|
| SpriteCardTextureChannel_t | schema rva 0x5cb630 |
| TextureGroup_t +0x2c | m_nTextureChannels |
| TextureGroup_t +0x30 | m_nTextureBlendMode |
| TextureGroup_t +0x28 | m_nTextureType |
| renderer +0x2d10 | per layer `channels | blend << 4` (8 bits a layer) |
| renderer +0x2d14 | `type << 3k` (<< 16 after) |
| CBaseRendererSource2 +0x23f0 | m_bOnlyRenderInEffectsBloomPass |
| +0x23f3 | m_bOnlyRenderInEffecsGameOverlay |
| +0x2268, +0x228, +0x23f1, +0x23f2, +0x41b8 | layer mask inputs (below) |
| +0x10a0 / +0x1218 | m_flMotionVectorScaleU / V |
| +0x2c68 | motion texture |
| +0x2c70 | base texture when layer 0 has none (unread) |
| texture desc +0x18 | vtex METADATA int16 at byte 6 (MotionVectorsMaxDistance, signed texels) |
| texture desc +0 / +2 | int16 width / height |
| CBaseTrailRenderer +0x3350 | m_bClampV (schema entry 0x1805c5a10) |
| C_OP_RenderRopes +0x34ec | m_bClampV (entry 0x1805c66b0) |
| particle 4-wide record +0x88 | the vertex time |
| collection +0x408 (= +0x2d8 + 38 x 8) | attribute 38 stream |
| SpriteCardPixelControls_t | `vec4 _m0.._m7; uvec2 _m8; uint _m9`: _m8 = PC c19.xy, _m9 = flag word c19.z |

## Constants

| Value | What |
|---|---|
| 0x40000 | flag ALPHA_REFERENCE |
| 0x4000 | flag F_ADDRESS_V_CLAMP (string 0x1805209a0) |
| 0x8000 | flag: a sheet (motion warp only with it) |
| 0x181d258c0 / 0x181d258d0 | "Effects Bloom" / "EffectsBloom" strings |
| +0x48 \|= 0x401801, +0x480 \|= 0x202 | the bloom layers' flag words |
| 0x181d25898 (at 1811cd808), format 9 | "QuarterResEffectsColor" at (render w >> 2, h >> 2) (`(x + (x >> 31 & 3)) >> 2` at 1811cd7e3-1811cd7fe) |
| 0x181d24ad0 (at 1811cd868), format 0x2a | "QuarterResDepth", same size, unless [+0xa0] says otherwise |
| m_flComputeBloomEffectsScale | default 1 (g_fEffectsScale) |

MotionVectorsMaxDistance per texture: explosion_fireball(_large)_01_motion -1, explosion_blast / burst -7,
fire_small_sim_a_mv -64, fire_gas_batch_b_top_mv_v2 -32, sparks_burst_mv -140, smokeloop_i_0_flw 64.

## Shader combos

spritecard_vulkan_50_ps.vcs id=1056 = S_MOTION_VECTORS=1 S_TEXTURE_LAYERS=1 ("PSM" lines: s1056_f0.glsl); 2048 /
3072 are 2 / 3 extra layers; no 3104 (motion + 3 layers).

| Combo | What |
|---|---|
| VS s16 | S_DRAW_AS_TRAIL |
| VS s128 / s160 | sprite (+ motion) |
| VS s144 | trail + 1 layer |
| VS s176 | trail + S_MOTION_VECTORS + 1 layer |
| VS s304 | trail, 2 extra layers + motion |
| PS s1024 / s1056 | sprite (+ motion) |
| PS s1536 | trail + 1 layer |
| PS s1568 | trail + motion |
| PS s2592 | trail, 2 extra layers + motion |

No motion combo with 3 extra layers (sprite or trail). Ropes and trails both use S_DRAW_AS_TRAIL.

## Channel mixes (SpriteCardTextureChannel_t)

0 RGB, 1 RGBA, 2 A, 3 RGB_A ("RGB with Alpha Passthrough"), 4 RGB_ALPHAMASK, 5 RGB_RGBMASK, 6 RGBA_RGBALPHA, 7 A_RGBALPHA,
8 RGB_A_RGBALPHA ("RGB with RGB as Alpha Passthrough"), 9 R, 10 G, 11 B, 12 RALPHA, 13 GALPHA, 14 BALPHA. The C++ copies
them unmixed (1802c1310).

- **Layer 0** (PSM:590-716): t = texel, k = blend != SUBTRACT. 0 (rgb, k); 1 t; 2 (k, k, k, a); 3 t; 4 (lerp(1, rgb, a),
  1); 5 (lerp(1, rgb, lum601), 1); 6 (rgb, lum601); 7 (k, lum601); 8 (1, 1, 1, lum601); 9-11 (c, kc, kc, k) per channel;
  12-14 (c, kc, kc, c).
- **Layers 1-3** (PSM:1001-1127; s3072 repeats at 1389 / 1800): the earlier layers' result (acc, `_23361`) in place of
  the constant 1s: 0 (rgb, k acc.a); 2 (k acc.rgb, a); 3 (rgb, acc.a a); 4 (lerp(acc.rgb, rgb, a), acc.a); 5
  (lerp(acc.rgb, rgb, lum601), acc.a); 7 (k acc.rgb, lum601); 8 (acc.rgb, acc.a lum601); 9-11 (..., k acc.a); 1, 6, 12-14
  as layer 0. (So a 1D lookup layer with channel RGB keeps the earlier alpha.)
- `_1658[ch].y` (PSM:19) is 1 for 3 and 8: a ZOOM / UVDISTORTION_ZOOM layer keeps the earlier alpha. `_1787[ch]`
  (PSM:20) is the 1D lookup's premultiply / alpha selector by the lookup layer's own channel.
- The 1D lookup reads `(lum709(srgb(q.rgb)) + uv.x) * uv.z` with q = acc (channels 0, 4, 5, 9-11), acc.a (2, 7) or
  (acc.rgb acc.a, 1). After a channel 8 base, acc.rgb = 1: the gradient's end colour, the shape in alpha.
- The flame / heat flipbooks are DXT1 (VTEX_FORMAT 1): RGB and alpha 1. The explosion flipbooks' frames are 256 px.

## Bloom-only renderers (+0x23f0)

Layer mask (1802c9f00 / 1802c2470): 9 (1 without +0x2268), | 0x40 (+0x228), | 0x80 (+0x23f0), | 0x1000 (+0x23f1), |
0x800 (+0x23f2), | 0x2000 (+0x23f3), | 0x10 (a global +0x58 with +0x1e4 < 0 or +0x220 > 0), | 0x4000 (+0x41b8). The
layer filter matching object bit 0x80 is unread.

bloom_cs D_BLOOM_MODE=1 (`bloom_cs_vulkan_50_cs.vcs id=0`, file 1, line 114):

    out = clamp(karis13(src) * g_fPreMultiply
                + textureLod(g_tEffectsBloom, bilinear clamp, min(uv, srcScale - g_vInvEffectsBloomDim.xy * 1.5)).rgb
                  * g_fEffectsScale, 0, 65504)      uv = saturate((dst + 0.5) * 2 / srcSize) * srcScale

## Motion-vector scale (PC c3.xy, 1802c4a4a)

With a motion texture (+0x2c68) and at least one layer:

    desc_m = render device vfn 0x2c8(+0x2c68)       desc_b = vfn 0x2c8(layer 0's m_hTexture, else +0x2c70)
    PC +0x30 (c3.x) = (float)(int16)desc_m+0x18 * scaleU / (float)(int16)desc_b+0
    PC +0x34 (c3.y) = (float)(int16)desc_m+0x18 * scaleV / (float)(int16)desc_b+2

else both 0.

## The 1D colour lookup layer's UV

Read for molotov_groundfire_outline.vpcf's edge flames (C_OP_RenderTrails: fire_small_sim_b_desat, a 1D_COLOR_LOOKUP
gradient, an ANIMMOTIONVEC group). The lookup's UV is not a texture coordinate. In every VS combo (sprite s128, trail
s144 / s176), a layer whose own sheet is absent (vertex controls vec2 _m9.y for layer 0, _m10.y for layer 1, <= 0) and
whose type (PC c19.y >> (16 + 3k) & 15, read in the VS from SpriteCardPixelControls_t._m0.y) is 2 gets, in place of the
corner UV (s144 layer 0: 196-330, layer 1: 1361-1775; the sheet branch's 2700 / 4032 repeat it):

    s0..s3 = four per-particle scale sources (switch 1-13 over TEXCOORD1 / COLOR0 / TEXCOORD4.w / TEXCOORD7 and the
             seed hashes; 1 for NONE), picked by nibbles of VC _m11.x (>> 16k) and VC_c4.x (>> 5k) / .y (>> 4k) /
             .z (>> 12 + 4k)
    o  = VC_c(5+k).xy * (s1, s2) + (VC_c4.x >> 5k bit 4 ? fract(TEXCOORD1.x * (51.48, 38.11)) : 0)   (layer 1's hashes)
    uv = (o.x, o.y / (VC_c(5+k).w * s0), 1 / (VC_c(5+k).z * s0), s3)

The PS (ps_s1024:870 sprite, ps_s1536:984 trail, identical) reads the gradient at
`((lum709(srgb(q.rgb)) + uv.x) * uv.z, uv.y)`: at the texel's luminance, moved by the offset, divided by the scale.
(The groundfire gradient's blue / purple stops are at 0.40 / 0.50: a lookup fed the strip's U lands in them.)

## The trail combo

**VS** bends a Catmull-Rom of four points (TEXCOORD3-6, radius in .w) at t = `TEXCOORD0.y * 0.5 + 0.5`
(s144:5262-5294):
- Corner: _23160 from TEXCOORD0 and the crop TEXCOORD8; `_20211` is it with y replaced by the rope's V,
  `(mix(T2.z, T7.x, t) + VC_c3.z) * VC_c3.w` when VC_c3.w > 0 (s144:181-182). The sheet path uses _23160 and its zoom
  lerp is `* 1.0` (s176:2685: no zoom on a trail); the no-sheet path and every layer past the base use _20211 through
  the no-sheet layer UV formula (s144:2184-2406, rotation VC_c7.x).
- Width w = the Catmull-Rom of the four radii (_16109, s144:5294), before the screen-size clamp (which makes the
  position's width _11937 from it: s176:5714-5720).
- Unless ALPHA_REFERENCE (0x40000, s144:5298), every layer UV's x and z are multiplied by w (s144:5512-5524,
  s304:8171-8183: base, layer 1, layer 2) and output_4 = (base blend, layer-1 blend, 1, w); with it the UVs stay and
  output_4.zw = (1 - s, s') from two scale sources.
- output_4.x = base sheet's blend, -1 without; .y = layer 1's own sheet's blend, else 0 when the base has a sheet
  (s176:2688 `_23767.y = 0.0`; sprites the same: s128 / s160:2918), -1 with no sheet at all.
- Motion UVs (output_6 on s176): without a sheet the base layer's UV (s176:2519); with one the motion texture's own
  sheet frames (its rows VC _m11) through the same corner and the base layer's offset / scale (s176:3859-4017, 5349),
  never multiplied by w.

**PS:**
- (ps_s1536:85-92, 215-220, s2592 layer 2) `tw = mix(1 / input_4.w, 1, flag & 0x40000)`; each layer's x and z times tw
  (projective U across a tapered quad). Layer 2 reads only xy (s2592).
- Samplers (ps_s1536:94-108): layer k's m_bClampUVs (PC c3.z bit k) clamps U and V; else flag 0x4000 samples
  `AddressV_Clamp_Filter_MinMagMipLinear` (V clamped, U wrapping); else both wrap. A 1D lookup's gradient strip uses the
  same sampler (ps_s1536:990-998).
- Motion (ps_s1568:93-157, 283-299; PSM:85-268 for sprites): only with flag 0x8000; the two motion texels fetched once,
  at input_6.xy / .zw, with layer 0's sampler, only when input_4.x > -1; else 0. Base UV =
  `(xy - (m0.yw * 2 - 1) * PC_c3.xy * input_4.x, zw + (m1.yw * 2 - 1) * PC_c3.xy * (1 - input_4.x))`, layer 1's the same
  with input_4.y when > -1 (with only the base sheeted, layer 1's zw move by the whole m1 term). Every type reads the
  moved UV: frame fetches, the 1D lookup's x / z (ps_s1568:1064), the zoom types, the distortions' base UV (PSM:427).
  Layers 2-3 have no warp or second frame on a trail.

## The vertex time (T1.z)

18032a2c0's templates write the particle's time at +0x88: FIXED_RATE the age, FIT_LIFETIME age / lifetime (0 where
lifetime <= 0), MANUAL_FRAMES attribute 38 unchanged. The VS treats all three alike at VC_c1.w (1 for MANUAL_FRAMES), so
a manual value is a sequence position, fraction and all (not a frame index): every MANUAL_FRAMES renderer in the game's
effects (106, none with m_bAnimateInFPS) sets it from a curve over the normalized age, 0..1 a whole run. Unchecked:
cosmo's hp_bar.vpcf (driven 0..16 by its script).

## Unread

- What +0x2c70 holds; whether the render device rewrites desc +0x18 at load.
- Which scale-source nibble feeds which term of the lookup UV.
- A layer's own sheet on a rope / trail (the combo's layer-1 sheet rows).
- The rope V's TEXCOORD2.z / 7.x on a trail (the trail writer's).
- How the 3-layer trail combo's layers 2-3 blend frames (s2592 shows none).
- Layers 2-3's blend weight on a sprite under a base sheet (s256 / s384 not read).
- The layer filter for object bit 0x80; 1802ca022's constant choice; 1811d1b10's filter.
- Texture detail: CS2 drops mips by its streaming budget (how, unread).
