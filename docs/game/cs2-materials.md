# CS2's world material shaders (the ports in web/src/world/cs2mat/)

What CS2's compiled world shaders compute for a material (albedo, normal, roughness, metalness, AO), read from
`shaders_vulkan_dir.vpk` and ported into three's MeshStandardMaterial (cs2mat/index.js: the port replaces the texture
reads; the lighting is still three's + world/lighting.js, not CS2's BRDF: a stand-in to trace).

Since 2026-11-19 most of them are not ported by hand any more: "The generated ports" below. The per-shader sections
after it are the notes of the hand ports (what each program was read to do), kept as the record.

## The generated ports (2026-11-19)

Ten shaders are no longer ported by hand: csgo_environment, csgo_environment_blend, csgo_complex, csgo_simple,
csgo_vertexlitgeneric, csgo_lightmappedgeneric, csgo_simple_3layer_parallax, csgo_simple_2way_blend, csgo_weapon and
csgo_static_overlay (and since 2026-11-19 generic.vfx: 213 programs; then csgo_unlitgeneric, 4 combinations: its
colour is what `output_0` is set to, the fog's alpha fade compiled out with the view's flag words, docs/game/skybox.md)
run CS2's own
statements, translated per static combo by `node tools/cs2mat/gen.mjs <shader>` into `web/src/world/cs2mat/gen/
<shader>/` (207 programs for the 32 baked maps; `p<pixel static id>_v<vertex static id>.js`, and `index.js`: which
features pick which module). The hand ports of eight of them are deleted (the parallax shader and csgo_weapon had none);
their notes below stay as the record of what was read. Why: csgo_environment_blend alone has two blend formulas
(S_USE_NEW_BLENDING is another program, not a branch), three layers, border / bevel effects per layer, detail
normals, a shared colour overlay, snow, biplanar mapping and wetness, in 35 combinations in use; the hand port had
the two-layer old-blend one.

### What the translator does (tools/cs2mat/)

- `glsl.mjs` parses the dump's `main()` (SPIRV-Cross output: one statement a line, every block braced) into a
  statement tree and takes a backward slice: the statements a set of values depends on, with the `if` / loop
  around them. `fold` compiles out branches a spec declares never taken.
- `specs.mjs` names, per shader family, the statements where the material is handed to the lighting (found by
  shape: SPIR-V ids are stable for one expression across combos, but a merged value's id is not):
  - F0: `vec3 _N = mix(vec3(<reflectance>).xyz, <albedo>.xyz, vec3(<metalness>))[.xyz * ..];` (every program with
    a specular term);
  - without one (csgo_vertexlitgeneric / csgo_lightmappedgeneric base): `vec3 _N = (<direct>.xyz + (<baked>.xyz *
    vec3(<view occlusion> * <AO>).xyz).xyz) * (<albedo>.xyz * (1.0 - <metalness>)).xyz;` (the occlusion is the
    product, the AO sample's `.x` alone, or the view's term alone in a translucent program, which reads no AO at
    all);
  - roughness: `vec2 _N = max(<r>.xy, vec2(pow(saturate(max(dot(dNdx, dNdx), dot(dNdy, dNdy))), 0.333)))`;
  - the shading normal: `vec3 _N = mix(<glint normal or vec3(1)>, <N>, bvec3(all(..)))` after F0, or N.L of the
    sun (`dot(PerViewLightingConstantBufferGpu_t._mK.xyz, <N>)`) where there is no F0;
  - AO: `vec3 _N = vec3(<view occlusion> * <AO>).xyz;`
  - alpha: `vec4 _N = vec4(_a, _b.yz, <alpha>);` (the output before the fog);
  - self-illumination: `vec3 _N = _lit.xyz + mix(e, e * albedo, vec3(g_flSelfIllumAlbedoFactor)).xyz;`
- `translate.mjs` rewrites CS2's names for engine data: `_Globals_.x` -> a uniform `x` (its GLSL type from the
  dump's struct), a bindless `sampler2D(g_bindless_Texture2D_float4[_Globals_.g_tX], ..)` -> a sampler `g_tX`,
  `input_N` -> a varying `vCs2I<N>`, `PerViewConstantBuffer_t` by member type (float: the time; vec3: the camera's
  position). The vertex program is sliced for the outputs the pixel slice reads and translated the same way, with
  `vTexCoord` / `vTexCoord2` / `vBlendColorTint` / `vColorBlendValues` -> the mesh's `uv` / `_uv2` / `color` /
  `_texcoord_4`, the object-to-world products -> three's (cs2WPos / cs2WNrm / cs2WTan), and the instance's colour
  bytes -> `cs2InstColor` (the object's tint, sRGB, as the vertex program decodes it itself).
- `mix(a, b, bvec)` of integer vectors has no GLSL ES 3.00 overload: `cs2Sel`. `textureQueryLod` has none either:
  `cs2Lod`'s isotropic estimate (as the hand ports).
- A dump's struct members are `_mN` by position after dead members are stripped, so `PerViewConstantBuffer_t._m0`
  is not one thing across programs: members are mapped by their type and use, never by index.

### Stand-ins inside the generated programs (each labelled where it is made)

- **Wetness** (puddles, wet darkening, ripples, rain drops; csgo_environment / _blend F_WETNESS): compiled out
  (`bool _N = g_bWetness != 0` taken as false). It runs on the view's rain state (PerViewConstantBufferCsgo_t
  members: untraced, what a map's rain sets); with that state zero the block changes nothing.
- **Fire scorching** (csgo_environment, csgo_complex and the others: the burn marks of infernos near a surface,
  `FireConstantBufferCsgo_t`: a count and flags): taken as none burning. TODO: feed it from grenades/inferno.js.
- Every other `PerViewConstantBufferCsgo_t` member a slice reads is zero (the camera-relative origin, `_m3.w`'s
  bitangent flip, the snow layer's view texture: a flat grey `cs2PvTex`). A generated module lists them in its header.
- **The vertex program without S_SHADER_QUALITY** for csgo_vertexlitgeneric: its `_vs` file has no program for
  static 64, the plain one (static 0 + the features) is used, as the hand port did.
- **Allow1 rules** (`StaticComboRule( Allow1( A, B ) )`): a material setting several keeps the first the rule
  lists (csgo_vertexlitgeneric's F_DECAL_TEXTURE + F_FORCE_UV2: 22 materials). The material system's own
  resolution is untraced.
- **Alpha test** where the program writes alpha 1 and has no discard (csgo_environment, csgo_complex): three tests
  the colour's alpha against the glTF cutoff. A program's own `discard` (csgo_lightmappedgeneric) is kept.
- **F_ADDITIVE_BLEND**: additive blending, from the feature's name (the .vfx lists no blend state).
- **Three's lighting under it**, as before: where CS2's program has no specular term, three's is turned off
  (gen-port.js); F_TRANSMISSIVE_BACKFACE_NDOTL, cloth shading and anisotropic gloss change CS2's lighting, not the
  material values: not drawn.
- **Texture units**: a WebGL fragment program has 16 on most GPUs; the lighting binds 6 (the lightmap's irradiance,
  direction and shadow masks, the cube map array and its table, the sun's cascades; the cube volume and order
  tables were made one texture for this). A material needing more than the 10 left runs without its detail normal
  maps (each layer's `g_fDetailTextureNormalContrast` 0: CS2's own no-detail branch): 352 materials, 0.34 % of
  the baked maps' triangles, nearly all on de_cache. Samplers bound to one texture share a unit (a `#define`).

### How it was checked

- **Against the hand port, pixel for pixel**: ze_resident_evil_3 from a fixed spot (the graphics preset pinned,
  the clock frozen for the frame, the viewmodel hidden), the generated csgo_environment / csgo_environment_blend
  against the hand ports: of 1,440,000 colour values 2 differ, by 1. (Two loads only compare when the preset is
  pinned: a hidden test pane picks another one per load, which moved 3 % of the picture.)
- csgo_complex's base program read line by line against the notes below (it is the hand port's lines, plus the
  texcoord scroll the hand port refused).
- **Every module compiled and linked** on the GPU: `web/src/world/cs2mat/dev/compile-all.js` (207 of 207; about
  0.5 s each for csgo_environment_blend's on the test machine, off the frame: three links in parallel). csgo_weapon's
  two S_STICKERS programs took 15.7 s each cold (150 KB of GLSL: five sticker slots' code); with the slots compiled
  out (below, 2026-11-19) they are 24 KB and 0.21 s, as the stickerless program (compile-all's `ms` with a `salt`, so
  the browser's GPU program cache can't serve them: RTX 4070, ANGLE D3D11).
- ze_resident_evil_3, ze_dark_souls and ze_hold_em_p loaded with them: no shader, program or per-frame GL error;
  ze_dark_souls and ze_hold_em_p with no material left on glTF.
- NOT done: any comparison with CS2's own picture (the paired shots, the tracker's P0); csgo_vertexlitgeneric,
  csgo_lightmappedgeneric, the parallax and 2-way shaders were not compared with their hand ports (their programs
  compile, and their base lines are the statements the hand ports copied).

### The later specs (2026-11-19, the same day)

- **csgo_weapon** (weapon models placed in a map; `weapon` in specs.mjs). Its program hands the lighting a diffuse
  and a specular colour (the metalness folded in with the paint's wear), not albedo + metalness:
  `vec3 _N = (_a.xyz + _b.xyz) * <diffuse>.xyz;` (S_STICKERS: `vec4 _N = vec4(_a * <diffuse>.xyz, <alpha>);`) and
  `vec3 _N = <spec> + ((vec3(1.0) - <spec>) * vec3(0.047619..));`. The port leaves three's metalness 0 and sets
  `material.specularColor` to CS2's after three's own (gen-port.js `flags.spec`). The iridescent paint reads the
  sun's direction inside the material (`PerViewLightingConstantBufferGpu_t._mK.xyz`): `cs2SunDir`, from the
  lighting's sun. Its vertex program projects in object space: `vPositionOs` / `vNormalOs` -> the mesh's own,
  turned to Source's axes and inches (a mesh the cut joined has lost its own space: stand-in), and it multiplies by
  the view-projection: three's (`cs2ViewProj`; three's clip space, not Vulkan's: stand-in). Its one `discard` is
  the view's dithered fade near the camera: left out. **Stickers**: the sticker textures are the game's to bind;
  a placed weapon names the default ones with every `g_bEnableSticker` 0, so the program reads none: they share one
  clear sampler (else the 30 samplers pass the GPU's 16 units). **The slots compiled out** (2026-11-19, specs.mjs
  `weapon.assume`): each slot k runs under `if (_Globals_.g_bEnableSticker<k> != 0) _b = true; else _b =
  _Globals_.g_bStickerPreviewForceOn != 0; if (_b) { ..~700 lines.. }` (csgo_weapon_PixelShader_s512_d3.glsl line 642
  for slot 0, the others every ~712 lines), inside `if (g_tStickerWepInputs.x > 0 && vTexCoord2.z > -1)`. Both
  comparisons are folded to false, which is CS2's own branch for a material with them 0: what is left of the block is
  the slots' else values copied through (and the one g_tStickerWepInputs fetch). A material that sets either
  (`folded` in the module's index entry: gen-reason.js) is refused and stays on glTF; none of the baked maps' does
  (cs2mat-census: the same 14 on glTF before and after).
- **csgo_environment S_PARALLAX_OCCLUSION + S_PIXEL_DEPTH_OFFSET** (ze_dark_souls): translates once the view's flag
  words are folded (`notEqual(PerViewConstantBufferCsgo_t._mK, ivec4(0))` -> all false): they switch a contact-AO
  pass that reads the scene's depth. The parallax march is in the material slice and runs; **the depth offset itself
  (`gl_FragDepth`) is not written** (it is after the lighting: stand-in), nor the contact AO.
- **csgo_static_overlay** (`overlay`): lit as csgo_complex; unlit programs have no lighting entry, so the anchor is
  the vec4 built before the fog, `vec4 _N = vec4(_a, <rgb>.yz, <alpha>);`. After the fog each blend mode ends with
  `rgb = mix(neutral, rgb, alpha)`: Mod2x (3) 0.5, Multiply (5) 1.0, ModThenAdd (6) 0.0; modes 1 and 4 write rgb and
  alpha as they are. Render states (the .vfx): BlendEnable, DstBlend `F_BLEND_MODE == 3 ? One : InvSrcAlpha`,
  DepthBias -64, DepthWriteEnable false, a stencil test NotEqual 3; SrcBlend is not listed, so gen-port.js's
  overlayState takes each mode's from its neutral value (Mod2x: the frame x twice it; Multiply: the frame x it;
  Additive and ModThenAdd: added): stand-ins, as are the polygon offset for the depth bias and the missing stencil.
  S_BLEND_EFFECTS's lit programs write F0 as `mix(vec3(r).xyz, <albedo>, vec3(m))` (no `.xyz` on the albedo).

### generic.vfx generated (2026-11-19, "mapbake-p12")

- Its textures are bound by name, not bindless: `sampler2D(g_tColor, g_sTrilinearWrap)` -> `g_tColor`
  (translate.mjs SAMPLER_NAMED; the sampler state is the material's, as for the bindless ones).
- Anchors (specs.mjs `generic`): without S_SPECULAR the lit colour is `(direct + baked [x the view's occlusion]) x
  ((g_tColor.rgb x g_vColorTint) x the vertex colour)` (PixelShader_s0_d3 line 857; S_TRANSLUCENT's s16 line 787
  without the occlusion): no metalness, no AO texture. S_SPECULAR (s1): F0 = mix(g_tMetalnessReflectanceFresnel.y x
  g_vReflectanceScaleAndBias.x + .y, albedo, g_tMetalnessReflectanceFresnel.x x g_vMetalnessScaleAndBias.x + .y)
  (line 318); roughness `min(1, ((r.z + r.w) / 2) x g_vRoughnessScaleAndBias.x + .y + (r.x + r.y) / 2)` of
  g_tRoughness, then the geometric floor (line 325). S_TRANSLUCENT alpha: vertex alpha x g_tColor.a x
  g_flOpacityScale (line 789). S_UNLIT (s2_d0): the vec4 before the fog, (g_tColor.rgb x g_vColorTint x the vertex
  colour, its alpha).
- The vertex program: the one the dump names for D_BAKED_LIGHTING_FROM_LIGHTMAP (VertexShader s0_d3) decodes the
  frame from nPackedFrame and has no lightmap UV output, one output fewer than the lightmapped pixel program reads;
  the one named for D_BAKED_LIGHTING_FROM_PROBE (s0_d2: vNormalOs, vTangentUOs_flTangentVSign, vLightmapUV) is its
  partner by interface. gen.mjs now checks every pair (location, type, centroid) and tries a spec's `vertexTry`
  combos. The packed-frame form is also mapped (`normalize(vec4(_N.xyz, 0) x transform)` -> cs2WNrm, the tangent ->
  `vec4(cs2WTan, tangent.w)`), unused now. Why the dump's index differs for this shader: untraced.
- 5 programs (p0_v0d2, p1_v1d2, p16_v0d2, p17_v1d2, p2_v2); generic.js (the hand port) deleted.

### csgo_glass F_OPAQUE_CUBEMAP_REFRACTION (2026-11-19, glass.js)

Pixel static 18 (`--combo S_SHADER_QUALITY=1,S_OPAQUE_CUBEMAP_REFRACTION=1`, 1,195 lines), vertex static 2. Lines up
to the lit colour are static 16's (its line 1013 = line 946 above). Then, opaque:

- r `_16734` = mix(g_flRefractMinRoughness, 1, dot(_15134.xy, 0.5)), `_15134` = g_tNormal.zz x the vertex alpha (the
  raw roughness, no geometric floor) (line 1086);
- the ray `_24296` = refract(normalize(pos - camera), N, 0.66) (lines 293, 1087); the "dominant direction" mix after
  it mixes the ray with itself (no change); the mip `_12665` = PerViewLightingConstantBufferGpu_t._m14.y x sqrt(r);
- the cubemap volumes walked as the reflection's (lines 1104-1188: the box fade, smoothstep weight, box parallax
  mixed back by r, the volume's own SH `_m7` gathered);
- output_0 = (lit + `_8674` (the light through) x env / total x min(luma(probe light) / dot((ray, 1), SH / total),
  max(r x _m4.x + _m4.y, 1)), 1) (line 1192).
- Ours: three's lit sum + cs2GlassThroughRgb x cs2EnvGather(world pos, ray, ray, r, lod) x min(luma(irradiance / PI) /
  g.a, 1) (glass.js FS_OUT). Stand-ins: the cap max(r x a + b, 1) taken as 1 (`_m4` unread; lighting.js
  cs2EnvSpecular does the same), the fog on the through term, nothing added without cubemaps.

### sky_occluder (read 2026-11-19; drawn since "mapbake-done": world/sky-occluder.js)

Not a surface material: the .vfx header says "Sky occluder - writes depth to hide the world". `Depth("csgo_depth_only.vfx")`,
PS dynamic combo D_SKY_OCCLUDER_PASS 0..3, `output_0 = vec4(g_tColor.rgb, 1)` in every pass, but **every pass's
RenderTargetWriteMask[0] is None** (sky_occluder_states.txt lines 100, 211, 322, 433): it never writes a colour.
Pass 0: depth test LessEqual, no depth write, stencil write mask 128, DecrSat on pass. Pass 1: depth write,
DepthFunc Always, stencil Equal (read 128, write 128) Replace. Passes 2 and 3: depth write LessEqual, no stencil.
StencilRef 128, CullMode Back. Seen: the world behind it is hidden and the sky shows there.

Ours: the sky's own program (lighting.js SKY_FS, its uniforms shared, so env_sky's tint, brightness and its legacy
fog are the sky's) on the occluder's surface, looked up along the view ray turned into the sky cube's frame
(`cs2SkyInv`, set by setSkyMesh), depth written, FrontSide. STAND-INS: the stencil passes' order in CS2's frame is
unread; a 3D skybox behind an occluder is hidden as the world is; its sun shadow is three's as any world mesh's
(whether CS2's depth-only mode puts it in the shadow map is unread). The chunk cut dropped it with the other tool
materials (`tools?(...|sky)` also matched toolsskybox_occluder): tools/chunk-world.mjs keeps it now and
ze_dark_souls was re-cut (8 chunks changed, the other 65 byte-identical; 16 occluder panels boxing two areas,
x 3340..5100 / y 280..3048 and x -116..4384 / y 5318..12176). Master's client still hides them by name.
Checked on ze_dark_souls (camera pinned inside the first box): the panels draw the sky cube where, with them
hidden, the fogged world beyond showed. Not compared with CS2's picture.

### csgo_textile_layer (2026-11-19, "mapbake-done": tools/cs2mat/specs.mjs `textile`)

Probe lit, no lightmap combo (PixelShader_s0_d0, S_SHADER_QUALITY=1, 1,344 lines): the dump's base combo. The material
hands the lighting a specular colour, not albedo + metalness: F0 `_17639 = mix(_18402, albedo _11121, metal)` (line
523) where `_18402` is g_flReflectance (= pow((1.5-1)/(1.5+1), 2), the vars table) or, with g_bClothShading, the
sheen colour mix(R, saturate(sqrt(albedo) x g_flSheenScale), cloth) (line 517); the diffuse colour is albedo x (1 -
metal) (line 1260, `(_11121 * _12929)`); the AO `_13436` (line 1259, x the view's dynamic AO `_21711`). With cloth
shading each light's specular lobe is another (lines 768-781 and 1084-1095: a sheen distribution
(2 + 1/a) x pow(1 - NdotH², 0.5/a) / (4 (NL + NV - NL NV)) mixed in by the cloth amount) and the ambient specular too
(lines 1118-1120, 1243-1249). three's lighting has none of that, so g_bClothShading (= F_CLOTH_SHADING ||
F_BACKWARDS_COMPATIBILITY) is compiled out at false and a material setting either feature is refused (`folded`);
de_boulder's leather02 sets neither, so for it this is CS2's own branch. Generated with the weapon's `spec` path
(cs2Spec in place of three's specular colour). To fold the view's dynamic AO switch (`if (_24465.x)` on an all-false
flag vector) glsl.mjs `fold` now also prunes an `if` on a component of a bool vector only ever assigned all-false:
csgo_lightmappedgeneric p6336 and three csgo_static_overlay programs lost the same dead branch (their anti-aliased
alpha test behind `bvec4(false).z`), the rest regenerated byte-identical. Checked: compile-all 214 of 214; de_boulder
loaded, its three leather meshes on the port, no shader error (the meshes are 2 x 2 x 1 units: not judged by eye).

### What is left on the glTF path (`node tools/cs2mat-census.mjs web/public/maps --units 16`)

16,481 of 16,680 world materials are ported (99.95 % of 162.6M triangles; 84.49 % at the start of 2026-11-19), 198
are drawn by another pass (water, effects, the unlit shaders, the sky occluder), **1 is left (156 triangles)** (3
before "mapbake-done": the textile layer is generated, the sky occluder drawn):

| Left | Materials | Triangles | Why |
|---|---|---|---|
| csgo_simple_liquid | 1 | 156 | de_fachwerk's wine bottle liquid (models/generic/winebottle_kit_01/wine_bottle_02_a_dusty_liquid). Not a background refraction after all: D_USE_BGREFRACT `Requires(S_OPAQUE_REFRACT)`, which this material does not set. Its only pixel program for a material with no feature is PixelShader_s0_d0 (no baked lighting, 2,349 lines; d32 for the probe combo is not in the vcs): **one program lights two layers itself**, a frosted glass shell (g_tFrost, lines 760-930) and the liquid inside (level, wobble, back fade, its own specular strengths 15.2 / 13.3, line 2343), reading the sun (PerViewLightingConstantBufferGpu_t _m18 / _m19), the cubemap volumes (_m16, lines 2250-2290), CS2's BRDF lookup texture (g_tBRDFLookup) and the barn lights itself. It hands no single material to the lighting, so the generator's slice-and-hand-over cannot take it: a whole-program port with CS2's lighting buffers mapped to ours (and the BRDF lookup baked) |

csgo_decalmodulate, csgo_glass and csgo_foliage keep their hand ports (decalmodulate.js, glass.js, foliage.js).

### The shader tables go stale with CS2 (found 2026-11-19)

`mat/shaders/<shader>.json` (the variable table lib/vfx/shader-vars.js evaluates) is CS2's, not the map's: six
folders baked before CS2's update of 2026-11-18 (ar_baggage, ar_pool_day, ar_shoots, ar_shoots_night, cs_italy,
ze_hold_em_p; ze_resident_evil_3 too) held the older tables (one variable fewer, sampler states as expressions),
46 files. Replaced with today's (identical to what `lasers-bake --materials` writes now: checked on de_nuke). A
generated program's uniforms are named from today's dump, so a table from another build can lack one.

## Cubemap normalisation (read 2026-11-19, "mapbake-p0"; world/lighting.js cs2EnvSpecular)

The lighting half of CS2's forward programs (here csgo_complex_PixelShader_s5120_d3.glsl, S_SHADER_QUALITY=1, lines
1150-1236; the same shape in the other world shaders' full programs, not sliced by the generator):
- the cube loop walks the view's envmap list (PerViewLightingConstantBufferGpu_t._m15._m0[i]: _m0 world-to-box matrix,
  _m1 / _m3 the box corners, _m5 the edge fade scale, _m4 the cube array slice, _m2 the array layer, _m6 a colour
  scale, _m7 the cube's baked SH (vec4 a channel)); weight = smoothstep of the box edge distance x (1 - weight so
  far), stops past 0.99; the lookup direction parallax-corrected and mixed toward the plain reflection by roughness.
- specular indirect = (sum env / total weight) x **min( dot(lightmap diffuse, (0.2125, 0.7154, 0.0721)) /
  dot(vec4(N, 1), sum SH / total weight), max( roughness x PerViewLightingConstantBufferGpu_t._m5.x + _m5.y, 1.0 ) )**
  x the BRDF lookup's split sum x the view occlusion x AO. roughness = `_17751 = dot(_11004.xy, 0.5)`, the
  geometric-floored roughness (line 484) averaged over its two axes.
- `_m5` is written in scenesystem **0x1801af964** (the per-view lighting constants' fill, function ~0x1801af7b0):
  `slope = (lb_cubemap_normalization_max - 1) / (1 - lb_cubemap_normalization_roughness_begin)` ->
  [rbp+0x30] (_m5.x), `max - slope` -> [rbp+0x34] (_m5.y); the 1.0 is xmm13, loaded from 0x1805fff70 at 0x1801af849.
  The cvars (tools/re/game/cvardefs.py, float bits): lb_cubemap_normalization_max 0x42000000 = 32.0 (handle 0x180923bd0,
  registered at 0x18001118f), lb_cubemap_normalization_roughness_begin 0x3DCCCCCD = 0.1 (0x180923be0, 0x18001123f),
  flags 7. client.dll's r_csgo_cubemap_normalization (default 1, handle 0x1825e7f20) not followed further.
- So the cap is 1 up to roughness 0.1 and rises to 32 at roughness 1: a rough surface's reflection is **brightened**
  to the lightmap's light, not only darkened. **Ours still caps at 1 (a stand-in)**: with CS2's cap, tried on
  de_vertigo, rough floors got bright specks CS2 doesn't draw and the metal elevator door it was tried for stayed at
  26 / 255 (CS2 63): at its roughness (0.45, cap 13) the limit was the ratio itself, the cubes' SH luma above the
  lightmap's. So our SH term (cs2EnvGather's g.a) or the gather differs from CS2's: trace `_m7` (what scenesystem puts
  there per cube) before switching the cap on.
- Unread: the order the loop visits cubes (findLSB over the cull bit words) against ours, the `_m6` colour scale, the
  view's other `_m5` uses.

## How a shader is read

```bash
./bake/bin/Release/net10.0/lasers-bake --shader-src <shader> <scratch dir> --cs2 "<cs2>/game/csgo" --glsl --vars-json \
  --combo S_SHADER_QUALITY=1,D_BAKED_LIGHTING_FROM_LIGHTMAP=1[,S_<FEATURE>=1]
```

- `--combo` picks one static + dynamic combo (every other combo value 0); the file is
  `<shader>_PixelShader_s<static id>_d<dynamic index>.glsl`. Without it: tens of thousands of programs.
- `<shader>.vfx` (VRF's reconstruction) lists the features, the static / dynamic combos and their rules, and the
  variables. `<shader>_vars.json` is the variable table the game evaluates (lib/vfx/shader-vars.js; the bake's
  `mat/shaders/<shader>.json`).
- `_NNNN` names are SPIR-V ids: they change between combos. To see what a feature adds, diff a combo against the base
  with the ids normalised (`_\d+` -> `_N`) and print the lines only the feature's file has.
- The pixel program holds the whole forward pass (lightmaps, barn lights, shadows, fog): the material is its first
  ~100 lines after `main()` and the lines that feed the final sum.

## csgo_complex (2026-11-18; 2,543 materials, 33.7M triangles in the 30 baked maps)

Pixel static combos: S_MODE_TOOLS_VIS, S_DETAIL_TEXTURE, S_SECONDARY_UV, S_ANISOTROPIC_GLOSS, S_ALPHA_TEST,
S_TRANSLUCENT, S_ADDITIVE_BLEND, S_SELF_ILLUM, S_TINT_MASK, S_METALNESS_TEXTURE, S_DECAL_TEXTURE, S_SHADER_QUALITY,
S_TRANSMISSIVE_BACKFACE_NDOTL (each `StaticCombo(S_X, F_X)`). Ids with S_SHADER_QUALITY=1 and
D_BAKED_LIGHTING_FROM_LIGHTMAP=1 (dynamic index 3):

| Static id | Combo | Read |
|---|---|---|
| 5120 | base | yes (ported) |
| 5760 | S_TINT_MASK | yes (ported) |
| 6400 | S_METALNESS_TEXTURE | yes (ported) |
| 5160 | S_ALPHA_TEST | yes (ported; see below) |
| 5440 | S_SELF_ILLUM | read, not ported |
| 5130 | S_SECONDARY_UV | read, not ported |
| 5122 | S_DETAIL_TEXTURE | read, not ported |
| 5200 | S_TRANSLUCENT | dumped, not read |

Vertex program (static 0, dynamic 8), `_Globals_`: g_vTexCoordXform0, g_vTexCoordXform1, g_vTexCoordScrollSpeed,
g_vColorTint, g_flModelTintAmount.

- UV (output_2.xy) = `(dot(uv, Xform0.xy) + Xform0.w, dot(uv, Xform1.xy) + Xform1.w) + g_vTexCoordScrollSpeed x time`
  (PerViewConstantBuffer_t._m1). output_2.zw: the second UV set with S_SECONDARY_UV.
- Colour (output_4) = `vec4(mix(1, instance tint, g_flModelTintAmount) x g_vColorTint, instance alpha x
  instance._m7)`. The instance tint is the instance buffer's RGBA8 (`_m0`), sRGB -> linear per channel
  (`c <= 0.04045 ? c x 0.0773993805 : pow(c x 0.947867334 + 0.0521327034, 2.4)`).
- Normal (output_1) = normalize(normal x the instance's transform); output_5 its centroid copy; output_6 the tangent
  with its sign in w.

Pixel program, base (5120), in the order of the file:

- `_21709` = the vertex normal: output_5 (centroid) where `dot(input_1, input_1) >= 1.01`, else input_1.
- `_12885` = `g_bRenderBackfaceNormals != 0 && g_bDontFlipBackfaceNormals == 0`; `_24347` = normalize(`_21709` x
  (front facing ? 1 : -1) when `_12885`): the geometric normal.
- Samples: g_tColor (sampler g_sUserConfigAllowGlobalMipBias), g_tAmbientOcclusion and g_tNormal (g_sUserConfig), all
  at input_2.xy.
- Normal: `a = (r + g) - 1.00392163; b = r - g; n = normalize(a, b, (1 - |a|) - |b|)` (hemi-octahedral).
  `_24327` = `_12885` && !front facing. N = input_1 x (`_24327` ? -1 : 1) (not renormalised);
  B = cross(N, T) x (T.w > 0 ? 1 : -1), negated when `PerViewConstantBufferCsgo_t._m3.w != 0` (unread: what sets
  it); n.y is negated unless `_24327`; world normal = normalize(T x n.x + B x n.y + N x n.z).
- Albedo `_14202` = g_tColor.rgb x input_4.rgb.
- F0 `_12351` = mix(g_flReflectance, albedo, g_flMetalness); g_flReflectance's expression is
  `pow((1.5-1)/(1.5+1),2)` = 0.04.
- Roughness `_11004` = max(g_tNormal.bb, pow(saturate(max(dot(dFdx(G), dFdx(G)), dot(dFdy(G), dFdy(G)))), 0.333)),
  G = `_24347` (a vec2: the two anisotropy axes take the same value in this combo).
- Line 1070-1073: `_13436` = `_21712` (the view's ambient occlusion term) x g_tAmbientOcclusion.r; diffuse =
  (direct diffuse + lightmap irradiance x (1 - the specular terms) x `_13436`) x albedo x (1 - metalness);
  output alpha = input_4.w.

Feature combos, the lines they change:

- **S_TINT_MASK** (5760): `_14202 = mix(c, c x input_4.rgb, g_tTintMask.r)`, the mask sampled at input_2.xy
  (g_sUserConfig).
- **S_METALNESS_TEXTURE** (6400): metalness `_10391` = g_tColor.a, in both the F0 mix and the diffuse's
  (1 - metalness).
- **S_ALPHA_TEST** (5160): the only change is the output's alpha = 1.0. No discard in this program: the test is
  elsewhere (a depth pre-pass program or alpha-to-coverage state: unread).
- **S_SELF_ILLUM** (5440): `e = g_tSelfIllumMask.rgb(input_2.xy + fract(g_vSelfIllumScrollSpeed x time)) x
  g_vSelfIllumTintScaled`; output += mix(e, e x albedo, g_flSelfIllumAlbedoFactor).
- **S_SECONDARY_UV** (5130): g_tAmbientOcclusion is sampled at input_2.zw when
  g_bUseSecondaryUvForAmbientOcclusion != 0 (default 1); the table also has g_bUseSecondaryUvForTintMask (0),
  ...ForDetailMask (1), ...ForDecal (1), ...ForSelfIllum (0), ...ForDetailTexture (1).
- **S_DETAIL_TEXTURE** (5122): the inputs shift by one (input_0: the detail UV); albedo = g_tColor.rgb x tint x
  mix(1, g_tDetail.rgb x 1.99215686, max(g_tDetailMask.r, g_flDetailBlendToFull) x g_flDetailBlendFactor), the mask
  at the base UV. g_vDetailTexCoordXform = scale.xxy x (cos, -sin, sin, cos) of g_flDetailTexCoordRotation (the
  vertex program's use of it: unread).

Unread: S_TRANSLUCENT (g_flOpacityScale), S_ADDITIVE_BLEND, S_ANISOTROPIC_GLOSS, S_DECAL_TEXTURE,
S_TRANSMISSIVE_BACKFACE_NDOTL, the cloth and specular features (Features-only: no pixel static combo of their own),
S_PAINT_VERTEX_COLORS (vertex), combos of two features together (taken as independent: not dumped), and the whole
lighting half of the program.

## csgo_simple (2026-11-18; 805 materials, 5.0M triangles)

Pixel static combos: S_METALNESS_TEXTURE, S_AMBIENT_OCCLUSION_TEXTURE, S_SHADER_QUALITY, S_MODE_TOOLS_VIS; vertex:
S_MODE_TOOLS_VIS, S_PAINT_VERTEX_COLORS. With S_SHADER_QUALITY=1 and D_BAKED_LIGHTING_FROM_LIGHTMAP=1 the pixel
program is static 4 (dynamic file index 36), the vertex program static 0 (dynamic 8).

- Static 4 is csgo_complex's 5120 line for line (no line of either is missing from the other with the ids
  normalised), and the vertex programs are equal the same way.
- Static 5 (S_METALNESS_TEXTURE): the same three lines csgo_complex's 6400 changes (metalness = g_tColor.a).
- Static 6 (S_AMBIENT_OCCLUSION_TEXTURE): no line changes (g_tAmbientOcclusion is sampled in every combo; without
  the feature the material's texture is the default white one).

So cs2mat/simple.js is complex.js with csgo_simple's feature list. Unread: S_PAINT_VERTEX_COLORS (vertex).

## csgo_vertexlitgeneric (2026-11-18; 2,125 materials, 13.0M triangles)

Pixel static combos: S_SPECULAR_DIRECT, S_SPECULAR_INDIRECT, S_FORCE_UV2, S_DECAL_TEXTURE, S_DETAIL_TEXTURE,
S_MODE_TOOLS_VIS, S_ALPHA_TEST, S_TRANSLUCENT, S_ADDITIVE_BLEND, S_TINT_MASK, S_SELF_ILLUM, S_SHADER_QUALITY. Ids with
S_SHADER_QUALITY=1, D_BAKED_LIGHTING_FROM_LIGHTMAP=1 (dynamic index 3): 2048 base, 2051 S_SPECULAR_DIRECT +
S_SPECULAR_INDIRECT, 2560 S_TINT_MASK, 2112 S_ALPHA_TEST, 2052 S_FORCE_UV2 (all read). The vertex program with
S_SHADER_QUALITY=1 (static 64) has no file in the dump; static 0 (dynamic 8) was read instead.

Vertex program `_Globals_`: g_vTexCoordXform0 / 1, g_vTexCoordScrollSpeed, g_vColorTint, g_flModelTintAmount,
g_vNormalTexCoordXform0 / 1.

- output_3.xy = the UV through g_vTexCoordXform0 / 1 + scroll x time; output_3.zw = the vertex's UV as it is.
- output_0 = the UV through g_vNormalTexCoordXform0 / 1 (the normal map's own transform: rotation, scale, centre,
  offset, as the colour's).
- output_5 = the tint, as csgo_complex's output_4.

Pixel program, base (2048):

- Colour `_19680` = g_tColor at input_3.xy; AO `_17476` = g_tAmbientOcclusion.r at input_3.zw;
  `_21710` = `g_flAmbientOcclusionScale > 0 ? min(mix(1, 2 x ao, scale), 1) : ao`.
- `_19069` = g_tMetalness at input_3.xy (its G is the metalness). g_tNormal at input_0.xy, decoded and framed as
  csgo_complex's.
- Line 876: diffuse = (direct diffuse + lightmap irradiance x (the view's occlusion x `_21710`)) x
  mix(c, c x input_5.rgb, saturate(g_tColor.a + g_flInverseBlendTint)) x (1 - g_tMetalness.g). No specular term at
  all in this combo, and g_tNormal.b (roughness) is unread.
- g_flInverseBlendTint's expression: `F_NOTINT ? -1 : 1-(F_TINT_MASK ? 1 : 0)`.

Feature combos:

- **S_SPECULAR_DIRECT + S_SPECULAR_INDIRECT** (2051): F0 `_12351` = mix(g_flReflectance (0.04), albedo,
  g_tMetalness.g); roughness = csgo_complex's `_11004` from g_tNormal.b; the diffuse line takes csgo_complex's form
  (the lightmap term x (1 - the specular terms)). Each combo alone: not dumped.
- **S_TINT_MASK** (2560): the tint's blend reads g_tTintMask.r (at input_3.xy) in place of g_tColor.a.
- **S_ALPHA_TEST** (2112): output alpha = 1, nothing else (as csgo_complex).
- **S_FORCE_UV2** (2052): no pixel line changes (the vertex program's side: unread).

Unread: S_DETAIL_TEXTURE, S_DECAL_TEXTURE, S_SELF_ILLUM, S_TRANSLUCENT, S_ADDITIVE_BLEND.

## csgo_complex and csgo_vertexlitgeneric: self-illum, detail, translucent (2026-11-18)

Read in both shaders; the lines are the same in each (cs2mat/complex.js EXTRA_MAIN):

- **S_SELF_ILLUM** (complex 5440, vertexlitgeneric 3072): `e = g_tSelfIllumMask.rgb(colour UV + fract(
  g_vSelfIllumScrollSpeed x time)) x g_vSelfIllumTintScaled`; output += mix(e, e x albedo,
  g_flSelfIllumAlbedoFactor). g_vSelfIllumTintScaled's expression: `pow(2, g_flSelfIllumBrightness) x
  g_flSelfIllumScale x SrgbGammaToLinear(g_vSelfIllumTint)`. The mask is an sRGB read (the table's flag).
- **S_DETAIL_TEXTURE** (complex 5122 / vertex static 2, vertexlitgeneric 2064 / vertex static 16): the detail's UV
  is the vertex program's `(dot(g_vDetailTexCoordXform.xy, uv), dot(g_vDetailTexCoordXform.zw, uv)) +
  g_vDetailTexCoordOffset` (the vertex's own UV); albedo x= mix(1, g_tDetail.rgb x 1.99215686,
  max(g_tDetailMask.r, g_flDetailBlendToFull) x g_flDetailBlendFactor), the mask at the colour UV. g_tDetail is a
  linear read.
- **S_TRANSLUCENT** (complex 5200, vertexlitgeneric 2176): output alpha = the vertex colour's alpha x (g_tColor.a x
  g_flOpacityScale). The program's lighting also changes (71 lines in vertexlitgeneric's): unread.

## csgo_lightmappedgeneric (2026-11-18; 1,070 materials, 0.8M triangles)

Pixel static combos: S_ALPHA_TEST, S_TRANSLUCENT, S_DETAILBLENDMODE, S_DETAILTEXTURE, S_FANCY_BLENDING, S_LAYERS,
S_METALNESS_TEXTURE, S_OVERLAY, S_SPECULAR_DIRECT, S_SPECULAR_INDIRECT, S_TEXTURETRANSFORMS, S_SHADER_QUALITY,
S_MODE_TOOLS_VIS. Ids with S_SHADER_QUALITY=1, D_BAKED_LIGHTING_FROM_LIGHTMAP=1 (dynamic index 3): 6144 base, 6150
the two specular combos, 6528 S_TRANSLUCENT, 6336 S_ALPHA_TEST, 6240 S_TEXTURETRANSFORMS (dumped, unread); S_OVERLAY
alone (7680) has no pixel file. Vertex static 0.

- Vertex: output_2 = the vertex's UV twice (xyxy) without S_TEXTURETRANSFORMS; output_4 = (mix(1, instance tint,
  g_flModelTintAmount) x g_vColorTint, a x g_flVertexColorOpacityScale), a the instance's alpha term.
- Base (6144): g_tColor at input_2.xy (g_sUserConfig), g_tLayer1AmbientOcclusion at input_2.xy (g_sTrilinearWrap),
  g_tLayer1NormalRoughness at input_2.zw; normal decoded and framed as csgo_complex's. Line 861: diffuse = (direct +
  lightmap x (the view's occlusion x AO.r)) x (g_tColor.rgb x g_vLayer1Tint x input_4.rgb) x (1 - g_flMetalness).
  No specular term. Output alpha = input_4.w.
- Specular (6150): roughness `_16570` = g_tLayer1NormalRoughness.b; with g_bNoSpecularAtFullRoughness
  (F_NO_SPECULAR_AT_FULL_ROUGHNESS): r + smoothstep(0.9, 1, r) x 2; then csgo_complex's geometric floor. F0 =
  mix(g_flReflectance, albedo, g_flMetalness).
- S_TRANSLUCENT (6528): alpha `_17232` = input_4.w x ((g_tColor.a x input_4.w) x g_flOpacityScale).
- S_ALPHA_TEST (6336): a = (g_tColor.a x input_4.w) x input_4.w; the test is in this program: with
  g_flAntiAliasedEdgeStrength the edge is `mix(saturate(0.5 + (a - ref) / max(fwidth(a), 1e-6)), a, mix(1,
  saturate(4 x length(fwidth(uv))), strength))`, else a - g_flAlphaTestReference.

Unread: S_DETAILTEXTURE, S_TEXTURETRANSFORMS, S_METALNESS_TEXTURE, S_OVERLAY's own program.

**S_LAYERS + S_FANCY_BLENDING** (read 2026-11-19 from the generated p6168_v24, pixel static 6168 / vertex 24 at
S_SHADER_QUALITY=1, and the Low-quality program, pixel static 24: the same lines). The .vfx: `Feature( F_FANCY_BLENDING,
0..3 (0="VertexBlend", 1="BlendModulateTexture,rg", 2="NewLayerBlending,g", 3="NewLayerBlending,a") )`, `FeatureRule(
Requires( F_FANCY_BLENDING, F_LAYERS==1 ) )`, `StaticCombo( S_FANCY_BLENDING, F_FANCY_BLENDING!=0 )` and
`int g_nFancyBlendingMode < Expression(F_FANCY_BLENDING); >` (the mode reaches the program as a constant, the combo is
0 / 1). The vertex program passes `vColorBlendValues` through untouched (`output_0 = vColorBlendValues`). Pixel, with
v = input_0.x and M = g_tBlendModulation at the colour UV (linear, g_sUserConfig):
- mode 0: w = v; mode 1: w = smoothstep(max(0, M.g - M.r), min(1, M.g + M.r), v);
- mode 2: w = smoothstep(max(0, M.g - g_flBlendSoftness), min(1, M.g + g_flBlendSoftness), v); mode 3 the same with M.a;
- modes 2 / 3 tint layer 1 by the border: albedo1 x mix(1, g_vLayerBorderTint (SrgbGammaToLinear), (1 - |2 x
  smoothstep(max(0, h - g_flLayerBorderSoftness), min(1, h + g_flLayerBorderSoftness), saturate(v -
  g_flLayerBorderOffset)) - 1|) x g_flLayerBorderStrength), h the modulation value used (M.g / M.a);
- albedo = mix(layer 1, g_tLayer2Color x g_vLayer2Tint, w) x the vertex tint; the normals, roughness and AO blend by
  the same w further down.
Until 2026-11-19 the generator read only `StaticCombo( S, F )`, so S_FANCY_BLENDING was dropped and every
fancy-blended material ran the S_LAYERS program (mode 0's plain vertex blend; BUGFIXES). Open: de_dust2's mode-2
materials show more layer 2 than CS2's picture (docs/MAP_SHOTS.md item 2).

## csgo_static_overlay (2026-11-18; 842 materials)

Pixel static combos: S_MATERIAL_REFERENCE, S_BLEND_MODE (0..6), S_LIT, S_BLEND_EFFECTS, S_TINT_MASK,
S_SHADER_QUALITY, S_MODE_TOOLS_VIS; rule `Requires(S_LIT==1, S_BLEND_MODE...)`. Read: 128 (S_BLEND_MODE=1, S_LIT,
quality, lightmap: dynamic index 3), 130 (S_BLEND_MODE=2, S_LIT), 114 (S_BLEND_MODE=1 unlit, dynamic 0), 118
(S_BLEND_MODE=3 unlit); vertex static 44 (S_PAINT_VERTEX_COLORS). In the 30 maps: lit mode 1 501, unlit mode 3
147, lit mode 2 93, unlit mode 1 64, mode 6 23, mode 4 5, mode 0 4, mode 5 1.

- Vertex: UV through g_vTexCoordXform0 / 1 + scroll; the colour (rgba) = (mix(1, instance tint,
  g_flModelTintAmount) x g_vColorTint, instance alpha), x vBlendColorTint (VertexPaintTintColor, rgba) with
  S_PAINT_VERTEX_COLORS unless all four of its components are 0; g_flOverlayLift > 0 lifts the vertex along the
  normal (x 1.5 / max(dot(N, view), 0.3)): unported.
- Lit (128): c `_7787` = g_tColor.rgb x colour.rgb; albedo = (vec4(c, 1) x g_mTextureColorAdjust).rgb, and with
  bAutomaticPBRColorFitting (F_AUTOMATIC_PBR_COLOR_FITTING) the fit of lines 290-296 (g_vAlbedoLevels,
  g_vMetallicAlbedoLevels, g_vDarkMetallicAlbedoLevels: cs2mat/overlay.js has it term for term). Metalness
  g_tMetalness.g, AO g_tAmbientOcclusion.r on the lightmap term, normal decoded with Y negated and XY x
  g_fTextureNormalContrast, roughness max(saturate(((b - 0.5) x g_fTextureRoughnessContrast + 0.5) x
  g_fTextureRoughnessBrightness), the geometric floor), self-illum as csgo_complex's with c as the albedo. Line
  1009: alpha = colour.a x (g_tColor.a x g_flOpacityScale). g_bSnow changes the lightmap term (line 1003): unread.
- Lit alpha test (130): a = g_tColor.a x colour.a; discarded where a - g_flAlphaTestReference - 0.001 < 0 (or the
  anti-aliased edge, as csgo_lightmappedgeneric's).
- Unlit (114): rgb = (vec4(g_tColor.rgb, 1) x g_mTextureColorAdjust).rgb x colour.rgb, alpha as above, then fog.
- Unlit Mod2x (118): the same, then rgb = mix(0.5, rgb, alpha) (a view flag adds a fitted branch, line 110: unread).
- Render states (.vfx): BlendEnable, DstBlend `F_BLEND_MODE == 3 ? One : InvSrcAlpha` (SrcBlend isn't listed),
  DepthBias -64, DepthWriteEnable false, stencil NotEqual ref 3 read mask 1 write mask 254.

## csgo_decalmodulate (2026-11-18)

Pixel static 0, dynamic 0 (85 lines; no pixel file with a baked-lighting dynamic combo): c = g_tColor (a linear
read, g_sUserConfigAllowGlobalMipBias) x the vertex colour (vec4(1) without S_VERTEX_COLOR); discard where c.a -
g_flAlphaTestReference < 0; two fog terms scale c.a (PerViewConstantBufferCsgo_t flags `_m0.y`, `_m0.z`); output rgb =
mix(0.5, c.rgb, c.a). Render states as csgo_static_overlay's stencil and depth; no blend state listed.

## generic.vfx (2026-11-18; 130 materials)

Pixel static 0 / dynamic index 3 (lightmap), vertex static 0. Not bindless (g_tColor, g_tNormal with
g_sTrilinearWrap). Vertex: output_2 = the UV twice; output_3 = the instance colour (sRGB -> linear) with its alpha.
Pixel: xy = g_tNormal.ag x 2 - 1, n = (x, -y, sqrt(saturate(1 - x^2 - y^2))), n.xy x g_flBumpStrength, normalised,
Y negated again unless a flipped back face; line 677: diffuse = (direct + lightmap x the view's occlusion) x
(g_tColor.rgb x g_vColorTint) x the instance colour. No specular, metalness or AO texture. g_vColorTint has no
expression in this shader's table (used as the material gives it). Unread: S_SPECULAR, S_TRANSLUCENT, S_UNLIT,
S_ALPHA_TEST, S_SELF_ILLUM, S_TINT_MASK, S_OVERLAY.

## csgo_simple_2way_blend (2026-11-18; 58 materials)

Pixel static 2 (quality), vertex static 0. Combos: S_ENABLE_AO, S_ENABLE_TINT_MASKS, S_PAINT_VERTEX_COLORS (vertex).
Vertex: output_0 = (vBlendValues.xyz, max(vBlendValues.w, 0.1)); UV and colour as csgo_complex's. Pixel: uvB =
uv x g_vTexCoordScale2; mask `_16038` = g_tMask.r at uvB (g_sTrilinearWrap); b `_24575` = smoothstep(max(0, m -
w), min(1, m + w), blend.x); albedo = mix(g_tColorA.rgb x colour, g_tColorB.rgb(uvB) x colour, b); the normal
textures mixed by b before the decode (Y negated, no back-face lines); metalness mix(g_flMetalnessA,
g_flMetalnessB, b); roughness the mixed B with csgo_complex's floor; line 1042 as csgo_complex's diffuse.

## csgo_vertexlitgeneric S_FORCE_UV2, undeclared features (2026-11-18)

- S_FORCE_UV2 (vertex static 4): output_3 = (the transformed UV, vTexCoord2): the AO reads the second UV set.
- csgo_complex's .vfx declares no F_SPECULAR, F_SPECULAR_CUBE_MAP, F_HIGH_QUALITY_GLOSS, F_DIFFUSE_WRAP or
  F_PREPASS_ALPHA_TEST, and csgo_lightmappedgeneric's no F_VERTEX_COLOR: vmats carry them, no combo or expression
  reads them.

## csgo_foliage (2026-11-18; 522 materials, 14.0M triangles)

Pixel static 384 (S_SHADER_QUALITY) with D_BAKED_LIGHTING_FROM_PROBE (dynamic file index 8), 400 S_TINT_MASK, 416
S_TRANSMISSIVE_BACKFACE_NDOTL; S_ALPHA_TEST=1 with that dynamic combo has no pixel file. Vertex static 0.

- Vertex: output_0 = vBlendColorTint (VertexPaintTintColor) as it is; UV and colour as csgo_complex's.
- `_24079` = clamp(input_0, 0.001, 1). Samples at input_3.xy: g_tColor, g_tAmbientOcclusion, g_tNormal.
- Normal: csgo_complex's decode and frame; when g_fTextureNormalContrast != 1 (lines 346-378) XY x the contrast and
  a second Y negation on a face that isn't a flipped back face (so that face's Y ends un-negated).
- Roughness `_11005` = max(saturate(((g_tNormal.b - 0.5) x g_fTextureRoughnessContrast + 0.5) x
  g_fTextureRoughnessBrightness), the geometric floor). F0 = g_flReflectance; no metalness.
- Line 1273: `_13436` = the view's occlusion x (g_tAmbientOcclusion.r x mix(1, pow(v.w,
  g_flVertexAmbientOcclusionPower), g_flVertexAmbientOcclusionAmount)).
- Line 1274: albedo = max((vec4(g_tColor.rgb x input_4.rgb, 1) x g_mTextureColorAdjust).rgb, 0) x (mix(0, pow(v.x,
  g_flHeightGradientPower), g_flHeightGradientAmount) + 1); line 1276: output alpha = g_tColor.a.
- S_TINT_MASK (400): the tint through mix(c, c x input_4.rgb, g_tTintMask.r) before the matrix.
- S_TRANSMISSIVE_BACKFACE_NDOTL (416): g_tTransmissiveColor at the UV, or the adjusted albedo with
  g_bUseAlbedoForTransmissive; g_mTransmissiveTextureColorAdjust with g_bApplyColorCorrectionToTransmissiveColor;
  x input_4.rgb; g_bTransmissiveShadows. How the lighting uses it: unread.

Unread: the vertex program's animation (S_VERTEX_ANIMATION, S_FOLIAGE_ANIMATION, g_tNoiseMap), S_ANIMATED_SHADOWS,
S_FOLIAGE_UV_ANIMATION, the alpha test's program.

## csgo_glass (2026-11-18; 97 materials)

Pixel static 16 (S_SHADER_QUALITY), dynamic 0, 1,022 lines; vertex static 0 (output_2 = the UV twice, output_3 =
the instance colour rgba, linear).

- o `_6671` = saturate(g_tGlassDust.a x input_3.a) x (g_flTranslucencyRemap.y - .x) + g_flTranslucencyRemap.x.
- t `_20059` = g_tGlassTintColor.rgb x mix(1, input_3.rgb, g_flModelTintAmount).
- Normal as csgo_complex's; roughness `_11004` = max(g_tNormal.b x input_3.a, the geometric floor).
- Line 919: L `_20321` = the direct diffuse + the ambient x (1 - the specular terms) + `_13137` x
  (g_tGlassTintColor.a x o). Line 920: `_6860` = o x g_tGlassDust.rgb x L.
- `_8674` (through) = (1 - mix(0.04, 1, pow(1 - max(0, V.N), 5))) x pow(t, 1 / max(0.01, sqrt(1 - 0.4444444 x (1 -
  (V.Ng)^2)))) x (1 - o), N the shading normal, Ng the geometric one.
- Line 946: rgb = `_6860` + the specular terms + through x o x g_tGlassDust.rgb x L x pow(t, 1.6); then fog (which
  also scales `through` by 1 - the fog amount); line 824: output = (rgb, luminance(through)).
- Render states: the stencil test only (NotEqual 3, read mask 1), depth as F_DISABLE_Z_BUFFERING says; no blend
  state listed. Both textures are sRGB reads (the table).

Unread: S_PAINT_VERTEX_COLORS, S_VERTEX_BREAK_ANIMATION (S_OPAQUE_CUBEMAP_REFRACTION and g_flRefractMinRoughness:
read 2026-11-19, the section above).

## Shaders dumped with no pixel file for the usual combo (2026-11-18)

csgo_static_overlay (pixel static 112, dynamic 8) and csgo_decalmodulate (pixel static 0, dynamic 4) wrote only a
vertex program for `S_SHADER_QUALITY=1,D_BAKED_LIGHTING_FROM_LIGHTMAP=1`: their valid combos differ (their
<shader>_combos.txt). Their .vfx gives the render states: both DepthBias -64, DepthWriteEnable false, a stencil test
NotEqual (read mask 1; csgo_decalmodulate ref 3, write mask 254); csgo_static_overlay BlendEnable, DstBlend
`F_BLEND_MODE == 3 ? One : InvSrcAlpha`, F_BLEND_MODE 0..6 = Opaque, Translucent, Alpha Test, Mod2x, Additive,
Multiply, ModThenAdd.

## The exported base colour (2026-11-18)

VRF's glTF export writes a material's baseColorFactor = the draw's tint x the vmat's g_vColorTint in linear:
measured on ze_resident_evil_3's world glb (15 materials with a non-white g_vColorTint: 14 carry exactly it, the
15th it times an object tint; 220 more carry only an object tint) and de_vertigo's (6 of 8). So a port reads the
object's tint as three's `diffuse / g_vColorTint` (glsl-common.js cs2Obj). Whether g_vLayer1Tint is folded in the
same way: not seen (every sample's was white).
