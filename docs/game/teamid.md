# The overhead team id and the decorated player name

What CS2 draws over a teammate's head (hudreticle.vxml's `PlayerID` snippet) and how it writes a player's name
anywhere `{g:player_name:player_slot}` is used (that label, the scoreboard's `#name`, the death notice). Read
2026-11-11 from client_20261015.dll (Ghidra ReVa, the `FUN_` addresses) and client_20261105.dll (tools/re, capstone:
the name provider), csgo_english.txt in the installed pak01, and the baked hudreticle / csgostyles / scoreboard
layouts. The port: `web/src/cs2web/client/hud/teamid.js` (the rules), `client/hud/tag-sprites.js` (the panel),
`src/cs2web/player/player-name.js` (the name), `world/body.js head()` (the bone).

## 1. The decorated name (client 2026-11-05)

`{g:player_name:<modifiers>:<slot variable>}`: a global dialog-variable handler registered under "player_name"
(registration 180dbe2f0: handler 180dbcec0, modifier parser 180dbcd10).

**The modifier parser 180dbcd10** splits the argument and ORs each known word's flag from the table at 181cbeb00
(9 entries of 0x18: name pointer, flag at +0xc, a "clear instead" byte at +0x10); no flag at all returns **7**:

| word | flag | | word | flag |
|---|---|---|---|---|
| `oc` | 1 | | `party` | 0x20 |
| `clan` | 1 | | `friend` | 0x40 |
| `pupp` | 4 | | `draft` | 8 |
| `name` | 2 | | `accept` | 0x80 |
| `bot` | 0x10 | | | |

**The handler 180dbcec0**: flags 0x20 / 0x40 / 8 / 0x80 take a xuid and the party / friends / draft / lobby providers
(180f9efd0, 180f9f050, 180f9f010, 181077650: `CDecoratedPlayerNameProviderVia*Api`). Otherwise the variable is a
player slot: controller = 180acc550(slot), provider = controller + 0x810 (C_CSPlayerController's
IDecoratedPlayerNameProvider sub-object, vtable 181c11e28), `GetDecoratedPlayerName2(provider, out, flags, true)`.

**IDecoratedPlayerNameProvider::GetDecoratedPlayerName2 1809049b0** (rcx provider, rdx CBufferString out, r8d flags,
r9b append):
1. flags 0 becomes 0x12. `bot = vfn 0x18() || vfn 0x20()`. With flag 0x10 and `bot`: flags = (flags & ~0x10) | 1.
2. The clan tag (flag 1) is dropped when not `bot` and (`sv_clantags_enabled` is 0, or the static at 18253d104 is
   set: a tier0 lookup by hash 0xcdbd1292, unread).
3. The puppeteer (flag 4) is dropped when vfn 0x28() (this is the original controller) or not vfn 0x18().
4. The order: localized `#FullPlayerNameOrder_Default:f`, or `#FullPlayerNameOrder_PlayerSlot:f` with
   `cl_playerslot_in_names`.
5. Three parts, each { flag, key, wrapper token, getter (a std::function over the provider) }, 0x58 apart:
   - 1, `clantag`, `#DecoratedPlayerName_ClanTag:f`, vfn 8
   - 4, `puppeteer`, `#DecoratedPlayerName_Puppeteer:f`, vfn 0
   - 2, `original_controller`, `#DecoratedPlayerName_ControllerName:f`, vfn 0x10

   A part whose flag is off, or whose getter returns null or "", replaces its key in the order with "". Otherwise
   the wrapper is localized with `{s:value}` = the getter's string and set as the order's variable.
6. With `cl_playerslot_in_names`: `playerslot` = vfn 0x38's number.
7. Until the length stops changing: Replace("{}", ""), Replace("()", ""), Replace("  ", " "). Then the ends are
   trimmed of " " and the result appended to `out`; 180c69020(table 182575d38, the appended text, 3, vfn 0x30())
   runs over it (unread).

csgo_english.txt:

```
"FullPlayerNameOrder_Default:f"          "{clantag} {original_controller} {puppeteer}"
"FullPlayerNameOrder_PlayerSlot:f"       "{playerslot}| {clantag} {original_controller} {puppeteer}"
"DecoratedPlayerName_ClanTag:f"          "<span class='decorated-player-name__clan-tag'>[{s:value}]</span>"
"DecoratedPlayerName_ControllerName:f"   "<span class='decorated-player-name__controller-name'>{s:value}</span>"
"DecoratedPlayerName_Puppeteer:f"        "<span class='decorated-player-name__puppeteer'>({s:value})</span>"
"SFUI_scoreboard_lbl_bot"                "BOT"
```

So the brackets around a clan tag are CS2's own; a server that sets "[Top Defender]" (CS2Fixes' default) gets
"[[Top Defender]] name".

**C_CSPlayerController's provider** (vtable 181c11e28; `this` = controller + 0x810):

| vfn | address | what |
|---|---|---|
| 0x00 | 18088b8d0 | puppeteer: m_hOriginalControllerOfCurrentPawn (+0x950)'s m_sSanitizedPlayerName; "" without one |
| 0x08 | 18088b810 | clan tag: m_fFlags (+0x3f4) bit 0x100 (a bot): localized `#SFUI_scoreboard_lbl_bot`; else "" when 180d39230()+0x82 is set or 18088e650(xuid) (cl_sanitize gates, unread); else m_sSanitizedClanTag (+0x880) |
| 0x10 | 18088b8a0 | name: m_sSanitizedPlayerName (+0x878) |
| 0x18 | 18088ae20 | is a bot (m_fFlags & 0x100) |
| 0x20 | 18088ae10 | m_bControllingBot (+0x920) |
| 0x28 | 18088ae30 | m_hOriginalControllerOfCurrentPawn is this controller |
| 0x30 | 18088ae00 | -> 180945990 (unread) |
| 0x38 | 18088adc0 | the player slot (1815e43f0 - 1) |

vfn 0 / 0x10 return "WWWWWWWWWWWWWWWW" under a debug cvar (pointer 182533390).

Cvars (tools/re/game/cvardump.py): `sv_clantags_enabled` 1 (flags 0x82000, "Show players' clan tags in their names."),
`cl_playerslot_in_names` 0, `cl_show_clan_in_death_notice` 1, `cl_sanitize_player_names` 0.

**Who asks with which flags** (the callers of 1809049b0, client 2026-11-05):
- the `player_name` handler: the label's modifiers, 7 without any (above);
- **the death notice** (CCSGO_HudDeathNotice's player_death handler 180e8b2f0, calls at 180e8b684 / 70d / 797 for
  the attacker, the assister and the victim): flags = 0x16 + (cl_show_clan_in_death_notice != 0), so the name, the
  puppeteer, a bot's "BOT" (0x10), and a player's tag only with the cvar (default 1). Before it, a controller with
  m_bControllingBot (18089df60) is swapped for 18088ca80's (m_hOriginalControllerOfCurrentPawn's entity). After it
  the name (a 0x294 buffer) goes through 180e87850: with cl_deathnotices_show_numbers 1 / 2 the team counter's slot
  digit replaces / prefixes it (default 0: nothing). Labels: huddeathnotice.vxml `text="{s:name}" html="true"`;
- the disconnect line (180cecc30's player_disconnect branch, 180cee8c7; `#csgo_player_left_game`): flags 0
  (= 0x12: the name, a bot's tag); 180ceebb2 the same for seasoncoin_levelup;
- the item found line (client_20261015 180d119c0, cases.md "The item found line": flags 0), 180fa1899, 180fb5767, 180fdcd54 / 180fdce2d (the kick vote), 180ff2539,
  180eb6622 (the target id), 180ed40e7, 180eda6b9: flags unread.

**Chat doesn't** (server.dll 2026-11-05; the port: web/server/cs2web/comms/chat-say.js): say / say_team 180cfab90
(controller, args, team only, ...):
- the text unquoted, CCSGameRules vfn 0x270 (a filter) over it, the sender's vfn 0x840 gate;
- token = CCSGameRules vfn 0x2c0 (**1809268f0**): alive = the pawn's vfn 0x550, or gamerules +0x11c is 4 / 5.
  Team only: team 3 alive `Cstrike_Chat_CT` (`_CT_Loc` with a place name, 180926b60), dead `_CT_Dead`; team 2 the
  `_T` ones; a spectator (180ad2ac0) `_Spec`. Else alive `_All`, a spectator `_AllSpec`, dead `_AllDead`;
- %s1 = the controller's vfn 0x480 (its plain name; "Console" without a player); no caller above is a chat one;
- each other connected player gets it when **180911fe0**(gamerules, listener, sender, team only) and the
  listener's vfn 0x838(sender) pass (and 180fd5110 doesn't block the pair); the sender always. Sent as SayText2
  (180feb3e0: sender, chat, token, name, text, place) or, without a token, the raw "name: text" (180feb640);
- 180911fe0 = **1809131f0**(listener, sender, team only, `sv_allchat`) (the voice check's base, web/server/cs2web/comms/voice.js
  baseCanHear: its third argument is this flag, its fourth the "other team too" switch), then for a living
  listener `sv_chat_proximity` > 0: the pawns closer than it. Cvars: `sv_allchat` 1 (registration 180103d00:
  "Players can receive all other players' text chat, no death restrictions"), `sv_chat_proximity` -1 (1800a58f0).

csgo_english, with the colour codes:

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

**Connecting, leaving, renaming** (the port: chat-say.js leftLine / connectedLine):
- connect: server 180a924f0 (the controller's connect), unless a bot (controller +0x388 bit 0x100): the name
  (180b553d0) with "%" turned to spaces, "<unconnected>" when empty, then 180fe9cf0(1, 
  "#Cstrike_TitlesTXT_Game_connected", name): ClientPrintAll at HUD_PRINTNOTIFY: every console, no chat line. The
  client's game event handler (client 2026-10-15 180ceaab0) returns at once for `player_connect` and
  `player_changename`; `player_connect_full` only posts a panorama event. **The port's connect line is the owner's
  own** ("name [uid]: Joined from CC" in chat), not this;
- disconnect: the same handler's `player_disconnect` branch writes the chat line itself: nothing when the
  controller is a bot (m_fFlags +0x3f4 & 0x100), when the event's `ever_fully_connected` is false, when `name`
  starts "unconnected" or "NULLNAME", or when 180b43a60() is true (unread). Else the decorated name at flags 0
  (180903100 = GetDecoratedPlayerName2 in that build), the reason: the event's `reason` as an
  ENetworkDisconnectionReason value, its `(network_connection_token)` option string (1812afec0 -> 18127ff60); a
  string starting "#" is cut at ":" and localized, anything else shown as it is (or `#SFUI_Disconnect_Title` with
  the command-line switch of hash 0xcdbd1292); then `#csgo_player_left_game` " \x08Player %s1 left the game (%s2)"
  to the chat (1811a5440). The reasons' tokens, from the client's embedded network_connection.proto: 2
  DISCONNECT_BY_USER `#GameUI_Disconnect_User` ("Disconnected by user."), 3 BY_SERVER `_Server`, 4 LOST
  `_ConnectionLost`, 29 TIMEDOUT `_TimedOut`, 30 DISCONNECTED `_Disconnected`, 39 KICKED `_Kicked` ("Kicked by
  server."), 40 BANADDED `_BanAdded`, 41 KICKBANADDED `_KickBanAdded` ("Kicked and banned"), 69 SERVER_SHUTDOWN
  `_ServerShutdown`; 1 SHUTDOWN has none. CS2Fixes kicks with KICKED and bans with KICKBANADDED
  (adminsystem.cpp:255, 1775);
- name change: no `Cstrike_Name_Change` string in server.dll and the client ignores the event: no line. (The port
  has no renaming.)

The client's colour for a code (client 2026-10-15 **180eb4120**(code, the sender's team)): 1 "#ffffff", 3 the
team's: team 3 "#a2c6ff", team 2 "#ffdf93", else "#ba81f0"; 4 "#40ff40", 5 "#bfff90", 6 "#a2ff47", 7 "#FF4040",
8 "#c5cad0", 9 "#ede47a", 10..16 the rarity colours (18118e640's vfn 0xc0 with code - 9), anything else (2)
"#ff0000"; a negative code: the team's "#ffdf93" / "#a2c6ff", else white. 180eb3e80 (a name for a line, with the
place in "#40ff40" after " @ " for the same team, and the competitive colour dot with teammate colours) uses the
same three team colours. The client's SayText2 handler: its sound below; the rest of it is unread.

### The chat line's sound (client 2026-11-05 with tools/re, 2026-10-15 in Ghidra; read 2026-11-17)

`HudChat.Message` is named three times in client.dll, each an EmitSound (2026-10-15's 180c09410) with entity **-1**
(the listener), volume 1.0 (0x3f800000), sound level 100, flags byte `& 0xe1 | 1`:

| handler (11-05 / 10-15) | message | sound when |
|---|---|---|
| 1811ac670 / 1811a7ca0, hooked by the HUD chat's constructor (10-15 1811a4470 HookMessage, its plVar[7]) | RadioText (by its `game_radio_team_prefix_%d`; message +0x60 a string, +0x6c an int) | `cl_clutch_mode` is 0 |
| 1811acf90 / 1811a85c0, CHudChatDelegate vtable 0x181d26518 slot 12 (0x60) | SayText2 (+0x48 messagename, +0x50..0x68 param1..4, +0x70 chat, +0x74 entityindex) | chat set and `cl_clutch_mode` 0, after the line is added (1811a5440) and echoed to the console (Msg "%s\n") |
| 1811ad6f0 / 1811a8d20, slot 11 (0x58) | SayText (+0x48 text, +0x50 chat, +0x54 entityindex) | always, after 1811a5550 adds the line (entity -1 when chat is 0) |

SayText2's chat flag: cleared when the sender (entityindex - 1) is muted (180c0c0b0 then 180c12010(sender), unless
param4 equals the 5-char constant at 10-15 0x181bb0ff4, unread); without chat the line is still shown when the sender
isn't muted (180c12010 false), with no sound. The sender must be connected (controller +0x6f4 0 or 3). The server's say
sends chat on: 180feb3e0(filter, sender, mode, token, ...) sets chat = `mode - 1 < 2` and a second byte `mode == 2`;
say passes mode = (its eax) + 1 (180cfb101 / 180cfb1c5, eax unread: 0 or 1 by the team-only path). TextMsg (dest
HUD_PRINTTALK: the server's notices, CS2Fixes' ClientPrint, the radio's line as comms/radio.js sends it) names no sound.

`cl_clutch_mode` (11-05 1800f2550; its handle 0x1825c3c90, +0x58 the value): flags 0x80000 (not archived), default 0,
"Silence voice and other distracting sounds until the end of round or next death.". Also read by 180c77710, 180c786b0,
180d375c0 (unread). HudChat.Message: sounds/common/talk.wav, volume 0.8, mixgroup UI. Port: client/hud/chat-sound.js
(chat-sound-test.mjs), called on each 'chat' message with a sender (core/game.js); the mute test has no list here
(TODO), the clutch mode's other effects and its reset aren't ported.

Styles: csgostyles.vcss `.decorated-player-name__clan-tag { font-family: Stratum2 Light Condensed }`;
hudreticle.vcss adds `text-shadow: 1px 1px 0px 0 #000000f0` for the overhead's. The scoreboard's `#name` is
`class="sb-team-tint stratum-medium"`, 18 px.

## 2. The overhead team id (client 2026-10-15)

CCSGO_HudReticle (constructor 180e9f9b0: the panels and the style symbols). Per frame 180eaf7c0:
180eb4df0 (who is shown: an entry each), 180eb4260 + the #TargetID label, 180ed3610 (unread: the voice bit),
180ed28e0 (entries -> panels), the bone loop, 180ed3150 (placement), 180ed0210 (pings).

An entry is 0x88 bytes (vector at hud +0x78 count / +0x80 data), its panels 0x70 (vector at +0x90 / +0x98):

| entry | |
|---|---|
| +0x00 | the pawn's handle |
| +0x04 | team (pawn +0x3e7) |
| +0x08 | bits: 1 seen this frame, 2 name shown, 4 extra info changed, 8 weapons shown, 0x10 primary shown, 0x20 / 0x40 icons changed, 0x80 defuser |
| +0x09 | bits: 1 C4, 2 talking (the chat icon), 4 defusing icon |
| +0x0c | position (12 bytes) |
| +0x18 | extra info kind + 1 (1 health, 2 money) |
| +0x20 | the extra info's token |
| +0x28 / +0x2c | health percent / money (-1: unused) |
| +0x78 / +0x7c | alpha, the alpha last applied |
| +0x80 | scale |

Panels: [0] the PlayerID root, [1] ContentParent, [2] Content, [3] JsNameContainer, [4] JsName, [5] JsExtraInfo,
[6] Weapons, [7] WeaponDefuser, [8] WeaponC4, [9] WeaponGrenades, [10] WeaponPrimary, [11] ArrowIcon, [12] ChatIcon,
[13] DefusingIcon (creation 180ea6a80, which also clears the inline wash-color of [11], [12], [4], [5]).

**180eb4df0** (who, alpha, scale): as web/src/cs2web/client/hud/teamid.js's header lists. Also in it: an alpha factor
max(0.25, (d - 56) / 88) under 160 u that needs "not spectating, an enemy" (never true for a shown player), the
position stored at +0xc as (vfn 0x568 point - abs origin) + (0, 0, 20), and bit 4 of +9 = not occluded and
pawn +0x1e9a.

**180ed10b0** (entry, _, name shown): the extra info. Returns with bit 2 cleared when the name isn't shown.
Else bit 2 set; kind 0 (health) unless the mode flag DAT_1825651d0+0x40 and 180759930: then money (the int at +0x40 of
the object at +0x818 of the controller behind pawn +0x14bc; not named). Health: `(uint)(max(0, m_iHealth) / (float)GetMaxHealth() * 100.0f)` (pawn +0x34c,
vfn 0x550). Tokens `#Panorama_HUD_playerid_overhead_health` "{d:player_health}%" and `..._money`
"${d:r:player_money}".

**180ed28e0** (entries -> panels):
- [0]: `playerid--team-ct` when team == 3, `playerid--team-t` when == 2.
- 1808a44a0(local team, team) (teammate colours): [11], [12] washed in the player's colour (180889c80 -> 180889bd0);
  [4] too with the cvar at 182579058, else its inline wash-color removed. Otherwise, with +9 bit 2: [12] washed
  0xffdcdcdc.
- [6] `playerid__weapons--hidden` = !bit 8; the icons' `playerid__weaponicon--hidden`; image sources
  `file://{images}/icons/equipment/%s.svg`.
- [3] `playerid__name--hidden` = !bit 2 (so the name and the extra info hide together).
- With bit 2: dialog variables `player_money` / `player_health`; when changed, `extra_info` = the localized token,
  `player_slot`, and [0]'s "extra" class switch: `low-health` (kind 1 and health < 26), `money` (kind 2), else
  `normal-health`.
- [11] `playerid__icon--hidden` = (+9 & 6) != 0; [12] hidden = !(+9 & 2); [13] hidden unless (+9 & 4) and !(+9 & 2).
- |alpha - last alpha| > 0.001: [2]'s opacity = alpha (1817b5650 -> style vfn 0xa8).

**The bone loop** (180eaf7c0, after 180ed28e0): for each entry, 180952970(pawn, hash) = a bone's index by its
name's token: 0x88319dad ("ValveBiped.Bip01_Head"), else 0x57320e21 ("head_0"); when found, +0xc = the bone's
world position (18093f490: the skeleton instance's transform for that index). CS2's agents have head_0.

**180ed3150** -> **180ecb3d0**(root, Content, position + (0, 0, 9), scale): the point projected (180c19db0) to
screen px, divided by the root's UI scale (180508d20 / 180508d30) = the root's translate; Content's transform =
scale3d(scale x 0.7, scale x 0.7, 1). hudreticle.vcss: the root is 1024 x 256 at x -512 / y -256 (its bottom centre
on the point), Content 400 wide, bottom centre, transform-origin 50% 100%, flow-children up.

## 3. Helpers

- CUtlStringToken's hash: MurmurHash2, seed 0x31415926, of the lowercased name (checked: "player_slot" 0x51cda125,
  "player_health" 0x387f108e, the two bone names above). `python tools/re/game/strtoken.py 88319dad 57320e21 --file
  <dll>` tries every identifier-like string in a file (and `-- name ...` given ones) against the wanted tokens.
- A class's vtables at every sub-object offset: its RTTI complete-object locators with offset != 0
  (tools/re/game/rtti.py only prints offset 0): `python tools/re/game/vtall.py <dll> CCSPlayerController 9`. The client's
  controller is `CCSPlayerController` in RTTI too (no C_ prefix).
- `python tools/re/game/vpkgrep.py <pak01_dir.vpk> <path regex> <content regex> [context]`: the game's own files
  (resource/csgo_english.txt, panorama/) searched in place; needs `pip install vpk`.

## 4. Unread

Panorama's own layout (panorama.dll): a label's line height, `text-overflow: shrink min( 20px ) ellipsis`'s
steps, how a span's "Stratum2 Light Condensed" meets the label's `font-weight: bold`; whether `{s:value}` is
HTML-escaped (CS2Fixes' coloured EntWatch tags send a span, so probably not); 180ed3610 (the talking bit);
180c69020; the sanitize gates; teammate colours' own functions; vfn 0x568 ("head", taken as the eye).
