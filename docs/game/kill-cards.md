# Kill cards above the health / ammo panel

server_20261105, client_20261015. hudhealthammocenter.vxml `#hud-HA__kills` (five cards kill_1..5.svg, each with the six
kill_pip_*.svg, and the extra card kill_extra.svg with `{d:hud-HA-kill-count}`), hudhealthammocenter.vcss,
particle_controls.vcss.

## Functions

| Address | Module | What |
|---|---|---|
| 180912130 | server | the rules' player-killed handler (before the death notice 18091da70) |
| 18091da70 | server | the death notice |
| 180de8600 | server | the killer, when a living player pawn (0x558 + 0xca8) |
| 180931650 | server | relationship: 1 enemy, -1 same team |
| 180b0b6e0 | server | action tracking (controller's services, relationship, headshot): round kill counts |
| 180931910 | server | kill type from the damage type (also inlined in 180912130) |
| 180a6e260 | server | push a kill type onto the controller's recent-kill queue |
| 18093ec40 | server | warmup test |
| 180a9a6c0 | server | clear the queue (count 0, first 0) |
| 180b20df0 | server | clear round kills, headshots, round damage |
| 180249530 | server | the pawn's respawn (vfn 0xaf8): calls the clears |
| 18093fe70 | server | also calls the clears (its other duties unread) |
| 180e92db0 | client | the health / ammo panel's update |
| 180e64cf0 / 180e64f00 | client | start / stop a particle panel |
| 180e38060 | client | CCSGO_Particle3dPanel slot 27: parses the attributes |
| 180e695e0 | client | CCSGO_Particle3dPanel slot 85: the camera |
| 18174fe70 -> 18174fb00 -> 18174ef50 | client | projection from fov / aspect |

## Fields

| Offset | Field |
|---|---|
| damage info +0x4c | damage type |
| action tracking +0x188 / +0x18c | m_iNumRoundKills / m_iNumRoundKillsHeadshots (server) |
| action tracking +0x190 | round damage |
| action tracking +0x3f0 / +0x3f4 / +0x3f8 | match totals |
| controller +0x928 | m_recentKillQueue (8 bytes, server) |
| controller +0x930 / +0x931 | m_nFirstKill / m_nKillCount (server) |
| controller +0x958 / +0x960 / +0x961 | m_recentKillQueue / m_nFirstKill / m_nKillCount (client) |
| controller +0x828 (client) | action tracking services: m_iNumRoundKills +0x128, m_iNumRoundKillsHeadshots +0x12c |
| pawn +0x14bc (client) | the watched pawn's controller |
| panel +0x1b0 | listener panel list (the HUD--on-kill--listener ones) |
| panel +0x238 | streak particle panel (#hud-HA__kills--fx, team wash) |
| panel +0x240 | special particle panel (#hud-HA__Specialkills--fx, wash white) |
| Particle3dPanel +0x8d4 | fov (default -1000: unset) |
| +0x8d8 | farPlane (default 1000) |
| +0x8dc..+0x8e4 | cameraOrigin |
| +0x8e8..+0x8f0 | lookAt |
| +0x8fb | squarePixels (default 0: the constructor's 0x10000 at +0x8f8) |
| camera +0x18 / +0x1c | fov / aspect |

## Constants

| Value | What |
|---|---|
| 0x40 DMG_BLAST -> 3, 8 DMG_BURN -> 4, 4 DMG_SLASH -> 5, bit 19 (headshot) -> 2, 0x100 DMG_SHOCK -> 6, else 1 | kill type |
| DAT_1825d6910 | class table, index min(n, 6): none at 0, HUD--NumKills--{1..5}, HUD--NumKills--extra at 6+ |
| DAT_1825d6930 + type x 10 + i x 2 | card class HUD--Kill{i+1}--{default, headshot, blast, burn, slash, shock}[type - 1] |
| 1822445d0[n] | streak particles: n < 7 ui_hud_kill_streaks_1..5, 6 _many; 7+ entry 0 (particles/dev/empty) |
| 182244598 | the _spectator_ streak set |
| 182244608[type] | special: 3 ui_hud_kill_sc_blast, 4 _sc_burn, 6 _sc_shock, else empty |
| 1825cadb0 | Particle3dPanel attribute table |
| 181cd0148 | CCSGO_Particle3dPanel vtable (client) |
| 0.017453292 | degrees -> radians |

## Server

1. 180912130: killer != victim: relationship = 180931650; 180b0b6e0(killer controller's action tracking, relationship, headshot); relationship == 1: kill type pushed (180a6e260).
2. 180b0b6e0, relationship 1 (and headshot != -1): m_iNumRoundKills += 1, the headshot one too when a headshot; the match totals unless warmup.
3. Push: m_nKillCount > 7: count - 1, `first = (first + 1) & 7`; then `queue[(first + count) & 7] = type`, count + 1.

## Client (180e92db0)

1. n = m_iNumRoundKills of the watched pawn's controller; the class group (vfn 0x508) on the panel from DAT_1825d6910.
2. Watched player or n changed: every listener panel's "animate" = same player; same player and n went up: HUD--on-kill re-triggered (vfn 0x510); another player: HUD--on-kill off.
3. For i < min(m_nKillCount, 5): group "kill--{i+1}" = the class of queue[(first + i) & 7].
4. Streak panel: 1822445d0[n], or spectating 182244598; special panel: 182244608[newest type]. Both started when the same player has kills, stopped when the player changed or has none.
5. hud-HA-kill-count = min(n, 99).

## Particle panel camera (slot 85, fov >= 0)

- angles = VectorAngles(lookAt - origin); camera fov = fov, aspect 1.0, near 1, far farPlane; squarePixels: aspect = panel width / height.
- Horizontal extent `tan(fov x 0.5 x 0.017453292)` x near; vertical = that / aspect (aspect clamped to >= 1/1024).
- Kill fx panels: ParticleScenePanel cameraOrigin 0 600 127, lookAt 0 0 127, fov 41; .UiParticlePanelAmmoCenter 900 x 500, bottom centre, translate 0 16, additive: a square 41 degree view stretched over 900 x 500.
- wash-color: colour over the panel's pixels, their alpha kept.

## Styles (hudhealthammocenter.vcss)

- CSGOHudHealthAmmoCenter 180 tall, bottom, margin-bottom 16.
- .hud-HA__kills 150 x 300 centred, translate(0, 52).
- .hud-HA__kill-flag full height, translate(0, 42) until shown; transform transition 0 s (.animate 0.2 s ease-in-out).
- .kill-flag-svg-size 152 tall centred; fan transforms per NumKills (vcss 1045-1125: up to -24 / +24 degrees).
- @keyframes on-kill (brightness 6, 6 at 30 %, 1), 0.7 s ease-out, on the newest card's .animate, the extra card's and the bar's HUD--on-kill.
- on-kill-spotlight (0, 0.2 at 1 %, 0.2 at 30 %, 0) on the 36 x 100 spotlight.
- Each card: world-blur hudWorldBlur gaussian(2,2,2) behind; the team-washed bluedots_large pattern (0.2) through kill_mask. scrimcomp2v2 variants exist.

## Unread

- 18093fe70's other duties.
