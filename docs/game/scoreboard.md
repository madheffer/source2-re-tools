# The scoreboard per game mode (CSGOScoreboard)

pak01: panorama layout/scoreboard.vxml, scripts/scoreboard.vts, styles/scoreboard.vcss,
scripts/common/gamerules_constants.vts; strings resource/csgo_english.txt. No client.dll read.

## Modes

`MockAdapter.GetGameModeInternalName(false)` by game_type / game_mode: 0/0 casual, 0/1 competitive, 0/2 scrimcomp2v2
(Wingman), 1/2 deathmatch, 1/0 gungameprogressive (Arms Race).

| mode | template (_LoadScoreboardTemplate) | row (_GetPlayerRowForGameMode) | sort (_GetSortOrderForMode) |
|---|---|---|---|
| casual | snippet_scoreboard-classic--no-timeline | row--casual: money kills deaths assists mvps (set 0) / hsp kdr adr utilitydamage enemiesflashed (set 1), score; report | sortOrder_default |
| competitive, premier | ...--with-timeline--half-times | row--comp (class competitive): money kills deaths assists hsp / mvps utilitydamage enemiesflashed kdr adr, damage; report, commend | sortOrder_tmm |
| scrimcomp2v2 | ...--with-timeline--half-times | row--wingman: as row--comp, no class | sortOrder_default |
| deathmatch | --no-teams (mp_teammates_are_enemies), else classic no-timeline (mp_dm_teammode) | row--deathmatch: kills deaths assists kdr hsp damage score; report | sortOrder_dm (sortOrder_default with mp_dm_teammode) |
| gungameprogressive | --no-teams | row--armsrace: kills deaths kdr hsp taserkills knifekills gglevel; report | sortOrder_gg |

`IsQueuedMatchmakingMode_Team()` overrides for every mode: row (row--premier, NAME-PREMIER), sort (tmm), title
("#SFUI_GameModeCompetitiveTeams | map": "Premier"), icon (competitive_teams.svg).

## Sort orders (scoreboard.vts 414-495)

Each stat 0: most first, -1: least first, in order.

| order | stats |
|---|---|
| default | dc score risc mvps kills assists deaths(-1) leader teacher friendly rank idx(-1) damage avgrisc ... |
| tmm | dc damage kills risc mvps assists deaths(-1) leader teacher friendly rank idx(-1) score avgrisc |
| dm | dc score kills kdr damage hsp idx(-1) assists deaths(-1) |
| gg | dc gglevel knifekills taserkills kills kdr hsp idx(-1) assists deaths(-1) |

- _SortPlayer compares with _lessthan (Number(), NaN below everything); returns at once while a row is hovered
  (_m_arrSortingPausedRefGetCounter).
- Highlighted label (sortstat) = `Object.keys(_m_sortOrder)[1]`. A label's onactivate re-sorts: dc, that stat (only if
  the mode's order has it), then the mode's order without it.

## Rows and stats

- _CreateLabelsForRow: row loaded once, a label per stat (Button `id-sb-<stat>`, text #Scoreboard_<stat>, tooltip
  #Scoreboard_<stat>_tooltip when not empty); a data-set stat into `id-sb-labels-set-N` (`_m_dataSetGetCount`; the
  cycle button loses `hidden` with the first set).
- _InitStatCell: set container moved after the first set cell; shading alternates per set.
- _UpdateAllPlayers (on open, delayed 0.01 s): every player silently. _UpdateJob (Scoreboard_UpdateJob): one player
  per call, round robin, not silently.
- _GenericUpdateStat(Direct): text only on a change, then `_Pulse` (sb-pulse-highlight: anim-pulse brightness
  1 -> 3 at 5 % -> 1, 1 s ease-in-out). Ping always silent; money hides below 0; mvps shows star + count from 1,
  pulses both.
- 'gglevel' = `floor(score / 2)`; 'kdr' = match stat kdr / 100 outside overtime, `kills / (deaths || 1)` in it,
  toFixed(2); match stats of -1 print "-".
- 'status' (dictPlayerStatusImage): 1 elimination (sb-player-status-dead), 2 bomb_c4, 3..6 dominated / nemesis,
  7 defuser, 8 / 9 team switch, 10..14 party stacks, 15 disconnect (sb-player-status-disconnected, dc 0, ping "DC").
- .sb-player-pulse-death has a rule; nothing adds it.
- .muted rows (GetGameStat is_muted, enemy team's mute, comms penalty): cells washed #ff0000a0, the avatar's muted icon.

## Timeline (Competitive, Wingman)

- _SupportsTimeline: maxrounds_this_period <= 30.
- _ResetTimeline (on change of maxrounds_this_period, side swap, overtime): segments first_round_this_period ..
  last_round_this_period, split at `midRound = first + ceil((last - first) / 2) - 1`, a divider when HasHalfTime();
  a tick label every 5th round; "#scoreboard_timeline_ot:f" ("Overtime", "Overtime N") in overtime.
- _UpdateAllRounds: m_topScore / m_botScore start at `(maxrounds + (overtime - 1) x maxrounds_overtime) / 2` in
  overtime, else 0.
- _UpdateRound(rnd):
  - tick `hilite` up to rounds_played + 1;
  - future round: clinch trophy (can_clinch, num_wins_to_clinch: top at `rounds_played + need - m_topScore` when <=
    the bottom's), past-clinch / clinch-round;
  - played round: top / bottom swap when AreTeamsPlayingSwitchedSides() differs from ...InRound(rnd); top
    sb-team--CT, bottom sb-team--TERRORIST; rounddata[rnd].result "ct_win_<kind>" / "t_win_<kind>" ->
    dictRoundResultImage[win_<kind>] (elimination kill.svg, rescue, defuse defuser.svg, time timer.svg, bomb, win
    trophy.svg) on that side, --active, the tick washed the side's colour;
  - casualties: 5 dashes a side (2 in scrimcomp2v2), past players_alive_<side> `dead-casualty`; shown while the
    cursor is over the segments (or cl_scoreboard_survivors_always_on 1).
- _UpdateTeams: score_1h / score_2h / score_ot per team_name (sb_team_score_2 / _3 / _ot), OT box only with score_ot.
- _UpdateRoundLossBonus: shown when mp_consecutive_loss_max > 0 and cash_team_loser_bonus_consecutive_rounds > 0;
  classes ..._CT1..4 / _TERRORIST1..4 for next_round_loss_bonus >= n; tooltip (#Scoreboard_lossmoneybonus_tooltip)
  `cash_team_loser_bonus + min(max(n, 0), mp_consecutive_loss_max) x consecutive bonus`.

## End of match (.eom-scoreboard)

Hidden: cursor instruction, music kit, money labels, alive counts, spectators, website button, block-UGC and mute
buttons, the clinch; meta fitted; button panel visible; no dead wash (`:not(.eom-scoreboard)`). `.eom
#players-table-*` caps the tables at 160 (ANY 400).

## Unread (client.dll)

- GetScoreDataJSO's rounddata result names from RoundEndReason; score_1h / _2h in overtime; next_round_loss_bonus.
- GetGameStat('status')'s rule.
- IsQueuedMatchmakingMode_Team(), the Scoreboard_UpdateJob rate, match stats' rounding (HS%, ADR, KDR).
- mp_consecutive_loss_max's registered default (4 seen: no cfg sets it).
