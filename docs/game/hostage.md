# Hostage Rescue: CHostage, the carry, func_hostage_rescue, the round's rules and money, the HUD

server_20261105, client_20261015 (HUD). Cfgs: game/csgo/cfg gamemode_*.cfg. Sounds:
soundevents/vo/game_sounds_hostage.vsndevts. Origin: CS:GO's cs_simple_hostage.cpp (build path string 0x1817c33f0) moved
to Source 2: the hostage no longer walks after its leader; a CT carries it on the back (CHostageCarriableProp,
models/hostage/hostage_carry.vmdl) and a carrier touching a func_hostage_rescue rescues it at once.

"now" is gpGlobals' GameTime (180927cb0 / 180927d30); time compares use the three-way 18017e2d0 (-1 when b > a).

## Functions

| Address | Module | What |
|---|---|---|
| 1803629a0 | server | CHostage Spawn (vfn 0x48) |
| 180361ea0 | server | Precache (vfn 0x38): hostage.vmdl, hostage_carry.vmdl, v_hostage_arm.vmdl |
| 18035b000 | server | constructor (list append, max 12) |
| 180930450 | server | Think "CHostageHostageThink" (think table 18035c200) |
| 18035b4e0 | server | "CHostageHostageUse": `jmp [vtable + 0xac0]` |
| 180931160 | server | Use (vfn 0xac0) |
| 180361940 | server | OnTakeDamage (vfn 0x7f0) |
| 180361960 | server | OnTakeDamage_Alive (vfn 0x7f8) |
| 18035c280 | server | Event_Killed (vfn 0x418) |
| 180999de0 | server | CHostageRescueZone Spawn |
| 18099a860 -> 180994400 | server | zone Touch (vfn 0x4b8 -> vfn 0x8b8 "CHostageRescueZoneHostageRescueTouch", 180993010) |
| 18093e040 | server | deathmatch test (game_type 1 / game_mode 2) |
| 18093ec40 | server | warmup (gamerules +0xd9) |
| 180242350 | server | view offset set |
| 18091f260 | server | drop to the floor (hull) |
| 180957e50 | server | RestartRound (selection at 180958e9e..180959e90; random pick 180959a65..180959c60) |
| 180ac74c0 | server | the +use hint pick's CHostage branch (use.md) |
| 18093e5c0 | server | hostage alive and not rescued |
| 18093d400 | server | m_leader resolves |
| 180ac7120 | server | the use pick (flag 0x2000000) |
| 180ae9bd0 | server | look test (mode 1, use.md) |
| 180ca7f40 / 180ca8180 | server | hint to the controller (type 4) / another hint print |
| 180ac8960 | server | item services: has a defuse kit |
| 180ae21a0 | server | progress bar (pawn, length) |
| 180abee60 | server | progress bar end (pawn, 2 finished / 1 cancelled) |
| 180231040 | server | script event OnHostagePickUpStart |
| 180f975a0 | server | stop a sound (the cut-free guid) |
| 18096b150 | server | physics step with m_vel / m_accel (outline only) |
| 18035b640 | server | (Think's step, unread) |
| 180362550 | server | the drop to the ground (hostage, ground) |
| 1803ebce0 | server | (hostage, 0, 0) on entering state 3 |
| 1809610f0 | server | the touch / carry (hostage, user) |
| 18035d1b0 | server | AddTeamAccount(3, 0xe, ...) |
| 180b006f0 | server | player award (controller, kind) |
| 180b00730 | server | player award with an amount (account, 7, ..) |
| 1801fc0c0 | server | contribution score |
| 180239eb0 | server | radio line (auto) |
| 180923710 | server | the pickup |
| 180a7af40 | server | CCSPlayer_HostageServices: carry (services, hostage) |
| 180d0e200 | server | effects |= (+0x5e8, 1): EF_NODRAW-like |
| 1803ebc00 | server | set parent |
| 1803d6ab0 | server | bones follow (.., 1) |
| 180b556c0 -> 180b76fb0 | server | skin copy |
| 180adf830 | server | PlayerMove (max speed at 180adfa2d..180adfb3d) |
| 180ab60d0 | server | carried hostage resolves |
| 18035bc40 | server | drop (hostage, at, rescued) |
| 180b05460 | server | death drop (calls 18035bc40 at 180b05dc0) |
| 180a99600 | server | services: clear m_hCarriedHostage, remove the prop |
| 180c2e710 | server | hull trace |
| 18023b020 | server | CCSPlayerPawn OnRescueZoneTouch |
| 18093df90 | server | mode has hostages |
| 1803561b0 -> 18035d350 | server | CHostage_API OnRescueZoneTouch -> the rescue |
| 180911880 | server | gamerules broadcast sound |
| 180917420 | server | CheckWinConditions |
| 18095f480 | server | rescue contribution scores |
| 180930260 | server | the rescue win (CheckWinConditions' tail) |
| 180916fb0 | server | the clock's win |
| 1809124d0 | server | round money list (TerminateRound -> 18095c3c0) |
| 180964f60 | server | team money table |
| 180952190 | server | player money table |
| 18090e220 | server | team money {team, reason} pairs (c4.md "The round") |
| 18093d7b0 | server | gamerules +0x132 (buy menu sells item_cutters: buy.md) |
| 180b67140 / 180b67340 | server | base OnTakeDamage / OnTakeDamage_Alive |
| 18095f460 | server | cash_player_killed_hostage |
| 1802c4c50 | server | info_hostage_rescue (bots' nav goals, unread) |
| 180e7d5d0 | client | CCSGO_HudGameIcons constructor |
| 180e8d230 | client | HudGameIcons round start |
| 180e92590 | client | HudGameIcons update |

## Classes

| Class | vtable | Notes |
|---|---|---|
| CHostage (hostage_entity, alias info_hostage_spawn) | 0x1817c1bc8 | |
| CHostageCarriableProp (hostage_carriable_prop) | 0x1817c11b8 | the back prop |
| CHostageRescueZone (func_hostage_rescue) | 0x1818de278 | |
| CHostageRescueZoneShim | 0x1818dd9a0 | |
| CCSPlayer_HostageServices | 0x1819216e8 | pawn +0xe38 (m_pHostageServices) |
| CTriggerHostageReset (trigger_hostage_reset) | 0x1817a0ed8 | unread (cs_office / cs_italy / cs_shelter have none: unchecked) |

## Fields

| Offset | Field |
|---|---|
| CHostage 0xb38 / 0xb50 / 0xb68 / 0xb80 | m_OnHostageBeginGrab / m_OnFirstPickedUp / m_OnDroppedNotRescued / m_OnRescued |
| 0xb98 | m_entitySpottedState |
| 0xbb0 | m_nSpotRules |
| 0xbb4 | m_uiHostageSpawnExclusionGroupMask |
| 0xbb8 | m_nHostageSpawnRandomFactor (1 at construction) |
| 0xbbc | m_bRemove (list full) |
| 0xbc0 | m_vel |
| 0xbcc | m_isRescued |
| 0xbcd | m_jumpedThisFrame |
| 0xbd0 | m_nHostageState |
| 0xbd4 | m_leader (the carrier) |
| 0xbd8 | m_lastLeader |
| 0xbe0 | m_reuseTimer (CountdownTimer: +8 duration, +0xc timestamp, +0x10 rate) |
| 0xbf8 | m_hasBeenUsed |
| 0xbfc | m_accel |
| 0xc08 / 0xc09 | m_isRunning / m_isCrouching |
| 0xc10 | m_jumpTimer |
| 0xc28 | m_isWaitingForLeader |
| 0x2c38 / 0x2c50 / 0x2ce0 / 0x2d00 | m_repathTimer / m_inhibitDoorTimer / m_inhibitObstacleAvoidanceTimer / m_wiggleTimer |
| 0x2d1c | m_isAdjusted |
| 0x2d1d | m_bHandsHaveBeenCut |
| 0x2d20 | m_hHostageGrabber |
| 0x2d24 | m_fLastGrabTime |
| 0x2d28 | m_flGrabStartTime |
| 0x2d2c | m_vecPositionWhenStartedDroppingToGround |
| 0x2d38 | m_vecGrabbedPos |
| 0x2d44 | m_flRescueStartTime |
| 0x2d48 | m_flGrabSuccessTime |
| 0x2d4c | m_flDropStartTime |
| 0x2d50 | m_nApproachRewardPayouts (4 at Spawn) |
| 0x2d54 | m_nPickupEventCount |
| 0x2d58 | m_vecSpawnGroundPos |
| 0x2d64 / 0x2d78 | the two cut-free sounds' guids |
| 0x2d8c | the pain line's last time |
| 0x2d90 | m_vecHostageResetPosition |
| 0x181faab70 / 0x181faab78 | hostage list CUtlVector count / data (max 12) |
| HostageServices +0x48 / +0x4c | m_hCarriedHostage / m_hCarriedHostageProp |
| CCSPlayerPawn 0xf91 | m_bInHostageRescueZone (client +0x15e8) |
| CCSPlayerPawn 0x14bf | m_bIsGrabbingHostage |
| CCSPlayerPawn 0x14c0 | (also forces max speed 1) |
| CCSPlayerPawn +0x1488 / +0x291*8 | once-only hint bits: 0x20000 rescue zone, 0x20 careful, 0x40 lost money, 0x200000 only CT |
| pawn +0x344 | team (3 CT) |
| movement services +0x58 | buttons (IN_USE, 0x100000000) |
| controller +0x1c9*8 = 0xe48 | action tracking services: +0x218 hostages carried (count), +0x224 picked-up flag (stats), +0x21c (written on a player's hostage damage; meaning unread) |
| controller +0x48 | radio line timer (10 s) |
| controller +0x7f8 +0x1b8 | counter + 1 on carry |
| CCSGameRules 0x12c | m_iHostagesRemaining |
| 0x130 | m_bAnyHostageReached |
| 0x131 | m_bMapHasBombTarget |
| 0x132 | m_bMapHasRescueZone |
| 0xd78 | m_bHasHostageBeenTouched |
| 0xda8 / 0xdb0 | m_arrSelectedHostageSpawnIndices count / data |
| 0xeb0 | m_iHostagesRescued |
| 0xeb4 | m_iHostagesTouched |
| 0xeb8 | m_flNextHostageAnnouncement |
| 0xed0 / 0xed8 | rescuers' handles (unique) |
| 0xee8 / 0xee9 | m_hostageWasInjured / m_hostageWasKilled |
| 0xa44 | m_iRoundWinStatus |
| 0x100 | m_iRoundTime |
| +0xe28 | CheckWinConditions context (the MVP) |
| zone +0x9b4 | disabled |
| 0x181faab88 | static CountdownTimer (Event.HostageRescued, 2 s) |
| 0x1817c3508 | HostageSpawnExclusionGroup1..32 key table |

## Constants

| Cvar | Default | Read by |
|---|---|---|
| mp_hostages_max | 2 | RestartRound's selection |
| mp_hostages_spawn_farthest | 0 | the selection |
| mp_hostages_spawn_same_every_round | 1 | the selection; Spawn (a warmup spawn without it is skipped) |
| mp_hostages_spawn_force_positions | "" | the selection ("0,2": zero-based indices) |
| mp_hostages_spawn_force_positions_xyz | "" | the selection ("x y z,x y z": the nearest hostage to each) |
| mp_hostages_run_speed_modifier | 1.0 (0.1 .. 1.5) | the follow movement (unused by a carried hostage) |
| mp_hostages_rescuetowin | 1 | the rescue win ("0 == all alive, any other number is the number the CT's need to rescue") |
| mp_hostages_rescuetime | 0 | m_bAnyHostageReached's round time bonus (minutes) |
| mp_hostages_takedamage | 0 | OnTakeDamage: DFLAG_SUPPRESS_HEALTH_CHANGES |
| mp_only_cts_rescue_hostages | 1 | Use / the touch |
| mp_roundtime_hostage | 60 (max) | the round's length on a hostage map ("If 0 then use mp_roundtime") |
| sv_cs_player_speed_has_hostage | 200 | PlayerMove (0x182175708) |
| hostage_drop_time | 1.0 | the drop to the ground (0x181faaac0) |
| hostage_is_silent | 0 | the response rules lines (0x18211a720) |
| hostage_debug | 0 | Use's T branch |
| cash_team_elimination_hostage_map_t / _ct | 1000 / 2000 | team reason 2 / 3 |
| cash_team_win_by_time_running_out_hostage | 3250 | reason 5 |
| cash_team_win_by_hostage_rescue | 3500 | reason 8 |
| cash_team_rescued_hostage | 0 | reason 0xb (per rescued, at the round's end) |
| cash_team_hostage_alive | 0 | reason 0xc (per live unrescued, to the winner) |
| cash_team_hostage_interaction | 500 | reason 0xe (first touch of a hostage) |
| cash_player_rescued_hostage | 1000 | player award 5 |
| cash_player_interact_with_hostage | 150 | award 6 |
| cash_player_damage_hostage | -30 | award 7 (per point of damage) |
| cash_player_killed_hostage | -1000 | award 8 |
| contributionscore_hostage_rescue_minor / _major / _kill | 1 / 3 / -2 | scoreboard |

Cfgs (gamemode_competitive / competitive2v2 / casual): elimination T 3000 / 2500 / 2000, CT 3000 / 2500 / 2300; time
3250 / 2750 / 2000; rescue win 2900 / 2900 / 3000; rescued 600 / 600 / 0; interaction 600 / 600 / 500; alive 0; player
rescued 1000, interact 300, damage -30, killed -1000; mp_roundtime_hostage 1.92 / 1.5 / 2. None sets an mp_hostages_*.

Team money table 180964f60 (reason -> cvar): 1 terrorist_win_bomb, 2 elimination_hostage_map_t, 3
elimination_hostage_map_ct, 4 elimination_bomb_map, 5 win_by_time_running_out_hostage, 6 _bomb, 7 win_by_defusing_bomb,
8 win_by_hostage_rescue, 9 loser_bonus, 10 loser_bonus_consecutive_rounds, 0xb rescued_hostage, 0xc hostage_alive, 0xd
planted_bomb_but_defused, 0xe hostage_interaction, 0x11 (0x18211a250), 0x12 bonus_shorthanded. Player table 180952190: 1
killed_enemy?, 2 / 0xb, 3, 4, 5 rescued_hostage, 6 interact_with_hostage, 7 damage_hostage, 8 killed_hostage, 9, 10.

| Value | What |
|---|---|
| 0x2000000 | entity flag: high-priority use pick (use.md) |
| 0xc3011 | hostage interacts-with |
| 0x10000000000 | collision group bit while carried |
| (0, 0, 35) | view offset (EyePosition) |
| (-8, -8, 0) .. (8, 8, 64) | hull |
| 100 | max health / health |
| 62 / 32 / -0.7 / -0.5 | use reach (+0x1c) / no line needed within (+0x20) / cones (+0x24 / +0x28) |
| 1000 u (1e6 squared) | Use's distance |
| 1.0 s / 4.0 s | grab with kit or cut hands / without |
| 1/60 (1/45 with a leader) | think interval |
| 0.05 s | grab hold grace |
| 0.1 s, (0, 0, 40) | lift onto the back |
| 0.25 s | dropped -> idle |
| 4 s | rescued -> not solid |
| 500 | drop trace length |
| 60 s / 10 s / 2 s | next announcement / radio line / rescued sound |

## States (m_nHostageState)

0 idle (usable), 1 being grabbed (a CT holding +use), 2 picked up (0.1 s lift), 3 carried, 5 dropped (0.25 s, then 0), 6
rescued, 7 dead. 4 is never stored.

## Spawn (1803629a0) / constructor (18035b000)

- Constructor: appends to the list (max 12, else DevMsg "The maximum number of hostages (%i) has been exceeded." and
  m_bRemove); mask 0, random factor 1.
- Spawn: keyvalues HostageSpawnExclusionGroup1..32 (bit n-1) and HostageSpawnRandomFactor (clamped 1..100). No hostages
  in deathmatch (18093e040); none in a warmup unless mp_hostages_spawn_same_every_round; m_bRemove: UTIL_Remove.
- models/hostage/hostage.vmdl; collision from the model's bounds (or the default hull), SOLID 8, interacts-with 0xc3011;
  flag 0x2000000; health 100; gravity 1.0; view offset (0, 0, 35) (180242350); think at now + 1/60; the use callback;
  dropped to the floor (18091f260, hull (-8, -8, 0) .. (8, 8, 64)); m_vecSpawnGroundPos; m_nApproachRewardPayouts 4;
  every state and time cleared.

## RestartRound's selection (after CleanUpMap)

When the list holds more than mp_hostages_max:

1. Without mp_hostages_spawn_same_every_round, m_arrSelectedHostageSpawnIndices is emptied.
2. A stored selection (count != 0): every hostage whose index isn't in it is removed (from the back).
3. Else mp_hostages_spawn_force_positions "a,b": those indices kept, the rest removed; _xyz "x y z,...": per point the
   nearest hostage (3D squared, first of equals) kept (malformed point: a warning); mp_hostages_spawn_farthest: every
   combination of mp_hostages_max indices (lexicographic from 0..max-1) scored by the sum of the pairs' squared 2D
   distances, the first with the largest kept.
4. Else the random pick: while fewer than the max picked and some remain: total = Σ m_nHostageSpawnRandomFactor; 0
   stops; r = RandomInt(0, total - 1); the first whose factor is above r (r less each factor passed) moves to the
   picks; with an exclusion mask, every other remaining hostage sharing a bit is removed (from the back). Then the rest
   removed, the list is the picks.
5. Still more than the max: RandomInt(0, n - 1) removed until it fits.
6. With an empty stored selection, the kept indices (into the list at the start) are stored, console "Selected %d
   hostage positions '...'".

## +use: the hint and Use (180931160)

Hint (180ac74c0's CHostage branch): only for a CT, the hostage alive and not rescued (18093e5c0), no leader (18093d400),
no other live connected grabber (m_hHostageGrabber a pawn other than the user, alive, its controller in state 0 or 3),
not in warmup; priority 1, type 0 (3D distance), the point its EyePosition (origin + 35), reach 62, no line within 32,
cones -0.7 / -0.5. Found through flag 0x2000000. A T never gets one.

Use (continuous: every command with +use):

1. User a player pawn (vfn 0x558), vfn 0xca8, alive (vfn 0x550). Warmup: hint
   `#Cstrike_TitlesTXT_Cannot_Move_Hostages_Warmup` (180ca7f40 type 4), nothing else.
2. Squared distance > 1e6 (`(dy dy + dx dx) + dz dz`): nothing.
3. Already carrying: `#Cstrike_TitlesTXT_CanOnlyCarryOneHostage` (180ca8180).
4. A T with mp_only_cts_rescue_hostages: 1809610f0 (its T branch prints `#Cstrike_TitlesTXT_Only_CT_Can_Move_Hostages`
   once).
5. State 1: grabber is the user: m_fLastGrabTime = now; another: `#Cstrike_TitlesTXT_SomeonePickingUpHostage`.
6. Else the grab starts: defuse kit (180ac8960) or m_bHandsHaveBeenCut: 1.0 s, `Hostage.CutFreeWithDefuser`; else 4.0 s,
   `Hostage.CutFreeWithoutDefuser` (from the hostage to everyone, guid kept); m_flGrabSuccessTime = now + length;
   180ae21a0(pawn, length); grabber = user; state 1; m_bIsGrabbingHostage = 1; m_fLastGrabTime = m_flGrabStartTime =
   now; m_OnHostageBeginGrab (activator the user); OnHostagePickUpStart (180231040); next think now.

## Think (180930450)

- m_jumpedThisFrame cleared. First think: m_isAdjusted, bounds (-8, -8, 0) .. (8, 8, 64).
- Next think: state 1 every tick; else now + 1/60 (1/45 with a leader).
- State 1 with a grabber:
  - now >= m_flGrabSuccessTime and grabber alive: `Hostage.PickUp`, m_bIsGrabbingHostage 0, 1809610f0(hostage,
    grabber), 180abee60(pawn, 2), grabber cleared, m_vecGrabbedPos = origin, state 2; OnHostagePickUp when the leader is
    the grabber.
  - Else it goes on while the grabber holds IN_USE or 0x100000000 (or within 0.05 s of m_fLastGrabTime), still looks at
    it (180ac74c0's entity is this hostage and 180ae9bd0 mode 1), and is FL_ONGROUND. Off the ground (alive):
    `#SFUI_Notice_Hostage_Pickup_Must_Be_On_Ground`. Otherwise the abort: 180abee60(pawn, 1), m_bIsGrabbingHostage 0,
    state 0, the cut-free sound stopped (180f975a0), grabber cleared, OnHostagePickUpAbort.
- Other states (and state 1 without a grabber): the nav area; 18096b150 (a still hostage's velocity decays by 4 x dt
  and snaps to 0 under 1 u/s); 18035b640; 180362550; the reset position follows a leader on the ground. Then:
  - State 2: SOLID_NONE, flags 0, use callback off, 0x2000000 off; for 0.1 s after m_flGrabSuccessTime lerp from
    m_vecGrabbedPos to the leader's origin + (0, 0, 40) (t = `(now - success) / 0.1`, each axis
    `(target - from) * t + from`); after: state 3, 1803ebce0(hostage, 0, 0).
  - State 5 after m_flDropStartTime + 0.25: state 0, SOLID 2 (bbox), collision group 8, the use callback, 0x2000000, the
    solid flags | 1.
  - State 6 4 s after m_flRescueStartTime: SOLID_NONE, flags 0, 0x2000000 off (stays where it was put down).

Drop to the ground 180362550(hostage, ground): while now < m_flDropStartTime + hostage_drop_time: from =
m_vecPositionWhenStartedDroppingToGround, floor = 18091f260 (16 x 16 x 64 hull); as decompiled: d = `|floor - from| *
((hostage_drop_time + start - now) / hostage_drop_time)`; `|floor - ground| <= d` ? the ground point : `floor +
normalize(ground - floor) * d`. Once past it (and not state 5): dropped to the floor, m_flDropStartTime = 0.

## The touch (1809610f0) and the pickup (180923710)

1809610f0(hostage, user), for a CT (or anyone without mp_only_cts_rescue_hostages, or with hostage_debug):

1. A dead leader is cleared.
2. Reuse timer elapsed: the first use (m_hasBeenUsed): CT team gets cash_team_hostage_interaction (18035d1b0) and the
   user award 6 (180b006f0); the user's contributionscore_hostage_rescue_minor (1801fc0c0); m_flNextHostageAnnouncement
   = now + 60 when passed and the round not won; m_bHasHostageBeenTouched; a human's radio "EscortingHostages" /
   `#Cstrike_TitlesTXT_Got_Hostages` (180239eb0) at most every 10 s; m_bHandsHaveBeenCut = 1; m_OnFirstPickedUp. Every
   use: m_nSpotRules |= 4 & ~0x20; first touch of the round: m_bAnyHostageReached and, not won, m_iRoundTime +=
   `mp_hostages_rescuetime * 60` and the `#hostagerescuetime` centre text.
3. User already the leader: leader cleared, "StopFollowing"; another live leader: nothing; else 180923710. Reuse timer
   restarts.

T branch (no hostage_debug): `#Cstrike_TitlesTXT_Only_CT_Can_Move_Hostages` once (+0x1488 0x200000).

180923710: controller count +1 (+0x218), +0x224 = 1; "StartFollowing" (response rules, leaderteam:CT, unless
hostage_is_silent); `hostage_follows` (userid, hostage = entindex, priority 5), m_nPickupEventCount + 1; m_leader /
m_lastLeader = user, m_isWaitingForLeader 0; 180a7af40; collision group bit 0x10000000000; log "picked up a hostage".

180a7af40: m_hCarriedHostage = hostage; hostage effects |= 1 (180d0e200(+0x5e8, 1)); unless a prop exists,
hostage_carriable_prop spawned at the pawn's origin, model models/hostage/hostage_carry.vmdl, parented (1803ebc00) with
bones following (vfn 0x1b0, 1803d6ab0(.., 1)), skin copied (180b556c0 -> 180b76fb0); m_hCarriedHostageProp; carrier hint
`#Cstrike_TitlesTXT_CarryingHostage`. Controller +0x7f8 +0x1b8 + 1.

## The carrier's movement (PlayerMove 180adf830)

mv+0x120 (max speed) = min(260, svc+0x1ac when 0 < it < sv_maxspeed, else sv_maxspeed); with a carried hostage
(180ab60d0) = sv_cs_player_speed_has_hostage (200); then min(active weapon vfn 0xc20). It is 1.0 instead when dead, move
type not 0 / 6, m_bIsDefusing, m_bIsGrabbingHostage, pawn+0x14c0, or the freeze period (the Valve-server exception
aside). Accelerate's walk `s * 0.52` (movement.md) is skipped while carrying.

## Dropping: 18035bc40(hostage, at, rescued)

- Carrier's death: 180b05460 (at 180b05dc0: handle live and count > 0) with the pawn's abs origin and 0; the rescue
  with the carrier's origin and 1.
- m_lastLeader cleared; with a leader: its count - 1, 180a99600; not rescued: m_OnDroppedNotRescued, SOLID 2, group 8,
  bit 0x10000000000 off, the use callback, solid flags | 1, "StopFollowing", state 5, m_flDropStartTime = now.
- Log "dropped off a hostage"; m_leader cleared; trace (180c2e710, the hull, interacts-with 0xc3001, group 5) from `at`
  to at - (0, 0, 500): m_vecPositionWhenStartedDroppingToGround = at, or the end when it hit (and the hostage put
  there); gravity 1.0; next think now; OnHostageDrop (not rescued).

## The rescue

- func_hostage_rescue's touch (180994400, unless +0x9b4) fires "OnRescueZoneTouch" at the toucher. 18023b020: in a
  mode with hostages (18093df90), m_bInHostageRescueZone = 1, a CT's hint `#Cstrike_TitlesTXT_Hint_hostage_rescue_zone`
  once (+0x1488 0x20000), and the carried hostage gets "OnRescueZoneTouch" -> 1803561b0 -> 18035d350. A hostage on the
  ground in a zone isn't rescued.
- 18035d350: once (m_isRescued); m_lastLeader = leader; use callback off; the leader's count - 1, m_OnRescued, the drop
  at the carrier's origin (rescued 1); SOLID_NONE; m_flRescueStartTime = now, state 6; OnHostageRescue;
  `Event.HostageRescued` to everyone (180911880) at most every 2 s (0x181faab88); rescuer award 5; `hostage_rescued`
  (userid, hostage, site 0, priority 5); m_iHostagesRescued + 1, rescuer added to +0xed0; not won: CheckWinConditions
  (180917420) with the rescuer as +0xe28; then 18095f480 (the rescuer's _major (3) when the rescue won, else _minor;
  every other live CT's _minor) and the round stats.
- Rescue win 180930260: n = hostages; alive = health > 0 and not rescued; need = mp_hostages_rescuetowin when non-zero
  and <= n, else n; m_iHostagesRemaining = alive; CTs win when `m_iHostagesRescued >= need && alive >= n - need` (and n
  > 0): `hostage_rescued_all`, TerminateRound(reason 11 HostagesRescued, {(CT, 8 WIN_BY_HOSTAGE_RESCUE)},
  mp_round_restart_delay).
- cash_player_rescued_hostage (award 5) to the rescuer (via 180b006f0(controller, 5); its award table unread).

## The round

- Elimination (180917420): on a map without a bomb target the Ts' win (reason 9) pays {(T, 2)}
  cash_team_elimination_hostage_map_t, the CTs' (reason 8) {(CT, 3)} cash_team_elimination_hostage_map_ct (bomb maps:
  4). No planted-bomb hold.
- Clock (180916fb0): mp_default_team_winner_no_objective -1, no bomb target, m_bMapHasRescueZone: Ts win, reason 13
  HostagesNotRescued, {(T, 5)}.
- Money list 1809124d0: the winner's pairs; then over the hostage list (health >= 1 and not rescued adds
  cash_team_hostage_alive; rescued counts; stops once the alive sum is over 1999): winner gets (0xc, alive sum), loser
  its loss bonus (9), CTs always (0xb, `cash_team_rescued_hostage * rescued`).
- Round time: mp_roundtime_hostage (0: mp_roundtime). The kit sells as item_cutters on a hostage map.

## Damage

- OnTakeDamage 180361940: without mp_hostages_takedamage the info's flags (+0x70) |= 1 (DFLAG_SUPPRESS_HEALTH_CHANGES):
  never loses health; then 180b67140.
- OnTakeDamage_Alive 180361960: 180b67340, the "Pain" line (every 2 s, unless hostage_is_silent); player attacker:
  controller +0x21c, m_hostageWasInjured; v = cash_player_damage_hostage (award 7); non-zero: hint
  `#Cstrike_TitlesTXT_Hint_careful_around_hostages` once (+0x1488 0x20), `hostage_hurt` (userid, hostage, priority 5),
  the attacker pays `min(health, (int) damage) * v` (180b00730(account, 7, ..)), damage = result +0x20 truncated.
- Event_Killed 18035c280: leader's count - 1, CheckWinConditions, m_hostageWasKilled; player attacker: 18095f460 and
  `#Cstrike_TitlesTXT_Hint_lost_money` once (+0x1488 0x40), award 8; use callback off, the base, `hostage_killed`
  (userid, hostage, priority 5), state 7, OnHostageKill.

## The HUD (client)

- CCSGO_HudGameIcons (180e7d5d0; panorama/layout/hud/hudgameicons.xml under #HudTopLeft beside the radar; listens to
  hostage_rescued and round_start): 180e8d230 clears `hud-game-icons--mode-hostage`, `--hostage-rescue-zone` and every
  icon's classes. Update 180e92590: `--hostage-rescue-zone` = local (or observed) pawn's m_bInHostageRescueZone
  (+0x15e8); over the 4 icon panels and the player resource's m_iHostageEntityIDs: slot marked rescued (+0x7c + i, set
  by hostage_rescued) counts rescued; else m_bHostageAlive[i] false dead; else m_isHostageFollowingSomeone[i] carried,
  else alive. Filled rescued first, then carried, alive, dead: each `--active` with `--carried` / `--rescued` / `--dead`;
  the rest lose `--active`. hudgameicons.vcss: 34 x 36 icons, the transit icon's 0.8 s wash loop, the zone icon.
- Progress bar `hud-progress-bar__pickup-hostage` (hudprogressbar.vcss: transit icon, hud-progress-bar-hostage-animate)
  and `__drop-hostage`; labels #SFUIHUD_InfoPanel_HostageText.

## Sounds and events

Sound events: Hostage.Pain, Hostage.StartFollowCT, Hostage.StartFollowCTGuardian, Hostage.CutFreeWithDefuser,
Hostage.CutFreeWithoutDefuser, Hostage.PickUp, Hostage.Drop, Hostage.Breath (client); Event.HostageRescued (gamerules
broadcast); Music.GotHostage (client). Game events: hostage_follows, hostage_hurt, hostage_killed, hostage_rescued,
hostage_rescued_all. Radio: "EscortingHostages" (#Cstrike_TitlesTXT_Got_Hostages) through the agents' VO.

## Unread

- 18096b150 / 18035b640 in detail (a carried hostage doesn't run them).
- The player award table (180b006f0 / 180b00730: kinds 5 / 6 / 7 / 8 into money), taken as the cash_player_* values.
- RandomInt's stream (vstdlib's uniform random).
- The hostage's response rules lines (StartFollowing / StopFollowing / Pain: its talker script).
- Who sets `--mode-hostage` (taken as: the map has a rescue zone); the progress bar's text pick.
- Client C_Hostage (animation, Hostage.Breath, the carried prop's graph, OnHostageStateChanged), v_hostage_arm.vmdl.
- trigger_hostage_reset, info_hostage_rescue (1802c4c50) and the bots' hostage behaviour.
