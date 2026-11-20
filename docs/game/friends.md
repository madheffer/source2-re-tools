# Friends list, friend codes, Recent Teammates, Looking to Play

client_20261112. pak01 panorama: layout/mainmenu.xml, scripts/mainmenu.ts, layout/friendslist.xml, scripts/friendslist.ts,
styles/friendslist.vcss, friendtile.*, context_menus/context_menu_playercard.*, popups/popup_add_friend.*,
friend_advertise_tile.ts; resource/csgo_english.txt.

## Functions

| Address | Module | What |
|---|---|---|
| 18106f180 | client | MyPersonaAPI.GetFriendCode (registered at 18108e25e): a cached string, made once by 180f88150 from the local account id |
| 180fb9280 | client | FriendsListAPI.GetXuidFromFriendCode (registered at 180fce1fc): skips leading whitespace (jump table on '\t'..' '), 180f87f90, then the SteamID64 = the local user's high word + the account id; "" when 0 |
| 180f88150 | client | encode(account id, buf) -> pointer |
| 180f87f90 | client | decode(text) -> account id |
| 180f88570 | client | parse a 15-char code into a u64 |
| 18106d430 | client | TeammatesAPI.GetCoPlayerTime (registered at 181090d72) |

## Constants

| Value | What |
|---|---|
| `ABCDEFGHJKLMNPQRSTUVWXYZ23456789` (0x181ce65f0) | ALNUM |
| 181ce6620 / 181ce6614 | "AAAA-%.*s" / "AAAA-" |
| IAT 181aa7010 | tier0 MD5_ProcessSingleBuffer |
| 0x4353474f_00000000 | "OGSC" high word over the id |
| 0x1194 (4500) s | GetCoPlayerTime "Just Now" limit |

## Friend code encode (180f88150)

1. MD5 over the 8 bytes of `0x4353474f_00000000 | id` little-endian (id then "OGSC"); h = digest byte 0.
2. `r = 0; for i in 0..7: r = ((r << 4) | (id >> 4i & 15)) << 1 | (h >> i & 1)` (40 bits); `n = byteswap64(r)`.
3. 13 digits ALNUM[n & 31], `n >>= 5`, '-' after the 4th and 9th.
4. Returns buf + 5 when it starts "AAAA-" (always, for 40 bits), else a fixed empty string.

## Decode (180f87f90)

1. CBufferString "AAAA-%.*s" with precision 10; 180f88570 parses it.
2. Top 24 bits must be 0 (`& 0xffffff0000000000`); the rounds undone (low bit = hash bit i, then the nibble); id 0 -> 0.
3. MD5 byte 0 must equal the 8 hash bits, else 0.

Parse (180f88570): length 15, '-' at 4 and 10, 13 characters each in ALNUM (via strchr: upper case only), a base-32 big number into a u64.

Checked: tools/re/game/friendcode_oracle.py runs 180f88150 and 180f87f90 under Unicorn (MD5 through hashlib,
CBufferString::AppendFormatV stubbed inline at +4 bit 30 / +8) over 514 account ids and 1493 strings.

## Sidebar (layout/mainmenu.xml, scripts/mainmenu.ts)

- `#JsMainMenuSidebar.mainmenu-sidebar` in the `MainMenuFriendsAndParty` CSGOBlurTarget: `#mainmenu-sidebar__blur-target` (`onmouseover="MainMenu.ExpandSidebar()" onmouseout="MainMenu.MinimizeSidebar()"`) and an 8px `__seperator`. `_InitFriendsList` creates `JsFriendsList` in the blur target and loads layout/friendslist.xml.
- `ExpandSidebar(AutoClose)`: removes `mainmenu-sidebar--minimized` (sound `sidemenu_slidein` if it was), dispatches SidebarIsCollapsed false, undims the background; AutoClose schedules MinimizeSidebar after 1 s.
- `MinimizeSidebar`: not while `_m_sideBarElementContextMenuActive`; adds the class (sound `sidemenu_slideout`).
- `SidebarContextMenuActive(b)`: sets that flag, then 0.25 s later minimizes unless hovered.
- mainmenu.vcss: `.mainmenu-sidebar { flow-children: left; horizontal-align: right; height: 100%; z-index: 3; transition position .25s ease-in-out }`, `--minimized { position: 256px 0 0 }`, `--hidden { 400px }`; `#mainmenu-sidebar__blur-target { width: friendstilewidth (320px); background-color: blurBackgroundColor rgba(255,255,255,.01); opacity .99 }`; `__seperator { width 8px; gradient(linear, 100% 0%, 0% 0%, from(#00000066), to(#00000000)) }`.

## The list (friendslist.xml / .ts / .vcss)

- Order: `#PartyList` (the lobby's members, hidden alone), `#JsIncomingInvites` (the first lobby invite as a friendlobby tile), then the accordion `#id-friendslist-accordian`: RadioButtons (group `friends_accordian`) Friends (`#id-friendslist-section-friends`: player.vsvg, `#SFUI_Lobby_FriendsListerTitle`, AddFriendBtn addplayer.vsvg "Add friend"), Looking to Play (`-broadcast`), Recent Teammates (`-recent`: recent.vsvg, `#SFUI_Friends_Recent`), Requests (`-invite`: invite.vsvg, `#SFUI_Friends_Requests`, `--noborder`).
- Header: a 64x64 icon container with the 22px icon and a `btn_alert.xml` counter (`text-only` on Friends, Looking to Play and Recent; the orange badge on Requests); label `stratum-bold-condensed fontSize-ml (20px) text-letterspace-2px fontcolor-basetext`.
- List: `rgba(0,0,0,0.6)`, linemap_png at 5 % (100% 50%), a JSDelayLoadList of 320 x 58 items, or the NoData snippet (info.vsvg 22px at 21px; text at 64px: title 24px, body 14px / 20px) with `FriendsList_nodata_<friends|recents|requests|advertising>[_title]`.
- `_UpdateSectionContent`: count = alerts_count if given else count; `_ShowHideCounter` (`hide-notification` at 0, else `alert_value`); `hide_if_empty` (Requests) hides the section at count < 1; only the active section fills.
- `_SetSectionHeight`: closed sections' lists 0 px; the active one the panel's height minus the closed headers, the party list and the invites.
- Counts: Friends `FriendsListAPI.GetCount()`; Requests `GetFriendRequestsCount()`, alerts `GetFriendRequestsNotificationNumber()`; Recent `TeammatesAPI.GetCount()`; Looking to Play `PartyBrowserAPI.GetResultsCount()`. Opening Recent calls `TeammatesAPI.Refresh()` (loading bar while `GetSecondsAgoFinished() < 0`).
- Events: GC_Hello (all), FriendsList_RebuildFriendsList (friends), Teammates_Refresh (recent), PartyBrowser_Refresh, FriendsList_NameChanged (one tile), PartyBrowser_InviteReceived / InviteConsumed (the invite tile).
- The list holds the online friends (nodata: "Your friends are not online currently"); order native (FriendsListAPI.GetXuidByIndex).

## A tile (friendtile.xml / .ts / .vcss)

- `.friendtile` 58px x 320px; `#JsFriendTileStatusBg` 4px x 96% additive, `.ingame` positiveColor #0F9D58; avatar 40px (margin-left 12px, shadow #0000005d 0 2px 8px 2); `__status` margin-left 14px, name 16px bold stratum2 white with 1px 1px 1px #00000091, status 14px stratum-light, letter-spacing 1px. `:Hover` gradient white to 1.25 %, #ffffff40, #30303080 at 2.5 %, to #30303000; sounds sidemenu_rollover / sidemenu_select.
- `_SetStatusBar`: bucket = GetFriendStatusBucket; a non-friend recent teammate in CS (`TeammatesAPI.GetCoPlayerInCSGO`) counts as PlayingCSGO, any other non-friend Offline.
- `_SetStatus`: a recent tile shows `GetCoPlayerTime(xuid)` unless empty, else `GetFriendStatus(xuid)`. Join / watch / invited icons per IsFriendJoinable / IsFriendWatchable / IsFriendInvited. The button (and its context menu event) opens context_menu_playercard.xml with `xuid` and `type`.

## Player card menu (context_menu_playercard.ts)

- playercard.xml card, a separator, then the entries whose `AvailableForItem(xuid)` holds, five a row: an IconButton with `icons/ui/<icon>.svg`, label `#tooltip_short_<name>`, tooltip `#tooltip_<name>` (or `#tooltip_disabled_<name>` when IsDisabled).
- Order: invite, join, watch, steamprofile, changeclantag, petbook, kick_from_lobby, leave_lobby, message, trade, friendaccept, friendignore, cancelinvite, removefriend, request, editprofile, changecolor, mute, report, commend, borrowmusickit, stopborrowmusickit, copycrosshair, viewaddon, kick_player.
- friendaccept / friendignore when the bucket is AwaitingLocalAccept, cancelinvite when AwaitingRemoteAccept (`SteamOverlayAPI.InteractWithUser(id, 'friendrequestaccept' | 'friendrequestignore' | 'friendremove')`); removefriend only on the Perfect World launcher (not self, no request either way; Steam's own UI unfriends otherwise); request ('friendadd') when not a friend, not self, no request.
- context_menu_playercard.vcss: contextMenuBackground #262626, radius 3px, shadowOffset; info 384px; separator 1px rgba(124,124,124,.15); buttons on rgba(0,0,0,.466), IconButton margin 8px, label 12px Stratum2 TF 64px wide.

## Add Friend popup (popup_add_friend.xml / .ts)

- `#AddFriend_Title`, a TextEntry (placeholder XXXXX-XXXX, upper case) with `JSFriendValidIcon` (check.vsvg 24px, opacity .04, 1 when valid), `#JsFriendCodeNotFound` ("No friend found for code '{s:code}'"), `#JsFriendCodeFound` (invite.vsvg 28px washed #3E3E3E that fades in on send, plus a friendtile 450px wide, radius 5px, rgba(0,0,0,.445)), buttons Send Friend Request (disabled until found), Copy Your Code (tooltip: your code; click: CopyTextToClipboard + "Copied your code to clipboard"), Cancel.
- `OnEntrySubmit` on every change: `FriendsListAPI.GetXuidFromFriendCode(text.toUpperCase())`; found: the tile, Send enabled; else the not-found line. `OnSendInvite`: `InteractWithUser(xuid, 'friendadd')`, the popup closes.

## Recent Teammates (TeammatesAPI)

- GetCoPlayerTime (18106d430): finds the xuid's record; `seconds = now + [this+0x40] - [this+0x30] - [rec+8]` (record time); under 0x1194 returns `#SFUI_Date_Format_JustNow`; else a localize interface's vtable +0x100 with (r8 = 8, r9 = the record's time) into a CBufferString, returns its text.
- The list comes from the GC (`k_EMsgGCCStrike15_v2_Account_RequestCoPlays`, CMsgGCCStrike15_v2_Account_RequestCoPlays_Player).
- Strings: SFUI_Date_Format_JustNow "Just Now", _Today, _Yesterday.

## Statuses (FriendsListAPI.GetFriendStatus / GetFriendStatusBucket)

- Buckets the scripts compare: PlayingCSGO, AwaitingLocalAccept, AwaitingRemoteAccept, Offline (and Steam's online / away / snooze).
- Strings: SFUI_Lobby_StatusOnline / Away / Snooze / Offline / InLobby / AwaitingLocalAccept "Wants to be Your Friend" / AwaitingRemoteAccept "Friend Request Sent"; rich presence `SFUI_Lobby_StatusRichPresence_<mode>_<lobby|game|community|watch|review>` (casual_game "Playing Casual", casual_community "Community Casual", deathmatch_game "Playing Deathmatch", competitive_game "Competitive", competitive_lobby "In Competitive Lobby", ...).
- "[ 10 : 12 ] Competitive Dust II" is Steam's rich presence display string for app 730, not in pak01. Map names `#SFUI_Map_<map>`.

## Looking to Play

- Section `#id-friendslist-section-broadcast`: icon advertising_icon.xml (class `advertising-active` while you advertise), label `#SFUI_Lobby_StatusLookingToPlay`; slider_toggle `#id-friendslist-broadcast-toggle`; per-mode filter RadioButtons (competitive / scrimcomp2v2 / cooperative, `data-type`, visible per `PartyListAPI.IsPlayerForHireAdvertisingEnabledForGameMode`), a refresh button, a loading bar (`PartyBrowserAPI.GetProgress()` 1..100 as its width), the list of friend_advertise_tile.xml.
- friendslist.ts: filter in setting `ui_nearbylobbies_filter`; `SetLobbiesTabListFilters(mode)` -> AdvertisingToggle.OnFilterPressed; `RefreshLobbyListings` -> `PartyBrowserAPI.SetSearchFilter(mode, '')` + `Refresh()`; the tab's `toggle-active` on the advertised mode (`AdvertisingToggle.GetAdvertisingSetting()`); counts `PartyBrowserAPI.GetResultsCount()`, items `GetXuidByIndex(i)`; event PanoramaComponent_PartyBrowser_LocalPlayerForHireAdvertisingChanged.
- friend_advertise_tile.ts: per lobby `GetPartySessionSetting(xuid, 'game/mode' | 'game/apr' (Prime) | 'game/loc' (country) | 'game/ark' (rating: / 10, Wingman's or Premier's emblem))`, the leader `GetPartyMemberXuid(xuid, 0)`'s name and avatar (context menu type 'nearby'), an invite button (`FriendsListAPI.ActionInviteFriend`) not on yourself.

## Unread

- CSGOBlurTarget's blur radius and any darkening.
- The friends list order (native GetXuidByIndex).
- GetCoPlayerTime's localize call (localize.dll).
- Which matches fill Recent Teammates and its count.
- The rich presence token behind "[ 10 : 12 ] Competitive Dust II".
- scripts/advertising_toggle.ts; layout/friend_advertise_tile.xml's styles; playercard.xml (level, rank, XP bar, medals).
