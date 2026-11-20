# Arms Race HUD (client)

client_20261015, server_20261105, panorama.dll (install of 2026-11-12). pak01 hudweaponselection.vxml / .vcss, hudteamcounter.vxml / .vcss, hudteamcounter-equipmentinfo.vcss (raw text from the .vcss_c), hudmoney.xml; csgo_character / csgo_weapon / panorama.vfx / panorama_fancyquad shader sources. The server's side: [armsrace.md](armsrace.md).

## Functions

| Address | Module | What |
|---|---|---|
| 0x1824c47b8 | client | game type interface (vfn 0x98 game_type, 0xa0 game_mode) |
| 180769d30 | client | game_type 1 (gun game: Arms Race, Deathmatch) |
| 180769d50 | client | game_type 1, game_mode 2 (Deathmatch) |
| 180769d90 | client | game_type 1, game_mode 0 (Arms Race) |
| 180769e60 | client | game_type 1, game_mode 2 and mp_dm_teammode != 0 |
| 180758bc0 | client | game mode rules object (CCSGameModeRules_ArmsRace's client side) |
| 180eb8970 | client | class tokens (table 0x1822452b8, weapon-selection.md) |
| 180ea2f90 | client | CSGOHudWeaponSelection constructor (hudweaponselection.xml) |
| 180ec6bc0 | client | build the ladder |
| 1808a08b0 | client | controller +0x820 m_pInventoryServices |
| 180905820 | client | inventory services ready |
| 180ec1180 | client | empty the list (vfn 0x1a8) |
| 180ea6120 | client | an item (panel, name, index) |
| 180904f80 | client | (controller, team, 0) +0x720: loadout knife |
| 180ecbfe0 | client | selected / wash update; rebuilds when the count changes |
| 180eae1d0 | client | reset slot: 180eac240 then the build |
| 180eafc30 | client | the think (every 0.25 s) |
| 180ec3a80 | client | item states (list, level, score % 2) |
| 180ed1cb0 | client | think tail |
| 180eb3450 | client | force the next think (+0x44 = -1) |
| 180ea0ca0 | client | CCSGO_HudTeamCounter constructor |
| 180ead860 -> 180ec6730 | client | layout (1 = gun game) |
| 180eb8050 | client | an avatar (x 0x14 into TeamAll) |
| 180ecec30 | client | the avatars |
| 1808865b0 | client | connected test |
| 180eabc80 | client | avatar sort |
| 1802803b0 | client | RemapValClamped(v, a, b, c, d) = `c + (d - c) x clamp((v - a) / (b - a), 0, 1)` (d at [rsp+0x28]) |
| 180dc75e0 | client | (s, s, 1.0): scale3d through the panel's style (vfn 0x238 -> 0x88) |
| 180eba820 | client | an avatar's data |
| 18076a470 | client | name less "weapon_" |
| 180ecc1f0 | client | avatar draw (kill flags, #ArsenalProgress) |
| 180c67c40 | client | spawn immunity amount |
| 0x180165050 | client | pawn vfn 0x4e8 (alive) |
| 18076a1e0 | client | warmup (on gamerules 0x1825651d0) |
| 18015c5e0 | client | a - b on two GameTime_t |
| 18015a220 | client | clamp(x, 0, 1) |
| 18075d250 | client | now (entity identity +0x38): gpGlobals->curtime (0x182230090 +0x30), via gamerules vfn 0x220 (180ba9260) |
| 180c9d440 | client | pawn's per-frame scene-object attributes |
| 18021a2c0 | client | entity list: the pawn, then 18021a140 (scene node children) |
| 18021a140 | client | scene node children (+0x40 first child / +0x48 next sibling, recursive) |
| 180c7ede0 | client | adds the active weapon (1808cc9c0 -> 180a7f360), its +0x1990 and m_hHudModelArms when vfn 0xac8 |
| 0x180ca1b40 | client | vfn 0xac8 `xor al, al` (C_CSPlayerPawn (vtable 0x181c8a138), C_CSPlayerPawnBase, C_CSObserverPawn) |
| 0x180cbf200 | client | vfn 0xac8 `mov al, 1` (C_CSGO_PreviewPlayer only) |
| 18021bca0 | client | model keyvalue lookup (`spawn_invuln_effect_override`, hash 0x8ad232bc) |
| 180c9e5f3 .. 180c9e665 | client | colour bytes / 255.0 |
| 180828340 | client | C_CSWeaponBase per-frame scene callback (registered 1807ff090, slot 13 of every weapon vtable) |
| 180941fa0 | client | m_hOwnerEntity (+0x520) |
| 180e6cf50 | client | item preview panel's weapon on `weapon_hand_r` (the UI's own blink) |
| 1811fef80 | client | per-view CB fill (r12 = the CB) |
| 1811ffac1 -> 1811ffb06, 1811ffe7f .. 1811ffea9 | client | BlueNoise bindless index / size writes |
| 1811cba30 | client | texture table (name -> handle) |
| 1800c8490 | scenesystem | view-constants dump |
| 0x180eab9a0 | client | CSGOMoneyPanel made (hudmoney.xml, vtable 0x181cdb780) |
| 0x180eb0c70 | client | money panel visibility |
| 0x180759930 | client | money shown |
| 0x180cb2100 | client | visibility test |
| 1801f7ca0, 1801f819b | server | pawn constructor: m_GunGameImmunityColor white |
| 18094d9c0 | server | Arms Race slot 8: team colour on a team join |
| 18014b780 | panorama | colour parser |
| 18014ca80 | panorama | float parse |
| 1803a2430 | panorama | sRGB -> linear |
| 1803a27e0 | panorama | RGB -> HSV |
| 1803a2680 | panorama | HSV -> RGB |
| 1803a2500 | panorama | linear -> sRGB |
| 18005ae10 | panorama | wash-color registration (symbol 1805e2dfe) |
| 180197ad0 / 180197a10 | panorama | wash-color setter / getter (CPanelStyle vtable 0x1804e4bf0 slot 0x180) |
| 1800f1970 | panorama | wash makes a composition layer (+0x224 \|= 0x10) |
| 180189830 | panorama | mix-blend-mode names |
| 1817ea560 | client | svg attributes registration |
| 1817eae70 -> 181884ca0 -> 181884cd0 | client | svg attribute handler (index) |

## Fields

| Offset | Field |
|---|---|
| controller +0x954 | m_iScore |
| controller +0x790 | m_bIsLocalPlayerController |
| controller +0x6f4 | m_iConnected |
| controller +0x934 | m_bPawnIsAlive |
| controller +999 | team |
| inventory services +0x30 | its controller |
| inventory services +0x58 / +0x5c | m_unMusicID / m_rank |
| +0x74 .. +0x84 | m_nPersonaDataPublicLevel .. m_nPersonaDataXpTrailLevel |
| +0x88 | m_vecServerAuthoritativeWeaponSlots (count > 0: loadout arrived) |
| pawn +0x3504 | m_fImmuneToGunGameDamageTime |
| pawn +0x3508 | m_bGunGameImmunity |
| pawn +0x350c | m_fImmuneToGunGameDamageTimeLast |
| pawn +0x1e10 | m_GunGameImmunityColor (r, g, b, a bytes); server pawn +0x155c |
| pawn +0x1560 | controller handle |
| pawn +0x12f0 | m_pWeaponServices |
| pawn +0x1da4 | m_hHudModelArms |
| pawn +0x338 / +0x38 | scene objects / count |
| pawn +0x330 | scene node |
| identity +0x48 | model keyvalues |
| weapon vdata +0x700 | gear slot |
| rules +0x30 / +0x38 | ladder count / m_WeaponSequence names |
| weapon selection +0x20 / +0x30 | #weapon-selection-list / #weapon-selection--armsrace-list |
| +0x90 | -1 on build |
| +0xec | item count |
| item +0x10 | pips |
| think +0x30 / +0x44 | curtime / next time |
| think object -8 | last score seen |
| team counter +0x68 / +0x70 / +0x78 / +0x80 / +0x88 | ScoreAndTimeAndBomb / BG / GameTime / TimerText / BombStatus |
| +0x90..0xa0 / +0xa8 / +0xc0 | bomb images / GameScore / PlayerCount |
| +0xc8 / +0xd0 / +0xd8 | TeamAll / TeamLargeCT / TeamLargeT |
| +0x127c | layout |
| +0x1990 | avatar array (max 0x20) |
| +0x1284 / +0x1288 | T / CT count |
| +0x20b8 (0.5 at 180ecf5fe) | avatars' re-sort timer |
| avatar entry +0x20 / +0 | m_iScore / player slot |
| avatar +0x26 | #ArsenalProgress |
| CB +0x40 / +0x44 | BlueNoise / brdf_lut bindless index |
| CB +0x70 .. +0x80 | water_droplets .. rain_ripples |
| CB +0xb0 / +0xb4 | BlueNoise width - 1 / height - 1 |
| view CB +0x9e8 / +0x9ec | g_flRealTime / g_flGameTime |

## Constants

| Value | What |
|---|---|
| mp_dm_teammode | cvar 0x1824bc6e8 (registered 180086a10) |
| cl_weapon_selection_rarity_color | 0x1825d72a8, default 0, registered 18010c0b0 |
| mp_respawn_immunitytime | 0x1824bc5b8 |
| mp_maxmoney | 0x1824bc418 (registered 0x180087d50) |
| mp_playercashawards | 0x1824bc438 (0x1800883a0) |
| mp_teamcashawards | 0x1824bc448 (0x18008a560) |
| 0x182561558 on, 0x1825790a0 off | money panel cvars (taken as cl_drawhud / cl_draw_only_deathnotices) |
| 0.25 s | weapon list think |
| 10.0 (181ad0f70), 20.0 (181ada2ec), 1.0 (181ac6074), 0.7 (181b06550), 5.0 (181acaf24) | avatar scale remaps |
| 20 / 10 + 10 | avatars in layout 1 / else |
| 0x244ec9b0 | g_flSpawnInvulnerability attribute (x4) |
| 0xb2caf4df | g_cInvulnerabilityColor attribute |
| 0x181791cb4 = ff ff ff ff | default immunity colour (white) |
| T -0x8a3716 = ea c8 75 ff = rgb(234, 200, 117); CT -0x54483 = 7d bb fa ff = rgb(125, 187, 250); -1 with mp_teammates_are_enemies (bool 18211a6d8) | Arms Race immunity colours |
| 0x1825f5ef0 | `textures/dev/blue_noise_256.vtex` (1811cbac0) handle; brdf_lut.vtex -> 1825f5ee8; water_droplets .. rain_ripples -> 1825f5f00 .. 1825f5f20 |
| 0, 0.96, 0.9 | WEAPONSELECTION_UNSELECTED_HSV_TRANSFORM (on csgo-hud__color-0) |
| 0x3ed55555 = 1/2.4 | linear -> sRGB exponent |
| 0xffffffff | wash-color unset |
| CStylePropertyWashColor 0x1804e12a8; CStylePropertyMixBlendMode 0x1804de650 | vtables |

## The weapon list's ladder (CSGOHudWeaponSelection)

- Class tokens: +0x14 weapon-selection--armsrace, +0x16 weapon-selection--armsrace-list, +0x18 armsrace-item--status (the item's SwitchClass group), +0x1a --future, +0x1c --current, +0x1e --done, +0x20 armsrace-pip, +0x22 armsrace-pip--status, +0x24 --unearned, +0x26 --current (unused), +0x28 --earned, +0x38 hud-colorize-wash--hsv. vfn 0x500 SetHasClass, 0x508 SwitchClass(group, class), 0x108 SetVisible.
- **Build (180ec6bc0)**: rules exist, local team (+999) > 1, 180905820 on m_pInventoryServices (its controller's +0x790 and +0x88 > 0): weapon-selection--armsrace on, list emptied, +0x90 = -1, an item per ladder name, +0xec = count. Called from 180ecbfe0 when the rules' count != +0xec, and from 180eae1d0.
- **Item (180ea6120)**: WeaponIcon--ArmsRace snippet; armsrace-item--knife for weapon_knifegg; dialog variable armsrace-level = index (label visibility: collapse); the knife item's image is the local team's melee item instead of the name; both images (#armsrace-weapon-outline / -filled) `file://{images}/icons/equipment/%s.svg` of the name after its first '_' (strchr 0x5f); 2 pips (1 on the knife), each a Panel with armsrace-pip.
- **Think (180eafc30)**: every 0.25 s (curtime +0x30 vs +0x44, +0.25); the watched pawn (observer target or yours); Arms Race: its controller's m_iScore vs the last seen, changed -> `180ec3a80(list, score / 2, score % 2)`; then 180ecbfe0, 180ed1cb0. weapon-selection--fade never comes on in Arms Race (the 180769d90 tests, decompile lines 105-118). Events weaponhud_selection, round_start, spec_target_updated, ggprogressive_player_levelup only force the next think.
- **States (180ec3a80)**, item i, `d = i - level`: d < 0: --done, every pip --earned; d > 0: d < 4 -> `armsrace-item--next%d` (next1..3), else --future, every pip --unearned; d == 0: --current, pip k --earned when `k < score % 2`, else --unearned.
- **180ecbfe0**: armsrace-item--selected on the list while the watched pawn's active weapon's gear slot < 2 (the spectated player's when spectating); on the current item's filled image hud-colorize-wash--hsv on unless cl_weapon_selection_rarity_color is on and a gun is held; with it on, weapon-selection-item--rarity-%d of the held weapon's econ item.

### vcss

- #weapon-selection--armsrace-list: 100% tall, margin-bottom 93, flow up, collapsed unless weapon-selection--armsrace.
- .armsrace-item: right, opacity 0, height 120, margin-top -10, padding-top 5, margin-right 16, transition opacity / height / margin-top .2s; --next3 .25, --next2 .5, --next1 .75, --current 1 and margin-top 0, --current.--knife 0, --done 0 / height 0 / margin-top 0.
- Images: origin (100%, 50%), pre-transform-scale2d -1 1, padding 7, scale .7, bottom, transition .2s; outline wash black, hidden on --future / --current / --done; filled hidden except --current (.additive), --selected scale .9 brightness 1.5.
- #armsrace-pips: top, x -30, right, flow up, opacity .5 (1 on --current), margin-top -4, margin-right 5; carries hud-colorize-wash--hsv (earned pips draw the washed team colour, others stay black).
- .armsrace-pip: 10 x 10, margin-bottom 20, #000000c0, round; --earned white additive.
- `.weapon-selection--armsrace .gear-slot--0 / --1 .weapon-selection-item-icon-main { opacity: 0 }`.
- WEAPONSELECTION_UNSELECTED_HSV_TRANSFORM on ct-color rgb(150, 200, 250) -> rgb(148, 193, 238); on t-color #eabe54 -> rgb(223, 183, 91).

## The top bar in game_type 1 (CCSGO_HudTeamCounter)

- **Layout (180ec6730)**: 1 when 180769d30 and not 180769e60; +0x127c = layout; GameModeGunGame on the panel for layout 1; layout 1: 20 avatars into TeamAll, TeamAll and GameTime shown, BombStatus / GameScore / PlayerCount / team rows hidden; else 10 + 10 into the team rows.
- **Avatars (180ecec30)**: every controller with m_iConnected 0 / 3 (or 1808865b0) on team 2 / 3; layout 1: all into one array, sorted by 180eabc80 (m_iScore down, then player slot up), the first 20 drawn; Arms Race: the avatar's weapon = the ladder's entry at `min(score / 2, count - 1)` (item def by name, econ schema 0x148), else the best weapon (slot 0, 1, 2).
- **Scale** (180ecf883..180ecfc49, when T or CT count changed): layout 1: `s = Remap(T + CT, 10.0, 20.0, 1.0, 0.7)` on #TeamAll; else `Remap(max(T, CT), 5.0, 10.0, 1.0, 0.7)` on #TeamLargeCT / T; applied via 180dc75e0, from #TeamAll's transform-origin 50% 0%.
- **Avatar data (180eba820)**: Arms Race: health passed 0 (#HealthBarContainer hides: 180ecc1f0 line 391 shows it only for health > 0), the second value 0 too; the number = m_iScore / 2 in Arms Race, m_iScore in Deathmatch (180769d50 and not 180769e60), else 0; weapon icon `file://{images}/icons/equipment/%s.svg`.
- **180ecc1f0**: kill flags (killattribute HTC__Avatar__*) only when layout isn't 1; #ArsenalProgress shown when the number != 0 or Arms Race: label the number (V_Int32ToString), class `gglevel-%d` = count - number - 1 (0 = knife level, -1 = won); AvatarL__GGText--Player for the local controller, else AvatarL__GGText--Bot; the weapon panel with the icon when there is one.
- vcss: .GameModeGunGame #TeamCounter flow down, .team__large_container--left / --right collapsed; #ArsenalProgress centred, 100% wide, padding 0 2, z -1, flow down, ignore-parent-flow, y 54; .gglevel-0 / --1 wash gold + gg-last-level (brightness 1 -> 1.5, .5 s, infinite, alternate), its Image gg-last-level--image (img-shadow 0 0 4px 1 gold at 100%); .AvatarL__GGTextBG 100% x 32, #0000006f, bluedots .03; .AvatarL__GGText bold 22, centred, bottom; --Player #fff, --Bot #ffffff50; .AvatarL__GGIconBG 54 wide, margin-top 4, padding 2; .AvatarL__GGIcon centred, img-shadow 1px 1px 1px #00000090; .endofmatch hides it. hudteamcounter-equipmentinfo.vcss: .deathmatch / .gungameprogressive .equipinfo--score-time__bg mask masks/score-time-dm-mask.vsvg.

## Spawn immunity's look

- **Amount (180c67c40)**: 0 unless the pawn is alive and m_bGunGameImmunity and (mp_respawn_immunitytime > 0 or the warmup); then `clamp(m_fImmuneToGunGameDamageTime - now, 0, 1)`: 1 while more than a second is left, down to 0 over the last.
- **180c9d440** (`if (pawn+0x338 == 0) return`): entities = 18021a2c0(pawn) (the pawn and its scene node's children: held weapons, attached models) plus 180c7ede0(pawn) (the active weapon, its +0x1990 and m_hHudModelArms only when vfn 0xac8: in game the first-person arms and viewmodel never get it; the menu's preview agents do). For every scene object, unless the model keyvalues have `spawn_invuln_effect_override`: g_flSpawnInvulnerability = the amount, g_cInvulnerabilityColor = m_GunGameImmunityColor r, g, b / 255.0 (no gamma: a linear colour in the shader's linear HDR). No CS2 model carries the override (pak01 weapons/models/ and characters/models/: 224 m_keyValueText blocks, the agents' empty).
- **Other writers**: 180828340 returns at once while the weapon has an owner; an unowned (dropped) weapon gets 0 and colour (1, 1, 1). 180e6cf50: the UI's own blink.
- **m_GunGameImmunityColor** (server pawn +0x155c): constructor white; the only other writer is Arms Race's slot 8 (18094d9c0) on a team join (T / CT / -1 above). Deathmatch, the base rules and every warmup draw it white.

### The shader (csgo_character / csgo_weapon pixel shaders, same tail)

On the lit colour after the fog (_12895 / _19366: the fog's two terms, then the distance contrast and the last decal's burn, then this):

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

- **BlueNoise** (PerViewConstantBufferCsgo_t._m4 / ._m15): 1811fef80: CB +0x40 = the bindless index (render device vfn 0x650) of texture global 0x1825f5ef0; CB +0xb0 / +0xb4 = width - 1 / height - 1 (vfn 0x2d0). _m4 is c4 (0x40), _m15 c11 (0xb0, also the smoke trace's mask): core's blue_noise_256 (256 x 256 RGBA8888), its green channel, mask (255, 255), rows from the top.
- **g_flGameTime** (PerViewConstantBuffer_t._m1): the view-constants dump prints g_flRealTime from +0x9e8 and g_flGameTime from +0x9ec: _m0 / _m1, the game time (the curtime the decal burn's g_flLastDecalTime is compared with).

## The money panel (CSGOMoneyPanel)

- Visible (0x180eb0c70) when the gamerules exist, 0x180759930 is true, and (no local pawn, or an observer (vfn 0x4f0) whose mode isn't 2 / 3, ...) 0x180cb2100 is 0, cvar 0x182561558 on and 0x1825790a0 off.
- 0x180759930: `mp_maxmoney >= 1 && (mp_playercashawards || mp_teamcashawards)`. Arms Race's cfg (mp_maxmoney 0) hides the panel.

## The win panel

- [winpanel.md](winpanel.md): Arms Race's MVP is the winner, reason 5 "#Panorama_winpanel_mvp_award_gungame" ("MVP").

## Panorama's colours (panorama.dll)

- **Parser (18014b780)**: `#rgb[a]` / `#rrggbb[aa]`, rgb() / rgba(), names, `hsv-transform(<colour>, dh, s, v)` (inner colour recursive, floats by 18014ca80; rejected when |dh| > 360, s < 0 or v < 0); next `opacity-transform(...)`.
- hsv-transform: each channel / 255 -> 1803a2430 (`x <= 0.04045 ? x / 12.92 : V_powf((x + 0.055) / 1.055, 2.4)`, x clamped 0..1) -> 1803a27e0 (max, min, `s = (max - min) / max`, `h = 60 x ((g - b) / d, (b - r) / d + 2, (r - g) / d + 4)`, +360 when negative) -> `h = V_fmodf(h + dh, 360)` (+360 when negative), `s *= s`, `v *= v` (each clamped to 1) -> 1803a2680 (`i = (int)(h / 60)`, f, p, q, t, the six cases; h == 360 -> 0) -> 1803a2500 (`x <= 0.0031308 ? 12.92 x : 1.055 V_powf(x, 1/2.4) - 0.055`) -> x 255 truncated (cvttss2si); alpha kept.
- **wash-color**: getter returns 0xffffffff when unset (a multiply's identity); both UI shaders draw texel x vertex colour (panorama.vfx D_TEXTURETYPE `Texture0.Sample * input_1`; panorama_fancyquad: layer texel x input_3), so the wash multiplies the panel's colours (alpha kept). Help: "blended over the panel and all its children at composition time, tinting them; the alpha value determines the intensity". A wash makes the panel a composition layer (1800f1970). The function folding the wash into the vertex colour isn't located (slot 0x180's 8 callers are other interfaces).
- **brightness / saturation / hue**: panorama_fancyquad D_COLORCORRECTION: the layer's texel (sRGB-read: linear) to HSV, h + m0 (frac), s x m1, v x m2, then the contrast lerp toward 0.5 (m3), back to RGB, x the vertex colour. Brightness b is linear(c) x b for a flat colour; the target clamps.
- **-s2-mix-blend-mode** (names: normal, multiply, screen, additive, opaque): `additive` adds the source (CSS plus-lighter). panorama.vfx D_DSTCOLOR_BLENDMODE converts the vertex colour to gamma, blends with the destination copy (Texture4), converts back: the UI target is sRGB (blending in linear light).
- **svg attributes** (index): 0 fill, 1 fillopacity, 2 stroke, 3 strokewidth, 4 linecap (butt / round / square), 5 linejoin (miter / round / bevel), 6 strokeopacity, 7 svgopacity, 8 fillrule; each sets a value and its bit in a "set" mask, opacities clamped 0..1: the rasteriser's style overrides. The equipment icons' paths set only fill, so overrides on the root are what every path draws with.

## Unread

- Where the wash is folded into a layer's vertex colour.
- The money panel's two cvars' names (0x182561558, 0x1825790a0).
