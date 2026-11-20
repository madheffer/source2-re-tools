# The match's end, halftimes and overtime (server_20261105.dll)

Read 2026-11-16 (tools/re/game/cvardefs.py for the registrations, tools/re/game/xref.py on each convar's value handle, ReVa's
decompiler on the readers). Ported in web/server/cs2web/modes/team/comp.js (endRound, period, roundRestart); checked
by overtime-test.mjs beside it. Nothing here is from CS:GO's source.

## The convars (registrations, all `int`, flags 0x82000 unless noted)

| Convar | Default | Object (handle) | Help string |
|---|---|---|---|
| mp_overtime_enable | 0 | 0x182119790 | If a match ends in a tie, use overtime rules to determine winner |
| mp_overtime_maxrounds | 6 | 0x1821197b0 | When overtime is enabled play additional rounds to determine winner |
| mp_overtime_startmoney | 10000 | 0x1821197c0 | Money assigned to all players at start of every overtime half |
| mp_overtime_limit | 0 | 0x1821197a0 | When overtime is enabled, only so many overtimes can be played |
| mp_overtime_halftime_pausetimer | 0 | 0x182119918 | If set to 1 will set mp_halftime_pausetimer to 1 before every half of overtime ... |
| mp_halftime (0x282000) | 0 | 0x18211a3e8 | Determines whether the match switches sides in a halftime event. |
| mp_halftime_pausetimer (0x282000) | 0 | 0x1821198f8 | Set to 1 to stay in halftime indefinitely ... |
| mp_maxrounds (0x282100) | 0 | 0x182119228 | max number of rounds to play before server changes maps |
| mp_match_can_clinch (0x282000) | 1 | 0x182119998 | Can a team clinch and end the match by being so far ahead ... |
| mp_team_timeout_ot_add_once / _add_each / _max | 0 / 0 / 1 | 0x182119278 / 288 / 298 | timeouts added per overtime (not ported: no timeouts here) |

None of the gamemode cfgs sets an mp_overtime_* convar (gamemode_competitive.cfg / _competitive2v2.cfg /
_casual.cfg read 2026-11-16), so these defaults hold: src/cs2web/gamemodes.js CS2_OVERTIME. An int convar's value is
`*(int *)(*(handle + 8) + 0x58)` (README's helper row): the readers below reference handle + 8 (0x182119798 enable,
0x1821197b8 maxrounds, 0x1821197c8 startmoney, 0x1821197a8 limit, 0x182119920 overtime pausetimer, 0x182119230
mp_maxrounds, 0x18211a3f0 mp_halftime, 0x1821199a0 mp_match_can_clinch, 0x182119748 mp_startmoney).

## CCSGameRules fields used

| Offset | What |
|---|---|
| +0x128 (int, networked) | m_nOvertimePlaying: overtimes started (k) |
| +0xf10 (short) | the same count, the source of +0x128 |
| +0xf0c (short) | rounds played (the match's) |
| +0x11c / +0xf24 | the game phase (2 first half, 3 second half, 4 halftime, 5 match ended): set by 180961850 |
| +0x120 | rounds played, as the phase code reads it |
| +0xf18 / +0xf20 (short) | the two teams' scores; +0xf12..+0xf1e their first-half / second-half / overtime parts |
| +0xd9 | warmup |

## CheckWinLimit's rounds half (0x1809101e0)

With `reg` = mp_maxrounds, `ot` = mp_overtime_maxrounds, `k` = +0x128, every division an integer one:

1. clinched = mp_maxrounds >= 1 and mp_match_can_clinch and `need = reg / 2 + 1 + (ot / 2) * k` > 0 and **mp_halftime**
   and either score >= need. (Without mp_halftime nothing ever clinches: Casual plays all 15 rounds.)
2. total = `k * ot + reg`. total < 1: the mp_timelimit path (0x182119308; not ported). Else, when rounds played <
   total and not clinched: nothing.
3. Otherwise the match would end. If mp_overtime_enable and not clinched and (mp_overtime_limit < 1 or k <
   mp_overtime_limit): **another overtime** - the timeouts topped up (mp_team_timeout_ot_*), +0xf10 += 1 copied to
   +0x128, the phase set to 4 (halftime: 180961850 (+0xf0c, 4)), the halftime clock (mp_halftime_duration-like float
   0x182119a38) and the round start times recomputed, every controller's +0x839 set, then return. There is **no tie
   test**: reaching the last round without a clinch is the tie (with clinching on); with mp_match_can_clinch 0 or
   mp_halftime 0 every match that reaches its total would go to overtime.
4. Else the end: 18092cdf0 (the match's end / intermission); a clinch also prints `#SFUI_Notice_CTs_Clinched_Match`
   / `#SFUI_Notice_Ts_Clinched_Match` (HUD print 3) to everyone.

## The halftime round (IsLastRoundBeforeHalftime, 0x18093d850)

True when mp_halftime and the phase is 2 (a first half) and rounds played (- 1 while a round is running, +0xa48) ==
H - 1, where H = `reg / 2` in regulation and `(2k - 1) * (ot / 2) + reg` in overtime k. 0x18093d960 is the
"one win from the clinch" test: either score == `(ot / 2) * k + reg / 2` outside the first half (it returns the
match point; -2 when nothing clinches).

## RestartRound's halftime branch (0x180957e50, lines 287-312 of the decompile)

When the phase is 4 (halftime): if k == 0 or rounds played > `(k - 1) * ot + reg` (a halftime in the middle of a
period), the two teams' score parts are swapped, 18096c880 pushes them to the team entities (+0x770 / +0x774 / +0x778)
and the phase becomes 3 (second half); otherwise (rounds played == `(k - 1) * ot + reg`: the halftime that starts
overtime k) **no swap**, the phase becomes 2 (first half). Later in the same function (line ~1636), after any
halftime (bVar5) with mp_halftime on, 0x18090fbb0 sets every T / CT player's account to GetStartMoney (as a delta
through 180b00630), and +0xd58 is set from min(0x182119140, 0x182119150) clamped at 0 (not read further).

AreTeamsPlayingSwitchedSides (0x18090ee00) agrees: in overtime k the first half is "switched" when k is odd, the second
half when k is even; so regulation's second half, overtime 1's first half, overtime 1's second half unswitched,
overtime 2's first half unswitched, ... Each overtime starts on the sides the last period ended on and swaps at its
half.

## GetStartMoney (0x18092a5e0)

Warmup (+0xd9): 0x182119758's value (the warmup's own start money convar, not identified); else k > 0 ?
mp_overtime_startmoney : mp_startmoney. 0x18093dc60 is the "low start money" test (<= 800 at the match's or the
halftime's first round) on the same choice.

## The phase setter (0x180961850)

SetGamePhase(rules + 0xf0c, phase): phase 4 with mp_halftime_pausematch (0x182119910) prints
`#SFUI_Notice_Match_Will_Pause`; phase 4 in an overtime (+4 short != 0) with mp_overtime_halftime_pausetimer sets
mp_halftime_pausetimer 1; writes +0x11c, clears +0x124, fires `GamePhaseChanged`. Not ported (no pauses here).

## Not read

The halftime's duration and how the halftime phase ends (the swap of the players themselves, as opposed to the
scores: the team switch at the next round reset); what happens to a surviving player's weapons when an overtime starts
(no swap: comp.js keeps them as after any round; the halftime with a swap strips them); +0x839 on the controllers.
