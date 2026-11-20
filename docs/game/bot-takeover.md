# Bot takeover (server_20261105.dll, client_20261015.dll)

A dead player watching a living bot teammate in eye presses +use and plays on as that bot. Port:
web/server/cs2web/modes/team/bot-takeover.js (every team mode: comp.js makes one; ZE has none), the pawn swap's
replica side the 'P' stimulus (web/src/cs2web/world/stimuli.js), the lag compensation's ze_lag_swap (sim/src/combat
abi.rs / lagcomp.rs), the client's HUD web/src/cs2web/client/modes/team/takeover-hud.js. Test:
web/server/cs2web/modes/team/bot-takeover-test.mjs.

## Fields (tools/re/game/schema.py)

CCSPlayerController (server; client +0x40 for the run below):

| server | client | field |
|---|---|---|
| +0x8e0 | +0x920 | m_bControllingBot |
| +0x8e1 | +0x921 | m_bHasControlledBotThisRound |
| +0x8e2 | +0x922 | m_bHasBeenControlledByPlayerThisRound (the bot's) |
| +0x8e4 | +0x924 | m_nBotsControlledThisRound |
| +0x8e8 | +0x928 | m_bCanControlObservedBot |
| +0x8ec | +0x92c | m_hPlayerPawn (the controller's own player pawn: never changed by a takeover; set at connect, 180a74d20) |
| +0x8f0 | +0x930 | m_hObserverPawn |
| +0x8f4 / +0x8f8 | | m_DesiredObserverMode / m_hDesiredObserverTarget |
| +0x918 | +0x950 | m_hOriginalControllerOfCurrentPawn (180a9db90's pawn mirror: the current pawn's +0xe14) |
| +0x4e0 | | m_hPawn (180b55040 resolves it: the current pawn, the observer pawn while dead) |
| +0x84c | | m_iCoachingTeam |

CCSPlayerPawn: +0xe14 m_hOriginalController (client +0x1560), +0xc98 its controller (1801c8ce0 resolves it),
+0xb28 the observer services, +0xb50 the movement services, +0x1500 the CCSBot, +0x1508 the bot brain on,
+0xbc8 m_angEyeAngles, +0xdfc (zeroed by the swap, copied back on a release), m_fFlags +0x388 bit 0x10 FL_BOT
(vfn 0xc20 = 1801cd1d0). Gamerules: +0xa44 m_iRoundWinStatus (18093e610), +0xd9 m_bWarmupPeriod (18093ec40).

Cvars: `bot_controllable` (object 0x181fa5ca8, value pointer 0x181fa5cb0 +0x58, registered 180058020, flags 0x80000,
default 1, "Determines whether bots can be controlled by players"; no gamemode_*.cfg sets it), `sv_coaching_enabled`
(0x182119820, 1800a5970, default 0).

## The functions

| address | what |
|---|---|
| 180a4c2d0 | CCSObserver_UseServices slot 12 (vtable 0x18191cd78): a dead player's command. The use button state (movement services +0x50, 180c80ad0 -> 18069c8a0: held, pressed or released this command) with an observer target (observer services vfn 0xc8 = 180a445f0) that is a player pawn (vfn 0x558, 0xca8) of a bot (vfn 0xc20) with its CCSBot (pawn +0x1508 set: +0x1500) -> CanControlBot(controller's pawn's controller, bot, 0); bot_controllable off: "disallowed by the server"; the pawn +0x820 set and not the team: "a pending team switch"; the engine's replay (vfn 0x338): "in replay mode"; then TakeControlOfBot: "Player %s took control bot %s (%d)", else "failed"; no target: "none could be found" |
| 180a71120 | CanControlBot(controller, bot, skipObserverChecks): bot_controllable, the controller's m_hPawn, the bot's pawn alive (vfn 0x550); unless skipping: sv_coaching_enabled with a spectator (team 1) coach (+0x84c) -> no; 180ad2a20(the controller's pawn, the bot's slot) = the bot an enemy (180ad2840) -> no; observer services present and IsValidObserverTarget (vfn 0x110 = 180a472b0) of the bot's pawn; then the bot not in its defuse state (1802d14b0: CCSBot +0x5c0 == +0x408); its active weapon (180c868d0) not a CC4 with m_bStartedArming (+0x12c9); the round not won (18093e610); not the warmup (18093ec40); skipping -> yes, else the controller's m_hPawn not alive (vfn 0x550) |
| 180a9cbe0 | TakeControlOfBot(controller, bot): CanControlBot(…, 1); the bot pawn's eye angles (+0xbc8, +0xbd0); bot controller +0x8d8 = bot +8; the swap 180a9c710; m_DesiredObserverMode 0, target -1; the new pawn's vfn 0xca8 -> 1802321d0; m_bControllingBot 1, m_bHasControlledBotThisRound 1, the bot controller's m_bHasBeenControlledByPlayerThisRound 1, m_nBotsControlledThisRound + 1; event `bot_takeover` { userid: the controller, botid: the bot's pawn, p, y, r }; 18022e820(gamerules, controller) |
| 180a9c710 | the swap: each controller SetPawn's (180b764f0(controller, pawn, 1, 0, 0, 0)) the other's m_hPawn; both pawns' +0xdfc = 0; a player pawn's bot brain 18023ee80(pawn, !vfn 0xc28) (pawn +0x1508 and CCSBot +0x1a8: off under a player, on with its own bot); 180ceffe0 on both |
| 180a991e0 | ReleaseControlOfBot(controller): with m_bControllingBot, the bot controller from the pawn's +0xe14, the swap back; the player's pawn now an observer pawn (vfn 0xcb0): observer services vfn 0xc0, State_Transition 18024d860(pawn, 6 = STATE_OBSERVER_MODE), +0xdfc from the released pawn; m_bControllingBot 0; 18022e820 |
| 180a77c10 | the controller's think tail (from 180a93970 after 180b66860's PhysicsRunThink; ChangeTeam 180a7d7d0; 180a93200): controlling and m_DesiredObserverMode != 0 (a death or a team change asks to observe) -> the bot controller takes the desired mode / target, then the release |
| 180236ce0 | the observer state's update (vtable 0x1817947f8 slot 2): m_bCanControlObservedBot 0, then 1 when the observer mode (services vfn 0xb8) > 1 and the target is a bot's pawn with its brain on that CanControlBot(…, 0) allows |
| 18095aef0 | RestartRound (180957e50 at 180957f99): every bot pawn (vfn 0xc20) whose controller (+0xc98) isn't a bot (+0x388 bit 0x100) -> its controller's release |
| 180a936c0 | the controller's OnPreResetRound (RestartRound at 180958017): a release when controlling |
| 180a9aba0 | the controller's round reset (slot 0x890; RestartRound at 18095a42f, after the spawns): +0x8e1, +0x8e2, +0x8e4 = 0 |
| 180a92980 | the controller's connection change (slot 0x808): m_iConnected 3 and controlling -> release; a bot (+0x388 bit 0x100) disconnecting whose pawn (+0x8ec) has another controller (pawn vfn 0xc28) -> that controller's release |
| 18023b580 | the script CSPlayerPawn.Reset: releases the pawn's original and current controllers first |
| 180a88120 | IsControllingBot (+0x8e0); 180223410 = pawn vfn 0xc28: +0xe14 != +0xc98 (a pawn a player controls) |
| 18024d860 | State_Transition(pawn, state): 0 active, 6 observer mode, 7 gungame respawn, 8 dormant |

No once-a-round rule: nothing in CanControlBot reads +0x8e1 or +0x8e2, so a player whose bot died may take another
living bot the same round (m_nBotsControlledThisRound counts them; the bots_assumed fun fact, minimum 2, is about
that). Only m_bCanControlObservedBot's update requires the in-eye / chase observer mode; +use itself takes the
observer target in any mode.

## Who is credited

The pawn's original controller (+0xe14) — the bot — is credited for what its pawn does under a player
("SFUI_Hint_ControlBotDontKeep": money, kills, deaths and weapons are the bot's):

- PlayerKilled 180912130: the victim's original controller's deaths (action tracking 180b0b5f0), the killer's
  original controller's kill (180b0b6e0) and round kill (180a6e260).
- 180952250 (the gamerules' kill handler): the kill award 180b00730(original controller's money services +0x7e8,
  2, the weapon's award) (+0xe14 read at 1809523fb); the teamkill penalty 180b006f0(current controller's, 1).
- The damage post 180a94520 (+0xe14 at 180a94914 -> 1801c9d50): the damage records.
- CCSGameStats (1801c4ca0 .. 1801c8184: every reader of +0xe14 there): the round stats.
- The money test 180a6fc60 (+0xe14): buying pays from the bot.
- The plant award (CC4 180a2030d: 1801c8ce0 = the planter pawn's current controller, +0xc98): the player.
- The defuse award (OnDefuse 180a1cd72, +0xe14 at 180a1cd09): the bot. The hostage awards 6 (18035d259, +0xe14 at
  18035d1f3) and 5 (18035d669, +0xe14 at 18035d5ff): the bot. Award 8 (Event_Killed 18035c280, the award at 18035c3a3,
  a hostage's death): the attacker pawn's controller by 1801c8060, its current controller (+0xc98), else its
  original (+0xe14): the player playing the pawn pays (hostages.js killed: the attacker as is, not `credit`).
- The default MVP (18090bae0) skips m_bHasControlledBotThisRound; the defused MVP sends a controlling defuser to the
  default (winpanel.md 1809f1550).
- Dominations (1801c0e00 / 1801d79b0, death-notice.md): skipped for a controller controlling a bot.
- The fun facts' player filter (winpanel.md): the controller's own pawn (m_hPlayerPawn +0x8ec); a bot pawn whose
  controller has +0x8e2 is out; without filter bit 0x100 a controller with +0x8e1 is out. bots_assumed reads +0x8e4.
  The survival streak (180b1d1e0) is reset for a controller controlling a bot.
- Lag compensation: the pawn's FL_BOT stays on (nothing in the swap touches +0x388), and StartLagCompensation
  rewinds nobody for a bot pawn's command, so a player controlling a bot has no lag compensation.

## The client

- `bot_takeover`: C_CSPlayerPawn listens (180c5fcf0); its handler (180c77002) reads p / y / r and sets the view
  angles (180b80e70).
- CCSPlayerController slot 0x748 (18089ecb0) -> 180e88280: the local pawn's m_hOriginalController (+0x1560) when
  controlling: hudtakeoverbot.vxml's panel (JoinPanel--Animate-FadeIn / -FadeOut), label `#SFUI_Notice_Hint_Bot_Takeover`
  "You are playing as BOT {s:s1}", s1 = 18088b2b0 (the name). hudtakeoverbot.vcss: .hud-takeover-bot (bottom,
  centred, 18 px, translateY 16 -> 0, .25 s), .hud-takeover-bot__text (13 px white, hud-outline-shadow).
- The spectator legend (hudlegend.vxml, CCSGO_HudHealthAmmoCenter's constructor 180e78360 finds `HotKey_ControlBot`):
  `#PANOHUD_Spectate_Navigation_Control_Bot` "[{s:bind_use}] Control Bot " in .HudSpecplayer__key-hints-text (11 px,
  rgb 212). Its show / hide reads m_bCanControlObservedBot (client +0x928) in 180e928f0, below.
- The decorated name (teamid.md 1809049b0): a controller controlling a bot wears the BOT tag (vfn 0x20); a bot whose
  current pawn's original controller is someone else shows "(name)" as its puppeteer; the death notice names a
  controlling controller by its m_hOriginalControllerOfCurrentPawn (18089df60 / 18088ca80).

## The legend strip (client 180e928f0)

Called from 180e91fb0 (the observer HUD's update). With cl_spec_show_bindings (client 1800e4d60: bool, default 0,
flags 0x10080000, "Toggle the visibility of the spectator bindings.") off every label is hidden; on, a bit per
HotKeyLabelContainer label in its vxml order, each label getting HudSpecplayer__key-hints-text--hidden without its bit:

| bit | label | when |
| --- | --- | --- |
| 1 | HotKey_ControlBot | the watched player a bot you may control (controller +0x3f4 bit 8; 180e7bd90: m_bCanControlObservedBot) |
| 2 | HotKey_XRay | a caster / HLTV (180ce24d0) |
| 4 | HotKey_CancelReplay | in a killer replay |
| 8 | HotKey_Arrows | always |
| 0x10 | HotKey_Camera | mp_forcecamera (client handle 0x1825510d0) 0, or a spectator (team 1) |
| 0x20 | HotKey_Map | always |
| 0x40 / 0x80 | HotKey_CameramanOn / DirectorOn | HLTV cameraman / autodirector |
| 0x100 | HotKey_ReplayLastKill | a killer replay ready |
| 0x200 | HotKey_ViewHighlight | highlights |
| 0x400 | HotKey_InspectLoadout | always ("#PANOHUD_Spectate_Vanity_Loadout_Show") |

The strip's root (+0xc0) is at opacity 1 for 8 s after the UI's last input (UI engine 0x182733f40 vfn 0x1e8, read as
its last input time), then fades to 0 over 4.5 s. Port: client/modes/team/takeover-hud.js.

## The observer target (server)

CCSObserver_ObserverServices, vtable 0x18191ca48 (its base CPlayer_ObserverServices 0x181952910). Slots:

| slot | function | |
| --- | --- | --- |
| 0xb8 | GetObserverMode | m_iObserverMode (23 in the vtable's getter) |
| 0xe0 | SetObserverTarget 180a4fd00 | m_hObserverTarget (+0x4c) |
| 0xf8 | SetObserverMode 180a4f810 | |
| 0x100 | FindNextObserverTarget 180a433e0 | from the start point, each controller's player pawn (+0x8ec) +1 (reverse -1), wrapping, the first valid; none: the C4 / hostages (not watched here) |
| 0x108 | GetNextObserverSearchStartPoint 180a43f60 | the target dead with a living killer (pawn +0x1498 m_nLastKillerIndex): the killer's slot as is; the target invalid: the valid pawns ranked FInViewCone x 2 + IsLineOfSightClear from your eye, ties by the dot (180a42950), the best's slot as is; else the target's slot (or yours) +1 / -1, wrapping |
| 0x110 | IsValidObserverTarget 180a472b0 | a living pawn: not yours, and with mp_forcecamera (0x1821915e8) on, for an observer on a team, a teammate; a dead one: mp_forcecamera 1 and no hostage rescue (0x181fa48fc 0) with the whole team dead (180a881c0): a dead teammate; else only your current target, until m_flDeathTime (+0xc7c) + spec_freeze_deathanim_time + spec_freeze_traveltime + spec_freeze_time |

- FInViewCone 180cfe7c0: cos(fov / 2) of the camera services' FOV against the direction to the target's origin, centre,
  eye. IsLineOfSightClear 180cfef00 (-> 180cfed40, the world only): your eye to its centre, eye, origin.
- The spec_freeze cvars: storage 0x182171510 / 520 / 530 / 540, defaults spec_freeze_time 3.0, spec_freeze_traveltime
  0.3, spec_freeze_time_lock 1.0, spec_freeze_deathanim_time 0.8.
- The command handler 180c72900: spec_mode cycles 2 -> 3 -> 4 -> 2 (an argument outside 2..4 becomes 2); spec_next /
  spec_prev / spec_player only in an observer mode >= 2 (past the death cam): FindNextObserverTarget then
  SetObserverTarget.
- Port: server/cs2web/core/observer.js (the team modes; ZE keeps the client's own spectating), observer-test.mjs. The
  client's MOUSE1 / MOUSE2 while dead send `specnext` (rev for MOUSE2), and follow the server's `spectate`.
  Not ported: the chase camera (mode 3) and roaming (mode 4): the observer is in eye.

## The port's model

The observer target is the server's (core/observer.js above); the takeover checks it: a living bot's own pawn, its
brain on (no player controlling it). The port's
IsValidObserverTarget for a living pawn is 180a472b0's alive branch as read: mp_forcecamera 0 anyone, else a
teammate (the branch's further dynamic casts, for non-player targets, don't apply to a pawn).

A ZePlayer is a controller with its current pawn's state on it; bot-takeover.js PAWN_FIELDS is that state, swapped
between the two ZePlayers (swapPawns). The replicas' pawn entities trade ids / hooks / names (stimulus 'P', so each
pawn entity keeps its touches, targetname and outputs), the lag tracks trade names (ze_lag_swap), the pose workers'
graph keys trade (pose-pool.js swap). ZePlayer.pawnOwner is +0xe14, ZePlayer.credit the controller credited.
