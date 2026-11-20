# Matchmaking, as the client and server show it

client, server, matchmaking.dll and engine2.dll of the 2026-11-16 install; pak01 panorama (layout/matchmaking_status.vxml, popups/popup_accept_match.vxml / .vcss / scripts/popups/popup_accept_match.vts, match-reconnect.vxml / .vts / .vcss, scripts/mainmenu.ts, scripts/common/formattext.ts, sessionutil.ts, rating_emblem.ts, leaderboard.vxml / .ts / .vcss, mainmenu_play.vxml / .ts, context_menus/context_menu_navbar_notification), soundevents/game_sounds_ui.vsndevts, images panorama/images/icons/ui/(ban_competitive|info).vsvg and map_icons/screenshots/360p/<map>_png.vtex, csgo_english.txt. What decides matches (who, when, which servers, cooldown lengths) is Valve's GC: in no file.

## Functions

| Address | Module | What |
|---|---|---|
| 0x180fb2410 | client | `LobbyAPI.GetReadyTimeRemainingSeconds` (bound at 0x180fd1fe2 in the LobbyAPI registration 0x180fd1c90) |
| 0x180007819 | engine2 | registers `sv_mmqueue_reservation_extended_timeout` |
| 0x1800076f3 | engine2 | registers `sv_mmqueue_reservation_timeout` |
| 0x180cf8693 | client | the reservation's session handler ('game/mmqueue', "Update { system { lock mmqueue } game { mmqueue reserved } }", "... mmqueue connect ...", 'QueueConnect', 'reservationid'): `popup_accept_match_found` when the reservation comes (three sites), `popup_accept_match_confirmed` at connect |
| 0x180f93b30 | client | `GetCooldownReason`: jump table on `penalty_reason - 1` (23 entries, table 0x180f93c38) |
| 0x180f93d10 | client | `GetCooldownType` (table 0x180f93d68 for 8..20) |
| 0x180a75eb0 | server | a queued player's team as they connect |
| 0x1808fe780 | server | writes the reservation string ("[%x]" per account) from CMsgGCCStrike15_v2_MatchmakingGC2ServerReserve `account_ids` |
| 0x180907ad0 | server | AreTeamsPlayingSwitchedSides (gamerules) |

## Fields

| Offset | Field |
|---|---|
| CCSGameRules +0xdf8 | m_pQueuedMatchmakingReservationString (`sv_mmqueue_reservation`, "Q[acc][acc]...") |
| CCSGameRules +0xdf0 | m_numQueuedMatchmakingAccounts |
| client lobby `this` +0x24 | reservation time (Plat_MSTime) |
| controller | m_msQueuedModeDisconnectionTimestamp, m_uiAbandonRecordedReason, m_bAbandonAllowsSurrender, m_bAbandonOffersInstantSurrender |

## Constants

| Value | What |
|---|---|
| sv_mmqueue_reservation_extended_timeout | default 21, flags 2, "Extended time in seconds before mmqueue reservation expires." (client: string 0x181cef568, ConVarRef 0x1825d96a8, found lazily by name) |
| sv_mmqueue_reservation_timeout | default 21, min 5, max 180, "Time in seconds before mmqueue reservation expires." |
| mm_dedicated_search_maxping | matchmaking.dll object 0x1801d7a10: default 150, min 25, max 350, flags 0x80 (FCVAR_ARCHIVE), "Longest preferred ping to dedicated servers for games" |
| sv_kick_players_with_cooldown | default 1: "0: do not kick on insecure servers; 1: kick players with Untrusted status or convicted by Overwatch; 2: kick players with any cooldown" |
| sv_disconnected_player_data_hold_time | 60 (the scoreboard keeps a dropped player 60 s) |
| 0x181aba088 | empty string (penalty reason 15) |
| CMsgGCCStrike15_v2_MatchmakingGC2ClientHello | field 2 `ongoingmatch` (a GC2ClientReserve), `penalty_seconds` 4, `penalty_reason` 5 |
| GC2ClientAbandon | `account_id`, `abandoned_match`, `penalty_seconds`, `penalty_reason` (server.dll's embedded descriptor) |

Penalty reasons (`#SFUI_CooldownExplanationReason_<x>`) and their type:

| Reason | Name | Type |
|---|---|---|
| 1 | Kicked | competitive |
| 2 | TK_Limit | competitive |
| 3 | TK_Spawn | competitive |
| 4 | DisconnectedTooLong | competitive |
| 5 | Abandon | competitive |
| 6 | TH_Limit | competitive |
| 7 | TH_Spawn | competitive |
| 8 | OfficialBan | global |
| 9 | KickedTooMuch | competitive |
| 10 | ConvictedForCheating | global |
| 11 | ConvictedForBehavior | global |
| 12 | Abandon_Grace | green |
| 13 | DisconnectedTooLong_Grace | green |
| 14 | OfficialBan | global |
| 15 | (empty) | global |
| 16 | FailedToConnect | competitive |
| 17 | KickAbuse | competitive |
| 18 | SkillGroupCalibration | green |
| 19 | GsltViolation | global |
| 20 | GsltViolation | global |
| 21 | GriefingReports | competitive |
| 22 | VacNetCulprit | global |
| 23 | VacNetAffiliate | global |

## The search status (matchmaking_status.vxml)

See [home-menu.md](home-menu.md) "The matchmaking status": `FormatText.SecondsToDDHHMMSSWithSymbolSeperator(LobbyAPI.GetTimeSpentMatchmaking())` once a second, `LobbyAPI.GetMatchmakingStatusString()` (SFUI_QMM_State_find_searching "Searching for players and servers..."), a non-host party member's "Waiting for lobby leader..." (party_waiting_lobby_leader). The formatter: days, hours, minutes, seconds, each two digits, starting at the first non-zero one or at minutes: 42 -> "00:42", 3723 -> "01:02:03". No estimated wait is shown.

## The accept popup

Layout: `PopupCustomLayout.accept-match` (popupbackground dim) > `#id-accept-match.accept-match-container` > `#AcceptMatchWarning` (unranked warning, hidden), `.accept-match__bg` > `#AcceptMatchMapImage.accept-match__map`, `#AcceptMatchDataContainer.accept-match__data` (`.accept-match__data__title` "#match_ready_title", a `.accept-match__seperator`, `.accept-match__data__details`: `#AcceptMatchModeIcon` icons/ui/competitive + `#AcceptMatchModeMap`), `#id-map-draft-phase-teams` (Your Team / Opponent avatars, > 2 players), `.accept-match__slots-count` (`#AcceptMatchSlots` pips + `#AcceptMatchPlayersAccepted`), `#AcceptMatchBtn.FlatButton` "#match_ready_accept", `#AcceptMatchGameServer` ("Game Server in {s:region} - {d:ping} ms", hidden after accept), `#AcceptMatchCountdown` (stratum-bold-mono), then `#Agreement` (`#AcceptMatchAgreementCompetitive`: SFUI_MapSelectCompWarning, and SFUI_AcceptAgreement, the Fair Play Guidelines link) and the Premier pick / ban frame.

Script:

- Init: attributes `map_and_isreconnect` ("map,true|false"; a map starting `@` is a non-queued match announcement: `m_isNqmmAnnouncementOnly`, accept already pressed), `location`, `ping`. The agreement shows unless reconnecting; its Competitive part only for `game.mode === 'competitive'`.
- Non-queued announcement: `.accept-match__data.auto` (margin 0, centred, ui-scale 125%), plays `popup_accept_match_confirmed_casual`, `$.Schedule(4.5, _OnNqmmAutoReadyUp)` sets ready ('deferred') and closes.
- `PanoramaComponent_Lobby_ReadyUpForMatch(shouldShow, playersReadyCount, numTotalClientsInReservation)`: closes when !shouldShow; `popup_accept_match_person` when accepted and the ready count went up; then `_UpdateUiState` and a 1 s timer.
- `_UpdateUiState`: slots show (timer hides) once accept is pressed or on reconnect; the button hides then; timer text `"0:" + (s < 10 ? "0" : "") + s`, hidden at <= 0. A slot `.accept-match__slots__player`, `--accepted` for `i < numPlayersReady`; label `match_ready_players_accepted` "{d:accepted} / {d:slots} Players Ready".
- `_OnTimerUpdate` (each 1 s while time is left): `popup_accept_match_waitquiet` after accepting, else `popup_accept_match_beep`.
- `OnAcceptMatchPressed`: `popup_accept_match_person`, `LobbyAPI.SetLocalPlayerReady('accept')`. No decline button: not pressing ACCEPT in time is the decline.
- `_SetMatchData`: `match_ready_match_data` "{s:mode} • {s:map}" (`#SFUI_GameMode_<mode>`, `#SFUI_Map_<map>`), or `_modifier` "{s:mode} • {s:modifier} • {s:map}" when the mode shows flags; map image `map_icons/screenshots/360p/<map>.png`.

Styles: `.accept-match` 0.2 s ease-in; `.Hidden` opacity 0, pre-transform-scale2d 1.25, translateY -10 px (sound UIPanorama.ui_custom_lobby_dialog_slide, volume 0); container padding-top 20%; `.accept-match__bg` min-width 720, `gradient(linear, 0% 0%, 0% 100%, from(#4CAF50), to(#255E28))`, 6 px padding, background video gobutton.webm; `__map` 300 px, brightness .05, background-img-opacity .8; `__data` margin-top 20; `__data__title` 52 px uppercase rgb(101, 228, 106), text-shadow 0 0 4 px 2.0 rgba(0,0,0,.534); `--details` 19 px; `__seperator` 1 px positiveColor (#0F9D58); FlatButton bottom, margin-bottom 76, rgb(53, 182, 81), label 52 px bold uppercase rgb(18, 59, 8), margin 12 32 10 32, white with a glow on hover, hidden: opacity 0 ui-scale 150% .25 s; `__slots-count` bottom, margin-bottom 70; a slot 48 px, border 4 px rgb(33, 78, 34), margin 8, rgb(28, 71, 31) with the player icon at 5%; accepted: border positiveColor, glow rgba(144, 212, 144, .493) 8 px, rgb(70, 160, 71), icon 100%; `__data__time` 242 x 32 at the bottom, margin-bottom 16, 20 px bold; `__agreement` translateY 20, rgba(0,0,0,.98), radius 6, max-width 740, padding 20; its label 16 px Stratum2 medium rgba(255,255,255,.7).

The window (0x180fb2410): `cvar(sv_mmqueue_reservation_extended_timeout).int - (Plat_MSTime() - [this + 0x24]) / 1000 - 1` (`imul 0x10624dd3; sar 6` is the /1000), 0 with no reservation. So the popup counts "0:20" to "0:00".

Sounds (game_sounds_ui.vsndevts, mixgroup UI, csgo_mega):

| Event | Volume | Sound |
|---|---|---|
| `popup_accept_match_found` | 0.4 | sounds/ui/panorama/game_ready_02 |
| `popup_accept_match_beep` | 0.4 | sounds/ui/competitive_accept_beep (time-volume curve 1 -> 0 over 1 s) |
| `popup_accept_match_waitquiet` | 1.0 | submenu_scroll_01 |
| `popup_accept_match_person` | 0.2 | submenu_select_01 |
| `popup_accept_match_confirmed` | 0.3 | sounds/ui/mm_success_lets_roll |
| `popup_accept_match_confirmed_casual` | 0.4 | mm_success_lets_roll |
| `generic_button_press` | | the reconnect buttons |

A failed accept (the GC's): the one who didn't, SFUI_QMM_ERROR_1_FailReadyUp_Title "YOU FAILED TO ACCEPT" / "A match was found for you, but you failed to accept it. You have been removed from the matchmaking queue."; their party, SFUI_QMM_ERROR_X_FailReadyUp "A match was found for you, but %s1 failed to accept it.".

## The Reconnect panel

In mainmenu.xml as `<Frame id="MatchmakingReconnectPanel">` beside the party chat. `.match-status-reconnect` (right, margin-right 96, 96 px tall, translateX -256 px unless `.sidebar-collapsed`) > `.match-status-ongoingmatch-container` (black .5, padding 8, translateY -100% until `.show-actions` / `.show-cancel`, .25 s) > `SFUI_MainMenu_Reconnect_Info` "You were disconnected from a Competitive Match" (18 px Stratum2 medium, max 420), then `#MatchmakingReconnect` (PopupButton Positive "RECONNECT") + `#MatchmakingAbandon` (PopupButton "ABANDON"), or while reconnecting `#MatchmakingReconnecting` (disabled "RECONNECTING") + `#MatchmakingCancel` ("CANCEL").

- Shown when `CompetitiveMatchAPI.HasOngoingMatch()`, the match hasn't ended (`GameState_OnGamePhaseChange` phase 5) and no accept popup is up; `show-cancel` while `sessionSettings.game.mapgroupname === 'reconnect'`.
- RECONNECT: `CompetitiveMatchAPI.ActionReconnectToOngoingMatch()`; ABANDON: `ActionAbandonOngoingMatch()` (no confirm popup); CANCEL: `LobbyAPI.StopMatchmaking()`; each plays UIPanorama.generic_button_press.
- The GC's hello carries the ongoing match. Queueing with one running: SFUI_QMM_ERROR_1_OngoingMatch "You have an ongoing match that you should rejoin from the Main Menu." (`_X_`: "%s1 has an ongoing match ...").

## Abandons and cooldowns

- mainmenu.ts `_GetNotificationBarData`: with `CompetitiveMatchAPI.GetCooldownSecondsRemaining() > 0` a top-bar alert, icon `ban_competitive` (`.mainmenu-top-navbar__alerts-icon.yellow-alert`: 32 px, margin 6, padding 4, radius 3, washed warningColor #b1af2d, pulsing `navbar-yellow-alert` 1.5 s: brightness 1 -> 2, a 3 px rgba(177,175,45,.5) border at 50%, img-shadow 3 px warningColor).
- Title by `GetCooldownType()`: "global" SFUI_MainMenu_Global_Ban_Title "Global Cooldown", "green" SFUI_MainMenu_Temporary_Ban_Title "Temporary Cooldown", "competitive" SFUI_MainMenu_Competitive_Ban_Title "Competitive Cooldown", + `FormatText.SecondsToSignificantTimeString(seconds)` unless permanent; tooltip `GetCooldownReason()`; a Fair Play Guidelines link when `ShowFairPlayGuidelinesForCooldown()`. A click opens context_menu_navbar_notification (title, tooltip, link). A cooldown < 0 (expired, unacknowledged) pops "Competitive Cooldown Expired" with SFUI_CooldownExplanationReason_Expired_Cooldown + the reason.
- `SecondsToSignificantTimeString`: < 60 s "1 Min"; else the biggest non-zero of days / hours / minutes, plus one when the next unit is past 16 h / 40 min / 40 s; SFUI_Store_Timer_Day / _Hour / _Min ("{n} Day(s)" ...).
- Notices: SFUI_Notice_Player_AbandonedCooldown_Min / _Hrs / _Days "%s1 abandoned the match and received a %s2 minute / hour / day competitive matchmaking cooldown"; SFUI_MainMenu_Queue_Abandon_Message (disconnecting from a running match). Queueing in cooldown: SFUI_QMM_ERROR_1_PenaltySeconds "You are in cooldown and cannot participate in competitive matchmaking yet." (`_X_`, and `...Green` "You need to wait before playing additional competitive matches.").
- The tiers are the GC's (not in any binary); CS:GO's players reported 30 min, 2 h, 24 h, 7 days, a step up per abandon within a week of the last (unverified).

## Who starts CT (0x180a75eb0)

1. The reservation string (+0xdf8) is scanned for '[' entries; the player's index `i` of `n` ("{%x}" entries are casters: "Forcing spectator team for %s player/%d (%x - %s).").
2. `team = ((i < n / 2) xor AreTeamsPlayingSwitchedSides()) + 2` (`cdq; sub; sar 1` is the signed /2): 3 CT, 2 T. The first half of the GC's list starts CT, swapped once the teams play switched sides.
3. Log "Team for queue player#%d/%d (%x - %s) on %s team for %s teams: %s\n" (i + 1, n, account, name, "first" / "second", "switched" / "normal", "CT" / "T").

Which team the GC lists first, and the queue's fill (skill, region, wait), are the GC's.

## Ratings (rating_emblem.ts)

Tiers, colours, the split: [home-menu.md](home-menu.md) "The rating tile". No rating until `SessionUtil.GetNumWinsNeededForRank` wins (sessionutil.ts: 'Competitive' 2, otherwise 10): "Win <b>N</b> more match(es)" (cs_rating_wins_needed:f), tooltip_cs_rating_none:f "Win N additional matches to establish your CS Rating."; 0 after one is "CS Rating Expired" (tooltip "Your CS Rating has expired due to inactivity. Win 1 match to display it again."); with one: "CS Rating", "{d:o:rank} in the World" when the leaderboard rank is in the top `GetPremierLeaderboardTopBestCount()`, else "Top {d:o:percentile} Percent"; SplitRating's third part '1' / '2': "Next match is a promotion / relegation match".

## The leaderboard

- Where: the play menu's Premier page (mainmenu_play.vxml MapSelectionContainer_premier): left `#jsParty` (lbtype "party") and `#jsPremierMapWinRecord`; right `#jsSeasonProgress` and `#jsLeaderboard` (lbtype "general"). `#PlayMenulLeaderboards` (graph icon, "#SFUI_LEADERBOARD") is always hidden by `_UpdateLeaderboardBtn`. (popup_leaderboards.vxml is the Pick'Em / operation one.)
- Layout: `.leaderboard-root` > `#lbNameButton` ("Submit a leaderboard name" / "Leaderboard Name: {s:leaderboard-name}", pending / approved), `.leaderboard__contents` > `.leaderboard-header` (`.leaderboard-title-bar__label` "{s:leaderboard-title}" = leaderboard_title_general "Leaderboards" / _party "Your Party"; `#id-leaderboard-navbar`: `#jsGoToTop` "Go to top", `#jsGoToMe` "Go to me", `#jsNavSeason`, the region DropDown `#jsNavLocation`), status panels `#id-leaderboard-loading` (Spinner, "Loading Leaderboard..."), `-nodata` ("No data found for this leaderboard"), `-newseason` ("The {s:season_name} regional leaderboards will populate once the ratings have been calibrated."), `-newseason-friends` ("The {s:season_name} friends leaderboard will populate as soon as you or your friends reestablish a CS Rating."), and `#id-leaderboard-list`: a header row and a JSDelayLoadList (`itemwidth 716px`, `itemheight 30px`) of `leaderboard-entry` rows.
- Columns (leaderboard_column_*): rank "Rank", rating "CS Rating" (rating_emblem), name "Player" (avatar + honor icon on the party board only), wins "Wins", winrate "Win %", rankpct "% Rank", region "LB".
- Script: season `LeaderboardsAPI.GetCurrentSeasonPremierLeaderboard()` ("#<lb>_name": "Season One" ... "Season Five"); dropdown `Friends`, `World`, then the regions (`GetAllSeasonPremierLeaderboardRegions`, sorted; with IS_AROUND_PLAYER only the ones you are on), selected: Friends; board name `<season>.friends` or `<season>[_<region>].self`. IS_AROUND_PLAYER is true: Go to top / Go to me hidden; once ready the list scrolls to your row centred (`GoToSelf`: ScrollToDelayLoadListItem 'center'); your row `.local-player`.
- A row: rank (`'-'` without one), the emblem (Premier, no full details), name (`displayName` or Steam's), wins (`matchesWon`), win % `matchesWon * 100 / (won + tied + lost)` to 2 decimals, % rank `pct.toFixed(0) + '%'`, region `#leaderboard_region_abbr_<Region>` (EU #FFDD00, AS #fc8200, AU #008bfc, AF #19bf00, NA #d281fc, SA #02c1e3, CN #ff5959). Refreshed when the cache is a minute old. Empty: Friends shows the newseason-friends text, World (around you) the same, else no data.
- Styles: `.leaderboard-root` padding 12; title bar 32 px, Stratum2 Medium Italic 22 px uppercase, padding 4 0 0 26, on icons/ui/premier_title_bg (a gold #FFD700 and a blue #4B69FF slash, then black .5); navbar labels Stratum2 Condensed 16 px, the dropdown 150 px (menu labels Stratum2 Medium Condensed 18 px; a board you are on washed rgb(214, 214, 0)); rows 30 px, padding-right 30, every other one rgba(0,0,0,.25); cells Stratum2 Regular Monodigit 14 px, right-aligned (the name left); header cells Stratum2 Condensed 18 px at .5; widths rank 70, rating 80, name fill, wins 50, winrate 70, rankpct 50 (visible on .friends and the party board only), region 30 (visible on .world / .friends); `.local-player` labels gold.

## Regions

The play menu has no region picker (mainmenu_play.ts has no ping / region / datacenter code). The one setting is Game > "Max Acceptable Matchmaking Ping" (DatacenterPingThresholdSlider): `mm_dedicated_search_maxping`. No server within it: SFUI_QMM_ERROR_1_FailPingServer "... try increasing your 'Max Acceptable Matchmaking Ping' in 'Options > Game Settings' ...".

## Unread

- How the GC fills, orders and times out (not in any binary).
- The Premier pick / ban popup (popup_premier_pick_ban) the accept popup hands over to.
- The client's handler that turns GC2ClientAbandon into the notice; the Expired popup's acknowledge (CompetitiveMatchAPI.ActionAcknowledgePenalty).
- m_bAbandonOffersInstantSurrender's surrender vote after an abandon.
