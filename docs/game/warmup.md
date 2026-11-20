# Warmup period (CCSGameRules)

server_20261105, client_20261015. game/csgo/cfg (installed game); pak01 resource/csgo_english.txt, layout/hud/hudalerts.xml, styles/hud/hudalerts.vcss.

## Functions

| Address | Module | What |
|---|---|---|
| 0x180968600 | server | the warmup think (while m_bWarmupPeriod) |
| 1809669f0 | server | the rules' Think (calls it) |
| 18094ea70, 18094f530 | server | Arms Race rules (call it) |
| 18092b540 | server | the warmup's end |
| 180961b10 | server | set m_fWarmupPeriodStart (also rewrites the end) |
| 180de86d0 | server | current time |
| 1801f95a0 / 1801f95b0 | server | `a - float` / `a - b` |
| 18017e2d0 | server | compare (-1 / 0 / 1) |
| 18017dc70 | server | `a + float` |
| 180187770 | server | a float convar's value |
| 1801b4c90 | server | set mp_warmuptime |
| 1801a49f0 | server | set mp_warmup_pausetimer |
| 180965160 | server | ShouldPlayTeamIntro |
| 180923c50 | server | (rules, 0) at the end |
| 180a79790 | server | at the end |
| 0x180e8fea0 | client | the HUD alert |
| 180e8f0d0 | client | set the alert (string, priority) |
| 18076a1f0 | client | timer paused (the pause's vfn 0x100; its tail unread) |
| 180769ee0 | client | m_bIsQueuedMatchmaking |
| 18075d6d0 | client | players the match wants (min(24, a maximum) in one branch) |

## Fields

| Offset | Field |
|---|---|
| rules +0xd9 | m_bWarmupPeriod |
| rules +0xdc | m_fWarmupPeriodEnd (networked; written by the think) |
| rules +0xe0 | m_fWarmupPeriodStart |
| rules +0x10c | m_flRestartRoundTime |
| rules +0x110 | m_bGameRestart |
| rules +0xdc4 | m_bFirstConnected (0: end is +inf) |
| rules +0xdc5 | m_bCompleteReset |
| rules +0xea8 | m_fWarmupNextChatNoticeTime |
| rules +0x102c | m_flLastThinkTime |
| rules +0x134 / +0x138 | m_bIsQueuedMatchmaking / m_nQueuedMatchmakingMode |
| rules +0x10a0 | mode rules |
| controller +0x344 | m_iTeamNum |
| controller +0x514 | m_iConnected |
| controller +0x388 | flags (bit 0x100: fake client) |
| pawn +0xd40 | m_iPlayerState |
| client rules +0x41 / +0x44 / +0x9c | m_bWarmupPeriod / m_fWarmupPeriodEnd / m_bIsQueuedMatchmaking |
| client rules +0x78 | byte: no beep |
| client controller +0x3f4 bit 4 | not counted by the waiting test |

## Constants

Convar values at [object + 8] + 0x58.

| Convar | Object | Registered at | Default | Competitive / Wingman | Casual | Notes |
|---|---|---|---|---|---|---|
| mp_warmuptime | 0x1821198a8 | 1800a4460 | 30 (min 5) | 120 | 90 | "How long the warmup period lasts. Changing this value resets warmup." Arms Race / deathmatch 20 |
| mp_warmuptime_all_players_connected | 0x1821198b8 | ~1800a4530 (`xorps xmm2`) | 0 | 15 | not set | "Warmup time to use when all players have connected. 0 to disable." |
| mp_warmuptime_match_cancelled | 0x1821198c8 | 1800a45d0 | 5 | | | |
| mp_endwarmup_player_count | 0x1821198d8 | 18009ebb0 | 0 | | | "Number of players required to be connected to end warmup early. 0 to require maximum players for mode." |
| mp_warmup_pausetimer | 0x1821198e8 | 1800a4340 | 0 | | | gamemode_workshop.cfg 1 |
| sv_warmup_to_freezetime_delay | 0x182118f28 | 1800a7f80 | 4 (max 20) | | | "Delay between end of warmup and start of match." |
| mp_warmup_online_enabled | 0x182119720 | 1800a4290 | 1 | | | |
| mp_warmup_offline_enabled | 0x182119730 | 1800a4230 | 0 | | | gamemode_rush.cfg true |

| Value | What |
|---|---|
| 0x182119200 | convar passed to the game types' vfn 0x160 (mode's max players) |
| 0x18218bff8 vfn 0x100 | server paused |
| 0x1821ba010 vfn 0x110, bool 0x182119380 | the clock's "online" test |
| 0x182118fb0 | convar: > 0 sends a user message at the end (unread) |
| 6.0 (0x18179be74) | pause cutoff before the end |
| 5.0 (0x1817a4438) | over-test window |
| 1.0 (0x181780580) | restart delay with the team intro |
| 10.0 | chat notice interval |
| 0x1824bc538 / 0x1824bc578 | client mp_warmuptime / likely mp_warmup_pausetimer |

## The think (0x180968600)

1. **All connected.** T = mp_warmuptime_all_players_connected, only when T > 0. `need` = game types' vfn 0x160 (type, mode, 0x182119200), capped by mp_endwarmup_player_count when >= 1. Count controllers with a name, not a fake client, with a pawn, m_iTeamNum 2 or 3, pawn m_iPlayerState != 3. When count >= need and `end - T >= now` and mp_warmuptime > T: m_fWarmupPeriodStart = now, mp_warmuptime = T, chat print (type 3) to everyone: `#SFUI_Notice_All_Players_Connected` with V_FloatToString(T) ("All players have connected. Match will start in %s1 seconds").
2. **Pause.** Server paused or mp_warmup_pausetimer != 0, and `end - 6.0 >= now`: m_fWarmupPeriodStart += now - m_flLastThinkTime, m_fWarmupNextChatNoticeTime += the same. A pause in the last 6 s holds nothing.
3. **End** (also 18092b540): +inf while m_bFirstConnected is 0; else, when 0x1821ba010 vfn 0x110 or bool 0x182119380 or mp_warmup_offline_enabled, start + mp_warmuptime; else 0. Written to m_fWarmupPeriodEnd.
4. m_fWarmupNextChatNoticeTime before now: now + 10.0 (the notice isn't sent here).
5. **Over?** Count as in 1, also m_iConnected 0 or 3 and a team. count > 0 and `end - 5.0 < now`, or mp_warmup_online_enabled 0: go on; else return (an empty server never leaves warmup).
6. mp_warmup_pausetimer = 0. Mode rules' vfn 0x18 true: return. `end <= now`, first time (m_bCompleteReset and m_bGameRestart both 0): log "Warmup period ended", m_flRestartRoundTime = now + (ShouldPlayTeamIntro ? 1.0 : (float) sv_warmup_to_freezetime_delay), m_bCompleteReset = 1, m_bGameRestart = 1, 180923c50(rules, 0), 180a79790, notice time now + 10; 0x182118fb0 > 0: a user message. Then once now >= m_flRestartRoundTime with m_bWarmupPeriod set: event `warmup_end`, m_bWarmupPeriod = 0.

## HUD alert (client 0x180e8fea0)

- `seconds = (int)(m_fWarmupPeriodEnd + 0.5 - now)`; end +inf: (int) mp_warmuptime. Under 1: nothing.
- Dialog variable `time_remaining` = "%d:%02d" (minutes, seconds), empty when 18076a1f0 says paused.
- seconds < 6: `#CSGO_Notice_Alert_Warmup_Period_Ending` ("Warmup Ending {s:time_remaining}", priority 1) and, unless rules +0x78, sound `Alert.WarmupTimeoutBeep`.
- else not queued matchmaking: `#CSGO_Notice_Alert_Warmup_Period` ("Warmup {s:time_remaining}").
- else: count controllers with +0x3f4 bit 4 clear; fewer than 18075d6d0: `#CSGO_Notice_Alert_Waiting_For_Players` ("WAITING FOR PLAYERS {s:time_remaining}"), else the Warmup line.

## The panel (hudalerts.xml / hudalerts.vcss)

- `CSGOHudAlerts` (classes AlertHidden / AlertVisible / FlashAnim / HideFlash): two `.alert-bar-side` (the second right-aligned), `.alert-bar-glitch`, `.alert-bar-bg`, Label `#AlertText` (stratum-medium-tf).
- Panel: width `alert-width` (csgostyles 300 px), centred, y 120 px, radius 3, world-blur hudWorldBlur (gaussian(2,2,2)), white; hidden `scale3d(0, 1, 1)`; visible scale 1 and rgba(255,255,255,0): transform .25 s ease-in after .25 s, the white clearing in .15 s.
- `.alert-bar-side`: 2 px wide, full height, white (hud-colorize-wash, additive).
- `.alert-bar-bg`: bluedots_large at backgroundDotsSize (360 px), background-img-opacity .04; visible rgba(0,0,0,.5).
- `.alert-bar-glitch`: videos/digital_glitch.webm at .25, opacity 0 once visible.
- `#AlertText`: width 400 px, centred, padding 8 24, white, 18 px, text-shadow 1px 1px 1px 2 #000000d2; opacity 0 hidden.
- `.MatchStartAlert`: Stratum2 medium; `.MatchAlertTimer`: Stratum2 Bold Monodigit; `.ReplayAlert`: #c9c9c9.
- FlashAnim (3.7 s), HideFlash (1 s): opacity / wash-color keyframes.

## Strings

- SFUI_Notice_Match_Will_Start_Chat ">> Match will start when warmup has ended"
- SFUI_Notice_Match_Will_Start_Waiting_Chat ">> Waiting for all players to connect"
- SFUI_Notice_Warmup_Has_Ended ">> Warmup has ended" (the 10 s chat notice's by name; the sender unread)

## Unread

- Where m_bWarmupPeriod and m_bFirstConnected are set (Arms Race's start: armsrace.md 18094d9c0); GMR_BeginWarmupPeriod ("will last %.1fs", 0x1818cbd38); mp_warmup_start / mp_warmup_end.
- 0x1821ba010 vfn 0x110 and bool 0x182119380; the game types' vfn 0x160.
- The 10 s chat notice's sender; the user message behind 0x182118fb0.
- 18076a1f0's tail; 18075d6d0's other branch; which alerts use FlashAnim / HideFlash.
- mp_warmuptime_match_cancelled's use; deathmatch's and Arms Race's warmups (mp_warmuptime 20).
