# player_death: the server's fields, the assist, the client's death notice

server_20261105, client_20261015 (Ghidra). huddeathnotice.vxml / .vcss. CS2Fixes customio.cpp (IgnitePawn).

## Functions

| Address | Module | What |
|---|---|---|
| 18091da70 | server | CCSGameRules' death notice (from 180912130) |
| 180de8600 | server | (rules, attacker handle, inflictor): the killer |
| 1809284a0 | server | (rules, victim, killer, pass): the damage assister |
| 180913af0 | server | (rules, victim, killer): the flash assister |
| 180931650 | server | (rules, a, victim): relationship: -1 same team (unless squads), 1 else, 0 no victim |
| 180931910 | server | (other callers unread) |
| 180ac5e00 | server | team number |
| 180ad2a20 | server | squads override |
| 180b0b500 | server | (controller +0x7f8 action tracking, 1): m_iAssists |
| 1801fc0c0 | server | (pawn, contributionscore_*): score |
| 180e8bed0 | server | noreplay test (fails: noreplay) |
| 180b08a20 | server | priority term |
| 180b07a70 | server | damage records of the +0x800 services |
| 180b0a510 / 180b0a4b0 | server | record's recipient / damager |
| 18017e2d0 | server | f32 compare (-1: curtime < blind until) |
| 1803a7410 | server | RadiusFlash (sets the flasher handle; [flashbang.md](flashbang.md)) |
| 1802106c0 | server | a pawn's flashed amount |
| 180ac8b40 | server | flash alpha (start, curtime, duration, in-ramp, maxAlpha, &alpha, &shot) |
| 180ac8cb0 | server | returns 0.094444446 |
| 1801fef80 | server | Blind ([flashbang.md](flashbang.md)) |
| 18091cf40 | server | the fields every death event shares (also player_hurt's) |
| 181ebdc58 | server | projectile dynamic-cast type |
| 180c868d0 | server | active weapon of the weapon services |
| 1803d95f0 | server | movetype (2 walk) |
| 181029810 | server | inflictor projectile's item |
| 180a94520 | server | the pawn's damage post (record, thrusmoke, dominations) |
| 180cf7020 | server | lethal test term |
| 1809165e0 | server | shot went through smoke |
| 180211b00 | server | (attacker, eye, point): IsLineBlockedBySmoke density via 1809bfc60 |
| 180b1dbe0 | server | record (controller +0x800, attacker, victim, damage, health, killType, flags) |
| 180b00ba0 | server | record add |
| 1801c0e00 | server | dominate / revenge bits |
| 1801d79b0 | server | domination counts (from 1801c5be0) |
| 18093e020 | server | game_type == 1 (deathmatch / arms race) |
| 180a88120 | server | killer controls a taken-over bot |
| 180a9b840 | server | (a, b, new): a dominates b |
| 180a88460 | server | (victim, killer slot): victim dominates killer |
| 1801d4ba0 | server | player leaving: zeroes both sides' counts |
| 180957e50 | server | RestartRound: 180a9a2e0 with dl = 1 -> 180b20ca0 clears the records |
| 180e885f0 | client | CCSGO_HudDeathNotice's player_death |
| 18089c930 | client | killer dominates victim |

## Fields

| Offset | Field |
|---|---|
| info +0x38 / +0x3c / +0x40 | inflictor / attacker handle / weapon |
| info +0x48 | flags bit 4: lethal |
| info +0x4c | flags (bit 19 headshot; 0x80000 priority) |
| info +0x28 | damage position |
| info +0x7c | penetrated (solids passed; [shots.md](shots.md) 6b) |
| controller +0x7f8 | action tracking |
| controller +0x800 | damage services (records) |
| controller +0x6f4 | 3 or 4: disconnecting (client) |
| pawn +0xa44 | noreplay |
| pawn +0x1530 | bits: 1 dominated, 2 revenge, 4 wipe, 8 thrusmoke |
| pawn +0xd38 / +0xd3c | m_blindUntilTime / m_blindStartTime |
| pawn +0xe04 / +0xe08 | m_flFlashDuration / m_flFlashMaxAlpha |
| pawn +0xe48 -> +0x220 | the flasher handle |
| pawn +0x344 | team |
| pawn +0xb10 | weapon services |
| pawn +0xe60 -> +0x48 / +0x4c | damage services: dmg_health / dmg_armor |
| item def +0x260 (from +0xb0e) | econ item name |
| weapon vdata +0x728 | == 1: silenced weapon |
| result +0x20 / +0x18 | m_flDamageDealt / m_nHealthLost |
| stats object (DAT_181f57c70) +0x9c + victim slot x 0x1128 + 0x1028 + killer slot x 4 | victim's unanswered deaths to the killer |
| stats row +0xf28 / +0x1028 / +0xe28 | killed-by / unanswered / kills of [slot] |

CDamageRecord (schema):

| Offset | Field |
|---|---|
| +0x30 | m_PlayerDamager |
| +0x38 | m_hPlayerControllerDamager |
| +0x50 | m_DamagerXuid |
| +0x58 | m_RecipientXuid |
| +0x60 | m_flBulletsDamage |
| +0x64 | m_flDamage |
| +0x68 | m_flActualHealthRemoved |
| +0x6c | m_iNumHits |
| +0x70 | m_iLastBulletUpdate |
| +0x74 | m_bIsOtherEnemy |
| +0x75 | m_killType |

## Constants

| Value | What |
|---|---|
| cs_AssistDamageThreshold | int, default 25, object 0x1821196c0, registered 180099d80; read as (float) of the int |
| sv_flashed_amount_for_blind_kill | float 0.7, registered 1800a6570, handle 182118fd8 |
| mp_teammates_are_enemies | bool 18211a6d8 |
| sv_nonemesis | bool, object 181f57c38, default 0 |
| contributionscore_assist | int, default 1 |
| contributionscore_assist_reqs | int, default 0 |
| contributionscore_kill | 2 |
| mp_display_kill_assists | replicated bool, 1 |
| 0.3 | flash-assist flashed amount |
| 0.094444446 (0x1819269e0) | flash ramp |
| 255 (0x181784e18) | flashed amount divisor |
| 0.0254 | units to metres (distance) |
| 7 | base priority |
| 0x902 | damage types giving bl = 2 (bullets) |
| 1818c95a4 | string `NPC_` |

## The death notice (18091da70)

1. Killer = 180de8600(rules, +0x3c, +0x38) when it's a living player pawn.
2. Assister: `1809284a0(rules, victim, killer, 2)`, else `1809284a0(..., 0)`, else the flash assister `180913af0(rules, victim, killer)`.
3. Found by damage and `180931650(rules, assister, victim) >= 1`: counts: 180b0b500(+0x7f8, 1) and, unless game_type 1 or
   (flag & 1 and the bullet pass failed), 1801fc0c0(pawn, contributionscore_assist). A damage assister on the victim's
   team is still sent, uncounted. assistedflash = the flash path found one.
4. noreplay when +0xa44 or 180e8bed0 fails; `priority = 7 + (killer and info flags & 0x80000) + 180b08a20(...)`.
5. dominated (+0x1530 bit 1) / revenge (bit 2), wipe (bit 4); distance (m) when killer != victim: `|killer eye - victim eye| * 0.0254`.

## The damage assister (1809284a0)

- Over the victim controller's records (180b07a70 on +0x800): counts when recipient (180b0a510) is the victim and
  damager (180b0a4b0) is someone else and not the killer.
- Value: m_flDamage (+0x64); pass 2: a record with m_flBulletsDamage (+0x60) <= 0 counts 0.
- Largest wins (strict `<`: the first of equal ones), must be above cs_AssistDamageThreshold.

## The flash assister (180913af0)

- Victim still blind: curtime < +0xd38 (18017e2d0 returns -1).
- Flasher: +0xe48 -> +0x220 handle, not the victim or killer, and (mp_teammates_are_enemies or another team (+0x344)
  or the victim's flashed amount (1802106c0) >= 0.3), then 180931650 >= 1.

## Shared fields (18091cf40)

- weapon: inflictor (+0x38) when it isn't the attacker pawn: its class name, or for a projectile (181ebdc58) its econ
  item's name; the attacker itself: the info's weapon (+0x40) or its active weapon (+0xb10 -> 180c868d0). Prefix off:
  `weapon_` (case-insensitive), else `NPC_`, else `func_`. World kill: "world".
- headshot: +0x4c bit 19 when the attacker is the killer.
- Silenced weapon (vdata +0x728 == 1) whose IsSilenced (vfn 0xd90) is false and name ends "silencer": `<name>_off`
  (usp_silencer_off, m4a1_silencer_off).
- penetrated = +0x7c.
- noscope: info's weapon is WEAPONTYPE_SNIPER_RIFLE (vfn 0xc60 == 5) and not zoomed (vfn 0xc90).
- thrusmoke: victim +0x1530 bit 8.
- attackerblind: attacker's flashed amount >= sv_flashed_amount_for_blind_kill.
- attackerinair: attacker != victim, no ground entity (vfn 0x668), movetype walk (1803d95f0 == 2), weapon type 0-6 or 8
  (knife, pistol, SMG, rifle, shotgun, sniper, machine gun, taser; not C4 7 or grenades).
- hitgroup (0 for DMG flags bit 6), dmg_health / dmg_armor (+0xe60 -> +0x48 / +0x4c).
- weapon_itemid / fauxitemid: the inflictor projectile's item (181029810) or the killer's weapon's.
- CS2Fixes IgnitePawn (CTakeDamageInfo(inflictor = attacker's pawn, attacker, ability null, DMG_FALL)): names the
  attacker's active weapon (180c868d0) and its item; no noscope / in-air (they read the null ability).

## Damage post (180a94520)

1. lethal = info damage >= 1 and not 180cf7020, or +0x48 bit 4.
2. Lethal: victim +0x1530 = 1801c0e00's dominate / revenge bits | 8 when 1809165e0: weapon type 1..6 (pistol .. machine
   gun) and 180211b00(attacker, weapon services' vfn 0xc8 (eye now), +0x28) density >= 1.
3. 180b1dbe0 on the attacker controller (+0x800), and on the victim's when they differ.
4. 180b00ba0: +0x60 += damage when flags & 2 (bl = 2 for info damage type & 0x902); +0x64 += damage; +0x68 += health;
   +0x6c += 1 unless the same +0x70; +0x75 = killType.
   `damage = (float)(int) result +0x20` (cvttss2si), `health = (float) result +0x18`.

## Flashed amount (1802106c0)

- 180ac8b40(+0xd3c, curtime, +0xe04, curtime - start < 0.094444446, +0xe08, &alpha, &shot); returns alpha.
- Both 0 unless start + duration >= now.
- Ramp: both = `clamp(elapsed / 0.0944 * maxAlpha, 0, maxAlpha)`.
- After: `shot = clamp(left * maxAlpha / duration)`, `alpha = (left <= 3 ? (left / 3)^2 : 1) * maxAlpha` clamped; both / 255.

## Dominations and revenge (1801c0e00 / 1801d79b0)

- Only when 18093e020 and sv_nonemesis off, killer and victim different players.
- On the lethal hit (180a94520 line 81, before the counts move): count = stats object cell (Fields). count == 3: victim
  flag 1 (dominated); unless the killer controls a taken-over bot (180a88120): 180a9b840(killer, victim, 1) and
  dominations / nemesis stats. Else if 180a88460(victim, killer slot): flag 2 (revenge) and, unless a takeover,
  180a9b840(victim, killer, 0).
- 1801d79b0: victim's row +0xf28 / +0x1028 [killer slot] + 1; killer's row +0xe28 [victim slot] + 1 and +0x1028 [victim
  slot] = 0 (each side skipped for a taken-over bot).
- Assist score: 1801fc0c0(assister, contributionscore_assist) unless game_type 1, or contributionscore_assist_reqs bit 0
  with no bullet assister.

## Client (180e885f0)

- No weapon string: nothing. Assister read only with mp_display_kill_assists and not the attacker.
- Suicide (attacker -1 or the victim, not trueview): DeathNoticeSuicide.
- DeathNotice_Victim: you died; DeathNotice_Killer: not your death and you are attacker or assister.
- Weapon prefix `weapon_` / `item_` off; knife_default_ct -> knife, knife_default_t -> knife_t, galil -> galilar,
  molotov_projectile_impact -> inferno; dangerzone_controller / env_gunfire / planted_c4 drop the suicide look;
  disconnecting victim (+0x6f4 3 or 4): "disconnect".
- Classes: noscope, through-smoke, attacker-blind, attackerinair (the event's bools), DeathNotice_Victim / _Killer,
  DeathNoticeWipe / Revenge / Domination, DeathNoticePenetrate (penetrated > 0), DeathNoticeHeadShot,
  DeathNoticeFlashbang (assistedflash), DeathNoticeSuicide, DeathNoticeAssist (assister != -1), TrueViewDeadOnServer;
  SpawnTime / Lifetime / LifetimeMod (x1.5 for a notice about you).
- DeathNoticeDomination for dominated or killer dominates victim (18089c930), else DeathNoticeRevenge for revenge.
- Icon `file://{images}/icons/equipment/<weapon>.svg`. Names: GetDecoratedPlayerName2 flags 0x16 + clan ([teamid.md](teamid.md));
  colour classes DeathNoticeCTColor (team 3) / DeathNoticeTColor (2).
- huddeathnotice.vxml order: Revenge, Domination, AttackerBlindIcon, Attacker, AssistParent ("+", Flashbang
  (flashbang_assist.svg), Assister), AttackerInAir, Weapon, NoScopeIcon, ThroughSmokeIcon, Penetrate, HeadShot, Suicide,
  Victim; the .vcss shows each by its class (#AttackerInAir margin-right -4px, margin-top -14px).

## Unread

180931910's other callers; the stats object's other counters.
