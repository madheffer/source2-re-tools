# The round's cues: freeze beeps, match announcements, the kill sound, the death cam's sounds

server_20261105, client_20261105 (image base 0x180000000; client decompiled in client_20261015 at the address in
brackets); pak01 panorama.

## Functions

| Address | Module | What |
|---|---|---|
| 180913f80 | server | freeze period think (from the rules' Think 1809669f0): beeps, final beep, round_announce_match_start (1809147f2) |
| 18017e2d0 | server | f32 three-way compare (-1: curtime < start) |
| 1801f95b0 | server | difference |
| 180a9ca80 | server | per-player hold test (unread) |
| 180921600 | server | called with more than 3.0 s left (unread) |
| 18093d9e0 | server | match paused |
| 180921370 | server | timeout branch's call |
| 180957e50 | server | RestartRound; the announcement at 18095aad4..18095ac7c |
| 180209da0 | server | CCSPlayerPawn Event_KilledOther (this = pawn, victim, damage info) |
| 180ad2700 | server | victim is an enemy (victim, info + 0xe8) |
| 18095f620 | server | team kill handling (1801fc0c0 with cvar 18211a0c0's value) |
| 180a79ab0 | server | controller's team |
| 180b1b1e0 | server | weapon services' kill callback |
| 18095f4b0 | server | kill award (flags: 1 hostage-related, 2 blast / fire / through-smoke) |
| 18093e020 | server | game_type 1 |
| 180911f80 | server | deathmatch bonus weapon (+0x38 name) |
| 180c84d30 | server | one-recipient filter (no observers) |
| 180f697b0 | server | emit UI.KillCard.1 |
| 180b55410 | server | slot (>= 0 valid) |
| 1801c7480 | server | (181f57c70, the victim's 1801c8ce0): per-attacker record (unread) |
| 180b0adf0 | server | buy menu pickup of a ground weapon (weapon services, item def index), called from 1801ffc30 |
| 18093df90 / 18093d470 | server | rule tests for the pickup (true / false) |
| 180ad2540 | server | pawn alive |
| 180a0ef00 | server | team may pick up |
| 180ab9620 | server | item services refusal |
| 180aea0a0 | server | pick up |
| 180cecc30 [180ceaab0] | client | client mode FireGameEvent |
| 180ced234 | client | cs_round_start_beep handler |
| 180ced2a5 | client | cs_round_final_beep handler |
| 180ced1bf | client | round_time_warning handler |
| 180b71a40 | client | (0) non-zero: taken as "a local player" |
| 180c0ac10 | client | 2D sound emit (sixth argument params +0x18 = delay) |
| 1808550e0 | client | pawn state (1 or 4) |
| 18075f470 | client | time left |
| 180e84c60 [180e81ff0] | client | HUD match alerts listener (panel at this - 0x20) |
| 180e8f0d0 | client | show alert (panel, token, 2) |
| 180c0ae30 [180c09410] | client | 2D sound (volume 1.0, pitch 100) |
| 180c77710 | client | gg_killed_enemy listener (with item_pickup), at 180c7805a |
| 180c0ad30 | client | sound from the local pawn |
| 180acca00 / 180a7dd40 | client | called with bonus 0 (unread) |
| 180cee4d9 [180ceaab0 line 600..670] | client | player_death (local) |
| 180500a80 | client | HLTV replay running |
| 18076b970 | client | death music test (unread) |
| 18076b340 / 18076b480 / 18076b4c0 | client | modes 6 / 1 / 3 / 4 / 2 / mode 0 / game_type 1 |
| 18076e500 | client | PlayMusic(_, type, 0xffff, 0) |
| 180500ed0 [1804fff70] | client | HLTV replay start / end ("%.2f OnHltvReplay %s") |
| 180c1b5a0 | client | stop sound |
| 180adfca0 [180ade3c0] | client | game instructor lesson start (Instructor.LessonStart) |

## Fields

| Offset | Field |
|---|---|
| rules +0x10a0 | object whose vfn 0x18 returns early (unread) |
| rules +0x84 | != 5 in the death music test |
| rules +0x8c7 | byte gating round_time_warning |
| rules +0xd9 | m_bWarmupPeriod |
| rules +0xe4 / +0xe5 | m_bTerroristTimeOutActive / m_bCTTimeOutActive |
| rules +0xe8 / +0xec | timeout clocks |
| rules +0xfc | m_iFreezeTime |
| rules +0x108 | m_fRoundStartTime |
| rules +0x120 | m_totalRoundsPlayed |
| rules +0x128 | m_nOvertimePlaying |
| rules +0xa48 | m_eRoundWinReason (set 0 at 18095a825) |
| rules +0xf04 | m_nLastFreezeEndBeep |
| rules +0xf0c | match block: rounds played (short) |
| rules +0xf18 / +0xf20 | two teams' total scores (shorts; which is whose unread) |
| rules +0xf24 | phase: 2 first half, 3 second half |
| rules +0xf6c / +0xf68 | handle / curtime + xmm6 after a kill (unread) |
| info +0x3c | attacker |
| info +0xe8 block | +0 byte, +8 slot, +0xc team |
| pawn +0x344 | team |
| pawn +0x1520 | music state (client) |
| pawn +0x1530 | flags: bit 0 dominated, bit 1 revenge |
| pawn +0xfb0 | in a buy zone (taken) |
| replay +0x14 | type (4 = victory) |

## Constants

| Value | What |
|---|---|
| 1821170e5 | byte: freeze think returns early |
| 3.0 s | start beeps window |
| 10.0 s | round_time_warning threshold |
| mp_halftime 18211a3f0, mp_maxrounds 182119230, mp_overtime_maxrounds 1821197b8, mp_match_can_clinch 1821199a0 | cvar objects (+0x58 value; overtime.md) |
| 18211a6d8 | mp_teammates_are_enemies |
| 182178768 | cvar gating the buy menu pickup |
| 181929878 | weapon class list |
| 1824a6c20 | client cvar gating the Deathcam.Review sounds |
| UI.KillCard.1 | sounds/player/kill_doof_01, volume 0.6, mixgroup KillCard, mix layer KillCardLayer |
| Music.Match.FinalRound / MatchPoint | sounds/music/cs_stinger, volume 0.2 |
| Music.Match.LastRoundHalf | sounds/ui/lastroundhalf, 0.3 |
| UI.DeathMatch.Revenge | sounds/music/revenge, volume 0.0 |
| Player.FreezeCam | sounds/music/deathcam_stinger, volume 0.0, delay 0.05 |

## Freeze beeps (180913f80)

1. Return when rules +0x10a0's vfn 0x18 says so or 1821170e5 is set. m_fRoundStartTime non-finite: "Infinite round
   start time!", reset.
2. While curtime < m_fRoundStartTime, after a pass over the controllers (team 2 / 3, pawn not alive (vfn 0xca8), not
   held: 180a9ca80):
   - more than 3.0 s left: 180921600;
   - a match pause: m_fRoundStartTime = curtime + m_iFreezeTime;
   - no timeout: `n = (int)((m_fRoundStartTime - curtime) + 1.0f)` (subss, addss, cvttss2si); `n < 4` and
     `n != m_nLastFreezeEndBeep` -> stored, game event `cs_round_start_beep` (no fields). One under 3 s, 2 s, 1 s
     (exactly 3.0 gives 4);
   - a timeout: m_fRoundStartTime = curtime + m_iFreezeTime, the timeout clock counts down by the frame; no beep;
     180921370, return.
3. Reached: `cs_round_final_beep` (180914599..1809145be), the per-player pass, round_freeze_end,
   `round_announce_match_start` (1809147f2). Freeze time 0 still fires the final beep.

Client:
- cs_round_start_beep: 180b71a40(0) non-zero -> 2D `UI.CounterBeep` (180c0ac10, delay 0, volume 1.0).
- cs_round_final_beep: `UI.CounterDoneBeep`, always; then a local pawn (vfn 0xac0) with 1808550e0 1 or 4 and music
  state 2: PlayMusic(3), state 3 (music kit round start).
- round_time_warning: unless rules +0x8c7, with <= 10.0 s left: PlayMusic(7), state 7.

## RestartRound's announcement (180957e50)

Skipped in warmup. m_eRoundWinReason = 0 just before, so the "one less while a result stands" corrections never apply.
Integer `/ 2` is `cdq; sub eax, edx; sar eax, 1` (toward zero). max = mp_maxrounds, otmax = mp_overtime_maxrounds,
ot = m_nOvertimePlaying.

1. mp_halftime and phase 2: `half = ot ? (2 ot - 1) x (otmax / 2) + max : max / 2`; `half > 0` and rounds played
   `== half - 1` -> `round_announce_last_round_half`.
2. Else `max > 0` and m_totalRoundsPlayed `== otmax x ot - 1 + max`: `c = max / 2 + 1 + (otmax / 2) x ot` with
   mp_match_can_clinch (else -1, r15d as it stands); unless either score equals c -> `round_announce_final`.
3. Else `point = (otmax / 2) x ot + max / 2` with `max > 0` and mp_match_can_clinch, else -2; not in phase 2, either
   score `== point` -> `round_announce_match_point`.

No fields on the events.

| event | alert | sound |
|---|---|---|
| round_announce_match_start | #CSGO_Notice_Alert_Match_Start | none |
| round_announce_final | #SFUI_Notice_Alert_Final_Round | `Music.Match.FinalRound` |
| round_announce_match_point | #SFUI_Notice_Alert_Match_Point | `Music.Match.MatchPoint` |
| round_announce_last_round_half | #SFUI_Notice_Alert_Last_Round_Half | `Music.Match.LastRoundHalf` |

The same listener handles `show_survival_respawn_status`, `round_start`, `game_newmap` (Danger Zone's line, the
panel's reset). UNSETTLED: the phase without mp_halftime (taken as 2 all match: no match point).

## Kill sound (180209da0)

1. victim = the entity when a player (vfn 0x558) and alive (vfn 0xca8, IsAlive; life state changes after this call);
   attacker = info +0x3c the same way. victim == attacker: return.
2. Not an enemy by 180ad2700 -> 18095f620, return. 180ad2700: false when the block's byte +0 is set or its slot (+8)
   is the victim's; true with mp_teammates_are_enemies; else victim's team (controller 180a79ab0 or pawn +0x344) !=
   block team (+0xc).
3. 180b1b1e0, `other_death` for a non-player victim, 18095f4b0.
4. game_type 1 with victim and attacker: event `gg_killed_enemy` { victimid, attackerid, `dominated` 1 when victim
   flags bit 0 else `revenge` 1 when bit 1, `bonus` 1 when the attacker's active weapon's item def is the bonus weapon }.
5. this == the attacker's pawn: filter of its controller; with a valid slot 1801c7480(...); when `bonus` is 0,
   `UI.KillCard.1` from this pawn's index, volume 1.0 (180f697b0). Every mode.
6. +0xf6c / +0xf68 (unread).

Client gg_killed_enemy: attackerid is local -> `revenge` == 1: `UI.DeathMatch.Revenge` from the local pawn; `bonus` == 0:
180acca00 / 180a7dd40.

## Local death (player_death, 180cee4d9)

Only for the local pawn / controller, not during an HLTV replay.
- Not 18076b970, rules +0x84 != 5, game_type 0 with a classic mode (18076b340 or 18076b480): PlayMusic(4)
  (18076e500(_, 4, 0xffff, 0)).
- Else game_type 1 (18076b4c0): `Player.FreezeCam` (delay 0.5, volume 1.0). Its event volume is 0.0: inaudible.

## Deathcam.Review_* (180500ed0)

Param: the replay's delay (0 = END). Start, cvar 1824a6c20 on: 2D `Deathcam.Review_Victory` when replay type is 4,
else `Deathcam.Review_Start`; mix layers ReplayLayer / ReplayBlinkLayer. End: both stopped (180c1b5a0); cvar on:
`Deathcam.Review_End` from the local player; `hide_freezepanel`.

## Other sounds

- `UIPanorama.buymenu_pickup_weapon`: 180b0adf0. With cvar 182178768 on, 18093df90 true, 18093d470 false, pawn alive,
  +0xfb0 set: the first unowned weapon entity (class list 181929878; owner flag bit 9 clear) the team may pick up
  whose item def is the asked one and 180ab9620 doesn't refuse is picked up (180aea0a0), sound to the pawn and its
  observers (the buy menu taking a ground weapon).
- `UIPanorama.buymenu_purchase` [panorama]: scripts/mapdraft.vts on a map draft vote (`_PlaySoundEffect('buymenu_purchase')`
  after MatchDraftAPI.ActionIngameCastMyVote); popup_inspect_purchase-bar.vts, popup_shopping_cart_checkout.vts.
- `UIPanorama.round_report_line_down / _line_up / _odds_dn / _odds_none / _odds_up` [panorama]:
  scripts/hud/hudwinpanel.vts, the win panel's round report (line by the change in the terrorists' odds,
  `index x _m_timeslice` apart; the odds counter's tick).
- `UI.DeathMatchBonusAlertStart / AlertEnd / BonusKill` [panorama]: styles/hud/huddmbonus.vcss (`sound:` / `sound-out:`
  on `.bonuspanel--active`, `sound:` on the bonus points' animation).
- `Instructor.LessonStart`: 180adfca0.

## Unread

- 180913f80's per-player pass and its > 3 s call (180921600); 180b71a40.
- 180e8f0d0 (alert text, priority, time); 18076b970 and rules +0x84; 1801ffc30 (who asks 180b0adf0).
- The music kit's PlayMusic types 3 / 4 / 7 as sounds.
