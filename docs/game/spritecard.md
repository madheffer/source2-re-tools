# The spritecard: layer channel mixes, bloom-only renderers, the motion-vector scale, the 1D lookup, the trail combo

Read 2026-11-16 ("keen-brahmagupta" session) for CS2's layered explosion sprites (the C4's explosion_c4_500, the HE's
explosion_basic), which drew as hard-edged flat quads. Port: web/src/fx/particles/render/spritecard-ps.js,
controls.js, web/src/fx/effects.js. Binaries: particles.dll md5 b10c565480d470dbf3d606da65882870 (game 2026-11-12;
the older notes in controls.js cite 63babcbf...: FUN_1802c32b0 there is 1802c3250 here, 1802c0450's loop 1802c1310),
client.dll of the same date.

## Shader dumps

ShaderDump (cs2-map-decompiler compiler/tools/re/particles/shaders/ShaderDump.Program.cs; csproj: ValveResourceFormat
20.1.7467 + Vortice.SpirvCross 1.6.0) over spritecard_vulkan_50_ps.vcs from shaders_vulkan_dir.vpk:
`shaderdump dump spritecard_vulkan_50_ps.vcs id=1056 <out>` (S_MOTION_VECTORS=1 S_TEXTURE_LAYERS=1; 2048 / 3072 are
2 / 3 extra layers; there is no 3104 = motion + 3 layers). "PSM" lines below are s1056_f0.glsl.

## Channel mixes (SpriteCardTextureChannel_t, schema rva 0x5cb630)

0 RGB, 1 RGBA, 2 A, 3 RGB_A ("RGB with Alpha Passthrough"), 4 RGB_ALPHAMASK, 5 RGB_RGBMASK, 6 RGBA_RGBALPHA, 7 A_RGBALPHA,
8 RGB_A_RGBALPHA ("RGB with RGB as Alpha Passthrough"), 9 R, 10 G, 11 B, 12 RALPHA, 13 GALPHA, 14 BALPHA.
The C++ copies them unmixed: 1802c1310 packs each layer object's (TextureGroup_t) +0x2c m_nTextureChannels |
+0x30 m_nTextureBlendMode << 4 into +0x2d10 (8 bits a layer) and +0x28 m_nTextureType << 3k into +0x2d14 (<< 16 after).

- **Layer 0** (PSM:590-716): t = its texel, k = blend != SUBTRACT. 0 (rgb, k); 1 t; 2 (k, k, k, a); 3 t; 4 (lerp(1, rgb,
  a), 1); 5 (lerp(1, rgb, lum601), 1); 6 (rgb, lum601); 7 (k, lum601); 8 (1, 1, 1, lum601); 9-11 (c, kc, kc, k) per
  channel; 12-14 (c, kc, kc, c).
- **Layers 1-3** (PSM:1001-1127; s3072 repeats it at 1389 / 1800): the same with what the earlier layers made (acc,
  `_23361`) in place of the constant 1s: 0 (rgb, k acc.a); 2 (k acc.rgb, a); 3 (rgb, acc.a a); 4 (lerp(acc.rgb, rgb, a),
  acc.a); 5 (lerp(acc.rgb, rgb, lum601), acc.a); 7 (k acc.rgb, lum601); 8 (acc.rgb, acc.a lum601); 9-11 (..., k acc.a);
  1, 6, 12-14 as layer 0. The port had used layer 0's mix for every layer, so a 1D lookup layer (channel RGB) reset the
  flame's shape alpha to 1: the quads drew solid.
- `_1658[ch].y` (PSM:19) is 1 for 3 and 8: a ZOOM / UVDISTORTION_ZOOM layer keeps the earlier alpha.
  `_1787[ch]` (PSM:20) is the 1D lookup's premultiply / alpha selector by the lookup layer's own channel.
- The 1D lookup reads `(lum709(srgb(q.rgb)) + uv.x) * uv.z` with q = acc (channels 0, 4, 5, 9-11), acc.a (2, 7) or
  (acc.rgb acc.a, 1). After a channel 8 base, acc.rgb = 1: the gradient's end colour, the shape in alpha.

The flame / heat flipbooks are DXT1 (VTEX_FORMAT 1): RGB and alpha 1, so the bake's greyscale RGB + alpha 255 is
what the GPU samples; nothing is lost.

## m_bOnlyRenderInEffectsBloomPass (CBaseRendererSource2 +0x23f0)

1802c9f00 / 1802c2470 build the renderer's scene-object layer mask: 9 (1 without +0x2268), | 0x40 (+0x228), | 0x80
(+0x23f0 bloom-only), | 0x1000 (+0x23f1), | 0x800 (+0x23f2), | 0x2000 (+0x23f3 m_bOnlyRenderInEffecsGameOverlay),
| 0x10 (a global +0x58 with +0x1e4 < 0 or +0x220 > 0), | 0x4000 (+0x41b8). client.dll 1811cd6f0 builds the
"Effects Bloom" / "EffectsBloom" layers (strings 0x181d258c0 / 0x181d258d0; layer flag words +0x48 |= 0x401801,
+0x480 |= 0x202). The layer filter matching object bit 0x80 is unread. 1802ca022 (the vertex controls) also picks a
different constant for bloom-only renderers (0x180534228 vs 0x1805341d0): unread.

The layer's targets, from the top of 1811cd6f0: "QuarterResEffectsColor" (string 0x181d25898, 1811cd808) at (render
w >> 2, render h >> 2) (the `(x + (x >> 31 & 3)) >> 2` divides at 1811cd7e3-1811cd7fe), format 9; "QuarterResDepth"
(0x181d24ad0, 1811cd868, format 0x2a) at the same size, filled by 1811d1b10 (unread: the downsample's filter) unless
[+0xa0] says otherwise. bloom_cs D_BLOOM_MODE=1 (`shaderdump dump bloom_cs_vulkan_50_cs.vcs id=0`, file 1, line 114):

    out = clamp(karis13(src) * g_fPreMultiply
                + textureLod(g_tEffectsBloom, bilinear clamp, min(uv, srcScale - g_vInvEffectsBloomDim.xy * 1.5)).rgb
                  * g_fEffectsScale, 0, 65504)      uv = saturate((dst + 0.5) * 2 / srcSize) * srcScale

The port (world/effects-bloom.js): the bloom-only meshes on three layer 7 (the scene pass never draws them), drawn
after the scene into a (w >> 2, h >> 2) half-float target cleared to black, depth-tested against the scene's depth
drawn down point-sampled (from the frame's scene copy when it has one, else a full-size depth blit; a scaled depth
blit is silently refused by ANGLE), each renderer with its own blend; bloom.js's first pass adds it as above with
m_flComputeBloomEffectsScale (default 1). Off with the bloom (the Low preset). Cost while such particles live: ~0.8 ms
a frame GPU-synced (C4 blast, 1305 x 979 render).

## The motion-vector scale (PC c3.xy)

FUN_1802c3250 evaluates m_flMotionVectorScaleU (+0x10a0) and V (+0x1218) (1802c359b / 1802c35c3, 1802bdf60 the input
evaluator) into locals; 1802c4a4a then, when the renderer has a motion texture (+0x2c68: 1802bfc80(this, .., 6), the
ANIMMOTIONVEC group's texture, set in 1802bfd40 at 1802c05aa) and at least one layer:

    desc_m = render device vfn 0x2c8(+0x2c68)       desc_b = vfn 0x2c8(layer 0's m_hTexture, else +0x2c70)
    PC +0x30 (c3.x) = (float)(int16)desc_m+0x18 * scaleU / (float)(int16)desc_b+0
    PC +0x34 (c3.y) = (float)(int16)desc_m+0x18 * scaleV / (float)(int16)desc_b+2

else both stay 0 (1802c49af). desc +0x18 is the vtex METADATA block's int16 at byte 6 (VRF
MotionVectorsMaxDistance, signed texels): explosion_fireball(_large)_01_motion -1, explosion_blast / burst -7,
fire_small_sim_a_mv -64, fire_gas_batch_b_top_mv_v2 -32, sparks_burst_mv -140, smokeloop_i_0_flw 64. The port had 1:
each frame's UV moved by up to the whole sheet, sampling other frames (the noisy, broken fire). The bake writes
`motionVecMax` per texture (ParticleBake.cs); an index without it gives 0 (no warp).

## The 1D colour lookup layer's UV, and the trail combo (2026-11-16)

Read for molotov_groundfire_outline.vpcf's edge flames (C_OP_RenderTrails: fire_small_sim_b_desat, a 1D_COLOR_LOOKUP
gradient, an ANIMMOTIONVEC group), which drew white with purple fringes. Dumps from the live game's
shaders_vulkan_dir.vpk (2026-11-16) with ShaderDump (above; an `extract <vpk> <substring> <outdir>` mode added in a
scratch copy, net10.0 for VRF 20.1.7467): `combos` lists the trail combos; VS s16 (S_DRAW_AS_TRAIL), s144 (+ 1 layer),
s176 (+ S_MOTION_VECTORS + 1 layer); PS s1536 (trail + 1 layer), s1568 (+ motion). So trail combos with layers and
with motion vectors exist (the port said none were dumped).

**The lookup's UV is not a texture coordinate.** In every VS combo (sprite s128 and trail s144 / s176 alike), a layer
whose own sheet is absent (the vertex controls' vec2 _m9.y for layer 0, _m10.y for layer 1, <= 0) and whose type
(PC c19.y >> (16 + 3k) & 15, read in the VS from SpriteCardPixelControls_t._m0.y) is 2 gets, in place of the corner
UV (s144 layer 0: 196-330, layer 1: 1361-1775; the sheet branch's 2700 / 4032 repeat it):

    s0..s3 = four per-particle scale sources (switch 1-13 over TEXCOORD1 / COLOR0 / TEXCOORD4.w / TEXCOORD7 and the
             seed hashes; 1 for NONE), picked by nibbles of VC _m11.x (>> 16k) and VC_c4.x (>> 5k) / .y (>> 4k) /
             .z (>> 12 + 4k): which nibble feeds which s is not pinned down here
    o  = VC_c(5+k).xy * (s1, s2) + (VC_c4.x >> 5k bit 4 ? fract(TEXCOORD1.x * (51.48, 38.11)) : 0)   (layer 1's hashes)
    uv = (o.x, o.y / (VC_c(5+k).w * s0), 1 / (VC_c(5+k).z * s0), s3)

and the PS (ps_s1024:870 sprite, ps_s1536:984 trail, identical) reads the gradient at
((lum709(srgb(q.rgb)) + uv.x) * uv.z, uv.y). So the gradient sits at the texel's luminance, moved by the offset and
divided by the scale. The port fed the layer's corner / strip UV: the lookup was moved by U (0..1), so a trail went
to the gradient's white end with the low-U edge in its blue / purple stops (0.40 / 0.50); a sprite's lookup also
drifted by its corner U. Port: spritecard.js efxLookupUV / efxSpriteUV (sprites) and MESH_VS (ropes, trails); scale
sources NONE and the randomize bit 0, as controls.js packs neither.

## The trail combo (2026-11-16, ported)

Ropes and trails both draw with it (S_DRAW_AS_TRAIL: particles.dll sets bit 1 of the combo word at 1802d7675 for
trails, 1802db425 for ropes). Combos read: VS s144 (1 extra layer), s176 (+ S_MOTION_VECTORS), s304 (2 extra layers
+ motion), s128 / s160 the sprite equivalents; PS s1536, s1568 (+ motion), s2592 (2 extra layers + motion), s1024 /
s1056 the sprite equivalents. There is no motion combo with 3 extra layers (sprite or trail). The SpriteCardPixelControls_t
cbuffer in these dumps is `vec4 _m0.._m7; uvec2 _m8; uint _m9`: _m8 = PC c19.xy, _m9 = the flag word c19.z.

**The VS** bends a Catmull-Rom of four points (TEXCOORD3-6, radius in .w) at t = TEXCOORD0.y x 0.5 + 0.5
(s144:5262-5294). The port tessellates that on the CPU (ropes.js, trails.js) and MESH_VS takes each vertex's results:
- the corner: _23160 from TEXCOORD0 and the crop TEXCOORD8; `_20211` is it with y replaced by the rope's V,
  (mix(T2.z, T7.x, t) + VC_c3.z) x VC_c3.w when VC_c3.w > 0 (s144:181-182). The sheet path uses _23160 and its zoom
  lerp is `* 1.0` (s176:2685: no zoom on a trail); the no-sheet path and every layer past the base use _20211
  through efxLayerUV's no-sheet formula (s144:2184-2406, rotation VC_c7.x).
- the width w = the Catmull-Rom of the four radii (_16109, s144:5294), before the screen-size clamp (that clamp
  makes the position's width _11937 from it: s176:5714-5720).
- unless ALPHA_REFERENCE (flag 0x40000, s144:5298), every layer UV's x and z are multiplied by w (s144:5512-5524,
  s304:8171-8183: base, layer 1, layer 2) and output_4 = (base blend, layer-1 blend, 1, w); with it the UVs stay
  and output_4.zw = (1 - s, s') from two scale sources (the alpha reference, not ported: controls.js reports it).
- output_4.x = the base sheet's blend, -1 without; .y = layer 1's: its own sheet's blend, else 0 when the base has a
  sheet (s176:2688 `_23767.y = 0.0`; sprites the same: s128 / s160:2918), -1 with no sheet at all.
- the motion UVs (output_6 on s176): without a sheet the base layer's UV (s176:2519), with one the motion
  texture's own sheet frames (its rows VC _m11) through the same corner and the base layer's offset / scale
  (s176:3859-4017, 5349), never multiplied by w.

**The PS:**
- (ps_s1536:85-92, 215-220, s2592 layer 2) `tw = mix(1 / input_4.w, 1, flag & 0x40000)`; each layer's x and z times
  tw: with the VS's multiply, U and the second frame's U interpolate projectively across a tapered quad (a texture is
  not sheared along the quad's diagonal). Layer 2 reads only xy (s2592).
- the samplers (ps_s1536:94-108): layer k's m_bClampUVs (PC c3.z bit k) clamps U and V; else flag 0x4000
  (F_ADDRESS_V_CLAMP) samples `AddressV_Clamp_Filter_MinMagMipLinear` (V clamped, U wrapping); else both wrap (the
  D3D default). The gradient strip of a 1D lookup goes through the same sampler (ps_s1536:990-998).
- motion (ps_s1568:93-157, 283-299; PSM:85-268 for sprites): only with flag 0x8000 (a sheet); the two motion
  texels are fetched once, at input_6.xy / .zw, with layer 0's sampler, and only when input_4.x > -1; otherwise
  they are 0. Then the base UV = (xy - (m0.yw x 2 - 1) x PC_c3.xy x input_4.x, zw + (m1.yw x 2 - 1) x PC_c3.xy x
  (1 - input_4.x)) and layer 1's the same with input_4.y when it is > -1 (so with only the base sheeted, layer 1's
  zw move by the whole m1 term). Every type reads the moved UV: the frame fetches, the 1D lookup's x / z
  (ps_s1568:1064, so its scale moves with the motion texture), the zoom types, the distortions' base UV (PSM:427).
  Layers 2-3 have no warp or second frame on a trail.

**F_ADDRESS_V_CLAMP** (string 0x1805209a0): `or [flags + 8], 0x4000` when the renderer's m_bClampV is set: trails
at 1802d769c (CBaseTrailRenderer +0x3350, schema entry 0x1805c5a10, read at 1802d767d in 1802d74d0), ropes at
1802db44c (C_OP_RenderRopes +0x34ec, entry 0x1805c66b0, read at 1802db42d in 1802db280); off the procedural path the
same bit goes through FUN 180424070 with the string's hash.

**The vertex time** (the T1.z the VS runs the sheet at; the sprite VS likewise). 18032a2c0 picks a sort / fill
template by the animation type (r9d 0 / 1 / 2, also by whether the sort is wanted: 180344530 / 180346430 /
1803483b0 sorted, 18034a320 / 18034c1c0 / 18034e0c0 unsorted, ...); each writes the particle's time at its 4-wide
record's +0x88: FIXED_RATE the age (180344eb8), FIT_LIFETIME age / lifetime masked to 0 where the lifetime is <= 0
(180346dde: `cmpltps`, `divps`, `andps`), MANUAL_FRAMES attribute 38's stream (collection +0x408 = +0x2d8 + 38 x 8,
loaded at 180348778) unchanged (180348d6b). The VS treats all three alike at VC_c1.w (1 for MANUAL_FRAMES), so a
manual value is a sequence position, fraction and all: every baked MANUAL_FRAMES renderer (106, none with
m_bAnimateInFPS) sets it from a curve over the normalized age, 0..1 a whole run. The port had floored it as a frame
index (a rule from the fork's Source 1 trainer, never traced), so impacts, molotov / incendiary explosions and the
ground fire held frame 0. Port: basis.js sampleSheet. UNSETTLED: cosmo's hp_bar.vpcf (scripts-cosmo.js sends 0..16)
is not baked here to check how it reads under this rule.

## Texture size

The particle textures are baked at the vtex's own size up to 4096 (ParticleBake.cs TopSide; it was 1024, so the
explosion flipbooks' 256 px frames came out 64 px), with `t2048/` / `t1024/` copies below it (the index entry's
`tiers`). fx/effects.js picks one by the texture quality as the player models do (Low 1024, Medium 2048, High own).
The sides are ours: CS2's texture detail drops mips by its streaming budget (TODO(trace), as BAKING.md "Texture tiers").

## Unread

What +0x2c70 holds (the base texture when layer 0 has none: the port gives 0), whether the render device
rewrites desc +0x18 at load. Which scale-source nibble feeds which term of the lookup UV. A layer's own sheet on a
rope / trail (the combo's layer-1 sheet rows: the port reads the strip's corner; controls.js reports it). The rope
V's TEXCOORD2.z / 7.x on a trail (the trail writer's; a trail's V is its streak, 0..1). How the 3-layer trail combo's
layers 2-3 blend frames (s2592 shows none). Layers 2-3's blend weight on a sprite under a base sheet (s256 / s384 not
read; the port keeps -1).
