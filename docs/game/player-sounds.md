# Player and physics sounds (who hears which sound event)

server_20261105 (image base 0x180000000) unless named; client_20261105 (client_20261015 addresses in brackets); vphysics2_20260924, vphysics2_20261103 (schema). game_sounds_physics.vsndevts, game_sounds_player, surfaceproperties.vsurf, soundstacks_csgo_*.vsndstck, items_game.txt, weapons.vdata.

## Functions

| Address | Module | What |
|---|---|---|
| 180f69780 | server | EmitSound(out*, filter*, entity index, EmitSound_t*) (EmitSound_t: +0 name, +0x14 volume = 1.0, +0x28 = 100) |
| 180f695d0 | server | an entity's EmitSound(entity, out*, name, 0, 0, 1, 0) |
| 180f697b0 | server | EmitSound (volume 1.0f) |
| 180c83dd0 | server | CRecipientFilter ctor (vtable 181785ca8) |
| 180c84870 | server | AddAllPlayers: every controller with connection state (+0x514) 0 or 3; thunk (filter, position) |
| 180c84e00 | server | AddRecipient(player, withObservers): with the flag, every controller whose pawn observes the player (observer services vfn 0xb8 mode == 2, vfn 200 target == the player) |
| 180c8b6a0 | server | RemoveRecipient(player): the player and its mode-2 observers |
| 180c8b610 | server | RemoveRecipient(controller): one bit |
| 180c84a60 | server | add the HLTV (m_bIsHLTV +0x510) |
| 180c83a60 | server | PAS filter (vtable 1818e4a70) |
| 180c864b0 | server | (filter, entity, 0.8): vfn 0x560 true -> one recipient (180c84c60), else 180c861f0(filter, entity vfn 0x6b8's point, attenuation) (earshot unread) |
| 180c8c8d0 | server | prediction rule (less the predicting player) |
| 180a77710 | server | one PAS sound from a pawn (pawn, excluded controller, name); global 181e23e88 set to 1 around it |
| 180a77f60 | server | (info, head): the attacker a server need not tell |
| 1809bff80 | server | smoke on a line (from*, to*, 0): sum over active smokes (list head 181faa578, next +0xb60, active +0xb6c) |
| 1803d95f0 | server | m_MoveType (+0x2f5) |
| 180a94400 | server | damage services' post |
| 180a95310 | server | the hit's sounds (services, result, armored) |
| 180cacf80 | server | the info's trace |
| 180cf7020 | server | health |
| 1801d6c60 | server | eye-to-eye line (filter vtable 18178c240) |
| 180c8cbc0 | server | emit from the victim's index |
| 180590da0 | server | (181ff56c8, attacker, victim's 1803d6f50) -> params +0x24 (unread) |
| 1813aa290 | server | entity index |
| 1805c0a60 | server | sound parameter (181ff56a0, filter, handle, hash, value) |
| 1802143f0 | server | (pawn) parameter value (4 bytes) |
| 1802089a0 | server | CCSPlayerPawn::Event_Killed |
| 180ac13d0 | server | the death's sounds (pawn, info) |
| 18212afd8 | server | class tested for the death sound (read as CCSPlayerPawn, unconfirmed) |
| 180a01880 / 180a019e0 / 180a01b40, 180b0a700 | server | weapons' owner casts (other users of 18212afd8) |
| 180b1c290 | server | CCSPlayer_WeaponServices::BumpWeapon (tail: pickup sound) |
| 18024b730 | server | silent(_, pawn) |
| 1803d6fb0 | server | pawn velocity |
| 1801cd370 | server | 2D length `sqrtss(vy vy + vx vx)` |
| 180b0a410 | server | the pawn |
| 180a6ee50, 180a6f6f0, 180ac8330, 180aea0a0 | server | Player.PickupWeapon emitters (unread) |
| 1801b3820 | server | CItemKevlar MyTouch (vtable 0x1817892f0, slot 0x9a8) |
| 1801b36b0 | server | CItemAssaultSuit MyTouch (vtable 0x181787380, slot 0x9a8) |
| 1801b3d70 / 1801b3c30 | server | m_bHasHelmet / m_ArmorValue network change |
| 18023a540 | server | (pawn) (unread) |
| 180ab85f0 | server | GiveNamedItem |
| 1816b6d80 | server | dynamic cast to the weapon type 181effb00 |
| 180e36650 | server | a weapon's give path |
| 1803eeac0 | server | CBaseEntity::Touch (vfn 0x4b8) |
| 180571ca0 | server | after GiveNamedItem's origin (unread) |
| 1809aec60 | server | vdata m_aShootSounds find |
| 1809c05c0 / 1809c0660 | server | zoom sounds |
| 1809c0760 | server | decoy's shot |
| 1809d3cd0 | server | StartGrenadeThrow (slot 2 at 1809d401c) |
| 1809d4a50 | server | ThrowGrenade (slot 0x17) |
| 180c9e320 / 180c9e5b0 / 180c9e7e0 | server | vdata KV3 parse |
| 18101cf10 | server | items_game visuals parse (stores +0xf8 + slot x 8 at 18101d8dc) |
| 181dbd890 | server | legacy sound name table (16-byte {name, WeaponSound_t}: empty 0, secondary_empty 1, single_shot 2, ...) |
| 0x181956c.. | server | WeaponSound_t names (32-byte {name*, value}) |
| 180056a10 | server | weapon_near_empty_sound registration |
| 180b1d420 -> 180b25450 | server | CCSPlayer_WaterServices slot 0x60 (vtable 0x181928258): drowning think |
| 180d079f0 | server | CBasePlayerPawn::PreThink (walks components +0xb58, next +0x40) |
| 180afd350 | server | water services constructor |
| 18017ca80 | server | time = 0 |
| 180b1e110 | server | slot 0xc8: reset (+0x50 = 0.0f, +0x4c = 2) |
| 180b02680 | server | slot 0xc0: false |
| 180b1c0f0 | server | slot 0xb8: water-level change callback |
| 180b67370 | server | pawn vfn 0x698: wade sounds |
| 1803d95d0 | server | move parent |
| 18017e2d0 | server | compare |
| 18017dc70 | server | time + float |
| 180fba3a0 | server | CTakeDamageInfo ctor |
| 180c10aa0 | server | (0x18218b950, 0): the world |
| 1803ed610 | server | TakeDamageOld |
| 180c86d00 / 180927cb0 | server | now = tick x interval |
| 180249530 | server | respawn (doesn't reset water services) |
| 180abb840 | server | CheckFalling |
| 180adc190 | server | fall damage (mv) |
| 1800c93b0 | server | sv_falldamage_scale registration |
| 18020a500 | server | pawn vfn 0x98: Player.DamageFall[.Fem] |
| 180feb800 | server | screen fade |
| 1809236a0 | server | CCSGameRules vfn 0x200: false |
| 1801ff590 | server | agent model setup: m_strVOPrefix, m_bHasFemaleVoice |
| 180ac165a | server | death's female voice read |
| 1809c8542, 1809d3f4d | server | jump throw's female voice read |
| 1809c8320 | server | ItemPostFrame branch (jump throw at 1809c8522) |
| 180ad2570 | server | jump window (0.1) |
| 180a02230 | server | grenade owner |
| 180e8eda0 | server | PhysicsCheckWaterTransition |
| 180e904c0 / 180e8f1f0 | server | PhysicsToss / PhysicsCustom |
| 1808c0940 | server | CBaseGrenade bounce touch |
| 1803d9e70 | server | water type |
| 180d05340 | server | VPHYSICS fluid touch (no sound) |
| 180c86d20 | server | GiveAmmo |
| 180b61580, 180b7a440 | server | GiveAmmo callers (180b61580 = CBasePlayerWeapon slot 0xaf8) |
| 1808d6e70 | server | CBrokenGlassTrap (vtable 0x1818aff68 slot 0x48) -> 1808c0d90 |
| 1809c8eb0 | server | CItemDogtags (slot 0x9a8) |
| 1808c63a0 | server | cash stack touch |
| 180d3d490 / 180bc68b0 / 18024cb10 | server | ItemSoda.Bounce / Metal.SawbladeStick / SprayCan |
| 180582670 | server | physics dispatcher (physics game system, world) |
| 180571240 -> 180593af0 | server | contact vectors adaptor |
| 180d1a340 | server | CBaseEntity vfn 0x278 VPhysicsCollision (the weapons' and CPhysicsProp's sound slot too) |
| 180d1a420 | server | vfn 0x280 (entity, index, event) |
| 180c00e80 | server | game material of a surface |
| 1805a9c70 | server | impact sound volume (system 181ff5690, ...) |
| 180e8df50 / 180e8dde0 | server | impact effects (by 181e27f5c / 181e27f60) |
| 180cbd840 | server | CWorld vfn 0x278 (static impact volume path) |
| 180575ab0 | server | impact sound queue |
| 1805ad380 | server | flush (CPhysicsGameSystem vtable 1818078c8 slot 34; also from 1805c83b0) |
| 1805aa5b0 | server | play an impact (out, name, entry, other surface's +0xac) |
| 1805c4680 | server | start the event |
| 1805a9a30 | server | break sound queue |
| 1805aaaf0 | server | play a break sound |
| 1800ad583 / 1800ad633 | client | cl_predict_body_shot_fx / cl_predict_head_shot_fx registrations |
| 180c77710 | client | pawn's game event handler (item_pickup; pawn at this - 0x14c8; local test 180c7781f..) |
| 180c0ad30 | client | emit from the pawn |
| 1807c3d20 | client | vdata m_aShootSounds find |
| 1807cf6c0 / 1807cf760 | client | zoom sounds |
| 1807dfaa0 | client | StartGrenadeThrow (slot 2) |
| 181115d80 | client | items_game visuals parse |
| 181651818 | client | libjpeg table (false scan match) |
| 0x1821d70b0 | client | legacy script keys (empty, ..., nearlyempty, reload, single_shot_accurate) |
| 180d25990 | client | FX_FireBullets |
| 180d26730 | client | play a weapon sound slot (vdata 1807cd090, the name via 1807c3d20; emit tail unread) |
| 1800f5c00 | client | weapon_near_empty_sound registration |
| 1800f5700 | client | snd_max_pitch_shift_inaccuracy registration |
| 180b9b490 [180b99a70] | client | bullet impact sound function (called from 180d27a20 in 1015) |
| 1827a2190 | client | impact sound job queue (vfn 0x428, 0x48-byte job) |
| 180c0ae30 | client | play FX_RicochetSound.Ricochet |
| 1800d42f0 | client | r_impact_ricochet_chance registration |
| 18122ed70 [18122a370] | client | effect handler using the ricochet name (dispatcher unread; sound via 180c1b230) |
| 180bae330 | client | PhysicsCheckWaterTransition |
| 1807214b0 | client | CBaseGrenade bounce touch |
| 180c30510 | client | C_LocalTempEntity hit-surface sound (from 180c2d7b0 = vtable 0x181c86658 slot 0x8d0) |
| 1811ae590 [1811a9bc0] | client | CCSHudWeaponSelection::SelectWeapon (slot 0x268) |
| 180805ce0 | client | CanBeSelected (vfn 0x998): an owner and vfn 0x9e0 |
| 18082f260 | client | knife CanBeSelected: true |
| 1807e24a0 | client | vfn 0x9e0 guns, C4, Zeus: true |
| 1807e2450 | client | vfn 0x9e0 grenade: (UsesClip and clip > 0) or reserve > 0 |
| 1811a9cb0 | client_20261015 | SelectSlot (slot 0x248 of vtable 0x181d21320) |
| 180c19e30 | client_20261015 | slot 0x2d8 (from the per-grenade binds 0x288..) |
| 180c0cc30 | client_20261015 | GetNextActivePos (0x258) |
| 1800ddf70 | client_20261015 | hud_fastswitch registration (object 0x18256aeb0; 1800dded0 before it registers gl_clear: checked 2026-11-21) |
| 1811a68c0 / 1811a6980 via 1811a7530 / 1811a77c0 | client_20261015 | next / prev (0x228 / 0x230) |
| 1811a5f30, 1811a5ac0, 1811a6450 | client_20261015 | slots 0x2f0 / 0x2f8 / 0x300 |
| 180943870 | client (build not stated; read with the 1015 callers) | owner |
| 1803ae000 | client | client physics event dispatcher |
| 1803ce260 | client | client impact (system, &scratch, event, index); twin of server 1805a9c70 |
| 1803b7840 | client | speed `|(vz nz + vy ny) + vx nx|` |
| 1803a3bc0 | client | client impact queue (twin of 180575ab0; flush unread) |
| 1808de830 | client | Player.Surf.* |
| 1800b2e70 | client | sv_surf_sounds registration |
| 1801fe920 | vphysics2 | collision tracker add (tracker, contact, flag) |
| 1802faf00 | vphysics2 | pair flags |
| 1801feca0 | vphysics2 | contact end |
| 1801fa810 | vphysics2 | collision record (0x70 bytes) |
| 180059170 | vphysics2 | world vfn 0x3d0: events |
| 180058a90 | vphysics2 | event fill (0x100 bytes) |
| 18000b970 | vphysics2 | surface property (shape, sub shape, triangle) |
| 180011d60 | vphysics2 | body wrapper vfn 0x148: body +0xfc |
| 180011320 | vphysics2 | body wrapper vfn 0x430: body +0x9c (time scale) |

## Fields

| Offset | Field |
|---|---|
| filter +8 | recipient mask (two u32 words, bit = slot) |
| filter +0x10 / +0x14 | predicting client's slot (-1) / 0xff |
| filter +0x16 | skip the predicting player |
| controller +0x514 | connection state |
| controller +0x510 | m_bIsHLTV |
| controller +0x708 | last CSGOUserCmdPB (+0x49 body / +0x4a head predicting) |
| pawn +0xb18 (+0x163*8) | m_pItemServices |
| item services +0x49 | m_bHasHelmet |
| pawn +0x1514 | m_ArmorValue |
| pawn +0xe6a | m_bHasFemaleVoice |
| pawn +0xe70 | m_strVOPrefix |
| agent item definition +0x3a8 | vo prefix |
| pawn +0x1494 | set when armor was hit and none is left |
| pawn +0x344 | team |
| pawn +0x388 | m_fFlags (0x4000 FL_GODMODE) |
| pawn +0x404 | m_flWaterLevel |
| pawn +0xb50 | movement services (+0x25c fall speed) |
| pawn +0x1283 | m_bJumpThrow |
| entity +0x2f5 | m_MoveType / m_nActualMoveType |
| entity +0x414 | flags (0x40 cleared below 1 u/s) |
| game rules +0xd8 | m_bFreezePeriod |
| info +0x38 / +0x3c | inflictor / attacker (handles) |
| info +0x4c | damage type bits |
| info +0x68 | trace |
| info +0x7c | solids shot through before the hit |
| result +0 / +0x20 | the info / m_flDamageDealt |
| damage services +0x4c | dmg_armor of this hit |
| weapon services +0xd8 | 1 for GiveNamedItem with no position |
| entity +0x2b0 | m_pfnTouch |
| vdata +0x4f8 / +0x504 / +0x508 | sound map / count / elements (0x28 each) |
| vdata +0x520 | CSWeaponType |
| vdata +0x7e0 | m_flInaccuracyPitchShift |
| vdata +0x7e4 | m_flInaccuracyAltSoundThreshold |
| item definition visuals +0xf8 + slot x 8 | items_game sound keys (read by nothing) |
| water services +0x48 / +0x4c / +0x50 | m_NextDrownDamageTime / m_nDrownDmgRate / m_AirFinishedTime (GameTime_t) |
| +0x54 / +0x58 / +0x64 | m_flWaterJumpTime / m_vecWaterJumpVel / m_flSwimSoundTime |
| +0x68 / +0x6c / +0x70 / +0x74 | 0 / -1 / 0 / 0 at construction |
| CPhysSurfaceProperties +0x48 | m_audioSounds (+0x20 m_bulletImpact, +0x40 m_meleeImpact) |
| +0xa8 | m_audioParams (+0x1c m_flOcclusionFactor) |
| surface (client) +0x68 / +0x88 / +0xc4 | m_bulletImpact / m_meleeImpact / m_flOcclusionFactor |
| record +0 / +0xbb / +0x4c | surface / flag / data's surface index |
| temp entity +0x1284 | sound flags (1 glass, 2 metal, 4 flesh, 8 wood, 0x10 shrapnel, 0x20 shell, 0x40 concrete, 0x80 / 0x1000 shotgun shell) |
| surface +0x10 | game material index (table 18218e4f8 +0x28) |
| surface +0x48 / +0x50 / +0x78 | soft / hard / break sound |
| surface +0xac | hardness |
| surface +0xb8 / +0xbc | hard threshold / hardVelocityThreshold |
| surface +0xc0 | static impact volume (read as m_flStaticImpactVolume) |
| system +0x4c8 / +0x4d0 | impact queue count / entries (0x28) |
| system +0x4e8 | break queue (0x10-byte entries: position, surface) |
| system +0x510 / +0x518 | listeners |
| system +0xd8 | summed frame time |
| 181e27f58 | silent game material id (unread which) |

## Constants

| Value | What |
|---|---|
| 0.8 | PAS attenuation |
| 1.0 / 100 | EmitSound_t volume / +0x28 |
| DMG_FALL 0x20, DMG_BURN 8, DMG_BULLET 2, slash 4, DMG_CLUB 0x80, DMG_SHOCK 0x100, DMG_DROWN 0x4000 | damage bits |
| 0x20 / 0x28 | no-sound mask (armor not hit / hit) |
| 1.4 | smoke gate |
| 0xdd82057c | the hit sound parameter (name unread) |
| 135.2 | silent pickup speed |
| CSWeaponType 9 grenade, 7 C4 | pickup sound pick |
| WEAPON_SOUND: SINGLE 2, SPECIAL1 9, NEARLYEMPTY 12, IMPACT 13, REFLECT 14, SECONDARY_IMPACT 15, SECONDARY_REFLECT 16, RELOAD 17, SINGLE_ACCURATE 18 (0x12), ZOOM_IN 19 (0x13), ZOOM_OUT 20, RADIO_USE 23 (0x17) | WeaponSound_t |
| weapon_near_empty_sound | handle 0x1825c3ec0 (+0x58), flags 0x6000 (replicated 0x2000 + cheat 0x4000), default 1, no help |
| 0.2f (0x181acff20) | near-empty fraction |
| snd_max_pitch_shift_inaccuracy | handle 1825c3ee8, default 0.08f, no flags, no help |
| r_impact_ricochet_chance | handle 182566f30, default 0.3f, flags 0x4000 |
| 12.0f / 1.0f / 5 | drown air / damage interval / max rate |
| 580, 0.23809524f, 0.1 | fall threshold, scale, floor |
| sv_falldamage_scale | default 1.0 |
| 10000, 10 | death fade hold, flags |
| 0.1 | jump throw window |
| sv_surf_sounds | replicated 0x82000, default 0, "Should we try to play sounds for surf?" |
| 30 u, 34 degrees | Glass.Strain trigger |
| 10.0 | event +0x18 (time since the pair's last collision, not kept) |
| 0.5 | event +0x18 threshold |
| 9.765625e-06 (1 / 320^2) | impact volume scale |
| 70.0 | client impact speed floor |
| 500.0 | default other body mass |
| 0.0001 | speed bias in the queue |
| 4 | queue absorb limit |
| 0.05 s | flush interval |
| 3 | break entries averaged |
| sv_phys_sound_disable_impact_sounds_under_hard_threshold | object 181ff5818, default false |
| 0x5a7cce4d position, 0x2d8464af volume, 0x41a38e55 speed, 0x4c2cbe7f other hardness | impact event parameter hashes |
| 0x31415926 / 0x53524332 | MurmurHash2 seeds tried (no match) |
| FLT_MAX | body +0x1f8 unset |

## Recipients

- 180a77f60: the info's attacker (+0x3c) when a player pawn that is also the inflictor (+0x38) and whose controller's +0x708 block has +0x49 (body) / +0x4a (head) set -> that controller, else 0. Read as the client's cl_predict_body_shot_fx / cl_predict_head_shot_fx (client-side userinfo, the defaults read as 0; damage-prediction.md): a client that predicts its hit effects is left out of the server's copy.

## A hit (180a94400 -> 180a95310)

The post first sets pawn +0x1494 when armor was hit and none is left; `armorDmg = services +0x4c`; **no sound when `type & (armorDmg < 1 ? 0x20 : 0x28)`** (a fall never; a burn not when the armor took part). Else `180a95310(services, result, armorDmg > 0)`:

1. hit group = the trace's only when `type & DMG_BULLET` and a trace; **head = (group == 1)**. excluded = 180a77f60(info, head).
2. `type & 8`: `Player.BurnDamage` (armored `Player.BurnDamageKevlar`) by 180a77710; done.
3. `type & 0x80`: `Flesh.BulletImpact` (armored `Player.DamageKevlar`); done.
4. Victim health < 1: nothing (the death's sounds play).
5. `(int)m_flDamageDealt <= 0`: `Player.DamageKevlar` by 180a77710; done.
6. attacker = the info's attacker if a player (vfn 0x558 and 0xca8).
7. Feedback gate: an attacker, `type & 6`, a line from the attacker's eye (vfn 0x5e8) to the victim's (mask unread) with `(info +0x7c == 0 || (fraction >= 1.0 && !startsolid))`, then `1809bff80(attacker eye, victim eye) < 1.4`.
8. Not the head:
   - Feedback: AddRecipient(attacker, observers) minus excluded; `Player.DamageBody.AttackerFeedback`, with `type & 4` `Player.DamageBody.Knife.AttackerFeedback`; armored `Player.DamageBodyArmor.AttackerFeedback` / `Player.DamageBodyArmor.Knife.AttackerFeedback`. From the victim's index; params +0x24 = 180590da0(...).
   - Onlookers: AddAllPlayers, RemoveRecipient(attacker) only if the feedback played, RemoveRecipient(victim), the HLTV: `Player.DamageBody.Onlooker` / `Player.DamageBodyArmor.Onlooker`, from the victim's index.
   - Victim: AddRecipient(victim, observers): `Player.DamageBody.Victim` / `Player.DamageBodyArmor.Victim`, **from the attacker's index** when there is one, else the victim's; then `1805c0a60(181ff56a0, filter, handle, 0xdd82057c, { type 3, 4 bytes: 1802143f0(victim) })`.
9. Head (armored = the victim's m_bHasHelmet, not the armor hit):
   - Victim: `Player.DamageHeadShot.Victim` / `Player.DamageHeadShotArmor.Victim`, from the victim's index.
   - Feedback (same gate): `Player.DamageHeadShot.AttackerFeedback` / `Player.DamageHeadShotArmor.AttackerFeedback`, then the 0xdd82057c parameter with 1802143f0(attacker).
   - Onlookers: `Player.DamageHeadShot.Onlooker` / `Player.DamageHeadShotArmor.Onlooker`.
- Every EmitSound_t: volume 1.0, +0x28 = 100. With no attacker the victim's and onlookers' events still play (a map's trigger_hurt).

## A death (Event_Killed 1802089a0 -> 180ac13d0 first, before armor is zeroed)

- attackerEnt = the info's attacker (any entity); attacker = it when a player. Head and excluded as in a hit.
- Head: no attackerEnt -> nothing. Else `Player.DeathHeadShot.AttackerFeedback` (helmet `Player.DeathHeadShotArmor.AttackerFeedback`) to AddRecipient(attackerEnt, observers) minus excluded; with a player attacker, onlookers' `Player.DeathHeadShot[Armor].Onlooker` (all minus victim and attacker, plus HLTV) and the victim's `Player.DeathHeadShot[Armor].Victim`. All from the victim's index. Done.
- Else: `Player.Death` (`Player.DeathFem` with m_bHasFemaleVoice); `type == 0x100` exactly: `Player.DeathTaser` / `Player.DeathTaser_F`. Plays (PAS, 0.8, from the pawn) when no attackerEnt, or its class isn't derived from 18212afd8 (walk over the class's bases: identity +8, +0x60 / +0x18). So a player's kill has no `Player.Death`.
- Then armored = `m_ArmorValue > 0` and hit group 0, 2, 3, 4, 5 or 8 (legs 6 / 7 not; 0 unless a bullet's trace). Player attacker: victim's `Player.DeathBody.Victim` / `Player.DeathBodyArmor.Victim`, onlookers' `Player.DeathBody[Armor].Onlooker`; any attackerEnt: `Player.DeathBody[Armor].AttackerFeedback` (minus excluded). No line / smoke gate, no Knife variant.

## A pickup (BumpWeapon 180b1c290's tail; pickups.md)

- `silent = 18024b730(_, pawn)`: 1 when the game rules exist, **m_bFreezePeriod is 0** and the pawn's 2D speed **< 135.2**. It is item_pickup's `silent`; when 0 the pawn emits (180f695d0): `Player.PickupGrenadeAudible` for type 9, `Player.PickupC4` for type 7, else `Player.PickupWeaponAudible`.
- `Player.PickupWeapon`: items/pickup_weapon_02.wav, volume 0.7 (its emitters unread; the ammo extraction's is in pickups.md).
- Own silent pickup (client 180c77710): "item_pickup" with the event's userid this pawn and the local player's live pawn (180c7781f..: [rbp+0x130]), `silent` set: **Player.PickupWeaponSilent** from the pawn (180c0ad30). item_pickup's silent is BumpWeapon's / GiveDefuser's (18024b730).

## Armour MyTouch (slot 0x9a8 (309))

1. (item, pawn): nothing unless the pawn's vfn 0x558 and 0xca8 (presumably IsPlayer / IsAlive).
2. Suit only: m_bHasHelmet = 1. Both: m_ArmorValue = 100; kevlar leaves the helmet.
3. 18023a540(pawn).
4. Pawn vfn 0x550 true (unread): CRecipientFilter with AddAllPlayers, the *item's* entity index, EmitSound of `Player.EquipArmor_CT` for team 3, else `Player.EquipArmor_T`.
5. Returns 1 (taken), 0 when the gate failed.

- From game_player_equip / GiveNamedItem: no position (param 6 null) sets weapon services +0xd8 = 1; a non-weapon (cast null) gets vfn 0x4b8 with the pawn: CBaseEntity::Touch (both items' slot), which runs m_pfnTouch (+0x2b0) and the other's vfn 0x4c8 / 0x4b8. The item spawns at the pawn's origin + 5 z (then 180571ca0).
- The buy menu's armour doesn't come here: item_kevlar 180a6f6f0 / item_assaultsuit 180a6ee50 play Player.PickupWeapon (buy.md; from the pawn, no silent test: item_pickup's silent is 0).

## Low-ammo click (client FX_FireBullets 180d25990)

- items_game.txt `sound_nearlyempty "Default.nearlyempty"` (44 prefabs); weapons.vdata m_aShootSounds NEARLYEMPTY -> Default.nearlyempty on the guns.
- The server reads slot 12 nowhere (1809aec60's eight callers: zoom 1809c05c0 / 1809c0660, 1809c0760, grenades 1809d3cd0 / 1809d4a50, vdata parse 180c9e320 / 5b0 / 7e0).
- Client, right after the shot's sound (180d25dcf: 180d26730 with SINGLE or 0x12), weapon in r12:
  1. weapon_near_empty_sound on;
  2. the weapon not null; vfn 0xa48(0) > 1 (the max clip: read by use, it must exceed 1 and divides);
  3. `f32(vfn 0xa58(0)) / f32(vfn 0xa48(0)) <= 0.2f` (comiss 0x181acff20 against the quotient; the clip over the max clip, both cvtdq2ps);
  4. `180d26730(player / entity, weapon, 12, the shot's r9, volume = the shot's xmm7, sound level 100 (0x64), the shot's [rbp+0x518])`.
- FX_FireBullets runs before BaseGunFire's Clip1 - 1 (fire-gate.md): a 30-round mag clicks on its last 6 rounds, a 5-round AWP on its last.
- Default.NearlyEmpty: lowammo_01.wav, volume 1.5, delay 0.05 s, position_offset z 60; positional, 1100 u.

## Accurate shot (client FX_FireBullets 180d25990)

1. At 180d259c1 `a = min(1.0f, inaccuracy [rbp+0x4e8])` (minss).
2. Before the shot's sound (180d25d03): `shift = min(a, snd_max_pitch_shift_inaccuracy) x m_flInaccuracyPitchShift` (minss, mulss).
3. Slot ([rbp+0x508]) 2 and `m_flInaccuracyAltSoundThreshold > 0 && > a` (two comiss / jbe): slot 0x12, shift 0.
4. Pitch `100 + (int)shift` (cvttss2si; add 0x64); volume 0 when [rbp+0x528] is 0.
- weapons.vdata sets the two on the Negev alone (-50 and 0.02; 83 others 0); its SINGLE_ACCURATE is `Weapon_Negev.SingleFocused` (items_game `sound_single_shot_accurate` agrees). Under 0.02: focused at 100; from 0.02 plain at 99 down to 96 (0.08 and over).
- A silenced shot's slot is SPECIAL1 (9), never 2 (taken from the weapons' sound pick, fire-gate.md); no silenced gun has an accurate sound.

## Ricochet (client 180b9b490)

The impact effect's sound function: (this, the trace's record, the impact's data).

1. Surface: the record's own (+0), or for fraction >= 1 without flag +0xbb / the same entity with a non-zero surface index, the physics properties' by the data's index (+0x4c).
2. Name: damage bit 0x80 and a non-empty m_meleeImpact, else m_bulletImpact. **Empty: return** (no ricochet).
3. Impact sound queued (0x48-byte job to 1827a2190 vfn 0x428: position, name, data's fields).
4. **`RandomFloat(0, 100) <= r_impact_ricochet_chance x (surface +0xc4 x 100)`** (180b9b66f..180b9b6a2; mulss 100, mulss the cvar; comiss, jb skips): **`FX_RicochetSound.Ricochet`** at the impact, volume 1.0, pitch 100.
- +0xc4 is the .vsurf's `audioparams.occlusionFactor`: 1.0 on 111 of the 164 stock surfaces (30 %); 0.0 on 22 (never); 0.8 on 24; 0.2, 0.7 x 2, 1.025 .. 1.1 on the rest. RandomFloat is tier0's unseeded one.

## Vdata sound slots and items_game keys nobody reads

- m_aShootSounds find callers (only): zoom (server 1809c05c0 / 1809c0660; client 1807cf6c0 / 1807cf760), decoy's shot (1809c0760: the thrower's gun's slot 2 or 9), StartGrenadeThrow (1809d3cd0 at 1809d401c, client 1807dfaa0: slot 2), ThrowGrenade (1809d4a50: slot 0x17), client 180d26730 (both callers in FX_FireBullets), KV3 parse (180c9e320 / 180c9e5b0).
- items_game `visuals` keys `sound_single_shot` / `sound_nearlyempty` / ...: parsed into visuals +0xf8 + slot x 8 and **read by nothing** (no `[reg + index x 8 + 0xf8]` load in either DLL but the two stores). So:
  - `Flashbang.Throw`, `HEGrenade.Throw`, `IncGrenade.Throw` never play: the grenades' vdata has no SINGLE (only RADIO_USE and NEARLYEMPTY). The throw heard is the viewmodel clip's Weapon_*.Throw / *.Throw event.
  - `c4.plant` (weapon_c4's SINGLE) never plays: slot 2 is read only for a grenade's throw, a decoy's gun and a bullet shot (plant sounds: c4.initiate / c4.plantquiet, c4.md).

## Drowning (water services slot 0x60, 180b25450)

1. m_nActualMoveType 7 (noclip) without a move parent: the reset, done.
2. m_iHealth (180cf7020) >= 0 and alive (vfn 0x550), else nothing.
3. **m_flWaterLevel != 1.0** (or slot 0xc0): m_AirFinishedTime != 0 and < now -> **Player.DrownStart** from the pawn; the reset.
4. Fully under: m_AirFinishedTime 0 -> now + 12.0f; then when < now, no FL_GODMODE and m_NextDrownDamageTime < now: damage = rate + 1 (at most 5), CTakeDamageInfo (the world as inflictor and attacker, DMG_DROWN), TakeDamageOld, m_NextDrownDamageTime = now + 1.0f.
- Runs once per command from PreThink, before movement. 12 s of air, then 3, 4, 5, 5 ... a second apart (65 ticks: the compares are strict); the gasp on surfacing after the air ran out.
- The constructor leaves the rate; respawn (180249530) doesn't reset the services (the state stays with the pawn).

## Fall damage (CheckFalling 180abb840)

1. Out of water, after a moving-down ground's speed is taken off (svc +0x25c), floored at 0.1: above 580 (`!(580 > f) && f > 580`) -> 180adc190(mv) (return ignored), then the impact punch 1.0.
2. 180adc190: the pawn (mv +4's handle) a player and alive; `damage = sv_falldamage_scale x ((svc+0x25c - 580) x 0.23809524f)` (order from 180adc268); > 0: CTakeDamageInfo (world, world, damage, DMG_FALL), TakeDamageOld, then 18020a500: **Player.DamageFall.Fem** with m_bHasFemaleVoice else **Player.DamageFall**, from the pawn, whether or not it killed.
3. A death fades the screen (180feb800: black, hold 10000, flags 10) only when CCSGameRules vfn 0x200 is true (1809236a0: false). The client names neither sound.

## Female voice

- 1801ff590: m_strVOPrefix from the agent item's definition (CUtlString::Set), then `m_bHasFemaleVoice = V_stristr_fast(prefix, "_fem") || IsEqual_CaseSensitive("fbihrt_epic") || IsEqual_CaseSensitive("swat_epic")`.
- items_game vo_prefix values: balkan_epic, ctm_gsg9, fbihrt_epic, gendarmerie_fem_epic, gendarmerie_male, jungle_fem, jungle_fem_epic, jungle_male, jungle_male_epic, leet_epic, professional_epic, professional_fem, seal_diver_01..03, seal_epic, seal_fem, swat_epic, swat_fem; base agents (tm_phoenix, ctm_sas) none.
- Readers: the death (180ac165a: Player.DeathFem / Player.DeathTaser_F), the fall (18020a500), the jump throw (1809c8542, 1809d3f4d: BaseGrenade.JumpThrowF / M).

## Jump throw grunt

- Both setters of m_bJumpThrow play it: StartGrenadeThrow at 1809d3efc whenever the release is inside the jump window (0.1), already set or not; ItemPostFrame (1809c8320) at 1809c8522 when it wasn't set.
- CRecipientFilter (+0x10 -1, +0x14 0xff, skip-predicting off), AddAllPlayers, no prediction rule (180c8c8d0 not called), the grenade's entity index, EmitSound of **BaseGrenade.JumpThrowF** with the owner's m_bHasFemaleVoice else **BaseGrenade.JumpThrowM**. The client names neither: everyone hears the server's, the thrower too.

## Named but never played

- **BaseEntity.EnterWater / ExitWater**: PhysicsCheckWaterTransition from PhysicsToss / PhysicsCustom only (grenades) and CBaseGrenade's bounce touch: all read the water type, which a grenade never gets (SetWaterType only from the player's CheckWater and the VPHYSICS fluid touch, which plays nothing).
- **Underwater.BulletImpact**: FX_TracerSound's type 0x10, which no caller passes (tracer-sound.md).
- **Bounce.Glass / Metal / Flesh / Wood / Shrapnel / Shell / Concrete / ShotgunShell** (+ 0x400 / 0x800 forms): 180c30510 by +0x1284; nothing writes it (the six stores are other classes' network setters); neither DLL has BreakModel / EjectBrass temp entities. CS2's shells are particles.
- **BaseCombatCharacter.AmmoPickup**: GiveAmmo (m_iAmmo[type] + count up to the max, sound from the pawn unless told not to); the event's volume is 0.0 (game_sounds_player): silent.
- **Player.DenyWeaponSelection**: SelectWeapon when CanBeSelected fails; only a spent grenade still held fails vfn 0x9e0. Every caller pre-filters (1015 build, vtable 0x181d21320): SelectSlot (from the slot keys and the per-grenade binds 0x288.. -> 0x2d8 with the slot) takes GetNextActivePos (only weapons with vfn 0x9e0 and CanBeSelected; hud_fastswitch 2: 0x9e0 alone, default not 2); next / prev and 0x2f0 / 0x2f8 / 0x300 test CanBeSelected first. The deny needs a candidate past 0x9e0 with no owner under hud_fastswitch 2 (a transient network state). SelectSlot plays Player.WeaponSelectionFoley when the pick isn't the active weapon.
- **Player.Surf.***: 1808de830, gated by sv_surf_sounds and surf_speed_slow / med / fast: off unless a server sets it.
- **Glass.Strain**: CBrokenGlassTrap (the cash stack model) -> 1808c0d90: a player within 30 u looking down past 34 degrees (or the trap moving): the sound from the player, the molotov_broken_glass particle, the trap removed.
- **DogTags.Pickup / PickupDeny** (CItemDogtags, cash stack touch), **ItemSoda.Bounce**, **Metal.SawbladeStick**, **SprayCan.Shake / Paint** (graffiti): entities and modes outside these games.

## Ragdolls' and client bodies' impact sounds (client)

1. 1803ae000 calls 1803ce260 for both bodies (index 0, 1) of a collision event (flag bit 0) unless its +0x77 byte is set.
2. speed = **|(vz nz + vy ny) + vx nx|** (event +0x38.. vectors; no mass or speed scale); nothing unless **speed > 70.0** (the server has no floor).
3. Event +0xf8 must hold a list with a non-zero count; the body (event +8) dynamic (vfn 0x20 == 2); its entity (vfn 0x478) must exist (death ragdolls are client entities); surface (event +0x20 + index x 4) non-zero.
4. volume = **min(1, speed^2 x 9.765625e-06)**; queue 1803a3bc0(system, the other entity, 0, the body (event +8 + index x 8), surface, other surface (+0x24 / +0x20), volume, speed, contact point event +0x28).
- So ragdolls play their surface's impacts (flesh: Flesh.ImpactHard / ImpactSoft) above 70 u/s.

## Physics impact sounds (server)

- Data: a weapon's world model shapes carry a surface (`WeaponRifle`, `WeaponPistol`, `WeaponSMG`, `WeaponSniper`, `WeaponShotgun`, `WeaponHeavy`, `WeaponKnife`, `WeaponC4`, the grenades'), whose impactHard / impactSoft events are `weapon.Rifle.Impact` ... (game_sounds_physics.vsndevts: csgo_mega, mixgroup Physics, `volume 1.5`, block_duration 0.2, block_distance 25, block_match_entity, instance_limit 3, child `weapon.Rifle.Impact.Rattles`, `use_impact_speed_input_volume_mapping_curve` with `impact_speed_input_volume_mapping_curve` (0 -> 0.114, 203.1 -> 0.305, 408.6 -> 1.0)).
- **Dispatcher 180582670**: the world's events (world vfn 0x3d0; 0x100 bytes: +0 flags, +8 / +0x10 bodies, +0x18 / +0x1c entity handles, +0x20 / +0x24 surface indices). Flag 1 collision, 4 start touch, 8 / 0x10 others. A collision builds the game's event (+0 / +8 bodies, +0x10 / +0x14 surfaces, **+0x18 = 10.0**, **+0x1c speed**, +0xd8 / +0xe0 entities) and calls each entity's VPhysicsCollision (vfn 0x278). Speed (180582b90..180582bf1): `|((Vy Ny + Vz Nz) + Vx Nx)| x ((tsA + 0 + tsB) x 0.5)`, V and N from 180593af0, ts each body's vfn 0x430.
- **vfn 0x278 (180d1a340)**: vfn 0x280, then clears flag 0x40 of +0x414 (m_fFlags-like) on an entity slower than 1 u/s.
- **vfn 0x280 (180d1a420)** (every weapon class and CBaseEntity: vslot of CAK47 1818f1b98, CCSWeaponBase 1818ec818, CKnife 1819154a0, CHEGrenade 181914520): needs the other entity, either one's m_MoveType == 5 (VPHYSICS), and (event +0x18 >= 0.5 or the other isn't itself). Both surfaces' game material must differ from 181e27f58. Then `1805a9c70(system 181ff5690, entity, body, other body, surface, other surface, speed, 1.0)`, then 180e8df50 / 180e8dde0.
- **180cbd840** (CWorld's vfn 0x278): an entity hit by a dynamic body (the other's vfn 0x20 == 2) whose own surface has +0xc0 > 0: the same call with that as the scale.
- **1805a9c70**: `volume = min(1, speed x speed x 9.765625e-06 x scale)`, then `180575ab0(system, entity, entity index, body, other body, surface, other surface, volume, speed, 0)` and the listeners.
- **Queue 180575ab0** (entries: +0 entity handle, +4 entity index, +8 volume, +0xc speed, +0x10 other body's mass (vfn 0x128 when its vfn 0x20 == 2, else 500.0), +0x14 surface, +0x18 other surface, +0x1c position): `speed += 0.0001`; an entry with the same surface, or any entry once more than 4 are queued, absorbs the new one (lower volume: takes the new position, entity and other surface; mass = max; volume += new; speed = max); else a new entry. Position: the argument, else the body's (vfn 400), else the entity's origin.
- **Flush 1805ad380**: frame time summed at +0xd8; **past 0.05 s** every entry plays, last first: surface = props (`1823ab5c0` vfn 0xb8, Get vfn 8); nothing without a hard sound (+0x50). `under = hardVelocityThreshold (+0xbc) > 0 && speed < it`. No soft sound: skipped when sv_phys_sound_disable_impact_sounds_under_hard_threshold and `under`, else hard. With a soft sound: soft when the other surface's hardness (+0xac) < this surface's hard threshold (+0xb8), or `under`; else hard. Played by 1805aa5b0. Then the break queue: each surface's +0x78 sound at volume 1.0 (1805aaaf0).
- **1805aa5b0**: starts the event (1805c4680) for a filter at the position (180c84870 thunk), then parameters by hash: 0x5a7cce4d position (12 bytes), 0x2d8464af volume (+8), 0x41a38e55 speed (+0xc: what the impact_speed curve reads; inferred), 0x4c2cbe7f the other surface's hardness, one more from +0x10. Names behind the hashes not found.
- surfaceproperties.vsurf (164): audioparams audioreflectivity, audiohardnessfactor (0, 0.2, 0.25, 0.5 or 1.0; 138 are 1.0), audioroughnessfactor, scrapeRoughThreshold, **impactHardThreshold 0.5 on every one**, occlusionFactor; none has a hard-velocity threshold or static impact volume or a game material. So with stock data the world's own side never plays, `under` is never true, and hard / soft is "soft against hardness < 0.5".
- csgo_mega's stack: one impact input, `public.impact_speed_input`, into a math_curve_2d (`impact_speed_input_volume_mapping_curve`, when `use_impact_speed_input_volume_mapping_curve`) multiplied into the volume chain (`impact_speed_input_volume_mapping_curve_mult`).

## vphysics2 collision events (vphysics2_20260924)

- **When**: the collide post-pass's Began list and the TOI flush's: a contact that starts touching with flags (+0x74) bit 2 goes to 1801fe920(tracker, contact, flag). Set at creation when the pair's flags (+0x78) keep any of 0x1c, which 1802faf00 leaves only when both shapes' function masks have 4 and their entity ids differ (and the group table's entry has them: 0x15 / 0x14 for nearly every pair).
- **1801fe920**: the body pair's entry (keyed by the two body ids; +8 counts its touching contacts). New pair: a record in the first list (tracker +0). Existing: in the second list (tracker +0x18) only when the contact is solid (+0x78 bit 0). Flags 8 pairs join the persist list. Then contact +0x74 |= 4 (its end reaches 1801feca0).
- **Record 1801fa810** (0x70): both bodies' frames (+0 / +0x20 origin and scale, +0x10 / +0x30 orientation), +0x40 the contact, +0x48 its manifold cache (ref counted); with a manifold, its first one's friction anchor (manifold +4 -> record +0x50) and normal (+0x10 -> +0x5c); without, the two origins' midpoint and direction.
- **World vfn 0x3d0 (180059170)**: first list -> flags `(solid) | 4`; second list -> 1; persist -> 8; ended pairs 0x10. Every solid contact that starts touching is one collision event.
- **Event 180058a90** (0x100): +8 / +0x10 body wrappers, +0x18 / +0x1c entity handles (bodies' first dword), +0x20 / +0x24 surfaces (18000b970 record +0x24: a hull's own; a mesh triangle's via the per-triangle material bytes, the triangle from the first manifold point's sub shape), +0x28 point, +0x34 normal, +0x80 / +0x8c linear and +0x98 / +0xa4 angular velocities **the frame started with** (body +0x220 / +0x22c) when the frame origin is set (+0x1f8 != FLT_MAX), else the current (+0x108 / +0x114); +0xb0.. the current ones again.
- **Adaptor 180593af0**: with a manifold, `V = (vA + wA x (P - cA)) - (vB + wB x (P - cB))`, c = body +0xfc; order `Vx = ((rAz wAy - rAy wAz) + vAx) - ((wBy rBz - wBz rBy) + vBx)`, and so on round the axes. vfn 0x430 = body +0x9c, the time scale.

## Unread

- Who is in earshot (180c861f0); 180590da0's value; the 0xdd82057c parameter's name and use; the eye line's mask.
- Class 18212afd8 (taken as CCSPlayerPawn).
- Player.PickupWeapon's emitters (180a6ee50, 180a6f6f0, 180ac8330, 180aea0a0); 18023a540.
- m_pfnTouch for a CItem (the MyTouch caller: 15 call sites of slot 0x9a8, none read); 180571ca0.
- Who calls FX_FireBullets for a gun it doesn't own (the others' clip); 180d26730's emit (who hears it).
- 18122ed70's dispatcher.
- Drowning: a player's move parent; the rate before the first reset.
- The client impact queue / flush (1803a3bc0); a ragdoll part's surface; the event +0xf8 list.
- sv_surf_sounds on GFL.
- The impact parameter hash names; whether the 0x2d8464af volume reaches the event's volume.
- vphysics2: the triangle read when the mesh is the first shape; not checked natively.
