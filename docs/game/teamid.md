# The overhead team id and the decorated player name

client_20261015 (decompiled), client_20261105 (disassembly: the name provider), server_20261105 (chat); pak01
csgo_english.txt, hudreticle.vxml / .vcss, csgostyles.vcss, scoreboard layout. CS2Fixes adminsystem.cpp:255, 1775.

## Functions

| Address | Module | What |
|---|---|---|
| 180dbe2f0 | client 11-05 | registers the "player_name" dialog-variable handler |
| 180dbcec0 | client 11-05 | `{g:player_name:<modifiers>:<slot>}` handler |
| 180dbcd10 | client 11-05 | modifier parser (table 181cbeb00) |
| 180f9efd0, 180f9f050, 180f9f010, 181077650 | client 11-05 | party / friends / draft / lobby providers (`CDecoratedPlayerNameProviderVia*Api`) |
| 180acc550 | client 11-05 | controller by slot |
| 1809049b0 | client 11-05 | IDecoratedPlayerNameProvider::GetDecoratedPlayerName2(provider, CBufferString out, flags, append) |
| 180c69020 | client 11-05 | (table 182575d38, appended text, 3, vfn 0x30()) over the result (unread) |
| 18088b8d0 / 18088b810 / 18088b8a0 / 18088ae20 / 18088ae10 / 18088ae30 / 18088ae00 / 18088adc0 | client 11-05 | controller provider vfns (table below) |
| 180d39230, 18088e650 | client 11-05 | cl_sanitize gates (unread) |
| 180945990 | client 11-05 | vfn 0x30's target (unread) |
| 1815e43f0 | client 11-05 | player slot + 1 |
| 180e8b2f0 | client 11-05 | CCSGO_HudDeathNotice player_death: calls at 180e8b684 / 180e8b70d / 180e8b797 (attacker, assister, victim) |
| 18089df60 / 18088ca80 | client 11-05 | m_bControllingBot / m_hOriginalControllerOfCurrentPawn's entity |
| 180e87850 | client 11-05 | death notice name: cl_deathnotices_show_numbers 1 / 2 replace / prefix with the team counter slot digit |
| 180cecc30 / 180cee8c7 | client 11-05 | game events: player_disconnect branch (flags 0) |
| 180ceebb2 | client 11-05 | seasoncoin_levelup (flags 0) |
| 180d119c0 | client 10-15 | item found line (cases.md; flags 0) |
| 180fa1899, 180fb5767, 180fdcd54 / 180fdce2d (kick vote), 180ff2539, 180eb6622 (target id), 180ed40e7, 180eda6b9 | client 11-05 | other GetDecoratedPlayerName2 callers (flags unread) |
| 180cfab90 | server | say / say_team (controller, args, team only, ...) |
| 1809268f0 | server | CCSGameRules vfn 0x2c0: the chat token |
| 180926b60 | server | place name |
| 180ad2ac0 | server | spectator test |
| 180911fe0 | server | (gamerules, listener, sender, team only) chat can hear |
| 1809131f0 | server | (listener, sender, team only, sv_allchat): the voice check's base (third argument this flag, fourth the "other team too" switch) |
| 180fd5110 | server | pair block |
| 180feb3e0 | server | SayText2 (filter, sender, mode, token, name, text, place): chat = `mode - 1 < 2`, second byte `mode == 2` |
| 180cfb101 / 180cfb1c5 | server | say's mode = eax + 1 (eax 0 or 1 by the team-only path, unread) |
| 180feb640 | server | raw "name: text" |
| 180a924f0 | server | controller connect |
| 180b553d0 | server | the name |
| 180fe9cf0 | server | ClientPrintAll(1, "#Cstrike_TitlesTXT_Game_connected", name) at HUD_PRINTNOTIFY |
| 180103d00 | server | registers sv_allchat |
| 1800a58f0 | server | registers sv_chat_proximity |
| 180ceaab0 | client 10-15 | game event handler: returns at once for player_connect, player_changename; player_connect_full posts a panorama event |
| 180b43a60 | client 10-15 | disconnect skip test (unread) |
| 180903100 | client 10-15 | GetDecoratedPlayerName2 in that build |
| 1812afec0 -> 18127ff60 | client 10-15 | disconnect reason's `(network_connection_token)` option string |
| 1811a5440 | client 10-15 | add a chat line |
| 1811a5550 | client 10-15 | add a SayText line |
| 180eb4120 | client 10-15 | chat colour (code, sender's team) |
| 18118e640 | client 10-15 | rarity colours (vfn 0xc0 with code - 9) |
| 180eb3e80 | client 10-15 | a line's name (place " @ " in #40ff40 for the same team, teammate colour dot) |
| 180c09410 | client 10-15 | EmitSound (HudChat.Message) |
| 1811ac670 / 1811a7ca0 | client 11-05 / 10-15 | RadioText handler (hooked by 1811a4470 HookMessage, its plVar[7]) |
| 1811acf90 / 1811a85c0 | client 11-05 / 10-15 | SayText2 handler (CHudChatDelegate vtable 0x181d26518 slot 12, 0x60) |
| 1811ad6f0 / 1811a8d20 | client 11-05 / 10-15 | SayText handler (slot 11, 0x58) |
| 180c0c0b0, 180c12010 | client 10-15 | mute tests (sender) |
| 1800f2550 | client 11-05 | registers cl_clutch_mode |
| 180c77710, 180c786b0, 180d375c0 | client | other cl_clutch_mode readers (unread) |
| 180e9f9b0 | client 10-15 | CCSGO_HudReticle constructor (panels, style symbols) |
| 180eaf7c0 | client 10-15 | reticle per frame |
| 180eb4df0 | client 10-15 | who is shown (an entry each), alpha, scale |
| 180eb4260 | client 10-15 | + the #TargetID label |
| 180ed3610 | client 10-15 | voice bit (unread) |
| 180ed28e0 | client 10-15 | entries -> panels |
| 180ed3150 -> 180ecb3d0 | client 10-15 | placement (root, Content, position + (0, 0, 9), scale) |
| 180ed0210 | client 10-15 | pings |
| 180ea6a80 | client 10-15 | panel creation (clears inline wash-color of [11], [12], [4], [5]) |
| 180ed10b0 | client 10-15 | extra info (entry, _, name shown) |
| 180759930 | client 10-15 | money mode test |
| 1808a44a0, 180889c80, 180889bd0 | client 10-15 | teammate colours (teammate-colors.md) |
| 1817b5650 | client 10-15 | opacity -> style vfn 0xa8 |
| 180952970 | client 10-15 | bone index by name token (pawn, hash) |
| 18093f490 | client 10-15 | bone world position |
| 180c19db0 | client 10-15 | project to screen |
| 180508d20 / 180508d30 | client 10-15 | the root's UI scale |

## Fields

| Offset | Field |
|---|---|
| controller +0x810 | IDecoratedPlayerNameProvider sub-object (vtable 181c11e28) |
| controller +0x3f4 | m_fFlags (0x100 bot) |
| controller +0x388 | server: bit 0x100 bot |
| controller +0x6f4 | connected: 0 or 3 |
| controller +0x878 / +0x880 | m_sSanitizedPlayerName / m_sSanitizedClanTag |
| controller +0x920 | m_bControllingBot |
| controller +0x950 | m_hOriginalControllerOfCurrentPawn |
| gamerules +0x11c | 4 / 5: everyone counts as alive |
| pawn +0x3e7 | team (reticle) |
| pawn +0x34c | m_iHealth |
| pawn +0x14bc | controller (the money: int +0x40 of the object at controller +0x818; unnamed) |
| pawn +0x1e9a | with "not occluded": +9 bit 4 |
| hud +0x78 / +0x80 | entries count / data (0x88 each) |
| hud +0x90 / +0x98 | panel sets (0x70 each) |
| RadioText +0x60 / +0x6c | a string / an int |
| SayText2 +0x48 / +0x50..0x68 / +0x70 / +0x74 | messagename / param1..4 / chat / entityindex |
| SayText +0x48 / +0x50 / +0x54 | text / chat / entityindex |

Entry (0x88):

| Offset | |
|---|---|
| +0x00 | pawn handle |
| +0x04 | team |
| +0x08 | bits: 1 seen this frame, 2 name shown, 4 extra info changed, 8 weapons shown, 0x10 primary shown, 0x20 / 0x40 icons changed, 0x80 defuser |
| +0x09 | bits: 1 C4, 2 talking (chat icon), 4 defusing icon |
| +0x0c | position (12 bytes) |
| +0x18 | extra info kind + 1 (1 health, 2 money) |
| +0x20 | extra info token |
| +0x28 / +0x2c | health percent / money (-1 unused) |
| +0x78 / +0x7c | alpha / last applied alpha |
| +0x80 | scale |

Panels: [0] PlayerID root, [1] ContentParent, [2] Content, [3] JsNameContainer, [4] JsName, [5] JsExtraInfo,
[6] Weapons, [7] WeaponDefuser, [8] WeaponC4, [9] WeaponGrenades, [10] WeaponPrimary, [11] ArrowIcon, [12] ChatIcon,
[13] DefusingIcon.

## Constants

| Value | What |
|---|---|
| sv_clantags_enabled 1 | flags 0x82000, "Show players' clan tags in their names." |
| cl_playerslot_in_names 0 | |
| cl_show_clan_in_death_notice 1 | |
| cl_sanitize_player_names 0 | |
| cl_deathnotices_show_numbers 0 | |
| sv_allchat 1 | "Players can receive all other players' text chat, no death restrictions" |
| sv_chat_proximity -1 | |
| cl_clutch_mode 0 | handle 0x1825c3c90 (+0x58), flags 0x80000, "Silence voice and other distracting sounds until the end of round or next death." |
| 18253d104 | static dropping clan tags: tier0 lookup by hash 0xcdbd1292 (a command-line switch) |
| 182533390 | debug cvar: vfn 0 / 0x10 return "WWWWWWWWWWWWWWWW" |
| 10-15 0x181bb0ff4 | 5-char constant: param4 equal to it skips the mute (unread) |
| DAT_1825651d0 +0x40 | mode flag for money |
| 182579058 | cl_teamid_overhead_colors_show |
| 0xffdcdcdc | talking chat icon wash |
| 0x88319dad / 0x57320e21 | tokens "ValveBiped.Bip01_Head" / "head_0" |
| 0x51cda125 / 0x387f108e | tokens "player_slot" / "player_health" |
| MurmurHash2, seed 0x31415926, lowercased | CUtlStringToken hash |
| HudChat.Message | sounds/common/talk.wav, volume 0.8, mixgroup UI; emitted with entity -1, volume 1.0 (0x3f800000), sound level 100, flags byte `& 0xe1 | 1` |

## Decorated name

Modifier words (181cbeb00: 9 entries of 0x18, name pointer, flag +0xc, "clear instead" byte +0x10); none -> 7:

| word | flag | word | flag |
|---|---|---|---|
| `oc` | 1 | `party` | 0x20 |
| `clan` | 1 | `friend` | 0x40 |
| `pupp` | 4 | `draft` | 8 |
| `name` | 2 | `accept` | 0x80 |
| `bot` | 0x10 | | |

Handler: flags 0x20 / 0x40 / 8 / 0x80 take a xuid and their provider; else the variable is a slot:
`GetDecoratedPlayerName2(controller + 0x810, out, flags, true)`.

GetDecoratedPlayerName2:
1. flags 0 -> 0x12. `bot = vfn 0x18() || vfn 0x20()`. Flag 0x10 and bot: `flags = (flags & ~0x10) | 1`.
2. Clan tag (1) dropped when not bot and (sv_clantags_enabled 0 or 18253d104 set).
3. Puppeteer (4) dropped when vfn 0x28() or not vfn 0x18().
4. Order: `#FullPlayerNameOrder_Default:f`, or `#FullPlayerNameOrder_PlayerSlot:f` with cl_playerslot_in_names.
5. Parts { flag, key, wrapper, getter } 0x58 apart: 1 `clantag` `#DecoratedPlayerName_ClanTag:f` vfn 8; 4 `puppeteer`
   `#DecoratedPlayerName_Puppeteer:f` vfn 0; 2 `original_controller` `#DecoratedPlayerName_ControllerName:f` vfn 0x10.
   Flag off or getter null / "": key -> "". Else the wrapper localized with `{s:value}`.
6. cl_playerslot_in_names: `playerslot` = vfn 0x38.
7. Until the length stops changing: Replace("{}", ""), Replace("()", ""), Replace("  ", " "); trim " "; append; 180c69020.

```
"FullPlayerNameOrder_Default:f"          "{clantag} {original_controller} {puppeteer}"
"FullPlayerNameOrder_PlayerSlot:f"       "{playerslot}| {clantag} {original_controller} {puppeteer}"
"DecoratedPlayerName_ClanTag:f"          "<span class='decorated-player-name__clan-tag'>[{s:value}]</span>"
"DecoratedPlayerName_ControllerName:f"   "<span class='decorated-player-name__controller-name'>{s:value}</span>"
"DecoratedPlayerName_Puppeteer:f"        "<span class='decorated-player-name__puppeteer'>({s:value})</span>"
"SFUI_scoreboard_lbl_bot"                "BOT"
```

The brackets are CS2's: a tag "[Top Defender]" (CS2Fixes' default) shows "[[Top Defender]] name".

| vfn | address | what |
|---|---|---|
| 0x00 | 18088b8d0 | puppeteer: m_hOriginalControllerOfCurrentPawn's m_sSanitizedPlayerName; "" without one |
| 0x08 | 18088b810 | clan tag: bot -> `#SFUI_scoreboard_lbl_bot`; "" when 180d39230()+0x82 set or 18088e650(xuid); else m_sSanitizedClanTag |
| 0x10 | 18088b8a0 | m_sSanitizedPlayerName |
| 0x18 | 18088ae20 | is a bot (m_fFlags & 0x100) |
| 0x20 | 18088ae10 | m_bControllingBot |
| 0x28 | 18088ae30 | m_hOriginalControllerOfCurrentPawn is this controller |
| 0x30 | 18088ae00 | -> 180945990 |
| 0x38 | 18088adc0 | player slot (1815e43f0 - 1) |

Callers' flags:
- player_name handler: the modifiers, 7 without.
- Death notice: `0x16 + (cl_show_clan_in_death_notice != 0)`; a controller with m_bControllingBot swapped for the
  original's first; the name (0x294 buffer) then 180e87850. huddeathnotice.vxml `text="{s:name}" html="true"`.
- Disconnect line, seasoncoin_levelup, item found line: 0 (= 0x12).

## Chat (server, 180cfab90)

1. Text unquoted, CCSGameRules vfn 0x270 (filter), sender's vfn 0x840 gate.
2. Token (1809268f0): alive = pawn vfn 0x550, or gamerules +0x11c 4 / 5. Team only: team 3 alive `Cstrike_Chat_CT`
   (`_CT_Loc` with a place), dead `_CT_Dead`; team 2 the `_T` ones; spectator `_Spec`. Else alive `_All`, spectator
   `_AllSpec`, dead `_AllDead`.
3. %s1 = controller vfn 0x480 (plain name; "Console" without a player): chat uses no decorated name.
4. Each other connected player gets it when 180911fe0 and the listener's vfn 0x838(sender) pass (and 180fd5110
   doesn't block); the sender always. SayText2 (180feb3e0) or, without a token, raw (180feb640).
5. 180911fe0 = 1809131f0(listener, sender, team only, sv_allchat), then for a living listener with
   sv_chat_proximity > 0: pawns closer than it.

```
Cstrike_Chat_CT        " [CT] \x03%s1: \x01%s2"                  Cstrike_Chat_T the same with [T]
Cstrike_Chat_CT_Loc    " [CT] \x03%s1\x04﹫%s3\x01: %s2"
Cstrike_Chat_CT_Dead   " [CT] \x03%s1 \x08[DEAD]\x01: %s2"
Cstrike_Chat_Spec      " \x01%s1 \x08[SPEC]\x01: %s2"
Cstrike_Chat_All       " \x01[ALL] \x03%s1\x01: %s2"
Cstrike_Chat_AllDead   " \x01[ALL] \x03%s1 \x08[DEAD]\x01: %s2"
Cstrike_Chat_AllSpec   " \x01[ALL] \x01%s1 \x08[SPEC]\x01: %s2"
Cstrike_Name_Change    " \x08%s1 changed name to %s2"
Cstrike_TitlesTXT_Game_connected  "%s1 connected"          csgo_player_left_game  " \x08Player %s1 left the game (%s2)"
```

## Connect, leave, rename

- Connect (180a924f0), unless a bot: name with "%" -> spaces, "<unconnected>" when empty;
  ClientPrintAll at HUD_PRINTNOTIFY (every console, no chat line). The client ignores player_connect.
- Disconnect (client): nothing for a bot, `ever_fully_connected` false, `name` starting "unconnected" or "NULLNAME", or
  180b43a60() true. Else decorated name (flags 0) and the reason: `reason` as ENetworkDisconnectionReason, its
  `(network_connection_token)` string; "#..." cut at ":" and localized, else shown as is (or `#SFUI_Disconnect_Title`
  with the hash 0xcdbd1292 switch); `#csgo_player_left_game` to chat (1811a5440).
- Reasons (network_connection.proto): 2 DISCONNECT_BY_USER `#GameUI_Disconnect_User` ("Disconnected by user."),
  3 BY_SERVER `_Server`, 4 LOST `_ConnectionLost`, 29 TIMEDOUT `_TimedOut`, 30 DISCONNECTED `_Disconnected`,
  39 KICKED `_Kicked` ("Kicked by server."), 40 BANADDED `_BanAdded`, 41 KICKBANADDED `_KickBanAdded` ("Kicked and
  banned"), 69 SERVER_SHUTDOWN `_ServerShutdown`; 1 SHUTDOWN none. CS2Fixes kicks with KICKED, bans with KICKBANADDED.
- Rename: no `Cstrike_Name_Change` in server.dll, client ignores the event: no line.

## Chat colours (180eb4120)

1 "#ffffff"; 3 the team's: team 3 "#a2c6ff", team 2 "#ffdf93", else "#ba81f0"; 4 "#40ff40", 5 "#bfff90",
6 "#a2ff47", 7 "#FF4040", 8 "#c5cad0", 9 "#ede47a", 10..16 rarity colours, else (2) "#ff0000"; negative: the team's
"#ffdf93" / "#a2c6ff", else white. 180eb3e80 uses the same three team colours.

## The chat line's sound (HudChat.Message)

| handler (11-05 / 10-15) | message | sound when |
|---|---|---|
| 1811ac670 / 1811a7ca0 | RadioText (by `game_radio_team_prefix_%d`) | cl_clutch_mode 0 |
| 1811acf90 / 1811a85c0 | SayText2 | chat set and cl_clutch_mode 0, after the line is added (1811a5440) and echoed (Msg "%s\n") |
| 1811ad6f0 / 1811a8d20 | SayText | always, after 1811a5550 (entity -1 when chat is 0) |

SayText2's chat flag cleared when the sender (entityindex - 1) is muted (180c0c0b0 then 180c12010, unless param4 equals
0x181bb0ff4's constant); without chat the line still shows when not muted (180c12010 false), no sound. Sender must be
connected. TextMsg (HUD_PRINTTALK) names no sound.

## Styles

csgostyles.vcss `.decorated-player-name__clan-tag { font-family: Stratum2 Light Condensed }`; hudreticle.vcss adds
`text-shadow: 1px 1px 0px 0 #000000f0` for the overhead. Scoreboard `#name`: `class="sb-team-tint stratum-medium"`, 18 px.

## Overhead team id (CCSGO_HudReticle)

Per frame 180eaf7c0: 180eb4df0, 180eb4260 + #TargetID, 180ed3610, 180ed28e0, the bone loop, 180ed3150, 180ed0210.

180eb4df0 (the who / alpha / scale rules are listed in cs2web's web/src/cs2web/client/hud/teamid.js header). Also:
alpha factor `max(0.25, (d - 56) / 88)` under 160 u needing "not spectating, an enemy" (never true for a shown player);
position at +0xc = `(vfn 0x568 point - abs origin) + (0, 0, 20)`; +9 bit 4 = not occluded and pawn +0x1e9a.

180ed10b0: name not shown -> bit 2 cleared, return. Else bit 2 set; kind health unless DAT_1825651d0+0x40 and
180759930 (then money). Health `(uint)(max(0, m_iHealth) / (float)GetMaxHealth() * 100.0f)` (GetMaxHealth vfn 0x550).
Tokens `#Panorama_HUD_playerid_overhead_health` "{d:player_health}%", `..._money` "${d:r:player_money}".

180ed28e0:
- [0] `playerid--team-ct` team 3, `playerid--team-t` team 2.
- Teammate colours shown: [11], [12] washed in the colour; [4] too with 182579058, else its wash removed. Otherwise
  with +9 bit 2: [12] washed 0xffdcdcdc.
- [6] `playerid__weapons--hidden` = !bit 8; icons `playerid__weaponicon--hidden`; `file://{images}/icons/equipment/%s.svg`.
- [3] `playerid__name--hidden` = !bit 2 (name and extra info hide together).
- Bit 2: dialog variables `player_money` / `player_health`; changed: `extra_info` = the token, `player_slot`, [0]'s
  class `low-health` (kind 1, health < 26), `money` (kind 2), else `normal-health`.
- [11] `playerid__icon--hidden` = (+9 & 6) != 0; [12] hidden = !(+9 & 2); [13] hidden unless (+9 & 4) and !(+9 & 2).
- |alpha - last| > 0.001: [2]'s opacity = alpha.

Bone loop: 180952970(pawn, 0x88319dad), else 0x57320e21; found: +0xc = 18093f490's position. CS2's agents have head_0.

180ecb3d0: the point projected to px, / the root's UI scale = the root's translate; Content transform =
`scale3d(scale x 0.7, scale x 0.7, 1)`. hudreticle.vcss: root 1024 x 256 at x -512 / y -256 (bottom centre on the
point), Content 400 wide, bottom centre, transform-origin 50% 100%, flow-children up.

## Helpers

- Client RTTI calls the controller `CCSPlayerController` (no C_ prefix); sub-object vtables: COLs with offset != 0.

## Unread

- Panorama's layout (panorama.dll): label line height, `text-overflow: shrink min( 20px ) ellipsis` steps, a span's
  "Stratum2 Light Condensed" against `font-weight: bold`; whether `{s:value}` is HTML-escaped (probably not).
- 180ed3610 (talking bit); 180c69020; the sanitize gates; vfn 0x568 ("head", taken as the eye).
- The SayText2 handler beyond its sound; cl_clutch_mode's other effects and reset.
