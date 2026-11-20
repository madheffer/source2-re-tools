# The map's end: time limit, GoToIntermission, the end-of-match cue

server_20261105. Casual (game_type 0, game_mode 0). CS2Fixes: map_votes.cpp, votemanager.cpp, detours.cpp:889-897,
events.cpp:236-241. End-of-match screen: winpanel.md "End of match".

## Functions

| Address | Module | What |
|---|---|---|
| 1809288a0 | server | GetMapRemainingTime |
| 1809654b0 | server | TerminateRound (its end 1809666b0..18096682c) |
| 18094e5f0 | server | the round's end processing |
| 180957e50 | server | RestartRound: clears m_iRoundWinStatus at 18095a7ff (`mov [r13 + 0xa44], r14d`, r14d = 0; checked against the disassembly) |
| 1809669f0 | server | CCSGameRules Think (its game phase switch) |
| 180914b60 | server | end-of-match think (returns 1 while the intermission runs: DAT_1821170e5) |
| 180913da0 | server | kill limit check (mp_fraglimit) |
| 18090fe70 / 1809101e0 | server | phase 2 / 3 (the halves') checks |
| 18092cdf0 | server | GoToIntermission(rules, aborted) |
| 1801bdd00 | server | accolades (winpanel.md) |
| 18091acd0 | server | next-map vote's options |
| 180961850 | server | SetGamePhase(+0xf0c, 5) |
| 180928fc0 | server | the map cycle's next map |
| 180ca7f40 | server | ClientPrint |
| 1801caad0 | server | match stats (ids 0x117 / 0x119 / 0x11b) |
| 1803c5940 | server | flag FL_FROZEN (0x20) |
| 180de34d0, 18092db60, 180b1b450, 1802524e0 | server | GoToIntermission's middle / per-controller / per-pawn calls (unread) |
| 18096ac20 | server | music event ("WonRound") |
| 18092b5f0 | server | the winners |
| 180187770 | server | float cvar getter (on the handle) |

## Fields (CCSGameRules)

| Offset | Field |
|---|---|
| +0xd8 | m_bFreezePeriod (GoToIntermission sets it) |
| +0xd9 | m_bWarmupPeriod |
| +0x104 | match start time ("after %d min": `(curtime - it + 59) / 60`) |
| +0x10c | m_flRestartRoundTime |
| +0x114 | m_flGameStartTime (the time limit counts from it) |
| +0x118 | time left shown in the intermission: `(+0xd7c + D) - curtime` |
| +0x11c | game phase as the end-of-match vote reads it (5: match ended) |
| +0x148 | m_bGameRestart? (GoToIntermission clears it) |
| +0x954 / +0x958 | end-of-match item reveal's start / end (endmatch_cmm_start_reveal_items) |
| +0x95c | end-of-match drops flag (set at GoToIntermission, cleared once +0x958 passes) |
| +0xa44 | m_iRoundWinStatus (0 while a round is on; set by the round's end, cleared by RestartRound) |
| +0xd60 | end-of-match items count |
| +0xd7c | m_flIntermissionStartTime (0 outside it) |
| +0xdcc | next-map vote's state |
| +0xf0c, +0xf24 | game phase (+0xf24 read by the Think: 1 standard play, 2 / 3 the halves, 4 halftime, 5 match ended) |
| +0xf18, +0xf20 | CT and T scores (shorts) |
| +0x1024 | win panel time: once curtime passes it in phase 5, cs_win_panel_match fires and it goes to 0 |
| +0x1028 | the Think's every-2-s timer |

## Constants

Cvar handles (value `*(handle + 8) + 0x58`, or 180187770 on the handle; names from the `lea rdx, name` beside each
handle's `lea rcx`):

| Handle | Cvar |
|---|---|
| 182119308 | mp_timelimit |
| 182119228 | mp_maxrounds |
| 182119a38 | mp_win_panel_display_time (3 in the casual cfgs) |
| 1821192e8 | mp_match_restart_delay (25) |
| 182119cb8 | mp_competitive_endofmatch_extra_time |
| 182119cc8 | mp_endmatch_votenextmap |
| 182119338 | nextlevel |
| 1821191e8 | nextmap_print_enabled |
| 182119188 | sv_matchend_drops_enabled |
| 182119998 | mp_match_can_clinch |
| 1821197b0 | mp_overtime_maxrounds |
| 1821191f8 | sv_skirmish_id |

| Value | What |
|---|---|
| 17 / 18 | surrender round end reasons |
| 0x23b0 | drops message |
| 1818cb248 | TerminateRound time-limit log line text (unread) |
| 0x58 bytes | the closing message (unless queued) |

## GetMapRemainingTime (1809288a0)

mp_timelimit <= 0: -1. Warmup (+0xd9): +inf. Else `max(0, mp_timelimit * 60 + m_flGameStartTime - curtime)` in floats,
that order (mulss 60.0, addss the start, subss curtime).

## TerminateRound's end

After 18094e5f0, unless the game mode object's vfn 0x18 says it ends rounds itself:
- Reason 17 / 18 outside queued matchmaking (sv_mmqueue_reservation not "Q..."): +0x1024 = curtime +
  mp_win_panel_display_time, GoToIntermission(false).
- mp_timelimit > 0, not warmup, the time exactly used up (`max(0, limit * 60 + start - curtime) == 0`), not queued: a log
  line, +0x1024 = curtime + mp_win_panel_display_time, GoToIntermission(false).

The map ends on the round's end itself, the round's win panel still up; RestartRound never runs.

## The Think's check (1809669f0)

When 180914b60 and 180913da0 don't stop it: phase 1 with mp_maxrounds < 1: GetMapRemainingTime() <= 0 and
m_iRoundWinStatus set -> +0x1024 = curtime + mp_win_panel_display_time, GoToIntermission(false). mp_maxrounds >= 1: the
rounds' and mp_match_can_clinch's tests. Phase 2 / 3: 18090fe70 / 1809101e0.

## GoToIntermission (18092cdf0)

1. "Going to intermission...".
2. Accolades (1801bdd00) for team 3 then team 2; Arms Race / deathmatch (game_type 1 with mode 0 / 2, or mode 2): one
   pass for everyone (-1).
3. The end-of-match player data user message.
4. Log "Game Over: <mode> <map> score CT:T after N min".
5. With sv_matchend_drops_enabled and not aborted: the drops message (0x23b0); +0x95c set.
6. 18091acd0; SetGamePhase 5; 180de34d0; +0x148 cleared; 18092db60; the cs_intermission event.
7. Next map: nextlevel if set and valid, else 180928fc0. With mp_endmatch_votenextmap, phase 5 and a map group of more
   than one map: +0xdcc set by its rules (6: no vote when +0x95c is clear).
8. Each controller 180b1b450; then each player: "#game_nextmap <map>" (HUD_PRINTTALK, 180ca7f40) when
   nextmap_print_enabled and there is a next map; match stats (1801caad0 0x117 / 0x119 / 0x11b).
9. Every live pawn flagged FL_FROZEN (1803c5940) and its 1802524e0; m_bFreezePeriod set; a closing message unless
   queued.

## The intermission's Think (phase 5)

- Once curtime passes +0x1024 (> 0): +0x1024 = 0, cs_win_panel_match (winpanel.md); with +0xd60 > 0
  endmatch_cmm_start_reveal_items, +0x954 / +0x958 set, +0xd7c moved on by the reveal's time.
- +0x118 = `(+0xd7c + D) - curtime`, D = mp_match_restart_delay, or queued: max(mp_match_restart_delay,
  mp_competitive_endofmatch_extra_time). Outside phase 4 / 5 +0x118 is kept 0.
- Once +0x10c + 3 s has passed, once: "WonRound" (18096ac20) to the winners (18092b5f0).
- 180914b60 returns 1 while the intermission runs, so nothing else of the Think (the round restart) runs.

## CS2Fixes

- GoToIntermission detoured (detours.cpp:889-897): refused once an intermission has started (IsIntermissionAllowed:
  "ending the map twice" breaks the vote), then the vote manager's last-round states (OnIntermission).
- cs_win_panel_match (events.cpp:236-241): idle checks paused, the map vote started (StartVote) unless one is on.
- StartVote's FinishVote timer: max(mp_endmatch_votenextleveltime, mp_match_restart_delay) - 3 s after the panel, so at
  +0xd7c + 25 with the defaults: when CS2's own vote closes (the 3 s is mp_win_panel_display_time); the map loads 1 s
  after it.

## Unread

- 180de34d0, 18092db60, 180b1b450, 1802524e0 only by name of what they touch.
- 1801caad0's stat ids 0x117 / 0x119 / 0x11b.
- The end-of-match user message's fields (the accolades' are in winpanel.md); the closing message (0x58 bytes).
- The log line's text at 1818cb248.
