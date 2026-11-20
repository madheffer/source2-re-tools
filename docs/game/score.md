# The kill's score: contribution score and deathmatch points

server_20261105. Configs: gamemode_deathmatch.cfg, gamemode_deathmatch_tmm.cfg. Assists: death-notice.md
(contributionscore_assist).

## Functions

| Address | Module | What |
|---|---|---|
| 180209da0 | server | CCSPlayerPawn::Event_KilledOther(victim pawn, damage info) |
| 180ad2700 | server | enemy test (false: team kill) |
| 18095f620 | server | team kill: 1801fc0c0(killer, contributionscore_team_kill) |
| 18095f4b0 | server | kill score (killer controller, victim pawn, flags) |
| 1802225f0 | server | pawn within 250 u (62500 squared) of a hostage passing 18093eba0 (alive, hostage +0xbcc clear) |
| 180222530 | server | pawn within 480 u (230400 squared) of a planted C4 with m_bBombTicking |
| 180b0b390 | server | (victim, 2) test with the killer controller's +0x800 (unread) |
| 180952250 | server | CCSGameRules death handling (calls PlayerKilled 180912130): suicide score |
| 1801fc0c0 | server | add to a pawn's controller's score (its +0xe14 original controller -> 180a6e350) |
| 180187770 | server | float cvar read |
| 180922080 | server | CCSGameModeRules_Deathmatch kill (rules, victim pawn, damage) |
| 1813aa290 | server | the victim's slot (hashed) |
| 180ad2840 | server | DM enemy test |
| 1809260d0 | server | damage info's weapon (dynamic_cast CCSWeaponBase) |
| 18090d0d0 | server | DM award (killer, points, bonus) |
| 1809284a0 | server | DM assister (victim, killer, 0) |
| 1802905b0 | server | callvote with an unregistered issue: DevMsg("Vote Issue Not Found!") only, caller told nothing |

## Fields

| Offset | Field |
|---|---|
| 0x181faab70 / 0x181faab78 | hostage list count / entries |
| 0x181f9f128 | planted C4 list (next +0xa58) |
| planted C4 +0xa98 | m_bBombTicking |
| pawn +0x344 | team (2 = T) |
| pawn +0xe48 +0x218 | > 0: taken as carrying a hostage (TODO) |
| damage +0x4c | type (& 0x902 sets flag bit 1) |
| controller +0x920 | score |
| controller +0x800 | used with 180b0b390 |
| rules +0x48 | DM kills since death (per slot) |
| rules +0x68 | DM Zeus streak (per slot) |
| rules +0x38 | DM bonus weapon name |

## Constants

Cvar value read at handle+8 +0x58.

| cvar | registered | handle | default | flags |
|---|---|---|---|---|
| contributionscore_kill | 1800998c0 | 0x18211a018 | 2 | 0x280004 |
| contributionscore_kill_reqs | 180099a10 | 0x18211a008 | 0 | 0x280004 |
| contributionscore_kill_factor | 180099970 | 0x18211a0f8 | 0 (float) | 0x280004 |
| contributionscore_objective_kill | 180099ac0 | 0x18211a028 | 3 | 0x280004 |
| contributionscore_suicide | 180099c20 | 0x18211a0a8 | -2 | 0x280004 |
| contributionscore_team_kill | 180099cd0 | 0x18211a0b8 | -2 | 0x280004 |
| contributionscore_participation | 180099b70 | 0x18211a098 | 0 | 0x280004 (no reader read) |
| mp_dm_kill_base_score | 18009dea0 | 0x182118e50 | 8 | 0x282000 |
| mp_dm_bonus_percent | 18009dbd0 | 0x182118e60 | 50 | 0x282000 |
| mp_dm_taser_bonus_streak_max | 18009df60 | 0x182118e70 | 2 | 0x82000 |
| mp_dm_healthshot_killcount | 18009ddf0 | 0x182118e40 | 3 | 0x82000 |

Also registered, not read: mp_dm_time_between_bonus_min / _max, mp_dm_bonus_length_min / _max, mp_dm_dogtag_score,
mp_dm_teammode (+ _kill_score / _bonus_score / _dogtag_score), mp_dm_bonusweapon_dogtags.
gamemode_deathmatch.cfg sets none of the scores (mp_roundtime 10, mp_timelimit 2, mp_maxrounds 0);
gamemode_deathmatch_tmm.cfg sets mp_dm_teammode 2 and the team-mode scores 1.

## Event_KilledOther (180209da0)

1. Return when the killer's pawn is the victim's. Not an enemy (180ad2700): 18095f620.
2. Else (both pawns real players, team 2 / 3): the flags, then 18095f4b0.
   - Bit 0 (objective): 1802225f0(victim) || 1802225f0(killer); else T killer: 180222530(victim) || 180222530(killer)
     || victim +0xe48 +0x218 > 0; CT killer: killer +0xe48 +0x218 > 0.
   - Bit 1: damage +0x4c & 0x902, or killer controller +0x800 test 180b0b390(victim, 2).
3. 18095f4b0: skipped when game type (gametypes vfn 0x98) is 1, or contributionscore_kill_reqs bit 0 with flags bit 1
   clear; 1801fc0c0(killer, bit 0 ? objective_kill : kill); then `floor(kill_factor * victim controller +0x920)` when
   both > 0.

Suicide (180952250): victim its own killer -> 1801fc0c0(victim, contributionscore_suicide).

## Deathmatch (180922080)

1. Zero the victim's +0x48 and +0x68 entries.
2. No points when the killer's pawn is the victim's, either is missing (a chicken kill: +1 and the _NoWeapon line), or
   180ad2840 says not an enemy.
3. Killer's +0x48 + 1; every mp_dm_healthshot_killcount kills it gets weapon_healthshot unless it has one.
4. Weapon = 1809260d0; none (grenade projectile, fire): no points.
5. Points = mp_dm_kill_base_score + (vfn 0xc60 weapon type 0, knife: 17; else by vfn 0xb88 price: < 201 +10, < 501 +8,
   < 701 +6, < 1401 +5, < 2501 +3, < 3501 +2, else 0).
6. Bonus = `points * mp_dm_bonus_percent / 100` when the weapon's name equals rules +0x38, else 0; Zeus (type 8): +0x68
   streak + 1 (1 the first time), bonus = `(min(streak, mp_dm_taser_bonus_streak_max) - 1) * points`.
7. 18090d0d0: 1801fc0c0(killer, points + bonus), ClientPrint 3 "%d" or "%d (+%d)" with
   #Player_Point_Award_Killed_Enemy(_Plural) / _NoWeapon(_Plural) / _Assist_Enemy(_Plural).
8. 1809284a0: assister gets `mp_dm_kill_base_score / 2 + 1` with the _Assist_Enemy line naming the victim.

## Notes

- Deathmatch's mp_timelimit doesn't cut its 10-minute round: the cfg's mp_timelimit 2 / mp_roundtime 10, and the time
  limit is checked at the round's end (intermission.md).
- The death panel's "Damage taken: N" is damage_taken (dealt), the bar the health actually removed (death-panel.md): 13
  damage at 5 health shows 13.

## Unread

- pawn +0xe48 +0x218 (taken as carrying a hostage) and 180b0b390.
