# Match end, halftimes and overtime

server_20261105. gamemode_competitive.cfg / _competitive2v2.cfg / _casual.cfg (none sets an mp_overtime_* convar).

## Functions

| Address | Module | What |
|---|---|---|
| 0x1809101e0 | server | CheckWinLimit's rounds half |
| 18092cdf0 | server | the match's end / intermission |
| 0x18093d850 | server | IsLastRoundBeforeHalftime |
| 0x18093d960 | server | "one win from the clinch": returns the match point; -2 when nothing clinches |
| 0x180957e50 | server | RestartRound (halftime branch decompile lines 287-312; start money ~1636) |
| 18096c880 | server | pushes the score parts to the team entities (+0x770 / +0x774 / +0x778) |
| 0x18090fbb0 | server | sets every T / CT player's account to GetStartMoney (a delta through 180b00630) |
| 180b00630 | server | account delta |
| 0x18090ee00 | server | AreTeamsPlayingSwitchedSides |
| 0x18092a5e0 | server | GetStartMoney |
| 0x18093dc60 | server | "low start money" test: <= 800 at the match's or the halftime's first round, same choice |
| 0x180961850 | server | SetGamePhase(rules + 0xf0c, phase) |

## Fields (CCSGameRules)

| Offset | Field |
|---|---|
| +0x128 (int, networked) | m_nOvertimePlaying: overtimes started (k) |
| +0xf10 (short) | the same count, the source of +0x128 |
| +0xf0c (short) | rounds played (the match's) |
| +0x11c / +0xf24 | game phase (2 first half, 3 second half, 4 halftime, 5 match ended), set by 0x180961850 |
| +0x120 | rounds played, as the phase code reads it |
| +0x124 | cleared by the phase setter |
| +0xf18 / +0xf20 (short) | the two teams' scores; +0xf12..+0xf1e their first-half / second-half / overtime parts |
| +0xa48 | a round is running |
| +0xd58 | min(0x182119140, 0x182119150) clamped at 0 (not read further) |
| +0xd9 | warmup |
| controller +0x839 | set on every controller when an overtime starts (unread) |

## Constants (convars, all `int`, flags 0x82000 unless noted)

An int convar's value is `*(int *)(*(handle + 8) + 0x58)`; the readers reference handle + 8.

| Convar | Default | Object | handle + 8 | Help string |
|---|---|---|---|---|
| mp_overtime_enable | 0 | 0x182119790 | 0x182119798 | If a match ends in a tie, use overtime rules to determine winner |
| mp_overtime_maxrounds | 6 | 0x1821197b0 | 0x1821197b8 | When overtime is enabled play additional rounds to determine winner |
| mp_overtime_startmoney | 10000 | 0x1821197c0 | 0x1821197c8 | Money assigned to all players at start of every overtime half |
| mp_overtime_limit | 0 | 0x1821197a0 | 0x1821197a8 | When overtime is enabled, only so many overtimes can be played |
| mp_overtime_halftime_pausetimer | 0 | 0x182119918 | 0x182119920 | If set to 1 will set mp_halftime_pausetimer to 1 before every half of overtime ... |
| mp_halftime (0x282000) | 0 | 0x18211a3e8 | 0x18211a3f0 | Determines whether the match switches sides in a halftime event. |
| mp_halftime_pausetimer (0x282000) | 0 | 0x1821198f8 | | Set to 1 to stay in halftime indefinitely ... |
| mp_maxrounds (0x282100) | 0 | 0x182119228 | 0x182119230 | max number of rounds to play before server changes maps |
| mp_match_can_clinch (0x282000) | 1 | 0x182119998 | 0x1821199a0 | Can a team clinch and end the match by being so far ahead ... |
| mp_team_timeout_ot_add_once / _add_each / _max | 0 / 0 / 1 | 0x182119278 / 288 / 298 | | timeouts added per overtime |
| mp_startmoney | | | 0x182119748 | |
| mp_timelimit | | 0x182119308 | | |
| mp_halftime_duration-like float | | 0x182119a38 | | the halftime clock |
| mp_halftime_pausematch | | 0x182119910 | | |
| warmup start money (not identified) | | 0x182119758 | | |

## CheckWinLimit's rounds half (0x1809101e0)

`reg` = mp_maxrounds, `ot` = mp_overtime_maxrounds, `k` = +0x128, every division an integer one.

1. clinched = mp_maxrounds >= 1 and mp_match_can_clinch and `need = reg / 2 + 1 + (ot / 2) * k` > 0 and **mp_halftime** and either score >= need. (Without mp_halftime nothing clinches: Casual plays all 15 rounds.)
2. total = `k * ot + reg`. total < 1: the mp_timelimit path. Else rounds played < total and not clinched: nothing.
3. Else, mp_overtime_enable and not clinched and (mp_overtime_limit < 1 or k < mp_overtime_limit): **another overtime**: timeouts topped up (mp_team_timeout_ot_*), +0xf10 += 1 copied to +0x128, phase 4 (180961850(+0xf0c, 4)), the halftime clock and round start times recomputed, every controller's +0x839 set, return. **No tie test**: reaching the last round without a clinch is the tie (with clinching on); with mp_match_can_clinch 0 or mp_halftime 0 every match reaching its total goes to overtime.
4. Else the end: 18092cdf0; a clinch also prints `#SFUI_Notice_CTs_Clinched_Match` / `#SFUI_Notice_Ts_Clinched_Match` (HUD print 3) to everyone.

## IsLastRoundBeforeHalftime (0x18093d850)

True when mp_halftime and phase 2 and rounds played (- 1 while a round is running, +0xa48) == H - 1; H = `reg / 2` in
regulation, `(2k - 1) * (ot / 2) + reg` in overtime k. 0x18093d960: either score == `(ot / 2) * k + reg / 2` outside the first half.

## RestartRound's halftime branch (0x180957e50)

- Phase 4: k == 0 or rounds played > `(k - 1) * ot + reg` (a mid-period halftime): score parts swapped, 18096c880, phase 3. Else (rounds played == `(k - 1) * ot + reg`: the halftime starting overtime k) **no swap**, phase 2.
- After any halftime (bVar5) with mp_halftime on: 0x18090fbb0; +0xd58 set.
- AreTeamsPlayingSwitchedSides: in overtime k the first half is switched when k is odd, the second half when k is even (regulation's second half, OT1 first half switched; OT1 second half, OT2 first half unswitched, ...). Each overtime starts on the sides the last period ended on and swaps at its half.

## GetStartMoney (0x18092a5e0)

Warmup (+0xd9): 0x182119758's value; else k > 0 ? mp_overtime_startmoney : mp_startmoney.

## SetGamePhase (0x180961850)

Phase 4 with mp_halftime_pausematch prints `#SFUI_Notice_Match_Will_Pause`; phase 4 in an overtime (+4 short != 0)
with mp_overtime_halftime_pausetimer sets mp_halftime_pausetimer 1; writes +0x11c, clears +0x124, fires `GamePhaseChanged`.

## Unread

- The halftime's duration and how the halftime phase ends (the players' own team switch at the next round reset).
- A surviving player's weapons when an overtime starts (no swap) or at a swapping halftime.
- +0x839 on the controllers.
