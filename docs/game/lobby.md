# CS2's lobbies, invites, Looking to Play and the map pick (pak01 panorama, 2026-11-16)

Read from CS2's pak01 (panorama/scripts/*.vts_c and styles/*.vcss_c hold their source text; resource/csgo_english.txt the
strings), dumped with a scratch copy of tools/dump-vpk-file.mjs. What these panels show comes from Valve's GC and Steam
(LobbyAPI, PartyBrowserAPI, FriendsListAPI, MatchDraftAPI are native): the rules behind them (an invite's lifetime, who
acts first in a draft, how the final map is chosen) are not in the client and are marked as ours below. Used by
server/cs2web/lobby/custom.js, lobby-invites.js, lobby-veto.js, lobby/friends.js and client/home/lobby/, friends/.
friends.md has the friends list itself.

## Sending an invite (scripts/context_menus/context_menu_playercard.ts)

- The player card's `invite` entry (icon `invite`, label `#tooltip_short_invite` "Invite", tooltip `#tooltip_invite`
  "Invite friend to play"): AvailableForItem = not playing a match (`GameStateAPI.IsLocalPlayerPlayingMatch`), not
  already in your lobby (`LobbyAPI.IsPartyMember`), not you, and a purchased licence. IsDisabled when the lobby's
  `game.apr` > 1 (Prime-restricted lobbies). OnSelected: `FriendsListAPI.ActionInviteFriend(xuid, '')`, then the
  `FriendInvitedFromContextMenu` event, which marks the sender's tile (friendtile.ts `_SetInvited`: `#JsFriendInvited`
  visible; afterwards `FriendsListAPI.IsFriendInvited`).
- `join` (icon JoinPlayer): a joinable friend not already in your lobby or server; `watch` (watch_tv): a watchable one.
- The lobby's own invite button (party.ts): tooltip `#tooltip_invite_to_lobby` "Invite friends to play".
- Chat lines: `SFUI_Lobby_InviteFriendMessage` "Invited %s1 to lobby.", `SFUI_Lobby_PersonInvitedFriendMessage`
  "{s:s1} invited {s:s2}".

## Receiving one (scripts/friendslist.ts, friendlobby.ts, styles/friendlobby.vcss)

- No popup and no toast in CS2's client: `PanoramaComponent_PartyBrowser_InviteReceived` / `_InviteConsumed` rebuild
  `#JsIncomingInvites` at the top of the friends list (above the accordion): **the first invite only**
  (`PartyBrowserAPI.GetInviteXuidByIndex(0)`), as a `friendlobby` tile of type `invited`.
- The tile (friendlobby.ts Init): the leader's avatar and `#tooltip_friend_invited_you` "<b>Invite</b> from
  <b>{s:friendname}</b>"; the lobby's mode (`lobby-mode`: the game mode's nameID) and maps (`lobby-maps`: up to four
  map group names, or `#SFUI_Groups_workshop`); one avatar slot per seat after the leader
  (`SessionUtil.GetMaxLobbySlotsForGameMode - 1`), empty ones `.friendlobby__slot--empty` (40 x 40,
  mapdraft/vote_box_png at .4 opacity); the rating emblem (Premier, or Wingman for scrimcomp2v2); the region flag.
- The join button `#JsFriendLobbyJoinBtn` (tooltip `#tooltip_accept_invite` "Accept this invite"): sound
  `PanoramaUI.Lobby.Joined`, `PartyBrowserAPI.ActionJoinParty(leader)`. Hidden when you're already in that lobby.
- The close button `FriendLobbyCloseButton` (tooltip `#tooltip_discard_invite` "Discard this invite"): sound
  `PanoramaUI.Lobby.Left`, `PartyBrowserAPI.ClearInvite(xuid)`.
- More than one invite: `#JsFriendLobbyCount` shows `#friends_lobby_count` "+ {s:lobby_count}" (the others), its button
  (`#tooltip_lobby_count` "View all lobby invites") opens context_menu_lobbies.xml listing them all.
- Styles: `.friendlobby` 365 px wide, flow down, .5 s transitions; `.friendlobby__join-btn` positiveColor (#0F9D58),
  radius 2 px, padding 6 px, its arrow image rotated 45 deg; `.friendlobby__row-avatars` margin 8 px 0 8 px 12 px;
  `.friendlobby__slot` margin 0 12 px (the first 24 px); `.friendlobby-avatar__Image` 40 px with a 4 px white border
  on hover; `.friendlobby__text` 12 px, 180 px; `.friendlobby__seperator` 1 px rgba(255,255,255,0.068) at 93 %.
- Strings worth having: `SFUI_Friends_Lobby_Invite` "<b>%s1</b> has invited you to play" (an older notification
  line, unused by these scripts), `SFUI_Lobby_StatusInvited` "Invited".
- An invite's lifetime is Steam's (until joined or discarded; not in the client). **Ours**: an invite lives as long
  as its signed token (10 minutes) and its lobby; a new invite from the same friend replaces the old.

## Invite links

CS2 has none of its own (Steam's "Join game" / steam://joinlobby). **Ours**: a signed, expiring token in the link
(`?lobby=<token>`, HMAC-SHA256 over the lobby's id, an expiry and a nonce: lobby-tokens.js), refused once the lobby
closes; the typed 6-character code stays, rate-limited per address.

## Public lobbies (Looking to Play, the friend lobbies)

- CS2 has no lobby browser: "Community Servers" opens Steam's own server browser (popup_serverbrowser.ts:
  `steam://open/servers`, `player_nevershow_communityservermessage`). The nearest in CS2 itself is the friends list's
  **Looking to Play** section (`id-friendslist-section-broadcast`, advertising_toggle.ts): a toggle
  `PartyListAPI.SetLocalPlayerForHireAdvertising(filter)` ("Look for Competitive": `advertising_for_hire_competitive`;
  title `advertising_for_hire_tooltip_title` "Look to Play", tooltip "Enables nearby players to invite you to their
  lobby", disabled in a lobby: "Look to Play is not available while you are in a lobby"), and lobbies listed by
  `PartyBrowserAPI` as friendlobby tiles of type `nearby` / `friend` / `suggested` with the join button's tooltip
  `#tooltip_join_public_lobby` "Join public lobby" and `SFUI_Lobby_GroupsNearby` "Nearby Public Lobby". Empty:
  `FriendsList_nodata_advertising_title` "Looking to Play", `FriendsList_nodata_advertising` "Couldn't find anyone near
  you looking to play at this time."
- **Ours**: a host marks the lobby Public; PLAY > Private Lobby lists the public ones as friendlobby-style tiles (host
  avatar and name, mode, map, a slot per seat, the green join button), with CS2's empty text.

## The map pick (scripts/popups/popup_premier_pick_ban.ts, styles/popups/popup_premier_pick_ban.vcss)

- Phases (k_EMapVetoPickPhase_*): 0 BeginDraftType1, 1 DecideWhoGoesFirst, 2 PickFirstOfTwoMaps, 3 PickBothOtherMaps,
  4 PickLastOfTwoMaps, 5 SelectingMap, 6 PickStartingSide, 7 EndDraftType1. `IsBanPhase()` returns false: today's
  Premier draft is all picks (the `_v2` strings).
- Vote slots a phase (GetNumVoteSlots): 2 -> 1, 3 -> 2, 4 -> 1, 6 -> 1. Every player of the team acting votes
  (`ActionPregameCastMyVote(phase, slot, voteId)`); the team's winning votes are the GC's
  (`GetPregameWinningVotes`); a tile shows its voters' avatars and "Pick" on the winning ones.
- Timers (GetMaxTimeForPhase): phase 2 15 s, 3 15 s, 4 10 s, 5 5 s, 6 5 s, 7 5 s (others 0: phase 1 has no timer in
  this draft). The phase bar shows `section-time` (seconds left) and fills `100 - floor(left / max * 100)` %, refreshed
  every 0.5 s; under 5 s left, sound `UI.Premier.CounterTimer`. A new phase: `UI.Premier.MapsLocked` (phases 1-4),
  `UI.Premier.SubmenuTransition` (5 on).
- Labels: `matchdraft_phase_<n>[_v2]` (0_v2 "Starting Map Selection", 2_v2 "Pick 1 Map", 3_v2 "Pick 2 Maps", 4_v2 "Pick
  1 Map", 5_v2 "Selecting Map", 5 "Pick Starting Team", 6 "Start Match", the bar's index > 5 using n - 1); the title
  `matchdraft_phase_action_<n>[_v2]` ("Pick {d:maps}/1 Map To Play", green: positiveColor) or, waiting,
  `matchdraft_phase_action_wait_<n>[_v2]` ("Waiting For Opponent To Pick 1 Map", "Waiting For Map Selection",
  "Waiting For Opponent To Pick A Starting Side"); a picked map's bottom line `matchdraft_pick_your` "Your Pick" /
  `matchdraft_pick_their` "Their Pick"; the end `matchdraft_final_map` "Playing On {s:mapname}",
  `matchdraft_phase_starting_team` "Starting Match as {s:teamname}".
- Phase 5 plays a random flash over the picked maps (`.premier-pickban-phase-5 .premier-pickban-pick`: 0.76 s x 5) before
  the chosen one stays: the GC picks one of the picked maps; the client only animates it. Side tiles: CT
  rgb(150,200,250), T #eabe54, the player's equipped agent's image.
- Styles: `.premier-pickban__progress` 96 px, sections 284 x 16 px bars (black, inner white, 1 s width transition),
  the active pick bar washed positiveColor, `--pre` bars scaleY(.25); map buttons 280 px.
- **Ours** (the GC's part): which team acts first (a coin flip), the winning vote (the most votes, a tie or no votes at
  random among them), the final map (one of the picked at random), which team picks the side (the team that didn't
  make the last pick). The pool is COMP_MAPS (3 maps today, not Premier's 7): the phases' pick counts are capped at the
  maps left, so with 3 maps phase 2 picks 1, phase 3 picks 2 and phase 4 is skipped.
