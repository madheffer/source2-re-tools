# CS2's lobbies, invites, Looking to Play and the map pick

pak01 panorama (scripts/*.vts_c, styles/*.vcss_c source text; resource/csgo_english.txt the strings), 2026-11-16.
LobbyAPI, PartyBrowserAPI, FriendsListAPI, MatchDraftAPI are native: the rules behind them (an invite's lifetime, who
acts first in a draft, how the final map is chosen) are the GC's / Steam's, not in the client.
[friends.md](friends.md) has the friends list itself.

## Sending an invite (scripts/context_menus/context_menu_playercard.ts)

- Player card `invite` entry: icon `invite`, label `#tooltip_short_invite` "Invite", tooltip `#tooltip_invite` "Invite friend to play".
  - AvailableForItem: not playing a match (`GameStateAPI.IsLocalPlayerPlayingMatch`), not already in your lobby
    (`LobbyAPI.IsPartyMember`), not you, a purchased licence.
  - IsDisabled: the lobby's `game.apr` > 1 (Prime-restricted lobbies).
  - OnSelected: `FriendsListAPI.ActionInviteFriend(xuid, '')`, then `FriendInvitedFromContextMenu`, which marks the
    sender's tile (friendtile.ts `_SetInvited`: `#JsFriendInvited` visible; afterwards `FriendsListAPI.IsFriendInvited`).
- `join` (icon JoinPlayer): a joinable friend not already in your lobby or server; `watch` (watch_tv): a watchable one.
- Lobby's own invite button (party.ts): tooltip `#tooltip_invite_to_lobby` "Invite friends to play".
- Chat lines: `SFUI_Lobby_InviteFriendMessage` "Invited %s1 to lobby.", `SFUI_Lobby_PersonInvitedFriendMessage` "{s:s1} invited {s:s2}".

## Receiving one (scripts/friendslist.ts, friendlobby.ts, styles/friendlobby.vcss)

- No popup, no toast: `PanoramaComponent_PartyBrowser_InviteReceived` / `_InviteConsumed` rebuild `#JsIncomingInvites`
  at the top of the friends list (above the accordion): **the first invite only** (`PartyBrowserAPI.GetInviteXuidByIndex(0)`),
  a `friendlobby` tile of type `invited`.
- Tile (friendlobby.ts Init): leader's avatar and `#tooltip_friend_invited_you` "<b>Invite</b> from <b>{s:friendname}</b>";
  mode (`lobby-mode`: the game mode's nameID); maps (`lobby-maps`: up to four map group names, or `#SFUI_Groups_workshop`);
  one avatar slot per seat after the leader (`SessionUtil.GetMaxLobbySlotsForGameMode - 1`), empty ones
  `.friendlobby__slot--empty` (40 x 40, mapdraft/vote_box_png at .4 opacity); rating emblem (Premier, or Wingman for
  scrimcomp2v2); region flag.
- Join `#JsFriendLobbyJoinBtn` (tooltip `#tooltip_accept_invite` "Accept this invite"): sound `PanoramaUI.Lobby.Joined`,
  `PartyBrowserAPI.ActionJoinParty(leader)`. Hidden when already in that lobby.
- Close `FriendLobbyCloseButton` (tooltip `#tooltip_discard_invite` "Discard this invite"): sound `PanoramaUI.Lobby.Left`,
  `PartyBrowserAPI.ClearInvite(xuid)`.
- More than one: `#JsFriendLobbyCount` shows `#friends_lobby_count` "+ {s:lobby_count}" (the others); its button
  (`#tooltip_lobby_count` "View all lobby invites") opens context_menu_lobbies.xml listing all.
- Strings: `SFUI_Friends_Lobby_Invite` "<b>%s1</b> has invited you to play" (older notification line, unused by these
  scripts), `SFUI_Lobby_StatusInvited` "Invited".
- Lifetime: Steam's (until joined or discarded).

| Style | Value |
|---|---|
| `.friendlobby` | 365 px wide, flow down, .5 s transitions |
| `.friendlobby__join-btn` | positiveColor (#0F9D58), radius 2 px, padding 6 px, arrow image rotated 45 deg |
| `.friendlobby__row-avatars` | margin 8 px 0 8 px 12 px |
| `.friendlobby__slot` | margin 0 12 px (the first 24 px) |
| `.friendlobby-avatar__Image` | 40 px, 4 px white border on hover |
| `.friendlobby__text` | 12 px, 180 px |
| `.friendlobby__seperator` | 1 px rgba(255,255,255,0.068) at 93 % |

## Invite links

None of CS2's own: Steam's "Join game" / steam://joinlobby.

## Public lobbies (Looking to Play)

- No lobby browser: "Community Servers" opens Steam's server browser (popup_serverbrowser.ts: `steam://open/servers`,
  `player_nevershow_communityservermessage`).
- Friends list **Looking to Play** (`id-friendslist-section-broadcast`, advertising_toggle.ts): toggle
  `PartyListAPI.SetLocalPlayerForHireAdvertising(filter)` ("Look for Competitive": `advertising_for_hire_competitive`;
  title `advertising_for_hire_tooltip_title` "Look to Play", tooltip "Enables nearby players to invite you to their
  lobby"; in a lobby: "Look to Play is not available while you are in a lobby").
- Lobbies from `PartyBrowserAPI` as friendlobby tiles of type `nearby` / `friend` / `suggested`; join tooltip
  `#tooltip_join_public_lobby` "Join public lobby"; `SFUI_Lobby_GroupsNearby` "Nearby Public Lobby".
- Empty: `FriendsList_nodata_advertising_title` "Looking to Play", `FriendsList_nodata_advertising` "Couldn't find anyone
  near you looking to play at this time."

## The map pick (scripts/popups/popup_premier_pick_ban.ts, styles/popups/popup_premier_pick_ban.vcss)

| Phase (k_EMapVetoPickPhase_*) | Vote slots | Max time |
|---|---|---|
| 0 BeginDraftType1 | | 0 |
| 1 DecideWhoGoesFirst | | 0 (no timer) |
| 2 PickFirstOfTwoMaps | 1 | 15 s |
| 3 PickBothOtherMaps | 2 | 15 s |
| 4 PickLastOfTwoMaps | 1 | 10 s |
| 5 SelectingMap | | 5 s |
| 6 PickStartingSide | 1 | 5 s |
| 7 EndDraftType1 | | 5 s |

- `IsBanPhase()` returns false: today's Premier draft is all picks (the `_v2` strings).
- Every player of the acting team votes (`ActionPregameCastMyVote(phase, slot, voteId)`); winning votes are the GC's
  (`GetPregameWinningVotes`); a tile shows its voters' avatars and "Pick" on the winning ones.
- Phase bar: `section-time` (seconds left), fills `100 - floor(left / max * 100)` %, refreshed every 0.5 s; under 5 s
  left, sound `UI.Premier.CounterTimer`. New phase: `UI.Premier.MapsLocked` (phases 1-4), `UI.Premier.SubmenuTransition` (5 on).
- Labels `matchdraft_phase_<n>[_v2]`: 0_v2 "Starting Map Selection", 2_v2 "Pick 1 Map", 3_v2 "Pick 2 Maps", 4_v2 "Pick
  1 Map", 5_v2 "Selecting Map", 5 "Pick Starting Team", 6 "Start Match" (the bar's index > 5 uses n - 1).
- Title `matchdraft_phase_action_<n>[_v2]` ("Pick {d:maps}/1 Map To Play", green: positiveColor), or waiting
  `matchdraft_phase_action_wait_<n>[_v2]` ("Waiting For Opponent To Pick 1 Map", "Waiting For Map Selection", "Waiting
  For Opponent To Pick A Starting Side").
- Picked map's bottom line `matchdraft_pick_your` "Your Pick" / `matchdraft_pick_their` "Their Pick"; end
  `matchdraft_final_map` "Playing On {s:mapname}", `matchdraft_phase_starting_team` "Starting Match as {s:teamname}".
- Phase 5: a random flash over the picked maps (`.premier-pickban-phase-5 .premier-pickban-pick`: 0.76 s x 5) before the
  chosen one stays: the GC picks one of the picked maps; the client only animates it.
- Side tiles: CT rgb(150,200,250), T #eabe54, the player's equipped agent's image.
- Styles: `.premier-pickban__progress` 96 px; sections 284 x 16 px bars (black, inner white, 1 s width transition); the
  active pick bar washed positiveColor; `--pre` bars scaleY(.25); map buttons 280 px.
- Not in the client: who acts first, the winning vote, the final map, who picks the side. Premier's pool is 7 maps.
