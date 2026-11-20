# Round end panel, MVP, fun facts, round end sounds, end of match

client_20261015; server_20261015 (MVP, fun facts) and server_20261105 (round end sounds' server side, end of match); tier0_20261103 / tier0_20261015 (CUtlSymbolTable, the same code). Panorama from pak01: layout/hud/hudwinpanel.vxml, styles/hud/hudwinpanel.vcss, scripts/hud/hudwinpanel.vts, scripts/hud/hudwinpanel_background_map.vts, layout/honor_icon.vxml, styles/honor_icon.vcss, endofmatch*.vxml / .vts / .vcss, player_stats_card.vts, rating_emblem.vts, digitpanel.vts; maps/ui/match_mvp.vpk, maps/prefabs/misc/end_of_match.vpk; resource/csgo_english.txt; items_game music_definitions.

## Functions: the panel (client)

| Address | Module | What |
|---|---|---|
| 180ea2b30 | client | construction: loads `file://{resources}/layout/hud/hudwinpanel.xml` |
| 180eae240 | client | registers for round_start, cs_win_panel_round, round_mvp, hltv_replay, round_freeze_end, player_hurt, player_death; hides the panel (180ec9a20(0)), drops winpanel-mvp--show, +0x44 = 0 |
| 180eb3510 | client | the event handler (object - 0x20 is the panel) |
| 180d36bc0 | client | HLTV replay (+0x82) |
| 180eca700 | client | show by reason |
| 1802c4c70 / 180cb3a00 | client | thunk -> the team's clan name |
| 180eb6af0 | client | (local team, winner, &token, panel): the title classes |
| 180ec9a20 | client | (panel, show) |
| 18075ecc0 | client | game mode test (competitive's round end report) |
| 180d5a3b0 | client | SetHasClass on each HUD panel (HUD_WINPANEL_VISIBLE; only hudrush.vcss reads it) |
| 180ec8f10 | client | round_mvp: winpanel-mvp--show on; HudWinPanel_MVP(xuid, reason, team (controller +999)) -> _SetMVP; 180ec9170 |
| 180ec9170 | client | the music kit: MVP__MusicKit--show only for a kit id >= 2 (1 the default): icon `file://{images}/%s.png`, winpanel-musickit-name, the StatTrak line ("#SFUI_WinPanel_Playing_MVP_MusicKit_StatTrak") when musickitmvps > 0 |
| 180eaeac0 | client | think: +0x45 and curtime >= +0x48 and not the warmup (18076a1e0): 180ec8be0 |
| 180ec8be0 | client | the fun fact: only with a non-empty funfact_token: funfact-player-playerslot, funfact-d1..d3, winpanel-funfact = the token localized, winpanel-funfacts--show on |
| 180dc1ea0 | client | CSGOHonorIcon state (#jsHonorIcon): show-honor for an XP trail level > 0 (or +0x31), show-prime for Prime (+0x38), else show-none (collapsed) |

## The panel's handler (180eb3510)

- round_start: removes winpanel-basic-round-result-visible.
- round_freeze_end, when shown (+0x44) and the game phase (rules +0x84) isn't 5: winpanel-mvp--show off, 180ec9a20(0).
- round_mvp (unless the HLTV replay): `userid`, `reason`, `musickitmvps` -> 180ec8f10 (with cl_... nomusic tests).
- cs_win_panel_round: +0x45 = 1, +0x48 = curtime + 1, funfact_player +0x4c, funfact_token +0x50, funfact_data1..3 +0x58..+0x60, then 180eca700(final_event).

## Show by reason (180eca700)

1. Returns when the local controller has no team (+999 == 0) and isn't an observer (+0x790 ? DAT_1825603a0 : +0x6f0), or cl_draw_only_deathnotices (0x1825790a0 +0x58).
2. +0x84 = reason; 180ec9a20(1).
3. Reasons 1 3 4 9 13 15 18 19 -> T (2); 2 5 6 7 8 11 12 14 17 20 -> CT (3) -> 180eb6af0. 10 -> WinPanelRoot--Draw + "#SFUI_WinPanel_Round_Draw".
4. A winner team with a clan name: winpanel-title-s1 = it, "#SFUI_WinPanel_Team_Win_Team"; winpanel-title = the token localized.
5. 18 / 17: winpanel-surrender "#winpanel_end_cts_surrender" / "_terrorists_surrender" + WinPanelRoot--Surrender, else "".

180eb6af0: group "winclass" = WinPanelRoot--Win--T / --CT; local == winner: "winrelative" = WinPanelRoot--Win, "#WinPanel_RoundWon"; the other team: --Lost, "#WinPanel_RoundLost"; no team: "winrelative" emptied, "#SFUI_WinPanel_T_Win" / "#SFUI_WinPanel_CT_Win".

180ec9a20: winpanel-round-end-report-visible (competitive's report), WinPanelRoot--ForceHide = !show, --Show = show, winpanel-basic-round-result-visible = show, +100 = show, winpanel-funfacts--show removed; dispatches HudWinPanel_Show(reason) / HudWinPanel_Hide; HUD_WINPANEL_VISIBLE on the HUD's panels.

## Script (hudwinpanel.vts)

`_SetMVP(xuid, reason, team)`: #MVPAvatar from the player slot (team--TERRORIST / team--CT), dialog var player_slot (name label `{g:player_name:player_slot}`), MvpBackgroundMap.SetUpMapWinPanel, the reason's token (1 kills, 2 bombplant, 3 bombdefuse, 4 rescue, 5 gungame, 7 / 12 winner, 9 ace, 10 inferno, 11 blast, 13 / 14 the clutch ones, 15 / 16 three / four kills; else "#Panorama_winpanel_mvp_award"), jsHonorIcon.Set(xp trail level). The "MVP..." strings are in csgo_english.txt; gungame's is "MVP". The rest is the competitive round end report (HudWinPanel_ShowRoundEndReport), with its own sounds.

## Layout and timing (hudwinpanel.vcss)

- Root: y 190, 100% wide, centred, flows down; opacity .3s ease-out; --ForceHide collapses it; .endofmatch opacity 0.
- Result: 400 x 80, opacity 0 / scale3d(0, 1, 1) -> 1 over .25s ease-in; 4px side borders and background by winner (CT rgb(150,200,250) / rgba(9,40,61,.85), T #eabe54 / rgba(66,46,8,.85), lost #DB4437 / rgba(32,2,2,.877), draw white / rgba(255,255,255,.356)); world-blur; bluedots .04.
- Title: bold 64 "Stratum2 Medium Condensed" (one face, weight 500), spacing 8, upper case, 340 x 60, shrink, pre-transform-scale2d 1.5 -> 1 over 5 s ease-in once shown, washed with the winner's colour (negativeColor when lost; an observer's with the winner's).
- Arrows (images/hud/double_arrows.vsvg, 16 tall): translateX 25 -> 0 and brightness 10 -> 1 after .5 s over .25 s.
- Glitch (videos/digital_glitch.webm, 720 x 405, .additive): opacity .25 brightness 10 -> 0 / 1 after .5 s over .2 s; the white flash: gone at once when shown, back after .25 s when hidden.
- MVP banner: scale3d(0, 1, 1) -> 1 at once, width -> 640 (.non-premier) after .25 s; opacity mask images/masks/mvp_banner_fade-both-right-left_png.vtex; its white flash out after .25 s; avatar 72 x 72, reason (18px, black on the winner's colour), name (28px Stratum2 Condensed black, the winner's colour x brightness 1.5).

## The MVP banner's scene

- hudwinpanel.vxml's MapPlayerPreviewPanel #id-match-mvp-map: map ui/match_mvp, camera "camera", pin-fov vertical, transparent-background false; SetUpMapWinPanel -> _MvpMapPanelLogicNonPremier: TransitionToCamera('camera_start', 0), after .1 s ('camera_non_premier', 3); HideCharacters; SharedMapLogic: the effects stopped, the spot lights' colours, background_particles_squares started with SetControlPoint "20: 0 0 <team>".
- maps/ui/match_mvp: camera_start (-2, -258, 62), camera_non_premier (-2, -192, 62), angles (0, 90, 0), verticalfov 9, znear 4, zfar 10000; background_particles_squares at (0, 400, 57): ui_map_mvp_winner_nonpremier (10 s; child ui_map_mvp_winner_bg_np: a 64 x 5 grid of squares 20 apart (C_INIT_CreateOnGrid), colour from CP 20's z remapped 2 -> 3 to 0 -> 1); the world is a white card and three fragments out of view (the lights only light them), env_fog_controller fog (67, 162, 230) on nothing in view: the frame is the clear colour behind the particles.
- TransitionToCamera's blend is CUI_MapPreviewCameraManager's (the panel's +0x4c0; vtable 181ccbd88): slot 0x48 180e65c50 -> 180b833b0 (from the camera it had, over the seconds, from realtime Now()); each frame slot 0x10 180b82920: progress = 1808a4520 (RemapValClamped through SimpleSpline: `t = clamp((now - start) / duration)`, `(3 - (t + t)) t t`), done at the end; origin and fov lerped by it, angles fitted-slerped (180b595e0). See [pets.md](pets.md) "Camera blend", [cases.md](cases.md) "The camera manager".

## MVP (server_20261015)

| Address | Module | What |
|---|---|---|
| 18095d500 | server | round end processing: m_iRoundWinStatus 2 / 3: the rules' MVP object (+0xe20, vfn 0) if set, else 18090bae0; then (18095db96) the fun fact: 18029aed0(rules +0xee8, winner, reason, &out) unless reason 16, into m_sRoundEndFunFactToken +0x13e0, slot +0x13e8, data +0x13ec..+0x13f4 |
| 18090bae0 | server | the default MVP |
| 180922410 | server | per team (6 ints): players (team < 4, vfn 0x558 / 0xca8), alive (vfn 0x550), dead with +0x1599 set, dead without, and [5] dead with m_iPlayerState +0xd40 == 3 (picking a class) |
| 180b027d0 | server | damage services (+0x800): sum of m_DamageList (+0x48 count, +0x50 data, 0x78 a record) m_flActualHealthRemoved (+0x68) where m_hPlayerControllerDamager (+0x38) is this one, the recipient (+0x3c) isn't, m_bIsOtherEnemy (+0x74) == the flag |
| 180b12450 | server | damage-dealt post (action tracking): DMG_BURN (info +0x4c & 8) -> +0x1a4 += (int) damage (enemies: 180aca940), DMG_BLAST (& 0x40) -> +0x1a8; team damage -> +0x3e4; DMG_BURN also appends the victim's slot to +0x438 (count +0x430) once |
| 180a8ebe0 | server | a team kill: action tracking +0x3ec (round) and +0x3e0 (total) += 1, m_bJustDidTeamKill |
| 1809f1550 | server | CPlantedC4DefusedMVP (CPlantedC4::OnDefuse; defuser at +8) |
| 1809366f0 | server | game_type 0 / game_mode 5, or a cvar's match: the bomb MVPs go to the default |
| 1809f1910 | server | CPlantedC4ExplodedMVP (CPlantedC4::OnExplode; planter's pawn at +8, controller by +0xe14) |
| 180957aa0 | server | applied to every alive T in 1809f1910 |
| 180354920 | server | CSimpleHostageRescueMVP: the rescuer -> 4 (bot-controlled: the default) |
| 180a76f50 | server | SetMVP(controller, reason): m_eMvpReason (+0x934), m_iMVPs (+0x940) += 1, round_mvp (180a8b550: userid, reason, value +0x938, musickitmvps +0x93c, nomusic +0x932); returns early when the cvar at 0x18216a6e8 is set |

Default MVP (18090bae0), every controller in slot order (skipping m_bHasControlledBotThisRound +0x8e1):

- game_type 1: eligible unless game_mode 2 with mp_dm_teammode (cvar 0x1821107b0) where only the winners are; m_iScore +0x91c, a tie to m_iNumRoundKills (action tracking +0x7f8 -> +0x188); reason 6 in team deathmatch, else 5.
- Otherwise winners only (team +0x344 == +0xa44, or +0xa44 == 1): round kills, a tie to 180b027d0 (enemies). Reason by the new best: fire (+0x1a4) > `dmg x 0.5 - fire` (0x18177957c) -> 10, else blast (+0x1a8) the same -> 11, else 3 kills 15, 4 kills 16, else 1; then, for every winner looked at, kills == the losing team's [0] - [5] of 180922410 -> 9. Calls 180a76f50.

Defused MVP (1809f1550): 1809366f0 -> the default; a bot-controlled defuser -> the default; with a T alive (team 2 filter, vfn 0x550) and no team kill, or else round kills >= the best CT's (team 3: each pawn's +0xe48 -> +0x60) - 1 with no team kill: one CT alive -> 14, else round kills >= 3 -> the default (3 if it picks no one), else 3; anything else the default.

Exploded MVP (1809f1910): every alive T 180957aa0'd; the best T round kills (pawn +0xe48 +0x60) >= 4 or a planter team kill -> the default; the planter alive and one T alive -> 13, else 2.

The pawn's action tracking +0x60 is its round kills (its writer isn't located).

## Fun facts (CCSFunFactMgr, server_20261015)

### The pick (18029aed0)

1. None for a surrender (reason 17 / 18).
2. Every fun fact (the manager's CUtlRBTree +0x110 by id) evaluates (vfn 1); one that adds a result counts a true round (+0x20); the round count (+0x138) += 1.
3. Score: `((magnitude + 1) x (coolness x 1.2) + 0) - fact recency (+0x24) - player recency (+0x10 + slot x 4) x 0.7 + V_powf(1 - true / rounds, 4.0)` (constants 0x181779580 1.0, 0x1817a53cc 1.2, 0x1817a53c4 0.7, 0x181799ec0 4.0); the strictly best wins.
4. Then the 64 player recencies x 0.5 (0x18177957c), the facts' x 0.8 (0x18178bfb0), the winner's player's and fact's 1.0.
5. The result (FUN_180290520 appends it): { id, token, slot, d1, d2, d3, magnitude }.

### Evaluators

Each first: the enabled flag bit 1, flag 0x100 = only on reason 8 / 9, and 180936780 (game_type == 0, the game mode object's vfn 0x98).

| Class | Vtable | Evaluate | Fields and rule |
|---|---|---|---|
| CFunFact_StatBest | 0x18179bc30 | 18027a670 | +0x20 stat, +0x24 minimum, +0x28 flags, +0x2c filter: the highest round stat (signed, strictly: the first of a tie), a result when >= the minimum: the player, d1 the value, magnitude `1 - minimum / value` |
| CFunFact_StatSum | 0x18179bc48 | 18027a9f0 | the same fields; the stat summed over the filter's players, slot -1 |
| CFunFact_PlayerEvalFunction | 0x18179bbc8 | 18027a1e0 | +0x20 function(controller, pawn), +0x28 minimum, +0x2c flags, +0x30 filter. Filter bit 4: the best only (a tie for the best, starting from 0, gives none); else a result for every player at the minimum or above |
| CFunFact_GenericEvalFunction | 0x18179b290 | 180279de0 | +0x20 function(&slot, &d1, &d2, &d3), +0x28 flags; slot -1 and data 0 before the call; magnitude 0 |

Player filter (18027a7c0..18027a8e9, the same in all three): the pawn from the controller's +0x8ec handle; bit 1 team 3 (CT), bit 2 team 2 (T); controller and pawn set; a bot pawn (vfn 0xc20) whose controller has +0x8e2 (m_bHasBeenControlledByPlayerThisRound, not m_bCanControlObservedBot +0x8e8; [bot-takeover.md](bot-takeover.md)) is out; without bit 0x100 one with m_bHasControlledBotThisRound (+0x8e1) is out; never team 1; bit 0x10 and bit 8 both want the pawn dead (each calls IsAlive, vfn 0x550, and skips a live pawn: from the disassembly, so 0x1c survived_multiple_attackers too is for the dead only); 0x20 the winners (team == m_iRoundWinStatus +0xa44), 0x40 the losers, 0x80 a kill this round (round stat 2 != 0).

### Registry and stats

- 61 factories 180292aa0..180294120, all in the static list 0x181d9bfe0 (61 entries of { 0, factory }; ids 0x27 / 0x28 / 0x33 / 0x34 / 0x40 included). Each: id +8, token +0x10, coolness +0x18, the vtable, the parameters.
- CCSGameStats is the global 0x181f4ea10 (vtable 0x18178a2a8); a player's block 1801cafc0(stats, controller) = `stats + slot x 0x1128 + 0x9c`; three int arrays of 0x12e stats: +0 delta, +0x4b8 round (what the fun facts read), +0x970 match; `+ 0x44a9c + team x 0x4b8` a team's.
- IncrementStat 1801cf720(stats, controller, id, delta, plain): skips a controller with +0x834 set; inlined copies elsewhere.
- Stat table 0x181dfb6b0 ({ id, name, label, flags }, 32 bytes): 0x0 total_shots_hit, 0x1 total_shots_fired, 0x2 total_kills, 0x4 total_damage_done, 0x2b / 0x2c / 0x34 knife / hegrenade / taser kills, 0xb6 headshot kills, 0xb7 enemy blinded kills, 0xba enemy weapon kills, 0xbb knife fight kills, 0xc3 rescued hostages, 0xc4 broken windows, 0xcb zoomed sniper kills, 0xcc weapons donated, 0xcf dominations, 0xd0 overkills, 0xd1 revenges, 0xd2 MVPs, 0xd3 contribution score; the round-only 0xb8..0xd7 others have no name.
- AT = the pawn's action tracking services (+0xe48) unless "controller AT".

### Each fun fact

| Id | Token | Cool | Evaluator / input | Writer |
|---|---|---|---|---|
| 0x0 / 0x1 | ct_win_no_kills / t_win_no_kills | 0.4 | 180296b70 / 180297170: winner 3 / 2 and m_bNoTerroristsKilled +0xeb4 / m_bNoCTsKilled +0xeb5 | RestartRound sets +0xeb4..+0xeb7 = 0x01010101 (180952fd6); PlayerKilled (18094aa10, 18094aeea) clears the victim's team's and m_bCanDonateWeapons |
| 0x2 | kill_defuser | 0.5 | player 180296f80: AT +0xc0; filter 0x22 | 180a44f40 (the pawn's kill credit, enemies only: 180acaa80): the victim's m_bIsDefusing (+0x14b6) |
| 0x3 | kill_rescuer | 0.5 | 180296fa0: AT +0xc1; filter 2 | 180a44f40: the victim's AT m_bIsRescuing (+0x224), the killer's AT +0x21c unset (set by a hostage's damage, CHostage's 18035ad9e after its "hostage_hurt" attacker test; cleared by 180a47f40), the killer not a bot (pawn vfn 0xc20 = 1801d1f10: FL_FAKECLIENT, +0x388 bit 4) |
| 0x4 / 0x5 | t / ct_win_no_casualties | 0.2 | 180297150 / 180296b50 | as 0x0 |
| 0x6 | damage_with_grenade | 0.5 | StatBest 0xd4, min 150 | RadiusDamage (18094debf, 18094e5f9): (int) the info's m_flDamage (+0x44) after the hit, an enemy victim (HE and the C4's blast) |
| 0x7 | kills_grenades | 0.7 | StatBest 0x2c, min 2 | the kill handler's weapon table (0x181e01d50, 0x28 a row, filled at run time) |
| 0x8 | kills_with_single_grenade | 0.8 | 180296fc0: AT +0xc4, min 2 | nothing writes +0xc4 but the spawn's resets (180a35b5f, 180a4665c, qword at +0xc4): always 0 |
| 0x9 | damage_no_kills | 0.2 | 180296bf0: stat 2 == 0 ? stat 4 | 1801c8c50: stat 4 += (int) the result's m_flDamageDealt (+0x20), enemies |
| 0xa | killed_enemies | 0.4 | StatBest 2, min 3, 0x101 | the kill handler (1801c9040, chunk 1801c918b): stat 2 on the killer's original controller (+0xe14) |
| 0xb / 0xc / 0xd | first_kill / first_blood / short_round | 0.2 | 180296e60 / 180296d40 / 180297050 | |
| 0xe | best_accuracy | 0.2 | 180296450: shots (stat 1) >= 15.0 ? cvtss2si(hits (stat 0) x 100 / shots) : 0; min 50, filter 0xc | stat 0 has no writer in this build (no IncrementStat, no inlined add, no weapon table entry): 0 |
| 0xf | knife_kills | 0.4 | StatBest 0x2b, min 1 | the weapon table |
| 0x10 | blind_kills | 0.9 | StatBest 0xb8, min 1 | 1801c9040: the killer's blindness end (18017e420(+0xd3c start, +0xe04 duration)) still ahead and its flashed amount (1802304b0) >= 0.3. 1802304b0 is server_20261105's 1802106c0 ([death-notice.md](death-notice.md)): the same instructions and fields (+0xd3c / +0xe04 / +0xe08); its inner 180ac0d80 = 1802106c0's 180ac8b40 |
| 0x11 | kills_with_last_round | 0.6 | StatBest 0xb9, min 1 | 180a44f40 (180a45478): the killer's active weapon's clip1 (vfn 0xac0(0) = m_iClip1 +0xec0, 1809b6b00) == 1, the info's weapon (+0x40) set and its CSWeaponType (vfn 0xc60, item +0x520) not 5 (sniper) or 0 (knife), its class not weapon_taser (0x181e06028, set from "*weapon_taser" at 1800b18e0), the killer the info's attacker, not a bot |
| 0x12 | donated_weapons | 0.3 | StatBest 0xcc, min 2 | the drop key's drop (180b03210, 180b0341a): with m_bCanDonateWeapons and the weapon's +0x1034 unset: +0x1034 = 1, donor (+0x1030) = the dropper (180a1bdf0); the pickup (180b14480, 180b149e4..180b14a1e): m_bPickedUpWeapon = 1, a donor (1809f8d00) gets 0xcc (1801c8e30, no team test) and is cleared |
| 0x13 | posthumous_kills_with_grenade | 1.0 | StatBest 0xd5, min 1 | 180a44f40 (180a453cb): the killer's pawn dead, the inflictor's class weapon_hegrenade (0x181e06130, "*weapon_hegrenade" at 1800b13a0), not a bot |
| 0x14 | knife_in_gunfight | 0.4 | 180296fd0: the victim's AT +0xcd; filter 0 | 180a44f40 (180a4556e): the victim's active weapon a knife (type 0, class not weapon_taser), the info's weapon set, its class not weapon_knife, type not 7 (C4) or 9 (grenade), the victim's pawn vfn 0xc28 (1801d20d0: original controller +0xe14 differs from controller +0xc98, a taken-over bot) false. The class is the weapon's +0xff0 symbol (the designer name) against "*weapon_knife" (0x181e06100, set at 1800b1460): the CT knife only, not weapon_knife_t or a skin's |
| 0x15 / 0x16 | num_times_jumped / fall_damage | 0.1 / 0.2 | StatBest 0xbf min 20 / 0xc2 min 50 | no writer (player_jump fired at 180ab4e1b, player_falldamage at 1809b5de0; CCSGameStats listens to neither): 0 |
| 0x17 | items_purchased | 0.2 | StatBest 0xcd, min 4 | 180b0f1e0 (+1, the purchase record) / 180b1ce60 (-1) |
| 0x18 | won_as_last_member | 0.6 | 180297280: winner 2 / 3, 180922410's winners alive 1 and losers alive 0: the living winner, d1 its stat 0xc0, true above 1 | 1801c9040: stat 0xc0 when the killer's team has 1 alive and more than one dead (the counts' [team x 6 + 3]: dead without +0x1599) |
| 0x19 | number_of_overkills | 0.5 | StatBest 0xd0, min 2 | 1801c12a8 (the nemesis code, game_type 1 only): 0 in game_type 0 |
| 0x1a | shots_fired | 0.2 | StatSum 1, min 100 | 1801c9c40 (from the shot 180a70388; skipped once m_iRoundWinStatus != 0: 180936e00) |
| 0x1b | money_spent | 0.2 | StatBest 0xce, min 5000 | the account change 180af82f0: amount < 0 (or a "sellback" refund) -> 1801c8a30 adds -amount; > 0 -> 1801c8970 stat 0xf |
| 0x1c / 0x1d | survived / died_from_multiple_attackers | 0.4 / 0.3 | 180297030 -> 180b024b0(damage services): records whose damager isn't me, recipient is me, m_bIsOtherEnemy (+0x74); min 3; filters 0xc / 0x14 (both: the dead) | the damage records |
| 0x1e | damage_multiple_enemies | 0.2 | 180296be0 -> 180b02380(svc, 0): records with me the damager and an enemy recipient; min 3 | the damage records |
| 0x1f | grenades_thrown | 0.3 | StatBest 0xd6, min 3 | 1809cd1e7 (by the grenade_thrown event) and 1809b17b0, the death drop's live grenade (below) |
| 0x20 | used_all_ammo | 0.5 | 180297190: weapon slots 0 and 1 (180c7e7e0(svc, slot, -1)) both held and vfn 0xaa0(0) (180b4f180: ammo left) false for both | the clip and reserve |
| 0x21 | defended_bomb | 0.5 | StatBest 0xbc, min 2 | 1801c9040: killer team 2, gamerules +0x95f (bomb planted), 1801d1f20(killer or victim): a ticking C4 within 480 |
| 0x22 | items_dropped_value | 0.4 | StatBest 0xd7, min 10000 | 180b03210 (180b033de): a weapon whose owners vector (+0x1018) hasn't the dropper (180a06cf0), then 1809ef490 adds it: + its price (vfn 0xb88) |
| 0x23 | kill_wounded_enemies | 0.2 | StatBest 0xc1, min 3, 0x101 | 1801c9040: the victim's 180b024b0 > 1 |
| 0x24 | used_multiple_weapons | 0.5 | 180297270: AT +0xf8 (the used set 0xd8's count), min 4 | 180a43d10 (from 1801c9c40): the shot's weapon class unless its tags (item +0x320, +0x870 table) hold weapon_knife / weapon_c4 / grenade; also AT +0x78 += 1 |
| 0x25 / 0x26 | terrorist / ct_accuracy | 0.1 | 1802970f0 / 180296af0: 18029b450(team) = the team's hits / shots when shots > 15 else 0; the team's > 0.3 (0x18178bfa4) and > the other's: d1 cvtss2si(x 100 (0x18178c000)) | stat 0 unwritten: never |
| 0x27 / 0x28 | best_terrorist / best_counterterrorist_accuracy | 0.1 | 1802967e0 / 1802964e0: over the team, a player's hits / shots once shots > 15 (else the register keeps the last value), the best strictly; best - team < 0.25 (0x18178bfa0) gives none; d1 / d2 the two x 100 | never (stat 0) |
| 0x29 | kills_headshots | 0.4 | StatBest 0xb6, min 2 | the kill handler (info flags & 0x80000) |
| 0x2a | kills_with_stattrak_weapon | 0.3 | StatBest 0xbd, min 3 | no writer: 0 |
| 0x2b | broke_windows | 0.1 | StatBest 0xc4, min 5 | no writer: break_prop (1801cb12a -> 1801c7d90) looks the prop's model up in stats +0x45420, which the constructor 1801bad20 (1801baf63..1801bb0d1) fills from the static list 0x181d97690 (10 rows { model, stat }: models/props/cs_office/computer_caseb, computer_monitor, phone, projector, TV_plasma, computer_keyboard -> 0xc7; radio -> 0xc8; trash_can, file_box -> 0xc9; models/props_junk/watermelon01 -> 0xca), then adds stat 0xc5 (props broken); nothing adds 0xc4: 0 |
| 0x2d | defused_with_dropped_kit | 0.5 | 180296c80: AT +0x1fd; filter 1 | 180a14be0 (180a1520d): at the defuse when AT +0x1fc is set; nothing sets +0x1fc (only resets: 180a3b339, 180a4668a): 0 |
| 0x30 | default_weapon | 0.1 | 180296c40: 180936450 (a pistol round: game_type 0, m_iTotalRoundsPlayed +0xd80 == 0 or mp_halftime and maxrounds / 2, GetStartMoney <= 800 (0x320)) -> 0, else the weapon services' m_bPickedUpWeapon (+0xb10 +0xda) unset -> 1; filter 0xa8 | set only by BumpWeapon (180b14480, CCSPlayer_WeaponServices vtable 0x181920588 slot 0xe8: a touch or +use pickup); GiveNamedItem (server_20261105 180ab85f0) equips through Weapon_Equip 180b23a70 directly, so a buy or the spawn's loadout leaves it unset; the spawn's 180a46691 clears it. m_iTotalRoundsPlayed: game_type 0's only increment is RestartRound's (180950b52, the next round's start; 18091ca0e is CCSGameModeRules_ArmsRace's round end, vtable 0x1818bda08 slot 0x20), so at the fun fact it is the rounds before this one |
| 0x31 | rounds_without_dying | 0.6 | 180297040: the controller AT +0x3b8, min 3; filter 0x2c (dead winners) | 180b1d1e0 per controller from 180b13750 at 18095df42, after the fun fact (18095db96): a live pawn's +0x3b8 + 1 (+0x3bc its best, +0x3c0 the total), else 0; also 0 while controlling a bot (180a80240 = m_bControllingBot +0x8e0) |
| 0x32 | taser_kill | 0.7 | StatBest 0x34, min 1 | the weapon table |
| 0x33 / 0x34 | ct_win_time / ter_win_time | 0.2 | 180296b90 / 1802970a0: 180922b20 (elapsed) < 30.0 (0x18178bfe0) and m_iRoundWinStatus 3 / 2: d1 (int) the time; flags 0x101 | |
| 0x35 | bots_assumed | 0.2 | 180297010: controller +0x8e4, min 2, filter 0x104 | m_nBotsControlledThisRound: TakeControlOfBot 180a9cbe0 adds 1, the round reset 180a9aba0 zeroes it |
| 0x36 | domination | 0.3 | 180a72970: m_nPlayerDominated (+0x850) bits when 180936810 (game_type == 1), filter 0x84 | never fires (game_type 1 for the count, 0 for the evaluator) |
| 0x37 | revenge | 0.3 | StatBest 0xd1, min 1 | no writer: 0 |
| 0x38 | empty_guns | 0.3 | 180296d30: AT +0x1b8 (the emptied set 0x198's count), min 2 | 180a43aa0 (from 1801c9c40) when the shot's weapon is out of ammo (vfn 0xaa8 180b74660: UsesClips (0xa98) and !HasAmmo(0) (0xaa0), and the secondary ammo likewise) |
| 0x3a | bomb_carriers | 0.3 | 180296ae0: controller AT +0x1a0, min 2 | 180afac30 (from 180a44f40's tail): the victim holds weapon_c4 (1801cf130) or its AT +0x68 (the last C4 drop time: 1801dbcbd afk drop, 180afcf75 the drop) > 0.0 (18017ea80): +0x1a0, +0x2b0 |
| 0x3b | knife_without_ammo | 0.3 | 180296ff0: AT +0x64, min 2 | 1801cef50: a kill by the weapon_knife class (the CT knife) with the primary and secondary held (180b036b0 / 180b036d0) all in the emptied set |
| 0x3c | molotov_burns | 0.3 | 180297000 -> 180b025c0: controller AT +0x430, min 2 | 180b12450 |
| 0x3d / 0x3e / 0x3f | defuse_was_close_call_tenths / hundredths / thousandths | 0.8 / 0.9 / 1.0 | 180296cd0 / 180296ca0 / 180296d00 -> 1802ad510(max 0.5 / 0.1 / 0.01, scale 10 / 100 / 1000): the first CT pawn (team 3 iterator) with AT +0x200 in [0, max]: d1 cvtss2si(t x scale) | 180a14be0 (180a14d44): the defuser's AT +0x200 = m_flC4Blow (+0xa9c) - now; the spawn resets it to -1.0 |
| 0x40 | (none) | 0.0 | 1802964d0: true | wins a round where nothing else scores above 0; the token is empty, so the panel shows nothing (180ec8be0) |

### The death drop's live grenade (0x1f)

180afd650 is server_20261105's death drop 180b05460 ([drops.md](drops.md); strings weapon_c4, weapon_taser, item_defuser / item_cutters, weapon_healthshot, the death grenade list; called for a human from 1801dadc0 / 180911bf9, a bot taking 180afccb0). Step 7 at 180afdcb0:

1. The active grenade (cast 1816af350), not out of ammo (vfn 0xaa8), its pin pulled (+0x1282) or m_fThrowTime (+0x1288) above 0.0 (18017ea80 against 0x18177a734).
2. vfn 0xdc0 -> 1809b17b0: emitted (vfn 0xdd0) at `origin + view offset (+0x818, 1801595e0) + forward (EyeVectors 180b47cb0) x 16.0` (0x18177de10), the pawn's velocity (1803d0150) with `z + -1.0` (0x18177de30) unless exactly 1.0, an angular impulse (600, RandomInt(-1200, 1200), 0), stat 0xd6, the grenade off its owner (1809b00b0). Create drops the impulse's value; the spin is Spawn's ([grenades.md](grenades.md) "The spin").
3. Then mp_death_drop_grenade 2 / 1 / 0 drop no other grenade, 3 every other one (180afdd27..180afde58).

### Helpers

18017ea80 (float a vs b: -1 / 1 / 0, 0x80 unordered), 180c80830 (the player iterator's team filter: controller or pawn team == the filter's), FUN_18029b450 (team accuracy), 180936450 (pistol round), 180936810 (game_type == 1), 180936e00 (m_iRoundWinStatus != 0). CCSWeaponBaseGun vtable 0x1818e8bd8: slot 0xa58 classname 1809b7800, 0xaa0 HasAmmo 180b4f180, 0xaa8 out of ammo 180b74660, 0xac0 clip 1809b6b00, 0xaf0 180b4d900 the reserve, 0xc60 the weapon type 1809b89b0.

### The sets' count (tier0 CUtlSymbolTable)

The used set (AT +0xd8, 180a43d10) and the emptied set (+0x198, 180a43aa0) add the weapon's class (vfn 0xa58) with `AddString(CUtlSymbolTable*, CUtlSymbol* out, const char*, bool* created)` (export 0x1801a5860: strlen, then the worker 0x1801a58c0).

| Offset | Field (constructor 0x1801a5300 (this, a, b = +0x30, insensitive = +0x58)) |
|---|---|
| +0x00..+0x14 | hash index (find 0x1801a6830; hash 0x180067b10 when +0x58 is set, else MurmurHash2 seed 0x31415926 inline) |
| +0x20 | CUtlVector<uint> count (data +0x28, allocation +0x30, flags +0x34): the string pool offsets; String 0x1801a5af0 reads data[sym] |
| +0x38.. | string pool (0x18007e0b0) |

The worker: a string the index already holds returns its symbol and changes nothing; else, below 0xfffe entries (`cmp [this + 0x20], 0xfffe; jge` -> the invalid symbol 0xffff), `*created = 1`, the string copied into the pool and its offset appended (0x180017480: `inc dword [vector]` at 0x18001759a), the symbol = the old count. RemoveAll 0x1801a5b60 zeroes +0x20. So +0x20 (AT +0xf8, +0x1b8) is the number of distinct class names added (the 65534 cap never reached).

## Round end sounds (client 180ceaab0, the client mode's event handler)

The win panel plays none (hudwinpanel.vts' PlaySoundEvent calls are the round end report's).

| Event | What |
|---|---|
| round_start | StopSoundEvents.StopAllExceptMusic |
| round_end | winner, reason; nothing more for reason 16 (game commencing). The watched player: the local controller, or for a spectator (team 1) / an observer the observer target (180c7b9e0). Music for game_type 0 (180769bb0: game_mode 6 / 1 / 3 / 4 / 2, or 180769cf0: 0 / 0): no watched player or winner != its team -> PlayMusic(9, LostRound), else PlayMusic(8, WonRound), each unless the event's nomusic == 1. Announcer: winner 3 and reason 7 -> "Announcer.BombDefused" + ".CS2_Classic" (index 0 of 181ca0c90), or for a CT's own client with the event's legacy 1..3 Event.BombDefused_Legacy1..3; then the sound's duration (2.0 when it has none) + 0.3 (0.7 legacy) gates something at +0x98; winner 3 and reason 11 -> no line (its Event.HostageRescued's duration only); other CT wins in game_type 0 (180769cd0) -> Announcer.CTWin.CS2_Classic; winner 2 and reason != 19 in game_type 0 -> Announcer.TWin.CS2_Classic; else (a draw) reason != 16 -> Announcer.RoundDraw.CS2_Classic |
| round_mvp | musickitid (0xffff default); a real kit (`(kit - 2) & 0xffff < 0xfffd`) or game_type 1 (180769d30): 180ec8970 true -> PlayMusic(11, MVPAnthem, kit), else StopSoundEvents.StopAllMusic. 180ec8970: with snd_mute_mvp_music_live_players (182579510) and nomusic == 1, true only for a local pawn passing vfn 0x4f0 and 18094dc30 (read as alive on a team) or game_type 1; else true |

PlayMusic 18076cd70(type, kit): types 8..11 but 10 set the round end music flag (1824bdae4), which then blocks types 5..7 (bomb planted, bomb ten seconds, ten seconds); types 1..3 and 13 / 14 clear it; an HLTV replay plays nothing. The name: table 182212ae0 [0 ?, 1 StartRound_GG, 2 StartRound, 3 StartAction, 4 DeathCam, 5 BombPlanted, 6 BombTenSecCount, 7 TenSecCount, 8 WonRound, 9 LostRound, 10 GotHostage, 11 MVPAnthem, 12 Selection, 13 MatchStart, 14 MatchEnd, 15 MatchFound, 16 LoadingScreen] + "." + the kit's music definition name, "valve_cs2_01" by default (items_game music_definitions 1: valve_cs2_01, "Valve, Counter-Strike 2"); a kit id 0xffff asks the local / observed player's.

Volume: the csgo_music events name volume_convar snd_roundend_volume / snd_mvp_volume (with _casual / _armsrace / _deathmatch / _rush ones by snd_music_mode), registered in client.dll at 1800f8f3d / 1800f90bd / 1800f8ffd / 1800f917d / 1800f923d and 1800f874d / 1800f88cd / 1800f880d / 1800f898d / 1800f8a4d: float [0, 1], default 0.16, flags 0x80080.

Server side (server_20261105): TerminateRound 1809654b0 sets gamerules +0x140c (round_end's nomusic, written by 18094e5f0 only when set) when a pawn of each team is alive (vfn 0x550 by team +0x344), unless (cvar 18211a3f0, read as mp_halftime) in the first half (+0xf24 == 2) it is the last round before halftime. +0x1410 (legacy) only for a CT win by defuse with no T alive, from the CTs' largest defuse time left (AT +0x200, unnamed between m_hLastWeaponBeforeC4AutoSwitch 0x1f8 and m_bIsRescuing 0x224: -1.0 from the services' reset (slot 19 180a43140), written by CPlantedC4::OnDefuse 180a1ccd4 as `m_flC4Blow (+0xa9c) - now` for the defuser), starting from -1: < 1 -> 3, < 3 -> 2 with RandomFloat < 0.75, < 7 -> 1 with RandomFloat < 0.5.

## End of match

| Address | Module | What |
|---|---|---|
| 180daae60 | client | CCSGO_EndOfMatch's listener: cs_win_panel_match sets +0x19; cs_game_disconnected / cs_match_end_restart / nextlevel_changed clear +0x19 / +0x1a; hltv_replay's "delay" sets +0x1a; with +0x19 and not +0x1a -> 180db8390(menu, 0), else 180da1460 |
| 180db8390 | client | (menu, hard cut), once (+0x38): the panel's vfn 0x108(1); team_intro_end and hide_deathpanel fired; HudVanityLoadout found and passed to 180df5d00; "snippet-eom-lower--default" into #id-eom-chat-and-score; the scoreboard moved into #id-eom-scoreboard-container with class eom-scoreboard; CCSGO_HudVoiceStatus moved into #id-eom-chat-container ("Error locating panel id-eom-chat-container ..." when missing), it and CCSGO_HudChat given EndOfMatchChat; EndOfMatch_Show (hard cut = the argument) dispatched; the HUD's panels given a class (180d5a3b0 with the symbol at 1825c89f8). Back at EndOfMatch_Shutdown |
| 180c76830 | client | client mode events: team_intro_start -> PlayMusic(13 MatchStart), team_intro_end -> PlayMusic(2 StartRound) (both unless game_type 1, 180769d30, and gated on the flags at mode -0x10e1 / -3: unread); cs_win_panel_match -> PlayMusic(14, MatchEnd) unless game_type 1 (same flags), music state +0x58 = 14 |
| 1800f823c | client | registers snd_menumusic_volume: float 0..1, default 0.04, flags 0x80080 (_casual / _armsrace / _deathmatch / _rush the same) |
| 18009fbb3 | server | registers mp_match_restart_delay |
| 18009e803 | server | registers mp_endmatch_votenextmap |
| 1800a45d0 | server | registers mp_warmuptime_match_cancelled |

Music.MatchEnd.valve_cs2_01: endofmatch.mp3, volume 0.8, loop 32.4..42 s, volume_convar snd_menumusic_volume.

Server convars (server_20261105): mp_match_restart_delay int, default 25, 1..9999, flags 0x82000 "Time (in seconds) until a match restarts." (no gamemode cfg sets it); mp_endmatch_votenextmap bool 1; mp_endmatch_votenextleveltime float 20; mp_match_end_restart bool 0; mp_match_end_changelevel bool 0; mp_win_panel_display_time float 3 (Competitive / Wingman / Casual cfgs 3, deathmatch / Arms Race 1). Official servers end the session after the match.

The panorama (endofmatch.vts):

- Panels in the layout's order (default: win, characters, rank, skillgroup, voting; premier: win, characters, skillgroup, rank, voting), revealed at 0 / 0.5 / 1.25 s; StartDisplayTimer; the timers on only for the last panel outside queued matchmaking.
- endofmatch-win.vts: 5 s, not for deathmatch or a winning_player; the result by the winning team and the local team (a spectator: the winner's), the scores your side first. MatchEndWinData's match_cancelled (#SFUI_match_cancelled, no won / lost) and cancel_reason_code (EomCancelReason<n>.show: 1 #SFUI_match_abort_match_vac_live .vaclive red, 2 #SFUI_match_abort_match_network_event .network-event black, 3 #SFUI_match_abort_match_abnormal_behavior_pano .vaclive); endofmatch.vcss .eom-cancelled.
- endofmatch-skillgroup.vts (Premier): 1.5 s, 5 s when the rating changed; GetWinLossStyle no-points (new 0, or established now, or no change) / lost-points / gain-points; "+N Points" / "-N Points" (eom-premier-points-gained / -lost, 0 when established), "#cs_rating_rating_established"; UI.Premier.EOM.SlideIn, then RankNeutral / RankDown / RankUp; the new rating 0.75 s on.
- eom-characters: EOM_Characters is no registered panel: endofmatch.vts starts it at 0.5 s with SetWantsCamera, its _DisplayMe (the lineup over the end_of_match prefab: end_of_match_camera and end_of_match_lineup_start / _end), then UIPanorama.gameover_show. Its player stats cards (player_stats_card.vts: each player's nomination, [accolades.md](accolades.md)).
- eom-voting: endofmatch-voting.vxml / .vts / .vcss (MapGroupSelection tiles over mainmenu_play.vcss's .map-selection-btn, the 360p shots, "<font color='#ffc130'>votes</font>/votes_to_succeed", the 0.2 s update, the winner's vote_check, the tie's map-selection-btn__gradient--whiteout flicker, the sounds); the last panel, no display timer.
- The Premier emblem: RatingEmblemAnim (0.75 s: SetXuid with presentation 'digital') -> rating_emblem.vts _SetPremierRatingValue: DigitPanelFactory.MakeDigitPanel(major, 2, '', 1, #digitpanel_digits_premier " 1234567890,?") and (minor, 4), set at once when made, then rolled (digitpanel.vts: translate3D(d %, -index x 100 %) over 1 s, cubic-bezier(0.9, 0.01, 0.1, 1)); SplitRating's parts with their spaces. The particles (RankSkillgroupParticles) are the skill group modes'; Premier's options have do_fx false.
- Strings: eom-win "MATCH RESULT", eom-skillgroup "SKILL RATING", eom-rank "RANK UP", eom-voting "VOTING", eom-result-win3 / -loss3 / -tie3 "VICTORY" / "DEFEAT" / "TIE", eom-skillgroup-win:f "{s:rating_type} {matcheswon, plural, one{Match} other{Matches}} Won".
- Assets: the five eom sound events; images bracket.vsvg, premier.vsvg, premier-rankup-bg / -dash, the fade masks, linemap / premier_gain / premier_lost / speed_lines.webm.
- Queued matchmaking keeps the game time labels off.

## Unread

- The flags gating 180c76830's intro / match-end music (mode -0x10e1 / -3).
- The pawn's action tracking +0x60 (round kills) writer.
