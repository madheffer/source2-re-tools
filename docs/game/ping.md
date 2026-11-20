# Player ping (`player_ping`, Mouse 3)

server_20261105, client_20261015. CS2Fixes' leader layer: leader.cpp:360-435.

## Functions

| Address | Module | What |
|---|---|---|
| 180ab7ec0 | server | `player_ping` command (registered 1800c8950) |
| 180cbc5b0 | server | the command's pawn |
| 180ac6630 | server | the services' CPlayerPing (spawned once per player, every ping moves it) |
| 180a9be60 | server | per-command spam filter (controller, cmd): 0 within 0.3 s of the last pass, else sets now, 1 |
| 180abf930 | server | take a token: first of 5 with now > token becomes now + cooldown |
| 180b4faf0 | server | eye angles -> forward |
| 180250e50 | server | the trace (start, end, ignore pawn, mask, group) |
| 180211b00 | server | ping lands on smoke: 1809bfc60 density along eye..end >= 1.0 |
| 180ac6b50 | server | entity rank: CPlantedC4 4, CCSWeaponBase 3, CItemDefuser 2, CChicken 1, else 0 |
| 180bf7da0 | server | partition query (sphere from 18048a430(.., 46.0)) |
| 180adb580 | server | place the ping (services, ping, urgent, special, entity, pos) |
| 1814bb3f0 | server | nav place name at a point (box 71 + half height, 10000 u) |
| 180ae0fc0 | server | think `player_ping_stop` |
| 180233820 | server | fires OnPlayerPing |
| 180927cb0 | server | the controller's curtime (the double-ping clock) |
| 18017e2d0 | server | f32 three-way compare (the token test, > 0) |
| 180343fd0 | server | chicken may follow (with gamerules +0xd8 set) |
| 180345830 | server | chicken follows the pinger (1 s) |
| 180962c50 | server | pings an entity without the command's gates (unread) |
| 1808dda40 | client | C_PlayerPing update: the icon |
| 180c76830 | client | `player_ping` event handler: the sound |
| 1808e5720 | client | pinger audible: m_iType 24 or same team |
| 180a7fd40 | client | local controller's team |
| 180c12010 | client | player muted |

## Fields

| Offset | Field |
|---|---|
| pawn +0xd30 | CCSPlayer_PingServices (decompiler: `plVar7[0x1a6]`) |
| pawn +999 (client) | team, read by the icon |
| gpGlobals +0x30 | now (the spam filter's time) |
| gamerules +0xd8 | flag gating the chicken follow |
| services +0x48 | m_flPlayerPingTokens[5] (float) |
| services +0x5c | m_hPlayerPing |
| controller +0xa58 / +0xa48 | spam filter: command symbols / times |
| ping +0x4ac | time of last ping (0 before the first) |
| ping +0x4b0 | m_hPlayer |
| ping +0x4b4 | m_hPingedEntity |
| ping +0x4b8 | m_iType |
| ping +0x4bc | m_bUrgent |
| ping +0x4bd | m_szPlaceName (18 chars) |
| smokegrenade +0xb6c / +0xbc0 | voxel grid read by the smoke test |

## Constants

| Value | What |
|---|---|
| 0.5 s | double-ping window (urgent) |
| 0.3 s | spam filter |
| 5 | tokens |
| 20.0 | player_ping_token_cooldown (cvar 182175890, reg 1800c89c0, flags 0x84000) |
| 2 x 16384 x 1.7320508 = 56755.84 | trace length |
| 0x1c1003, group 4 | trace interacts-with, collision group |
| 46.0 / 36.0 | snap sphere radius / max distance to the entity's point (vfn 0x2c8) |
| 6.0 s (special 30 s) | ping lifetime |
| CT (181, 212, 238), T (234, 209, 138) | icon CP1, as bytes 0..255; CP2 (1, 1, 1) |

## Command order (180ab7ec0)

1. Gates: pawn vfn 0x558, 0xca8, 0x550 true; bool cvar 18211a6d8 (+0x58) off.
2. `urgent = ping+0x4ac != 0 && now - ping+0x4ac < 0.5`.
3. Refused by the spam filter or out of tokens: allowed only if `urgent && !ping+0x4bc`; else radio text `#Chatwheel_ping_on_cooldown`.
4. Trace from EyePosition (vfn 0x5e8) along the forward. Miss: time and urgent still set, no event.
5. Hit: into smoke, the smoke point; else when the hit's rank < 3, the highest-ranked (> 1), nearest entity within the snap.
6. 180adb580.

## Placing (180adb580)

- m_iType: special 24, urgent 13, else 0; pinged entity: CPlantedC4 25 (point 1803d6f50), CCSWeaponBase 1, CItemDefuser 27, CChicken 26.
- m_bUrgent = urgent && !special. Entity teleported (vfn 0x528), yaw + 180.
- Event `player_ping` { userid, entityid, x, y, z, urgent }, then OnPlayerPing; think at +6 s.

## Client

- Icon: particles/overhead_icon_fx/player_ping.vpcf; shown for the local team (or m_iType 24), not muted, cl_player_ping_mute != 2.
- Sound: `UI.PlayerPingUrgent` / `UI.PlayerPing` at (x, y, z) as ints (truncated), only when cl_player_ping_mute == 0.

## CS2Fixes (leader.cpp:360-435)

Edits the event's recipients only (muted: no sound, icon still shown); with !disablepings and a human leader, a non-leader CT's ping entity is removed. A CT leader's ping clears their five tokens.

## Unread

Pawn vfns 0x558 / 0xca8 / 0x550; cvar 18211a6d8's name; 180962c50; the caller of the special ping (m_iType 24); the HUD's ping panels; cl_ping_fade_distance / cl_ping_fade_deadzone; 180769bb0 (teammate colour mode).
