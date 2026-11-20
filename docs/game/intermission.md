# The map's end: the time limit, GoToIntermission, the end-of-match screen's cue (server_20261105.dll)

How a casual server (game_type 0, game_mode 0: ZE's) ends a map, read 2026-11-18 for the end-of-match plan's R3
(ported: core/game.js goToIntermission / intermissionThink). The vote's own think is ported in
modes/team/endmatch-vote.js; the end-of-match screen in client/hud/end-of-match.js (docs/game/winpanel.md "End of
match"). CS2Fixes' map vote (map_votes.cpp) rides on this: cs2fixes/map-votes.js.

## Fields (CCSGameRules)

| Offset | What |
|---|---|
| +0xd8 | m_bFreezePeriod (GoToIntermission sets it) |
| +0xd9 | m_bWarmupPeriod |
| +0x104 | the match start time (GoToIntermission's "after %d min": (curtime - it + 59) / 60) |
| +0x114 | m_flGameStartTime (the time limit counts from it) |
| +0x118 | the time left the clients show in the intermission: (+0xd7c + the delay) - curtime |
| +0x11c | game phase as the end-of-match vote reads it (5: match ended) |
| +0x148 | m_bGameRestart? (GoToIntermission clears it) |
| +0x958 | the end-of-match item reveal's end (endmatch_cmm_start_reveal_items) |
| +0x95c | an end-of-match drops flag (set at GoToIntermission, cleared once +0x958 passes) |
| +0xa44 | m_iRoundWinStatus (0 while a round is on; set by the round's end, cleared by RestartRound 18095a7ff) |
| +0xd7c | m_flIntermissionStartTime (0 outside it) |
| +0xdcc | the next-map vote's state (endmatch-vote.js) |
| +0xf0c, +0xf24 | the game phase (+0xf24 read by the Think: 1 standard play, 2 / 3 the halves, 4 halftime, 5 match ended; SetGamePhase 180961850(+0xf0c, 5)) |
| +0xf18, +0xf20 | the CT and T scores (shorts) |
| +0x1024 | the win panel's time: once curtime passes it in phase 5, cs_win_panel_match fires and it goes to 0 |
| +0x1028 | the Think's every-2-s timer |

Cvars by their handles (the code reads `*(handle + 8) + 0x58`, or a float getter 180187770 on the handle): 182119308 mp_timelimit, 182119228 mp_maxrounds,
182119a38 mp_win_panel_display_time (3 in the casual cfgs), 1821192e8 mp_match_restart_delay (25),
182119cb8 mp_competitive_endofmatch_extra_time, 182119cc8 mp_endmatch_votenextmap, 182119338 nextlevel,
1821191e8 nextmap_print_enabled, 182119188 sv_matchend_drops_enabled, 182119998 mp_match_can_clinch,
1821197b0 mp_overtime_maxrounds, 1821191f8 sv_skirmish_id. (scratch cvarname.py: the `lea rdx, name` beside each
handle's `lea rcx`.)

## GetMapRemainingTime (1809288a0)

mp_timelimit <= 0: -1. In the warmup (+0xd9): +inf. Else max(0, mp_timelimit x 60 + m_flGameStartTime - curtime), in
floats, that sum order (mulss by 60.0, addss the start, subss curtime). Ours: core/game.js timeleft() (the same sum;
its max(0, .) where CS2 compares it).

## TerminateRound's end (1809654b0, 1809666b0..18096682c)

After the round's end processing (18094e5f0), unless the game mode object's vfn 0x18 says it ends rounds itself:
- reason 17 / 18 (a surrender) outside queued matchmaking (sv_mmqueue_reservation not "Q..."): +0x1024 = curtime +
  mp_win_panel_display_time, GoToIntermission(false);
- mp_timelimit > 0, not the warmup, the map's time exactly used up (max(0, limit x 60 + start - curtime) == 0) and not
  queued: a log line, +0x1024 = curtime + mp_win_panel_display_time, GoToIntermission(false).

So the map ends on the round's end itself, the round end's win panel still up; RestartRound never runs.

## The Think's own check (1809669f0, its game phase switch)

When the end-of-match think (180914b60) and the kill limit check (180913da0: mp_fraglimit) don't stop it: phase 1
(standard play) with mp_maxrounds < 1: GetMapRemainingTime() <= 0 and m_iRoundWinStatus set (the round is over) ->
+0x1024 = curtime + mp_win_panel_display_time, GoToIntermission(false). (mp_maxrounds >= 1: the rounds' and
mp_match_can_clinch's tests, the team modes' path.) Phase 2 / 3: 18090fe70 / 1809101e0 (the halves' checks).

## GoToIntermission (18092cdf0, (rules, aborted))

In order: "Going to intermission..."; the accolades (1801bdd00: docs/game/winpanel.md) for team 3 then team 2,
except Arms Race / deathmatch (game_type 1 with mode 0 / 2, or mode 2) where it is one pass for everyone (-1); the
end-of-match player data user message; the "Game Over: <mode> <map> score CT:T after N min" log line; with
sv_matchend_drops_enabled and not aborted the drops message (0x23b0); +0x95c set; 18091acd0 (the next-map vote's
options: endmatch-vote.js voteOptions); SetGamePhase 5; 180de34d0; +0x148 cleared; 18092db60; the cs_intermission
event; the next map: the nextlevel cvar if set and valid, else the map cycle's next (180928fc0); with
mp_endmatch_votenextmap and game phase 5 and a map group of more than one map, the vote's state (+0xdcc) set by its
rules (6: no vote when +0x95c is clear); every player's pawn: each controller 180b1b450; then for each player:
"#game_nextmap <map>" (HUD_PRINTTALK, ClientPrint 180ca7f40) when nextmap_print_enabled and there is a next map, and
their match stats for the end (1801caad0 0x117 / 0x119 / 0x11b); every live pawn flagged 0x20 (FL_FROZEN: 1803c5940)
and its 1802524e0; m_bFreezePeriod set; a closing message unless queued.

## The intermission's Think (1809669f0, game phase 5)

Each Think: once curtime passes +0x1024 (> 0): +0x1024 = 0, the cs_win_panel_match event (the clients' end-of-match
screen: docs/game/winpanel.md), and with end-of-match items (+0xd60 > 0) endmatch_cmm_start_reveal_items, +0x954 /
+0x958 (the reveal's start and end) and +0xd7c moved on by the reveal's time. +0x118 = (+0xd7c + D) - curtime, D =
mp_match_restart_delay, or in queued matchmaking max(mp_match_restart_delay, mp_competitive_endofmatch_extra_time). Once the
round end's +0x10c (m_flRestartRoundTime) + 3 s has passed, once: the "WonRound" music event (18096ac20) to the
winners (18092b5f0). Outside phase 4 / 5 +0x118 is kept 0. The end-of-match think (180914b60) returns 1 while the
intermission runs (DAT_1821170e5), so nothing else of the Think (the round restart) runs; its vote and the level
change: modes/team/endmatch-vote.js's header.

## What CS2Fixes does with it (map_votes.cpp, votemanager.cpp)

- GoToIntermission is detoured (detours.cpp:889-897): refused once an intermission has started (IsIntermissionAllowed:
  "ending the map twice" breaks the vote), then the vote manager's last-round states (OnIntermission).
- cs_win_panel_match (events.cpp:236-241): the idle checks paused, the map vote started (StartVote) unless one is on.
- StartVote's FinishVote timer: max(mp_endmatch_votenextleveltime, mp_match_restart_delay) - 3 s after the panel,
  so at +0xd7c + 25 with the defaults: when CS2's own vote closes (the "3 seconds off" is mp_win_panel_display_time);
  the map loads 1 s after it.

## Not read

- 180de34d0, 18092db60, 180b1b450, 1802524e0 (GoToIntermission's middle and its per-pawn calls) only by name of
  what they touch; 1801caad0's stat ids 0x117 / 0x119 / 0x11b; the end-of-match user message's fields (the accolades'
  are: docs/game/winpanel.md); the closing message (0x58 bytes) unless queued.
- The log line's text at 1818cb248 (TerminateRound's time-limit branch).
