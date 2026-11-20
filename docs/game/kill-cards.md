# The kill cards above the health / ammo panel

CS2's hudhealthammocenter.vxml `#hud-HA__kills` (five cards kill_1..5.svg, each with the six kill_pip_*.svg, and the
"extra" card kill_extra.svg with `{d:hud-HA-kill-count}`), styled by hudhealthammocenter.vcss. Ported in
web/src/ui/hud-kills.js / .css (client) and web/server/cs2web/combat/kill-notice.js (killType, the round's kill queue).

## Server (server_20261105.dll)
- **180912130** (the rules' player-killed handler, before the death notice 18091da70): the killer = 180de8600 when a
  living player pawn (0x558 + 0xca8). killer != victim: relationship = 180931650 (1 enemy, -1 same team);
  180b0b6e0(killer controller action tracking, relationship, headshot) and, when relationship == 1, the kill type
  pushed onto the killer controller's queue (180a6e260).
- **180b0b6e0**: relationship 1 (and headshot != -1): m_iNumRoundKills (action tracking +0x188) += 1, the headshot
  one (+0x18c) too when a headshot; the match totals +0x3f0 / +0x3f4 / +0x3f8 unless warmup (18093ec40).
- **Kill type** (inline here, also 180931910) from the damage type (info +0x4c): 0x40 DMG_BLAST -> 3, 8 DMG_BURN -> 4,
  4 DMG_SLASH -> 5, bit 19 (the headshot bit) -> 2, 0x100 DMG_SHOCK -> 6, else 1.
- **180a6e260** (push): m_nKillCount (+0x931) > 7: count - 1, m_nFirstKill (+0x930) = (first + 1) & 7; then
  m_recentKillQueue[(first + count) & 7] (+0x928, 8 bytes) = type, count + 1.
- **Cleared** (180a9a6c0: count 0, first 0; 180b20df0: round kills, headshots, round damage +0x190 zeroed) from
  180249530 (the pawn's respawn, vfn 0xaf8) and 18093fe70.
- Client schema: CCSPlayerController m_recentKillQueue +0x958, m_nFirstKill +0x960, m_nKillCount +0x961; the action
  tracking services (+0x828) m_iNumRoundKills +0x128, m_iNumRoundKillsHeadshots +0x12c.

## Client (client_20261015.dll 180e92db0, the health / ammo panel's update)
- The watched pawn's controller (pawn +0x14bc); n = m_iNumRoundKills; the class group (vfn 0x508) on the panel:
  HUD--NumKills--{1..5}, HUD--NumKills--extra at 6 or more, none at 0 (table DAT_1825d6910, index min(n, 6)).
- When the watched player changed or n changed: on every listener panel (param_1 +0x1b0 list, the
  HUD--on-kill--listener ones) "animate" = same player; same player and n went up: HUD--on-kill re-triggered
  (vfn 0x510); another player: HUD--on-kill off. Then for i < min(m_nKillCount, 5): the group "kill--{i+1}" =
  HUD--Kill{i+1}--{default, headshot, blast, burn, slash, shock}[type - 1] of queue[(first + i) & 7]
  (table DAT_1825d6930 + type x 10 + i x 2).
- The particle panels (ported: ui/hud-kills-fx.js, lasers-bake --uifx): the streak panel (+0x238, #hud-HA__kills--fx,
  team wash) gets table 1822445d0[n] (n < 7: ui_hud_kill_streaks_1..5, 6 _many; 7+ entry 0, particles/dev/empty) or,
  spectating, 182244598 (the _spectator_ set); the special panel (+0x240, #hud-HA__Specialkills--fx, wash white)
  182244608[newest type] (3 ui_hud_kill_sc_blast, 4 _sc_burn, 6 _sc_shock, else empty); both started (180e64cf0) when
  the same player has kills, stopped (180e64f00) when the player changed or has none. ParticleScenePanel: cameraOrigin
  0 600 127, lookAt 0 0 127, fov 41; .UiParticlePanelAmmoCenter (particle_controls.vcss) 900 x 500, bottom centre,
  translate 0 16, additive.
- hud-HA-kill-count = min(n, 99).

## Styles (hudhealthammocenter.vcss)
- CSGOHudHealthAmmoCenter 180 tall, bottom, margin-bottom 16; .hud-HA__kills 150 x 300 centred, translate(0, 52);
  .hud-HA__kill-flag full height, translate(0, 42) until shown, transform transition 0 s (.animate 0.2 s ease-in-out);
  .kill-flag-svg-size 152 tall centred; the fan transforms per NumKills (vcss 1045-1125: up to -24 / +24 degrees);
  @keyframes on-kill (brightness 6, 6 at 30 %, 1) on the newest card's .animate, the extra card's and the bar's
  HUD--on-kill, 0.7 s ease-out; on-kill-spotlight (0, 0.2 at 1 %, 0.2 at 30 %, 0) on the 36 x 100 spotlight.
- Ported: world-blur hudWorldBlur (gaussian(2,2,2): backdrop-filter sigma 2 x sqrt 2) behind each card, the team-washed
  bluedots_large pattern (0.2) through kill_mask. Not used: the scrimcomp2v2 variants (no such class here).

## The panel's camera (CCSGO_Particle3dPanel, client_20261015 vtable 181cd0148)
- Attributes (static table 1825cadb0, parsed by slot 27 180e38060): fov -> +0x8d4 (default -1000: unset), farPlane ->
  +0x8d8 (default 1000), cameraOrigin -> +0x8dc..+0x8e4, lookAt -> +0x8e8..+0x8f0, squarePixels -> +0x8fb (default 0:
  the constructor's 0x10000 at +0x8f8).
- Slot 85 180e695e0, fov >= 0: angles = VectorAngles(lookAt - origin), the camera struct's fov (+0x18) = fov, aspect
  (+0x1c) = 1.0, near 1, far farPlane; with squarePixels the aspect becomes the panel's width / height. 18174fe70 ->
  18174fb00 -> 18174ef50: tan(fov x 0.5 x 0.017453292) times near on the horizontal extent, that over the aspect
  (clamped to 1/1024 at least) on the vertical. So the kill-fx panels draw a square 41 degree view stretched over 900 x
  500 (ui/hud-kills-fx.js).
- wash-color: the colour over the panel's pixels, their alpha kept (as the repo's other panels draw it).

## Still unread
- 18093fe70's other duties. The watched player's cards: the snapshot sends your own, or the living player you watch
  while dead (me.rk / me.rkid). Nothing else open on the cards.
