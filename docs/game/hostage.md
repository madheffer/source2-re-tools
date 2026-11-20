# Hostage Rescue: CHostage, the carry, func_hostage_rescue, the round's rules and money, the HUD

server_20261105.dll (2026-11-16, "hostage"), with client_20261015.dll for the HUD. CS2's hostage is CS:GO's
cs_simple_hostage.cpp (the build path string at 0x1817c33f0) moved to Source 2: it no longer walks after its leader,
a CT **carries it on the back** (CHostageCarriableProp, models/hostage/hostage_carry.vmdl) and a carrier touching a
func_hostage_rescue rescues it at once. Addresses are functions unless said otherwise; "now" is gpGlobals' GameTime
(180927cb0 / 180927d30), compares the GameTime three-way 18017e2d0 (-1 when b > a).

Ported (2026-11-16): web/server/cs2web/modes/team/hostage/ (hostages.js the entities and their think, hostage-select.js
RestartRound's spawn selection, rescue-zones.js the zones), comp.js (the variant, the money, the win paths), use-hint.js
(the hint's CHostage branch), move-sim.js / sim (the carrier's speed, Accelerate's walk skip), the client's
client/modes/team/hostage-view.js (the models, the carry prop, the sounds) and hostage-icons.js (CS2's HudGameIcons).
Assets: lasers-bake --hostage (bake/HostageBake.cs -> web/public/ze-hostage). Test: `node
web/server/cs2web/modes/team/official-maps-test.mjs cs_office cs_italy cs_shelter [--replica]` (a grab, the carry, a
rescue winning the round). Stand-ins: each file's header and "Still unread" below.

## Classes, vtables, fields

| Class | vtable (RTTI, tools/re/game/rtti.py) | Notes |
|---|---|---|
| CHostage (hostage_entity, alias info_hostage_spawn) | 0x1817c1bc8 | Spawn vfn 0x48 = **1803629a0**; Precache vfn 0x38 = 180361ea0 (hostage.vmdl, hostage_carry.vmdl, v_hostage_arm.vmdl); constructor **18035b000**; Think **180930450** ("CHostageHostageThink", the think table 18035c200); Use 18035b4e0 ("CHostageHostageUse": `jmp [vtable + 0xac0]`) -> vfn 0xac0 = **180931160**; OnTakeDamage vfn 0x7f0 = **180361940**; OnTakeDamage_Alive vfn 0x7f8 = **180361960**; Event_Killed vfn 0x418 = **18035c280** |
| CHostageCarriableProp (hostage_carriable_prop) | 0x1817c11b8 | the back prop |
| CHostageRescueZone (func_hostage_rescue) | 0x1818de278 | Spawn vfn 0x48 = 180999de0; Touch vfn 0x4b8 = 18099a860 -> vfn 0x8b8 = **180994400** ("CHostageRescueZoneHostageRescueTouch", 180993010) |
| CHostageRescueZoneShim | 0x1818dd9a0 | |
| CCSPlayer_HostageServices | 0x1819216e8 | the pawn's +0xe38 (m_pHostageServices) |
| CTriggerHostageReset (trigger_hostage_reset) | 0x1817a0ed8 | not ported (none of the three maps has one: TODO(check)) |

Fields (tools/re/game/schema.py):

- **CHostage**: m_OnHostageBeginGrab 0xb38, m_OnFirstPickedUp 0xb50, m_OnDroppedNotRescued 0xb68, m_OnRescued 0xb80,
  m_entitySpottedState 0xb98, m_nSpotRules 0xbb0, **m_uiHostageSpawnExclusionGroupMask 0xbb4**, **m_nHostageSpawnRandomFactor
  0xbb8** (1 at construction), m_bRemove 0xbbc (set when the 12-hostage list is full), m_vel 0xbc0, **m_isRescued 0xbcc**,
  m_jumpedThisFrame 0xbcd, **m_nHostageState 0xbd0**, **m_leader 0xbd4** (the carrier), m_lastLeader 0xbd8, m_reuseTimer 0xbe0
  (a CountdownTimer: +8 duration, +0xc timestamp, +0x10 rate), **m_hasBeenUsed 0xbf8**, m_accel 0xbfc, m_isRunning 0xc08,
  m_isCrouching 0xc09, m_jumpTimer 0xc10, m_isWaitingForLeader 0xc28, m_repathTimer 0x2c38, m_inhibitDoorTimer 0x2c50,
  m_inhibitObstacleAvoidanceTimer 0x2ce0, m_wiggleTimer 0x2d00, **m_isAdjusted 0x2d1c**, **m_bHandsHaveBeenCut 0x2d1d**,
  **m_hHostageGrabber 0x2d20**, **m_fLastGrabTime 0x2d24**, m_flGrabStartTime 0x2d28,
  **m_vecPositionWhenStartedDroppingToGround 0x2d2c**, **m_vecGrabbedPos 0x2d38**, **m_flRescueStartTime 0x2d44**,
  **m_flGrabSuccessTime 0x2d48**, **m_flDropStartTime 0x2d4c**, m_nApproachRewardPayouts 0x2d50 (4 at Spawn),
  m_nPickupEventCount 0x2d54, m_vecSpawnGroundPos 0x2d58, (0x2d64 / 0x2d78 the two cut-free sounds' guids),
  (0x2d8c the pain line's last time), m_vecHostageResetPosition 0x2d90. The hostage list: a CUtlVector at
  **0x181faab70** (count) / 0x181faab78 (data), max 12 (18035b000: DevMsg "The maximum number of hostages (%i) has been
  exceeded.", m_bRemove).
- **CCSPlayer_HostageServices**: **m_hCarriedHostage +0x48**, **m_hCarriedHostageProp +0x4c**.
- **CCSPlayerPawn**: m_bInHostageRescueZone 0xf91, **m_bIsGrabbingHostage 0x14bf**; the hint bits +0x1488 (0x20000 the
  rescue zone's), +0x1488 / +0x291*8 bits 0x20, 0x40, 0x200000 (the once-only hints below).
- **CCSPlayerController** (+0x1c9*8 = 0xe48 the action tracking services): +0x218 the hostages it carries (count),
  +0x224 a "picked up a hostage" flag (stats).
- **CCSGameRules**: m_iHostagesRemaining 0x12c, **m_bAnyHostageReached 0x130**, m_bMapHasBombTarget 0x131,
  **m_bMapHasRescueZone 0x132**, m_bHasHostageBeenTouched 0xd78, **m_arrSelectedHostageSpawnIndices 0xda8** (count; data
  0xdb0), **m_iHostagesRescued 0xeb0**, m_iHostagesTouched 0xeb4, **m_flNextHostageAnnouncement 0xeb8**, (0xed0 / 0xed8
  the rescuers' handles, unique), m_hostageWasInjured 0xee8, m_hostageWasKilled 0xee9, m_iRoundWinStatus 0xa44,
  m_iRoundTime 0x100.

## Cvars (tools/re/game/cvardump.py; the defaults the registrations store)

| Cvar | Default | Read by |
|---|---|---|
| mp_hostages_max | 2 | RestartRound's selection |
| mp_hostages_spawn_farthest | 0 | the selection |
| mp_hostages_spawn_same_every_round | 1 | the selection; Spawn (a warmup spawn without it is skipped) |
| mp_hostages_spawn_force_positions | "" | the selection ("0,2": zero-based indices) |
| mp_hostages_spawn_force_positions_xyz | "" | the selection ("x y z,x y z": the nearest hostage to each) |
| mp_hostages_run_speed_modifier | 1.0 (0.1 .. 1.5) | the follow movement (unused by a carried hostage) |
| mp_hostages_rescuetowin | **1** | the rescue win ("0 == all alive, any other number is the number the CT's need to rescue") |
| mp_hostages_rescuetime | 0 | m_bAnyHostageReached's round time bonus (minutes) |
| mp_hostages_takedamage | **0** | OnTakeDamage: DFLAG_SUPPRESS_HEALTH_CHANGES |
| mp_only_cts_rescue_hostages | 1 | Use / the touch (CHostage 1809610f0) |
| mp_roundtime_hostage | 60 (max) | the round's length on a hostage map ("If 0 then use mp_roundtime") |
| sv_cs_player_speed_has_hostage | **200** | PlayerMove's max speed (0x182175708) |
| hostage_drop_time | 1.0 | the drop to the ground (0x181faaac0) |
| hostage_is_silent | 0 | the hostage's response rules lines (0x18211a720) |
| hostage_debug | 0 | Use's T branch |
| cash_team_elimination_hostage_map_t / _ct | 1000 / 2000 | team money reason 2 / 3 |
| cash_team_win_by_time_running_out_hostage | 3250 | reason 5 |
| cash_team_win_by_hostage_rescue | 3500 | reason 8 |
| cash_team_rescued_hostage | 0 | reason 0xb (per rescued hostage, at the round's end) |
| cash_team_hostage_alive | 0 | reason 0xc (per live unrescued hostage, to the winner) |
| cash_team_hostage_interaction | 500 | reason 0xe (the first touch of a hostage) |
| cash_player_rescued_hostage | 1000 | player award 5 |
| cash_player_interact_with_hostage | 150 | player award 6 |
| cash_player_damage_hostage | -30 | player award 7 (per point of damage) |
| cash_player_killed_hostage | -1000 | player award 8 |
| contributionscore_hostage_rescue_minor / _major / _kill | 1 / 3 / -2 | the scoreboard's score |

The game mode cfgs (game/csgo/cfg, read 2026-11-16) set the cash_* (gamemode_competitive / competitive2v2 / casual:
elimination T 3000 / 2500 / 2000, CT 3000 / 2500 / 2300; time 3250 / 2750 / 2000; rescue win 2900 / 2900 / 3000;
rescued 600 / 600 / 0; interaction 600 / 600 / 500; alive 0; player rescued 1000, interact 300, damage -30, killed
-1000) and mp_roundtime_hostage (1.92 / 1.5 / 2); none sets an mp_hostages_* cvar.

The money tables: **team** 180964f60 (reason -> cvar: 1 terrorist_win_bomb, 2 elimination_hostage_map_t, 3
elimination_hostage_map_ct, 4 elimination_bomb_map, 5 win_by_time_running_out_hostage, 6 _bomb, 7 win_by_defusing_bomb,
8 win_by_hostage_rescue, 9 loser_bonus, 10 loser_bonus_consecutive_rounds, 0xb rescued_hostage, 0xc hostage_alive, 0xd
planted_bomb_but_defused, 0xe hostage_interaction, 0x11 (0x18211a250), 0x12 bonus_shorthanded); **player** 180952190
(1 killed_enemy?, 2 / 0xb, 3, 4, 5 rescued_hostage, 6 interact_with_hostage, 7 damage_hostage, 8 killed_hostage, 9,
10). Team money goes in as {team, reason} pairs (18090e220; c4.md "The round").

## The hostage's states (m_nHostageState, +0xbd0)

0 idle (usable), 1 being grabbed (a CT holding +use on it), 2 picked up (the 0.1 s lift onto the back), 3 carried, 5
dropped (0.25 s, then 0), 6 rescued, 7 dead. (4 is never stored in this build.)

## Spawn 1803629a0 / the constructor 18035b000

- The constructor appends to the list (max 12, else m_bRemove); m_uiHostageSpawnExclusionGroupMask 0,
  m_nHostageSpawnRandomFactor 1.
- Spawn reads the keyvalues **HostageSpawnExclusionGroup1..32** (bit n-1 of the mask; the table at 0x1817c3508) and
  **HostageSpawnRandomFactor** (clamped 1..100). Then: no hostages in game_type 1 / game_mode 2 (deathmatch, 18093e040);
  none in a warmup (gamerules +0xd9, 18093ec40) unless mp_hostages_spawn_same_every_round; m_bRemove: UTIL_Remove.
- models/hostage/hostage.vmdl; the collision from the model's bounds (or the default hull) with SOLID 8, interacts-with
  0xc3011; flag **0x2000000** (the high-priority use pick, use.md); max health / health **100**; gravity 1.0; the view
  offset **(0, 0, 35)** (180242350: the EyePosition the use hint aims at); the think CHostageHostageThink at now +
  1/60; the use callback; dropped to the floor (18091f260, hull (-8, -8, 0) .. (8, 8, 64)); m_vecSpawnGroundPos;
  m_nApproachRewardPayouts 4; every state and time cleared.

## RestartRound's selection (180957e50, at 180958e9e..180959e90; after CleanUpMap)

When the list holds more than mp_hostages_max:

1. Without mp_hostages_spawn_same_every_round, m_arrSelectedHostageSpawnIndices is emptied.
2. **A stored selection** (its count != 0): every hostage whose index isn't in it is removed (from the back).
3. Else **mp_hostages_spawn_force_positions** "a,b": the hostages at those indices kept, the rest removed;
   **mp_hostages_spawn_force_positions_xyz** "x y z,...": for each point the nearest hostage (3D squared distance, the
   first of equals) kept (a malformed point: a warning); **mp_hostages_spawn_farthest**: every combination of
   mp_hostages_max indices (lexicographic, starting 0..max-1) scored by the sum of the pairs' squared 2D distances, the
   first with the largest kept.
4. Else **the random pick** (180959a65..180959c60): while fewer than mp_hostages_max are picked and some remain: total =
   the sum of m_nHostageSpawnRandomFactor; 0 stops; r = RandomInt(0, total - 1); the first whose factor is above r (r
   less each factor passed) is taken out of the list into the picks; with an exclusion mask, every other remaining
   hostage sharing a bit with it is removed (from the back). Then the rest are removed and the list is the picks.
5. Still more than the max: RandomInt(0, n - 1) removed until it fits.
6. With an empty stored selection, the kept hostages' indices (into the list as it was at the start) are stored
   (m_arrSelectedHostageSpawnIndices), and the console line "Selected %d hostage positions '...'".

## +use: the pick (use.md) and Use 180931160

**180ac74c0's CHostage branch** (the hint): the entity is the hostage only for a **CT** (+0x344 3), with the hostage
alive and not rescued (18093e5c0), no leader (18093d400: m_leader resolves), no other live, connected grabber
(m_hHostageGrabber a pawn other than the user, alive, its controller in state 0 or 3) and not in the warmup (18093ec40);
priority 1, type 0 (the 3D distance), the point its **EyePosition** (origin + 35), reach 62 (+0x1c), no line needed
within 32 (+0x20), cones -0.7 / -0.5 (+0x24 / +0x28). The pick 180ac7120 finds it through the 0x2000000 flag. A T never
gets one: the hostage is a CT's to use (Use's T branch only runs with hostage_debug).

**Use** (continuous: every command +use finds it):

1. The user a player pawn (vfn 0x558), vfn 0xca8, alive (vfn 0x550). In the warmup (+0xd9): the hint
   `#Cstrike_TitlesTXT_Cannot_Move_Hostages_Warmup` (to the controller, 180ca7f40 type 4), nothing else.
2. Farther than 1000 u (squared distance > 1e6, x y z as (dy dy + dx dx) + dz dz): nothing.
3. Already carrying (hostage services +0x48 resolves): `#Cstrike_TitlesTXT_CanOnlyCarryOneHostage` (180ca8180).
4. A T with mp_only_cts_rescue_hostages: 1809610f0 (below: its T branch prints `#Cstrike_TitlesTXT_Only_CT_Can_Move_Hostages` once).
5. State 1: the grabber is the user: m_fLastGrabTime = now (keeps the grab going); another: the user's controller gets
   `#Cstrike_TitlesTXT_SomeonePickingUpHostage`.
6. Else **the grab starts**: a defuse kit (the item services' 180ac8960) or m_bHandsHaveBeenCut: **1.0 s**,
   `Hostage.CutFreeWithDefuser`; else **4.0 s**, `Hostage.CutFreeWithoutDefuser` (both from the hostage to everyone,
   the guid kept to stop it); **m_flGrabSuccessTime = now + length**; the progress bar (180ae21a0(pawn, length));
   m_hHostageGrabber = the user; **state 1**; **m_bIsGrabbingHostage = 1**; m_fLastGrabTime = m_flGrabStartTime = now;
   m_OnHostageBeginGrab (activator the user); OnHostagePickUpStart (the script event 180231040); next think now.

## The Think 180930450

- m_jumpedThisFrame cleared. The first think: m_isAdjusted, the collision bounds **(-8, -8, 0) .. (8, 8, 64)**.
- Next think: state 1 every tick (the frame interval); else now + 1/60 (1/45 with a leader).
- **State 1 with a grabber**:
  - now >= m_flGrabSuccessTime and the grabber alive: `Hostage.PickUp` (from the hostage), m_bIsGrabbingHostage 0,
    **1809610f0(hostage, grabber)** (below: the carry), the progress bar finished (180abee60(pawn, 2)), grabber cleared,
    m_vecGrabbedPos = the hostage's origin, **state 2**; OnHostagePickUp when the leader is the grabber.
  - Else the grab goes on while the grabber holds IN_USE or 0x100000000 (movement services +0x58) or within 0.05 s of
    m_fLastGrabTime, **and** still looks at it (180ac74c0's entity is this hostage and 180ae9bd0 mode 1: use.md),
    **and** stands on the ground (FL_ONGROUND). Off the ground (alive): `#SFUI_Notice_Hostage_Pickup_Must_Be_On_Ground`.
    Otherwise **the abort**: the progress bar cancelled (180abee60(pawn, 1)), m_bIsGrabbingHostage 0, state 0, the
    cut-free sound stopped (180f975a0), grabber cleared, OnHostagePickUpAbort.
- Every other state (and state 1 without a grabber): the nav area; 18096b150 (the physics step with m_vel / m_accel,
  read in outline: a still hostage's velocity decays by 4 x dt and snaps to 0 under 1 u/s); 18035b640; **180362550**
  (the drop to the ground, below); the reset position follows a leader on the ground. Then:
  - **state 2**: SOLID_NONE, flags 0, the use callback off, flag 0x2000000 off; for 0.1 s after m_flGrabSuccessTime
    the hostage lerps from m_vecGrabbedPos to the leader's origin + (0, 0, 40) (t = (now - success) / 0.1, each axis
    (target - from) x t + from); after: **state 3** (carried), 1803ebce0(hostage, 0, 0).
  - **state 5** after m_flDropStartTime + 0.25: **state 0**, SOLID 2 (bbox), collision group 8, the use callback, flag
    0x2000000, the solid flags | 1.
  - **state 6** 4 s after m_flRescueStartTime: SOLID_NONE, flags 0, 0x2000000 off (it stays where it was put down).

**The drop to the ground 180362550(hostage, ground)**: while now < m_flDropStartTime + hostage_drop_time: the hostage at
from = m_vecPositionWhenStartedDroppingToGround moved toward the floor point (18091f260 with the 16 x 16 x 64 hull) by
|floor - from| x ((hostage_drop_time + start - now) / hostage_drop_time) back from the floor... (as decompiled: d =
|floor - from| x remaining fraction; when |floor - ground| <= d the ground point, else floor + normalize(ground - floor)
x d); once past it (and not state 5) dropped to the floor and m_flDropStartTime = 0.

## The carry: 1809610f0 (the touch) and 180923710 (the pickup)

**1809610f0(hostage, user)**, for a CT (or anyone without mp_only_cts_rescue_hostages, or with hostage_debug):

1. A dead leader is cleared.
2. With the reuse timer elapsed: **the first use** (m_hasBeenUsed): **the CT team gets cash_team_hostage_interaction**
   (18035d1b0: AddTeamAccount(3, 0xe, ...)) and the user's award kind 6 (180b006f0); the user's
   contributionscore_hostage_rescue_minor (1801fc0c0); m_flNextHostageAnnouncement = now + 60 when passed and the
   round not won; m_bHasHostageBeenTouched; a human's radio line **"EscortingHostages" /
   `#Cstrike_TitlesTXT_Got_Hostages`** (180239eb0, auto) at most every 10 s (the controller's +0x48 timer);
   **m_bHandsHaveBeenCut = 1** (a later grab takes 1 s); m_OnFirstPickedUp. Every use: m_nSpotRules |= 4 & ~0x20;
   the first touch of the round: **m_bAnyHostageReached** and, the round not won, m_iRoundTime += mp_hostages_rescuetime
   x 60 and the `#hostagerescuetime` centre text.
3. The user already the leader: leader cleared, the "StopFollowing" response; another live leader: nothing; else
   **180923710** (the pickup). The reuse timer restarts.

The T branch: a T without hostage_debug: the hint `#Cstrike_TitlesTXT_Only_CT_Can_Move_Hostages` once (+0x1488 0x200000).

**180923710(hostage, user)**: the controller's hostage count +1 (+0x218), +0x224 = 1; "StartFollowing" (the hostage's
response rules, leaderteam:CT, unless hostage_is_silent); **`hostage_follows`** (userid, hostage = entindex, priority 5),
m_nPickupEventCount + 1; m_leader / m_lastLeader = the user, m_isWaitingForLeader 0; **180a7af40(user's hostage
services, hostage)**; the collision's group bit 0x10000000000; the log line "picked up a hostage".

**180a7af40 (CCSPlayer_HostageServices)**: m_hCarriedHostage = the hostage; the hostage's effects |= 1 (EF_NODRAW-like:
180d0e200(+0x5e8, 1)); unless a prop exists, **hostage_carriable_prop** spawned at the pawn (origin), its model
**models/hostage/hostage_carry.vmdl**, parented to the pawn (1803ebc00) with its bones following (vfn 0x1b0,
1803d6ab0(.., 1)), the hostage's skin copied (180b556c0 -> 180b76fb0); m_hCarriedHostageProp; the carrier's hint
**`#Cstrike_TitlesTXT_CarryingHostage`**. The controller's +0x7f8 +0x1b8 counter + 1.

## The carrier's movement (PlayerMove 180adf830, 180adfa2d..180adfb3d)

mv+0x120 (the max speed) = min(260, svc+0x1ac when 0 < it < sv_maxspeed, else sv_maxspeed); **with a carried hostage
(+0xe38 +0x48 resolves, 180ab60d0) it is set to sv_cs_player_speed_has_hostage (200)**; then min(the active weapon's
vfn 0xc20). It is **1.0** instead when the pawn is dead, its move type not 0 / 6, m_bIsDefusing, **m_bIsGrabbingHostage**,
pawn+0x14c0, or the freeze period (the Valve-server exception aside). Accelerate's walk (movement.md): s x 0.52 is
skipped while carrying (the same +0x48 test). Ported: move-sim.js J[53] 0x40000 (grabbing: max speed 1) / 0x80000
(carrying: the walk skip), F[52].

## Dropping: 18035bc40(hostage, at, rescued)

- From a carrier's death: the death drop 180b05460 (at 180b05dc0: the hostage handle live and the controller's count >
  0) calls it with **the pawn's abs origin** and 0; the rescue calls it with the carrier's origin and 1.
- m_lastLeader cleared; with a leader: its count - 1, **180a99600** (the services clear m_hCarriedHostage and remove the
  prop); not rescued: m_OnDroppedNotRescued, SOLID 2, group 8, the group bit 0x10000000000 off, the use callback, the
  solid flags | 1, "StopFollowing", **state 5**, **m_flDropStartTime = now**.
- The log line "dropped off a hostage"; m_leader cleared; a trace (180c2e710, the entity's hull, interacts-with
  0xc3001, group 5) from `at` to at - (0, 0, 500): m_vecPositionWhenStartedDroppingToGround = at, or the trace's end
  when it hit (and the hostage put there); gravity 1.0; next think now; OnHostageDrop (not rescued).

## The rescue

- **func_hostage_rescue** (CHostageRescueZone): its touch (180994400, unless disabled +0x9b4) fires the input
  "OnRescueZoneTouch" at the toucher. **CCSPlayerPawn's OnRescueZoneTouch 18023b020**: in a mode with hostages
  (18093df90: game mode check), m_bInHostageRescueZone = 1, a CT's hint `#Cstrike_TitlesTXT_Hint_hostage_rescue_zone`
  once (+0x1488 0x20000), and **the carried hostage gets "OnRescueZoneTouch"** -> CHostage_API's 1803561b0 ->
  **18035d350**. A hostage on the ground in a zone isn't rescued: the carrier is what touches.
- **18035d350 (the rescue)**: once (m_isRescued); m_lastLeader = the leader; the use callback off; the leader's count -
  1, m_OnRescued, **the drop at the carrier's origin (rescued 1)**; SOLID_NONE; **m_flRescueStartTime = now, state 6**;
  OnHostageRescue; **`Event.HostageRescued`** to everyone (the gamerules' 180911880) at most every 2 s (a static
  CountdownTimer 0x181faab88); the rescuer's award kind 5; **`hostage_rescued`** (userid, hostage, site 0, priority 5);
  m_iHostagesRescued + 1, the rescuer added to the unique rescuers (+0xed0); the round not won: **CheckWinConditions**
  (180917420) with the rescuer as its context (+0xe28: the MVP); then the contribution scores (18095f480: the rescuer's
  _major (3) when the rescue won the round, else _minor; every other live CT's _minor) and the round stats.
- **The rescue win 180930260** (CheckWinConditions' tail): n = the hostages; alive = those with health > 0 not rescued;
  need = mp_hostages_rescuetowin when non-zero and <= n, else n; m_iHostagesRemaining = alive; **the CTs win when
  m_iHostagesRescued >= need and alive >= n - need** (and n > 0): `hostage_rescued_all`, TerminateRound(reason **11
  HostagesRescued**, {(CT, 8 WIN_BY_HOSTAGE_RESCUE)}, mp_round_restart_delay).
- **The player's money**: cash_player_rescued_hostage (award 5) to the rescuer. TODO(trace): the award's own call site
  (180b006f0(controller, 5) pays it: the action tracking's award table is unread).

## The round

- **Elimination** (180917420): on a map without a bomb target, the Ts' win (reason 9) pays {(T, 2)}
  cash_team_elimination_hostage_map_t, the CTs' (reason 8) {(CT, 3)} cash_team_elimination_hostage_map_ct (the bomb
  map's 4 otherwise). A hostage map has no planted-bomb hold.
- **The clock** (180916fb0): with mp_default_team_winner_no_objective -1, no bomb target and **m_bMapHasRescueZone**:
  the **Ts win**, reason **13 HostagesNotRescued**, {(T, 5 WIN_BY_TIME_RUNNING_OUT_HOSTAGE)}.
- **The round's money list 1809124d0** (TerminateRound -> 18095c3c0): the winner's pairs; then the hostage loop over the
  list (each: health >= 1 and not rescued adds cash_team_hostage_alive; rescued counts; the loop stops once the alive
  sum is over 1999): **the winner gets (0xc, the alive sum)**, the loser its loss bonus (9), and **the CTs always get
  (0xb, cash_team_rescued_hostage x the rescued count)**.
- The round time: mp_roundtime_hostage on a hostage map (0: mp_roundtime).
- The buy menu sells the kit as item_cutters on a hostage map (buy.md, 18093d7b0 = gamerules +0x132).

## Damage

- **OnTakeDamage 180361940**: without mp_hostages_takedamage (the default) the info's flags (+0x70) |= 1
  (**DFLAG_SUPPRESS_HEALTH_CHANGES**): a hostage never loses health, then the base (180b67140).
- **OnTakeDamage_Alive 180361960**: the base (180b67340), the pain line ("Pain" response, every 2 s, unless
  hostage_is_silent); a player attacker: the controller's +0x21c, gamerules m_hostageWasInjured; v =
  cash_player_damage_hostage (award 7); when non-zero: the hint `#Cstrike_TitlesTXT_Hint_careful_around_hostages` once
  (+0x1488 0x20), **`hostage_hurt`** (userid, hostage, priority 5), and the attacker pays **min(health, (int) damage) x v**
  (180b00730(account, 7, ..)), the damage the result's +0x20 truncated.
- **Event_Killed 18035c280**: the leader's count - 1, CheckWinConditions, m_hostageWasKilled; a player attacker:
  18095f460 (cash_player_killed_hostage) and `#Cstrike_TitlesTXT_Hint_lost_money` once (+0x1488 0x40), award kind 8;
  the use callback off, the base, **`hostage_killed`** (userid, hostage, priority 5), **state 7**, OnHostageKill.

## The HUD (client_20261015)

- **CCSGO_HudGameIcons** (constructor 180e7d5d0, panorama/layout/hud/hudgameicons.xml under #HudTopLeft beside the
  radar; it listens to hostage_rescued and round_start): 180e8d230 (round start) clears `hud-game-icons--mode-hostage`,
  `--hostage-rescue-zone` and every icon's classes; **the update 180e92590**: `hud-game-icons--hostage-rescue-zone` =
  the local (or observed) pawn's m_bInHostageRescueZone (+0x15e8); over the 4 icon panels and the player resource's
  m_iHostageEntityIDs: a slot marked rescued (+0x7c + i, set by hostage_rescued) counts rescued; else
  m_bHostageAlive[i] false counts dead; else m_isHostageFollowingSomeone[i] counts carried, else alive. The panels are
  then filled **rescued first, then carried, alive, dead**: each `--active`, with `--carried` / `--rescued` / `--dead`
  as its kind; the rest lose `--active`. Styles: hudgameicons.vcss (34 x 36 icons, the transit icon's 0.8 s wash loop,
  the zone icon). TODO(trace): who sets `--mode-hostage` (read as: the map has a rescue zone).
- The progress bar's `hud-progress-bar__pickup-hostage` (hudprogressbar.vcss: the transit icon, its
  hud-progress-bar-hostage-animate) and `__drop-hostage`; the labels #SFUIHUD_InfoPanel_HostageText (TODO(trace) the
  bar's text pick).

## Sounds and events

Sound events (soundevents/vo/game_sounds_hostage.vsndevts): Hostage.Pain, Hostage.StartFollowCT,
Hostage.StartFollowCTGuardian, **Hostage.CutFreeWithDefuser**, **Hostage.CutFreeWithoutDefuser**, **Hostage.PickUp**,
Hostage.Drop, Hostage.Breath (client); **Event.HostageRescued** (the gamerules' broadcast); Music.GotHostage (client).
Game events: hostage_follows, hostage_hurt, hostage_killed, hostage_rescued, hostage_rescued_all. The radio:
"EscortingHostages" (#Cstrike_TitlesTXT_Got_Hostages) through the agents' VO (radio.js).

## Still unread (TODO(trace))

- 18096b150 / 18035b640 in detail (a carried hostage doesn't run them; a dropped one falls by 180362550)
- the player award table (180b006f0 / 180b00730: kinds 5 / 6 / 7 / 8 into money), read as the cash_player_* values
- RandomInt's stream (vstdlib's uniform random): the server's Math.random here
- the hostage's response rules lines (StartFollowing / StopFollowing / Pain: the hostage's talker script)
- the client's C_Hostage (its animation, Hostage.Breath, the carried prop's graph, OnHostageStateChanged), the
  first-person v_hostage_arm.vmdl; hudprogressbar's hostage label
- trigger_hostage_reset, info_hostage_rescue (1802c4c50: the bots' nav goals) and the bots' hostage behaviour
