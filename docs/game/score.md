# The kill's score: CS2's contribution score and deathmatch's points (server_20261105.dll)

Read 2026-11-20 with ReVa (headless, tools/re/game/reva.mjs). Ported in web/server/cs2web/core/contribution-score.js and
web/server/cs2web/modes/team/dm-score.js (called from core/game.js kill); checks: core/contribution-score-test.mjs.
Assists were already ported (combat/kill-notice.js, docs/game/death-notice.md: contributionscore_assist).

## Cvars (registration -> handle; value read at handle+8 +0x58)

| cvar | registered | handle | default | flags |
|---|---|---|---|---|
| contributionscore_kill | 1800998c0 | 0x18211a018 | 2 | 0x280004 |
| contributionscore_kill_reqs | 180099a10 | 0x18211a008 | 0 | 0x280004 |
| contributionscore_kill_factor | 180099970 | 0x18211a0f8 | 0 (float, read with 180187770) | 0x280004 |
| contributionscore_objective_kill | 180099ac0 | 0x18211a028 | 3 | 0x280004 |
| contributionscore_suicide | 180099c20 | 0x18211a0a8 | -2 | 0x280004 |
| contributionscore_team_kill | 180099cd0 | 0x18211a0b8 | -2 | 0x280004 |
| contributionscore_participation | 180099b70 | 0x18211a098 | 0 | 0x280004 (not ported: no reader read) |
| mp_dm_kill_base_score | 18009dea0 | 0x182118e50 | 8 | 0x282000 |
| mp_dm_bonus_percent | 18009dbd0 | 0x182118e60 | 50 | 0x282000 |
| mp_dm_taser_bonus_streak_max | 18009df60 | 0x182118e70 | 2 | 0x82000 |
| mp_dm_healthshot_killcount | 18009ddf0 | 0x182118e40 | 3 | 0x82000 |

Also registered, not read here: mp_dm_time_between_bonus_min / _max, mp_dm_bonus_length_min / _max,
mp_dm_dogtag_score, mp_dm_teammode (+ _kill_score / _bonus_score / _dogtag_score), mp_dm_bonusweapon_dogtags.
gamemode_deathmatch.cfg sets none of the scores (mp_roundtime 10, mp_timelimit 2, mp_maxrounds 0);
gamemode_deathmatch_tmm.cfg sets mp_dm_teammode 2 and the team-mode scores 1.

## Functions

| Address | What |
|---|---|
| 180209da0 | CCSPlayerPawn::Event_KilledOther(victim pawn, damage info): returns when the killer's pawn is the victim's; a non-enemy (180ad2700 false): 18095f620; else (both pawns real players, team 2 / 3) the flags (below), 18095f4b0 |
| 18095f620 | team kill: 1801fc0c0(killer, contributionscore_team_kill) |
| 18095f4b0 | (killer controller, victim pawn, flags): skipped when the game type (gametypes vfn 0x98) is 1, or contributionscore_kill_reqs bit 0 with flags bit 1 clear; 1801fc0c0(killer, objective_kill if flags bit 0 else kill); then floor(kill_factor x victim controller's +0x920 score) when both > 0 |
| 1802225f0 | pawn within 250 units (62500 squared) of a hostage in the list 0x181faab70 (count) / 0x181faab78 that 18093eba0 passes (alive, hostage +0xbcc clear) |
| 180222530 | pawn within 480 units (230400 squared) of a planted C4 in the list at 0x181f9f128 (next +0xa58) with m_bBombTicking (+0xa98) |
| 180952250 | CCSGameRules' death handling (calls PlayerKilled 180912130): the victim its own killer -> 1801fc0c0(victim, contributionscore_suicide) |
| 1801fc0c0 | add to a pawn's controller's score (its +0xe14 original controller -> 180a6e350) |
| 180922080 | CCSGameModeRules_Deathmatch's kill (rules, victim pawn, damage): see below |
| 18090d0d0 | DM award: 1801fc0c0(killer, points + bonus), the ClientPrint 3 line "%d" or "%d (+%d)" with #Player_Point_Award_Killed_Enemy(_Plural) / _NoWeapon(_Plural) / _Assist_Enemy(_Plural) |

Event_KilledOther's flags: bit 0 (objective) when 1802225f0(victim) or 1802225f0(killer); else for a T killer (pawn
+0x344 == 2): 180222530(victim) or 180222530(killer), else victim +0xe48 +0x218 > 0; for a CT killer: killer +0xe48
+0x218 > 0. Bit 1 when the damage's +0x4c & 0x902, or the killer controller's +0x800 test 180b0b390(victim, 2).
TODO(trace): +0xe48 +0x218 (taken as carrying a hostage) and 180b0b390.

## Deathmatch (180922080)

- The victim's slot (1813aa290, hashed) zeroes its entry in two counters at rules +0x48 (kills since death) and +0x68
  (Zeus streak).
- No points when the killer's pawn is the victim's, either is missing (a chicken kill: +1 and the _NoWeapon line,
  not ported: no killable chickens in deathmatch here), or 180ad2840 says not an enemy.
- The killer's +0x48 count + 1; every mp_dm_healthshot_killcount it gets weapon_healthshot unless it has one (no
  healthshot item in this game yet).
- The weapon: 1809260d0(damage info) dynamic_cast to CCSWeaponBase; none: no points (a grenade's projectile, fire).
  Points = mp_dm_kill_base_score + (vfn 0xc60 weapon type 0, the knife: 17; else by vfn 0xb88 the price: < 201 +10,
  < 501 +8, < 701 +6, < 1401 +5, < 2501 +3, < 3501 +2, else 0).
- Bonus = points x mp_dm_bonus_percent / 100 when the weapon's name equals the rules' +0x38 (the bonus weapon: none
  here yet), else 0; a Zeus (type 8): its +0x68 streak + 1 (1 the first time), bonus = (min(streak,
  mp_dm_taser_bonus_streak_max) - 1) x points.
- 18090d0d0(killer, points, bonus). Then the assister 1809284a0(victim, killer, 0): mp_dm_kill_base_score / 2 + 1 with
  the _Assist_Enemy line naming the victim.

## Not a bug (checked while here)

- Deathmatch's mp_timelimit doesn't cut its 10-minute round: the cfg's own mp_timelimit 2 / mp_roundtime 10, and the
  time limit is checked at the round's end (docs/game/intermission.md).
- callvote with an issue the server hasn't registered (Surrender in Casual): 1802905b0 prints only
  DevMsg("Vote Issue Not Found!") on the server; the caller is told nothing.
- The death panel's "Damage taken: N" is damage_taken (dealt), the bar the health actually removed
  (docs/game/death-panel.md): 13 damage at 5 health shows 13.
