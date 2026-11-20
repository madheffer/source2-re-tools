# The warmup period

CCSGameRules' warmup: its clock, the cut once everyone has connected, the pause, its end, and the HUD's alert. Read
2026-11-18 from server_20261105.dll and client_20261015.dll (ReVa + tools/re), the cfgs from the installed game
(game/csgo/cfg), the strings from pak01's resource/csgo_english.txt. Ported in server/cs2web/modes/team/warmup.js (the
think) and client/hud/warmup-alert.js (the alert); warmup-test.mjs / warmup-match-test.mjs check them.

## Fields (CCSGameRules, tools/re/game/schema.py on server_20261105.dll)

| Offset | Field | |
|---|---|---|
| +0xd9 | m_bWarmupPeriod | |
| +0xdc | m_fWarmupPeriodEnd | networked; written by the think |
| +0xe0 | m_fWarmupPeriodStart | setter 180961b10 (also rewrites the end) |
| +0x10c | m_flRestartRoundTime | |
| +0x110 | m_bGameRestart | |
| +0xdc4 | m_bFirstConnected | 0: the end is +inf |
| +0xdc5 | m_bCompleteReset | |
| +0xea8 | m_fWarmupNextChatNoticeTime | |
| +0x102c | m_flLastThinkTime | |
| +0x134 / +0x138 | m_bIsQueuedMatchmaking / m_nQueuedMatchmakingMode | |

Controller: m_iTeamNum +0x344, m_iConnected +0x514, flags +0x388 (bit 0x100: a fake client). Pawn: m_iPlayerState
+0xd40. Client (client_20261015.dll): m_bWarmupPeriod +0x41, m_fWarmupPeriodEnd +0x44, m_bIsQueuedMatchmaking +0x9c.

## Convars (server_20261105.dll; value at [object + 8] + 0x58)

| Convar | Object | Registered | Competitive / Wingman cfg | Casual cfg | |
|---|---|---|---|---|---|
| mp_warmuptime | 0x1821198a8 | 30 (min 5) | 120 | 90 | "How long the warmup period lasts. Changing this value resets warmup." Arms Race / deathmatch 20 |
| mp_warmuptime_all_players_connected | 0x1821198b8 | 0 | 15 | not set | "Warmup time to use when all players have connected. 0 to disable." |
| mp_warmuptime_match_cancelled | 0x1821198c8 | 5 | | | not run here (a cancelled match's server closes) |
| mp_endwarmup_player_count | 0x1821198d8 | 0 | | | "Number of players required to be connected to end warmup early. 0 to require maximum players for mode." |
| mp_warmup_pausetimer | 0x1821198e8 | 0 | | | gamemode_workshop.cfg 1 |
| sv_warmup_to_freezetime_delay | 0x182118f28 | 4 (max 20) | | | "Delay between end of warmup and start of match." |
| mp_warmup_online_enabled | 0x182119720 | 1 | | | |
| mp_warmup_offline_enabled | 0x182119730 | 0 | | | gamemode_rush.cfg true |

Registrations: mp_warmuptime 1800a4460, mp_warmuptime_all_players_connected ~1800a4530 (default: `xorps xmm2`),
mp_warmuptime_match_cancelled 1800a45d0, mp_endwarmup_player_count 18009ebb0, mp_warmup_pausetimer 1800a4340,
sv_warmup_to_freezetime_delay 1800a7f80, mp_warmup_online_enabled 1800a4290, mp_warmup_offline_enabled 1800a4230.

## The think: server.dll 0x180968600

Called while m_bWarmupPeriod from the rules' Think (1809669f0) and from Arms Race's rules (18094ea70, 18094f530).
Helpers: 18092b540 the warmup's end (below), 180de86d0 the current time, 1801f95a0 `a - float`, 1801f95b0 `a - b`,
18017e2d0 compare (-1 / 0 / 1), 18017dc70 `a + float`, 180187770 a float convar's value.

1. **All connected.** T = mp_warmuptime_all_players_connected; only when T > 0. `need` = the game types' vfn 0x160
   (type, mode, the convar at 0x182119200: the mode's maximum players; not read further), capped by
   mp_endwarmup_player_count when that is >= 1. Count the controllers with a name, not a fake client, with a pawn,
   m_iTeamNum 2 or 3, the pawn's m_iPlayerState != 3. When count >= need and `end - T >= now` and mp_warmuptime > T:
   m_fWarmupPeriodStart = now (180961b10), mp_warmuptime set to T (1801b4c90), and a chat print (type 3) to everyone:
   `#SFUI_Notice_All_Players_Connected` with V_FloatToString(T) ("All players have connected. Match will start in %s1
   seconds").
2. **The pause.** When the server is paused (vfn 0x100 of the global at 0x18218bff8) or mp_warmup_pausetimer != 0,
   and `end - 6.0 >= now` (0x18179be74): m_fWarmupPeriodStart += now - m_flLastThinkTime, and
   m_fWarmupNextChatNoticeTime += the same. So a pause set in the last 6 s holds nothing.
3. **The end** (also 18092b540): +inf while m_bFirstConnected is 0; else, when the vfn 0x110 of the global at
   0x1821ba010 is true or the bool at 0x182119380 or mp_warmup_offline_enabled is set, start + mp_warmuptime; else 0.
   Written to m_fWarmupPeriodEnd.
4. m_fWarmupNextChatNoticeTime: when it is before now, now + 10.0 (the notice itself isn't sent here).
5. **Over?** Count as in 1, also wanting m_iConnected 0 or 3 and a team. With count > 0 and `end - 5.0 < now`
   (0x1817a4438), or with mp_warmup_online_enabled 0: go on; otherwise return (the warmup stays: an empty server never
   leaves it).
6. mp_warmup_pausetimer = 0 (1801a49f0). The mode rules' (+0x10a0) vfn 0x18 true: return. `end <= now`: the first
   time (m_bCompleteReset and m_bGameRestart both 0): log "Warmup period ended", m_flRestartRoundTime = now +
   (ShouldPlayTeamIntro 180965160 ? 1.0 (0x181780580) : (float) sv_warmup_to_freezetime_delay), m_bCompleteReset = 1,
   m_bGameRestart = 1, 180923c50(rules, 0), 180a79790, the notice time now + 10; with the convar at 0x182118fb0 > 0 a
   user message (not read). Then once now >= m_flRestartRoundTime with m_bWarmupPeriod still set: the game event
   `warmup_end`, m_bWarmupPeriod = 0.

## The HUD alert: client.dll 0x180e8fea0 (client_20261015.dll)

seconds = (int)(m_fWarmupPeriodEnd + 0.5 - now); with the end +inf, (int) mp_warmuptime (0x1824bc538). Under 1:
nothing. The dialog variable `time_remaining` is "%d:%02d" (minutes, seconds), or empty when 18076a1f0 says the
timer is paused (the pause's vfn 0x100; its tail, likely mp_warmup_pausetimer 0x1824bc578, not read).

- seconds < 6: `#CSGO_Notice_Alert_Warmup_Period_Ending` ("Warmup Ending {s:time_remaining}", priority 1) and, unless
  the rules' byte +0x78 is set, the sound `Alert.WarmupTimeoutBeep`.
- else not m_bIsQueuedMatchmaking (180769ee0): `#CSGO_Notice_Alert_Warmup_Period` ("Warmup {s:time_remaining}").
- else: count the player controllers whose flag bit 4 of +0x3f4 is clear; fewer than 18075d6d0 (the players the match
  wants: min(24, a maximum) in one branch, not read further): `#CSGO_Notice_Alert_Waiting_For_Players` ("WAITING FOR
  PLAYERS {s:time_remaining}"), else the Warmup line.

The alert is set through 180e8f0d0 (the string, a priority).

### The panel: layout/hud/hudalerts.xml, styles/hud/hudalerts.vcss (pak01, `lasers-bake --settings-ref <out> --match hudalerts`)

`CSGOHudAlerts` (class AlertHidden / AlertVisible / FlashAnim / HideFlash) holds two `.alert-bar-side` (the second
right-aligned), `.alert-bar-glitch`, `.alert-bar-bg` and the Label `#AlertText` (stratum-medium-tf).
- The panel: width `alert-width` (csgostyles: 300 px), centred, y 120 px, radius 3, world-blur hudWorldBlur
  (gaussian(2,2,2)), white; hidden `scale3d(0, 1, 1)`; visible scale 1 and rgba(255,255,255,0): transform .25 s
  ease-in after .25 s, the white clearing in .15 s.
- `.alert-bar-side`: 2 px wide, full height, white (hud-colorize-wash, additive).
- `.alert-bar-bg`: bluedots_large at backgroundDotsSize (360 px), background-img-opacity .04; visible: rgba(0,0,0,.5).
- `.alert-bar-glitch`: videos/digital_glitch.webm at .25, opacity 0 once visible (not drawn here).
- `#AlertText`: width 400 px, centred, padding 8 24, white, 18 px, text-shadow 1px 1px 1px 2 #000000d2; opacity 0 hidden.
- `.MatchStartAlert`: Stratum2 medium; `.MatchAlertTimer`: Stratum2 Bold Monodigit; `.ReplayAlert`: #c9c9c9.
- FlashAnim (3.7 s) and HideFlash (1 s): opacity / wash-color keyframes (not drawn here).
Ported: client/hud/warmup-alert.css.

Other strings: SFUI_Notice_Match_Will_Start_Chat ">> Match will start when warmup has ended",
SFUI_Notice_Match_Will_Start_Waiting_Chat ">> Waiting for all players to connect", SFUI_Notice_Warmup_Has_Ended ">>
Warmup has ended" (the 10 s chat notice's, by their names: who prints them isn't read).

## Ours

- **The load gate** (the owner's, 2026-11-18; not CS2's): the page reports its loading bar (`loadpct`, 5 % steps:
  client/core/load-report.js; cleaned by the anti-cheat's loadPct). While a seat is under 50 % the think holds the
  clock exactly as step 2 does, for 180 s of holding at most (warmup.js LOAD_GATE). The alert then reads WAITING FOR
  PLAYERS with "The slowest player is N% loaded" under it.
- `need` is the match's human seats (g.tickets with a side), since bots fill seats here.
- A match with fewer than two human seats has no clock (comp.js checkLive: live 1 s after both sides have a player),
  standing in for CS2's offline test in step 3.
- The first human on a team sets m_bFirstConnected.

## Unread

- Where m_bWarmupPeriod and m_bFirstConnected are set (the warmup's start; docs/game/armsrace.md has Arms Race's
  18094d9c0), GMR_BeginWarmupPeriod ("will last %.1fs", 0x1818cbd38), mp_warmup_start / mp_warmup_end.
- The vfn 0x110 of 0x1821ba010 and the bool at 0x182119380 (the clock's "online" test); the game types' vfn 0x160.
- The 10 s chat notice's sender; the user message behind the convar at 0x182118fb0.
- 18076a1f0's tail; 18075d6d0's other branch; which alerts use FlashAnim / HideFlash.
- Deathmatch's and Arms Race's warmups (mp_warmuptime 20): the drop-in servers keep their stand-in.
