# The scoreboard per game mode (CSGOScoreboard: layout/scoreboard.vxml, scripts/scoreboard.vts)

pak01 read 2026-11-20 with `lasers-bake --decompile <pak01> "panorama/(layout|styles|scripts)/scoreboard"` (plus
scripts/common/gamerules_constants.vts, styles/scoreboard.vcss), strings from resource/csgo_english.txt. Ported in
web/src/ui/scoreboard.js (the board), scoreboard-modes.js (the per-mode tables), scoreboard-row.js (a row),
scoreboard-timeline.js + .css (the timeline); the data from client/hud/board.js and, for the timeline, the server's
modes/team/round-history.js (the board's `tl`). No client.dll was read for this (ReVa was down): what the script
takes from GameStateAPI / MockAdapter is listed under "Not traced".

## The mode

`MockAdapter.GetGameModeInternalName(false)` is CS2's mode name; ours from gamemodes.js cs2GameMode's game_type /
game_mode (scoreboard-modes.js modeOf): 0/0 casual (ZE, the Casual queue), 0/1 competitive, 0/2 scrimcomp2v2
(Wingman: our 1v1 / 3v3), 1/2 deathmatch, 1/0 gungameprogressive (Arms Race).

| | template (_LoadScoreboardTemplate) | row (_GetPlayerRowForGameMode) | sort (_GetSortOrderForMode) |
|---|---|---|---|
| casual | snippet_scoreboard-classic--no-timeline | row--casual: money kills deaths assists mvps (set 0) / hsp kdr adr utilitydamage enemiesflashed (set 1), score; report | sortOrder_default |
| competitive, premier | ...--with-timeline--half-times | row--comp (class competitive): money kills deaths assists hsp / mvps utilitydamage enemiesflashed kdr adr, damage; report, commend | sortOrder_tmm |
| scrimcomp2v2 | ...--with-timeline--half-times | row--wingman: as row--comp, no class | sortOrder_default |
| deathmatch | --no-teams (mp_teammates_are_enemies), else classic no-timeline (mp_dm_teammode) | row--deathmatch: kills deaths assists kdr hsp damage score; report | sortOrder_dm (sortOrder_default with mp_dm_teammode) |
| gungameprogressive | --no-teams | row--armsrace: kills deaths kdr hsp taserkills knifekills gglevel; report | sortOrder_gg |

`IsQueuedMatchmakingMode_Team()` overrides the row (row--premier, NAME-PREMIER) and sort (tmm) for every mode, the
title ("#SFUI_GameModeCompetitiveTeams | map": "Premier") and the icon (competitive_teams.svg).

Sort orders (414-495, each stat 0: most first, -1: least first, in order): default dc score risc mvps kills assists
deaths(-1) leader teacher friendly rank idx(-1) damage avgrisc ...; tmm dc damage kills risc mvps assists deaths(-1)
leader teacher friendly rank idx(-1) score avgrisc; dm dc score kills kdr damage hsp idx(-1) assists deaths(-1); gg dc
gglevel knifekills taserkills kills kdr hsp idx(-1) assists deaths(-1). _SortPlayer compares with _lessthan (Number(),
NaN below everything) and returns at once while a row is hovered (_m_arrSortingPausedRefGetCounter). The highlighted
label (sortstat) is `Object.keys(_m_sortOrder)[1]`; a label's onactivate re-sorts: dc, that stat (only if the mode's
order has it), then the mode's order without it.

## Rows and stats

- _CreateLabelsForRow loads the row once and makes a label per stat (Button `id-sb-<stat>`, its text
  #Scoreboard_<stat>, its tooltip #Scoreboard_<stat>_tooltip when not empty); a data-set stat goes into
  `id-sb-labels-set-N` (`_m_dataSetGetCount` counts them; the cycle button loses `hidden` with the first set).
- _InitStatCell: the set container is moved after the first set cell; shading alternates per set.
- _UpdateAllPlayers (open, delayed 0.01 s) updates every player silently; _UpdateJob (Scoreboard_UpdateJob)
  updates one player per call, round robin, not silently. _GenericUpdateStat(Direct): the label's text only on a
  change, then `_Pulse` (sb-pulse-highlight: anim-pulse brightness 1 -> 3 at 5 % -> 1, 1 s ease-in-out). Ping is
  always silent; money hides its label below 0; mvps shows star + count from 1 and pulses both.
- 'gglevel' = floor(score / 2); 'kdr' = the match stat kdr / 100 outside overtime, kills / deaths (|| 1) in it,
  toFixed(2); match stats of -1 print "-".
- 'status' (dictPlayerStatusImage): 1 elimination (sb-player-status-dead), 2 bomb_c4, 3..6 dominated / nemesis, 7
  defuser, 8 / 9 team switch, 10..14 party stacks, 15 disconnect (sb-player-status-disconnected, dc 0, ping "DC").
- .sb-player-pulse-death has a rule but nothing in the script adds it.
- .muted rows (GetGameStat is_muted, the enemy team's mute, a comms penalty): cells washed #ff0000a0, the avatar's
  muted icon. (Ours: no per-player voice mute yet.)

## The timeline (Competitive, Wingman)

- _SupportsTimeline: maxrounds_this_period <= 30.
- _ResetTimeline (on a change of maxrounds_this_period, the side swap, the overtime): segments for
  first_round_this_period..last_round_this_period, split at midRound = first + ceil((last - first) / 2) - 1 with a
  divider when HasHalfTime(); a round's tick label every 5th round; the "#scoreboard_timeline_ot:f" label ("Overtime",
  "Overtime N") shown in overtime.
- _UpdateAllRounds: m_topScore / m_botScore start at (maxrounds + (overtime - 1) x maxrounds_overtime) / 2 in
  overtime, else 0. _UpdateRound(rnd): tick `hilite` up to rounds_played + 1; a future round: the clinch trophy
  (can_clinch, num_wins_to_clinch: top at rounds_played + need - m_topScore when <= the bottom's), past-clinch /
  clinch-round; a played round: when AreTeamsPlayingSwitchedSides() differs from ...InRound(rnd) top and bottom swap,
  top gets sb-team--CT, bottom sb-team--TERRORIST; rounddata[rnd].result "ct_win_<kind>" / "t_win_<kind>" ->
  dictRoundResultImage[win_<kind>] (elimination kill.svg, rescue, defuse defuser.svg, time timer.svg, bomb, win
  trophy.svg) on that side, --active, the tick washed the side's colour; the casualties: 5 dashes a side (2 in
  scrimcomp2v2), past players_alive_<side> `dead-casualty`; shown while the cursor is over the segments (or
  cl_scoreboard_survivors_always_on 1).
- _UpdateTeams: score_1h / score_2h / score_ot per team_name (sb_team_score_2 / _3 / _ot), the OT box shown only with
  score_ot.
- _UpdateRoundLossBonus: shown when mp_consecutive_loss_max > 0 and cash_team_loser_bonus_consecutive_rounds > 0;
  classes ..._CT1..4 / _TERRORIST1..4 for next_round_loss_bonus >= n; the tooltip
  (#Scoreboard_lossmoneybonus_tooltip) cash_team_loser_bonus + min(max(n, 0), mp_consecutive_loss_max) x the
  consecutive bonus.

## End of match (.eom-scoreboard)

Hidden: the cursor instruction, the music kit, money labels, the alive counts, the spectators, the website button,
block-UGC and mute buttons; the clinch hidden; the meta fitted; the button panel visible; no dead wash
(`:not(.eom-scoreboard)`). `.eom #players-table-*` caps the tables at 160 (ANY 400).

## Not traced (client.dll)

- GetScoreDataJSO's rounddata result names from the round's RoundEndReason (ours: comp.js's why taken as the obvious
  kind), score_1h / _2h in an overtime, next_round_loss_bonus (ours: comp.js's loss count).
- GetGameStat('status')'s rule (ours: dead; the C4 / a kit on your own team's rows or everyone's for an observer).
- IsQueuedMatchmakingMode_Team(), the Scoreboard_UpdateJob rate, the match stats' rounding (HS%, ADR, KDR).
- mp_consecutive_loss_max's registered default (4 here: no cfg sets it).
