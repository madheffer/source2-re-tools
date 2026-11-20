# The player ping (CS2's `player_ping`, Mouse 3)

server_20261105.dll and client_20261015.dll (Ghidra project cs2, ReVa), read 2026-11-16. Ported in
web/server/cs2web/comms/ping.js (the server's command and its rules) and web/src/cs2web/client/fx/ping-view.js (the icon and sound);
CS2Fixes' leader rule over it is server/cs2web/cs2fixes/leader/leader.js pingAllowed (docs/CS2FIXES_ZR.md "Leader").

## The command: player_ping (server 180ab7ec0, registered by 1800c8950)

The pawn (180cbc5b0, the command's client) and its CCSPlayer_PingServices (pawn+0xd30, `plVar7[0x1a6]`); the
services' one CPlayerPing (180ac6630: m_hPlayerPing, spawned through CEntitySpawner<CPlayerPing> the first time), so
each player has a single ping entity that every ping moves.

1. Gates: pawn vfn 0x558, 0xca8, 0x550 all true (taken as: a live player pawn in play; TODO each name), and the bool
   cvar at 18211a6d8 (+0x58) off (read in movement.md as mp_teammates_are_enemies: TODO its name). Else nothing.
2. **Double ping**: `urgent = !(ping+0x4ac == 0) && now - ping+0x4ac < 0.5` (ping+0x4ac: the time of the last ping,
   180927cb0 the controller's curtime; 0 before the first).
3. **The spam filter** 180a9be60(controller, the command): a per-command-name time table on the controller
   (+0xa58 symbols, +0xa48 times); the same command within **0.3 s** of its last pass returns 0, else the time is set
   to now (gpGlobals+0x30) and 1. The first use passes.
4. **The tokens** 180abf930(services): 5 floats at services+0x48 (m_flPlayerPingTokens); the first with now > token
   (18017e2d0 compare > 0) becomes now + **player_ping_token_cooldown** (cvar 182175890, registered 1800c89c0,
   default **20.0**, flags 0x84000) and the ping is allowed. None free: refused.
5. The order: controller present and the filter refuses, or no token: then allowed only if `urgent && !ping+0x4bc`
   (the last ping wasn't urgent): a fast double tap is a free urgent ping. Else the pinger gets the radio text
   `#Chatwheel_ping_on_cooldown` ("Cannot ping. Ping is on cooldown.", with #Game_radio_location) and nothing else.
6. **The trace**: dir = the eye angles' forward (180b4faf0), start = EyePosition (vfn 0x5e8), end = start + dir x
   (g_flConfigMaxCoord + g_flConfigMaxCoord) x 1.7320508 (16384: **56755.84 units**); 180250e50(start, end, ignore the
   pawn, interacts-with **0x1c1003**, collision group 4). A miss (fraction 1): no position (the ping entity's time and
   urgent still change, the event isn't fired: 180adb580 below).
7. A hit: 180211b00(pawn, eye, end, out) = 1809bfc60's smoke density along eye..end >= 1.0 (every active smoke's voxel
   grid, smokegrenade +0xb6c / +0xbc0): **a ping into a smoke lands on the smoke** (out). Else the entity snap: the hit
   entity's rank (180ac6b50, RTTI casts: CPlantedC4 4, CCSWeaponBase 3, CItemDefuser 2, CChicken 1, else 0); under 3, a
   partition query (180bf7da0) of a 46-unit sphere (18048a430(.., 46.0)) round the end: each entity of rank > 1 and >=
   the best so far, its vfn 0x2c8 point within **36 units** of the end, the nearest at the highest rank, is pinged.
8. 180adb580(services, ping, urgent, 0, pinged entity, the end point).

## Placing it (server 180adb580(services, ping, urgent, special, entity, pos))

- m_hPlayer (ping+0x4b0) = the pawn; services m_hPlayerPing (+0x5c) = the ping.
- **m_iType** (ping+0x4b8): special ? 24 : urgent ? **13** : 0; then by the pinged entity: CPlantedC4 25 (its point
  1803d6f50), CCSWeaponBase **1**, CItemDefuser 27, CChicken 26; the entity's point (vfn 0x2c8) is the position.
- ping+0x4ac = now; **m_bUrgent** (ping+0x4bc) = urgent && !special; m_hPingedEntity (+0x4b4).
- m_szPlaceName (+0x4bd, 18 chars): the nav place under the point (1814bb3f0: a nav query with the 71 + half height
  box, 10000 units); empty without one.
- The entity teleported to the point (vfn 0x528), angles the pawn's (180 deg added to the yaw).
- The event **player_ping** { userid, entityid (the ping), x, y, z, urgent }, then 180233820: the OnPlayerPing output.
- Its think 180ae0fc0 (`player_ping_stop`) at now + **6.0 s** (special: 30 s; a chicken pinged while the gamerules
  flag +0xd8 is set and 180343fd0(chicken): 180345830 makes it follow the pinger, 1 s).
- Other caller: 180962c50 pings an entity (special 0) without the command's gates (TODO what it is).

## The client (client_20261015)

- **The icon** (C_PlayerPing's update 1808dda40, from the entity, not the event): particles/overhead_icon_fx/
  player_ping.vpcf at the entity when it moves, shown only if the pinger's team (pawn+999) is the local player's
  (180a7fd40: the local controller's team) or m_iType is 24, the pinger isn't muted (180c12010) and
  **cl_player_ping_mute != 2**. CP1 = the team's colour as **bytes** (the float vector 0..255): CT (181, 212, 238),
  T (234, 209, 138) (or the player's teammate colour when 180769bb0 is set: TODO which mode), CP2 = (1, 1, 1). So a
  particle tint CP takes colour bytes, not 0..1.
- **The sound** (the event handler 180c76830, "player_ping"): the pinger's pawn on the local player's team
  (1808e5720: m_iType 24, or the same team), not muted, **cl_player_ping_mute == 0**: `UI.PlayerPingUrgent` if urgent,
  else `UI.PlayerPing`, at (x, y, z) read **as integers** (GetInt: truncated), from the local player's entity.
- So teammates only: CTs see and hear CT pings, Ts T pings; a spectator (team 1) neither (TODO 180a7fd40 while
  spectating: whether it is the observed player's team).
- The HUD's off-screen markers (PlayerPing / PlayerPingOffMap panels, VisiblePlayerPings) are not read.

## CS2Fixes on top (leader.cpp:360-435)

It edits the event's recipients only (`*clients = 0` mutes it: no sound), so a muted ping's icon still shows to the
pinger's team; only with !disablepings and a human leader is a non-leader CT's ping entity removed (no icon either).
A CT leader's ping is heard, gets the leader's mark and clears their five tokens.

## Not read

The pawn vfns of step 1, the bool at 18211a6d8's name, 180962c50, the special ping's caller (m_iType 24), the HUD's
ping panels, cl_ping_fade_distance / cl_ping_fade_deadzone (the icon's fade: not ported), 180769bb0.
