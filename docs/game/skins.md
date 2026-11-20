# Weapon skins (client_20261015.dll)

A paint kit on a weapon, drawn as CS2 draws it: the kit's composite material (a `.vcompmat`) run on the weapon's own
material, its generated g_tColor / g_tMetalness put on the weapon in first person, on other players and on the ground.
The runtime is web/src/cs2web/client/fx/skins/, the server's part web/server/cs2web/econ/weapon-paints.js, the bake
`lasers-bake --weapon-skins` (bake/WeaponSkinsBake.cs) + tools/skin-shaders.mjs into web/public/ze-skins (BAKING.md).

## The textures: CS2's own files, linked from vpkstuff

The composite reads CS2's compiled textures themselves: the browser fetches `/cs2-paint/<path>.vtex_c` and uploads
each mip level in its stored format (client/fx/skins/vtex.js: VRF's resource / Texture.cs layout, LZ4 mips), so the GPU
decodes BC7 / DXT1 / ATI1N / ATI2N as CS2's does and samples an ATI1N as (r, 0, 0, 1). No texture is decoded or
re-encoded by us. The files come from the paint assets folder (server/cs2web/econ/paint-assets.js): in dev vpkstuff's
extract on a share (ZE_PAINT_ASSETS), linked, never copied; in production the files the bake
lists (`web/public/ze-skins/textures.json`) are copied to the server by `node tools/paint-assets.mjs`. The few the
share lacks (3 shotgun shell textures) the bake writes raw from pak01 into `ze-skins/vtex/`, served after the share.

Checked 2026-11-17: all 1,424 listed files on the share are byte for byte pak01's (CS2 build of 2026-10-15); every
listed texture parses to VRF's size and level count (skins-test.mjs); the AK-47 | Oiled composite from the raw files
has the same mean colour / metalness as from the old VRF-decoded PNGs (137,134,126 / 255,104,184). The level chains
stop at 4 x 4 (three uploads them as immutable storage of that many levels, so trilinear stays complete). ze-skins went
from 686 MB (3 weapons' decoded PNGs) to 34 MB for all 35 weapons and 645 kits. Formats in use: BC7 118 files of the
first 197, ATI2N 44, ATI1N 28, RGBA16F 4, RGBA8888 2, DXT1 1 (WebGL 2's bptc / s3tc / rgtc extensions: a browser
without one draws that weapon stock and logs why).

Only Valve's raw files are taken from vpkstuff; its renderer, recipes and decoded PNGs are not used (ours runs CS2's own
composite program and shaders). Reference for what's still open: the vpkstuff project has the full skin work
(its CompositeResolver in C#, gloves, knives, stickers): read it before tracing any of the open items below again.

## The composite request (client)

| address | what |
| --- | --- |
| 1807fa510 | builds the weapon item's composite on the weapon entity: the kit's .vcompmat, the target material, an `econ_instance` container |
| 1807fa62c | the legacy kits' path: `weapons/paints/legacy/` + the paint kit's name + `.vcompmat` (items_game paint_kits[id].composite_material_path otherwise) |
| 1807fa7e7 / 1807fa9db | econ_instance's variables: g_flWearAmount (the item's wear, FLOAT1, vfn +0x28), g_nRandomSeed (its seed, vfn +0x20) |
| 1807fab0f | the in-game resolution: "low-res weapon", 0x200 (512) |
| 1807fab37 | `missing_paintkit.vcompmat` when the kit's own isn't there |
| 18077b9f0 / 18077d840 | the include merge and the request's container merge: not disassembled (compmat.js UNSETTLED) |
| 180797dc0 | the team intro's item lookup for a spot's weapon: not read (weapon-paints.js TODO) |

## The composite system (client)

| address | what |
| --- | --- |
| 1814d441e | the mutator switch over CompMatPropertyMutatorType_t (compmat.js) |
| 1814d4481 | RANDOM_ROLL_INPUT_VARIABLES: the seeded roll (UniformRandomStream), its draw order, a missing / unbounded variable's burned draws (skins-test.mjs) |
| 1814d5191 | GENERATE_TEXTURE: the generator material's shader drawn over the target's UV square (customweapon.js) |
| 1814cd861 | the render size: min(_texgen_resolution, the request's), then the power of two at or below |

csgo_customweapon's programs come from csgo_customweapon_vulkan_50.vcs (every static combo, SPIRV-Cross's GLSL
backend, rewritten to GLSL ES 3.00 only in spelling: tools/skin-shaders.mjs). The pixel shader's static combo index is
S_PAINT_STYLE + 9 x (S_OVERRIDE_NORMAL + 2 x (S_USE_ALL_MASKS + ... S_PATINA_AGE)), least significant first (customweapon.js
psCombo; each of the 1152 program files' headers checked against it in skins-test.mjs). Dynamic expressions are VRF's
VfxEval text evaluated in float32 (shader-vars.js).

## A kit's own normal map

A program that COPY_PROPERTYs a paint's g_tNormal over the weapon's (236 weapon / kit pairs in the catalog: the
hydrographics, gunsmiths, workshop kits; all ATI2N with codec 12) has that normal drawn as the weapon's normal map
(client/fx/skins/normal.js). The weapon models' own normal maps in their glbs are VRF's export of the weapon's g_tNormal:
the file decoded, then its codec applied (ValveResourceFormat TextureDecoders/Common.cs ApplyTextureConversions:
Decode_HemiOct for HemiOctRB, then ReconstructNormals for NormalizeNormals; green as stored, no flip). The codec is
VRF's Texture.RetrieveCodecFromResourceEditInfo (the file's CompileTexture special dependencies: "Mip
HemiOctIsoRoughness_RG_B" gives HemiOctRB 4, "Image NormalizeNormals" 8; Dxt5nm 16 for a DXT5 with NormalizeNormals;
a BC7 with both drops NormalizeNormals), written by the bake into textures.json as `codec`. normal.js runs that maths on
the GPU over the file's own level at or below 1024 (texelFetch, each texel rounded to a byte as VRF's decoder hands them
over), into an RGBA8 target with generated mips.

Checked 2026-11-17: the AK-47's ak47_default_normal (ATI2N, codec 12) decoded so matches the AK glb's PNG to a mean
1.5 / 255 a channel (the glb was resized from the 4096 level to 1024); p90_container_normal decoded on the GPU against
the same decode offline (BC5 by the spec's interpolation): 3 texels of 4 exact, one 2 / 255 apart (the GPU's RGTC
interpolation keeps more than 8 bits; CS2's GPU reads the file the same way).

## StatTrak

The module (client/fx/skins/stattrak.js, put on by paintWeapon for a paint whose count is >= 0):

| address | what |
| --- | --- |
| client 1807ff090 | the weapon entity's spawn (C_CSWeaponBase; its item view at +0x1268): calls 180801e30 (StatTrak), 180801390 and 1808002d0 (the other econ attachments: not read) unless +0x1b22 or 1811783b0 |
| client 180801e30 | the StatTrak module: only for an item with the attribute hash 0xc8d7255e and a kill eater value (181187750; or the global +0x58); `weapons/models/shared/stattrak/stattrak_module.vmdl`, `stattrak_module_knife.vmdl` when the item's class name has "weapon_knife" (V_stristr_fast); a C_StattrakModule spawned with model, parentname (the weapon), parentAttachmentName (18078ac90), useLocalOffset 1; +0x1270 = is a knife |
| client 18078ac90 | the attachment: "stattrak_legacy" when the model's current body group choice (the group DAT_181bbe238) ends with "_legacy" and the model has the attachment hash 0x0dd0640f, else "stattrak" |
| client 180806f40 | registers the render attribute "$ent_stattrak" ("Stattrak Integer Display Value", CEntityStattrakDisplayValueRenderAttribCallback, vtable 0x18221c5f0) |
| client 1807e4e80 | its callback (vtable slot 0, 0x181bd6c68): the entity's (or its owner weapon's: vfn +0x210 type 5 / 7) item, 181187750's kill eater count, else 0 |
| server 180952250 | the kill handler: an enemy kill calls 1809202a0(the inflictor weapon's item, killer, victim, 0, 1, null); a teammate kill takes the "#SFUI_Notice_Hint_careful_around_teammates" branch past it |
| server 1809202a0 | the increment: the item's "kill eater" attribute; killer != victim; the killer's CSteamID (180b56340) valid (universe 1..4, account type 1 with instance 1 and a non-zero account, or type 9) and its account == the item's (+0x58: the owner); the victim's the same; the victim's vfn +0xc20 false; then the attribute += amount and GC message 0x432 (killer account, victim account, item id, event type, amount) |

The digits: both display materials (stattrak_module_display, _display_knife) are csgo_weapon with F_STATTRAK and
`g_nStatTrakValue` = `return $ent_stattrak;` (range -1..999999). csgo_weapon_vulkan_50's vertex shader, static combo 12
(S_STATTRAK; read from `lasers-bake --shader-src csgo_weapon --glsl`): a vertex with vTexCoord.y < 0 is digit slot
d = floor(u) - 1, i = clamp(int(d), 0, 5), q = uint(value) / {100000, 10000, 1000, 100, 10, 1}[i], and its u (the one
after g_vTexCoordXform, the identity on both materials) becomes u - d * 0.0625 + ((q != 0 || i == 5 ? 1 : 0) + q % 10) *
0.0625: column 0 of the digit atlas for a leading zero, 1..10 for 0..9. The module glbs keep those UVs (u 1..6.37,
v -1..-0.92, VRF's export); stattrak.js puts the same maths in three's uv_vertex. The attachments come from the bake
(index.json weapons[cls].att: VRF's compiled CAttachment, its first influence's bone, offset and rotation), placed in
the bone's frame (Source axes, metres in the glb) with the glb's axes turned into Source's (fp/util.js SOURCE_QUAT).
Checked 2026-11-17: the P90 with count 1337 draws "1337" behind two column-0 slots.

The count: econ/stattrak.js wraps game.kill with 1809202a0's rules (the item: the paint on the attacker's slot of the
killing weapon class, its inventory row and owner kept off the wire on the paint: weapon-paints.js withItem; a Steam
player killing a Steam player, not a bot; an enemy; the owner's own item). The new count goes out in the player's
paints message, and ze_inventory.kill_eater (migration 012, our Game Coordinator's copy of the attribute) is bumped.
Not here: the module on other players' bodies (world/body-weapon.js draws a body's weapon meshes batched: the module
isn't in its list), the count on another player's held weapon updating without a repaint, the KillEaterRank names.

## Knives

The 20 econ knives (items_game prefab `melee_unusual`, defs 500..526, both sides, flexible_loadout_slot melee) are in
data/items.js as `econ: true` (tools/item-list.mjs): a loadout may wear one in its melee position (the Inventory's
Equip, which also picks the skin item), never offered by the stock picker. Their viewmodels are baked like the default
knives (tools/bake-fp.mjs: weapons/models/knife/knife_<name>/weapon_knife_<name>.vmdl and its clips under
animation/anims/viewmodel/knife/knife_<name>, on viewmodel_knife.vnmgraph+<variation> (navaja: +navajo), the butterfly,
karambit and talon on graphs of their own: viewmodel_knife_butterfly / _karambit / _talon.vnmgraph; inspects graphs
viewmodel_inspects+knife_<v>, none for the butterfly), into web/public/weapons/fp (12 to 19 clips each).

The server (econ/weapon-paints.js syncPaints): the knife slot's stock knife (weapon_knife, ZR's weapon_knife_t) takes
the side's melee item when it is an econ knife the player owns a skin of (econKnife); the paint goes out keyed by that
knife's own class, and a vanilla knife (no finish) is paint kit 0. The weapon stays weapon_knife in the game: every
CS2 knife's vdata has the same numbers. The client draws the class's chassis (fp/chassis.js knifeChassisFor: CS2's vdata
names, weapon_knife_widowmaker -> knife_talon ...) in first person (game.js syncWeapons -> vm.setKnife) and on bodies
(peers.js st.model -> body-weapon.js, the viewmodel bake's model as for the T knife; the anim graph keeps weapon_knife),
painted by its kit and with the knife StatTrak module (stattrak_module_knife). TODO(trace): GiveNamedItem's econ
lookup (server.dll: that the loadout's knife replaces the given weapon_knife / weapon_knife_t, the zombie's included).

## The server

The econ item lives on the weapon entity: a weapon given to a player (not picked up) takes the owner's loadout skin for
its class, checked against their ze_inventory rows (the Steam account's, else the guest token's); it keeps its paint
through drops and pickups. Messages `paints` (a player's held and loadout paints) and `wpaint` (a world weapon's).
TODO(trace): GiveNamedItem's econ lookup (which spawns / buys get the loadout item).

## Open

- The composite's mip chain and BC7 copy (composite_material_use_bc7): WebGL's generateMipmap here.
- A shader variable defined twice in one table (the uv transforms): which one the constant buffer gets (`DUPLICATE`).
- Stickers, name tags: not drawn. StatTrak and gloves on other players' bodies (above, below).

## Gloves

- The models: agents/models/shared/arms/glove_<type>/glove_<type>.vmdl (bloodhound, brokenfang, fingerless, fullfinger,
  handwrap, hardknuckle, hydra, motorcycle, slick, specialist, sporty; client 18077d200 precaches them with
  glove_cloth_collision and the agents). Exported 2026-11-17 into web/public/weapons/fp/gloves/<type>.glb (+
  <type>_armrig.glb on weapon_arms' 82 bones for 8 of them) by vpkstuff's `--viewmodel-anim-spike` without
  `--skip-shared`: what weapons/fp/fp.js's stock arms load (`gloves/<gloveId>.glb`). CS2's arrangement (fp.js): the
  glove model is the whole first-person arm and the agent adds only its sleeves, its `firstperson_hide_default_gloves`
  mesh group (client strings at 0x181bb7170; `thirdperson_hide_default_gloves` 0x181bb7138 for the body; the econ item
  is the pawn's `m_glovesItem`, 0x181bbb8d8: 180792630 / 180787390, unread).
- The item: items_game's glove items are prefab hands_paintable (sporty_gloves 5030, studded_bloodhound_gloves 5027,
  ...: model_player agents/models/shared/arms/glove_<type>/glove_<type>.vmdl), worn in the loadout's clothing_hands
  position (the defaults ct_gloves / t_gloves); data/items.js lists them `econ` (tools/item-list.mjs).
- The paint's program: client 181138380(kit, out, prefix) gives the kit's composite_material_path when it has one,
  else `Format("%s%s.vcompmat", prefix, kit name)` ("default" or an empty name: none); the prefix is
  "weapons/paints/legacy/" for a weapon (1807ff680) and "gloves/paints/" for gloves (180c65330). Every catalog glove kit
  is at gloves/paints/<name>.vcompmat (72; tools/weapon-skins.mjs uses the same rule for both).
- The request: client 180c65330 (C_WorldModelGloves' spawn: the glove model bone-merged on the pawn, "!bonemerge",
  useParentRenderBounds) builds the econ_instance as g_flWearAmount (vfn +0x28), g_nRandomSeed (vfn +0x20) and
  g_nRandomSeedAlt = seed + 1, at 0x200 (512) "low-res gloves" (compmat.js econ.alt).
- The program (gloves/paints/_shared_paint_generic.vcompmat, included by each kit's): match filter composite_target;
  containers target, econ_instance, paint (the kit's vmat), target_instance, handedness / material_seed
  (VARIABLE_FROM_TARGET_ATTR "left" / "seed_offset": the glove material's int attributes, the bake's `ia`), and
  instance_params; the roll from g_nRandomSeed (or g_nRandomSeedAlt where seed_offset is 1); INIT target_instance, the
  paint's F_CLOTH_SHADING / F_ANISOTROPIC_GLOSS copied, then GENERATE_TEXTURE g_tColor (F_OUTPUT_MODE 0), g_tMetalness
  (2), g_tNormal (1), g_tAmbientOcclusion (3), g_tAnisoGloss (4, when the paint has F_ANISOTROPIC_GLOSS), each with
  g_fWearProgress = the wear and g_bFlipFixup on the left hand (unless the paint flips already), and g_flSheenScale
  copied when the paint has it.
- csgo_customglove (csgo_customglove_vulkan_50): features F_BACKWARDS_COMPATIBILITY (the classic kits 0, the
  volatile_02 ones 1), F_ANISOTROPIC_GLOSS, F_CLOTH_SHADING, F_PATTERN, F_PATTERN_PAINT, F_PUFFY_PAINT, F_TINT_ID,
  F_OUTPUT_MODE; 6 pixel programs, the static combo S_BACKWARDS_COMPATIBILITY + 2 x S_ANISOTROPIC_GLOSS + 4 x
  S_TINT_ID (ids 0 1 2 3 5 7), 2 vertex programs (S_BACKWARDS_COMPATIBILITY, its UV attribute named vTextureCoords);
  the output is the uniform g_nOutputMode = F_OUTPUT_MODE: 0 colour, 1 the normal hemi-octahedral in RG with roughness
  in B, 2 (0, metalness, cloth), 3 occlusion, 4 the anisotropic gloss, each SrgbGammaToLinear'd into the sRGB target.
  Its colour-adjust matrices are VfxEval's MatrixMultiply / MatrixColorTint2 / MatrixColorCorrect2 over
  TextureAverageColor (a file's Reflectivity, textures.json `refl`): vfx-matrix.js, VRF's port (TODO(trace):
  materialsystem2's own). The sRGB reads are the variable table's Sampler2D flags (they match vpkstuff's interface
  dump). Converted by tools/skin-shaders.mjs into web/public/ze-skins/shaders/csgo_customglove.
- 22 to 38 (texture, sampler) pairs a program, 18 to 22 distinct files a kit: more than WebGL 2's 16 units, so the
  program reads them from 2 or 3 texture arrays (tex-arrays.js: each layer the file's own levels at its texel
  density, square files sampled exactly; 8 bits a channel; three uploads only an uncompressed array's level 0, the
  rest go up by hand).
- On the glove model (glove-maps.js): the colour as the map; the normal decoded as VRF decoded the glove's stock
  normal (Decode_HemiOct); an ORM of occlusion, roughness (the normal's B) and metalness (output 2's G: vpkstuff's
  reading, TODO(trace) csgo_character's g_tMetalness read).
- First person (weapons/viewmodel.js setGloves): the glove model as the arm (fp.js stock arms:
  weapons/fp/gloves/<type>.glb) with the pawn model's sleeves over it, its firstperson_hide_default_gloves group baked
  as ze-players/<key>/<key>_sleeves.glb (`lasers-bake --zclass-sleeves`, sleeves.json: 15 models; the zombies' group is
  empty: the glove arm alone), painted per hand. The server: the side's clothing_hands item when it is an owned econ
  glove (weapon-paints.js econGloves), sent as the paints message's `gl`.
- Checked 2026-11-17: Sport Gloves (sporty_light_blue, seed 7, wear 0.15) composites both hands (the hexagon pattern
  rolled apart by seed / seed + 1), a flat-centred normal with the stitching relief, occlusion 0.75 .. 1; drawn on the
  first-person arm with Master Chief's sleeves.
- Left: the gloves on bodies (C_WorldModelGloves bone-merged on the pawn, the model's thirdperson_hide_default_gloves
  group), g_tAnisoGloss (24 kits: no three.js input), the volatile_02 kits checked, the left / right pattern flip
  compared against CS2.

## Stickers

An item's stickers drawn on its weapon (web/src/cs2web/client/fx/skins/stickers.js, sticker-glsl.js; the template
tools/sticker-shader.mjs; the server's list econ/weapon-paints.js stickersOf). A sticker is no texture of its own on the
weapon: a second composite request copies each sticker kit's material keys into the weapon's csgo_weapon material, and
csgo_weapon's F_STICKERS pixel pass draws up to five of them over the weapon's surface in its second UV set.

| address | what |
| --- | --- |
| 1807ff680 | the weapon's econ requests: the paint's (1807fa510 path), then 180788e00 + 1807849c0 and a second request on the same entity (vfn +8 of entity+0x610) when the item has a sticker |
| 181137060 | the item attribute set per sticker slot, 7 sets cached: "sticker slot %d id / wear / scale / rotation / offset x / offset y / schema" |
| 180788e00 | item slots 0..5 -> entries (stride 0x28: +0 sticker_material string, +8 / +0xc offset x / y, +0x10 scale, +0x14 rotation, +0x18 wear, +0x1c UICameraRotation, +0x24 deprecated): attribute 0 the kit (181137800 lookup, kit+0x20 its sticker_material), 1 the wear; an entry per slot index (padded with empty ones); slot 5 takes the first empty entry once there are more than four, else is appended; attribute 6 the schema (-1: the slot's own index; slot 5 and 182215c90 >= 0: that global, unread); then 18078d460; then (param_4: not a preview) rotation += attr 3 * 0.0027777778, offset x += attr 4, offset y += attr 5. Attribute 2 (scale) is not read here |
| 18078d460 | the weapon model's keyvalues `StickerMarkup` (hash 9d901f54): the entry whose `Index` is the schema and whose `LegacyModel` equals 18078db50 (the weapon draws its legacy body) -> Offset (2 floats) +8, Rotation +0x14, Scale +0x10, UICameraRotation +0x1c, Deprecated +0x24 |
| 1807849c0 | the request: per non-empty entry k, loose variables g_bEnableSticker%d (BOOLEAN 1), g_flSticker%dWear (FLOAT1), g_vSticker%dOffset (FLOAT2: x +8, y +0xc), g_flSticker%dRotation (FLOAT1), g_vSticker%dScale (FLOAT1, though the shader's is a Float2) into container "econ_instance_vars", and a material container "sticker%d" = Format("stickers/%s.vmat", the sticker_material); the program weapons/stickers/dev/_shared_sticker_generic.vcompmat, the request's name "stickers" (+0x70). 1807836c0: the souvenir capsule's (sticker_case_souvenirs.vcompmat), 1807843a0 / 180c64760 patches (_shared_patch_generic.vcompmat): not read |
| scenesystem 1800c8490 | the view constants' dump: m_viewConstantBufferData g_flRealTime, g_vCameraPositionWs, g_vCameraUpDirWs, g_vCameraDirWs ... (the names the sticker pass's PerViewConstantBuffer_t._m0 / _m7 / _m8 / _m9 are, by their use) |

The program (_shared_sticker_generic.vcompmat): match filters MATERIAL_SHADER "csgo_weapon.vfx" and ATTRIBUTE_EXISTS
"composite_inputs"; containers target_instance, econ_instance_vars (g_bEnableSticker0..4 false, g_flSticker0..4Wear 0),
sticker0..4 (stickers/dev/sticker_default.vmat); mutators INIT target_instance, COPY_MATCHING_KEYS econ_instance_vars,
then per slot k COPY_KEYS_WITH_SUFFIX sticker<k> "Sticker0" -> "Sticker<k>" when econ_instance_vars.g_bEnableSticker<k>
== 1. A sticker material (csgo_weapon_sticker.vfx) holds its look as *Sticker0 keys: g_tSticker0, g_tNormalRoughnessSticker0,
g_tSfxMaskSticker0, g_tHoloSpectrumSticker0, g_tGlitterNormalSticker0, g_bHolographic / Glitter / Metallic /
PaperBacking / SelfIllum / AutomaticPBRColorFitting / LegacyTintMultiply / PreserveRoughnessSticker0, colour tint,
saturation, boosts, wear bias and scratches.

The pass: csgo_weapon's pixel static combo 512 (S_STICKERS alone; S_ENABLE_ADJUSTMENTS 1, S_MODE_TOOLS_VIS 2, S_ALPHA_TEST
4, S_TRANSLUCENT 8, S_ADDITIVE_BLEND 16, S_TINT_MASK 32, S_GLITTER 64, S_ENABLE_SFX_MASK 128, S_SELF_ILLUM 256, S_STICKERS
512, ...: the combos file's order). The vertex shader passes vTexCoord2 (the model's second UV, glTF TEXCOORD_1) as
input_4.zw. Before the slots: g_tStickerWepInputs at the uv (x: where a sticker may be, y: a wear bias), the slots run
only where x > 0 and vTexCoord2.x > -1. Each slot (the five blocks are one text: tools/sticker-shader.mjs checks it; slot 0
has the start values folded in) reads the previous slot's state and writes it: albedo, the tangent-space normal, roughness
(2), metalness, occlusion, g_tMetalness.z, F0 (0.02 -> 0.04 under a sticker), self-illumination, glitter, a mask (x
coverage, w coverage x (1 - wear)), the alpha. A slot: skipped when its scale's x or y is 0 or the mask is 0; the sticker
uv = rotate(((vTexCoord2 - 0.5) - offset) * |scale.x|, rotation x 2pi) + 0.5, nothing outside [0, 1]; the sticker's alpha
x 12.75; an edge darkening sampled 0.01 along the camera's (right, up) projection of the normal when the sticker's LOD
(textureQueryLod) < 4; its normal (g_tNormalRoughnessSticker hemi-oct, y flipped) added x 2 x alpha to the weapon's normal
read at LOD max(sticker LOD, 3); occlusion min(pow(AO at that LOD, 0.75), 0.5 alpha + 0.5); glitter (g_tGlitterNormal
point and trilinear, the sparkle by reflect(view, normal) x 12); the PBR colour fitting (g_vAlbedoLevels /
g_vMetallicAlbedoLevels / g_vDarkMetallicAlbedoLevels: the expressions in the variable table); holo (g_tSfxMask's x the
amount, the spectrum at (mask.y + N.V + V.sun, mask.z), g_vHoloAlbedoLevels); wear (g_tStickerScratches, the wear bias,
the paper backing's grey); the editor's peel / highlight / apply-slot paths (g_nActiveStickerApplySlot, g_flHighlightTime:
off in game). After the slots: albedo -> diffuse x (1 - metal)^g_flMetalnessTransitionBias and F0 mix, the self-
illumination added to the lit colour, the glitter to the specular.

What the port does (sticker-glsl.js header): three's base values in, CS2's out at three's normal_fragment_maps; the
material's switches (Bool / Int: g_bHolographicSticker<k>, glitter, paper backing, ..) GLSL constants, so a slot holds
only its kind's code, and its numbers (wear, offset, rotation, scale, tints) uniforms, so one program serves every
item with the same sticker kinds in the same slots (2026-11-19: before, every number was a constant and each item,
each scrape, its own program: 3.0 s cold for a 4-sticker AK on an RTX 4070, again for each new wear; now 3.7 s for
the first of a layout, 73 ms for the next. Against the constants, 90 of 2.4M colour values of two 1200 x 500 shots
moved, by at most 7: the compiler's folding of the constants, not the formula; CS2 itself reads them from the
material's constant buffer). The material is compiled before it goes on (weapon-skins.js `opts.prepare`: the
viewmodel's and the map weapons' prepareModel, a 120 s cap): the weapon shows without its stickers until then (a
frame stalled 2.4 s on the link before; with it no frame over 170 ms, that one the composite's texture build).
The textures from two texture arrays (tex-arrays.js:
WebGL's 16 units; the levels kept texel for texel, explicit levels shifted by the file's offset). Checked 2026-11-17
(client/dev/sticker-preview.js, the weapon drawn alone): the AK-47 with a paper, a holo, a glitter and a foil sticker in
its four markup slots; wear 0.35 / 0.7 / 1 scrape them, rotation 45 turns one, offset y 0.03 moves one into the weapon
mask's cut.

UNSETTLED / TODO(trace):
- a FLOAT1 loose variable on a Float2 material variable (g_vSticker%dScale): taken as (x, x). Evidence: 59 of 168
  markup entries' Scale differs from the vmat's g_vSticker%dScale, and the 5th slots (AUG, CZ75, Deagle ...) have vmat
  scale 0, so CS2 draws them only if the float replaces it with a y that is not 0
- the sticker request's target: the weapon's material instance after the paint request (here: the paint's result, else
  the weapon's own material); how the request's containers merge into the program's (as econ_instance)
- COPY_KEYS_WITH_SUFFIX: every key of the source with the suffix (not only the keys the destination declares)
- PerViewConstantBuffer_t._m8 / _m9: up / direction by the geometry (cross(dir, up) = right); _m0 a constant (the
  editor's timers only); PerViewConstantBufferCsgo_t._m2.x (glitter scale 2.5 / 1.75): 0; PerViewLightingConstantBufferGpu_t._m16
  (the holo's second direction): the scene's first directional light, toward it
- the sampler states (g_sAniso, g_sPoint, g_sAnisoClampV, g_sTrilinearWrap, g_sUserConfig): read their descriptors
  from the vcs; textureQueryLod: the isotropic LOD
- the self-illumination and glitter go to three's emissive; F0, the pearl mask, the alpha and the sticker mask are not
  used (three's lighting is not CS2's)
- the sticker_gaps material (F_TRANSLUCENT, no composite_inputs: the program does not match it) draws as dark lines,
  stickers or not (how CS2 draws it: unread)
- 18078db50 (legacy body): stickers.js asks for a body_legacy mesh as stattrak.js does
- the stickers baked: the four capsules' (tools/case-list.mjs STICKER_CAPSULES, read back by tools/weapon-skins.mjs: 117)

### Sticker items (the econ)

- The capsules (prefab sticker_capsule; their loot lists tiered as a case's, entries "[sticker kit]sticker") are cases
  in the catalog: each sticker a row of weapon 'sticker', def 1209 (items_game `sticker`, CSGO_Tool_Sticker), paint
  its kit id, rarity the kit's item_rarity, image econ/stickers/<sticker_material>; opened (econ/inventory-store.js), a
  ze_inventory row of kind 'sticker'. No StatTrak, no float (econ_cases.stattrak false).
- Applying (CS2: popup_capability_can_sticker, work_type can_sticker; the GC applies): econ/stickers.js checks both
  items are the requester's, the weapon takes stickers (not a knife or gloves) and the slot is one of its model's
  StickerMarkup indices 0..4 and empty, then writes { slot, id, wear 0, schema -1, x, y, rot } into the weapon's
  attrs.stickers and deletes the sticker item, in one transaction. Scraping (work_type remove_sticker): wear + 0.1 a
  scrape, the one at 0.9 or more removes it (TODO(trace): the GC's step). The placement's limits (x, y +-0.1, rotation
  +-180) are ours (TODO(trace): CS2's drag placement, popup_can_apply_pick_slot.vts).
- The Inventory (home/cases/sticker-apply.js): Apply Sticker on a sticker (the weapons with an empty slot, then the slot
  and placement previewed on the weapon: fx/skins/weapon-shot.js, the stock model with its paint and stickers), Scrape
  Sticker on a weapon with stickers. The loadout goes to a server on join, so an applied sticker is in the next match.
