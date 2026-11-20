# CS2's vote controller (server_20261105.dll), read 2026-11-18 (end-of-match plan R1; not ported yet)

The callvote / vote commands, CVoteController's create, cast, think and reset, and CBaseIssue's slots. match-pause.md
has the surrender and timeout issues and GetNumberOfVotesRequired (1802789f0); this file is the controller around them
and the other issues. Read with ReVa's decompiler, tools/re/game/vtdump.py, disasm.py, the scratch cvarname.py (a handle's
registration name) and the enum name table in .rdata.

## The controllers and their fields

Three controllers: DAT_181fa0a80 (every team), DAT_181fa0a88, DAT_181fa0a90 (the team ones). CVoteController's vtable
0x1817a18a8; CBaseIssue's 0x1817a1798.

| Field | What |
|---|---|
| +0x4a8 | the active issue's index in +0x630 (-1: none) |
| +0x4ac | the vote's team (-1: everyone; the caller's team when the issue's slot 0x68 is true) |
| +0x4b0 [5] | the vote count per option (networked: each write goes through 180288420 / the change notifier) |
| +0x4c4 | the potential votes when it started (slot 0xc0) |
| +0x4c8 | the issue is yes / no (slot 0xd0) |
| +0x4d0 | the vote's CountdownTimer: duration +0x4d8, timestamp +0x4dc, its timescale +0x4e0 |
| +0x4e8 | the ExecuteCommand delay's timer (timestamp +0x4f4) |
| +0x500 | the reset timer, 5 s (timestamp +0x50c) |
| +0x518 [slot] | each player's option (5: none) |
| +0x618 | the caller's slot (99: the server) |
| +0x61c | the second slot CreateVote stores (TryCastVote compares a team-restricted voter's team with its controller's): TODO which player, check CreateVote's store |
| +0x620 | the winning option (multiple-choice votes) |
| +0x628 / +0x630 | the issue list: count, array (each issue's name at issue +0x20) |
| +0x640 / +0x648 | the options: count, strings (slot 0xe0) |

## The failure reasons (vote_create_failed_t: the enum's name table in .rdata, file offset 0x17f4bb0)

0 GENERIC, 1 TRANSITIONING_PLAYERS, 2 RATE_EXCEEDED, 3 YES_MUST_EXCEED_NO, 4 QUORUM_FAILURE, 5 ISSUE_DISABLED,
6 MAP_NOT_FOUND, 7 MAP_NAME_REQUIRED, 8 FAILED_RECENTLY, 9 TEAM_CANT_CALL, 10 WAITINGFORPLAYERS, 11 PLAYERNOTFOUND,
12 CANNOT_KICK_ADMIN, 13 SCRAMBLE_IN_PROGRESS, 14 SPECTATOR, 15 FAILED_RECENT_KICK, 16 FAILED_RECENT_CHANGEMAP,
17 FAILED_RECENT_SWAPTEAMS, 18 FAILED_RECENT_SCRAMBLETEAMS, 19 FAILED_RECENT_RESTART, 20 SWAP_IN_PROGRESS, 21 DISABLED,
22 NEXTLEVEL_SET, 23 TOO_EARLY_SURRENDER, 24 MATCH_PAUSED, 25 MATCH_NOT_PAUSED, 26 NOT_IN_WARMUP, 27 NOT_10_PLAYERS,
28 TIMEOUT_ACTIVE, 29 TIMEOUT_INACTIVE, 30 TIMEOUT_EXHAUSTED, 31 CANT_ROUND_END, 32 REMATCH, 33 CONTINUE, 34 MAX.
The code agrees: sv_allow_votes off gives 21, a spectator 14, the recent-failure checks 15..19.

## Convars (by handle; the data pointer is the ref + 8, `*(handle + 0x58)` its value)

sv_vote_timer_duration 0x181fa0578, sv_vote_command_delay 0x181fa0588 (CBaseIssue slot 0x48, 1802725e0),
sv_vote_failure_timer 0x181fa05a8 (slot 0xf0, 180274130), sv_vote_creation_timer 0x181fa05b8, sv_vote_quorum_ratio
0x181fa05c8 (read at 05d0), sv_vote_allow_spectators 0x181fa05d8 (05e0), sv_vote_count_spectator_votes 0x181fa05e8
(05f0), sv_vote_allow_in_warmup 0x181fa05f8 (0600), sv_allow_votes 0x181fa0598 (1, read at 05a0),
sv_vote_disallow_kick_on_match_point 0x181fa0608 (0, read at 0610: the base CanCallVote's kick test),
sv_vote_issue_kick_allowed 0x181fa06d0 (1), sv_vote_kick_ban_duration 0x181fa06e0 (float 15),
sv_vote_issue_restart_game_allowed 0x181fa06c0 (0), sv_vote_issue_changelevel_allowed 0x181fa0730 (1),
sv_vote_to_changelevel_before_match_point 0x181fa0740 (0), sv_vote_to_changelevel_rndmin 0x181fa0750 (0),
sv_vote_issue_nextlevel_allowed 0x181fa0760 (1), _choicesmode 0x181fa0770 (1), _allowextend 0x181fa0780 (1),
_prevent_change 0x181fa0790 (1), sv_vote_issue_scramble_teams_allowed 0x181fa07a0 (0), _swap_teams_allowed
0x181fa07f0 (0), sv_vote_command_delay default 2. Defaults from tools/re/game/cvardefs.py / cvardump.py.

## callvote (1802905b0) and CreateVote (1802690c0)

- callvote: needs the three controllers; a spectator is refused (14) unless sv_vote_allow_spectators; no arguments
  lists the issues (18028b210, "---Vote commands---"); else the issue by name in the global controller's list, then
  the team controller's, and CreateVote.
- CreateVote: sv_allow_votes off: CallVoteFailed 21. A vote in progress (+0x4a8 != -1, or another controller busy for
  an issue whose votes required > 1): `#SFUI_vote_failed_vote_in_progress`. Slot 0x60 CanCallVote(slot, name,
  details, &reason, &time) false: CallVoteFailed(slot 0xf8 of the reason) to the caller (the server: the "Vote failed"
  log). The caller's sv_vote_creation_timer against their +0x950 / +0x958: 2 RATE_EXCEEDED with the seconds left.
- Then: +0x618 the caller, +0x61c, slot 0x18 the details, +0x4c8 = slot 0xd0, +0x4a8 the issue, +0x4ac the team;
  slot 0xe0's options to +0x640 (more than one fires `vote_options` { count, option1..5 }); VoteStart to the players
  who can vote (180c844b0): team, caller, vote_type (slot 0xe8), disp_str (0x98), details_str (0x10), other_team_str
  (0xa0), is_yes_no_vote, entidx_target (0x100); the log `Vote started "%s %s" from #%u %s`; +0x4c4 = slot 0xc0; the
  timer: 45 s in queued matchmaking, else sv_vote_timer_duration, over +0x4e0, at +0x4d8 / +0x4dc; slot 0x28
  OnVoteStarted; a yes / no vote casts the caller's "Option1"; the caller's last-vote time set; the target told
  (180a4b790).

## TryCastVote (18028db40: controller, slot, "OptionN") -> 0 or the vote command's failure

1. sv_allow_votes off: 1. slot past the max clients: 7. No vote (+0x4a8 == -1): 2. The command timer +0x4f4 running
   (the vote passed, its command pending): 6.
2. The voter (180cbc9a0) missing, its connection state (+0x514) neither 0 nor 3, a spectator (+0x344 not 2 / 3) unless
   both sv_vote_allow_spectators and sv_vote_count_spectator_votes, +0x388 bit 8, or +0x510 set: 3.
3. A team issue (slot 0x68): +0x61c's controller missing or on another team (180a79ab0) than the voter: 3.
4. "Option" then n (atoi): n - 1 outside 0..4: 7. A voter who has voted (+0x518 != 5): the issue's slot 0x70 (may
   change a vote; base false) false: 4, else their old option's count - 1.
5. A yes / no issue clamps the option to 1 (Option3..5 count as No). The count + 1 (networked), +0x518 = the option.
6. The voter's stats (their pawn's +0xe48, 180a4bed0(vote_type, option, target's slot)); `vote_cast` { vote_option,
   team, userid }; the log `Vote cast "%s %s" from #%u %s option%d`.
7. Slot 0x70 false: the counts summed; when the sum >= +0x4c4 the timer's duration becomes 0 and its timestamp now
   (the think ends the vote at its next run). Return 0.

The vote command (180a7ca80) prints the failures: "no vote in progress", "server disabled", "no active issue",
"team restricted", "no changing vote", "already voting", "voting closed", "system error" (TODO: which code each).

## The think (18028f970), every 0.1 s (0.5 s with no issue)

1. No issue: next think in 0.5 s.
2. The result: a yes / no issue: option 0 (Yes) when Yes > No, else 1 (`Yes <= No`); else +0x620 = the first option
   with the most votes. Not yes / no, or the result past the option count: the message "Trying to resolve a vote that
   is not a YES/NO vote..." and return (multiple-choice votes are never resolved here).
3. While the timer has started (timestamp > 0): required = slot 0x90. Yes >= required and slot 0x70 false: passed now.
   Else: vote_type 7 with (+0x4c4 - No) < required: CallVoteFailed(slot 0xf8(3)) to everyone, failed; else while the
   timer runs, wait; at its end passed = Yes >= required, else CallVoteFailed(slot 0xf8(4) QUORUM_FAILURE).
4. A yes / no issue: slot 0xd8 (yes, no, potential) (stores them at the issue's +0x164..+0x16c). The timer stopped.
5. Passed: the command timer = slot 0x48 (sv_vote_command_delay), the reset timer 5 s, the caller's +0x950 stopped,
   the log `Vote succeeded "%s %s" from #%u %s`, VotePass to everyone: team, vote_type, disp_str (slot 0xb8),
   details_str (0x10). Failed: slot 0x20 (OnVoteFailed, base 180285170: unread) and the reset timer 5 s.
6. The command timer's end: the issue's slot 0xa8 ExecuteCommand. The reset timer's end: 180286890 (the issue index
   -1, each option's count 0, +0x4c4 0, the timers stopped: read in part). Next think in 0.1 s.

## CBaseIssue's slots (0x1817a1798; the kick issue's 0x1818c6030 beside it)

| Slot | Base | What | Kick (CKickIssue) |
|---|---|---|---|
| 0x10 | 180273910 | details string | 180273930 |
| 0x18 | 180289540 | SetIssueDetails (copies 0x104 chars to +0x60) | |
| 0x20 | 180285170 | OnVoteFailed (unread) | 180285340 |
| 0x28 | 180285420 (nothing) | OnVoteStarted | 180285430 |
| 0x30 | false | IsEnabled | 1802807b0: cvar 06d8, then an entity (handle DAT_181da3290) whose first field is null, or no entity |
| 0x38 / 0x40 | false / false | allowed in queued matchmaking / in the warmup | 18093d550 true / false |
| 0x48 | sv_vote_command_delay | the command's delay | |
| 0x50 | false | | |
| 0x58 | true | CanTeamCallVote | |
| 0x60 | 180266290 | CanCallVote | 1802667c0 |
| 0x68 | false | team-restricted | 18093d370 true |
| 0x70 | false | a vote can be changed (and the vote runs its full time) | |
| 0x78 / 0x80 / 0x88 | false | unanimous / one vote / the caller must be ... (180a884b0) | |
| 0x90 | 1802789f0 | votes required (match-pause.md) | |
| 0x98 / 0xa0 / 0xa8 / 0xb0 | pure | disp string / other team's string / ExecuteCommand / ? | 180273bc0 / 180276ee0 / 18026e970 / 180281530 |
| 0xb8 | 1802788c0 (a string) | the passed string | 1802788e0 |
| 0xc0 | 1802688b0 | potential votes | |
| 0xc8 | 2 | (an option count?) | |
| 0xd0 | true | yes / no | |
| 0xd8 | 18028b0b0 | stores yes, no, potential | |
| 0xe0 | 180278780 | options | |
| 0xe8 | -1 | vote_type | 0 |
| 0xf0 | sv_vote_failure_timer | | |
| 0xf8 | the reason itself | the failure reason | |
| 0x100 | -1 | the target's entity index | 180278060 |

Potential votes (1802688b0): every controller connected (state 0 / 3), without +0x388 bit 8 or +0x510, on team 2 / 3
(any team when both spectator cvars are on), on the vote's team (or any when it is -1).

The base CanCallVote (180266290: issue, slot, name, details, &reason, &time):
- slot 99 (the server): yes. slot -1: no.
- sv_vote_allow_in_warmup off, the warmup (18093ec40) and slot 0x40 false: 10.
- A caller whose team can't call (slot 0x58) or, with slot 0x88, who fails 180a884b0: 9.
- 5 ISSUE_DISABLED: queued matchmaking and slot 0x38 false; queued and gamerules +0xde8 > 1; or (queued or cvar 0610)
  with 18093d8d0 and 18093d960 for a "Kick".
- The issue's failure records (+0x8 count, +0x10 array: name [0x40], details [0x40] at +0x40, the time +0x80): a
  record more than 1 s from its time: the same name and details: ChangeLevel 16, Kick 15, else 8; the same name, other
  details: SwapTeams 17, ScrambleTeams 18, RestartGame 19; an empty or other name: 8. The seconds left to &time.

The kick's CanCallVote (1802667c0): the base; IsEnabled false: 5; the target = atoi(details up to a space); missing,
+0x388 bit 8, not connected (0 / 3) or +0x510: 11; the target's component (1816b6d80) +0x8c8 set: 9; no caller (the
server): yes; else the caller on team 2 / 3 and the target on the caller's team or a spectator; the target with
+0x5b0 bit 0, or (gamerules slot 0x110 false and the target's slot (1813aa290) 1): 12 CANNOT_KICK_ADMIN.

The base OnVoteFailed (180285170): the issue's failure record with the same details (+0x40, strncmp 0x3f) gets its
time = now + slot 0xf0 (sv_vote_failure_timer); none: a new record { the issue's name, the details, that time }.

## Which issues a server has (the gamerules' setup, 18091ba50: the block at 18091ca3c..18091ce98)

Each `new` (180ff2430) then the issue's constructor (180262640: name, controller). In order:

1. Kick on both team controllers (0x181fa0a90, then 0x181fa0a88): a team vote. In queued matchmaking a switch on the
   reservation's type ((DAT & 0xf) - 4, 0..11, jump table at 0x18091cf08) can skip it (TODO: read the table).
2. RestartGame, ChangeLevel, NextLevel on the global controller (0x181fa0a80).
3. A competitive game mode (18093de70): StartTimeOut on both team controllers.
4. Queued matchmaking (18093e410) with a match-info interface (a static found by hash 0xae335601, unnamed):
   PauseMatch, UnpauseMatch, LoadBackup, ReadyForMatch, NotReadyForMatch (global).
5. Queued matchmaking: Surrender on both team controllers.
6. ScrambleTeams, SwapTeams (global), always.

So a casual server (ours: ZE, Casual, Deathmatch, custom lobbies) has Kick (per team), RestartGame, ChangeLevel,
NextLevel, ScrambleTeams, SwapTeams; a competitive-mode one adds StartTimeOut; pause / ready / load-backup votes exist
only on a queued tournament server.

vote_type (slot 0xe8): Kick 0, ChangeLevel 1, NextLevel 2, SwapTeams 3, ScrambleTeams 4, RestartGame 5, Surrender 6,
PauseMatch 9, UnpauseMatch 10, LoadBackup 11, ReadyForMatch 12, NotReadyForMatch 13, StartTimeOut 14 (the think's
early fail tests type 7, which no issue here returns).

## Kick (CKickIssue 0x1818c6030)

- IsEnabled (1802807b0): sv_vote_issue_kick_allowed (1), then an entity by handle DAT_181da3290 whose first field is
  null, or no such entity (TODO: which entity).
- CanCallVote (1802667c0): above. Team-restricted (slot 0x68 true), allowed in queued matchmaking (slot 0x38 true).
- disp_str (180273bc0) `#SFUI_vote_kick_player_other` (the details' slot parsed, unused), other_team_str (180276ee0)
  `#SFUI_otherteam_vote_kick_player`, passed (1802788e0) `#SFUI_vote_passed_kick_player`, details (180273930: the
  target's name from the slot in the details, 112 bytes: read in outline).
- OnVoteStarted (180285430): the target (the details' slot): no controller, no target, a spectator (team 1) or +0x388
  bit 8: the captured SteamID (+0x180) 0; else the target votes "Option2" (No) through TryCastVote, and their SteamID
  (180b56340) is captured at +0x180.
- OnVoteFailed (180285340): the base record, +0x180 = 0.
- ExecuteCommand (18026e970): no valid captured SteamID (+0x184's universe / type bits): the warning "Kick vote passed
  against '%s' but no SteamID was captured for the target, ignoring." Else the connected (0 / 3), non-bot player with
  that SteamID; sv_vote_kick_ban_duration (float minutes, 15, ref 0x181fa06e0) > 0: 18095fe40(gamerules, the SteamID,
  1, 0); the player (if found) kicked: engine slot 0x308(slot, 0, 0x9d: the disconnect reason); a ban > 0: engine slot
  0x310(SteamID, the minutes, 1) (banid); in queued matchmaking 1802bb5f0 for the kicked player's team.

## ChangeLevel (CChangeLevelIssue 0x1818c6260)

- IsEnabled (1802806f0): sv_vote_issue_changelevel_allowed (1); off with sv_vote_to_changelevel_before_match_point (0)
  on a match point (18093d960 / 18093d7e0); sv_vote_to_changelevel_rndmin (0) > 0: off once that many rounds
  (gamerules +0x120) are played, or (not 18093df90) once the match has run that many minutes (18092a140).
- CanCallVote (180266650): the base; IsEnabled false: 5; no map: 7 MAP_NAME_REQUIRED; a map group that isn't a
  workshop collection (IGameTypes slot 0x130) and a map the engine doesn't have (slot 0x108): 6 MAP_NOT_FOUND; then
  only a map in the server's map group (IGameTypes slot 0x1f8, an exact compare): else no (no reason set).
- Global (slot 0x68 false), CanTeamCallVote true, yes / no. disp `#SFUI_vote_changelevel`, other team
  `#SFUI_otherteam_vote_unimplemented`, passed `#SFUI_vote_passed_changelevel`, details the map (+0x60).
- ExecuteCommand (18026e920): `nextlevel` (0x182119338) = the map, then the gamerules' change level (1809136e0: the
  same the end-of-match vote's think calls; it reads nextlevel).

## NextLevel (CNextLevelIssue 0x1818c6370)

- IsEnabled (180280840): sv_vote_issue_nextlevel_allowed (1).
- CanCallVote (180266a30): the base; sv_vote_issue_nextlevel_choicesmode (1) and the server calling: yes when there
  are no details; IsEnabled false: 5; no map: 7; not found: 6 (as ChangeLevel); sv_vote_issue_nextlevel_prevent_change
  (1) and `nextlevel` already set to a map that exists: 22 NEXTLEVEL_SET; else the map must be in the map group.
- No details and choicesmode: 5 options (slot 0xc8), not yes / no, disp `#SFUI_vote_nextlevel_choices`; else 2,
  yes / no, `#SFUI_vote_nextlevel`. passed (180278900): the details against the current map:
  `#SFUI_vote_passed_nextlevel_extend` when it is the current map, else `#SFUI_vote_passed_nextlevel`.
- ExecuteCommand (18026edb0): details "Extend current Map": mp_timelimit + 20 (when > 0), mp_maxrounds + 2 (> 0),
  mp_winlimit + 2 (> 0), each as a server command; else `nextlevel` = the map, then the map's index in the map group is
  found (the rest, 18026ef7e.., unread).

## RestartGame / ScrambleTeams / SwapTeams (0x1818c5f20 / 0x1818c6490 / 0x1818c65a0)

CanCallVote: the base, then IsEnabled (sv_vote_issue_restart_game_allowed 0 / sv_vote_issue_scramble_teams_allowed 0
/ sv_vote_issue_swap_teams_allowed 0) else 5. ExecuteCommand: the server command `mp_restartgame 1;` /
`mp_scrambleteams 2;` / `mp_swapteams;`. Passed: `#SFUI_vote_passed_restart_game` / `_scramble_teams` /
`_swap_teams`; disp `#SFUI_vote_restart_game` / `_scramble_teams` / `_swap_teams`. All global, yes / no.

## StartTimeOut / Surrender's reasons (their slot 0xf8)

- StartTimeOut (CStartTimeOutIssue 0x1818c6b38): CanTeamCallVote (180267170): gamerules present, no timeout running
  (+0xe4 the T's, +0xe5 the CT's), and the team's timeouts left (+0xf0 T, +0xf4 CT) > 0. CanCallVote (180266ea0): the
  base, then IsEnabled (180280900) else 5. Its failure reason (1802822c0): 9 TEAM_CANT_CALL becomes 28
  TIMEOUT_ACTIVE (a timeout running), 24 MATCH_PAUSED (18093d9e0), else 30 TIMEOUT_EXHAUSTED (30 with no gamerules).
- Surrender (0x1818c6c78): its failure reason (180943510): 9 TEAM_CANT_CALL and 10 WAITINGFORPLAYERS become 23
  TOO_EARLY_SURRENDER.

A failure record blocks a call again only for the same details (Kick 15, ChangeLevel 16, any other issue 8) or, for
SwapTeams / ScrambleTeams / RestartGame, any details; an issue without details (StartTimeOut) is never blocked by it
(only the caller's sv_vote_creation_timer holds them).

## The client's reason table (client_20261105.dll 0x181cdfa40)

`{ int reason, const char *token }` pairs, 16 bytes each, read with the scratch ptrtab.py / dumptab.py: 0
`#SFUI_vote_failed`, 1 `_transition_vote`, 2 `#Panorama_vote_failed_vote_spam`, 3 `_yesno`, 4 `_quorum`, 5
`_disabled_issue`, 6 `_map_not_found`, 7 `_map_name_required`, 8 `#Panorama_vote_failed_recently`, 15 `_recent_kick`,
16 `_recent_changemap`, 17 `_recent_swapteams`, 18 `_recent_scrambleteams`, 19 `_recent_restart` (those five
Panorama_), 9 `_team_cant_call`, 10 `_waitingforplayers`, 11 `#SFUI_vote_failed`, 12 `_cannot_kick_admin`, 13
`_scramble_in_prog`, 20 `_swap_in_prog`, 14 `_spectator`, 21 `_disabled`, 22 `_nextlevel_set`, 32 `_rematch`, 23
`_surrender_too_early`, 33 `_continue`, 24 `_paused`, 25 `_not_paused`, 26 `_not_in_warmup`, 27 `_not_10_players`, 28
`_timeout_active`, 29 `#SFUI_vote_failed`, 30 `_timeouts_exhausted`, 31 `_cant_round_end`, 34 `#SFUI_vote_failed`
(the `#SFUI_vote_failed_` prefix left off). Ported in client/hud/vote-strings.js.

## The Call Vote menu (panorama/scripts/context_menus/context_menu_vote.vjs_c, pak01 2026-11-18)

GetCurrentVoteIssues: not queued matchmaking: "Change Map..." (ChangeLevel, a popup of GetMapsInCurrentMapGroup's maps,
their display names upper-cased); queued and not a tournament: "Surrender?"; queued and a tournament: on a team
starttimeout and PauseMatch (enabled out of the warmup and the pause), else Ready / NotReady in the warmup, Unpause /
Pause after it, and LoadBackup; not a tournament: "Call a Tactical Timeout" (starttimeout) in a competitive /
scrimcomp5v5 / scrimcomp2v2 game mode, then "Kick Player..." (a popup of GetKickTargets' avatars, `callvote Kick
<slot>`). Each item runs `callvote <issue> [param]`.

The disconnect for a vote kick: 157 NETWORK_DISCONNECT_KICKED_VOTEDOFF (network_connection.proto's enum, read from
the DLL's descriptor), "Voted off" (#Player_DisconnectReason_VotedOff).

## Not read yet

- The pause / ready / load-backup issues' slots (registered only on queued tournament servers, so not ours).
- CallVoteFailed (180287c80), the vote command's code-to-string map (180a7ca80), +0x61c, the kick IsEnabled's entity,
  the queued Kick switch, NextLevel's execute tail.
- The client: the vote panel (its show, the passed / failed lines and their hide), the Esc menu's Call Vote
  (context_menu_vote.ts: match-pause.md has its issue list).
