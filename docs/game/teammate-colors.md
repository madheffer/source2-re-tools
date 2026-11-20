# Competitive teammate colours and the match stakes

server_20261105.dll and client_20261015.dll (ReVa, tools/re: schema.py, fieldwrites.py, callers.py, vtowner.py,
cvardump.py / cvardefs.py, disasm.py, fnstrings.py), panorama from pak01 (`lasers-bake --decompile`:
scripts/common/teamcolor.vts, scoreboard.vts, teamintromenu.vts, match_stakes.vts, layout/hud/hudteamcounter.vxml,
styles/csgostyles.vcss, hudteamcounter.vcss, match_stakes.vcss), csgo_english.txt. Read 2026-11-16. Ported in
server/cs2web/modes/team/teammate-colors.js, src/cs2web/modes/team/teammate-colors.js, client/hud/teammate-color.js,
client/hud/match-stakes.js, server/cs2web/lobby/ratings.js matchStakes.

## Fields (schema.py)

| Field | server | client |
|---|---|---|
| CCSPlayerController::m_iCompTeammateColor (int, -1 none) | +0x828 | +0x858 |
| m_bEverPlayedOnTeam | +0x82c | |
| (unnamed) the controller has been through the assignment | +0x82d (byte) | |
| (unnamed) the preferred colour, read once from cl_color | +0x830 | |
| m_iCompetitiveRanking / m_iCompetitiveWins / m_iCompetitiveRankType (byte) | +0x860 / +0x864 / +0x868 | |
| m_iCompetitiveRankingPredicted_Win / _Loss / _Tie | +0x86c / +0x870 / +0x874 | +0x8ac / +0x8b0 / +0x8b4 |
| m_iMVPs | +0x940 | |

The constructor 180a6bdd0 sets +0x828 to -1 through its state-changed helper 180a8ce80 (the only writer besides the
three below); 180a79750(controller, value) is the plain setter.

## Server: the assignment

| Address | What |
|---|---|
| 18093de70 | the colour mode: g_pGameTypes (182125888) vfn 0x98 game_type == 0 and vfn 0xa0 game_mode in {6, 1, 3, 4, 2} (the same set as the client's 180769bb0) |
| 180a9b940 (controller, force) | +0x82d = 1. No game rules (1821ba1c0) or not the colour mode: the colour to -1 (180a8ce80) and return. Team (+0x344) < 2: return. full = 180a761a0(182173828, team). Colour != -1 and not force: return. +0x830 == -1: the engine's client convar (1821ba010 vfn 0x1a8(slot, "cl_color")), V_atoi, 0 unless it is 0..4 unsigned (cmovbe at 180a9ba25), stored. c = the colour if >= 0, else +0x830. Loop: c = c % 5 (imul 0x99999999 signed); walk the controllers of the team (180cbc9a0 / 180c86be0 / 180c88670 with { team, 1 }, slot order) for one other than this with colour == c; none: assign c (bVar3 false). A clash: not `full` -> return unchanged (180a9bc76, r12b 0); `full` -> c + 1, tries + 1 (r15d), r12b = 1; tries >= 5 -> assign -1 |
| 180a761a0 (obj, team) | the latch: team 2 reads obj+0x11, team 3 obj+0x12; set -> 1. Else counts the team's controllers with +0x82d != 0; more than 4 -> sets the flag, returns 1; else 0. Nothing here clears the flags |
| 180a9e720 | the controller's think (called from 180a9ab30, which counts +0x944, and 180a9a740): first, a pawn passing vfn 0xca8 with +0x514 0 or 3, vfn 0xc20 (FL_BOT) and pawn +0x1508 (the bot brain on) / +0x1500 (its CCSBot) set -> colour -1 and +0x82d = 1: a bot playing its own pawn; then (at 180a9e8d8, for a connected controller with a pawn) 180a9b940(controller, 0), so such a bot picks again from its preferred colour every think (ported: teammate-colors.js think; a taken-over bot has its brain off and keeps its colour); the ping smoothing (+0x948 / +0x808 every 10th call); then 180a9b940(controller, 0); then, with 18093e410, the GC's per-account list (1821195c0 count, 1821195c8 entries; entry +0x38 the account): +0x860 = +0x3c, +0x864 = +0x40, +0x868 = +0x48 (byte), +0x86c = +0x58, +0x870 = +0x5c, +0x874 = +0x60; no entry: +0x860 / +0x864 = 0 |
| 1801ad7a0 | CSource2Server vtable 181990f38 slot 89 (0x2c8): with the colour mode, every controller's colour to -1 (180a79750), 180a71cb0, then twice: each controller in the list at 1821195a8 -> 180a9b940(controller, 1) and 180a79c60; 180a79790. Its trigger (which engine call slot 89 is) is unread: not ported |

## Client: showing it

| Address | What |
|---|---|
| 1800adb9c .. 1800ade9c | cl_teammate_color_1..5 (flags 0xa), Color defaults 0xfff5ce88 (136, 206, 245), 0xff809e00 (0, 158, 128), 0xff41e4f1 (241, 228, 65), 0xff2a80e6 (230, 128, 42), 0xff962cbd (189, 44, 150): blue, green, yellow, orange, purple; handles 18252e1c8 / 1d8 / 1e8 / 1f8 / 208 |
| 1800adf50 | cl_teammate_colors_show int, default 1, flags 0x80088: "In competitive, 1 = show teammates as separate colors in the radar, scoreboard, etc., 2 = show colors and letters" (value via 18252e218) |
| 1800ad8e0 | cl_show_enemy_avatar_colors bool, default 1 (value via 18252e228) |
| 1800edb2c | cl_teamid_overhead_colors_show bool, default 1, flags 0x80080, "Show team overhead id in teammate color" (182579058) |
| 1800e3c60 | cl_color int 0..4, default RandomInt(0, 4) (the import at 181aad4a8 called at registration), flags 0x280 (archive, userinfo), "Preferred teammate color" |
| 180769bb0 | game_type 0 and game_mode 6 / 1 / 3 / 4 / 2 |
| 1808a44a0 (local team, their team) | shown: cl_teammate_colors_show != 0, their team 2 or 3, 18075d6d0 (the engine's max clients, clamped to 24) < 11, game rules and 180769bb0, and (cl_show_enemy_avatar_colors, the same team, or the local team 1) |
| 1808a4490 | cl_teammate_colors_show == 2 (letters) |
| 180889c80 (controller) | game rules and 180769bb0 ? +0x858 : -1 |
| 180889bd0 (out, index) | 0..4 the convar's colour, 5 0xff0000ff (red), any other >= -1 0, below -1 0xffc8c8c8 |
| 180eb4d30 (_, kind, index) | kind 0: "B" "G" "Y" "O" "P"; kind != 0: other strings (181cdf34c ...) |
| 180faf660 | GameStateAPI.GetPlayerColor(xuid) (bound at 180fd3f4d): "" when 180d568d0 == 3, no game rules, no local controller or theirs, or 1808a44a0 false; else "#RRGGBB" (hex digits from the table at 18224d758, written into its +0x10) of 180889bd0(180889c80); a "#n" argument takes n as the index |
| 180eb3e80 | the voice popup's name: without a colour CT #a2c6ff, T #ffdf93, else #ba81f0; with one: `<font color=colour>dot </font><font color=team>name</font>`, team CT #729bdd, T #e0b756, else #ffffff, the dot #CSGO_Competitive_Dot or with letters _B / _G / _Y / _O / _P; " @ place" in #40ff40 for a living teammate |
| 180ea9f50 | the chat line's segments (codes 1..16): a code 3 segment of a sender with a shown colour gets `<font color="#RRGGBB">dot </font>` before the team-coloured text (the same dot choice) |
| 180ecc1f0 | the team counter avatar: 1808a44a0 false -> its washed panel list (+0x34 count +0x32) in #eabe54 (T) / #6f9ce6 (CT); true -> the colour % 5 (180889bd0) on each, #PlayerColor visible, #PlayerLetter's text 180eb4d30(_, 0, colour) with the letters flag (param +0x27). Which panels the list holds is unread (the frame #PlayerColor is drawn here) |
| 180ed28e0 | the overhead id: with 1808a44a0 the arrow [11] and chat icon [12] washed in the colour, the name [4] too with cl_teamid_overhead_colors_show (docs/game/teamid.md) |
| 180e92db0 | the HUD root's think: the class group "teammatecolor" = hud-teammatecolor--blue / green / yellow / orange / purple for the observed player's colour, read by csgostyles.vcss only with csgo-hud__color-12 (cl_hud_color: client 1800e41d0, int, default 0, flags 0x80088; csgostyles.vcss's .csgo-hud__color-N rules, @define color-hud-1..11 and color-player-*). Ported: core/game.js (#hud data-hudcolor / data-tcolor), ui/hud.css, ui/hud-kills-fx.js, buy-menu.js |
| 180ec4140 | a radar icon's place and turn (no colour). The colour is 180ed3220: every 0.5 s (icon +0x14c), icon kinds 9 (CT) / 0xd (T) with 1808a44a0(controller +999, team): #PlayerLetter shown with 1808a4490 (cl_teammate_colors_show 2), and for a player of your side with a colour, the icon's CT (+0x60 / +0x68 / +0x70) or T (+0x80 / +0x88 / +0x90; T also +0x160 > 0) OnMap / OffMap / Death images washed in it (180889bd0), the letter 180eb4d30(team counter, 0, colour); a spectator (18089c9e0 or the engine's observer test) sees the team counter slot number instead (max clients < 11). hudradar.vxml PlayerIconPackage, .PI_Text: Stratum2 medium 10 px black. Ported: hud/radar-view.js, ui/radar.js |
| 1808dda40 | C_PlayerPing vtable slot 113: the icon particle (player_ping.vpcf) CP1: without the colour mode (180769bb0) the pinger's team, CT (181, 212, 238) / T (234, 209, 138); with it 180889bd0(180889c80(the pinger's controller via 18075cfa0), 3 with none) as bytes (a teammate without a colour: black); CP2 (1, 1, 1). cl_teammate_colors_show isn't read. Ported: client/fx/ping-view.js |
| 1808a30e0 | a hidden (sanitized) name becomes the colour's name (table 182220610) when the colour is shown: not ported |

Never read by the death notice (180e885f0): the kill feed has no teammate colours.

Strings: CSGO_Competitive_Dot "●", _Y "Ⓨ", _P "Ⓟ", _G "Ⓖ", _B "Ⓑ", _O "Ⓞ". Panorama: teamcolor.vts (index -1 or
out of range "100,100,100"), scoreboard.vts 'avatar' (#player-color washed by the 'color' stat, hidden for ""),
csgostyles.vcss .avatar-team-color (100 %, 3px white border; .sb-main 1.5px), hudteamcounter.vcss .AvatarL__PlayerLetter
(x 5, y 3, 14 px white, shadow) and `.dead .avatar-team-color, .dead .AvatarL__PlayerLetter { collapse }`,
teamintromenu.vts (the name washed by GetPlayerColor).

## Match stakes

match_stakes.vts (StartTeamIntro / EndTeamIntro) shows only for a Premier rank type: the local
GetPlayerPremierRankStatsObject's score and predictedRankingIfWin / IfLoss (the controller's +0x860 and +0x86c /
+0x870, the GC's list above), the delta "prediction - score" ("+0" / "-0" for none), .no-rating for a score of 0.
Our numbers: ratings.js matchStakes (the same Elo delta rateMatch applies, against the other side's average as the
sides stand; the shown rating 0 until 10 wins), the board's `rk` { r, n, w, l, t }.

## Not read

- (slot 89's trigger read: engine2's connectionless reservation packet 0x21, 1800a70c0 -> 1800aa9f0, state 2; ours the matchmaker seating a match: matchmaker.js seat)
- (the team counter's list: its .colorize-teammate-color children, hudteamcounter.vxml AvatarLargeSnippet's .AvatarL_BG and #PlayerColor (180eb8050 finds them by that class); AvatarL_BG shows only on .Avatar__SpectateTarget: ported, hud/teamcounter.js)
- 180c88670's second filter field (1): taken as "every controller of the team".
