# The round's cues: freeze beeps, match announcements, the kill sound, the death cam's sounds

server_20261105.dll and client_20261105.dll (image base 0x180000000), read 2026-11-18 with tools/re and Ghidra
(server_20261105; the client's functions decompiled in client_20261015 at the address in brackets, found by the same
string's xref). The ports: web/src/cs2web/sim/round-announce.js (+ its test), server/cs2web/core/game.js (the beeps,
the kill sound), server/cs2web/modes/team/comp.js (the announcements), client/core/game.js (`announce`),
server/cs2web/modes/team/round-sounds-test.mjs. The sounds are in ze-ui/sounds (bake/MenuSoundBake.cs).

## 1. The freeze time's beeps: `180913f80` (the freeze period's think, from the rules' Think 1809669f0)

Returns at once when the object at rules +0x10a0 says so (its vfn 0x18: unread) or the byte 1821170e5 is set.
m_fRoundStartTime (+0x108) non-finite: "Infinite round start time!" and it is reset. Then, **while curtime <
m_fRoundStartTime** (18017e2d0 gives -1), after a pass over the controllers (a team 2 / 3 player whose pawn isn't
alive, vfn 0xca8, and isn't otherwise held: 180a9ca80, unread):

- more than 3.0 s left (1801f95b0 = the difference): 180921600 (unread);
- a match pause (18093d9e0): m_fRoundStartTime = curtime + m_iFreezeTime (+0xfc);
- **no timeout running** (m_bTerroristTimeOutActive +0xe4 and m_bCTTimeOutActive +0xe5 both 0):
  `n = (int)((m_fRoundStartTime - curtime) + 1.0f)` (subss, addss, cvttss2si); **`n < 4` and `n !=
  m_nLastFreezeEndBeep` (+0xf04)** -> it is stored and the game event **`cs_round_start_beep`** fires (no fields).
  So one as the time left drops under 3 s, under 2 s and under 1 s (exactly 3.0 left gives 4: not yet).
- a timeout running: m_fRoundStartTime = curtime + m_iFreezeTime again and the timeout's own clock (+0xe8 / +0xec)
  counts down by the frame (comp-pause.js); no beep. 180921370, return.

**Once curtime reaches it**: the game event **`cs_round_final_beep`** (180914599..1809145be), then the per-player
pass and the rest of the freeze's end (round_freeze_end, `round_announce_match_start` at 1809147f2: unread here).
A freeze time of 0 still fires the final beep, with no start beeps before it.

The client (the client mode's FireGameEvent 180cecc30 [180ceaab0], below):
- `cs_round_start_beep` (180ced234): when 180b71a40(0) is non-zero (unread: taken as "a local player"), the 2D sound
  **`UI.CounterBeep`** through 180c0ac10 (delay 0, volume 1.0).
- `cs_round_final_beep` (180ced2a5): **`UI.CounterDoneBeep`** the same way, always; then for a local pawn (vfn 0xac0)
  whose 1808550e0 is 1 or 4 and whose music state (+0x1520) is 2: PlayMusic(3) and the state 3 (the music kit's
  round start cue: not ported, no kit music here but the win panel's and the end of match's).
- `round_time_warning` (180ced1bf): unless the rules' byte +0x8c7, with 10.0 s or less left (18075f470): PlayMusic(7)
  and the music state 7 (not ported).

Port: game.js's tick (the beeps as `{ k: 'snd', n, ui: 1 }` to everyone; a held freeze sends none), sim/round-announce.js
`freezeBeep`. ZE runs it too (mp_freezetime 5 on GFL: three beeps and the end's).

## 2. RestartRound's announcement: `180957e50` at 18095aad4..18095ac7c

Skipped in the warmup (m_bWarmupPeriod +0xd9). m_eRoundWinReason (+0xa48) was set to 0 at 18095a825 just before, so
the "one less while a round's result stands" corrections on the two counts never apply here. The cvar objects (their
+0x58 the value; overtime.md names them): mp_halftime 18211a3f0, mp_maxrounds 182119230, mp_overtime_maxrounds
1821197b8, mp_match_can_clinch 1821199a0. The match's block is at rules +0xf0c: its rounds played (a short, +0xf0c),
the two teams' total scores (shorts +0xf18 and +0xf20: which is whose isn't read, both are tested alike), the phase
(+0xf24: 2 first half, 3 second half). m_totalRoundsPlayed +0x120, m_nOvertimePlaying +0x128. Integer division by 2
is `cdq; sub eax, edx; sar eax, 1` (toward zero).

1. **mp_halftime and the phase is 2**: `half = ot ? (2 ot - 1) x (otmax / 2) + max : max / 2`; `half > 0` and the
   match's rounds played `== half - 1` -> **`round_announce_last_round_half`**.
2. else, with `max > 0` and m_totalRoundsPlayed `== otmax x ot - 1 + max` (the period's last round): the clinching
   score `c = max / 2 + 1 + (otmax / 2) x ot` with mp_match_can_clinch (else -1, r15d as it stands); **unless either
   score equals c**, **`round_announce_final`**.
3. else `point = (otmax / 2) x ot + max / 2` with `max > 0` and mp_match_can_clinch, else -2; **not in a phase 2**,
   either score `== point` -> **`round_announce_match_point`**.

The events have no fields. `round_announce_match_start` is fired from 180913f80 (1), not here.

The client's HUD alert panel listens (180e84c60 [180e81ff0], a CCSGO_HudMatchAlerts-style listener; the panel is at
its this - 0x20): each shows its alert through 180e8f0d0(panel, token, 2) and plays a 2D sound through 180c0ae30
[180c09410] with volume 1.0, pitch 100:

| event | alert | sound |
|---|---|---|
| round_announce_match_start | #CSGO_Notice_Alert_Match_Start | none |
| round_announce_final | #SFUI_Notice_Alert_Final_Round | `Music.Match.FinalRound` |
| round_announce_match_point | #SFUI_Notice_Alert_Match_Point | `Music.Match.MatchPoint` |
| round_announce_last_round_half | #SFUI_Notice_Alert_Last_Round_Half | `Music.Match.LastRoundHalf` |

(`show_survival_respawn_status`, `round_start` and `game_newmap` are the same function's other events: Danger Zone's
line and the panel's reset.) FinalRound and MatchPoint are both sounds/music/cs_stinger (volume 0.2), LastRoundHalf
sounds/ui/lastroundhalf (0.3).

Port: sim/round-announce.js `roundAnnounce`, comp.js roundStart (a live round of a round-limited match), the event
`{ k: 'announce', a }`, the client's stinger. **Not ported: the alert's text** (180e8f0d0's priority 2: how long it
shows isn't read; hud/warmup-alert.js has the panel). UNSETTLED: the phase without mp_halftime, taken as 2 all match
(no match point then; nothing clinches without mp_halftime in comp.js either).

## 3. A kill's sound: CCSPlayerPawn's Event_KilledOther `180209da0` (this = the pawn, the victim, the damage info)

- victim = the entity when it is a player (vfn 0x558) and alive (vfn 0xca8: read as IsAlive from 180913f80's use on
  the pawns it respawns; the victim's life state changes after this call); attacker = the info's attacker (+0x3c)
  the same way. **victim == attacker: return.**
- a victim that isn't an enemy by **180ad2700(victim, info + 0xe8)** -> 18095f620 (the team kill's handling: 1801fc0c0
  with the cvar 18211a0c0's value) and return. 180ad2700: false when the info's attacker block has its byte +0 set
  or its slot (+8) is the victim's; true with mp_teammates_are_enemies (18211a6d8); else the victim's team (its
  controller's 180a79ab0, or the pawn's +0x344) != the block's team (+0xc).
- the weapon services' kill callback (180b1b1e0), `other_death` for a non-player victim, the kill award
  (18095f4b0 with flags: 1 a hostage-related kill, 2 a blast / fire / through-smoke one: outline only).
- **18093e020 (game_type 1) with a victim and an attacker**: the game event **`gg_killed_enemy`**: victimid,
  attackerid, `dominated` 1 when the victim's flags (+0x1530) bit 0 is set else `revenge` 1 when bit 1 is, and
  `bonus` 1 when the attacker's active weapon's item definition is deathmatch's bonus weapon (180911f80's +0x38 name).
- **this == the attacker's pawn**: a filter of one recipient, this pawn's controller (180c84d30: no observers), and
  **when `bonus` is 0** the sound **`UI.KillCard.1`** from this pawn's index, volume 1.0 (180f697b0). Before it, with
  a valid slot (180b55410 >= 0), 1801c7480(181f57c70, the victim's 1801c8ce0) (unread: a per-attacker record).
  This is outside the game_type test: every mode.
- then m_... +0xf6c / +0xf68 (a handle and curtime + the float in xmm6: unread).

UI.KillCard.1: sounds/player/kill_doof_01, volume 0.6, mixgroup KillCard with the mix layer KillCardLayer
(lib/sound-mix-cs2.js has both).

Port: game.js kill(): a living attacker's kill of an enemy (game.teammates: the same team unless
mp_teammates_are_enemies) sends `{ k: 'snd', n: 'UI.KillCard.1', ui: 1, to: the attacker }`. TODO: no deathmatch bonus
weapon here, so its kills aren't left out.

The client's `gg_killed_enemy` (the same listener as item_pickup's, 180c77710 at 180c7805a): attackerid is the local
player -> with `revenge` == 1 the sound **`UI.DeathMatch.Revenge`** from the local pawn (180c0ad30); with `bonus` == 0
a call into 180acca00 / 180a7dd40 (unread). **UI.DeathMatch.Revenge's volume is 0.0 in CS2's own event**
(sounds/music/revenge): nothing is heard, nothing to port.

## 4. The local player's death: the client mode's `player_death` (180cee4d9 [180ceaab0 line 600..670])

Only when the event's userid is the local pawn or the local controller. Not during an HLTV replay (180500a80).
- not 18076b970 (unread), the rules' +0x84 != 5, and game_type 0 with a classic game_mode (18076b340: modes 6 / 1 / 3
  / 4 / 2, or 18076b480: mode 0): **PlayMusic(4)** (18076e500(_, 4, 0xffff, 0): the music kit's death cam cue; not
  ported, no kit music);
- else game_type 1 (18076b4c0): the sound **`Player.FreezeCam`** (delay 0.5, volume 1.0: the emit helper
  180c0ac10's sixth argument is the params' +0x18, the delay).

**Player.FreezeCam's volume is 0.0 in CS2's own event** (sounds/music/deathcam_stinger, delay 0.05): nothing is heard
in deathmatch or Arms Race either, nothing to port.

## 5. Deathcam.Review_*: the HLTV kill replay, client `180500ed0` [1804fff70] ("%.2f OnHltvReplay %s")

The replay system's start / end (param: the replay's delay, 0 = END): at the start, with the cvar 1824a6c20 on, a 2D
`Deathcam.Review_Victory` when the replay's type (+0x14) is 4, else `Deathcam.Review_Start`; the mix layers
ReplayLayer / ReplayBlinkLayer. At the end both are stopped (180c1b5a0) and, with the cvar on, `Deathcam.Review_End`
plays from the local player; `hide_freezepanel`. There is no kill replay here (spec_replay): not ours yet.

## 6. Sounds this session placed elsewhere

- **`UIPanorama.buymenu_pickup_weapon`**: server `180b0adf0(weapon services, item definition index)`, called from
  1801ffc30 (unread: the buy path). With the cvar 182178768 on, 18093df90 true and 18093d470 false (unread rule
  tests), the pawn alive (180ad2540) and its byte +0xfb0 set (read as "in a buy zone"): the first unowned weapon
  entity (class list 181929878; owner flag bit 9 clear) the pawn's team may pick up (180a0ef00) whose item definition
  is the asked one and that the item services' 180ab9620 doesn't refuse is picked up (180aea0a0) with the sound to
  the pawn and its observers. This is the buy menu taking a dropped weapon from the ground: **not ported** (cs2-buy.js
  always buys).
- **`UIPanorama.buymenu_purchase`** [panorama]: not the buy menu. scripts/mapdraft.vts plays it on a map draft vote
  (`_PlaySoundEffect('buymenu_purchase')` after MatchDraftAPI.ActionIngameCastMyVote); popup_inspect_purchase-bar.vts
  and popup_shopping_cart_checkout.vts on a store purchase.
- **`UIPanorama.round_report_line_down / _line_up / _odds_dn / _odds_none / _odds_up`** [panorama]:
  scripts/hud/hudwinpanel.vts, the win panel's round report (each event's line by the change in the terrorists'
  odds, `index x _m_timeslice` apart; the odds counter's own tick). No round report in our win panel.
- **`UI.DeathMatchBonusAlertStart / AlertEnd / BonusKill`** [panorama]: styles/hud/huddmbonus.vcss (`sound:` /
  `sound-out:` on `.bonuspanel--active`, `sound:` on the bonus points' animation): deathmatch's bonus weapon panel.
  No bonus weapon here.
- **`Instructor.LessonStart`**: client 180adfca0 [180ade3c0], the game instructor's lesson start. No instructor here.

## Unread

180913f80's per-player pass and its > 3 s call (180921600); 180b71a40 (the start beep's test); the alert's 180e8f0d0
(text, priority, time); 18076b970 and the rules' +0x84 in the death's music test; 1801ffc30 (who asks
180b0adf0); the music kit's PlayMusic types 3 / 4 / 7 as sounds.
