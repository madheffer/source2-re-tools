# Arms Race's HUD (client)

client_20261015.dll (ReVa, tools/re/game/schema.py, tools/re/game/dispuses.py), panorama from pak01 (hudweaponselection.vxml /
.vcss, hudteamcounter.vxml / .vcss, hudteamcounter-equipmentinfo.vcss: the raw text read out of the .vcss_c, the baked
.css under web/public/panorama is a prettified copy that drops some blocks). Read 2026-11-16. Ported in
web/src/cs2web/client/modes/team/armsrace-hud.js (+ .css) and client/hud/teamcounter-gg.js (+ .css); the server's
side is docs/game/armsrace.md.

## Game-type helpers (the game type interface 0x1824c47b8: vfn 0x98 game_type, 0xa0 game_mode)

| Address | True when |
|---|---|
| 180769d30 | game_type 1 (gun game: Arms Race, Deathmatch) |
| 180769d50 | game_type 1, game_mode 2 (Deathmatch) |
| 180769d90 | game_type 1, game_mode 0 (Arms Race) |
| 180769e60 | game_type 1, game_mode 2 and mp_dm_teammode (cvar 0x1824bc6e8, registered 180086a10) != 0 |
| 180758bc0 | the game mode rules object (CCSGameModeRules_ArmsRace's client side): +0x30 count, +0x38 the names of m_WeaponSequence |

Controller fields (schema): m_iScore +0x954, m_bIsLocalPlayerController +0x790, m_iConnected +0x6f4, m_bPawnIsAlive
+0x934. Pawn: m_fImmuneToGunGameDamageTime +0x3504, m_bGunGameImmunity +0x3508, m_fImmuneToGunGameDamageTimeLast
+0x350c, m_GunGameImmunityColor +0x1e10 (Color: r, g, b, a bytes).

## The weapon list's ladder (CSGOHudWeaponSelection)

- Class tokens (180eb8970, table 0x1822452b8, see weapon-selection.md): +0x14 weapon-selection--armsrace, +0x16
  weapon-selection--armsrace-list, +0x18 armsrace-item--status (the item's SwitchClass group), +0x1a --future, +0x1c
  --current, +0x1e --done, +0x20 armsrace-pip, +0x22 armsrace-pip--status (the pip's group), +0x24 --unearned, +0x26
  --current (unused by the ladder), +0x28 --earned, +0x38 hud-colorize-wash--hsv. vfn 0x500 = SetHasClass, 0x508 =
  SwitchClass(group, class), 0x108 = SetVisible.
- 180ea2f90 (constructor): loads hudweaponselection.xml, finds #weapon-selection-list (+0x20) and
  #weapon-selection--armsrace-list (+0x30).
- **180ec6bc0** (build): the rules exist and the local controller's team (+999) > 1 and 180905820 on the local
  controller's +0x820 (1808a08b0): m_pInventoryServices; 180905820 tests that object's +0x30 (its controller) +0x790
  m_bIsLocalPlayerController and +0x88 > 0, the count of CCSPlayerController_InventoryServices'
  m_vecServerAuthoritativeWeaponSlots (schema: m_unMusicID +0x58, m_rank +0x5c, m_nPersonaDataPublicLevel +0x74 ..
  m_nPersonaDataXpTrailLevel +0x84, m_vecServerAuthoritativeWeaponSlots +0x88): the server's loadout slots have arrived
  (always so here once joined): weapon-selection--armsrace on, the list emptied
  (180ec1180, vfn 0x1a8), +0x90 = -1, an item per ladder name (180ea6120(panel, name, index)), +0xec = the count.
  Called from 180ecbfe0 when the rules' count != +0xec, and from 180eae1d0 (a reset slot: 180eac240 then the build).
- **180ea6120** (an item): the WeaponIcon--ArmsRace snippet; armsrace-item--knife when the name is weapon_knifegg;
  the dialog variable armsrace-level = the index (its label is visibility: collapse); the knife item's image is the
  local player's team melee item (180904f80(controller, team, 0) +0x720: the loadout's knife) instead of the name;
  both images (#armsrace-weapon-outline / -filled) `file://{images}/icons/equipment/%s.svg` of the name after its
  first '_' (strchr 0x5f); 2 pips (1 on the knife), each a Panel with armsrace-pip, kept at item +0x10.
- **180eafc30** (the think, every 0.25 s: curtime +0x30 vs +0x44, +0.25): the watched pawn (the observer target or
  yours); in Arms Race (180769d90) its controller (pawn +0x1560 handle) m_iScore (+0x954) against the last one seen
  (the think's object -8): changed -> **180ec3a80(list, score / 2, score % 2)**; then 180ecbfe0, 180ed1cb0. In Arms Race the list's
  weapon-selection--fade never comes on (the 105-118 lines' 180769d90 tests). The events weaponhud_selection,
  round_start, spec_target_updated and ggprogressive_player_levelup only force the next think (180eb3450: +0x44 = -1).
- **180ec3a80** (the states), for item i with d = i - level: d < 0: --done, every pip --earned; d > 0: d < 4 ->
  `armsrace-item--next%d` (next1..3), else --future, every pip --unearned; d == 0: --current, pip k --earned when
  k < score % 2, else --unearned.
- **180ecbfe0**: armsrace-item--selected on the list (+0x30) while the watched pawn's active weapon's vdata +0x700
  (gear slot) is below 2; on the current item's filled image hud-colorize-wash--hsv on unless
  cl_weapon_selection_rarity_color (0x1825d72a8, default 0, registered 18010c0b0) is on and a gun is held; with it on,
  weapon-selection-item--rarity-%d of the held weapon's econ item.
- vcss (all ported, values in armsrace-hud.css): #weapon-selection--armsrace-list 100% tall, margin-bottom 93, flow up,
  collapsed unless weapon-selection--armsrace; .armsrace-item right, opacity 0, height 120, margin-top -10, padding-top
  5, margin-right 16, transition opacity / height / margin-top .2s; --next3 .25, --next2 .5, --next1 .75, --current 1
  and margin-top 0, --current.--knife 0, --done 0 / height 0 / margin-top 0; the images origin (100%, 50%),
  pre-transform-scale2d -1 1, padding 7, scale .7, bottom, transition .2s; the outline wash black, hidden on
  --future / --current / --done; the filled hidden except --current, --selected scale .9 brightness 1.5;
  #armsrace-pips top, x -30, right, flow up, opacity .5 (1 on --current), margin-top -4, margin-right 5; .armsrace-pip
  10 x 10, margin-bottom 20, #000000c0, round, --earned white additive (#armsrace-pips carries hud-colorize-wash--hsv too: the earned pips draw the washed team colour, the others stay black; #armsrace-weapon-filled is .additive); `.weapon-selection--armsrace .gear-slot--0 / --1
  .weapon-selection-item-icon-main { opacity: 0 }` (the classic list's gun and pistol icons).
  WEAPONSELECTION_UNSELECTED_HSV_TRANSFORM 0, 0.96, 0.9 on the team colour (csgo-hud__color-0).

## The top bar in game_type 1 (CCSGO_HudTeamCounter)

- Panels (constructor 180ea0ca0, offsets of the object 180ec6730 gets): +0x68 ScoreAndTimeAndBomb, +0x70 its BG, +0x78
  GameTime, +0x80 TimerText, +0x88 BombStatus, +0x90..0xa0 the bomb images, +0xa8 GameScore, +0xc0 PlayerCount, +0xc8
  TeamAll, +0xd0 TeamLargeCT, +0xd8 TeamLargeT.
- **180ead860 -> 180ec6730(layout)**: layout 1 when 180769d30 and not 180769e60; +0x127c = layout; GameModeGunGame
  on the panel for layout 1; then layout 1: 20 avatars into TeamAll (180eb8050 x 0x14), TeamAll shown, GameTime shown,
  BombStatus / GameScore / PlayerCount / the team rows hidden; else 10 + 10 into the team rows.
- **180ecec30** (the avatars): every controller with m_iConnected 0 / 3 (or 1808865b0) on team 2 / 3; in layout 1 all
  of them into one array (+0x1990, at most 0x20), sorted by **180eabc80** (entry +0x20 m_iScore down, then entry +0
  the player slot up), the first 20 drawn; in Arms Race the avatar's weapon = the ladder's entry at
  min(score / 2, count - 1) (its item def by name, 0x148 of the econ schema), else the best weapon (slot 0, 1, 2).
  The scale (180ecf883..180ecfc49, when the T count (+0x1284) or the CT count (+0x1288) changed): 1802803b0 is
  RemapValClamped(v, a, b, c, d) = c + (d - c) x clamp((v - a) / (b - a), 0, 1) (d at [rsp+0x28]); layout 1:
  s = Remap(T + CT, 10.0 (181ad0f70), 20.0 (181ada2ec), 1.0 (181ac6074), 0.7 (181b06550)) on #TeamAll (+0xc8),
  else Remap(max(T, CT), 5.0 (181acaf24), 10.0, 1.0, 0.7) on #TeamLargeCT / T (+0xd0 / +0xd8); applied as
  180dc75e0(s, s, 1.0): scale3d through the panel's style (vfn 0x238 -> 0x88), from #TeamAll's transform-origin
  50% 0%. (The 0.5 / +0x20b8 value at 180ecf5fe is the avatars' re-sort timer, not the scale.)
- **180eba820** (an avatar's data): in Arms Race the health passed is 0 (so #HealthBarContainer hides: 180ecc1f0 line
  391 shows it only for health > 0) and the second value too; the number = m_iScore / 2 in Arms Race, m_iScore in
  Deathmatch (180769d50 and not 180769e60), else 0; the weapon icon `file://{images}/icons/equipment/%s.svg` of the
  item's name less "weapon_" (18076a470).
- **180ecc1f0**: kill flags (killattribute HTC__Avatar__*) only when the layout isn't 1; #ArsenalProgress (+0x26 of
  the avatar) shown when the number != 0 or Arms Race: its label the number (V_Int32ToString), class
  `gglevel-%d` = count - number - 1 (the rules' count; 0 = the knife level, -1 = won); AvatarL__GGText--Player when
  the entry's local flag (controller +0x790 m_bIsLocalPlayerController) is set, else AvatarL__GGText--Bot; the weapon
  panel shown with the icon when there is one.
- vcss: .GameModeGunGame #TeamCounter flow down, .team__large_container--left / --right collapsed; #ArsenalProgress
  centred, 100% wide, padding 0 2, z -1, flow down, ignore-parent-flow, y 54; .gglevel-0 / --1 wash gold +
  gg-last-level (brightness 1 -> 1.5, .5 s, infinite, alternate), its Image gg-last-level--image (img-shadow 0 0 4px 1
  gold at 100%); .AvatarL__GGTextBG 100% x 32, #0000006f, bluedots .03; .AvatarL__GGText bold 22, centred, bottom;
  --Player #fff, --Bot #ffffff50; .AvatarL__GGIconBG 54 wide, margin-top 4, padding 2; .AvatarL__GGIcon centred,
  img-shadow 1px 1px 1px #00000090; .endofmatch hides it. hudteamcounter-equipmentinfo.vcss: .deathmatch /
  .gungameprogressive .equipinfo--score-time__bg mask masks/score-time-dm-mask.vsvg.

## Spawn immunity's look

- **180c67c40** (the amount): 0 unless the pawn is alive (vfn 0x4e8 = 0x180165050) and m_bGunGameImmunity (+0x3508)
  and (mp_respawn_immunitytime (0x1824bc5b8, named by its registration) > 0 or the warmup, 18076a1e0 on the gamerules
  0x1825651d0); then clamp(m_fImmuneToGunGameDamageTime (+0x3504) - now, 0, 1) (18015c5e0: a - b on two GameTime_t;
  18015a220: clamp(x, 0, 1)). now = 18075d250(entity identity +0x38): gpGlobals->curtime (0x182230090 +0x30), through
  the gamerules' vfn 0x220 (180ba9260) when they exist. 1 while more than a second is left, down to 0 over the last.
- **180c9d440** (the pawn's per-frame scene-object attributes, `if (pawn+0x338 == 0) return`): the entity list is
  18021a2c0(pawn) (the pawn, then 18021a140: its scene node's (+0x330) children, +0x40 first child / +0x48 next
  sibling, recursively: the held weapons and every other attached model) plus 180c7ede0(pawn), which adds the active
  weapon (1808cc9c0: m_pWeaponServices +0x12f0 -> 180a7f360), that weapon's handle +0x1990 and m_hHudModelArms
  (+0x1da4) only when vfn 0xac8 is true: 0x180ca1b40 (`xor al, al`) for C_CSPlayerPawn (vtable 0x181c8a138),
  C_CSPlayerPawnBase and C_CSObserverPawn, 0x180cbf200 (`mov al, 1`) only for C_CSGO_PreviewPlayer. **In game the
  first-person arms and viewmodel never get it**; the menu's preview agents do. For every scene object of each
  entity (+0x338, count +0x38), unless the entity's model keyvalues (identity +0x48) have `spawn_invuln_effect_override`
  (18021bca0, hash 0x8ad232bc): attribute 0x244ec9b0 (g_flSpawnInvulnerability) = the amount (x4) and 0xb2caf4df
  (g_cInvulnerabilityColor) = m_GunGameImmunityColor (+0x1e10) r, g, b / 255.0 (180c9e5f3 .. 180c9e665): the bytes
  as they are, no gamma: a linear colour in the shader's linear HDR. The override key: no CS2 model carries it
  (Source2Viewer-CLI `-b DATA` over pak01's weapons/models/ and characters/models/: 224 m_keyValueText blocks, the
  agents' empty, none with `spawn_invuln`), so every pawn and held weapon takes the look; a custom model with the key
  would need its keyvalues baked (none of ours has any).
- **The other two writers**: 180828340 (C_CSWeaponBase's per-frame scene callback, registered by 1807ff090, slot 13 of
  every weapon vtable): returns at once while the weapon has an owner (180941fa0: m_hOwnerEntity +0x520); an unowned
  (dropped) weapon's objects get 0 and colour (1, 1, 1): a dropped gun never shows it. 180e6cf50 (an item preview
  panel's weapon on a hand, `weapon_hand_r`): the UI's own blink, not the game's.
- **m_GunGameImmunityColor** (server 2026-11-05, pawn +0x155c): the constructor (1801f7ca0, 1801f819b) stores
  0x181791cb4 = ff ff ff ff (white); the only other writer in the DLL (a [reg+0x155c] scan) is Arms Race's slot 8
  (18094d9c0): on a team join T -0x8a3716 = bytes ea c8 75 ff = rgb(234, 200, 117), CT -0x54483 = 7d bb fa ff =
  rgb(125, 187, 250), -1 with mp_teammates_are_enemies (the bool at 18211a6d8). So deathmatch, the base rules and every
  warmup draw it white; Arms Race by team. Sent by snapshots.js immunitySnap with each immune pawn.
- **The shader** (csgo_character's and csgo_weapon's pixel shaders, `lasers-bake --shader-src csgo_character` /
  `csgo_weapon`: both end with the same lines), on the lit colour after the fog (_12895 / _19366: the fog's two terms,
  then the distance contrast and the last decal's burn, then this):
  ```
  if (g_flSpawnInvulnerability > 0) {
    fres  = 1 - saturate(dot(_19257, _17120))   // _19257 = normalize(worldPos - eye) negated: V toward the eye;
                                                // _17120 = the shading normal (normal-mapped, the face's sign: input_3
                                                // flipped for a back face), frost-bent when g_vFrostState is on
    noise = texelFetch(BlueNoise, ivec2(gl_FragCoord.xy) & mask, 0).y
    f     = mix(fres * noise, 1.0, fres)
    e     = mix(3.0, 6.0, 1.0 + sin(g_flGameTime * 20) * 0.5)
    lum   = dot(c, (0.2125, 0.7154, 0.0721))
    c     = mix(c, g_cInvulnerabilityColor * (mix(lum, 0.5, 0.5) + 4 * pow(f, e)), g_flSpawnInvulnerability)
  }
  ```
- **BlueNoise** (PerViewConstantBufferCsgo_t._m4 / ._m15): the client's per-view CB fill **1811fef80** (r12 = the CB):
  r12+0x40 = the bindless index (vfn 0x650 of the render device) of the texture global **0x1825f5ef0** (1811ffac1 ->
  1811ffb06), r12+0xb0 / +0xb4 = that texture's width - 1 / height - 1 (vfn 0x2d0, 1811ffe7f .. 1811ffea9). 0x1825f5ef0
  is filled from the table at 1811cba30: name `textures/dev/blue_noise_256.vtex` (1811cbac0) -> handle 1825f5ef0 (as
  brdf_lut.vtex -> 1825f5ee8 = r12+0x44, water_droplets .. rain_ripples -> 1825f5f00 .. 1825f5f20 = r12+0x70 .. +0x80).
  So _m4 is c4 (0x40) and _m15 is c11 (0xb0, the smoke trace's mask): core's blue_noise_256 (256 x 256 RGBA8888, the
  one tools/bake-legs.mjs bakes to player/fp-legs/blue_noise_256.rgba), its green, mask (255, 255), rows from the top.
- **g_flGameTime** (PerViewConstantBuffer_t._m1): scenesystem's view-constants dump (1800c8490) prints
  m_viewConstantBufferData.g_flRealTime from +0x9e8 and g_flGameTime from +0x9ec: _m0 / _m1 of the block, the game time
  (the curtime the decal burn's g_flLastDecalTime is compared with in the same shader).
- **The port**: world/body-tint.js (the GLSL above, at three's tonemapping slot: the HDR target's linear colour after
  everything lit; bodies and held guns get no fog here, so nothing lies between), V = normalize(vViewPosition), N =
  three's `normal` (view space, normal-mapped, flipped for back faces); the noise row flipped (targetH - 1 - y);
  g_flGameTime = the client's curtime (game.js flashClock: the replica's tick + fraction). The amount per pawn: the
  server sends `gg` = "id:endTick[:rrggbb]" (snapshots.js; endTick in the round world's ticks, only while
  mp_respawn_immunitytime > 0 or the warmup), the client clamps endTick/64 - curtime (game.js immunityAmount). Shared
  bodies draw the model's immunity copies at 1 (one per colour) and, below 1, a pooled set of copies of their own (one
  uniform object, given back when the fade ends: body.js takeFade / giveFade; the same programs). Your own body (the
  legs) patches its own materials once at load (amount 0 until immune). The held world guns (instance-batch.js) carry
  the amount and colour per instance (attribute cs2Inv, uploaded only while someone has it), read by the gun's
  material in its instanced variant (patchInvulnInstanced). No material onBeforeRender: world/rawgl/hybrid.js keeps
  every patched material on its fast path.

## The money panel (CSGOMoneyPanel, client 2026-10-15)

- Made by 0x180eab9a0 (hudmoney.xml, its vtable 0x181cdb780) with the visibility callback **0x180eb0c70**: visible
  when the gamerules exist, **0x180759930** is true, and (no local pawn, or the pawn is an observer (vfn 0x4f0) whose
  mode isn't 2 / 3, ...) 0x180cb2100 is 0, the cvar at 0x182561558 is on and the one at 0x1825790a0 off (taken as
  cl_drawhud / cl_draw_only_deathnotices: not named).
- **0x180759930**: mp_maxmoney (0x1824bc418, registered at 0x180087d50) >= 1 and (mp_playercashawards (0x1824bc438,
  0x1800883a0) or mp_teamcashawards (0x1824bc448, 0x18008a560)). Arms Race's cfg (mp_maxmoney 0) hides the panel.
  Ported: client/core/game.js moneyShown, ui/hud.js.

## The win panel

docs/game/winpanel.md (every mode's round end; Arms Race's MVP is the winner, reason 5
"#Panorama_winpanel_mvp_award_gungame": "MVP"). Ported: client/hud/winpanel.js.

## Panorama's colours (panorama.dll, the install of 2026-11-12, imported into ReVa as /panorama_installed_1112.dll)

- **18014b780** (the colour parser): `#rgb[a]` / `#rrggbb[aa]`, rgb()/rgba(), names, and `hsv-transform(<colour>,
  dh, s, v)`: the inner colour parsed recursively, the three floats by 18014ca80; rejected when |dh| > 360, s < 0 or
  v < 0; each channel / 255 through **1803a2430** (sRGB -> linear: x <= 0.04045 ? x / 12.92 : V_powf((x + 0.055) /
  1.055, 2.4), x clamped to 0..1), **1803a27e0** (RGB -> HSV: max, min, s = (max - min) / max, h = 60 x ((g - b) / d,
  (b - r) / d + 2, (r - g) / d + 4), +360 when negative), h = V_fmodf(h + dh, 360) (+360 when negative), s *= s,
  v *= v (each clamped to 1), **1803a2680** (HSV -> RGB: i = (int)(h / 60), f, p, q, t, the six cases; h == 360 ->
  0), **1803a2500** (linear -> sRGB: x <= 0.0031308 ? 12.92 x : 1.055 V_powf(x, 0x3ed55555 = 1/2.4) - 0.055), x 255
  truncated to a byte (cvttss2si); the alpha kept. Next in the parser: `opacity-transform(...)`. Ported:
  src/lib/panorama-color.js hsvTransform (float32). WEAPONSELECTION_UNSELECTED_HSV_TRANSFORM on ct-color
  rgb(150, 200, 250) -> rgb(148, 193, 238), on t-color #eabe54 -> rgb(223, 183, 91).
- **wash-color** (CStylePropertyWashColor vtable 0x1804e12a8; registered 18005ae10, symbol 1805e2dfe; the setter
  180197ad0, the getter **180197a10** = CPanelStyle vtable 0x1804e4bf0 slot 0x180, returning **0xffffffff** when
  unset): a white default is a multiply's identity, and both UI shaders draw texel x vertex colour (panorama.vfx
  D_TEXTURETYPE: `Texture0.Sample * input_1`; panorama_fancyquad: the layer's texel x input_3), so the wash multiplies
  the panel's colours (the alpha kept). Its help text: "blended over the panel and all its children at composition
  time, tinting them; the alpha value determines the intensity". A wash makes the panel a composition layer
  (1800f1970: +0x224 |= 0x10). The function that folds the wash into the layer's vertex colour isn't located (the 8
  callers of slot 0x180 are other interfaces); every wash this HUD uses is opaque, where the multiply is exact.
- **brightness** / saturation / hue: panorama_fancyquad's D_COLORCORRECTION (`lasers-bake --shader-src
  panorama_fancyquad --cs2 <game/core>`): the layer's texel (sRGB-read: linear) to HSV, h + m0 (frac), s x m1,
  v x m2, then the contrast lerp toward 0.5 (m3), back to RGB, then x the vertex colour. So brightness b is linear(c)
  x b for a flat colour; the target clamps. Ported as precomputed colours (brightened()).
- **-s2-mix-blend-mode** (CStylePropertyMixBlendMode vtable 0x1804de650; the names at 180189830: normal, multiply,
  screen, additive, opaque): `additive` adds the source to what is under it: CSS plus-lighter. panorama.vfx's
  D_DSTCOLOR_BLENDMODE variants convert the vertex colour to gamma, blend with the destination copy (Texture4) and
  convert back to linear: the UI's render target is sRGB (blending in linear light); the page's compositor blends the
  encoded values. That difference is the page's, every panel's, not this HUD's.
- **svgstroke** and the other Image svg attributes (client.dll, the panorama client library: registered 1817ea560,
  handled by 1817eae70 -> 181884ca0 -> 181884cd0 with an index: 0 fill, 1 fillopacity, 2 stroke, 3 strokewidth,
  4 linecap (butt / round / square), 5 linejoin (miter / round / bevel), 6 strokeopacity, 7 svgopacity, 8 fillrule;
  each sets a value and its bit in a "set" mask, opacities clamped 0..1): the rasteriser's style overrides. The
  equipment icons' paths set only fill, so the overrides on the root are what every path draws with. Ported:
  armsrace-hud.js makes the outline's svg with stroke="#ffffff" stroke-width="1" stroke-opacity="1"
  fill-opacity="1" on its root (a blob URL, once per icon).

## Spectating

180ecbfe0 tests the watched pawn's active weapon (the observer target's when you spectate): the client takes the
spectated player's held weapon from the replica's sample (gearSlot 1 / 2) for armsrace-item--selected; the ladder's
score was already the watched player's (me.sc).
