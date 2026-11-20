# CS2's matchmaking, as its client and server show it

Read 2026-11-16 from the install (game/csgo/pak01_dir.vpk panorama sources, csgo_english.txt; client.dll, server.dll,
matchmaking.dll, game/bin/win64/engine2.dll of that day's build). Used by server/cs2web/lobby/ (matchmaker.js,
ready-check.js, queue-fill.js, penalties.js, seats.js, queue-wait.js) and client/home/ (accept-popup.js, reconnect.js,
queue-toast.js). What decides matches (who, when, which servers, cooldown lengths) is Valve's GC: not in any file
here; each place that needs it is a labelled stand-in in the code.

How the sources were read:

- Panorama layouts / styles / scripts, decompiled: `lasers-bake --settings-ref <out> --match accept_match,match-reconnect,rating_emblem,premier,matchmaking_status,mainmenu_play,mainmenu.,friendlobby,sessionutil,formattext,context_menu_navbar_notification`
  (bake/SettingsRefBake.cs; `--match` picks the files whose path holds any of the terms).
- Sound events: `lasers-bake --decompile <pak01_dir.vpk> "soundevents/game_sounds_ui\.vsndevts_c" <out>`; the ones the
  home plays baked by `lasers-bake --menu-sounds web/public/ze-ui/sounds` (bake/MenuSoundBake.cs).
- Images the home shows (web/public/ze-ui/mm/, gitignored): `lasers-bake --decompile <pak01_dir.vpk>
  "panorama/images/(icons/ui/(ban_competitive|info)\.vsvg_c|map_icons/screenshots/360p/de_(dust2|inferno|mirage)_png\.vtex_c)" <out>`,
  the .vsvg renamed .svg, the `_png.vtex.png` to `<map>.png`.
- Binaries: tools/re (strings.py, riprefs.py: new, a string's / global's rip-relative users by bytes; fnstrings.py,
  fnat.py, cvardump.py, protomsg.py, schema.py, dispuses.py).

## The search status (layout/matchmaking_status.vxml)

Already in home-menu.md "The matchmaking status": the time searched (`FormatText.SecondsToDDHHMMSSWithSymbolSeperator`
of `LobbyAPI.GetTimeSpentMatchmaking()`, once a second), the status string (`LobbyAPI.GetMatchmakingStatusString()`:
SFUI_QMM_State_find_searching "Searching for players and servers..."), a non-host party member's "Waiting for lobby
leader..." (party_waiting_lobby_leader). `SecondsToDDHHMMSSWithSymbolSeperator` (scripts/common/formattext.ts): days,
hours, minutes, seconds, each padded to two digits, starting at the first non-zero one or at minutes: 42 -> "00:42",
3723 -> "01:02:03" (queue-toast.js clock()). CS2's panel shows **no estimated wait**: ours is a stand-in (queue-wait.js).

## The accept popup (layout/popups/popup_accept_match.vxml, .vcss, scripts/popups/popup_accept_match.vts)

Layout (ids / classes): `PopupCustomLayout.accept-match` (popupbackground dim) > `#id-accept-match.accept-match-container` >
`#AcceptMatchWarning` (the unranked warning, hidden), `.accept-match__bg` > `#AcceptMatchMapImage.accept-match__map`,
`#AcceptMatchDataContainer.accept-match__data` (`.accept-match__data__title` "#match_ready_title", a
`.accept-match__seperator`, `.accept-match__data__details`: `#AcceptMatchModeIcon` icons/ui/competitive + `#AcceptMatchModeMap`),
`#id-map-draft-phase-teams` (Your Team / Opponent avatars, > 2 players), `.accept-match__slots-count` (`#AcceptMatchSlots`
pips + `#AcceptMatchPlayersAccepted`), `#AcceptMatchBtn.FlatButton` "#match_ready_accept", `#AcceptMatchGameServer`
("Game Server in {s:region} - {d:ping} ms", hidden after accept), `#AcceptMatchCountdown` (stratum-bold-mono), then
`#Agreement` (`#AcceptMatchAgreementCompetitive`: SFUI_MapSelectCompWarning, and SFUI_AcceptAgreement, the Fair Play
Guidelines link) and the Premier pick / ban frame.

Script:

- Init: attributes `map_and_isreconnect` ("map,true|false"; a map starting `@` is a non-queued match announcement:
  `m_isNqmmAnnouncementOnly`, accept already pressed), `location`, `ping`. The agreement shows unless reconnecting; its
  Competitive part only for `game.mode === 'competitive'`.
- A non-queued announcement: `.accept-match__data.auto` (margin 0, centred, ui-scale 125%), plays
  `popup_accept_match_confirmed_casual`, and `$.Schedule(4.5, _OnNqmmAutoReadyUp)` sets the player ready
  ('deferred') and closes the popup.
- `PanoramaComponent_Lobby_ReadyUpForMatch(shouldShow, playersReadyCount, numTotalClientsInReservation)`: closes when
  !shouldShow; plays `popup_accept_match_person` when accepted and the ready count went up; then `_UpdateUiState` and a
  1 s timer.
- `_UpdateUiState`: the slots show (and the timer hides) once accept is pressed or on reconnect; the button hides then;
  the timer text is `"0:" + (s < 10 ? "0" : "") + s`, hidden at <= 0. A slot is `.accept-match__slots__player`, lit with
  `--accepted` for `i < numPlayersReady`; the label `match_ready_players_accepted` "{d:accepted} / {d:slots} Players Ready".
- `_OnTimerUpdate` (each 1 s while time is left): `popup_accept_match_waitquiet` after accepting, else `popup_accept_match_beep`.
- `OnAcceptMatchPressed`: `popup_accept_match_person`, `LobbyAPI.SetLocalPlayerReady('accept')`. There is **no decline
  button**: not pressing ACCEPT in time is the decline.
- `_SetMatchData`: `match_ready_match_data` "{s:mode} • {s:map}" (`#SFUI_GameMode_<mode>`, `#SFUI_Map_<map>`), or
  `_modifier` "{s:mode} • {s:modifier} • {s:map}" when the mode shows flags; the map image
  `map_icons/screenshots/360p/<map>.png`.

Styles (the ones drawn, accept-popup.css): `.accept-match` 0.2 s ease-in; `.Hidden` opacity 0, pre-transform-scale2d 1.25,
translateY -10 px (sound UIPanorama.ui_custom_lobby_dialog_slide, volume 0 in game_sounds_ui); container padding-top 20%;
`.accept-match__bg` min-width 720, `gradient(linear, 0% 0%, 0% 100%, from(#4CAF50), to(#255E28))`, 6 px padding,
background video gobutton.webm (not drawn); `__map` 300 px, brightness .05, background-img-opacity .8; `__data` margin-top
20; `__data__title` 52 px uppercase rgb(101, 228, 106), text-shadow 0 0 4 px 2.0 rgba(0,0,0,.534); `--details` 19 px;
`__seperator` 1 px positiveColor (#0F9D58); FlatButton bottom, margin-bottom 76, rgb(53, 182, 81), label 52 px bold
uppercase rgb(18, 59, 8), margin 12 32 10 32, white with a glow on hover, hidden: opacity 0 ui-scale 150% .25 s;
`__slots-count` bottom, margin-bottom 70; a slot 48 px, border 4 px rgb(33, 78, 34), margin 8, rgb(28, 71, 31) with the
player icon at 5%; accepted: border positiveColor, glow rgba(144, 212, 144, .493) 8 px, rgb(70, 160, 71), icon 100%;
`__data__time` 242 x 32 at the bottom, margin-bottom 16, 20 px bold; `__agreement` translateY 20, rgba(0,0,0,.98),
radius 6, max-width 740, padding 20; its label 16 px Stratum2 medium rgba(255,255,255,.7).

The accept window:

- client.dll **0x180fb2410** `LobbyAPI.GetReadyTimeRemainingSeconds` (bound at 0x180fd1fe2 in the LobbyAPI
  registration 0x180fd1c90): `cvar(sv_mmqueue_reservation_extended_timeout).int - (Plat_MSTime() - [this + 0x24]) / 1000 - 1`
  (the `imul 0x10624dd3; sar 6` is the /1000), 0 when no reservation; the convar found lazily by name (string 0x181cef568,
  ConVarRef object 0x1825d96a8).
- engine2.dll registers it (0x180007819): `sv_mmqueue_reservation_extended_timeout` default **21**, flags 2,
  "Extended time in seconds before mmqueue reservation expires."; beside it `sv_mmqueue_reservation_timeout` default 21,
  min 5, max 180 (0x1800076f3), "Time in seconds before mmqueue reservation expires.". So the popup counts "0:20" to
  "0:00" (ready-check.js READY_S 21, secs 20).
- client.dll **0x180cf8693** (the reservation's session handler: 'game/mmqueue', "Update { system { lock mmqueue } game
  { mmqueue reserved } }", "... mmqueue connect ...", 'QueueConnect', 'reservationid'): plays
  `popup_accept_match_found` when the reservation comes (three sites) and `popup_accept_match_confirmed` at connect.

Sounds (soundevents/game_sounds_ui.vsndevts, all mixgroup UI, csgo_mega): `popup_accept_match_found` 0.4,
sounds/ui/panorama/game_ready_02; `_beep` 0.4, sounds/ui/competitive_accept_beep (a time-volume curve 1 -> 0 over 1 s);
`_waitquiet` 1.0, submenu_scroll_01; `_person` 0.2, submenu_select_01; `_confirmed` 0.3, sounds/ui/mm_success_lets_roll;
`_confirmed_casual` 0.4, mm_success_lets_roll; `generic_button_press` (the reconnect buttons).

What happens when someone doesn't accept is the GC's. What the client says (csgo_english.txt): the one who didn't,
SFUI_QMM_ERROR_1_FailReadyUp_Title "YOU FAILED TO ACCEPT" / "A match was found for you, but you failed to accept it. You
have been removed from the matchmaking queue."; their party, SFUI_QMM_ERROR_X_FailReadyUp "A match was found for you,
but %s1 failed to accept it.". Stand-ins (ready-check.js / matchmaker.js): the others go back to the queue at their own
place; the one who didn't gets a 60 s Competitive block (penalties.js FAIL_ACCEPT_S, reason 16 FailedToConnect).

## The Reconnect panel (layout/match-reconnect.vxml, scripts/match-reconnect.vts, styles/match-reconnect.vcss)

In mainmenu.xml as `<Frame id="MatchmakingReconnectPanel">` beside the party chat. `.match-status-reconnect` (right,
margin-right 96, 96 px tall, translateX -256 px unless `.sidebar-collapsed`) > `.match-status-ongoingmatch-container`
(black .5, padding 8, translateY -100% until `.show-actions` / `.show-cancel`, .25 s) > the message
`SFUI_MainMenu_Reconnect_Info` "You were disconnected from a Competitive Match" (18 px Stratum2 medium, max 420), then
`#MatchmakingReconnect` (PopupButton Positive "RECONNECT") + `#MatchmakingAbandon` (PopupButton "ABANDON"), or while
reconnecting `#MatchmakingReconnecting` (disabled "RECONNECTING") + `#MatchmakingCancel` ("CANCEL").

Script: shown when `CompetitiveMatchAPI.HasOngoingMatch()` and the match hasn't ended (`GameState_OnGamePhaseChange`
phase 5) and no accept popup is up; `show-cancel` while `sessionSettings.game.mapgroupname === 'reconnect'`. RECONNECT:
`CompetitiveMatchAPI.ActionReconnectToOngoingMatch()`; ABANDON: `ActionAbandonOngoingMatch()` (no confirm popup here);
CANCEL: `LobbyAPI.StopMatchmaking()`; each plays UIPanorama.generic_button_press. The GC's hello carries the ongoing
match (CMsgGCCStrike15_v2_MatchmakingGC2ClientHello field 2 `ongoingmatch`, a GC2ClientReserve). Queueing with one
running is refused: SFUI_QMM_ERROR_1_OngoingMatch "You have an ongoing match that you should rejoin from the Main Menu."
(`_X_`: "%s1 has an ongoing match ...").

Ours (seats.js, reconnect.js): the seat's ticket kept in the browser and, for a signed-in player, in /api/ze/me; the
match is asked about on the `/ze?seat=` socket. The panel itself is no longer drawn (the owner's, 2026-11-18): the Play
screen's GO button is RESUME with ABANDON under it instead (home.js), ABANDON asking with abandon-popup.js.

## Abandons and cooldowns

What the client shows (scripts/mainmenu.ts `_GetNotificationBarData`): with `CompetitiveMatchAPI.GetCooldownSecondsRemaining()
> 0` a top-bar alert, icon `ban_competitive` (`.mainmenu-top-navbar__alerts-icon.yellow-alert`: 32 px, margin 6, padding 4,
radius 3, washed warningColor #b1af2d, pulsing `navbar-yellow-alert` 1.5 s: brightness 1 -> 2, a 3 px rgba(177,175,45,.5)
border at 50%, img-shadow 3 px warningColor), title by `GetCooldownType()`: "global" SFUI_MainMenu_Global_Ban_Title
"Global Cooldown", "green" SFUI_MainMenu_Temporary_Ban_Title "Temporary Cooldown", "competitive"
SFUI_MainMenu_Competitive_Ban_Title "Competitive Cooldown", + `FormatText.SecondsToSignificantTimeString(seconds)` unless
permanent; the tooltip `GetCooldownReason()`; a Fair Play Guidelines link when `ShowFairPlayGuidelinesForCooldown()`.
Clicking opens context_menus/context_menu_navbar_notification (title, tooltip, link). A cooldown < 0 (expired, unacknowledged)
pops "Competitive Cooldown Expired" with SFUI_CooldownExplanationReason_Expired_Cooldown + the reason (not drawn).

`SecondsToSignificantTimeString` (formattext.ts): < 60 s "1 Min"; else the biggest non-zero of days / hours / minutes,
plus one when the next unit is past 16 h / 40 min / 40 s; SFUI_Store_Timer_Day / _Hour / _Min ("{n} Day(s)" ...)
(reconnect.js significantTime()).

client.dll **0x180f93b30** `GetCooldownReason`: a jump table on `penalty_reason - 1` (23 entries, table 0x180f93c38):
1 Kicked, 2 TK_Limit, 3 TK_Spawn, 4 DisconnectedTooLong, 5 Abandon, 6 TH_Limit, 7 TH_Spawn, 8 OfficialBan, 9 KickedTooMuch,
10 ConvictedForCheating, 11 ConvictedForBehavior, 12 Abandon_Grace, 13 DisconnectedTooLong_Grace, 14 OfficialBan, 15 (empty
string 0x181aba088), 16 FailedToConnect, 17 KickAbuse, 18 SkillGroupCalibration, 19 GsltViolation, 20 GsltViolation,
21 GriefingReports, 22 VacNetCulprit, 23 VacNetAffiliate (each `#SFUI_CooldownExplanationReason_<x>`).
client.dll **0x180f93d10** `GetCooldownType`: 8, 10, 11, 14, 15, 19, 20 "global" (table 0x180f93d68 for 8..20), 22, 23
"global", 12, 13, 18 "green", anything else "competitive" (penalties.js cooldownType).
The penalty comes from the GC (GC2ClientHello `penalty_seconds` 4 / `penalty_reason` 5; GC2ClientAbandon
`account_id`, `abandoned_match`, `penalty_seconds`, `penalty_reason`: server.dll's embedded descriptor). The game's notice
when someone abandons: SFUI_Notice_Player_AbandonedCooldown_Min / _Hrs / _Days "%s1 abandoned the match and received a %s2
minute / hour / day competitive matchmaking cooldown"; SFUI_MainMenu_Queue_Abandon_Message (disconnecting from a running
match). Queueing in cooldown: SFUI_QMM_ERROR_1_PenaltySeconds "You are in cooldown and cannot participate in competitive
matchmaking yet." (`_X_`, and `...Green` "You need to wait before playing additional competitive matches.").

server.dll fields on the player controller: `m_msQueuedModeDisconnectionTimestamp`, `m_uiAbandonRecordedReason`,
`m_bAbandonAllowsSurrender`, `m_bAbandonOffersInstantSurrender` (a surrender vote after an abandon: not done here);
`sv_kick_players_with_cooldown` (default 1: "0: do not kick on insecure servers; 1: kick players with Untrusted status or
convicted by Overwatch; 2: kick players with any cooldown"); `sv_disconnected_player_data_hold_time` 60 (the scoreboard
keeps a dropped player 60 s).

**Stand-ins** (the GC's, penalties.js / seats.js): the tiers 30 min, 2 h, 24 h, 7 days, a step up per abandon within a
week of the last (what CS:GO's players reported); the time a dropped player has before it counts as DisconnectedTooLong
(ABANDON_MS 5 min); only rated matches (no bots, everyone signed in) give one; kept in memory (a restart forgets them).

## Who starts CT (server.dll 0x180a75eb0)

A queued player's team as they connect: the reservation (`sv_mmqueue_reservation`, the "Q[acc][acc]..." string the
gamerules build from the GC's CMsgGCCStrike15_v2_MatchmakingGC2ServerReserve `account_ids`: 0x1808fe780 writes it with
"[%x]" per account into CCSGameRules `m_pQueuedMatchmakingReservationString` +0xdf8, counting `m_numQueuedMatchmakingAccounts`
+0xdf0) is scanned for '[' entries; the player's index `i` of `n` ("{%x}" entries are casters: "Forcing spectator team
for %s player/%d (%x - %s)."). Then `team = ((i < n / 2) xor AreTeamsPlayingSwitchedSides()) + 2` (0x180907ad0 on the
gamerules; `cdq; sub; sar 1` is the signed /2), so 3 CT, 2 T: **the first half of the GC's list starts CT**, the second
T, swapped once the teams play switched sides. Logged as "Team for queue player#%d/%d (%x - %s) on %s team for %s teams:
%s\n" (i + 1, n, account, name, "first" / "second", "switched" / "normal", "CT" / "T"). Which team the GC lists first
is the GC's: ours is a coin flip (queue-fill.js startSides).

## The queue's fill

The GC's (matching by skill, region, wait): not readable. Ours (queue-fill.js pickMatch): the oldest groups that pack
into two whole sides, searched depth first in age order.

## Ratings and regions

- The Premier rating tile: home-menu.md "The rating tile" (tiers, colours, the split). From rating_emblem.ts also: no
  rating until `SessionUtil.GetNumWinsNeededForRank` wins (sessionutil.ts: 'Competitive' 2, otherwise 10): "Win <b>N</b>
  more match(es)" (cs_rating_wins_needed:f), tooltip_cs_rating_none:f "Win N additional matches to establish your CS
  Rating."; a rating of 0 after one is "CS Rating Expired" (tooltip "Your CS Rating has expired due to inactivity. Win 1
  match to display it again."); with one: "CS Rating", "{d:o:rank} in the World" when the leaderboard rank is in the top
  `GetPremierLeaderboardTopBestCount()`, else "Top {d:o:percentile} Percent"; the third part of SplitRating '1' / '2':
  "Next match is a promotion / relegation match". Ours (ratings.js, rating-tile.js): the rating hidden until 10 wins
  (the server sends null with winsNeeded, the tile "---" with "Win N additional matches to establish your CS Rating."),
  then "CS Rating" with "{rank} in the World" (an ordinal, within TOP_BEST 100: GetPremierLeaderboardTopBestCount is
  the GC's) or "Top {pct} Percent". Not done (the GC's): expiry, promotion / relegation, seasons.

## The leaderboard (layout/leaderboard.vxml, scripts/leaderboard.ts, styles/leaderboard.vcss)

Where: the play menu's Premier page (mainmenu_play.vxml MapSelectionContainer_premier): left `#jsParty` (lbtype
"party": your party's ratings) and `#jsPremierMapWinRecord`; right `#jsSeasonProgress` and `#jsLeaderboard` (lbtype
"general"). The play menu also has a `#PlayMenulLeaderboards` option button (graph icon, "#SFUI_LEADERBOARD"), always
hidden by `_UpdateLeaderboardBtn` today. (popup_leaderboards.vxml is the Pick'Em / operation one, not Premier's.)

Layout: `.leaderboard-root` > `#lbNameButton` (leaderboard name registration: "Submit a leaderboard name" /
"Leaderboard Name: {s:leaderboard-name}", pending / approved), `.leaderboard__contents` > `.leaderboard-header`
(`.leaderboard-title-bar__label` "{s:leaderboard-title}" = leaderboard_title_general "Leaderboards" / _party "Your
Party"; `#id-leaderboard-navbar`: `#jsGoToTop` "Go to top", `#jsGoToMe` "Go to me", the season label `#jsNavSeason`,
the region DropDown `#jsNavLocation`), the status panels `#id-leaderboard-loading` (Spinner, "Loading
Leaderboard..."), `-nodata` ("No data found for this leaderboard"), `-newseason` ("The {s:season_name} regional
leaderboards will populate once the ratings have been calibrated."), `-newseason-friends` ("The {s:season_name} friends
leaderboard will populate as soon as you or your friends reestablish a CS Rating."), and `#id-leaderboard-list`: a
header row and a JSDelayLoadList (`itemwidth 716px`, `itemheight 30px`) of the `leaderboard-entry` snippet's rows.
Columns (leaderboard_column_*): rank "Rank", rating "CS Rating" (the rating_emblem), name "Player" (avatar + honor icon
on the party board only), wins "Wins", winrate "Win %", rankpct "% Rank", region "LB".

Script: the season is `LeaderboardsAPI.GetCurrentSeasonPremierLeaderboard()` ("#<lb>_name": "Season One" ... "Season
Five"); the dropdown `Friends`, `World`, then the regions (`GetAllSeasonPremierLeaderboardRegions`, sorted; with
IS_AROUND_PLAYER only the ones you are on), **selected: Friends**; the board name is `<season>.friends` or
`<season>[_<region>].self` (around you). IS_AROUND_PLAYER is true: Go to top / Go to me hidden, and once ready the list
scrolls to your row centred (`GoToSelf`: ScrollToDelayLoadListItem 'center'); your row gets `.local-player`. A row:
rank (`'-'` without one), the emblem (Premier, no full details), name (`displayName` or Steam's), wins
(`matchesWon`), win % `matchesWon * 100 / (won + tied + lost)` to 2 decimals, % rank `pct.toFixed(0) + '%'`, region
`#leaderboard_region_abbr_<Region>` (coloured: EU #FFDD00, AS #fc8200, AU #008bfc, AF #19bf00, NA #d281fc, SA #02c1e3, CN
#ff5959). Refreshed when the cache is a minute old. Empty: the Friends board shows the newseason-friends text, World
(around you) the same, else no data.

Styles: `.leaderboard-root` padding 12; title bar 32 px, Stratum2 Medium Italic 22 px uppercase, padding 4 0 0 26, on
icons/ui/premier_title_bg (a gold #FFD700 and a blue #4B69FF slash, then black .5); navbar labels Stratum2 Condensed 16 px,
the dropdown 150 px (menu labels Stratum2 Medium Condensed 18 px; a board you are on washed rgb(214, 214, 0)); rows 30 px,
padding-right 30, every other one rgba(0,0,0,.25); cells Stratum2 Regular Monodigit 14 px, right-aligned (the name
left); header cells Stratum2 Condensed 18 px at .5; widths rank 70, rating 80, name fill, wins 50, winrate 70, rankpct 50
(visible on .friends and the party board only), region 30 (visible on .world / .friends); `.local-player` labels gold.

Ours (server/cs2web/lobby/leaderboard.js, client/home/leaderboard.js): one board a format (1v1 / 3v3 / 5v5: the format
shown where the season is), Friends (you and ze_friends) and World, established ratings (10 wins) by rating, ties sharing
a rank, around you, pages of 50 as the list scrolls, signed-in players only. Opened from the Competitive page's LEADERBOARD
option button (CS2's own, shown here), over the Mode / Maps column. Stand-ins: no regions (LB "-"), no seasons, no
leaderboard names (Steam names as last seen), no party board.
- Regions: CS2's play menu has **no region picker** (mainmenu_play.ts has no ping / region / datacenter code). The one
  setting is Game > "Max Acceptable Matchmaking Ping" (settings layout DatacenterPingThresholdSlider):
  `mm_dedicated_search_maxping`, registered in matchmaking.dll (object 0x1801d7a10): default **150**, min **25**, max
  **350**, flags 0x80 (FCVAR_ARCHIVE), "Longest preferred ping to dedicated servers for games". When no server is within
  it: SFUI_QMM_ERROR_1_FailPingServer "... try increasing your 'Max Acceptable Matchmaking Ping' in 'Options > Game
  Settings' ...". Ours: the slider stores it (client/settings/index.js), the queue socket sends it, the matchmaker keeps
  it on the member and, with more than one region configured, a region over any member's max isn't searched (FailPingServer when none is left: lobby/region-pick.js; regions are ours, docs/MATCHMAKING.md "Regions and joining").

## Cooldowns in the database (ours)

penalties.js keeps each signed-in player's cooldown in ze_cooldowns (migration 008: reason, expires_at, tier, last_at:
the tier and the last abandon's time decide the next step up within a week) and logs every one in ze_cooldown_events;
net.js reads the running ones and the week's tiers back once the db is up (pen.load()). CS2's are the GC's.

## Still unread

- How the GC fills, orders and times out (not in any binary).
- The Premier pick / ban popup (popup_premier_pick_ban) the accept popup hands over to.
- The client's handler that turns GC2ClientAbandon into the notice, and the Expired popup's acknowledge
  (CompetitiveMatchAPI.ActionAcknowledgePenalty).
