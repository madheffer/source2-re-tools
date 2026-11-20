# Weapon skins: paint kits, StatTrak, knives, gloves, stickers

client_20261015, server_20261105, scenesystem; pak01 (CS2 build of 2026-10-15): items_game, the .vcompmat programs,
csgo_customweapon_vulkan_50.vcs, csgo_customglove_vulkan_50, csgo_weapon_vulkan_50. Texture codecs as
ValveResourceFormat reads them (Texture.cs, TextureDecoders/Common.cs). The vpkstuff project has a full C# skin
resolver (CompositeResolver, gloves, knives, stickers): read it before tracing the open items again.

A paint kit is the kit's composite material (`.vcompmat`) run on the weapon's own material; its generated g_tColor /
g_tMetalness go on the weapon in first person, on other players and on the ground.

## Functions

| Address | Module | What |
|---|---|---|
| 1807fa510 | client | builds the weapon item's composite on the entity: the kit's .vcompmat, the target material, an `econ_instance` container |
| 1807fa62c | client | legacy kits' path: `weapons/paints/legacy/` + kit name + `.vcompmat` (else items_game paint_kits[id].composite_material_path) |
| 1807fa7e7 / 1807fa9db | client | econ_instance variables: g_flWearAmount (wear, FLOAT1, vfn +0x28), g_nRandomSeed (seed, vfn +0x20) |
| 1807fab0f | client | in-game resolution "low-res weapon", 0x200 (512) |
| 1807fab37 | client | `missing_paintkit.vcompmat` when the kit's own isn't there |
| 18077b9f0 / 18077d840 | client | include merge / request container merge (not disassembled) |
| 180797dc0 | client | the team intro's item lookup for a spot's weapon (not read) |
| 1814d441e | client | mutator switch over CompMatPropertyMutatorType_t |
| 1814d4481 | client | RANDOM_ROLL_INPUT_VARIABLES: seeded roll (UniformRandomStream), its draw order, a missing / unbounded variable's burned draws |
| 1814d5191 | client | GENERATE_TEXTURE: the generator material's shader drawn over the target's UV square |
| 1814cd861 | client | render size: min(_texgen_resolution, the request's), then the power of two at or below |
| 1807ff090 | client | weapon entity spawn (C_CSWeaponBase; item view +0x1268): 180801e30, 180801390, 1808002d0 unless +0x1b22 or 1811783b0 |
| 180801390 / 1808002d0 | client | other econ attachments (not read) |
| 180801e30 | client | the StatTrak module |
| 181187750 | client | kill eater value |
| 18078ac90 | client | StatTrak attachment name |
| 180806f40 | client | registers render attribute "$ent_stattrak" ("Stattrak Integer Display Value", CEntityStattrakDisplayValueRenderAttribCallback, vtable 0x18221c5f0) |
| 1807e4e80 | client | its callback (slot 0, 0x181bd6c68): the entity's (or owner weapon's: vfn +0x210 type 5 / 7) item's kill eater count, else 0 |
| 180952250 | server | kill handler: enemy kill -> 1809202a0(inflictor weapon's item, killer, victim, 0, 1, null); teammate kill takes the "#SFUI_Notice_Hint_careful_around_teammates" branch |
| 1809202a0 | server | StatTrak increment |
| 180b56340 | server | CSteamID of a player |
| 18077d200 | client | precaches the glove models with glove_cloth_collision and the agents |
| 180792630 / 180787390 | client | m_glovesItem users (unread) |
| 181138380 | client | (kit, out, prefix): composite_material_path, else `Format("%s%s.vcompmat", prefix, kit name)` ("default" / empty: none) |
| 1807ff680 | client | the weapon's econ requests (prefix "weapons/paints/legacy/") |
| 180c65330 | client | C_WorldModelGloves spawn (prefix "gloves/paints/") |
| 181137060 | client | per sticker slot attribute sets, 7 cached: "sticker slot %d id / wear / scale / rotation / offset x / offset y / schema" |
| 180788e00 | client | item sticker slots 0..5 -> entries |
| 181137800 | client | sticker kit lookup (kit+0x20 sticker_material) |
| 18078d460 | client | weapon model's `StickerMarkup` (hash 9d901f54) |
| 18078db50 | client | the weapon draws its legacy body |
| 1807849c0 | client | the sticker composite request |
| 1807836c0 | client | souvenir capsule's request (sticker_case_souvenirs.vcompmat; not read) |
| 1807843a0 / 180c64760 | client | patches (_shared_patch_generic.vcompmat; not read) |
| 1800c8490 | scenesystem | view constants dump: m_viewConstantBufferData g_flRealTime, g_vCameraPositionWs, g_vCameraUpDirWs, g_vCameraDirWs ... |

## Fields

| Offset | Field |
|---|---|
| C_CSWeaponBase +0x1268 | item view |
| C_CSWeaponBase +0x1b22 | set: skips the econ attachments |
| +0x1270 | = is a knife, set by 180801e30 (the object is not named in the notes: beside the weapon's +0x1268 item view, so likely the weapon) |
| item +0x58 (server, 1809202a0) | the owner's account |
| a global +0x58 (client, 180801e30) | kill eater value when 181187750 has none |
| entity +0x610 | vfn +8: second request (stickers) |
| request +0x70 | name ("stickers") |
| sticker entry (stride 0x28) | +0 sticker_material string, +8 / +0xc offset x / y, +0x10 scale, +0x14 rotation, +0x18 wear, +0x1c UICameraRotation, +0x24 deprecated |
| 182215c90 | global: slot 5's schema when >= 0 (unread) |
| DAT_181bbe238 | body group read for "_legacy" |
| 0x181bb7170 / 0x181bb7138 | strings firstperson_ / thirdperson_hide_default_gloves |
| 0x181bbb8d8 | string m_glovesItem (the pawn's glove item) |

## Constants

| Value | What |
|---|---|
| 0xc8d7255e | kill eater attribute hash |
| 0x0dd0640f | "stattrak_legacy" attachment hash |
| 0x432 | GC message (killer account, victim account, item id, event type, amount) |
| -1..999999 | g_nStatTrakValue range |
| 0.0625 | digit atlas column width |
| 0.0027777778 | sticker rotation attr scale (1/360) |
| 12.75 | sticker alpha scale |
| 0.01 | edge darkening sample distance |
| 4 / 3 | sticker LOD for the edge darkening / normal read min LOD |
| 0.75, 0.5 | sticker occlusion `min(pow(AO, 0.75), 0.5 alpha + 0.5)` |
| 0.02 -> 0.04 | F0 under a sticker |
| 12 | glitter sparkle `reflect(view, normal) * 12` |
| 2.5 / 1.75 | glitter scale (PerViewConstantBufferCsgo_t._m2.x) |
| 1209 | `sticker` item def (CSGO_Tool_Sticker) |
| 500..526 | econ knife defs (prefab `melee_unusual`) |
| 5030 / 5027 | sporty_gloves / studded_bloodhound_gloves |
| codec 4 / 8 / 16 / 12 | HemiOctRB / NormalizeNormals / Dxt5nm / HemiOctRB + NormalizeNormals |

## Textures

- The composite reads CS2's compiled `.vtex_c` files, each mip in its stored format (BC7, DXT1, ATI1N, ATI2N, RGBA16F,
  RGBA8888; LZ4 mips): the GPU decodes them; an ATI1N samples as (r, 0, 0, 1). The files' level chains stop at 4 x 4.
- Codec (VRF Texture.RetrieveCodecFromResourceEditInfo, from the file's CompileTexture special dependencies): "Mip
  HemiOctIsoRoughness_RG_B" gives HemiOctRB 4, "Image NormalizeNormals" 8; Dxt5nm 16 for a DXT5 with NormalizeNormals;
  a BC7 with both drops NormalizeNormals.
- A weapon model's normal map = g_tNormal decoded, then its codec (ApplyTextureConversions: Decode_HemiOct for HemiOctRB,
  then ReconstructNormals for NormalizeNormals; green as stored, no flip). ak47_default_normal: ATI2N, codec 12, 4096 top level.
- A kit's own normal: a program that COPY_PROPERTYs a paint's g_tNormal over the weapon's (236 weapon / kit pairs: the
  hydrographics, gunsmiths, workshop kits; all ATI2N, codec 12) has that normal as the weapon's normal map.

## csgo_customweapon

- Programs: csgo_customweapon_vulkan_50.vcs, 1152 program files.
- Pixel static combo `S_PAINT_STYLE + 9 * (S_OVERRIDE_NORMAL + 2 * (S_USE_ALL_MASKS + ... S_PATINA_AGE))`, least significant first.
- Dynamic expressions: VfxEval text, float32.

## StatTrak

- 180801e30: only for an item with attribute 0xc8d7255e and a kill eater value (181187750; or the global +0x58);
  `weapons/models/shared/stattrak/stattrak_module.vmdl`, `stattrak_module_knife.vmdl` when the class name has
  "weapon_knife" (V_stristr_fast); a C_StattrakModule with model, parentname (the weapon), parentAttachmentName
  (18078ac90), useLocalOffset 1; +0x1270 = is a knife.
- 18078ac90: "stattrak_legacy" when the model's current choice of body group DAT_181bbe238 ends with "_legacy" and the
  model has attachment 0x0dd0640f, else "stattrak".
- Display materials stattrak_module_display / _display_knife: csgo_weapon with F_STATTRAK, `g_nStatTrakValue` =
  `return $ent_stattrak;`.
- csgo_weapon_vulkan_50 vertex shader, static combo 12 (S_STATTRAK): a vertex with vTexCoord.y < 0 is digit slot
  `d = floor(u) - 1`, `i = clamp(int(d), 0, 5)`, `q = uint(value) / {100000, 10000, 1000, 100, 10, 1}[i]`; its u (after
  g_vTexCoordXform, identity on both materials) becomes
  `u - d * 0.0625 + ((q != 0 || i == 5 ? 1 : 0) + q % 10) * 0.0625`: column 0 for a leading zero, 1..10 for 0..9.
  The module models' UVs: u 1..6.37, v -1..-0.92.
- Server increment (1809202a0): the item's "kill eater" attribute; killer != victim; the killer's CSteamID (180b56340)
  valid (universe 1..4, account type 1 with instance 1 and a non-zero account, or type 9) and its account == the item's
  (item +0x58); the victim's the same; the victim's vfn +0xc20 false; then attribute += amount and GC message 0x432.

## Knives

- 20 econ knives (prefab `melee_unusual`, defs 500..526, both sides, flexible_loadout_slot melee).
- Viewmodels: weapons/models/knife/knife_<name>/weapon_knife_<name>.vmdl, clips under
  animation/anims/viewmodel/knife/knife_<name>, on viewmodel_knife.vnmgraph+<variation> (navaja: +navajo); butterfly,
  karambit and talon on their own graphs (viewmodel_knife_butterfly / _karambit / _talon.vnmgraph); inspects
  viewmodel_inspects+knife_<v>, none for the butterfly; 12 to 19 clips each.
- Every CS2 knife's vdata has the same numbers. vdata names map to models (weapon_knife_widowmaker -> knife_talon ...).
- A vanilla knife (no finish) is paint kit 0; its icon is its own image_inventory.

## Gloves

- Models: agents/models/shared/arms/glove_<type>/glove_<type>.vmdl (bloodhound, brokenfang, fingerless, fullfinger,
  handwrap, hardknuckle, hydra, motorcycle, slick, specialist, sporty), precached by 18077d200. weapon_arms has 82 bones.
- In first person the glove model is the whole arm and the agent adds only its sleeves: its
  `firstperson_hide_default_gloves` mesh group (`thirdperson_hide_default_gloves` for the body); the econ item is the
  pawn's `m_glovesItem`.
- Items: prefab hands_paintable (sporty_gloves 5030, studded_bloodhound_gloves 5027, ...; model_player the glove
  vmdl), worn in clothing_hands (defaults ct_gloves / t_gloves).
- Program path: 181138380 with prefix "gloves/paints/" (180c65330); every glove kit is gloves/paints/<name>.vcompmat (72).
- Request (180c65330: the glove model bone-merged on the pawn, "!bonemerge", useParentRenderBounds): econ_instance
  g_flWearAmount (vfn +0x28), g_nRandomSeed (vfn +0x20), g_nRandomSeedAlt = seed + 1, at 0x200 (512) "low-res gloves".
- gloves/paints/_shared_paint_generic.vcompmat (included by each kit's): match filter composite_target; containers
  target, econ_instance, paint (the kit's vmat), target_instance, handedness / material_seed (VARIABLE_FROM_TARGET_ATTR
  "left" / "seed_offset": the glove material's int attributes), instance_params; roll from g_nRandomSeed (or
  g_nRandomSeedAlt where seed_offset is 1); INIT target_instance, the paint's F_CLOTH_SHADING / F_ANISOTROPIC_GLOSS
  copied, then GENERATE_TEXTURE g_tColor (F_OUTPUT_MODE 0), g_tMetalness (2), g_tNormal (1), g_tAmbientOcclusion (3),
  g_tAnisoGloss (4, with F_ANISOTROPIC_GLOSS), each with g_fWearProgress = wear and g_bFlipFixup on the left hand
  (unless the paint flips already); g_flSheenScale copied when the paint has it.
- csgo_customglove: features F_BACKWARDS_COMPATIBILITY (classic kits 0, volatile_02 1), F_ANISOTROPIC_GLOSS,
  F_CLOTH_SHADING, F_PATTERN, F_PATTERN_PAINT, F_PUFFY_PAINT, F_TINT_ID, F_OUTPUT_MODE; 6 pixel programs, static combo
  `S_BACKWARDS_COMPATIBILITY + 2 * S_ANISOTROPIC_GLOSS + 4 * S_TINT_ID` (ids 0 1 2 3 5 7); 2 vertex programs
  (S_BACKWARDS_COMPATIBILITY, UV attribute vTextureCoords).
- g_nOutputMode = F_OUTPUT_MODE: 0 colour, 1 normal hemi-octahedral in RG with roughness in B, 2 (0, metalness, cloth),
  3 occlusion, 4 anisotropic gloss; each SrgbGammaToLinear'd into the sRGB target.
- Colour-adjust matrices: VfxEval's MatrixMultiply / MatrixColorTint2 / MatrixColorCorrect2 over TextureAverageColor (a
  file's Reflectivity). sRGB reads: the variable table's Sampler2D flags.
- 22 to 38 (texture, sampler) pairs a program, 18 to 22 distinct files a kit; 24 kits use g_tAnisoGloss.

## Stickers

A sticker is no texture of its own: a second composite request copies each sticker kit's material keys into the
weapon's csgo_weapon material; csgo_weapon's F_STICKERS pass draws up to five over the surface in its second UV set.

### Request

1. 1807ff680: the paint's request (1807fa510 path), then 180788e00 + 1807849c0 and a second request on the same entity
   (entity+0x610 vfn +8) when the item has a sticker.
2. 180788e00: slots 0..5 -> entries: attribute 0 the kit (181137800, kit+0x20 sticker_material), 1 the wear; an entry
   per slot index (padded with empty ones); slot 5 takes the first empty entry once there are more than four, else is
   appended; attribute 6 the schema (-1: the slot's own index; slot 5 and 182215c90 >= 0: that global); then 18078d460;
   then (param_4: not a preview) `rotation += attr 3 * 0.0027777778`, `offset x += attr 4`, `offset y += attr 5`.
   Attribute 2 (scale) is not read here.
3. 18078d460: `StickerMarkup` (hash 9d901f54): the entry whose `Index` is the schema and whose `LegacyModel` equals
   18078db50 -> Offset (2 floats) +8, Rotation +0x14, Scale +0x10, UICameraRotation +0x1c, Deprecated +0x24.
4. 1807849c0: per non-empty entry k, loose variables g_bEnableSticker%d (BOOLEAN 1), g_flSticker%dWear (FLOAT1),
   g_vSticker%dOffset (FLOAT2: x +8, y +0xc), g_flSticker%dRotation (FLOAT1), g_vSticker%dScale (FLOAT1, though the
   shader's is a Float2) into container "econ_instance_vars"; material container "sticker%d" =
   Format("stickers/%s.vmat", sticker_material); program weapons/stickers/dev/_shared_sticker_generic.vcompmat; name "stickers".

### The program (_shared_sticker_generic.vcompmat)

- Match filters MATERIAL_SHADER "csgo_weapon.vfx" and ATTRIBUTE_EXISTS "composite_inputs".
- Containers target_instance, econ_instance_vars (g_bEnableSticker0..4 false, g_flSticker0..4Wear 0), sticker0..4
  (stickers/dev/sticker_default.vmat).
- Mutators: INIT target_instance, COPY_MATCHING_KEYS econ_instance_vars, then per slot k COPY_KEYS_WITH_SUFFIX sticker<k>
  "Sticker0" -> "Sticker<k>" when econ_instance_vars.g_bEnableSticker<k> == 1.
- A sticker material (csgo_weapon_sticker.vfx) holds its look as *Sticker0 keys: g_tSticker0, g_tNormalRoughnessSticker0,
  g_tSfxMaskSticker0, g_tHoloSpectrumSticker0, g_tGlitterNormalSticker0, g_bHolographic / Glitter / Metallic /
  PaperBacking / SelfIllum / AutomaticPBRColorFitting / LegacyTintMultiply / PreserveRoughnessSticker0, colour tint,
  saturation, boosts, wear bias and scratches.

### The pass (csgo_weapon pixel static combo 512)

- Combo bits (the combos file's order): S_ENABLE_ADJUSTMENTS 1, S_MODE_TOOLS_VIS 2, S_ALPHA_TEST 4, S_TRANSLUCENT 8,
  S_ADDITIVE_BLEND 16, S_TINT_MASK 32, S_GLITTER 64, S_ENABLE_SFX_MASK 128, S_SELF_ILLUM 256, S_STICKERS 512, ...
- The vertex shader passes vTexCoord2 (the model's second UV) as input_4.zw.
- Before the slots: g_tStickerWepInputs at the uv (x: where a sticker may be, y: a wear bias); the slots run only where
  x > 0 and vTexCoord2.x > -1.
- Each slot (five identical blocks; slot 0 has the start values folded in) reads the previous slot's state and writes
  it: albedo, tangent-space normal, roughness (2), metalness, occlusion, g_tMetalness.z, F0, self-illumination, glitter,
  a mask (x coverage, w coverage x (1 - wear)), the alpha.
- A slot: skipped when its scale's x or y is 0 or the mask is 0;
  `uv = rotate(((vTexCoord2 - 0.5) - offset) * |scale.x|, rotation * 2pi) + 0.5`, nothing outside [0, 1];
  alpha x 12.75; an edge darkening sampled 0.01 along the camera's (right, up) projection of the normal when the
  sticker's LOD (textureQueryLod) < 4; its normal (g_tNormalRoughnessSticker hemi-oct, y flipped) added x 2 x alpha to
  the weapon's normal read at LOD max(sticker LOD, 3); occlusion `min(pow(AO at that LOD, 0.75), 0.5 alpha + 0.5)`;
  glitter (g_tGlitterNormal point and trilinear, sparkle by `reflect(view, normal) * 12`); PBR colour fitting
  (g_vAlbedoLevels / g_vMetallicAlbedoLevels / g_vDarkMetallicAlbedoLevels: expressions in the variable table); holo
  (g_tSfxMask's x the amount, the spectrum at (mask.y + N.V + V.sun, mask.z), g_vHoloAlbedoLevels); wear
  (g_tStickerScratches, the wear bias, the paper backing's grey); the editor's peel / highlight / apply-slot paths
  (g_nActiveStickerApplySlot, g_flHighlightTime: off in game).
- After the slots: albedo -> `diffuse * (1 - metal)^g_flMetalnessTransitionBias` and F0 mix; self-illumination added to
  the lit colour, glitter to the specular.
- PerViewConstantBuffer_t._m0 / _m7 / _m8 / _m9 are, by use, the view constants (_m8 / _m9 up / direction by the
  geometry: cross(dir, up) = right; _m0 a constant: the editor's timers only); PerViewLightingConstantBufferGpu_t._m16
  the holo's second direction (taken as the scene's first directional light, toward it).

### Sticker items

- Capsules: prefab sticker_capsule; loot lists tiered as a case's, entries "[sticker kit]sticker"; a sticker is def 1209
  with its kit id, rarity the kit's item_rarity, image econ/stickers/<sticker_material>. No StatTrak, no float.
- Applying: popup_capability_can_sticker, work_type can_sticker (the GC applies); a weapon's slots are its model's
  StickerMarkup indices 0..4. Scraping: work_type remove_sticker. Drag placement: popup_can_apply_pick_slot.vts.

## Unread

- GiveNamedItem's econ lookup (server: which spawns / buys get the loadout item; that the loadout's knife replaces the
  given weapon_knife / weapon_knife_t).
- The composite's mip chain and BC7 copy (composite_material_use_bc7).
- A shader variable defined twice in one table (the uv transforms): which one the constant buffer gets.
- 18077b9f0 / 18077d840 (include / container merge); 180797dc0; 180801390 / 1808002d0; 180792630 / 180787390.
- Name tags; the KillEaterRank names.
- csgo_character's g_tMetalness read (taken as output 2's G); materialsystem2's own colour matrices; the left / right
  pattern flip; the volatile_02 kits.
- A FLOAT1 loose variable on a Float2 material variable (g_vSticker%dScale): taken as (x, x). Evidence: 59 of 168
  markup entries' Scale differs from the vmat's g_vSticker%dScale, and the 5th slots (AUG, CZ75, Deagle ...) have vmat
  scale 0, so CS2 draws them only if the float replaces it with a y that is not 0.
- The sticker request's target (the weapon's material instance after the paint request?); how the request's
  containers merge into the program's; COPY_KEYS_WITH_SUFFIX: every key with the suffix or only declared ones.
- PerViewConstantBufferCsgo_t._m2.x's value (glitter scale 2.5 / 1.75); the sampler states (g_sAniso, g_sPoint,
  g_sAnisoClampV, g_sTrilinearWrap, g_sUserConfig) from the vcs; textureQueryLod's LOD (isotropic?).
- The sticker_gaps material (F_TRANSLUCENT, no composite_inputs: the program does not match it): how CS2 draws it.
- 18078db50 (legacy body); 182215c90; the GC's scrape step and placement limits; souvenir capsules and patches.
