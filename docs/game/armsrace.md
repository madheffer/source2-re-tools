# Arms Race (CS2's gun game)

CS2 ships it: game_type 1 (gungame) game_mode 0 (`gungameprogressive`, gamemodes.txt in pak01, uid 11), added
2024-02-06 ("A Call to Arms"). Its config is game/csgo/cfg/gamemode_armsrace.cfg; its maps the `mg_armsrace` group
(ar_shoots, ar_shoots_night, ar_baggage, ar_pool_day). The rules are a game-mode class in server.dll,
`CCSGameModeRules_ArmsRace` (vtable 0x1818c5b60 in server_20261105.dll; the base `CCSGameModeRules` 0x1818c5aa0;
the Deathmatch one beside it). gamemodes.txt's `weaponprogression_ct / _t` blocks belong to `gungametrbomb`
(Demolition), not Arms Race: Arms Race's ladder is built in code. Read 2026-11-16 (server_20261105.dll, ReVa).
Ported in web/server/cs2web/modes/team/armsrace.js.

## The class

| Slot | Address | What |
|---|---|---|
| 0 | 0x18095ef20 | destructor |
| 2 | 0x18090bbe0 | deleting destructor (size 0x88) |
| 4 | 0x18094ea70 | Think (each frame, below) |
| 5 | 0x18094df20 | the match's (re)start: builds the ladder (0x180956090), winner = -1, every controller's score reset (0x180a71500) or, a bot, re-added |
| 7 | 0x18094de40 | reset: leader -1, the knife music handle cleared, winner -1 |
| 8 | 0x18094d9c0 | a player joining: the first starts the warmup; the controller's teammate colour (+0x155c) |
| 9 | 0x18094ddf0 | the spawn's equip: tail-jumps to 0x18092c0f0 |
| 10 | 0x180921c30 | a player killed (the base's 0x180921c20 does nothing) |

Fields (rules object): +0x30 / +0x38 the ladder (`m_WeaponSequence`, a networked CUtlVector<CUtlString>: count,
elements), +0x48 / +0x49 restart flags, +0x4c the match leader's slot (-1 none), +0x50..+0x60 the "reached knife" music
sound handle (0 = not playing), +0x64 the winner's slot (-1 none), +0x68 a set of slots whose weapon must be
refreshed next Think. Controller: **m_iScore +0x91c** is the progress (level = m_iScore / 2, integer), +0x920 a second
score counter the same adds go to (unclamped), +0x8ec the pawn handle, +0x514 checked 0 or 3 before an equip.
Pawn: +0x344 the team (2 T, 3 CT), +0xb10 (param_2[0x162]) the weapon services, +0xb18 (param_2[0x163]) the item
services.

## The ladder (0x180956090 -> 0x180929ca0)

0x180929ca0 appends groups in this order, each through 0x1808ffa60(out, k, group): a Fisher-Yates over the group
(i = 0..n-1 when n > 1: j = RandomInt(i, n-1), swap i, j; tier0's RandomInt, the server's own stream), then its
first k appended.

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

17 levels, the same for both teams, rebuilt at each match start (slot 5). 0x180956090 copies the names into
`m_WeaponSequence`.

## A kill (0x180921c30)

Runs in the warmup (gamerules +0xd9) or a live round (+0x148 set, +0xd7c 0). Needs the victim's pawn and controller,
the attacker's (0x180fc9950 from the damage info) and 0x180ad2840(attacker pawn, victim pawn) true: enemies (teams
differ, or mp_teammates_are_enemies). Then, with `len` the ladder's count and `lvl` = attacker m_iScore / 2:

1. lvl >= len: nothing more (go to 4).
2. The killing weapon: 0x1809260d0(damage info) cast to CCSWeaponBase; its type vfn 0xc60 (CSWeaponType), 12 with no
   weapon (a grenade's projectile, the world). Knife (0): attacker +2, victim -2. Else, only while lvl < len - 1:
   attacker +1, victim -1 if it was the taser (8), else 0. At the knife level a non-knife kill gives nothing.
3. AddScore 0x180a6e350(controller, n): +0x920 += n, m_iScore += n, clamped at 0. The new level above lvl: below len,
   the attacker's slot goes into the refresh set (+0x68, a hash of the slot: murmur-style finalizer); at len, the
   attacker is the winner (+0x64).
4. The feedback 0x180951c90(rules, attacker, lvl), then the victim's: UI.ArmsRace.PlayerDeath; their level dropped
   (m_iScore / 2 below the old / 2): UI.ArmsRace.Weapon_LevelDown.

0x180951c90 (sounds through 0x1805c4680, a recipient filter each: 0x180c84d30 one player, 0x180c84870 everyone):
- the attacker's level == len: UI.ArmsRace.FinalKill_Knife to everyone. Else:
- UI.ArmsRace.Kill1 to the attacker; leveled up (lvl below the new level): UI.ArmsRace.Weapon_LevelUp; the new level
  == len - 1 (the knife): UI.ArmsRace.ReachedKnife to them and, if the music handle is 0, UI.ArmsRace.ReachedKnife_Music
  to everyone (the handle kept; Think stops it when the round ends).
- leveled up and not the leader already: if no other controller's level is >= theirs, they lead: the old leader (if
  any) hears UI.ArmsRace.Demoted, the leader slot is theirs, UI.ArmsRace.BecomeMatchLeader to them.

## The equip (0x18092c0f0, the spawn's and the refresh's)

Pawn alive (vfn 0x550), the controller's +0x514 0 or 3. level = m_iScore / 2:
- level == len - 1: 0x180b04ac0(weapon services, 1): the primary and pistol slots removed (0x180b04db0 0 / 1), the
  weapon_taser removed, each of molotov, incgrenade, smokegrenade, hegrenade, flashbang, decoy removed unless it's
  being thrown (vfn 0xaa8), the C4 dropped; then the knife slot (gear slot 2, 0x180c86620) selected (vfn 0xf0).
- level < len: the ladder's weapon, unless already held (0x180c86530 by name): `keep` = a gun was held (slot 0 or 1)
  and the active weapon is a knife or taser (type & ~8 == 0); both gun slots removed; the item services' give (vfn
  0xb8) with the weapon services' +0xdb flag = keep for the give (the new gun isn't switched to while you hold the
  knife or Zeus), restored after. Then a weapon_taser, if not held, given the same way with +0xdb = 1.

## Think (0x18094ea70)

Restart handling (+0x48, +0x49: the warmup's start / end, a game restart), then each queued slot of the refresh set
gets the equip, the set emptied. In a live round (+0x148, +0xd7c 0): no winner yet and the time left (mp_timelimit,
gamerules +0x100 / +0x108) <= 0: the winner is the controller with the highest m_iScore (strictly higher: the first
of a tie, in slot order; 0x180c844f0 filters who counts). With a winner: the knife music stopped (0x1805c4d20), the
round ended (GMR_EndRound) with reason 8 if the winner's pawn is a CT (+0x344 == 3), 9 a T, else 10, then the
intermission (0x1809654b0, "GMR_BeginIntermission", +0x1024 the time it ends): the match is over.

## The cfg (gamemode_armsrace.cfg, what the port reads)

mp_teammates_are_enemies 0 (two teams), mp_respawn_on_death_t / _ct 1, mp_randomspawn 1, mp_respawn_immunitytime 10,
mp_free_armor 2, sv_infinite_ammo 2, mp_roundtime 10, mp_timelimit 10, mp_maxrounds 0, mp_freezetime 0,
mp_warmuptime 20, mp_buytime 0, every cash_* 0, mp_startmoney 0, mp_maxmoney 0, mp_death_drop_gun 0,
mp_death_drop_grenade 0, mp_weapons_allow_map_placed 0, mp_ct / t_default_melee weapon_knife, the default
secondary / primary "", mp_display_kill_assists 0, sv_talk_enemy_living / dead 1, sv_deadtalk 1, spec_freeze_time 2,
bot_quota 10 fill, healthshot_health 50, mp_friendlyfire 1 with every ff_damage_reduction_* 0.

## Spawn immunity (every mode; on where mp_respawn_immunitytime > 0 or in the warmup)

Pawn fields: m_bGunGameImmunity +0x15a8, m_fImmuneToGunGameDamageTime +0x15a4 (GameTime), m_GunGameImmunityColor
+0x155c (Arms Race's slot 8 sets it by team: T -0x8a3716, CT -0x54483, else -1 when mp_teammates_are_enemies),
m_bHasMovedSinceSpawn +0xdf1. mp_respawn_immunitytime is registered at 0x1800a09f0 (default 4.0, flags 0x282000, "Set
to negative value to disable warmup immunity"). Ported in server/cs2web/combat/immunity.js.

- **The respawn** (180249530, ~line 176): t = mp_respawn_immunitytime; t < 0, or t <= 0 outside the warmup (gamerules
  +0xd9, 18093ec40): flag 0, time 0. Else: if not deathmatch (18093e040: game_type 1 && game_mode 2) or the pawn's
  0x388 bit 4 (vfn 0xc20, 0x1801cd1d0: unnamed), a warmup sets t = 3.0; otherwise (deathmatch) m_bInBuyZone (+0xf71) = 1.
  Then time = now + t, flag 1.
- **The active state's think** (180237450, every tick): only when (t > 0 or the warmup) and the flag is on. A ragdoll
  pawn (vfn 0x840 = 0x180b5d3b0: +0x334 m_bClientSideRagdoll) loses it. Past the time (now > time) it ends. Before
  it: if 180ad2380 (the controller's +0x514 is 0 or 3, the game phase isn't 4 / 5, and the warmup or
  mp_respawn_on_death_ct / _t for the pawn's team) and m_bHasMovedSinceSpawn, a time more than 1.0 s away becomes
  now + 1.0.
- **m_bHasMovedSinceSpawn**: PlayerMove_PostMove (180adcb90) sets it once the move data's velocity (+0x38) has a
  non-zero 2D length (1802d52b0: sqrt(x² + y²), so a fall from a high spawn point doesn't count); the respawn
  (180249fa0) clears it.
- **Ended at once** by 1801ffbb0 (flag 0, time 0): FireBullet (180a78120 -> 1801c6830 -> 180a4bbf0), the knife swing
  (180a2fa80 -> 180a4bea0), a grenade throw (1809d4a50 "grenade_thrown" -> 180a4be70, which also counts the throw at
  +0x7c).
- **Its effect**: the damage services' OnTakeDamage (180a93f70) does nothing while the flag is on (its first test:
  flag 0, the services' state not 7 / 8, ...). The hit group function 180a89430 also reads it (unread past that).

## The respawn (deathmatch, Arms Race)

The dead pawn's think (180237640, the death cam: src/cs2web/sim/deathcam.js) moves it to STATE_GUNGAME_RESPAWN (7)
when 180ad2380 allows (else, a team without respawns, the observer mode) at m_flDeathTime (+0xc7c) +
spec_freeze_deathanim_time (0.8, 0x1800c5320) + spec_freeze_traveltime (0.3, 0x1800c5500) + spec_freeze_time (the
cfg's 2; registered 3, 0x1800c53c0), or once m_flDeathTime + spec_freeze_deathanim_time + spec_freeze_time_lock (1.0,
0x1800c5460) is past and a button (but bit 33) is held, with mp_deathcam_skippable. mp_respawnwavetime_ct / _t (0 in
these cfgs) would hold it for the team's wave. STATE_GUNGAME_RESPAWN's think (180237bd0; the state classes' vtables
are 4 slots apart from 0x181792e20: observer, gungame respawn 0x181792e40, death-wait-for-key 0x181792e60) respawns the
pawn (1802521c0) unless sv_max_deathmatch_respawns_per_tick (> 0; the cfgs' 1) respawns have happened this tick (a
global count, DAT_181f9ed6c).

**The order among several waiting pawns** (2026-11-16): the state's enter (slot 0, 1802085d0) tries the respawn at once
as well, under the same cap; the count rises only when 1802521c0 respawned (it returns 0 while the engine's client
value, CServerSideClient +0xef4, is non-zero or the pawn's +0xdf0 is already set), and FrameUpdatePreEntityThink
(180923bc0 -> 180233f10) zeroes it each frame. The state thinks from the pawn's PreThink (180236f50 -> 1802371c0:
pawn +0xd48 vfn 0x10) in its usercmds, and the controllers run their usercmds in slot order (1805b70a0, frame.md): the
lowest slot first, at most the cap a frame, the rest the next frame in the same order. Ported in comp.js tick (the
players in join order, the repo's slot order); spawn-test.mjs "two due at once" checks it. docs/game/spawns.md has
the same.

## The Zeus (weapon_taser, CWeaponTaser)

weapon_taser.cpp's class, vtable 0x181919110; against CCSWeaponBaseGun (0x1818f0d38) it overrides slots 0x0, 0x20,
0x38 (0x180a2f130: precaches particles/blood_impact/impact_taser_bodyfx.vpcf and
particles/weapons/cs_weapon_fx/weapon_tracers_taser.vpcf), 0x48, 0x168-0x180. Ported in server/cs2web/combat/taser.js;
its numbers are weapons.vdata's (lasers-bake --weapons now writes CS2_TASER: m_nDamage 500, m_iMaxClip1 1,
m_flCycleTime 0.15 / 0.3, m_flRange 120, m_flRangeModifier 0.99, m_flArmorRatio 2, m_GearSlot GEAR_SLOT_KNIFE
position 1, Weapon_Taser.Single, the taser tracer).

- **PrimaryAttack** (0x180a2f1e0): CSBaseGunFire (1809f8a70) with the cycle time (vfn 0xbb0); a shot -> m_fFireTime
  (weapon +0x12a0) = now, then the think 0x180a315a0 scheduled at now + mp_taser_recharge_time (0x1800c4390: default
  30.0, "-1 = disabled", flags 0x282000). An empty one's dry fire (180a1e400) plays Weapon_Taser.ChargeNotReady (a
  pistol Default.ClipEmpty_Pistol, else Default.ClipEmpty_Rifle).
- **FireBullet** (0x180a2c980, once a tick: +0x12a4 holds the tick): Weapon_Taser.Single from the weapon; the lag
  compensation (the manager's vfn 0x10, 180ee08d0: StartLagCompensation(pawn, 2, the eye +0x14, the angles +0x20,
  radius)) with the radius m_flRange + 128 (vdata +0x830; 130 with no vdata). The radius is the job filter's
  (vtable 0x1819cf9b8, slot 0 **180ee3da0**: after WantsLagCompensationOnEntity (pawn vfn 0xaf0), a radius of exactly 0
  takes everyone, else |the entity's abs origin - the start| <= radius + 1024 (0x1817b2c84), (dz dz + dy dy) + dx dx,
  comiss / setbe); the bullets pass m_flRange (FX_FireBullets 1802a53d7), the knife its reach + 128. Ported:
  sim/src/combat/lagcomp.rs within_radius, ze_lag_poses words 23-26, combat.js posesAt's `unlag`.
  The trace **180a31040**(weapon, trace, start, end, plain, out end): the eye to eye + forward(angles) x m_flRange,
  TraceShape (180c2f3c0, which never asks the hitbox system: so the player layer 0x40000 of interacts-with
  0x1c1003 meets the pawns' collision boxes, not their hitboxes) with group 4, flags 0x4b, detail 0xffff, object set
  0xf, the shooter's handles first. `plain` 1: a CTraceFilter (vtable 0x18178c240) with +0x40 = 0 (the nearest
  hit); 0: CTraceFilterTaserIgnoreTeammates (vtable 0x18191a060, ShouldHitEntity **0x180a2f690**: not the shooter
  (+0x20) and not InSameTeam with it, vfn 0x350 180cfb4b0: g_Teams[+0x344] of both; +0x40 = 1). dir =
  normalize(end - start) ((dz dz + dy dy) + dx dx, 1 / |d| times each); radius r = 0, 2, 4: a line to the end, then
  spheres (180530ae0 marks a sphere for r > 0) to end - dir r; a trace that hits (fraction below 1 or start solid)
  writes the out end (a line's trace end +0x84; a sphere's contact point 18157ff20: (end + centre) - r normal) and
  returns 1 when what it hit is a player pawn (vfn 0x558) or a CChicken (the cast to 0x181f065c0,
  ".?AVCChicken@@"); else the next radius; past 4: 0. FireBullet: the out end starts as the line's end; the plain
  trace; a hit (1802c35a0) on a pawn (vfn 0xca8) that **180ad2840** says isn't an enemy (mp_teammates_are_enemies
  +0x58 of 0x18211a6d8, else the teams differ) runs the trace again with the flag clear and **180a316b0** (a cast to
  a live pawn: vfn 0x558 and 0xca8) on what it hit, whose result goes unused (0x180a2ccd2: rax dropped, rdi still the
  teammate): the victim stays the teammate, only the trace and the out end (the rope's end) are the second one's.
  A non-pawn hit is cast to CChicken (damaged when it is one: none in this game, so the world and map entities take
  nothing). The damage info (0x180fba3a0): attacker the pawn, inflictor the taser, 500.0 (not m_nDamage), DMG_SHOCK
  0x100 (no hit group, 180a89430; no armor, 180a88f30), the force direction the forward, the trace. Then the
  cstaserrope event: the start the pawn's weapon_hand_r attachment (180b51910 -> 180cb4610 / 180cabc70: the
  attachment by its name's MurmurHash2 in the bone cache; none: WorldSpaceCenter, vfn 0x2c8 18015a2f0) + 7.61985
  along its rotated (1, 0, 0) and 2.32976 along its rotated (0, 0, 1), the end the out end, the shooter's and the
  victim's handles. Ported: sim/src/combat/taser.rs (+ taser_abi.rs ze_taser), src/cs2web/sim/trace-world.js
  taser(), server/cs2web/combat/taser.js, taser-rope.js (the attachment from src/cs2web/data/hand-attachments.js,
  lasers-bake --attachments; the hand_R bone from poses.js's pose, its slot after the hitboxes).
- **The recharge think** (0x180a315a0): mp_taser_recharge_time >= 0 and clip (vfn 0xac0) 0 -> clip 1 (vfn 0xad0) and,
  when the round's start (18092a2a0) is before m_fFireTime, Weapon_Taser.ChargeReady.
- **Death drop**: 180b05460 step 3, weapon_taser thrown (mode 1) with mp_death_drop_taser (registered 1, 18009d5f0;
  gamemode_armsrace.cfg doesn't set it). Pickup: refused while one is carried (docs/game/pickups.md).
- **Arms Race**: the equip gives one when none is carried (0x18092c0f0, the services' +0xdb = 1: not switched to);
  the knife level removes it (0x180b04ac0); its kill takes 1 point off the victim (0x180921c30, type 8).

## Buying the Zeus (every team mode)

- **mp_weapons_allow_zeus** (registered 1800a4b30 at 0x182119bc8, default 1, flags 0x282000: "how many Zeus purchases
  a player can make per round (0 to disallow, -1 to have no limit)"). The modes' cfgs (game/csgo/cfg): competitive /
  competitive2v2 / rush 5, casual 2, deathmatch 1 then -1 (the later line holds), armsrace -1, demolition 0,
  dm_freeforall / retakecasual / teamdeathmatch 1. **mp_weapons_allow_typecount** (1800a4a80, 0x182119c18, default 5;
  casual 2, deathmatch / armsrace -1). **mp_warmup_items_nocount_policy** (1800a4130, 0x182119c28, default 42: bits
  1 c4, 3 kevlar / kit, 5 healthshot).
- **CanAcquire** (CCSPlayer_ItemServices 180ab9620, a purchase: method 1, a teammate's 2): a weapon already carried
  (180b02570) -> 2; then the Zeus: allow_zeus 0 -> 9; above 0 and this round's purchases of it (controller +0xe48
  +0x298, 180a43a60) >= mult x allow_zeus -> 3 (mult 1000 in the warmup when the nocount policy has the item's
  category bit: 0 gun, 1 C4, 2 grenade, 3 kevlar / kit, 4 the Zeus, 5 healthshot; else 1); the item's team (def
  +0x48) not the buyer's -> 6; a knife -> 9; typecount 0 -> 9, above 0 and the count >= mult x typecount -> 3; the
  price over the money -> 13. A pickup (method 0): the Zeus allowed only with allow_zeus != 0 (else 8).
- **The buy** (180a7cf90): CanAcquire's 2 / 4 / 5 -> "#Cstrike_TitlesTXT_Cannot_Carry_Anymore", 1; any other but 0 ->
  4 silently (the jump table at 0x180a7d798: 0 go on, 2 / 4 / 5 the message, 1 / 3 / 6-10 4). Then the price
  (GetItemPrice: weapon_taser's m_nPrice 200), the money, GiveNamedItem (Weapon_Equip without the weapon services'
  +0xdb keep flag: switched to, as a bought gun is; Arms Race's equip sets it). The count goes up (180a4ab40).
- Ported: src/cs2web/modes/team/buy-items.js purchaseLimit (the Zeus in BUY_MENU's gear column, its price from
  CS2_TASER), server/cs2web/modes/team/cs2-buy.js (roundBuys, the Zeus's branch, every item's limit), the snapshot's
  bza / bal (core/snapshots.js) and the menu's NOT ALLOWED / AT LIMIT / OWNED (client/modes/team/buy-menu.js),
  gamemodes.js (each mode's cfg values). ZE: GFL / CS2Fixes' weapons.cfg disables the taser
  (src/cs2web/modes/ze/config.js DISABLED_WEAPONS: CS2Fixes' configs/zr/weapons.cfg.example, ZR's CanAcquire
  NotAllowedByProhibition): no buy, no pickup, no give for a human; that rule is ZR's alone now (items.js canPickup:
  a team match's CT picks up a Zeus, a flashbang, a smoke as CS2 allows).
- The death sound: 180ac13d0 plays Player.Death from the victim (PAS 0.8), Player.DeathTaser when the damage type is
  exactly 0x100, the _F / DeathFem ones with m_bHasFemaleVoice (+0xe6a), unless the attacker is a CPlantedC4 (the
  class 18212afd8: 1800b7e50 registers it as "planted_c4" / "CPlantedC4"); a head shot instead has the three
  DeathHeadShot events only; a pawn attacker's kill adds the DeathBody trio (damage-sounds.js death).
- The rope's start: the attachment into the bone cache is 180ca65e0 -> 0x1814a2f70 -> **0x1814a2730** (one influence:
  position (C + (w t + o)) s + p, rotation q x r with r flipped to q's hemisphere, 181475200's lane sums; taser-rope.js
  float for float), then 180a2c980's offsets (C + (w t + a), (p + rX k1) + rZ k2).
- The holster (180a2d5a0): mp_taser_recharge_time < 0 and no ammo (vfn 0xaa8, 180b7c4a0) -> 180b01b60 takes the Zeus
  off the pawn (loadout.js holster, L.taserNoRecharge).
- CS2's bots never draw a carried Zeus. Their behaviour trees (pak01 scripts/ai/<mode>/bt_default.kv3, armsrace's
  too) equip with action_equip_weapon "BEST" (0x18030c4e0: +0x60 set -> **CCSBot::EquipBestWeapon 0x1802c4430**): gear
  slot 0 when the bot_allow_* of its type (rifles 3, shotguns 4, machine guns 6, snipers 5, SMGs 2) allows it and it
  isn't empty (vfn 0xaa8), else gear slot 1 with bot_allow_pistols, else nothing more when weapon_knife is out, else
  gear slot 2's first weapon (180c86620(services, 2, -1): m_hMyWeapons in order; the knife comes first, given at spawn).
  bt_config.kv3's attack table gives TASER -1 (no attack timings), as the knife and the C4. Our bots (core/bots.js)
  take the same order: primary, pistol, knife.
- **The enemy test 0x180ad2840**, read whole: 0x180fe1050 fills the other's info (+0 null, +1 a player pawn, +4 the
  handle, +8 its controller's player slot via 180b55410, +0xc its team via 180ac5e00: the controller's 180a79ab0,
  else the pawn's +0x344); the attacker's slot equal to the other's -> false; mp_teammates_are_enemies -> true;
  else the attacker's team != the other's. 180a79ab0: with sv_coaching_enabled (0x182119820, registered 1800a5970,
  default 0) a spectator (team 1) with a coached team (+0x84c) counts as that team. Ported: src/cs2web/player/enemy.js,
  each pawn's `enemy` bit in ze_taser (taser.rs), the server's shot and your predicted one.

## The golden knife

There is none to port: weapon_knifegg is the ladder's last name (0x180929ca0) and a panorama icon
(icons/equipment/knifegg.vsvg_c); weapons.vdata has no weapon_knifegg block and pak01 no golden knife model. The knife
level strips the guns and brings out the knife the pawn already carries (0x180b04ac0 then gear slot 2).

## Still unread

- Where m_iScore's ordinary kill / assist points go in Arms Race (the base rules' contribution score): the port gives
  only the mode's points (a kill +1 would make the level jump); TODO trace CCSGameRules' score award under this mode.
- Deathmatch's spawn-immunity branch test (pawn 0x388 bit 4).
- The Arms Race HUD (the next-weapon panel, the level list): client.dll and its panorama, unread.
- The time-left formula (+0x100 int + 0x108 against the game start) beyond "mp_timelimit".
