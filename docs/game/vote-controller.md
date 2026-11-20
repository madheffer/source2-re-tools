# Vote controller (callvote / vote, CVoteController, CBaseIssue)

server_20261105, client_20261105; panorama/scripts/context_menus/context_menu_vote.vjs_c (pak01 2026-11-18).
[match-pause.md](match-pause.md) has the surrender and timeout issues and GetNumberOfVotesRequired (1802789f0).

## Functions

| Address | Module | What |
|---|---|---|
| 1802905b0 | server | `callvote` command |
| 18028b210 | server | lists the issues ("---Vote commands---") |
| 1802690c0 | server | CreateVote |
| 18028db40 | server | TryCastVote(controller, slot, "OptionN") -> 0 or the vote command's failure |
| 180a7ca80 | server | `vote` command (prints the failures; code-to-string map unread) |
| 18028f970 | server | the think (0.1 s; 0.5 s with no issue) |
| 180286890 | server | reset: issue index -1, counts 0, +0x4c4 0, timers stopped (read in part) |
| 180287c80 | server | CallVoteFailed (unread) |
| 180288420 | server | networked count write (change notifier) |
| 180c844b0 | server | the players who can vote (VoteStart recipients) |
| 180a4b790 | server | tells the target |
| 180cbc9a0 | server | the voter |
| 180a79ab0 | server | controller's team |
| 180a4bed0 | server | voter stats (vote_type, option, target's slot), via pawn +0xe48 |
| 180a884b0 | server | slot 0x88's caller test |
| 1802688b0 | server | potential votes |
| 180266290 | server | base CanCallVote(issue, slot, name, details, &reason, &time) |
| 180285170 | server | base OnVoteFailed |
| 18091ba50 | server | gamerules setup: the issues (block 18091ca3c..18091ce98) |
| 180ff2430 / 180262640 | server | `new` / issue constructor (name, controller) |
| 18093de70 | server | competitive game mode |
| 18093e410 | server | queued matchmaking |
| 18093ec40 | server | warmup |
| 18093d960 / 18093d7e0 | server | match point |
| 18093d8d0 | server | (with 18093d960) kick refused |
| 18093d9e0 | server | match paused |
| 18093df90 | server | (ChangeLevel's minute test gate) |
| 18092a140 | server | match minutes |
| 1809136e0 | server | gamerules change level (reads nextlevel) |
| 18095fe40 | server | (gamerules, SteamID, 1, 0): called by the kick when sv_vote_kick_ban_duration > 0 (unread) |
| 1802bb5f0 | server | queued matchmaking: the kicked player's team |
| 180b56340 | server | SteamID |
| 1813aa290 | server | entity slot |
| 1816b6d80 | server | target component (+0x8c8) |

## Fields

Controllers: DAT_181fa0a80 (every team), DAT_181fa0a88, DAT_181fa0a90 (the team ones). CVoteController vtable
0x1817a18a8; CBaseIssue 0x1817a1798.

| Offset | Field |
|---|---|
| ctrl +0x4a8 | active issue's index in +0x630 (-1 none) |
| ctrl +0x4ac | the vote's team (-1 everyone; the caller's when slot 0x68) |
| ctrl +0x4b0 [5] | vote count per option (networked) |
| ctrl +0x4c4 | potential votes at the start (slot 0xc0) |
| ctrl +0x4c8 | yes / no (slot 0xd0) |
| ctrl +0x4d0 | vote CountdownTimer: duration +0x4d8, timestamp +0x4dc, timescale +0x4e0 |
| ctrl +0x4e8 | ExecuteCommand delay timer (timestamp +0x4f4) |
| ctrl +0x500 | reset timer, 5 s (timestamp +0x50c) |
| ctrl +0x518 [slot] | each player's option (5 none) |
| ctrl +0x618 | caller's slot (99 the server) |
| ctrl +0x61c | second slot CreateVote stores (TryCastVote compares a team-restricted voter's team with its controller's): TODO which player |
| ctrl +0x620 | winning option (multiple choice) |
| ctrl +0x628 / +0x630 | issue list count / array (issue +0x20 name) |
| ctrl +0x640 / +0x648 | options count / strings (slot 0xe0) |
| issue +0x8 / +0x10 | failure records count / array: name [0x40], details [0x40] at +0x40, time +0x80 |
| issue +0x60 | details (0x104 chars) |
| issue +0x164..+0x16c | yes, no, potential (slot 0xd8) |
| kick +0x180 / +0x184 | captured SteamID / its universe-type bits |
| player controller +0x344 | team |
| +0x388 bit 8 | set: no vote, not counted, not a kick target (movement.md reads controller +0x388 bit 8 as a bot) |
| +0x510 | set: can't vote |
| +0x514 | connection state (0 / 3 connected) |
| +0x5b0 bit 0 | can't be kicked (12) |
| +0x950 / +0x958 | last vote time (sv_vote_creation_timer) |
| gamerules +0xe4 / +0xe5 | T / CT timeout running |
| gamerules +0xf0 / +0xf4 | T / CT timeouts left |
| gamerules +0x120 | rounds played |
| gamerules +0xde8 | > 1: issue disabled in queued |
| gamerules slot 0x110 | (kick admin test) |

## Constants

Data pointer = handle + 8; `*(handle + 0x58)` the value.

| Handle | Cvar | Default / use |
|---|---|---|
| 0x181fa0578 | sv_vote_timer_duration | |
| 0x181fa0588 | sv_vote_command_delay | 2 (slot 0x48, 1802725e0) |
| 0x181fa05a8 | sv_vote_failure_timer | (slot 0xf0, 180274130) |
| 0x181fa05b8 | sv_vote_creation_timer | |
| 0x181fa05c8 | sv_vote_quorum_ratio | read at 05d0 |
| 0x181fa05d8 | sv_vote_allow_spectators | read at 05e0 |
| 0x181fa05e8 | sv_vote_count_spectator_votes | read at 05f0 |
| 0x181fa05f8 | sv_vote_allow_in_warmup | read at 0600 |
| 0x181fa0598 | sv_allow_votes | 1, read at 05a0 |
| 0x181fa0608 | sv_vote_disallow_kick_on_match_point | 0, read at 0610 (base CanCallVote's kick test) |
| 0x181fa06d0 | sv_vote_issue_kick_allowed | 1 (read at 06d8) |
| 0x181fa06e0 | sv_vote_kick_ban_duration | float 15 (minutes) |
| 0x181fa06c0 | sv_vote_issue_restart_game_allowed | 0 |
| 0x181fa0730 | sv_vote_issue_changelevel_allowed | 1 |
| 0x181fa0740 | sv_vote_to_changelevel_before_match_point | 0 |
| 0x181fa0750 | sv_vote_to_changelevel_rndmin | 0 |
| 0x181fa0760 | sv_vote_issue_nextlevel_allowed | 1 |
| 0x181fa0770 / 0x181fa0780 / 0x181fa0790 | sv_vote_issue_nextlevel_choicesmode / sv_vote_issue_nextlevel_allowextend / sv_vote_issue_nextlevel_prevent_change | 1 / 1 / 1 |
| 0x181fa07a0 | sv_vote_issue_scramble_teams_allowed | 0 |
| 0x181fa07f0 | sv_vote_issue_swap_teams_allowed | 0 |
| 0x182119338 | nextlevel | |

| Value | What |
|---|---|
| 45 s | vote timer in queued matchmaking |
| 5 s | reset timer |
| 0.1 / 0.5 s | think interval / with no issue |
| 99 | the server's slot |
| 157 | NETWORK_DISCONNECT_KICKED_VOTEDOFF (0x9d; network_connection.proto), "Voted off" (#Player_DisconnectReason_VotedOff) |
| 0xae335601 | hash of the match-info interface static (unnamed) |
| 0x17f4bb0 | file offset of vote_create_failed_t's name table |

### vote_create_failed_t

0 GENERIC, 1 TRANSITIONING_PLAYERS, 2 RATE_EXCEEDED, 3 YES_MUST_EXCEED_NO, 4 QUORUM_FAILURE, 5 ISSUE_DISABLED,
6 MAP_NOT_FOUND, 7 MAP_NAME_REQUIRED, 8 FAILED_RECENTLY, 9 TEAM_CANT_CALL, 10 WAITINGFORPLAYERS, 11 PLAYERNOTFOUND,
12 CANNOT_KICK_ADMIN, 13 SCRAMBLE_IN_PROGRESS, 14 SPECTATOR, 15 FAILED_RECENT_KICK, 16 FAILED_RECENT_CHANGEMAP,
17 FAILED_RECENT_SWAPTEAMS, 18 FAILED_RECENT_SCRAMBLETEAMS, 19 FAILED_RECENT_RESTART, 20 SWAP_IN_PROGRESS, 21 DISABLED,
22 NEXTLEVEL_SET, 23 TOO_EARLY_SURRENDER, 24 MATCH_PAUSED, 25 MATCH_NOT_PAUSED, 26 NOT_IN_WARMUP, 27 NOT_10_PLAYERS,
28 TIMEOUT_ACTIVE, 29 TIMEOUT_INACTIVE, 30 TIMEOUT_EXHAUSTED, 31 CANT_ROUND_END, 32 REMATCH, 33 CONTINUE, 34 MAX.
(sv_allow_votes off 21, a spectator 14, recent failures 15..19.)

### vote_type (slot 0xe8)

Kick 0, ChangeLevel 1, NextLevel 2, SwapTeams 3, ScrambleTeams 4, RestartGame 5, Surrender 6, PauseMatch 9,
UnpauseMatch 10, LoadBackup 11, ReadyForMatch 12, NotReadyForMatch 13, StartTimeOut 14 (the think's early fail tests 7:
no issue returns it).

## callvote 1802905b0

Needs the three controllers; a spectator refused (14) unless sv_vote_allow_spectators; no arguments: list; else the
issue by name in the global controller's list, then the team controller's; CreateVote.

## CreateVote 1802690c0

1. sv_allow_votes off: CallVoteFailed 21.
2. In progress (+0x4a8 != -1, or another controller busy for an issue needing > 1 vote):
   `#SFUI_vote_failed_vote_in_progress`.
3. Slot 0x60 CanCallVote(slot, name, details, &reason, &time) false: CallVoteFailed(slot 0xf8 of the reason) to the
   caller (the server: the "Vote failed" log).
4. sv_vote_creation_timer against +0x950 / +0x958: 2 with the seconds left.
5. +0x618 caller, +0x61c, slot 0x18 details, +0x4c8 = slot 0xd0, +0x4a8, +0x4ac; slot 0xe0's options to +0x640 (more
   than one: `vote_options` { count, option1..5 }).
6. VoteStart to 180c844b0's players: team, caller, vote_type (0xe8), disp_str (0x98), details_str (0x10), other_team_str
   (0xa0), is_yes_no_vote, entidx_target (0x100); log `Vote started "%s %s" from #%u %s`.
7. +0x4c4 = slot 0xc0; timer 45 s queued else sv_vote_timer_duration, over +0x4e0, at +0x4d8 / +0x4dc; slot 0x28; a
   yes / no vote casts the caller's "Option1"; the caller's last-vote time; 180a4b790.

## TryCastVote 18028db40

1. sv_allow_votes off: 1. slot past max clients: 7. No vote: 2. Command timer +0x4f4 running: 6.
2. Voter missing, +0x514 not 0 / 3, a spectator (+0x344 not 2 / 3) unless both spectator cvars, +0x388 bit 8, or +0x510:
   3.
3. Team issue (slot 0x68): +0x61c's controller missing or on another team: 3.
4. "Option" + atoi: n - 1 outside 0..4: 7. Already voted (+0x518 != 5): slot 0x70 false -> 4, else old count - 1.
5. Yes / no clamps to 1 (Option3..5 = No). Count + 1, +0x518 = option.
6. 180a4bed0; `vote_cast` { vote_option, team, userid }; log `Vote cast "%s %s" from #%u %s option%d`.
7. Slot 0x70 false: sum of counts >= +0x4c4 -> timer duration 0, timestamp now. Return 0.

The `vote` command's strings: "no vote in progress", "server disabled", "no active issue", "team restricted", "no
changing vote", "already voting", "voting closed", "system error" (TODO: which code each).

## The think 18028f970

1. No issue: next in 0.5 s.
2. Result: yes / no -> 0 (Yes) when Yes > No, else 1; else +0x620 = first option with the most votes. Not yes / no, or
   past the option count: "Trying to resolve a vote that is not a YES/NO vote..." and return (multiple choice never
   resolved here).
3. Timer started (timestamp > 0): required = slot 0x90. Yes >= required and slot 0x70 false: passed. Else vote_type 7
   with `(+0x4c4 - No) < required`: CallVoteFailed(slot 0xf8(3)) to everyone; else wait for the timer; at its end
   passed = Yes >= required, else CallVoteFailed(slot 0xf8(4)).
4. Yes / no: slot 0xd8(yes, no, potential). Timer stopped.
5. Passed: command timer = slot 0x48, reset timer 5 s, caller's +0x950 stopped, log `Vote succeeded "%s %s" from #%u
   %s`, VotePass to everyone: team, vote_type, disp_str (slot 0xb8), details_str (0x10). Failed: slot 0x20, reset 5 s.
6. Command timer end: slot 0xa8 ExecuteCommand. Reset timer end: 180286890. Next in 0.1 s.

## CBaseIssue slots (0x1817a1798; CKickIssue 0x1818c6030)

| Slot | Base | What | Kick |
|---|---|---|---|
| 0x10 | 180273910 | details string | 180273930 |
| 0x18 | 180289540 | SetIssueDetails (0x104 chars to +0x60) | |
| 0x20 | 180285170 | OnVoteFailed | 180285340 |
| 0x28 | 180285420 (nothing) | OnVoteStarted | 180285430 |
| 0x30 | false | IsEnabled | 1802807b0 |
| 0x38 / 0x40 | false / false | allowed in queued matchmaking / in warmup | 18093d550 true / false |
| 0x48 | sv_vote_command_delay | command delay | |
| 0x50 | false | | |
| 0x58 | true | CanTeamCallVote | |
| 0x60 | 180266290 | CanCallVote | 1802667c0 |
| 0x68 | false | team-restricted | 18093d370 true |
| 0x70 | false | a vote can change (and runs its full time) | |
| 0x78 / 0x80 / 0x88 | false | unanimous / one vote / the caller must be ... (180a884b0) | |
| 0x90 | 1802789f0 | votes required | |
| 0x98 / 0xa0 / 0xa8 / 0xb0 | pure | disp / other team's string / ExecuteCommand / ? | 180273bc0 / 180276ee0 / 18026e970 / 180281530 |
| 0xb8 | 1802788c0 | passed string | 1802788e0 |
| 0xc0 | 1802688b0 | potential votes | |
| 0xc8 | 2 | option count? | |
| 0xd0 | true | yes / no | |
| 0xd8 | 18028b0b0 | stores yes, no, potential | |
| 0xe0 | 180278780 | options | |
| 0xe8 | -1 | vote_type | 0 |
| 0xf0 | sv_vote_failure_timer | | |
| 0xf8 | the reason | failure reason | |
| 0x100 | -1 | target's entity index | 180278060 |

## Rules

- Potential votes 1802688b0: every controller connected (0 / 3), not +0x388 bit 8 or +0x510, on team 2 / 3 (any with
  both spectator cvars), on the vote's team (any when -1).
- Base CanCallVote 180266290:
  1. slot 99: yes. slot -1: no.
  2. sv_vote_allow_in_warmup off, warmup and slot 0x40 false: 10.
  3. Team can't call (slot 0x58) or, with slot 0x88, fails 180a884b0: 9.
  4. 5: queued and slot 0x38 false; queued and gamerules +0xde8 > 1; or (queued or cvar 0610) with 18093d8d0 and
     18093d960 for a "Kick".
  5. A failure record more than 1 s from its time: same name and details: ChangeLevel 16, Kick 15, else 8; same name,
     other details: SwapTeams 17, ScrambleTeams 18, RestartGame 19; empty or other name: 8. Seconds left to &time.
- Base OnVoteFailed 180285170: the record with the same details (+0x40, strncmp 0x3f) gets time = now + slot 0xf0;
  none: a new { name, details, time }.
- A record blocks only the same details (Kick 15, ChangeLevel 16, other 8) or, for SwapTeams / ScrambleTeams /
  RestartGame, any; an issue without details (StartTimeOut) is never blocked (only sv_vote_creation_timer).

## The issues a server has (18091ba50)

1. Kick on both team controllers (0x181fa0a90, 0x181fa0a88). Queued: a switch on the reservation's type ((DAT & 0xf) -
   4, 0..11, jump table 0x18091cf08) can skip it (TODO).
2. RestartGame, ChangeLevel, NextLevel (global 0x181fa0a80).
3. Competitive mode (18093de70): StartTimeOut on both team controllers.
4. Queued (18093e410) with the match-info interface: PauseMatch, UnpauseMatch, LoadBackup, ReadyForMatch,
   NotReadyForMatch (global).
5. Queued: Surrender on both team controllers.
6. ScrambleTeams, SwapTeams (global), always.

A casual server: Kick (per team), RestartGame, ChangeLevel, NextLevel, ScrambleTeams, SwapTeams; competitive adds
StartTimeOut; pause / ready / load-backup only on a queued tournament server.

## Kick (CKickIssue 0x1818c6030)

- IsEnabled 1802807b0: sv_vote_issue_kick_allowed, then an entity by handle DAT_181da3290 whose first field is null, or
  no such entity (TODO: which).
- CanCallVote 1802667c0: the base; IsEnabled false: 5; target = atoi(details up to a space); missing, +0x388 bit 8, not
  0 / 3 or +0x510: 11; target component (1816b6d80) +0x8c8: 9; no caller: yes; else caller on 2 / 3 and target on the
  caller's team or a spectator; target +0x5b0 bit 0, or (gamerules slot 0x110 false and target slot (1813aa290) 1): 12.
- disp 180273bc0 `#SFUI_vote_kick_player_other` (slot parsed, unused), other team 180276ee0
  `#SFUI_otherteam_vote_kick_player`, passed 1802788e0 `#SFUI_vote_passed_kick_player`, details 180273930 (target's
  name, 112 bytes: read in outline).
- OnVoteStarted 180285430: no controller / target, a spectator (team 1) or +0x388 bit 8: +0x180 = 0; else the target votes "Option2" through
  TryCastVote, SteamID (180b56340) captured at +0x180.
- OnVoteFailed 180285340: the base record, +0x180 = 0.
- ExecuteCommand 18026e970: no valid SteamID (+0x184): "Kick vote passed against '%s' but no SteamID was captured for
  the target, ignoring." Else the connected non-bot with that SteamID; ban duration > 0: 18095fe40(gamerules, SteamID,
  1, 0); kicked: engine slot 0x308(slot, 0, 0x9d); ban > 0: engine slot 0x310(SteamID, minutes, 1) (banid); queued:
  1802bb5f0.

## ChangeLevel (CChangeLevelIssue 0x1818c6260)

- IsEnabled 1802806f0: sv_vote_issue_changelevel_allowed; off with sv_vote_to_changelevel_before_match_point (default 0) on a match point (18093d960 / 18093d7e0);
  rndmin > 0: off once that many rounds (+0x120), or (not 18093df90) that many minutes (18092a140).
- CanCallVote 180266650: base; disabled 5; no map 7; a map group not a workshop collection (IGameTypes slot 0x130) and
  a map the engine lacks (slot 0x108): 6; then only a map in the map group (slot 0x1f8, exact): else no (no reason).
- Global, CanTeamCallVote, yes / no. disp `#SFUI_vote_changelevel`, other `#SFUI_otherteam_vote_unimplemented`, passed
  `#SFUI_vote_passed_changelevel`, details the map (+0x60).
- ExecuteCommand 18026e920: `nextlevel` = the map, then 1809136e0.

## NextLevel (CNextLevelIssue 0x1818c6370)

- IsEnabled 180280840: sv_vote_issue_nextlevel_allowed.
- CanCallVote 180266a30: base; sv_vote_issue_nextlevel_choicesmode and the server calling: yes with no details; disabled 5; no map 7; not found
  6; sv_vote_issue_nextlevel_prevent_change and `nextlevel` already a map that exists: 22; else the map must be in the group.
- No details and choicesmode: 5 options (slot 0xc8), not yes / no, `#SFUI_vote_nextlevel_choices`; else 2, yes / no,
  `#SFUI_vote_nextlevel`. Passed 180278900: `#SFUI_vote_passed_nextlevel_extend` when the details are the current map,
  else `#SFUI_vote_passed_nextlevel`.
- ExecuteCommand 18026edb0: "Extend current Map": mp_timelimit + 20 (> 0), mp_maxrounds + 2 (> 0), mp_winlimit + 2 (>
  0), server commands; else `nextlevel` = the map, then its index in the map group (18026ef7e.. unread).

## RestartGame / ScrambleTeams / SwapTeams (0x1818c5f20 / 0x1818c6490 / 0x1818c65a0)

CanCallVote: base, then IsEnabled (their cvars) else 5. ExecuteCommand `mp_restartgame 1;` / `mp_scrambleteams 2;` /
`mp_swapteams;`. Passed `#SFUI_vote_passed_restart_game` / `_scramble_teams` / `_swap_teams`; disp
`#SFUI_vote_restart_game` / `_scramble_teams` / `_swap_teams`. Global, yes / no.

## StartTimeOut / Surrender reasons (slot 0xf8)

- StartTimeOut (CStartTimeOutIssue 0x1818c6b38): CanTeamCallVote 180267170: gamerules, no timeout running (+0xe4 /
  +0xe5), timeouts left (+0xf0 / +0xf4) > 0. CanCallVote 180266ea0: base, then IsEnabled 180280900 else 5. Reason
  1802822c0: 9 -> 28 (a timeout running), 24 (18093d9e0), else 30 (30 with no gamerules).
- Surrender (0x1818c6c78): reason 180943510: 9 and 10 -> 23.

## Client reason table (client 0x181cdfa40)

`{ int reason, const char *token }`, 16 bytes; `#SFUI_vote_failed_` prefix left off unless shown: 0 `#SFUI_vote_failed`,
1 `_transition_vote`, 2 `#Panorama_vote_failed_vote_spam`, 3 `_yesno`, 4 `_quorum`, 5 `_disabled_issue`, 6
`_map_not_found`, 7 `_map_name_required`, 8 `#Panorama_vote_failed_recently`, 15 `_recent_kick`, 16 `_recent_changemap`,
17 `_recent_swapteams`, 18 `_recent_scrambleteams`, 19 `_recent_restart` (those five Panorama_), 9 `_team_cant_call`,
10 `_waitingforplayers`, 11 `#SFUI_vote_failed`, 12 `_cannot_kick_admin`, 13 `_scramble_in_prog`, 20
`_swap_in_prog`, 14 `_spectator`, 21 `_disabled`, 22 `_nextlevel_set`, 32 `_rematch`, 23 `_surrender_too_early`, 33
`_continue`, 24 `_paused`, 25 `_not_paused`, 26 `_not_in_warmup`, 27 `_not_10_players`, 28 `_timeout_active`, 29
`#SFUI_vote_failed`, 30 `_timeouts_exhausted`, 31 `_cant_round_end`, 34 `#SFUI_vote_failed`.

## The Call Vote menu (context_menu_vote.vjs_c)

GetCurrentVoteIssues: not queued: "Change Map..." (ChangeLevel, a popup of GetMapsInCurrentMapGroup's maps, display
names upper-cased); queued, not a tournament: "Surrender?"; queued tournament: on a team starttimeout and PauseMatch
(enabled out of warmup and pause), else Ready / NotReady in warmup, Unpause / Pause after, and LoadBackup; not a
tournament: "Call a Tactical Timeout" (starttimeout) in competitive / scrimcomp5v5 / scrimcomp2v2, then "Kick
Player..." (GetKickTargets' avatars, `callvote Kick <slot>`). Each item runs `callvote <issue> [param]`.

## Unread

- The pause / ready / load-backup issues' slots (queued tournament servers only).
- CallVoteFailed 180287c80, the vote command's code-to-string map 180a7ca80, +0x61c, the kick IsEnabled's entity, the
  queued Kick switch, NextLevel's execute tail.
- Client: the vote panel (show, passed / failed lines, hide), the Esc menu's Call Vote (context_menu_vote.ts:
  match-pause.md has its issue list).
