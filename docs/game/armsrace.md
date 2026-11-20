# Arms Race (CS2's gun game)

server_20261105. pak01 gamemodes.txt (game_type 1 gungame, game_mode 0 `gungameprogressive`, uid 11; added
2024-02-06, "A Call to Arms"), game/csgo/cfg/gamemode_armsrace.cfg, map group `mg_armsrace` (ar_shoots,
ar_shoots_night, ar_baggage, ar_pool_day). gamemodes.txt's `weaponprogression_ct / _t` belong to `gungametrbomb`
(Demolition): Arms Race's ladder is built in code.

## CCSGameModeRules_ArmsRace (vtable 0x1818c5b60; base CCSGameModeRules 0x1818c5aa0, Deathmatch's beside it)

| Slot | Address | What |
|---|---|---|
| 0 | 0x18095ef20 | destructor |
| 2 | 0x18090bbe0 | deleting destructor (size 0x88) |
| 4 | 0x18094ea70 | Think |
| 5 | 0x18094df20 | match (re)start: ladder (0x180956090), winner -1, every controller's score reset (0x180a71500) or a bot re-added |
| 7 | 0x18094de40 | reset: leader -1, knife music handle cleared, winner -1 |
| 8 | 0x18094d9c0 | player joining: the first starts the warmup; sets +0x155c by team (the old note called it "the controller's teammate colour"; schema.py: +0x155c is the pawn's m_GunGameImmunityColor) |
| 9 | 0x18094ddf0 | spawn equip: tail-jumps to 0x18092c0f0 |
| 10 | 0x180921c30 | player killed (base 0x180921c20 does nothing) |

## Functions

| Address | What |
|---|---|
| 0x180956090 | copies the ladder into m_WeaponSequence (via 0x180929ca0) |
| 0x180929ca0 | builds the ladder |
| 0x1808ffa60 | (out, k, group): Fisher-Yates, append first k |
| 0x180fc9950 | attacker from damage info |
| 0x180ad2840 | enemy test (attacker pawn, other pawn) |
| 0x180fe1050 | fills the other's info for 0x180ad2840 |
| 0x180ac5e00 | team for the info |
| 0x180a79ab0 | controller's team (coaching aware) |
| 0x1809260d0 | killing weapon from damage info |
| 0x180a6e350 | AddScore(controller, n) |
| 0x180951c90 | kill feedback (rules, attacker, lvl) |
| 0x1805c4680 | emit sound with a filter |
| 0x180c84d30 / 0x180c84870 | filter: one player / everyone |
| 0x18092c0f0 | equip (spawn and refresh) |
| 0x180b04ac0 | (weapon services, 1): strip for the knife level |
| 0x180b04db0 | remove slot (0 / 1) |
| 0x180c86620 | gear slot's first weapon (services, slot, -1) |
| 0x180c86530 | weapon held by name |
| 0x180c844f0 | filters who counts for the time-limit winner |
| 0x1805c4d20 | stop the knife music |
| 0x1809654b0 | GMR_BeginIntermission |
| 0x1800a09f0 | registers mp_respawn_immunitytime |
| 180249530 | the respawn (~line 176): immunity |
| 18093ec40 | warmup test |
| 18093e040 | deathmatch: game_type 1 && game_mode 2 |
| 0x1801cd1d0 | pawn vfn 0xc20 (0x388 bit 4; unnamed) |
| 180237450 | active state's think (immunity) |
| 0x180b5d3b0 | pawn vfn 0x840: +0x334 m_bClientSideRagdoll |
| 180ad2380 | may respawn: controller +0x514 0 or 3, phase not 4 / 5, warmup or mp_respawn_on_death_ct / _t |
| 180adcb90 | PlayerMove_PostMove: sets m_bHasMovedSinceSpawn |
| 1802d52b0 | 2D length sqrt(x² + y²) |
| 180249fa0 | respawn clears m_bHasMovedSinceSpawn |
| 1801ffbb0 | ends immunity (flag 0, time 0) |
| 180a78120 -> 1801c6830 -> 180a4bbf0 | FireBullet's call |
| 180a2fa80 -> 180a4bea0 | knife swing's call |
| 1809d4a50 -> 180a4be70 | "grenade_thrown": call, counts the throw at +0x7c |
| 180a93f70 | damage services' OnTakeDamage: nothing while immune |
| 180a89430 | hit group function (reads the flag too; unread past that) |
| 180237640 | dead pawn's think (death cam) |
| 0x1800c5320 / 0x1800c5500 / 0x1800c53c0 / 0x1800c5460 | register spec_freeze_deathanim_time / _traveltime / _time / _time_lock |
| 180237bd0 | STATE_GUNGAME_RESPAWN think |
| 1802085d0 | its enter (slot 0): tries the respawn at once, same cap |
| 1802521c0 | respawn the pawn (0 while CServerSideClient +0xef4 non-zero or pawn +0xdf0 set) |
| 180923bc0 -> 180233f10 | FrameUpdatePreEntityThink: zeroes the respawn count |
| 180236f50 -> 1802371c0 | pawn PreThink -> state think (pawn +0xd48 vfn 0x10) |
| 1805b70a0 | controllers' usercmds in slot order (frame.md) |
| 0x180a2f130 | CWeaponTaser slot 0x38: precache |
| 0x180a2f1e0 | Taser PrimaryAttack |
| 1809f8a70 | CSBaseGunFire |
| 0x180a315a0 | recharge think |
| 0x1800c4390 | registers mp_taser_recharge_time |
| 180a1e400 | dry fire |
| 0x180a2c980 | Taser FireBullet (once a tick) |
| 180ee08d0 | lag comp manager vfn 0x10: StartLagCompensation(pawn, 2, eye +0x14, angles +0x20, radius) |
| 180ee3da0 | lag comp job filter (vtable 0x1819cf9b8 slot 0), after WantsLagCompensationOnEntity (pawn vfn 0xaf0) |
| 1802a53d7 | FX_FireBullets passes m_flRange |
| 180a31040 | taser trace (weapon, trace, start, end, plain, out end) |
| 180c2f3c0 | TraceShape (never asks the hitbox system) |
| 0x180a2f690 | CTraceFilterTaserIgnoreTeammates::ShouldHitEntity |
| 180cfb4b0 | vfn 0x350 InSameTeam: g_Teams[+0x344] of both |
| 180530ae0 | marks a sphere (r > 0) |
| 18157ff20 | sphere contact point: `(end + centre) - r normal` |
| 1802c35a0 | hit test |
| 180a316b0 | cast to a live pawn (vfn 0x558, 0xca8); result unused at 0x180a2ccd2 |
| 0x180fba3a0 | damage info |
| 180a88f30 | armor (not applied for the taser) |
| 180b51910 -> 180cb4610 / 180cabc70 | attachment by name hash in the bone cache |
| 18015a2f0 | WorldSpaceCenter (vfn 0x2c8) |
| 180ca65e0 -> 0x1814a2f70 -> 0x1814a2730 | attachment into the bone cache (one influence) |
| 181475200 | lane sums |
| 18092a2a0 | round start time |
| 180b05460 | death drop (step 3: taser) |
| 18009d5f0 | registers mp_death_drop_taser |
| 1800a4b30 / 1800a4a80 / 1800a4130 | register mp_weapons_allow_zeus / _typecount / mp_warmup_items_nocount_policy |
| 180ab9620 | CCSPlayer_ItemServices CanAcquire |
| 180b02570 | weapon carried |
| 180a43a60 | this round's purchases of an item |
| 180a7cf90 | the buy |
| 180a4ab40 | purchase count up |
| 180ac13d0 | death sound |
| 1800b7e50 | registers "planted_c4" / "CPlantedC4" (class 18212afd8) |
| 180a2d5a0 | taser holster |
| 180b7c4a0 | no ammo (vfn 0xaa8) |
| 180b01b60 | take the weapon off the pawn |
| 0x18030c4e0 | bot action_equip_weapon (+0x60 set -> EquipBestWeapon) |
| 0x1802c4430 | CCSBot::EquipBestWeapon |
| 1800a5970 | registers sv_coaching_enabled |

## Fields

| Offset | Field |
|---|---|
| rules +0x30 / +0x38 | m_WeaponSequence (networked CUtlVector<CUtlString>: count, elements) |
| rules +0x48 / +0x49 | restart flags (warmup start / end, game restart) |
| rules +0x4c | match leader slot (-1) |
| rules +0x50..+0x60 | "reached knife" music handle (0 = not playing) |
| rules +0x64 | winner slot (-1) |
| rules +0x68 | slots to refresh next Think (hash: murmur-style finalizer) |
| gamerules +0xd9 | warmup |
| gamerules +0x148 / +0xd7c | live round: set / 0 |
| gamerules +0x100 / +0x108 | time-left inputs (int, against the game start) |
| gamerules +0x1024 | intermission end time |
| controller +0x91c | m_iScore (level = m_iScore / 2) |
| controller +0x920 | second score counter (same adds, unclamped) |
| controller +0x8ec | pawn handle |
| controller +0x514 | 0 or 3 before an equip |
| controller +0x84c | coached team |
| controller +0xe48 +0x298 | this round's purchases |
| pawn +0x344 | team (2 T, 3 CT) |
| pawn +0xb10 / +0xb18 | weapon services / item services (decompiler param_2[0x162] / [0x163]) |
| pawn +0x334 | m_bClientSideRagdoll |
| pawn +0x388 bit 4 | vfn 0xc20 flag |
| pawn +0xc7c | m_flDeathTime |
| pawn +0xdf0 | already respawned |
| pawn +0xdf1 | m_bHasMovedSinceSpawn |
| pawn +0xe6a | m_bHasFemaleVoice |
| pawn +0xf71 | m_bInBuyZone |
| pawn +0x155c | m_GunGameImmunityColor (schema.py checked, with +0x15a4 / +0x15a8 / +0xdf1 / +0xe6a / +0xf71 / +0xc7c / +0x334, controller m_iScore +0x91c, rules m_WeaponSequence +0x30) |
| pawn +0x15a4 | m_fImmuneToGunGameDamageTime (GameTime) |
| pawn +0x15a8 | m_bGunGameImmunity |
| weapon services +0xdb | keep flag (don't switch to the given weapon) |
| move data +0x38 | velocity |
| taser +0x12a0 | m_fFireTime |
| taser +0x12a4 | the tick of the last FireBullet |
| taser vdata +0x830 | m_flRange |
| item def +0x48 | item's team |
| trace filter +0x20 / +0x40 | shooter / mode |

## Constants

| Value | What |
|---|---|
| CSWeaponType 0 / 8 / 12 | knife / taser / none (grenade projectile, world) |
| reason 8 / 9 / 10 | round end: winner CT / T / other |
| T -0x8a3716, CT -0x54483, else -1 | immunity colour (slot 8; -1 with mp_teammates_are_enemies) |
| mp_respawn_immunitytime 4.0 | flags 0x282000, "Set to negative value to disable warmup immunity" |
| 3.0 / 1.0 | warmup immunity; cut to now + 1.0 once moved |
| spec_freeze_deathanim_time 0.8, spec_freeze_traveltime 0.3, spec_freeze_time 3 (cfg 2), spec_freeze_time_lock 1.0 | |
| button bit 33 | excluded from the skip |
| DAT_181f9ed6c | respawns this tick (global) |
| 0x181792e20 / 0x181792e40 / 0x181792e60 | state vtables 4 slots apart: observer / gungame respawn / death-wait-for-key |
| STATE_GUNGAME_RESPAWN | 7 |
| 0x181919110 | CWeaponTaser vtable (overrides 0x0, 0x20, 0x38, 0x48, 0x168-0x180 against CCSWeaponBaseGun 0x1818f0d38) |
| mp_taser_recharge_time 30.0 | "-1 = disabled", flags 0x282000 |
| 128 (130 no vdata) | lag comp radius = m_flRange + 128 |
| 1024 (0x1817b2c84) | job filter: `|origin - start| <= radius + 1024`, `(dz dz + dy dy) + dx dx`, comiss / setbe; radius 0 = everyone |
| 0x1c1003, layer 0x40000 | interacts-with (player layer meets collision boxes) |
| group 4, flags 0x4b, detail 0xffff, object set 0xf | taser trace |
| 0x18178c240 | CTraceFilter vtable |
| 0x18191a060 | CTraceFilterTaserIgnoreTeammates vtable |
| 0x181f065c0 | ".?AVCChicken@@" |
| r = 0, 2, 4 | trace radii |
| 500.0 | taser damage (not m_nDamage) |
| 0x100 | DMG_SHOCK |
| 7.61985 / 2.32976 | rope start: along the attachment's rotated (1, 0, 0) / (0, 0, 1) |
| 0x18211a6d8 (+0x58) | mp_teammates_are_enemies |
| mp_death_drop_taser 1 | |
| mp_weapons_allow_zeus 1 | 0x182119bc8, flags 0x282000, "how many Zeus purchases a player can make per round (0 to disallow, -1 to have no limit)" |
| mp_weapons_allow_typecount 5 | 0x182119c18 |
| mp_warmup_items_nocount_policy 42 | 0x182119c28: bits 1 c4, 3 kevlar / kit, 5 healthshot |
| 1000 | warmup mult with the nocount policy bit |
| category bits | 0 gun, 1 C4, 2 grenade, 3 kevlar / kit, 4 Zeus, 5 healthshot |
| 0x180a7d798 | buy's jump table: 0 go on, 2 / 4 / 5 message, 1 / 3 / 6-10 4 |
| sv_coaching_enabled 0 | 0x182119820 |
| bot_allow_* types | rifles 3, shotguns 4, machine guns 6, snipers 5, SMGs 2 |
| weapon_taser | m_nDamage 500, m_iMaxClip1 1, m_flCycleTime 0.15 / 0.3, m_flRange 120, m_flRangeModifier 0.99, m_flArmorRatio 2, m_GearSlot GEAR_SLOT_KNIFE position 1, Weapon_Taser.Single, the taser tracer, m_nPrice 200 |

## The ladder (0x180929ca0)

Each group: Fisher-Yates (i = 0..n-1 when n > 1: `j = RandomInt(i, n-1)`, swap i, j; tier0's RandomInt, the server's
stream), first k appended.

| # | k | Group |
|---|---|---|
| 1 | 1 | scar20, g3sg1 |
| 2 | 1 | awp |
| 3 | 4 | ak47, aug, famas, galilar, m4a1, m4a1_silencer, sg556 |
| 4 | 1 | m249, negev |
| 5 | 3 | mac10, p90, ump45, bizon, mp7, mp5sd, mp9 |
| 6 | 1 | deagle, revolver, ssg08 |
| 7 | 3 | elite, fiveseven, glock, tec9, hkp2000, usp_silencer, p250 |
| 8 | 2 | xm1014, nova, mag7, sawedoff |
| 9 | 1 | knifegg |

17 levels, both teams, rebuilt each match start.

## A kill (0x180921c30)

In warmup or a live round; needs both pawns and controllers and 0x180ad2840 true. `len` = ladder count, `lvl` =
attacker m_iScore / 2.
1. lvl >= len: go to 4.
2. Weapon type (vfn 0xc60; 12 with none). Knife: attacker +2, victim -2. Else, only while `lvl < len - 1`: attacker
   +1, victim -1 if taser (8), else 0. At the knife level a non-knife kill gives nothing.
3. AddScore: +0x920 += n, m_iScore += n, clamped at 0. New level above lvl: below len -> refresh set; at len -> winner.
4. 0x180951c90, then the victim: UI.ArmsRace.PlayerDeath; level dropped: UI.ArmsRace.Weapon_LevelDown.

0x180951c90:
- attacker level == len: UI.ArmsRace.FinalKill_Knife to everyone. Else:
- UI.ArmsRace.Kill1 to the attacker; leveled up: UI.ArmsRace.Weapon_LevelUp; new level == len - 1:
  UI.ArmsRace.ReachedKnife to them and, if the handle is 0, UI.ArmsRace.ReachedKnife_Music to everyone (kept; Think
  stops it at round end).
- leveled up and not the leader: if no other controller's level >= theirs, they lead; the old leader hears
  UI.ArmsRace.Demoted; UI.ArmsRace.BecomeMatchLeader to them.

## The equip (0x18092c0f0)

Pawn alive (vfn 0x550), controller +0x514 0 or 3. level = m_iScore / 2:
- level == len - 1: 0x180b04ac0: primary and pistol slots removed, weapon_taser removed, molotov, incgrenade,
  smokegrenade, hegrenade, flashbang, decoy removed unless being thrown (vfn 0xaa8), the C4 dropped; then gear slot 2
  selected (vfn 0xf0).
- level < len: the ladder's weapon unless held: `keep` = a gun held (slot 0 or 1) and the active weapon a knife or
  taser (`type & ~8 == 0`); both gun slots removed; item services give (vfn 0xb8) with +0xdb = keep, restored after.
  Then a weapon_taser if not held, +0xdb = 1.

## Think (0x18094ea70)

Restart handling (+0x48, +0x49), then the refresh set's equips, set emptied. Live round: no winner and time left
(mp_timelimit) <= 0: winner = highest m_iScore (strictly: first of a tie in slot order; 0x180c844f0 filters). With a
winner: music stopped, GMR_EndRound reason 8 / 9 / 10, intermission: match over.

## gamemode_armsrace.cfg

mp_teammates_are_enemies 0, mp_respawn_on_death_t / _ct 1, mp_randomspawn 1, mp_respawn_immunitytime 10,
mp_free_armor 2, sv_infinite_ammo 2, mp_roundtime 10, mp_timelimit 10, mp_maxrounds 0, mp_freezetime 0,
mp_warmuptime 20, mp_buytime 0, every cash_* 0, mp_startmoney 0, mp_maxmoney 0, mp_death_drop_gun 0,
mp_death_drop_grenade 0, mp_weapons_allow_map_placed 0, mp_ct / t_default_melee weapon_knife, default secondary /
primary "", mp_display_kill_assists 0, sv_talk_enemy_living / dead 1, sv_deadtalk 1, spec_freeze_time 2,
bot_quota 10 fill, healthshot_health 50, mp_friendlyfire 1 with every ff_damage_reduction_* 0. mp_death_drop_taser not set.

## Spawn immunity (every mode)

- Respawn (180249530): t = mp_respawn_immunitytime; t < 0, or t <= 0 outside warmup: flag 0, time 0. Else if not
  deathmatch or pawn 0x388 bit 4, a warmup sets t = 3.0; otherwise (deathmatch) m_bInBuyZone = 1. Time = now + t, flag 1.
- Think (180237450, every tick): only when (t > 0 or warmup) and flag on. A ragdoll pawn loses it. now > time: ends.
  Before: 180ad2380 and m_bHasMovedSinceSpawn: a time more than 1.0 s away becomes now + 1.0.
- m_bHasMovedSinceSpawn: set once the move velocity has non-zero 2D length (a fall doesn't count); cleared by the respawn.
- Ended at once (1801ffbb0) by FireBullet, the knife swing, a grenade throw.
- Effect: OnTakeDamage does nothing while on (first test: flag 0, services' state not 7 / 8, ...).

## The respawn (deathmatch, Arms Race)

- 180237640 moves the dead pawn to STATE_GUNGAME_RESPAWN when 180ad2380 allows (else observer mode) at
  `m_flDeathTime + spec_freeze_deathanim_time + spec_freeze_traveltime + spec_freeze_time`, or once
  `m_flDeathTime + spec_freeze_deathanim_time + spec_freeze_time_lock` is past and a button (but bit 33) is held, with
  mp_deathcam_skippable. mp_respawnwavetime_ct / _t (0 in these cfgs) would hold it for the team's wave.
- 180237bd0 respawns (1802521c0) unless sv_max_deathmatch_respawns_per_tick (> 0; cfgs 1) respawns happened this tick.
- Order: the count rises only when 1802521c0 respawned; zeroed each frame. The state thinks from PreThink in the
  pawn's usercmds; controllers run in slot order: lowest slot first, at most the cap a frame, the rest next frame
  (spawns.md).

## The Zeus (weapon_taser, CWeaponTaser, weapon_taser.cpp)

- Precache: particles/blood_impact/impact_taser_bodyfx.vpcf, particles/weapons/cs_weapon_fx/weapon_tracers_taser.vpcf.
- PrimaryAttack: CSBaseGunFire with the cycle time (vfn 0xbb0); a shot -> m_fFireTime = now, recharge think at
  now + mp_taser_recharge_time. Empty dry fire: Weapon_Taser.ChargeNotReady (a pistol Default.ClipEmpty_Pistol, else
  Default.ClipEmpty_Rifle).
- FireBullet: Weapon_Taser.Single; lag compensation radius m_flRange + 128 (the knife its reach + 128).
- Trace 180a31040: eye to `eye + forward x m_flRange`, TraceShape, the shooter's handles first. `plain` 1: CTraceFilter,
  +0x40 = 0 (nearest hit); 0: CTraceFilterTaserIgnoreTeammates (not the shooter, not InSameTeam; +0x40 = 1).
  `dir = normalize(end - start)` (`(dz dz + dy dy) + dx dx`, 1 / |d| times each); r = 0, 2, 4: a line to the end,
  then spheres to `end - dir r`; a hit (fraction < 1 or start solid) writes the out end (line: trace end +0x84;
  sphere: 18157ff20) and returns 1 for a player pawn (vfn 0x558) or a CChicken; else next radius; past 4: 0.
- FireBullet: out end = the line's end; plain trace; a hit on a pawn (vfn 0xca8) that 0x180ad2840 says isn't an enemy
  reruns with the flag clear and 180a316b0 on its hit, result unused: the victim stays the teammate, only the trace
  and the out end are the second one's. A non-pawn hit cast to CChicken (world and map entities take nothing).
- Damage info: attacker the pawn, inflictor the taser, 500.0, DMG_SHOCK (no hit group, no armor), force direction
  the forward, the trace. Then `cstaserrope`: start = weapon_hand_r attachment (none: WorldSpaceCenter) + 7.61985
  along rotated (1, 0, 0) + 2.32976 along rotated (0, 0, 1); end = out end; shooter's and victim's handles.
- Attachment (0x1814a2730, one influence): position `(C + (w t + o)) s + p`, rotation `q x r` with r flipped to q's
  hemisphere; then 180a2c980's offsets `(C + (w t + a), (p + rX k1) + rZ k2)`.
- Recharge (0x180a315a0): mp_taser_recharge_time >= 0 and clip (vfn 0xac0) 0 -> clip 1 (vfn 0xad0) and, when the
  round start is before m_fFireTime, Weapon_Taser.ChargeReady.
- Holster (180a2d5a0): mp_taser_recharge_time < 0 and no ammo -> 180b01b60 takes it off the pawn.
- Death drop: thrown (mode 1) with mp_death_drop_taser. Pickup refused while one is carried (pickups.md).
- Arms Race: given when none carried (+0xdb = 1); removed at the knife level; its kill takes 1 from the victim.

## Buying the Zeus

- Cfgs: mp_weapons_allow_zeus competitive / competitive2v2 / rush 5, casual 2, deathmatch 1 then -1 (later line
  holds), armsrace -1, demolition 0, dm_freeforall / retakecasual / teamdeathmatch 1. mp_weapons_allow_typecount
  casual 2, deathmatch / armsrace -1.
- CanAcquire (180ab9620; method 1 purchase, 2 a teammate's, 0 pickup): carried -> 2; Zeus: allow_zeus 0 -> 9; above 0
  and purchases >= `mult x allow_zeus` -> 3 (mult 1000 in warmup with the policy's category bit, else 1); item team
  not the buyer's -> 6; a knife -> 9; typecount 0 -> 9, above 0 and count >= `mult x typecount` -> 3; price over money
  -> 13. Pickup: Zeus only with allow_zeus != 0 (else 8).
- Buy (180a7cf90): 2 / 4 / 5 -> "#Cstrike_TitlesTXT_Cannot_Carry_Anymore", 1; other non-0 -> 4 silently. Price
  (GetItemPrice), money, GiveNamedItem (no +0xdb: switched to). Count up.
- Death sound (180ac13d0): Player.Death from the victim (PAS 0.8), Player.DeathTaser when damage type is exactly 0x100,
  _F / DeathFem with m_bHasFemaleVoice, unless the attacker is a CPlantedC4; a head shot has the three DeathHeadShot
  events only; a pawn attacker's kill adds the DeathBody trio.
- Bots never draw a carried Zeus: bt_default.kv3 (pak01 scripts/ai/<mode>/, armsrace too) equips "BEST":
  EquipBestWeapon: gear slot 0 when its bot_allow_* allows and not empty (vfn 0xaa8), else gear slot 1 with
  bot_allow_pistols, else nothing more with weapon_knife out, else gear slot 2's first (m_hMyWeapons order: the knife).
  bt_config.kv3's attack table gives TASER -1, as the knife and the C4.

## Enemy test (0x180ad2840)

0x180fe1050 fills the other's info (+0 null, +1 a player pawn, +4 handle, +8 controller slot via 180b55410, +0xc
team via 180ac5e00: controller's 180a79ab0, else pawn +0x344). Attacker slot == other's -> false;
mp_teammates_are_enemies -> true; else teams differ. 180a79ab0: with sv_coaching_enabled a spectator (team 1) with
a coached team (+0x84c) counts as that team.

## The golden knife

None: weapon_knifegg is the ladder's last name and a panorama icon (icons/equipment/knifegg.vsvg_c); weapons.vdata has
no weapon_knifegg block, pak01 no golden knife model. The knife level shows the knife already carried.

## Unread

- Where m_iScore's ordinary kill / assist points go in Arms Race (CCSGameRules' score award under this mode).
- Deathmatch's spawn-immunity branch test (pawn 0x388 bit 4).
- The Arms Race HUD (next-weapon panel, level list): client.dll and panorama.
- The time-left formula (+0x100 int + 0x108 against the game start) beyond mp_timelimit.
