# Bot takeover

server_20261105, client_20261015. A dead player watching a living bot teammate presses +use and plays on as that bot.

## Functions

| Address | Module | What |
|---|---|---|
| 180a4c2d0 | server | CCSObserver_UseServices slot 12 (vtable 0x18191cd78): a dead player's +use |
| 180c80ad0 / 18069c8a0 | server | the use button state (movement services +0x50): held, pressed or released this command |
| 180a445f0 | server | observer services vfn 0xc8: the observer target |
| 180a71120 | server | CanControlBot(controller, bot, skipObserverChecks) |
| 180ad2a20 | server | (the controller's pawn, the bot's slot): the bot an enemy (180ad2840) |
| 1802d14b0 | server | bot in its defuse state: CCSBot +0x5c0 == +0x408 |
| 180c868d0 | server | GetActiveWeapon |
| 18093e610 | server | gamerules m_iRoundWinStatus |
| 18093ec40 | server | gamerules m_bWarmupPeriod |
| 180a9cbe0 | server | TakeControlOfBot(controller, bot) |
| 1802321d0 | server | called with the new pawn's vfn 0xca8 |
| 18022e820 | server | (gamerules, controller), after take / release |
| 180a9c710 | server | the pawn swap |
| 180b764f0 | server | SetPawn(controller, pawn, 1, 0, 0, 0) |
| 18023ee80 | server | (pawn, on): the bot brain (pawn +0x1508 and CCSBot +0x1a8) |
| 180ceffe0 | server | run on both pawns after the swap |
| 180a991e0 | server | ReleaseControlOfBot(controller) |
| 18024d860 | server | State_Transition(pawn, state) |
| 180a77c10 | server | controller think tail (from 180a93970 after 180b66860's PhysicsRunThink; ChangeTeam 180a7d7d0; 180a93200) |
| 180236ce0 | server | the observer state's update (vtable 0x1817947f8 slot 2): m_bCanControlObservedBot |
| 18095aef0 | server | RestartRound part (180957e50 at 180957f99): releases every player-controlled bot pawn |
| 180a936c0 | server | controller OnPreResetRound (RestartRound at 180958017): release when controlling |
| 180a9aba0 | server | controller round reset (slot 0x890; RestartRound at 18095a42f, after the spawns): +0x8e1, +0x8e2, +0x8e4 = 0 |
| 180a92980 | server | controller connection change (slot 0x808) |
| 18023b580 | server | script CSPlayerPawn.Reset: releases the pawn's original and current controllers first |
| 180a88120 | server | IsControllingBot (+0x8e0) |
| 180223410 | server | pawn vfn 0xc28: +0xe14 != +0xc98 (a pawn a player controls) |
| 1801cd1d0 | server | pawn vfn 0xc20: FL_BOT |
| 1801c8ce0 | server | pawn's current controller (+0xc98) |
| 180b55040 | server | resolves controller m_hPawn |
| 180a74d20 | server | sets m_hPlayerPawn at connect |
| 180a9db90 | server | m_hOriginalControllerOfCurrentPawn mirror (the current pawn's +0xe14) |
| 180912130 | server | PlayerKilled: victim's original controller's deaths (180b0b5f0), killer's original controller's kill (180b0b6e0) and round kill (180a6e260) |
| 180952250 | server | gamerules kill handler: kill award 180b00730(original controller's money services +0x7e8, 2, the weapon's award) (+0xe14 read at 1809523fb); teamkill penalty 180b006f0(current controller's, 1) |
| 180a94520 | server | damage post (+0xe14 at 180a94914 -> 1801c9d50): damage records |
| 1801c4ca0 .. 1801c8184 | server | CCSGameStats: every reader of +0xe14 there (round stats) |
| 180a6fc60 | server | money test (+0xe14): buying pays from the bot |
| 180a2030d | server | CC4 plant award: 1801c8ce0 (the planter pawn's current controller) |
| 180a1cd72 | server | OnDefuse award (+0xe14 at 180a1cd09): the bot |
| 18035d259 | server | hostage award 6 (+0xe14 at 18035d1f3): the bot |
| 18035d669 | server | hostage award 5 (+0xe14 at 18035d5ff): the bot |
| 18035c280 | server | hostage Event_Killed: award 8 at 18035c3a3, the attacker pawn's controller by 1801c8060 (current +0xc98, else original +0xe14) |
| 18090bae0 | server | default MVP: skips m_bHasControlledBotThisRound |
| 1809f1550 | server | defused MVP: a controlling defuser goes to the default ([winpanel.md](winpanel.md)) |
| 1801c0e00 / 1801d79b0 | server | dominations ([death-notice.md](death-notice.md)): skipped for a controller controlling a bot |
| 180b1d1e0 | server | survival streak: reset for a controller controlling a bot |
| 180a4fd00 | server | SetObserverTarget (slot 0xe0) |
| 180a4f810 | server | SetObserverMode (slot 0xf8) |
| 180a433e0 | server | FindNextObserverTarget (slot 0x100) |
| 180a43f60 | server | GetNextObserverSearchStartPoint (slot 0x108) |
| 180a42950 | server | rank by FInViewCone x 2 + IsLineOfSightClear, ties by the dot |
| 180a472b0 | server | IsValidObserverTarget (slot 0x110) |
| 180a881c0 | server | the whole team dead |
| 180cfe7c0 | server | FInViewCone: cos(fov / 2) of the camera services' FOV against the direction to the target's origin, centre, eye |
| 180cfef00 | server | IsLineOfSightClear (-> 180cfed40, the world only): your eye to its centre, eye, origin |
| 180c72900 | server | spectator command handler (spec_mode / spec_next / spec_prev / spec_player) |
| 180c5fcf0 | client | C_CSPlayerPawn listens for `bot_takeover` |
| 180c77002 | client | its handler: p / y / r -> view angles (180b80e70) |
| 18089ecb0 | client | CCSPlayerController slot 0x748 -> 180e88280: the takeover panel |
| 18088b2b0 | client | the bot's name for s1 |
| 180e78360 | client | CCSGO_HudHealthAmmoCenter constructor: finds `HotKey_ControlBot` |
| 180e928f0 | client | the legend strip (from 180e91fb0, the observer HUD's update) |
| 180e7bd90 | client | m_bCanControlObservedBot test (controller +0x3f4 bit 8) |
| 180ce24d0 | client | caster / HLTV |
| 1809049b0 | client | decorated name ([teamid.md](teamid.md)) |
| 18089df60 / 18088ca80 | client | death notice: a controlling controller named by m_hOriginalControllerOfCurrentPawn |
| 180058020 | server | registers bot_controllable |
| 1800a5970 | server | registers sv_coaching_enabled |
| 1800e4d60 | client | registers cl_spec_show_bindings |

## Fields

CCSPlayerController (client +0x40 for the run below):

| Server | Client | Field |
|---|---|---|
| +0x8e0 | +0x920 | m_bControllingBot |
| +0x8e1 | +0x921 | m_bHasControlledBotThisRound |
| +0x8e2 | +0x922 | m_bHasBeenControlledByPlayerThisRound (the bot's) |
| +0x8e4 | +0x924 | m_nBotsControlledThisRound |
| +0x8e8 | +0x928 | m_bCanControlObservedBot |
| +0x8ec | +0x92c | m_hPlayerPawn (the controller's own player pawn: never changed by a takeover) |
| +0x8f0 | +0x930 | m_hObserverPawn |
| +0x8f4 / +0x8f8 | | m_DesiredObserverMode / m_hDesiredObserverTarget |
| +0x918 | +0x950 | m_hOriginalControllerOfCurrentPawn |
| +0x4e0 | | m_hPawn (the current pawn, the observer pawn while dead) |
| +0x84c | | m_iCoachingTeam |
| +0x8d8 | | set to bot +8 by TakeControlOfBot (on the bot controller) |
| +0x388 bit 0x100 | | a bot |

| Offset | Field |
|---|---|
| CCSPlayerPawn +0xe14 (client +0x1560) | m_hOriginalController |
| CCSPlayerPawn +0xc98 | its controller |
| CCSPlayerPawn +0xb28 | observer services |
| CCSPlayerPawn +0xb50 | movement services |
| CCSPlayerPawn +0x1500 / +0x1508 | the CCSBot / bot brain on |
| CCSPlayerPawn +0xbc8 / +0xbd0 | m_angEyeAngles |
| CCSPlayerPawn +0xdfc | zeroed by the swap, copied back on a release |
| CCSPlayerPawn +0x388 bit 0x10 | m_fFlags FL_BOT |
| CCSPlayerPawn +0x820 | pending team switch |
| CCSPlayerPawn +0x1498 | m_nLastKillerIndex |
| CCSPlayerPawn +0xc7c | m_flDeathTime |
| CCSBot +0x1a8 | brain on |
| CC4 +0x12c9 | m_bStartedArming |
| gamerules +0xa44 | m_iRoundWinStatus |
| gamerules +0xd9 | m_bWarmupPeriod |
| observer services +0x4c | m_hObserverTarget |

## Constants

| Value | What |
|---|---|
| bot_controllable | object 0x181fa5ca8, value pointer 0x181fa5cb0 +0x58, flags 0x80000, default 1, "Determines whether bots can be controlled by players"; no gamemode_*.cfg sets it |
| sv_coaching_enabled | 0x182119820, default 0 |
| cl_spec_show_bindings | client bool, default 0, flags 0x10080000, "Toggle the visibility of the spectator bindings." |
| mp_forcecamera | server 0x1821915e8; client handle 0x1825510d0 |
| 0x181fa48fc | hostage rescue (0: none) |
| spec_freeze_time 3.0, spec_freeze_traveltime 0.3, spec_freeze_time_lock 1.0, spec_freeze_deathanim_time 0.8 | storage 0x182171510 / 520 / 530 / 540 |
| State_Transition states | 0 active, 6 observer mode (STATE_OBSERVER_MODE), 7 gungame respawn, 8 dormant |
| 0x18191ca48 | CCSObserver_ObserverServices vtable (base CPlayer_ObserverServices 0x181952910) |
| 0x182733f40 vfn 0x1e8 | client UI engine: read as its last input time |

## +use (180a4c2d0)

Use button state with an observer target that is a player pawn (vfn 0x558, 0xca8) of a bot (vfn 0xc20) with its CCSBot (pawn +0x1508 set: +0x1500) -> CanControlBot(controller's pawn's controller, bot, 0). Messages: bot_controllable off "disallowed by the server"; pawn +0x820 set and not the team "a pending team switch"; the engine's replay (vfn 0x338) "in replay mode"; then TakeControlOfBot: "Player %s took control bot %s (%d)", else "failed"; no target "none could be found".

## CanControlBot (180a71120)

1. bot_controllable; the controller's m_hPawn; the bot's pawn alive (vfn 0x550).
2. Unless skipping: sv_coaching_enabled with a spectator (team 1) coach (+0x84c) -> no; 180ad2a20 (an enemy) -> no; observer services present and IsValidObserverTarget (vfn 0x110) of the bot's pawn.
3. The bot not in its defuse state (1802d14b0); its active weapon not a CC4 with m_bStartedArming; the round not won (18093e610); not the warmup (18093ec40).
4. Skipping -> yes, else the controller's m_hPawn not alive (vfn 0x550).

No once-a-round rule: nothing reads +0x8e1 or +0x8e2, so a player whose bot died may take another living bot the same round (m_nBotsControlledThisRound counts them; the bots_assumed fun fact, minimum 2). Only m_bCanControlObservedBot's update requires the in-eye / chase mode; +use takes the observer target in any mode.

## TakeControlOfBot (180a9cbe0)

1. CanControlBot(..., 1); the bot pawn's eye angles (+0xbc8, +0xbd0); bot controller +0x8d8 = bot +8.
2. The swap 180a9c710; m_DesiredObserverMode 0, target -1; the new pawn's vfn 0xca8 -> 1802321d0.
3. m_bControllingBot 1, m_bHasControlledBotThisRound 1, the bot controller's m_bHasBeenControlledByPlayerThisRound 1, m_nBotsControlledThisRound + 1.
4. Event `bot_takeover` { userid: the controller, botid: the bot's pawn, p, y, r }; 18022e820(gamerules, controller).

## The swap (180a9c710)

Each controller SetPawn's (180b764f0) the other's m_hPawn; both pawns' +0xdfc = 0; a player pawn's bot brain 18023ee80(pawn, !vfn 0xc28) (off under a player, on with its own bot); 180ceffe0 on both.

## Release

- ReleaseControlOfBot (180a991e0): with m_bControllingBot, the bot controller from the pawn's +0xe14, the swap back; the player's pawn now an observer pawn (vfn 0xcb0): observer services vfn 0xc0, State_Transition(pawn, 6), +0xdfc from the released pawn; m_bControllingBot 0; 18022e820.
- 180a77c10: controlling and m_DesiredObserverMode != 0 (a death or a team change asks to observe) -> the bot controller takes the desired mode / target, then the release.
- 18095aef0: every bot pawn (vfn 0xc20) whose controller (+0xc98) isn't a bot (+0x388 bit 0x100) -> its controller's release.
- 180a92980: m_iConnected 3 and controlling -> release; a bot disconnecting whose pawn (+0x8ec) has another controller (pawn vfn 0xc28) -> that controller's release.
- 180236ce0: m_bCanControlObservedBot 0, then 1 when the observer mode (services vfn 0xb8) > 1 and the target is a bot's pawn with its brain on that CanControlBot(..., 0) allows.

## Who is credited

The pawn's original controller (+0xe14), the bot, is credited for what its pawn does under a player ("SFUI_Hint_ControlBotDontKeep": money, kills, deaths and weapons are the bot's): deaths / kills / round kills (180912130), the kill award (180952250; the teamkill penalty to the current controller), damage records (180a94520), round stats (CCSGameStats), buying (180a6fc60), the defuse award, hostage awards 6 and 5. The player (current controller) gets: the plant award (180a2030d), hostage award 8 (a hostage's death, 18035c280).

- Fun facts' player filter ([winpanel.md](winpanel.md)): the controller's own pawn (m_hPlayerPawn +0x8ec); a bot pawn whose controller has +0x8e2 is out; without filter bit 0x100 a controller with +0x8e1 is out. bots_assumed reads +0x8e4.
- Lag compensation: the pawn's FL_BOT stays on (the swap never touches +0x388), and StartLagCompensation rewinds nobody for a bot pawn's command, so a player controlling a bot has no lag compensation.

## The client

- `bot_takeover`: 180c77002 reads p / y / r and sets the view angles (180b80e70).
- 180e88280: the local pawn's m_hOriginalController (+0x1560) when controlling: hudtakeoverbot.vxml's panel (JoinPanel--Animate-FadeIn / -FadeOut), label `#SFUI_Notice_Hint_Bot_Takeover` "You are playing as BOT {s:s1}", s1 = 18088b2b0. hudtakeoverbot.vcss: .hud-takeover-bot (bottom, centred, 18 px, translateY 16 -> 0, .25 s), .hud-takeover-bot__text (13 px white, hud-outline-shadow).
- Spectator legend (hudlegend.vxml): `#PANOHUD_Spectate_Navigation_Control_Bot` "[{s:bind_use}] Control Bot " in .HudSpecplayer__key-hints-text (11 px, rgb 212); shown by m_bCanControlObservedBot (client +0x928) in 180e928f0.
- Decorated name (1809049b0): a controller controlling a bot wears the BOT tag (vfn 0x20); a bot whose current pawn's original controller is someone else shows "(name)" as its puppeteer.

## The legend strip (180e928f0)

cl_spec_show_bindings off: every label hidden; on: a bit per HotKeyLabelContainer label in its vxml order, each label without its bit gets HudSpecplayer__key-hints-text--hidden.

| Bit | Label | When |
|---|---|---|
| 1 | HotKey_ControlBot | the watched player a bot you may control (controller +0x3f4 bit 8; 180e7bd90) |
| 2 | HotKey_XRay | a caster / HLTV (180ce24d0) |
| 4 | HotKey_CancelReplay | in a killer replay |
| 8 | HotKey_Arrows | always |
| 0x10 | HotKey_Camera | mp_forcecamera 0, or a spectator (team 1) |
| 0x20 | HotKey_Map | always |
| 0x40 / 0x80 | HotKey_CameramanOn / DirectorOn | HLTV cameraman / autodirector |
| 0x100 | HotKey_ReplayLastKill | a killer replay ready |
| 0x200 | HotKey_ViewHighlight | highlights |
| 0x400 | HotKey_InspectLoadout | always ("#PANOHUD_Spectate_Vanity_Loadout_Show") |

The strip's root (+0xc0) is at opacity 1 for 8 s after the UI's last input, then fades to 0 over 4.5 s.

## The observer target (server, 0x18191ca48)

| Slot | Function | What |
|---|---|---|
| 0xb8 | GetObserverMode | m_iObserverMode (23 in the vtable's getter) |
| 0xe0 | SetObserverTarget 180a4fd00 | m_hObserverTarget (+0x4c) |
| 0xf8 | SetObserverMode 180a4f810 | |
| 0x100 | FindNextObserverTarget 180a433e0 | from the start point, each controller's player pawn (+0x8ec) +1 (reverse -1), wrapping, the first valid; none: the C4 / hostages |
| 0x108 | GetNextObserverSearchStartPoint 180a43f60 | target dead with a living killer (pawn +0x1498): the killer's slot as is; target invalid: the valid pawns ranked FInViewCone x 2 + IsLineOfSightClear from your eye, ties by the dot (180a42950), the best's slot as is; else the target's slot (or yours) +1 / -1, wrapping |
| 0x110 | IsValidObserverTarget 180a472b0 | a living pawn: not yours, and with mp_forcecamera on, for an observer on a team, a teammate; a dead one: mp_forcecamera 1 and no hostage rescue (0x181fa48fc 0) with the whole team dead (180a881c0): a dead teammate; else only your current target, until `m_flDeathTime + spec_freeze_deathanim_time + spec_freeze_traveltime + spec_freeze_time` |

- 180c72900: spec_mode cycles 2 -> 3 -> 4 -> 2 (an argument outside 2..4 becomes 2); spec_next / spec_prev / spec_player only in an observer mode >= 2 (past the death cam): FindNextObserverTarget then SetObserverTarget.
- IsValidObserverTarget's alive branch has further dynamic casts for non-player targets.
