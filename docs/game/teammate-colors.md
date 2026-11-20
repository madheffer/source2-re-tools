# Competitive teammate colours and the match stakes

server_20261105, client_20261015; pak01 panorama (scripts/common/teamcolor.vts, scoreboard.vts, teamintromenu.vts,
match_stakes.vts, layout/hud/hudteamcounter.vxml, styles/csgostyles.vcss, hudteamcounter.vcss, match_stakes.vcss),
csgo_english.txt.

## Functions (server)

| Address | What |
|---|---|
| 180a6bdd0 | controller constructor: +0x828 = -1 via 180a8ce80 |
| 180a8ce80 | colour state-changed setter |
| 180a79750 (controller, value) | plain colour setter |
| 18093de70 | colour mode: g_pGameTypes (182125888) vfn 0x98 game_type == 0 and vfn 0xa0 game_mode in {6, 1, 3, 4, 2} |
| 180a9b940 (controller, force) | the assignment (below) |
| 180a761a0 (obj, team) | the "team full" latch (below) |
| 180cbc9a0 / 180c86be0 / 180c88670 | walk the team's controllers ({ team, 1 }, slot order) |
| 180a9e720 | controller think (from 180a9ab30, which counts +0x944, and 180a9a740) |
| 18093e410 | gate for the GC per-account list copy |
| 1801ad7a0 | CSource2Server vtable 181990f38 slot 89 (0x2c8): reassign everyone |
| 180a71cb0, 180a79c60, 180a79790 | called by slot 89 |
| 1800a70c0 -> 1800aa9f0 | engine2: connectionless reservation packet 0x21, state 2 (slot 89's trigger) |

## Functions (client)

| Address | What |
|---|---|
| 1800adb9c .. 1800ade9c | register cl_teammate_color_1..5 |
| 1800adf50 | register cl_teammate_colors_show |
| 1800ad8e0 | register cl_show_enemy_avatar_colors |
| 1800edb2c | register cl_teamid_overhead_colors_show |
| 1800e3c60 | register cl_color (default from the RandomInt import at 181aad4a8) |
| 1800e41d0 | register cl_hud_color |
| 180769bb0 | colour mode: game_type 0 and game_mode 6 / 1 / 3 / 4 / 2 |
| 1808a44a0 (local team, their team) | colour shown (below) |
| 1808a4490 | cl_teammate_colors_show == 2 (letters) |
| 18075d6d0 | engine max clients, clamped to 24 |
| 180889c80 (controller) | game rules and 180769bb0 ? +0x858 : -1 |
| 180889bd0 (out, index) | 0..4 the convar's colour, 5 0xff0000ff (red), other >= -1 0, below -1 0xffc8c8c8 |
| 180eb4d30 (_, kind, index) | kind 0: "B" "G" "Y" "O" "P"; kind != 0 other strings (181cdf34c ...) |
| 180faf660 | GameStateAPI.GetPlayerColor(xuid) (bound at 180fd3f4d) |
| 180d568d0 | state test (== 3: "") |
| 180eb3e80 | voice popup name |
| 180ea9f50 | chat line segments (codes 1..16) |
| 180ecc1f0 | team counter avatar |
| 180eb8050 | finds the team counter's .colorize-teammate-color children |
| 180ed28e0 | overhead id (teamid.md) |
| 180e92db0 | HUD root think: class group "teammatecolor" |
| 180ec4140 | radar icon place and turn (no colour) |
| 180ed3220 | radar icon colour |
| 18089c9e0 | spectator test |
| 1808dda40 | C_PlayerPing vtable slot 113: the icon particle |
| 18075cfa0 | the pinger's controller |
| 1808a30e0 | hidden (sanitized) name -> the colour's name (table 182220610) |
| 180e885f0 | death notice: never reads the colour |

## Fields

| Offset | Field |
|---|---|
| controller +0x828 (client +0x858) | m_iCompTeammateColor (int, -1 none) |
| controller +0x82c | m_bEverPlayedOnTeam |
| controller +0x82d (byte) | been through the assignment |
| controller +0x830 | preferred colour, read once from cl_color |
| controller +0x344 | team |
| controller +0x860 / +0x864 / +0x868 (byte) | m_iCompetitiveRanking / m_iCompetitiveWins / m_iCompetitiveRankType |
| controller +0x86c / +0x870 / +0x874 (client +0x8ac / +0x8b0 / +0x8b4) | m_iCompetitiveRankingPredicted_Win / _Loss / _Tie |
| controller +0x940 | m_iMVPs |
| controller +0x944 | think counter |
| controller +0x948 / +0x808 | ping smoothing (every 10th call) |
| pawn +0x514 | 0 or 3 for the bot test |
| pawn +0x1508 / +0x1500 | bot brain on / its CCSBot |
| latch obj +0x11 / +0x12 | team 2 / team 3 full flag |
| GC list 1821195c0 / 1821195c8 | count / entries; entry +0x38 account |
| entry +0x3c / +0x40 / +0x48 / +0x58 / +0x5c / +0x60 | -> +0x860 / +0x864 / +0x868 (byte) / +0x86c / +0x870 / +0x874 |
| 1821195a8 | controller list walked by slot 89 |
| radar icon +0x14c | 0.5 s timer |
| radar icon CT +0x60 / +0x68 / +0x70, T +0x80 / +0x88 / +0x90 | OnMap / OffMap / Death images; T also +0x160 > 0 |
| team counter list +0x34 / +0x32 | washed panel list / count; param +0x27 letters flag |
| GetPlayerColor hex table 18224d758 | written into its +0x10 |

## Constants

| Value | What |
|---|---|
| cl_teammate_color_1..5 | flags 0xa; 0xfff5ce88 (136, 206, 245) blue, 0xff809e00 (0, 158, 128) green, 0xff41e4f1 (241, 228, 65) yellow, 0xff2a80e6 (230, 128, 42) orange, 0xff962cbd (189, 44, 150) purple; handles 18252e1c8 / 18252e1d8 / 18252e1e8 / 18252e1f8 / 18252e208 |
| cl_teammate_colors_show 1 | int, flags 0x80088, "In competitive, 1 = show teammates as separate colors in the radar, scoreboard, etc., 2 = show colors and letters" (18252e218) |
| cl_show_enemy_avatar_colors 1 | bool (18252e228) |
| cl_teamid_overhead_colors_show 1 | bool, flags 0x80080, "Show team overhead id in teammate color" (182579058) |
| cl_color | int 0..4, default RandomInt(0, 4), flags 0x280 (archive, userinfo), "Preferred teammate color" |
| cl_hud_color 0 | int, flags 0x80088 |
| 182173828 | the latch object |
| 1821ba1c0 | game rules |
| 1821ba010 vfn 0x1a8 | engine client convar read (slot, "cl_color") |
| 0x99999999 | imul for c % 5 (signed) |
| 11 | max clients must be < 11 |
| 4 | more than 4 assigned controllers latches "full" |
| CSGO_Competitive_Dot "●", _Y "Ⓨ", _P "Ⓟ", _G "Ⓖ", _B "Ⓑ", _O "Ⓞ" | strings |

## Assignment (180a9b940)

1. +0x82d = 1. No game rules or not the colour mode: colour -1 (180a8ce80), return. Team < 2: return.
2. `full = 180a761a0(182173828, team)`. Colour != -1 and not force: return.
3. +0x830 == -1: cl_color via the engine, V_atoi, 0 unless 0..4 unsigned (cmovbe at 180a9ba25), stored.
4. c = colour if >= 0, else +0x830. Loop: `c = c % 5`; look for another controller of the team with colour == c.
   None: assign c. A clash: not `full` -> return unchanged (180a9bc76, r12b 0); `full` -> c + 1, tries + 1 (r15d),
   r12b = 1; tries >= 5 -> assign -1.

180a761a0: team 2 reads obj+0x11, team 3 obj+0x12; set -> 1. Else counts the team's controllers with +0x82d != 0; more
than 4 -> sets the flag, returns 1; else 0. Nothing clears the flags.

## Controller think (180a9e720)

1. A pawn passing vfn 0xca8 with +0x514 0 or 3, vfn 0xc20 (FL_BOT), +0x1508 and +0x1500 set: colour -1, +0x82d = 1
   (a bot playing its own pawn).
2. At 180a9e8d8, connected with a pawn: 180a9b940(controller, 0) (such a bot re-picks from its preferred colour every
   think; a taken-over bot has its brain off and keeps its colour).
3. Ping smoothing; 180a9b940(controller, 0) again.
4. With 18093e410: the GC per-account list into +0x860..+0x874; no entry: +0x860 / +0x864 = 0.

Slot 89 (1801ad7a0): with the colour mode, every colour -1 (180a79750), 180a71cb0, then twice: each controller at
1821195a8 -> 180a9b940(controller, 1) and 180a79c60; 180a79790.

## Client display

- 1808a44a0 shown: cl_teammate_colors_show != 0, their team 2 or 3, max clients < 11, game rules and 180769bb0, and
  (cl_show_enemy_avatar_colors, same team, or local team 1).
- GetPlayerColor: "" when 180d568d0 == 3, no game rules, no local or their controller, or 1808a44a0 false; else
  "#RRGGBB" of 180889bd0(180889c80); a "#n" argument takes n as the index.
- Voice popup (180eb3e80): no colour: CT #a2c6ff, T #ffdf93, else #ba81f0; with one:
  `<font color=colour>dot </font><font color=team>name</font>`, team CT #729bdd, T #e0b756, else #ffffff; dot
  #CSGO_Competitive_Dot, or with letters _B / _G / _Y / _O / _P; " @ place" in #40ff40 for a living teammate.
- Chat (180ea9f50): a code 3 segment of a sender with a shown colour gets `<font color="#RRGGBB">dot </font>` before
  the team-coloured text.
- Team counter (180ecc1f0): not shown -> washed in #eabe54 (T) / #6f9ce6 (CT); shown -> colour % 5 on each,
  #PlayerColor visible, #PlayerLetter = 180eb4d30(_, 0, colour) with the letters flag. Its list: .colorize-teammate-color
  children, AvatarLargeSnippet's .AvatarL_BG and #PlayerColor (180eb8050); AvatarL_BG shows only on .Avatar__SpectateTarget.
- Overhead id (180ed28e0): arrow [11] and chat icon [12] washed, the name [4] too with cl_teamid_overhead_colors_show.
- HUD root (180e92db0): "teammatecolor" = hud-teammatecolor--blue / green / yellow / orange / purple for the observed
  player; read by csgostyles.vcss only with csgo-hud__color-12 (cl_hud_color; .csgo-hud__color-N, @define
  color-hud-1..11, color-player-*).
- Radar (180ed3220): every 0.5 s, icon kinds 9 (CT) / 0xd (T) with 1808a44a0(controller +999, team): #PlayerLetter shown
  with 1808a4490; a player of your side with a colour has the OnMap / OffMap / Death images washed, letter
  180eb4d30(team counter, 0, colour); a spectator sees the team counter slot number (max clients < 11).
  hudradar.vxml PlayerIconPackage, .PI_Text: Stratum2 medium 10 px black.
- Ping (1808dda40) CP1: without the colour mode the pinger's team CT (181, 212, 238) / T (234, 209, 138); with it
  180889bd0(180889c80(...), 3 with none) as bytes (no colour: black); CP2 (1, 1, 1). cl_teammate_colors_show not read.
- Kill feed: no teammate colours.

Panorama: teamcolor.vts (index -1 or out of range "100,100,100"); scoreboard.vts 'avatar' (#player-color washed by the
'color' stat, hidden for ""); csgostyles.vcss .avatar-team-color (100 %, 3px white border; .sb-main 1.5px);
hudteamcounter.vcss .AvatarL__PlayerLetter (x 5, y 3, 14 px white, shadow), `.dead .avatar-team-color,
.dead .AvatarL__PlayerLetter { collapse }`; teamintromenu.vts (name washed by GetPlayerColor).

## Match stakes

match_stakes.vts (StartTeamIntro / EndTeamIntro), Premier rank type only: GetPlayerPremierRankStatsObject's score and
predictedRankingIfWin / IfLoss (+0x860, +0x86c / +0x870), delta "prediction - score" ("+0" / "-0" for none),
.no-rating for a score of 0.

## Unread

- 180c88670's second filter field (1): taken as "every controller of the team".
