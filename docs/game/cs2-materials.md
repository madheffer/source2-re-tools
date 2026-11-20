# World material shaders

shaders_vulkan_dir.vpk (CS2 of 2026-11-18 / 2026-11-19), dumped as SPIRV-Cross GLSL per combo, with VRF's .vfx reconstruction and the `_vars.json` variable tables; scenesystem.dll for the lighting constants. What each compiled world shader computes for a material (albedo, normal, roughness, metalness, AO) and where it hands that to the lighting. Line numbers are in the named dump file.

## Functions

| Address | Module | What |
|---|---|---|
| ~0x1801af7b0 | scenesystem | the per-view lighting constants' fill; writes `_m5` at 0x1801af964 |
| 0x18001118f | scenesystem | registers lb_cubemap_normalization_max |
| 0x18001123f | scenesystem | registers lb_cubemap_normalization_roughness_begin |

## Constants

| Value | What |
|---|---|
| lb_cubemap_normalization_max | 0x42000000 = 32.0, handle 0x180923bd0, flags 7 |
| lb_cubemap_normalization_roughness_begin | 0x3DCCCCCD = 0.1, handle 0x180923be0, flags 7 |
| 1.0 (0x1805fff70) | xmm13, loaded at 0x1801af849 |
| r_csgo_cubemap_normalization | client, default 1, handle 0x1825e7f20 (not followed) |
| g_flReflectance | `pow((1.5-1)/(1.5+1),2)` = 0.04 |
| (0.2125, 0.7154, 0.0721) | luma weights in the cubemap normalisation |
| 1.00392163 | hemi-octahedral normal decode bias |
| 1.99215686 | detail texture scale |
| sRGB decode | `c <= 0.04045 ? c x 0.0773993805 : pow(c x 0.947867334 + 0.0521327034, 2.4)` |

## Reading a shader

- `--combo` picks one static + dynamic combo (every other combo value 0); the file is `<shader>_PixelShader_s<static id>_d<dynamic index>.glsl`. Without it: tens of thousands of programs.
- `<shader>.vfx` lists the features, the static / dynamic combos and their rules, and the variables; `<shader>_vars.json` is the variable table the game evaluates.
- `_NNNN` names are SPIR-V ids: they change between combos (stable for one expression across combos, a merged value's id is not). Diff a combo against the base with `_\d+` -> `_N` to see what a feature adds.
- A dump's struct members are `_mN` by position after dead members are stripped: `PerViewConstantBuffer_t._m0` isn't one thing across programs (map by type and use).
- The pixel program holds the whole forward pass (lightmaps, barn lights, shadows, fog): the material is its first ~100 lines after `main()` and the lines feeding the final sum.
- `StaticComboRule( Allow1( A, B ) )`: the material system's resolution of a material setting several is untraced (csgo_vertexlitgeneric's F_DECAL_TEXTURE + F_FORCE_UV2: 22 materials).
- The `mat/shaders/<shader>.json` tables are CS2's, not the map's: CS2's update of 2026-11-18 changed them (one variable fewer, sampler states as expressions).

## Where the material meets the lighting (statement shapes)

| Value | Shape |
|---|---|
| F0 (every program with a specular term) | `vec3 _N = mix(vec3(<reflectance>).xyz, <albedo>.xyz, vec3(<metalness>))[.xyz * ..];` |
| lit colour without F0 (csgo_vertexlitgeneric / csgo_lightmappedgeneric base) | `vec3 _N = (<direct>.xyz + (<baked>.xyz * vec3(<view occlusion> * <AO>).xyz).xyz) * (<albedo>.xyz * (1.0 - <metalness>)).xyz;` (the occlusion is the product, the AO sample's `.x` alone, or the view's term alone in a translucent program, which reads no AO) |
| roughness | `vec2 _N = max(<r>.xy, vec2(pow(saturate(max(dot(dNdx, dNdx), dot(dNdy, dNdy))), 0.333)))` |
| shading normal | `vec3 _N = mix(<glint normal or vec3(1)>, <N>, bvec3(all(..)))` after F0, or N.L of the sun (`dot(PerViewLightingConstantBufferGpu_t._mK.xyz, <N>)`) without F0 |
| AO | `vec3 _N = vec3(<view occlusion> * <AO>).xyz;` |
| alpha | `vec4 _N = vec4(_a, _b.yz, <alpha>);` (the output before the fog) |
| self-illumination | `vec3 _N = _lit.xyz + mix(e, e * albedo, vec3(g_flSelfIllumAlbedoFactor)).xyz;` |
| csgo_weapon diffuse | `vec3 _N = (_a.xyz + _b.xyz) * <diffuse>.xyz;` (S_STICKERS: `vec4 _N = vec4(_a * <diffuse>.xyz, <alpha>);`) |
| csgo_weapon specular | `vec3 _N = <spec> + ((vec3(1.0) - <spec>) * vec3(0.047619..));` |
| csgo_static_overlay unlit | `vec4 _N = vec4(_a, <rgb>.yz, <alpha>);`; S_BLEND_EFFECTS's lit F0 `mix(vec3(r).xyz, <albedo>, vec3(m))` (no `.xyz` on the albedo) |

Vertex inputs: `vTexCoord` / `vTexCoord2` / `vBlendColorTint` / `vColorBlendValues`; the instance's colour bytes are sRGB, decoded by the vertex program itself. `PerViewConstantBuffer_t` members by type: float the time, vec3 the camera position.

## View and per-frame state the programs read

- Wetness (csgo_environment / _blend F_WETNESS: puddles, wet darkening, ripples, rain drops) runs on `g_bWetness` and the view's rain state (PerViewConstantBufferCsgo_t members, untraced); with that zero it changes nothing.
- Fire scorching (csgo_environment, csgo_complex and others: inferno burn marks near a surface) reads `FireConstantBufferCsgo_t` (a count and flags).
- PerViewConstantBufferCsgo_t also gives the camera-relative origin, `_m3.w` (the bitangent flip; what sets it unread), the snow layer's view texture, and flag words `_mK` (csgo_environment S_PARALLAX_OCCLUSION + S_PIXEL_DEPTH_OFFSET: `notEqual(PerViewConstantBufferCsgo_t._mK, ivec4(0))` switches a contact-AO pass that reads the scene's depth).
- csgo_vertexlitgeneric's vertex program has no file for S_SHADER_QUALITY (static 64); static 0 + the features is the plain one.
- Alpha test: csgo_environment / csgo_complex write alpha 1 with no discard (the test is elsewhere: a depth pre-pass or alpha-to-coverage, unread); csgo_lightmappedgeneric has its own `discard`.
- F_ADDITIVE_BLEND: the .vfx lists no blend state.
- F_TRANSMISSIVE_BACKFACE_NDOTL, cloth shading and anisotropic gloss change the lighting, not the material values.

## csgo_environment_blend

Two blend formulas (S_USE_NEW_BLENDING is another program, not a branch), three layers, border / bevel effects per layer, detail normals, a shared colour overlay, snow, biplanar mapping and wetness, in 35 combinations in use.

## csgo_environment S_PARALLAX_OCCLUSION + S_PIXEL_DEPTH_OFFSET (ze_dark_souls)

The parallax march is in the material part; the depth offset (`gl_FragDepth`) is written after the lighting; the view flag words switch a contact-AO pass.

## csgo_weapon (weapon models placed in a map)

- Hands the lighting a diffuse and a specular colour (the metalness folded in with the paint's wear), not albedo + metalness.
- The iridescent paint reads the sun's direction inside the material (`PerViewLightingConstantBufferGpu_t._mK.xyz`).
- The vertex program projects in object space (`vPositionOs` / `vNormalOs`, Source's axes and inches) and multiplies by the view-projection (Vulkan clip space).
- Its one `discard` is the view's dithered fade near the camera.
- Stickers: the sticker textures are the game's to bind; a placed weapon names the default ones with every `g_bEnableSticker` 0. Each slot k runs under `if (_Globals_.g_bEnableSticker<k> != 0) _b = true; else _b = _Globals_.g_bStickerPreviewForceOn != 0; if (_b) { ..~700 lines.. }` (csgo_weapon_PixelShader_s512_d3.glsl line 642 for slot 0, the others every ~712 lines), inside `if (g_tStickerWepInputs.x > 0 && vTexCoord2.z > -1)`. With both 0 what is left is the slots' else values copied through (and one g_tStickerWepInputs fetch). The S_STICKERS programs are ~150 KB of GLSL (five sticker slots' code), 30 samplers.

## csgo_static_overlay

- Lit as csgo_complex. After the fog each blend mode ends with `rgb = mix(neutral, rgb, alpha)`: Mod2x (3) 0.5, Multiply (5) 1.0, ModThenAdd (6) 0.0; modes 1 and 4 write rgb and alpha as they are.
- Render states (.vfx): BlendEnable, DstBlend `F_BLEND_MODE == 3 ? One : InvSrcAlpha` (SrcBlend not listed), DepthBias -64, DepthWriteEnable false, stencil NotEqual ref 3 read mask 1 write mask 254. F_BLEND_MODE 0..6 = Opaque, Translucent, Alpha Test, Mod2x, Additive, Multiply, ModThenAdd.
- Pixel static combos: S_MATERIAL_REFERENCE, S_BLEND_MODE (0..6), S_LIT, S_BLEND_EFFECTS, S_TINT_MASK, S_SHADER_QUALITY, S_MODE_TOOLS_VIS; rule `Requires(S_LIT==1, S_BLEND_MODE...)`. Read: 128 (S_BLEND_MODE=1, S_LIT, quality, lightmap: dynamic index 3), 130 (S_BLEND_MODE=2, S_LIT), 114 (S_BLEND_MODE=1 unlit, dynamic 0), 118 (S_BLEND_MODE=3 unlit); vertex static 44 (S_PAINT_VERTEX_COLORS). `S_SHADER_QUALITY=1,D_BAKED_LIGHTING_FROM_LIGHTMAP=1` (pixel static 112, dynamic 8) has only a vertex program.
- In 30 maps (842 materials): lit mode 1 501, unlit mode 3 147, lit mode 2 93, unlit mode 1 64, mode 6 23, mode 4 5, mode 0 4, mode 5 1.
- Vertex: UV through g_vTexCoordXform0 / 1 + scroll; colour (rgba) = (mix(1, instance tint, g_flModelTintAmount) x g_vColorTint, instance alpha), x vBlendColorTint (VertexPaintTintColor, rgba) with S_PAINT_VERTEX_COLORS unless all four components are 0; g_flOverlayLift > 0 lifts the vertex along the normal (`x 1.5 / max(dot(N, view), 0.3)`).
- Lit (128): c `_7787` = g_tColor.rgb x colour.rgb; albedo = (vec4(c, 1) x g_mTextureColorAdjust).rgb, and with bAutomaticPBRColorFitting (F_AUTOMATIC_PBR_COLOR_FITTING) the fit of lines 290-296 (g_vAlbedoLevels, g_vMetallicAlbedoLevels, g_vDarkMetallicAlbedoLevels). Metalness g_tMetalness.g, AO g_tAmbientOcclusion.r on the lightmap term, normal decoded with Y negated and XY x g_fTextureNormalContrast, roughness `max(saturate(((b - 0.5) x g_fTextureRoughnessContrast + 0.5) x g_fTextureRoughnessBrightness), the geometric floor)`, self-illum as csgo_complex's with c as the albedo. Line 1009: alpha = `colour.a x (g_tColor.a x g_flOpacityScale)`. g_bSnow changes the lightmap term (line 1003): unread.
- Lit alpha test (130): a = g_tColor.a x colour.a; discarded where `a - g_flAlphaTestReference - 0.001 < 0` (or the anti-aliased edge, as csgo_lightmappedgeneric's).
- Unlit (114): rgb = `(vec4(g_tColor.rgb, 1) x g_mTextureColorAdjust).rgb x colour.rgb`, alpha as above, then fog.
- Unlit Mod2x (118): the same, then `rgb = mix(0.5, rgb, alpha)` (a view flag adds a fitted branch, line 110: unread).

## generic.vfx (130 materials)

- Textures bound by name, not bindless: `sampler2D(g_tColor, g_sTrilinearWrap)`.
- Without S_SPECULAR: lit colour = `(direct + baked [x the view's occlusion]) x ((g_tColor.rgb x g_vColorTint) x the vertex colour)` (PixelShader_s0_d3 line 857; S_TRANSLUCENT's s16 line 787 without the occlusion): no metalness, no AO texture. g_vColorTint has no expression in this shader's table.
- S_SPECULAR (s1): F0 = `mix(g_tMetalnessReflectanceFresnel.y x g_vReflectanceScaleAndBias.x + .y, albedo, g_tMetalnessReflectanceFresnel.x x g_vMetalnessScaleAndBias.x + .y)` (line 318); roughness `min(1, ((r.z + r.w) / 2) x g_vRoughnessScaleAndBias.x + .y + (r.x + r.y) / 2)` of g_tRoughness, then the geometric floor (line 325).
- S_TRANSLUCENT alpha: `vertex alpha x g_tColor.a x g_flOpacityScale` (line 789). S_UNLIT (s2_d0): the vec4 before the fog, (g_tColor.rgb x g_vColorTint x the vertex colour, its alpha).
- Base (pixel static 0 / dynamic 3, vertex static 0): vertex output_2 = the UV twice; output_3 = the instance colour (sRGB -> linear) with its alpha. Pixel: `xy = g_tNormal.ag x 2 - 1`, `n = (x, -y, sqrt(saturate(1 - x^2 - y^2)))`, n.xy x g_flBumpStrength, normalised, Y negated again unless a flipped back face; line 677: diffuse = `(direct + lightmap x the view's occlusion) x (g_tColor.rgb x g_vColorTint) x the instance colour`.
- Vertex programs: the one the dump names for D_BAKED_LIGHTING_FROM_LIGHTMAP (VertexShader s0_d3) decodes the frame from nPackedFrame (`normalize(vec4(_N.xyz, 0) x transform)`) and has no lightmap UV output, one fewer than the lightmapped pixel program reads; the one named for D_BAKED_LIGHTING_FROM_PROBE (s0_d2: vNormalOs, vTangentUOs_flTangentVSign, vLightmapUV) is its partner by interface. Why the dump's index differs for this shader: untraced.
- Programs in use: p0_v0d2, p1_v1d2, p16_v0d2, p17_v1d2, p2_v2.

## csgo_unlitgeneric

4 combinations: its colour is what `output_0` is set to; the fog's alpha fade switched by the view's flag words ([skybox.md](skybox.md)).

## csgo_glass (97 materials)

Pixel static 16 (S_SHADER_QUALITY), dynamic 0, 1,022 lines; vertex static 0 (output_2 = the UV twice, output_3 = the instance colour rgba, linear).

- o `_6671` = `saturate(g_tGlassDust.a x input_3.a) x (g_flTranslucencyRemap.y - .x) + g_flTranslucencyRemap.x`.
- t `_20059` = `g_tGlassTintColor.rgb x mix(1, input_3.rgb, g_flModelTintAmount)`.
- Normal as csgo_complex's; roughness `_11004` = max(g_tNormal.b x input_3.a, the geometric floor).
- Line 919: L `_20321` = `the direct diffuse + the ambient x (1 - the specular terms) + _13137 x (g_tGlassTintColor.a x o)`. Line 920: `_6860` = `o x g_tGlassDust.rgb x L`.
- `_8674` (through) = `(1 - mix(0.04, 1, pow(1 - max(0, V.N), 5))) x pow(t, 1 / max(0.01, sqrt(1 - 0.4444444 x (1 - (V.Ng)^2)))) x (1 - o)`, N the shading normal, Ng the geometric one.
- Line 946: rgb = `_6860 + the specular terms + through x o x g_tGlassDust.rgb x L x pow(t, 1.6)`; then fog (which also scales `through` by 1 - the fog amount); line 824: output = (rgb, luminance(through)).
- Render states: the stencil test only (NotEqual 3, read mask 1), depth as F_DISABLE_Z_BUFFERING says; no blend state. Both textures sRGB reads.

F_OPAQUE_CUBEMAP_REFRACTION: pixel static 18 (`S_SHADER_QUALITY=1,S_OPAQUE_CUBEMAP_REFRACTION=1`, 1,195 lines), vertex static 2. Lines up to the lit colour are static 16's (its line 1013 = line 946 above). Then, opaque:

1. r `_16734` = `mix(g_flRefractMinRoughness, 1, dot(_15134.xy, 0.5))`, `_15134` = g_tNormal.zz x the vertex alpha (the raw roughness, no geometric floor) (line 1086).
2. Ray `_24296` = `refract(normalize(pos - camera), N, 0.66)` (lines 293, 1087); the "dominant direction" mix after it mixes the ray with itself (no change); mip `_12665` = `PerViewLightingConstantBufferGpu_t._m14.y x sqrt(r)`.
3. The cubemap volumes walked as the reflection's (lines 1104-1188: box fade, smoothstep weight, box parallax mixed back by r, the volume's own SH `_m7` gathered).
4. output_0 = `(lit + _8674 x env / total x min(luma(probe light) / dot((ray, 1), SH / total), max(r x _m4.x + _m4.y, 1)), 1)` (line 1192). `_m4`: unread.

## sky_occluder

"Sky occluder - writes depth to hide the world". `Depth("csgo_depth_only.vfx")`, PS dynamic combo D_SKY_OCCLUDER_PASS 0..3, `output_0 = vec4(g_tColor.rgb, 1)` in every pass, but every pass's RenderTargetWriteMask[0] is None (sky_occluder_states.txt lines 100, 211, 322, 433): no colour written.

| Pass | States |
|---|---|
| 0 | depth test LessEqual, no depth write, stencil write mask 128, DecrSat on pass |
| 1 | depth write, DepthFunc Always, stencil Equal (read 128, write 128) Replace |
| 2, 3 | depth write LessEqual, no stencil |

StencilRef 128, CullMode Back. The world behind it is hidden and the sky shows there. Material toolsskybox_occluder. ze_dark_souls: 16 occluder panels boxing two areas, x 3340..5100 / y 280..3048 and x -116..4384 / y 5318..12176. Unread: the stencil passes' order in the frame; whether depth-only mode puts it in the shadow map.

## csgo_textile_layer

Probe lit, no lightmap combo (PixelShader_s0_d0, S_SHADER_QUALITY=1, 1,344 lines). Hands the lighting a specular colour:

- F0 `_17639` = `mix(_18402, albedo _11121, metal)` (line 523); `_18402` is g_flReflectance or, with g_bClothShading, the sheen colour `mix(R, saturate(sqrt(albedo) x g_flSheenScale), cloth)` (line 517).
- Diffuse colour = albedo x (1 - metal) (line 1260, `(_11121 * _12929)`); AO `_13436` (line 1259, x the view's dynamic AO `_21711`).
- Cloth shading: each light's specular lobe is a sheen distribution `(2 + 1/a) x pow(1 - NdotH², 0.5/a) / (4 (NL + NV - NL NV))` mixed in by the cloth amount (lines 768-781 and 1084-1095), and the ambient specular too (lines 1118-1120, 1243-1249). g_bClothShading = F_CLOTH_SHADING || F_BACKWARDS_COMPATIBILITY. de_boulder's leather02 sets neither.
- The view's dynamic AO switch: `if (_24465.x)` on an all-false flag vector (the same dead branch in csgo_lightmappedgeneric p6336 and csgo_static_overlay programs: their anti-aliased alpha test behind `bvec4(false).z`).

## csgo_simple_liquid

de_fachwerk's wine bottle liquid (models/generic/winebottle_kit_01/wine_bottle_02_a_dusty_liquid, 156 triangles). Not a background refraction: D_USE_BGREFRACT `Requires(S_OPAQUE_REFRACT)`, which it doesn't set. Its only pixel program with no feature is PixelShader_s0_d0 (no baked lighting, 2,349 lines; d32 for the probe combo is not in the vcs): one program lights two layers itself, a frosted glass shell (g_tFrost, lines 760-930) and the liquid inside (level, wobble, back fade, its own specular strengths 15.2 / 13.3, line 2343), reading the sun (PerViewLightingConstantBufferGpu_t _m18 / _m19), the cubemap volumes (_m16, lines 2250-2290), the BRDF lookup texture (g_tBRDFLookup) and the barn lights. It hands no single material to the lighting.

## Cubemap normalisation

The lighting half of the forward programs (csgo_complex_PixelShader_s5120_d3.glsl, S_SHADER_QUALITY=1, lines 1150-1236; the same shape in the other world shaders):

- The cube loop walks the view's envmap list (PerViewLightingConstantBufferGpu_t._m15._m0[i]: _m0 world-to-box matrix, _m1 / _m3 the box corners, _m5 the edge fade scale, _m4 the cube array slice, _m2 the array layer, _m6 a colour scale, _m7 the cube's baked SH (vec4 a channel)); weight = smoothstep of the box edge distance x (1 - weight so far), stops past 0.99; the lookup direction parallax-corrected and mixed toward the plain reflection by roughness.
- Specular indirect = `(sum env / total weight) x min(dot(lightmap diffuse, (0.2125, 0.7154, 0.0721)) / dot(vec4(N, 1), sum SH / total weight), max(roughness x PerViewLightingConstantBufferGpu_t._m5.x + _m5.y, 1.0))` x the BRDF lookup's split sum x the view occlusion x AO. roughness = `_17751 = dot(_11004.xy, 0.5)`, the geometric-floored roughness (line 484) averaged over its two axes.
- `_m5` (0x1801af964): `slope = (lb_cubemap_normalization_max - 1) / (1 - lb_cubemap_normalization_roughness_begin)` -> [rbp+0x30] (_m5.x), `max - slope` -> [rbp+0x34] (_m5.y).
- So the cap is 1 up to roughness 0.1 and rises to 32 at roughness 1: a rough surface's reflection is brightened to the lightmap's light, not only darkened. de_vertigo's metal elevator door (roughness 0.45, cap 13) draws 63 / 255 in CS2.
- Unread: `_m7`'s contents per cube (what scenesystem puts there), the loop's cube order (findLSB over the cull bit words), the `_m6` colour scale, the view's other `_m5` uses.

## csgo_complex (2,543 materials, 33.7M triangles in 30 maps)

Pixel static combos: S_MODE_TOOLS_VIS, S_DETAIL_TEXTURE, S_SECONDARY_UV, S_ANISOTROPIC_GLOSS, S_ALPHA_TEST, S_TRANSLUCENT, S_ADDITIVE_BLEND, S_SELF_ILLUM, S_TINT_MASK, S_METALNESS_TEXTURE, S_DECAL_TEXTURE, S_SHADER_QUALITY, S_TRANSMISSIVE_BACKFACE_NDOTL (each `StaticCombo(S_X, F_X)`). The .vfx declares no F_SPECULAR, F_SPECULAR_CUBE_MAP, F_HIGH_QUALITY_GLOSS, F_DIFFUSE_WRAP or F_PREPASS_ALPHA_TEST (vmats carry them; nothing reads them). Ids with S_SHADER_QUALITY=1 and D_BAKED_LIGHTING_FROM_LIGHTMAP=1 (dynamic index 3):

| Static id | Combo |
|---|---|
| 5120 | base |
| 5760 | S_TINT_MASK |
| 6400 | S_METALNESS_TEXTURE |
| 5160 | S_ALPHA_TEST |
| 5440 | S_SELF_ILLUM |
| 5130 | S_SECONDARY_UV |
| 5122 | S_DETAIL_TEXTURE |
| 5200 | S_TRANSLUCENT |

Vertex program (static 0, dynamic 8), `_Globals_`: g_vTexCoordXform0, g_vTexCoordXform1, g_vTexCoordScrollSpeed, g_vColorTint, g_flModelTintAmount.

- UV (output_2.xy) = `(dot(uv, Xform0.xy) + Xform0.w, dot(uv, Xform1.xy) + Xform1.w) + g_vTexCoordScrollSpeed x time` (PerViewConstantBuffer_t._m1). output_2.zw: the second UV set with S_SECONDARY_UV.
- Colour (output_4) = `vec4(mix(1, instance tint, g_flModelTintAmount) x g_vColorTint, instance alpha x instance._m7)`; the instance tint is the instance buffer's RGBA8 (`_m0`), sRGB -> linear per channel.
- Normal (output_1) = normalize(normal x the instance's transform); output_5 its centroid copy; output_6 the tangent with its sign in w.

Pixel, base (5120), in file order:

1. `_21709` = the vertex normal: output_5 (centroid) where `dot(input_1, input_1) >= 1.01`, else input_1.
2. `_12885` = `g_bRenderBackfaceNormals != 0 && g_bDontFlipBackfaceNormals == 0`; `_24347` = normalize(`_21709` x (front facing ? 1 : -1) when `_12885`): the geometric normal.
3. Samples: g_tColor (sampler g_sUserConfigAllowGlobalMipBias), g_tAmbientOcclusion and g_tNormal (g_sUserConfig), all at input_2.xy.
4. Normal: `a = (r + g) - 1.00392163; b = r - g; n = normalize(a, b, (1 - |a|) - |b|)` (hemi-octahedral). `_24327` = `_12885` && !front facing. N = input_1 x (`_24327` ? -1 : 1) (not renormalised); B = cross(N, T) x (T.w > 0 ? 1 : -1), negated when `PerViewConstantBufferCsgo_t._m3.w != 0`; n.y negated unless `_24327`; world normal = `normalize(T x n.x + B x n.y + N x n.z)`.
5. Albedo `_14202` = g_tColor.rgb x input_4.rgb.
6. F0 `_12351` = mix(g_flReflectance, albedo, g_flMetalness).
7. Roughness `_11004` = `max(g_tNormal.bb, pow(saturate(max(dot(dFdx(G), dFdx(G)), dot(dFdy(G), dFdy(G)))), 0.333))`, G = `_24347` (a vec2: both anisotropy axes the same in this combo).
8. Lines 1070-1073: `_13436` = `_21712` (the view's ambient occlusion) x g_tAmbientOcclusion.r; diffuse = `(direct diffuse + lightmap irradiance x (1 - the specular terms) x _13436) x albedo x (1 - metalness)`; output alpha = input_4.w.

Features:

- S_TINT_MASK (5760): `_14202 = mix(c, c x input_4.rgb, g_tTintMask.r)`, the mask at input_2.xy (g_sUserConfig).
- S_METALNESS_TEXTURE (6400): metalness `_10391` = g_tColor.a, in the F0 mix and the diffuse's (1 - metalness).
- S_ALPHA_TEST (5160): only the output's alpha = 1.0; no discard.
- S_SELF_ILLUM (5440; csgo_vertexlitgeneric 3072): `e = g_tSelfIllumMask.rgb(colour UV + fract(g_vSelfIllumScrollSpeed x time)) x g_vSelfIllumTintScaled`; output += `mix(e, e x albedo, g_flSelfIllumAlbedoFactor)`. g_vSelfIllumTintScaled = `pow(2, g_flSelfIllumBrightness) x g_flSelfIllumScale x SrgbGammaToLinear(g_vSelfIllumTint)`. The mask is an sRGB read.
- S_SECONDARY_UV (5130): g_tAmbientOcclusion at input_2.zw when g_bUseSecondaryUvForAmbientOcclusion != 0 (default 1); the table also has g_bUseSecondaryUvForTintMask (0), ...ForDetailMask (1), ...ForDecal (1), ...ForSelfIllum (0), ...ForDetailTexture (1).
- S_DETAIL_TEXTURE (5122 / vertex static 2; csgo_vertexlitgeneric 2064 / vertex static 16): the inputs shift by one (input_0: the detail UV = the vertex program's `(dot(g_vDetailTexCoordXform.xy, uv), dot(g_vDetailTexCoordXform.zw, uv)) + g_vDetailTexCoordOffset`, the vertex's own UV); albedo x= `mix(1, g_tDetail.rgb x 1.99215686, max(g_tDetailMask.r, g_flDetailBlendToFull) x g_flDetailBlendFactor)`, the mask at the colour UV; g_tDetail a linear read. g_vDetailTexCoordXform = scale.xxy x (cos, -sin, sin, cos) of g_flDetailTexCoordRotation.
- S_TRANSLUCENT (5200; vertexlitgeneric 2176): alpha = `the vertex colour's alpha x (g_tColor.a x g_flOpacityScale)`; the lighting also changes (71 lines in vertexlitgeneric's): unread.

Unread: S_ADDITIVE_BLEND, S_ANISOTROPIC_GLOSS, S_DECAL_TEXTURE, S_TRANSMISSIVE_BACKFACE_NDOTL, the cloth and specular features (Features-only), S_PAINT_VERTEX_COLORS (vertex), combos of two features together.

## csgo_simple (805 materials, 5.0M triangles)

Pixel static combos: S_METALNESS_TEXTURE, S_AMBIENT_OCCLUSION_TEXTURE, S_SHADER_QUALITY, S_MODE_TOOLS_VIS; vertex: S_MODE_TOOLS_VIS, S_PAINT_VERTEX_COLORS. With S_SHADER_QUALITY=1 and the lightmap: pixel static 4 (dynamic file index 36), vertex static 0 (dynamic 8).

- Static 4 is csgo_complex's 5120 line for line (ids normalised), the vertex programs too.
- Static 5 (S_METALNESS_TEXTURE): csgo_complex 6400's three lines.
- Static 6 (S_AMBIENT_OCCLUSION_TEXTURE): no line changes (g_tAmbientOcclusion is sampled in every combo; without the feature the texture is the default white).

Unread: S_PAINT_VERTEX_COLORS (vertex).

## csgo_vertexlitgeneric (2,125 materials, 13.0M triangles)

Pixel static combos: S_SPECULAR_DIRECT, S_SPECULAR_INDIRECT, S_FORCE_UV2, S_DECAL_TEXTURE, S_DETAIL_TEXTURE, S_MODE_TOOLS_VIS, S_ALPHA_TEST, S_TRANSLUCENT, S_ADDITIVE_BLEND, S_TINT_MASK, S_SELF_ILLUM, S_SHADER_QUALITY. Ids (quality, lightmap, dynamic index 3): 2048 base, 2051 S_SPECULAR_DIRECT + S_SPECULAR_INDIRECT, 2560 S_TINT_MASK, 2112 S_ALPHA_TEST, 2052 S_FORCE_UV2. The vertex program with S_SHADER_QUALITY=1 (static 64) has no file; static 0 (dynamic 8).

Vertex `_Globals_`: g_vTexCoordXform0 / 1, g_vTexCoordScrollSpeed, g_vColorTint, g_flModelTintAmount, g_vNormalTexCoordXform0 / 1.

- output_3.xy = the UV through g_vTexCoordXform0 / 1 + scroll x time; output_3.zw = the vertex's UV as it is (S_FORCE_UV2, vertex static 4: vTexCoord2, so the AO reads the second UV set).
- output_0 = the UV through g_vNormalTexCoordXform0 / 1 (the normal map's own transform).
- output_5 = the tint, as csgo_complex's output_4.

Pixel, base (2048):

1. Colour `_19680` = g_tColor at input_3.xy; AO `_17476` = g_tAmbientOcclusion.r at input_3.zw; `_21710` = `g_flAmbientOcclusionScale > 0 ? min(mix(1, 2 x ao, scale), 1) : ao`.
2. `_19069` = g_tMetalness at input_3.xy (G the metalness). g_tNormal at input_0.xy, decoded and framed as csgo_complex's.
3. Line 876: diffuse = `(direct diffuse + lightmap irradiance x (the view's occlusion x _21710)) x mix(c, c x input_5.rgb, saturate(g_tColor.a + g_flInverseBlendTint)) x (1 - g_tMetalness.g)`. No specular term; g_tNormal.b unread.
4. g_flInverseBlendTint = `F_NOTINT ? -1 : 1-(F_TINT_MASK ? 1 : 0)`.

Features:

- S_SPECULAR_DIRECT + S_SPECULAR_INDIRECT (2051): F0 `_12351` = mix(g_flReflectance (0.04), albedo, g_tMetalness.g); roughness = csgo_complex's `_11004` from g_tNormal.b; the diffuse line takes csgo_complex's form. Each alone: not dumped.
- S_TINT_MASK (2560): the tint's blend reads g_tTintMask.r (at input_3.xy) in place of g_tColor.a.
- S_ALPHA_TEST (2112): output alpha = 1, nothing else.
- S_FORCE_UV2 (2052): no pixel line changes.

Unread: S_DECAL_TEXTURE, S_ADDITIVE_BLEND.

## csgo_lightmappedgeneric (1,070 materials, 0.8M triangles)

Pixel static combos: S_ALPHA_TEST, S_TRANSLUCENT, S_DETAILBLENDMODE, S_DETAILTEXTURE, S_FANCY_BLENDING, S_LAYERS, S_METALNESS_TEXTURE, S_OVERLAY, S_SPECULAR_DIRECT, S_SPECULAR_INDIRECT, S_TEXTURETRANSFORMS, S_SHADER_QUALITY, S_MODE_TOOLS_VIS. The .vfx declares no F_VERTEX_COLOR. Ids (quality, lightmap, dynamic index 3): 6144 base, 6150 the two specular combos, 6528 S_TRANSLUCENT, 6336 S_ALPHA_TEST, 6240 S_TEXTURETRANSFORMS (unread); S_OVERLAY alone (7680) has no pixel file. Vertex static 0.

- Vertex: output_2 = the vertex's UV twice (xyxy) without S_TEXTURETRANSFORMS; output_4 = `(mix(1, instance tint, g_flModelTintAmount) x g_vColorTint, a x g_flVertexColorOpacityScale)`, a the instance's alpha term.
- Base (6144): g_tColor at input_2.xy (g_sUserConfig), g_tLayer1AmbientOcclusion at input_2.xy (g_sTrilinearWrap), g_tLayer1NormalRoughness at input_2.zw; normal as csgo_complex's. Line 861: diffuse = `(direct + lightmap x (the view's occlusion x AO.r)) x (g_tColor.rgb x g_vLayer1Tint x input_4.rgb) x (1 - g_flMetalness)`. No specular. Alpha = input_4.w.
- Specular (6150): roughness `_16570` = g_tLayer1NormalRoughness.b; with g_bNoSpecularAtFullRoughness (F_NO_SPECULAR_AT_FULL_ROUGHNESS): `r + smoothstep(0.9, 1, r) x 2`; then the geometric floor. F0 = mix(g_flReflectance, albedo, g_flMetalness).
- S_TRANSLUCENT (6528): alpha `_17232` = `input_4.w x ((g_tColor.a x input_4.w) x g_flOpacityScale)`.
- S_ALPHA_TEST (6336): `a = (g_tColor.a x input_4.w) x input_4.w`; the test is in this program: with g_flAntiAliasedEdgeStrength the edge is `mix(saturate(0.5 + (a - ref) / max(fwidth(a), 1e-6)), a, mix(1, saturate(4 x length(fwidth(uv))), strength))`, else `a - g_flAlphaTestReference`.

S_LAYERS + S_FANCY_BLENDING (pixel static 6168 / vertex 24 at quality 1, and Low quality pixel static 24: the same lines):

- .vfx: `Feature( F_FANCY_BLENDING, 0..3 (0="VertexBlend", 1="BlendModulateTexture,rg", 2="NewLayerBlending,g", 3="NewLayerBlending,a") )`, `FeatureRule( Requires( F_FANCY_BLENDING, F_LAYERS==1 ) )`, `StaticCombo( S_FANCY_BLENDING, F_FANCY_BLENDING!=0 )`, `int g_nFancyBlendingMode < Expression(F_FANCY_BLENDING); >` (the mode is a constant, the combo 0 / 1).
- The vertex program passes `vColorBlendValues` through (`output_0 = vColorBlendValues`). Pixel, v = input_0.x, M = g_tBlendModulation at the colour UV (linear, g_sUserConfig):
  - mode 0: w = v; mode 1: `w = smoothstep(max(0, M.g - M.r), min(1, M.g + M.r), v)`;
  - mode 2: `w = smoothstep(max(0, M.g - g_flBlendSoftness), min(1, M.g + g_flBlendSoftness), v)`; mode 3 the same with M.a;
  - modes 2 / 3 tint layer 1 by the border: `albedo1 x mix(1, g_vLayerBorderTint (SrgbGammaToLinear), (1 - |2 x smoothstep(max(0, h - g_flLayerBorderSoftness), min(1, h + g_flLayerBorderSoftness), saturate(v - g_flLayerBorderOffset)) - 1|) x g_flLayerBorderStrength)`, h the modulation value used (M.g / M.a);
  - albedo = `mix(layer 1, g_tLayer2Color x g_vLayer2Tint, w) x the vertex tint`; normals, roughness and AO blend by the same w.

Unread: S_DETAILTEXTURE, S_TEXTURETRANSFORMS, S_METALNESS_TEXTURE, S_OVERLAY's own program.

## csgo_decalmodulate

Pixel static 0, dynamic 0 (85 lines; no pixel file with a baked-lighting combo; `S_SHADER_QUALITY=1,D_BAKED_LIGHTING_FROM_LIGHTMAP=1` (pixel static 0, dynamic 4) has only a vertex program): c = g_tColor (linear, g_sUserConfigAllowGlobalMipBias) x the vertex colour (vec4(1) without S_VERTEX_COLOR); discard where `c.a - g_flAlphaTestReference < 0`; two fog terms scale c.a (PerViewConstantBufferCsgo_t flags `_m0.y`, `_m0.z`); rgb = `mix(0.5, c.rgb, c.a)`. Render states: DepthBias -64, DepthWriteEnable false, stencil NotEqual ref 3 read mask 1 write mask 254; no blend state.

## csgo_simple_2way_blend (58 materials)

Pixel static 2 (quality), vertex static 0. Combos: S_ENABLE_AO, S_ENABLE_TINT_MASKS, S_PAINT_VERTEX_COLORS (vertex). Vertex: output_0 = `(vBlendValues.xyz, max(vBlendValues.w, 0.1))`; UV and colour as csgo_complex's. Pixel: `uvB = uv x g_vTexCoordScale2`; mask `_16038` = g_tMask.r at uvB (g_sTrilinearWrap); b `_24575` = `smoothstep(max(0, m - w), min(1, m + w), blend.x)`; albedo = `mix(g_tColorA.rgb x colour, g_tColorB.rgb(uvB) x colour, b)`; the normal textures mixed by b before the decode (Y negated, no back-face lines); metalness mix(g_flMetalnessA, g_flMetalnessB, b); roughness the mixed B with the geometric floor; line 1042 as csgo_complex's diffuse.

## csgo_foliage (522 materials, 14.0M triangles)

Pixel static 384 (S_SHADER_QUALITY) with D_BAKED_LIGHTING_FROM_PROBE (dynamic file index 8), 400 S_TINT_MASK, 416 S_TRANSMISSIVE_BACKFACE_NDOTL; S_ALPHA_TEST=1 with that dynamic combo has no pixel file. Vertex static 0.

- Vertex: output_0 = vBlendColorTint (VertexPaintTintColor) as it is; UV and colour as csgo_complex's.
- `_24079` = clamp(input_0, 0.001, 1). Samples at input_3.xy: g_tColor, g_tAmbientOcclusion, g_tNormal.
- Normal: csgo_complex's; when g_fTextureNormalContrast != 1 (lines 346-378) XY x the contrast and a second Y negation on a face that isn't a flipped back face (so that face's Y ends un-negated).
- Roughness `_11005` = `max(saturate(((g_tNormal.b - 0.5) x g_fTextureRoughnessContrast + 0.5) x g_fTextureRoughnessBrightness), the geometric floor)`. F0 = g_flReflectance; no metalness.
- Line 1273: `_13436` = `the view's occlusion x (g_tAmbientOcclusion.r x mix(1, pow(v.w, g_flVertexAmbientOcclusionPower), g_flVertexAmbientOcclusionAmount))`.
- Line 1274: albedo = `max((vec4(g_tColor.rgb x input_4.rgb, 1) x g_mTextureColorAdjust).rgb, 0) x (mix(0, pow(v.x, g_flHeightGradientPower), g_flHeightGradientAmount) + 1)`; line 1276: alpha = g_tColor.a.
- S_TINT_MASK (400): the tint through `mix(c, c x input_4.rgb, g_tTintMask.r)` before the matrix.
- S_TRANSMISSIVE_BACKFACE_NDOTL (416): g_tTransmissiveColor at the UV, or the adjusted albedo with g_bUseAlbedoForTransmissive; g_mTransmissiveTextureColorAdjust with g_bApplyColorCorrectionToTransmissiveColor; x input_4.rgb; g_bTransmissiveShadows. The lighting's use: unread.

Unread: the vertex animation (S_VERTEX_ANIMATION, S_FOLIAGE_ANIMATION, g_tNoiseMap), S_ANIMATED_SHADOWS, S_FOLIAGE_UV_ANIMATION, the alpha test's program.

## VRF's glTF export: the base colour

baseColorFactor = the draw's tint x the vmat's g_vColorTint, in linear (ze_resident_evil_3's world glb: 15 materials with a non-white g_vColorTint, 14 carry exactly it, the 15th it times an object tint; 220 more carry only an object tint; de_vertigo 6 of 8). Whether g_vLayer1Tint is folded in the same way: not seen (every sample's was white).

## Unread

- The material system's Allow1 resolution; what sets PerViewConstantBufferCsgo_t `_m3.w`; the rain state's members.
- csgo_glass S_PAINT_VERTEX_COLORS, S_VERTEX_BREAK_ANIMATION; `_m4` (the refraction cap).
- The whole lighting half beyond the cubemap normalisation; `_m7`, `_m6`, the loop's cube order.
- Whether csgo_complex's alpha test is a depth pre-pass or alpha-to-coverage.
