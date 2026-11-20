# The spectators' xray: the glow through walls and the grenade trails

What a dead player (or a caster) sees that the living don't: living pawns outlined through walls (`spec_show_xray`)
and a flying grenade's path (`particles/entity/spectator_utility_trail.vpcf`). Addresses are **client_20261015.dll**
(Ghidra `/client_20261015.dll`) unless marked; the 2026-11-05 build has the trail's string referenced three times
(0x1807c3efc, 0x1807c9e0b, 0x18084bb82: the third is new and unread). The port: src/cs2web/player/spec-xray.js (the
rules), client/fx/nade-trails.js (the trail), client/fx/spec-xray-view.js + client/fx/outlines.js (the glow).

## The grenade trail: C_BaseCSGrenadeProjectile 1807c81c0 (param_1 the projectile, param_2 "force end")

Fields (schema, client): `m_bCanCreateGrenadeTrail` +0x12fd, `vecLastTrailLinePos` +0x12ec, `flNextTrailLineTime`
+0x12f8, `m_nSnapshotTrajectoryEffectIndex` +0x1300 (-1 none), `m_hSnapshotTrajectoryParticleSnapshot` +0x1308,
`m_arrTrajectoryTrailPoints` +0x1310 (CUtlVector<Vector>: count +0x1310, memory +0x1318, alloc +0x1320),
`m_arrTrajectoryTrailPointCreationTimes` +0x1328 (CUtlVector<float>), `m_flTrajectoryTrailEffectCreationTime` +0x1340.
Called from 1807c7070 and 1807dfdb0 (not read: when it runs).

1. +0x12fd off: return. param_2, or the abs origin (18021c3f0) equal to +0x12ec: +0x12fd = 0 (this call goes on).
2. The pawn's simulation time (entity +0x10 +0x38 through 18075d250) below +0x12f8 with +0x12fd still on: return.
3. t = `sv_grenade_trajectory_prac_trailtime` (handle 0x1824c6ee0). Shown (bVar16) = 180ce2420 (a caster: below) or
   t > 0, else: the grenade's m_iTeamNum (+999) 2 / 3, the local pawn (180c7c160) not alive (vfn 0x4e8), observing
   (18094dc30: its observer services +0x1308, vfn 0xf0 mode != 0) and on the grenade's team. t <= 0 and shown: t =
   `sv_grenade_trajectory_time_spectator` (0x1824c6ed0; registered 0.0, 0..8, flags 0x282000; server 1800b43e0 the same;
   **gamemode_competitive.cfg line 81 and gamemode_rush.cfg set 4**, no other cfg).
4. t > 0 or the system made: the first time, +0x1340 = curtime (PTR_DAT_182230090 +0x30), the system
   (1807c88e0, attach 8) and CP 16 = (r, g, b) as floats: CT (114, 155, 221), else (224, 175, 86) (FUN_180a11f30).
   Every time: CP 3 = (t, 1.1, shown and spec_show_xray ? 1 : 0). The snapshot made once (mgr vfn 0x148, 1807c4a50,
   set on CP 0: 180a12420). The origin appended to +0x1310, curtime - +0x1340 to +0x1328; past 0x3ff each drops its
   oldest (memmove 0x3000 / 0x1000 bytes: 1024 kept). The snapshot filled (mgr vfn 0x150) from descriptor slot 0 =
   the points (position) and slot 17 = the times (creation time). The projectile's glow (CGlowProperty at +0xde8):
   type 3 when shown, +0x12fd on and spec_show_xray, else 0 (180ba9430 / 180bb0320), colour the team's with alpha 0xcc
   (180bb02a0).
5. +0x12ec = the origin; +0x12f8 = the simulation time + 0.05.

The vpcf (pak01, decompiled: `lasers-bake --decompile`): C_OP_MaintainEmitter (1, snapshot CP 0: the snapshot's count),
C_INIT_InitFromCPSnapshot (position), lifetime x CP 3.x, radius 5 x CP 3.y, alpha2 = curve(PF_TYPE_PARTICLE_NUMBER: 0,
0.72 at 2, 1 at 5), alpha by age (curve), radius in 0..0.5 / out 0.5..1 of the age, radius x curve(particle number
normalized), C_OP_EndCapTimedDecay 10, C_OP_DifferencePreviousParticle; three C_OP_RenderRopes: beam_cable (overbright
3, GameOverlay), beam_hotwhite (add, overbright 2, GameOverlay), beam_flame (bloom pass only); colour scale CP 16 x
0.0035, alpha scale CP 3.z, radius scale 0.5. No decay operator: a particle past its life stays (alpha 0) until the
system stops.

**particles.dll 2026-11-12 (md5 b10c5654) 0x18006fac5**, PF_TYPE_PARTICLE_NUMBER (the case before _NORMALIZED's
0x18006fb34): when the stage (vfn 0xd0 of [rbp+0xa08]) is 2 (initializers) the value is coll+0x88 + coll+0x94 + block x
4 + lane, else block x 4 + lane (the particle's index); lanes 0..3 from xmm6. Ported in fx/particles/inputs.js (coll+0x94
taken as the batch offset, as evenIndex). It read 0 before, which zeroed the trail's alpha2 and so its ropes.

## The glow: FUN_180c9a3a0 (a pawn's glow each frame) and its rules 0x181c8cb58

180c9a3a0 (param_1 +0x38 the target pawn, the local pawn 18096a8f0(0)) walks the rule list {180c7d290, 180c7d380, 0};
the first that answers sets the glow (CGlowProperty at pawn +0x1bd x 8) type 3, else type 0. A rule fills: rgb,
start alpha (param_4, the caller passes the last alpha +0x48), end alpha (param_5, 1.0 in), start / end time
(param_6 / 7), interpolate (param_8). The alpha: interpolated (now - start) / (end - start) between them when end >
start and now > start, else the end's; the colour bytes x 255, alpha x 255. The pawn's children (weapons) get the
same type and colour.

- 180c7d290: an observer-mode / spotted rule (FUN_1804ffb20 on 0x1821fffd0, convar 0x182570df0 == 3): white, 0.8 or
  0.6. Not ported (not the xray).
- **180c7d380, the xray**: `spec_show_xray` (handle 0x182570e48, registered 1, flags 0x80080) 0: no. The local pawn:
  an observer pawn (vfn 0xac0) in mode 2 (180853840) looks through its target (1808538e0); a player pawn (vfn 0xab8 not
  set: none); that pawn not alive (vfn 0x4e8): no. 180cb2100 set: no. The target the observer watches in-eye: white
  only for a weapon state (param_2[0x261] vfn 0x180 == 2), else no. Not a caster (180ce2420): the local pawn alive: no;
  not observing (18094dc30): no; an enemy (1808d9120) under `mp_forcecamera` (0x1825510d0) != 0: no. The colour:
  `mp_teammates_are_enemies` (0x1824bcf88) (0.949, 0.459, 0.459), else CT (0.447, 0.608, 0.867), T (0.878, 0.686,
  0.337), else no. A replay's selected player (DAT_1825603a0, 180baa650) white (not ported: HLTV). Then the noise:
  E = max(m_flEmitSoundTime +0x1ea0, m_flEmitSoundTime_Client +0x1ea4) (180c56d50), silent = spec_glow_silent_factor
  (0.4), spike = spec_glow_spike_factor (1.2), full = spec_glow_full_time (1.0), decay = spec_glow_decay_time (2.0),
  st = spec_glow_spike_time (0.0) (registrations 0x1800e70d0..0x1800e7400, handles 0x182570df8 / e08 / e18 / e28 / e38):

      now < E + full + decay:
        now < E + full:
          now < E + 2st:
            now < E + st:  now < E: end 1    else: (now, 1.6666 -> now + st, spike)
            else:          (E + st, spike -> E + 2st, 1)
          else:            (E + 2st, 1 -> E + full, 1)
        else:              (E + full, 1 -> E + full + decay, silent)
      else:                end silent
      both alphas x 0.6

- 1808d9120 (enemies): the local player info (180c19ee0: +0 none, +8 its controller, +0xc its team); none: no; the
  same controller: no; mp_teammates_are_enemies: yes; else the target's team (1808cca40) != the local's.
- 180ce2420 (a caster): `force_spectator_only_tools` (0x18257b368), the controller's m_bIsHLTV (+0x6f0; +0x790 picks
  DAT_1825603a0 instead), or an observed caster pawn (1808d9430 with DAT_1825651d0, 180769bb0). Ours: an admin's ghost.

**m_flEmitSoundTime** (server_20261105 pawn +0x14c4): EmitSoundByHandle 180f698d0 sets it to curtime when the emitter
is a player pawn (vfn 0x558), or an entity whose owner (1803d9790) is one, and the event has the param token 0x442583
= `public.display_broadcast` (soundevents' display_broadcast; false in every stack); cleared at spawn (180249530);
also written at 1803418e5 / 180341966 (unread). tools/broadcast-sounds.mjs lists the events (649 of 21541,
data/broadcast-sounds.js).

## The glow pass: FUN_1811faa40 (built by the pipeline builder 1811d9d30 when r_csgo_enable_glows, after LetterboxBottom)

Convars: `r_csgo_enable_glows` 1 (handle 0x1825f6240), `r_csgo_outline_glow_scaledenom` 1 (0x1825f6250; 1 / 2 / 4 the
solid target's divisor), `glow_outline_width` 6.0 (0x1825f5e10, "Width of glow outline effect in screen space": set on
the Blur Y layer as attribute 0x39dda75a, which blur.vfx doesn't read). Materials (static init 0x1801295b0): 0x1825f6c50
`materials/dev/csgo_glow_blur.vmat` (blur.vfx F_GAUSSIAN_KERNEL 1, F_SRGB_READ 1), 0x1825f6c48
`materials/dev/bicubicfilter_invalphablended.vmat` (core pak: sampletexture_bicubic.vfx F_ALPHA_BLEND, F_INVERT_ALPHA),
`materials/dev/downsample_outlineglows.vmat`; the objects `materials/dev/glowproperty.vmat` (solidcolor.vfx F_BLEND_MODE 1,
F_DISABLE_STENCIL_WRITE, F_DISABLE_Z_WRITE, F_WRITE_TO_DESTALPHA). `materials/dev/outlines.vmat` (outlines.vfx, an edge
finder) is in pak01 but nothing in client.dll names it.

1. "Glows: Render Objects Solid Color" into `glowColorHalf` (size / scaledenom; quarter-size when 4), layer token
   0xacbff579 (the glow helper objects, +0xc4): solidcolor PS out = (tint x vertex colour.rgb x per-view c18, vertex
   alpha); blend One / One on RGB, SrcBlendAlpha Zero (DstBlendAlpha left at the default: Zero, from the references'
   flat fills), so alpha 0 where drawn.
2. "Glows: DownsampleToQuarter" (when scaledenom != 4) into `glowColorQuarter`: D_DOWNSAMPLE_MODE = scaledenom != 2:
   mode 1 four bilinear taps at +-1 texel around fragCoord x invDim x 4, mode 0 one tap at x 2.
3. "Glows: Blur X" into `glowColorQuarter2` and "Blur Y" back: the 7-wide kernel: 5 bilinear taps at -3, -1.182425, 0,
   1.182425, 3 texels, weights 0.004433, 0.296042, 0.39905, 0.296042, 0.004433 (blur.vfx s6). (The pass call also gets
   13 gaussian weights, the table 0x181d2a3d0 / 0.179016, which this shader doesn't take.)
4. "Glows: Render Objects into Stencil" ("Depth" target, no colour): the objects again. The layer's depth state isn't
   read; the port marks the whole silhouette (the reference shots: a rim, not a fill, round a pawn behind a wall).
5. "Glow MSAA Resolve", then "Glows: Stencil To Screen" onto the frame, a render-state override (0x1824d7640) for the
   stencil test: sampletexture_bicubic (cubic B-spline as 4 bilinear taps, 1/6 matrix), RenderState SrcBlend One,
   DstBlend SrcAlpha (F_INVERT_ALPHA), RGB writes only: frame = glow.rgb + frame x glow.a outside the stencil.

The colour: CGlowProperty +0x40 (m_glowColorOverride) / 255 (0x180ba92f0; +0x44 flashing: x (0.7 + 0.3 sin(20 t))),
copied to the glow helper scene object +0xd0 (0x180b78090, the desc 0x182233d10, vtable 0x181c5fb70); the draw
(0x180b56b20) scales alpha by the glow range fade and skips alpha 0, multiplies RGB by m_flGlowBackfaceMult (+0xf8)
for a viewer behind the model's facing, and packs linear to sRGB bytes (0x181749eb0). solidcolor's vertex shader turns
them back to linear.

Port: world/glow-pass.js (half-size solid target + one bilinear tap = CS2's 4 x 4 box; the mask in the HDR target's
alpha for the final blit, which can't read a stencil; the composite folded into world/render.js's blit, in linear,
after the vignette). world/peers.js keeps a glowing body posed (not PVS-culled).

## Unread

1807c7070 / 1807dfdb0 (when the trail runs), 1807c4bf0 (its end: the glow off, the system stopped?), 0x18084bb82
(2026-11-05's third reference), 180c7d290's convar 0x182570df0, the in-eye weapon state, CS2's glow pass itself (the
outline shader), the GameOverlay layer's depth rule.
