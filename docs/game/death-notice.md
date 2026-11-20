# player_death: the server's fields, the assist, the client's death notice

server_20261105.dll unless marked client (client_20261015.dll in the Ghidra project). Ported in
web/server/cs2web/combat/kill-notice.js (server) and web/src/ui/killfeed.js + web/src/cs2web/client/core/game.js killfeed (client).

## Server

### 18091da70: CCSGameRules' death notice (called from 180912130)
- The killer = 180de8600(rules, info's attacker handle +0x3c, inflictor +0x38) when it's a living player pawn.
- **The assister**: `1809284a0(rules, victim, killer, 2)`, else `1809284a0(..., 0)`, else (when none) the flash
  assister `180913af0(rules, victim, killer)`.
  - Found by damage and `180931650(rules, assister, victim) >= 1` (not the victim's team): the assist counts:
    180b0b500(controller +0x7f8 action tracking, 1) (m_iAssists) and, unless game_type 1 or (flag & 1 and the bullet
    pass failed), 1801fc0c0(pawn, contributionscore_assist) (not ported). A damage assister on the victim's team is
    still sent as the assister, uncounted.
  - assistedflash = the flash path found one.
- noreplay when +0xa44 or 180e8bed0 fails; priority = 7 + (killer and info flags & 0x80000) + 180b08a20(...).
- dominated (victim pawn +0x1530 bit 1) / revenge (bit 2), wipe (bit 4); distance (m) when the killer isn't the victim:
  |killer eye - victim eye| x 0.0254.

### 1809284a0: the damage assister
- Walks the victim's controller's damage records (180b07a70 on the controller's +0x800 services); a record counts when
  its recipient (180b0a510) is the victim and its damager (180b0a4b0) is someone else and not the killer.
- Value: m_flDamage (record +0x64); in pass 2 a record with m_flBulletsDamage (+0x60) <= 0 counts as 0.
- The largest wins (strict `<`: the first of equal ones), and must be above **cs_AssistDamageThreshold** (int, default
  **25**, object 0x1821196c0 registered at 180099d80; read as (float) of the int).

### 180913af0: the flash assister
- The victim still blind: curtime < m_blindUntilTime (pawn +0xd38) (18017e2d0 returns -1).
- The flasher: the victim pawn's +0xe48 services' +0x220 handle (set by RadiusFlash 1803a7410 for each pawn it blinds; the flashbang session's docs/game/flashbang.md), not the victim or the
  killer, and (mp_teammates_are_enemies (bool 18211a6d8) or another team (+0x344) or the victim's flashed amount
  1802106c0 >= 0.3), then 180931650 >= 1.

### 180931650: the relationship
- -1 for two pawns on one team (180ac5e00 team number), unless 180ad2a20 (squads) says otherwise; else 1; 0 without a
  victim.

### 18091cf40: the fields every death event shares (also player_hurt's)
- weapon: the inflictor (info +0x38) when it isn't the attacker pawn: its class name, or for a projectile (dynamic cast
  181ebdc58) its econ item's name (+0x260 of the item def from +0xb0e); the attacker itself: the info's weapon (+0x40)
  or its active weapon (pawn +0xb10 services -> 180c868d0). Prefix off: `weapon_` (case-insensitive), else `NPC_`
  (string 1818c95a4), else `func_`. A map's world kill: "world".
- headshot: info flags (+0x4c) bit 19 when the attacker is the killer.
- A silenced weapon (vdata +0x728 == 1) whose IsSilenced (vfn 0xd90) is false and whose name ends "silencer":
  weapon = "<name>_off" (usp_silencer_off, m4a1_silencer_off).
- **penetrated** = info +0x7c: the count of solids the bullet passed (shots.md 6b).
- **noscope**: the info's weapon is WEAPONTYPE_SNIPER_RIFLE (vfn 0xc60 == 5) and not zoomed (vfn 0xc90).
- **thrusmoke**: the victim pawn's +0x1530 bit 8 (set below).
- **attackerblind**: the attacker's flashed amount 1802106c0 >= **sv_flashed_amount_for_blind_kill** (float 0.7,
  registered at 1800a6570, handle 182118fd8).
- **attackerinair**: attacker != victim, no ground entity (vfn 0x668), movetype walk (1803d95f0 == 2), the info's
  weapon type in 0-6 or 8 (knife, pistol, SMG, rifle, shotgun, sniper, machine gun, taser; not C4 7 or grenades).
- hitgroup (0 for DMG flags bit 6), dmg_health / dmg_armor from the victim's damage services (+0xe60 -> +0x48 / +0x4c).

### 180a94520: the pawn's damage post (the record, thrusmoke)
- lethal = this hit kills (info damage >= 1 and not 180cf7020, or info flags bit 4 of +0x48).
- On a lethal hit: the victim's +0x1530 = 1801c0e00's dominate / revenge bits | 8 when **1809165e0** says the shot went
  through smoke: the info's weapon type 1..6 (pistol .. machine gun) and 180211b00(attacker, the weapon services'
  vfn 0xc8 (the eye now), the damage position info +0x28) = 1809bfc60 (IsLineBlockedBySmoke's density) >= 1.
- The record: 180b1dbe0(attacker controller +0x800, attacker, victim, damage, health, killType, flags) and the same on
  the victim's controller when they differ; 180b00ba0 adds: m_flBulletsDamage (+0x60) += damage when flags & 2
  (bl = 2 for info damage type & 0x902), m_flDamage (+0x64) += damage, m_flActualHealthRemoved (+0x68) += health,
  m_iNumHits (+0x6c) += 1 unless the same m_iLastBulletUpdate (+0x70), m_killType (+0x75).
  damage = (float)(int) result +0x20 (m_flDamageDealt, cvttss2si), health = (float) result +0x18 (m_nHealthLost).
- CDamageRecord fields (schema): m_PlayerDamager +0x30, m_hPlayerControllerDamager +0x38, m_DamagerXuid +0x50,
  m_RecipientXuid +0x58, m_flBulletsDamage +0x60, m_flDamage +0x64, m_flActualHealthRemoved +0x68, m_iNumHits +0x6c,
  m_iLastBulletUpdate +0x70, m_bIsOtherEnemy +0x74, m_killType +0x75.

### 1802106c0: a pawn's flashed amount (attackerblind, the flash assist's 0.3)
- 180ac8b40(m_blindStartTime +0xd3c, curtime, m_flFlashDuration +0xe04, curtime - start < 0.094444446 (0x1819269e0,
  also 180ac8cb0's return), m_flFlashMaxAlpha +0xe08, &alpha, &shot); returns alpha. Both 0 unless start + duration
  >= now. In the ramp both = clamp(elapsed / 0.0944 x maxAlpha, 0, maxAlpha); after it shot = clamp(left x maxAlpha /
  duration), alpha = (left <= 3 ? (left / 3)^2 : 1) x maxAlpha clamped; both / 255 (0x181784e18). kill-notice.js
  flashedAmount. (Blind itself, 1801fef80, and RadiusFlash are the flashbang session's.)

### 1801c0e00 / 1801d79b0: dominations (nemesis) and revenge (ported, deathmatch)
- Only when 18093e020 (game_type == 1: deathmatch / arms race) and sv_nonemesis (bool, object 181f57c38, default 0)
  is off, and the killer and victim are different players.
- On the lethal hit (180a94520 line 81, before the counts move): count = the stats object (DAT_181f57c70) +0x9c +
  victim slot x 0x1128 + 0x1028 + killer slot x 4 (the victim's unanswered deaths to the killer). count == 3: victim
  flag 1 (dominated); unless the killer controls a taken-over bot (180a88120): the killer dominates the victim
  (180a9b840(killer, victim, 1)) and dominations / nemesis stats. Else if the victim dominates the killer
  (180a88460(victim, killer slot)): flag 2 (revenge) and, unless a takeover, 180a9b840(victim, killer, 0).
- 1801d79b0 (from 1801c5be0, after): the victim's row +0xf28 / +0x1028 [killer slot] + 1 (killed-by, unanswered); the
  killer's row +0xe28 [victim slot] + 1 and +0x1028 [victim slot] = 0 (each side skipped for a taken-over bot).
- 1801d4ba0 (a player leaving) zeroes both sides' counts.
- The client (180e885f0) shows DeathNoticeDomination for dominated or when the killer dominates the victim
  (18089c930), else DeathNoticeRevenge for revenge.

### More traced
- The damage records are cleared by RestartRound (180957e50 calls 180a9a2e0 with dl = 1 -> 180b20ca0 on the
  controller's +0x800 services).
- The assist's score: 1801fc0c0(assister, contributionscore_assist (int, default 1)) unless game_type 1, or
  contributionscore_assist_reqs (int, default 0) bit 0 with no bullet assister; contributionscore_kill is 2.
- ZR's napalm (CS2Fixes IgnitePawn, customio.cpp: CTakeDamageInfo(inflictor = the attacker's pawn, attacker, ability
  null, DMG_FALL)): with the attacker as the inflictor 18091cf40 names the attacker's active weapon (180c868d0) and its
  item; no noscope / in-air (they read the null ability).
- weapon_itemid / fauxitemid: the inflictor projectile's item (181029810) or the killer's weapon's.

### Still unread
- 180931910's other callers; the stats object's other counters.

## Client: 180e885f0, CCSGO_HudDeathNotice's player_death (client_20261015)
- No weapon string: nothing. The assister is read only when mp_display_kill_assists (replicated bool, 1) and isn't the
  attacker.
- Suicide (attacker -1 or the victim, not trueview): DeathNoticeSuicide.
- DeathNotice_Victim: you died; DeathNotice_Killer: not your death and you are the attacker or the assister.
- Weapon prefix `weapon_` / `item_` off; knife_default_ct -> knife, knife_default_t -> knife_t, galil -> galilar,
  molotov_projectile_impact -> inferno; dangerzone_controller / env_gunfire / planted_c4 drop the suicide look;
  a disconnecting victim (+0x6f4 3 or 4): "disconnect".
- Classes toggled on the notice: noscope, through-smoke, attacker-blind, attackerinair (the event's bools),
  DeathNotice_Victim / _Killer, DeathNoticeWipe / Revenge / Domination, DeathNoticePenetrate (penetrated > 0),
  DeathNoticeHeadShot, DeathNoticeFlashbang (assistedflash), DeathNoticeSuicide, DeathNoticeAssist (assister != -1),
  TrueViewDeadOnServer; SpawnTime / Lifetime / LifetimeMod (x1.5 for a notice about you).
- Icon: `file://{images}/icons/equipment/<weapon>.svg`. Names: GetDecoratedPlayerName2 flags 0x16 + clan (teamid.md);
  colour classes DeathNoticeCTColor (team 3) / DeathNoticeTColor (2).
- huddeathnotice.vxml's order: Revenge, Domination, AttackerBlindIcon, Attacker, AssistParent ("+", Flashbang
  (flashbang_assist.svg), Assister), AttackerInAir, Weapon, NoScopeIcon, ThroughSmokeIcon, Penetrate, HeadShot, Suicide,
  Victim; the .vcss makes each visible by its class (#AttackerInAir margin-right -4px, margin-top -14px).
