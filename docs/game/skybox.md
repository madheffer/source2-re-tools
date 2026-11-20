# The 3D skybox and the 2D sky (client.dll 20261015, sky.vfx, csgo_unlitgeneric.vfx)

Read 2026-11-19 (branch agent/mapbake-sky) with ReVa (client_20261015.dll) and tools/re (strings, strva, riprefs on
source2-compiler's tools/re/binaries/client_20261015.dll), and `lasers-bake --shader-src` over shaders_vulkan_dir.vpk.
Ported in web/src/world/render.js (renderSkyPass), lighting.js (skyFog), unlit.js; baked by bake/SkyboxBake.cs.

## Where the skybox lives (the bake)

- A map's `skybox_reference` names `maps/<dir>/<name>.vmap`. CS2's own maps ship that world as a vpk of its own:
  game/csgo/maps/prefabs/de_dust2/de_dust2_skybox.vpk, prefabs/de_mirage/3dskybox_mirage_legacy.vpk,
  prefabs/de_vertigo/skybox2.vpk, prefabs/de_inferno/inferno_skybox.vpk (a workshop item carries it inside the item).
  Its world is `maps/<dir>/<name>/world.vwrld_c`: world nodes, its own lightmaps and env_cubemap_array.
- The team maps' sky materials (materials/skybox/sky_de_dust2.vmat ...) are in CS2's pak01, not the map's vpk.
- de_vertigo's own env_sky starts disabled; the enabled one (`[PR#]54_sky`, the same sky_de_vertigo.vmat) is in its
  skybox prefab. de_inferno's prefab has an enabled env_gradient_fog.

## AddViewsToSceneSystem: 0x180a39760 (loopmodegame.cpp line 0x4d6)

The reader of r_draw3dskybox (string 0x181ad3088; ConVar object 0x18254e650, registered by 0x1800c0540; its value
byte read at [0x18254e658] + 0x58).

- With r_draw3dskybox on and the sky camera's scale (int16, local_1550) != 0, the skybox view's eye is
  `sky camera origin (local_154c / 1548 / 1544) + the view's eye (view + 0x4a0 / 0x4a4 / 0x4a8) / scale`.
- The fog record `0x180c0d8d0()` = `0x18096a8f0() + 0x13e8` (enabled byte at +100) is copied whole into the skybox
  view's params, with its +0x24 and +0x28 multiplied by 1 / scale. UNSETTLED: that those two are the fog's start and
  end distances (the record's layout is unread; the gradient fog's own cooked record, gradient-fog.md, keeps start
  and end as a pair).
- The sky camera volume (local_1568, found by 0x1807a8240 at view + 0x4a0): its bytes +0x648 / +0x649 copied into
  the view (UNREAD: likely m_bSkyboxReceivesWorldCsm / m_bWorldReceivesSkyboxCsm, strings 0x181bbe320 / 340), its
  handle +0x630, and when +0x639 is set an offset +0x63c..0x644 added to a position (UNREAD).
- The view is handed on through vtable +0x58 of param_1 + 0x60. UNREAD: scenesystem's order of the skybox view and
  the world's (ours: skybox, depth cleared, world: Source's design, a stand-in), the near / far of the skybox view,
  and sky_camera's clip_3D_skybox_near_to_world_far (string 0x181c1ec48, read in 0x1809205f0) and its separate
  skybox fog (enable_separate_skybox_fog 0x181c52860, read in 0x180ad9150; fog_*skybox).

## sky.vfx (the 2D sky)

- VS: the cube at the eye; `output_0 = normalize(position x g_matSkyWsToOs)`.
- PS (BC6H, D_FOG_TYPE 1): the cube sampled at the direction turned by `g_flRotation x 2 pi` about z, with
  `z + g_flHorizonOffset`; x g_flBrightnessExposureBias x g_flRenderOnlyExposureBias x g_vTint (SkyTint); both
  biases go through `Expression(pow(2,this))` (ours: 2^(bias + bias) x tint, the same). Then lerped toward the
  view's fog colour by `saturate(min(maxOpacity, saturate(farDistance x scale + bias)^exponent))`: CS2 fogs the 2D
  sky with the view's fog at one fixed distance. Ours: only env_fog_controller fogs it; g_flRotation /
  g_flHorizonOffset not applied (0 on the team maps read). Combos: D_FOG_TYPE 0..2, D_MIN_ANGULAR_FOG (fog type 2).

## csgo_unlitgeneric.vfx (de_dust2's skybox clouds)

- F_BLEND_MODE: 0 Opaque, 1 Translucent, 2 Alpha Test, 3 Mod2x, 4 Additive, 5 Multiply, 6 ModThenAdd.
- PS static combo 18 (S_BLEND_MODE=4, S_TWOTEXTURE; static radix S_BLEND_MODE x7, S_GRADIENTMODULATION x2,
  S_TWOTEXTURE x2, ...): `g_tColor(uv0) x g_tColor2(uv1) x the vertex colour`, fog (g_bFogEnabled) only on alpha.
- VS: the vertex colour = `mix(1, the instance tint, g_flModelTintAmount) x g_vColorTint`.
- Render states: the features file lists target 0..2 as One / One, no depth write; D_MBOIT_PASS1 / 2 require
  S_BLEND_MODE 1 or 4 (translucent and additive go through MBOIT). VRF decodes the pixel program's per-combo states
  as defaults and the _psrs program's as null: the per-mode factors are UNREAD.
- de_dust2's nuke_clouds_002 (Additive, two textures): both textures white with the cloud in alpha (averages 0.04 and
  0.22); in our client the chunk material has no texture at all, so it adds a flat g_vColorTint over the sky (the
  white sky on de_dust2). Next: draw csgo_unlitgeneric from the skybox's mat/ blocks (the generator) through MBOIT.
