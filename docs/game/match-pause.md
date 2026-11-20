# The halftime, tactical timeouts and the surrender vote (server_20261105.dll, pak01 2026-11-16)

Read with tools/re/game/cvardefs.py (registrations), xref.py / fieldwrites.py / callers.py / fnat.py, rtti.py + vtdump.py
(the vote issues' vtables), schema.py (field offsets) and ReVa's decompiler; the panels' scripts and strings from pak01
(scripts/context_menus/context_menu_vote.ts, resource/csgo_english.txt). Ported in server/cs2web/modes/team/comp-pause.js,
match-votes.js and client/hud/match-pause.js; tests comp-pause-test.mjs, match-votes-test.mjs. overtime.md has the
halftime's place in the match (IsLastRoundBeforeHalftime, RestartRound's halftime branch).

## Convars (int unless noted)

| Convar | Default | Object | Help |
|---|---|---|---|
| mp_halftime_duration (float, 0..300) | 15 | 0x182119978 | Target number of seconds that halftime lasts; shortened if team intros are active |
| mp_halftime_pausetimer | 0 | 0x1821198f8 | Set to 1 to stay in halftime indefinitely. Set to 0 to resume the timer. |
| mp_halftime_pausematch | 0 | 0x182119908 | Set to 1 to pause match after halftime countdown elapses. Match must be resumed by vote or admin. |
| mp_overtime_halftime_pausetimer | 0 | 0x182119918 | sets mp_halftime_pausetimer 1 before every half of overtime |
| mp_team_timeout_time | 60 | 0x182119258 | Duration of each timeout. |
| mp_team_timeout_max | 1 | 0x182119268 | Number of timeouts each team gets per match. |
| mp_team_timeout_ot_add_once / _add_each / _max | 0 / 0 / 1 | 0x182119278 / 288 / 298 | added at overtime |
| mp_technical_timeout_per_team | 0 | 0x1821192a8 | How many technical timeouts are there per team? |
| mp_technical_timeout_duration_s | 0 | 0x1821192b8 | How many seconds is a full technical timeout? |
| sv_vote_issue_surrrender_allowed (sic) | 1 | 0x181fa0800 | Can people hold votes to surrender? |
| sv_vote_issue_timeout_allowed | 1 | 0x181fa07d0 | Can people hold votes to time out? |
| sv_vote_issue_pause_match_allowed | 1 | 0x181fa07b0 | Can people hold votes to pause/unpause the match? |
| sv_vote_timer_duration (float) | 15 | 0x181fa0... (reg 180053b90) | a vote's length |
| sv_vote_creation_timer (float) | 120 | (reg 180052be0) | a player's wait between votes called |
| sv_vote_failure_timer (float) | 300 | (reg 180052d30) | a failed issue's wait before it can be called again |
| sv_vote_quorum_ratio (float, .01..1) | 0.501 | 0x181fa05c8 | The minimum ratio of players needed to vote on an issue to resolve it. |
| sv_vote_allow_spectators / sv_vote_count_spectator_votes / sv_vote_allow_in_warmup | 0 / 0 / 0 | 0x181fa05d8 / e8 / f8 | |
| mp_freezetime (0..60) | 6 | 0x182119ec8 | how many seconds to keep players frozen when the round starts |
| sv_auto_full_alltalk_during_warmup_half_end | 1 | 0x182119de8 | full all talk in warmup, at halftime and at the match's end |

## Gamerules fields (schema)

CCSGameRules: m_bTerroristTimeOutActive +0xe4, m_bCTTimeOutActive +0xe5, m_flTerroristTimeOutRemaining +0xe8,
m_flCTTimeOutRemaining +0xec, m_nTerroristTimeOuts +0xf0, m_nCTTimeOuts +0xf4, m_bTechnicalTimeOut +0xf8,
m_bMatchWaitingForResume +0xf9, m_iFreezeTime +0xfc, the technical timeouts used +0x139c / +0x13a0, the game phase
+0x11c (4 halftime). CCSPlayerController: m_bAbandonAllowsSurrender +0x8ca, m_bAbandonOffersInstantSurrender +0x8cb,
m_bDisconnection1MinWarningPrinted +0x8cc, m_nDisconnectionTick +0x8d0. CTeam: m_bSurrendered +0x568.

## Tactical timeouts

- Gamerules init (1809058c0) and a full restart (RestartRound's +0xdc5 branch, 180958442..18095853b): each team's
  timeouts = mp_team_timeout_max, each remaining = mp_team_timeout_time, the technical counts 0, m_bTechnicalTimeOut 0.
  The halftime's team swap (18094e8a0) swaps every team-indexed timeout field (active, remaining, count, technical).
- **Start** (`timeout_terrorist_start` / `timeout_ct_start`, console commands 18096f510 → StartTerroristTimeOut
  180964c10 / CT 1809644b0; arg "technical" for a technical one): nothing if either team's timeout is already active;
  a tactical one needs the team's count >= 1, a technical one its used count < mp_technical_timeout_per_team. Then
  active = 1; remaining = mp_team_timeout_time (count - 1), or mp_technical_timeout_duration_s (used + 1);
  m_bTechnicalTimeOut set; HUD print 6 `#SFUI_Notice_Match_Will_Pause` (" The match is set to pause during freeze
  time") or `_Technical`; m_bMatchWaitingForResume 1 (log "Match pause is enabled - TimeOutTs").
- **Running** (the Think's freeze part, 180913f80 at 18091428d..1809143b5): while a team's timeout is active, the
  round's start (m_fRoundStartTime, the freeze's end) is set to now + m_iFreezeTime every frame, so the freeze never
  ends; the remaining time drops by the frame's interval (a technical one is cleared at once when nobody is missing:
  1809230a0); at <= 0, 180920930 ends it. So a timeout called mid-round waits for the next freeze time
  (`#SFUI_vote_passed_timeout` "A timeout vote has passed. It will begin next freeze time.") and the full freeze time
  follows it.
- A disconnect in queued matchmaking can start a technical one by itself (180921370: per team, with
  mp_technical_timeout_per_team > 0): not ported (its default is 0).
- Not read: 180920930's body (ending: active 0, m_bMatchWaitingForResume 0 assumed), the HUD's timeout banner
  (`SFUI_Notice_Alert_Timeout` "%s1 Timeout %s2"; client.dll not read): ours draws CS2's string with the team and the
  seconds left.

## The halftime

- The phase 4 (SetGamePhase 180961850) starts at the round end after IsLastRoundBeforeHalftime and at an overtime's
  start (overtime.md). mp_halftime_duration: the target length (the win panel stays, the scoreboard shown: client;
  `SFUI_Scoreboard_Halftime` "Halftime", `SFUI_Scoreboard_OvertimeHalftime` "Overtime Intermission",
  `SFUI_HalftimePrompt` "HALFTIME"). With mp_halftime_pausetimer the halftime lasts until it is set back to 0;
  entering phase 4 in an overtime with mp_overtime_halftime_pausetimer sets mp_halftime_pausetimer 1.
  mp_halftime_pausematch: the match pauses after the countdown (#SFUI_Notice_Match_Will_Pause).
- Not read: where the halftime's countdown is compared (the restart time); the team intro shortening. Ours: the
  next round starts mp_halftime_duration after the halftime round's end (in place of mp_round_restart_delay), held
  while mp_halftime_pausetimer is set.

## The vote issues (CBaseIssue vtables: CStartTimeOutIssue 0x1818c6b38, the surrender issue "CSurrender" 0x1818c6c78)

- Slot 0x58 (CanTeamCallVote, surrender 1802671c0): the server can; otherwise only in queued matchmaking
  (18093e410: the reservation's first character 'Q'), and only a team with a member whose m_bAbandonAllowsSurrender
  is set (the GC sets it when a teammate abandons: `SFUI_vote_failed_surrender_too_early` "You cannot surrender until a
  teammate abandons the match.").
- Slot 0x60 (CanCallVote, surrender 180266f50): the base checks (180266290), then in queued matchmaking not once the
  match is decided (+0xde8), not in the halftime or the match's end (phase 4 / 5), not on the last round before the
  halftime (reason 5, ISSUE_DISABLED), and not before a round has been played (reason 10, WAITINGFORPLAYERS); then
  IsEnabled (slot 0x30: sv_vote_issue_surrrender_allowed). The timeout's IsEnabled (180280900): a competitive game
  mode (18093de70: game_mode 1 / 2 / ...) and sv_vote_issue_timeout_allowed.
- Slot 0x90 (GetNumberOfVotesRequired, shared 1802789f0): n = the potential voters (slot 0xc0, 1802688b0; at least the
  count when it started, controller +0x4c4); in queued matchmaking in a competitive mode for an issue whose slot 0x68
  is false: gamerules +0xdf0; slot 0x80 true: 1; slot 0x78 true (unanimous): n; **a competitive game mode: ceil(n - 1)
  (at least 1)**; else ceil(n x sv_vote_quorum_ratio). Both issues have slot 0x68 true and 0x70..0x88 false.
- Slot 0xa8 (ExecuteCommand): the timeout's (18026f440) runs `timeout_terrorist_start;` / `timeout_ct_start;` for the
  caller's team. The surrender's (18026f4f0): in queued matchmaking, during the warmup or the halftime it prints 0x1f to
  the caller and does nothing; once decided (+0xde8) or at the match's end nothing; else the surrendering team's
  m_bSurrendered (18090c740 / 18090dc20 on its team), +0xde8 = 7 (T) / 8 (CT), and TerminateRound(0, 17
  TerroristsSurrender / 18 CTSurrender) (1809654b0): `#SFUI_Notice_Terrorists_Surrender` "Terrorists Surrender" /
  `#SFUI_Notice_CTs_Surrender` "CTs Surrender"; the match ends with the other team winning. Outside queued matchmaking
  it only terminates the round with that reason.
- Strings: `#SFUI_vote_surrender` "Surrender?", `#SFUI_otherteam_vote_surrender` " The other team is voting to
  surrender.", `#SFUI_vote_passed_surrender` "Surrendering...", `#SFUI_vote_start_timeout` "Call a timeout?",
  `#SFUI_otherteam_vote_timeout`, `#SFUI_vote_failed_timeouts_exhausted` "Your team has no timeouts left.",
  `#SFUI_vote_failed_timeout_active` "A timeout is already in progress.", `#SFUI_vote_failed_vote_in_progress`,
  `#SFUI_vote_failed_waitingforplayers` "Voting not allowed during warmup.", `#SFUI_vote_failed_vote_spam` / Panorama's
  "You called a vote recently and can not call another for {d:num_second} seconds.".
- The menu (context_menu_vote.ts GetCurrentVoteIssues): queued matchmaking and not a tournament: "Surrender"
  (`#SFUI_vote_surrender`); not a tournament and a competitive / scrimcomp5v5 / scrimcomp2v2 mode: "starttimeout"
  (`#SFUI_Vote_StartTimeout` "Call a Tactical Timeout"); not a tournament: "Kick" (`#SFUI_Vote_KickPlayer`). Each runs
  `callvote <issue>`.
- Ours: queued matchmaking = a Competitive queue match (matchmaker.js, not a custom lobby); a competitive game mode =
  every round mode outside Casual (Casual is CS2's 0/0). The abandon flag comes from seats.js (playerAbandoned).
  m_bAbandonOffersInstantSurrender (read in 180921370 only, its effect not traced) is not ported.
