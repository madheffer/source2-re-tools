# Spectator xray: glow through walls, grenade trails

client_20261015 unless marked; server_20261105; particles 2026-11-12 (md5 b10c5654). particles/entity/
spectator_utility_trail.vpcf (pak01); gamemode_competitive.cfg, gamemode_rush.cfg. In client_20261105 the trail's
string has three references (0x1807c3efc, 0x1807c9e0b, 0x18084bb82: the third new, unread).

## Functions

| Address | Module | What |
|---|---|---|
| 1807c81c0 | client | C_BaseCSGrenadeProjectile trail (projectile, force end); called from 1807c7070 and 1807dfdb0 |
| 18021c3f0 | client | abs origin |
| 18075d250 | client | simulation time (entity +0x10 +0x38) |
| 1807c88e0 | client | creates the system (attach 8) |
| 180a11f30 | client | set CP (floats) |
| 1807c4a50 | client | the snapshot (mgr vfn 0x148), set on CP 0 by 180a12420; filled by mgr vfn 0x150 |
| 180ba9430 / 180bb0320 | client | glow type |
| 180bb02a0 | client | glow colour |
| 180c9a3a0 | client | a pawn's glow each frame (param_1 +0x38 the target; local pawn 18096a8f0(0)); rules 0x181c8cb58 = {180c7d290, 180c7d380, 0} |
| 180c7d290 | client | observer-mode / spotted rule (1804ffb20 on 0x1821fffd0, convar 0x182570df0 == 3): white, 0.8 or 0.6 |
| 180c7d380 | client | the xray rule |
| 180853840 / 1808538e0 | client | observer mode / target |
| 180cb2100 | client | set: the xray rule answers no (unread) |
| 180ce2420 | client | a caster |
| 18094dc30 | client | observing (observer services +0x1308, vfn 0xf0 mode != 0) |
| 1808d9120 | client | enemies |
| 180c19ee0 | client | local player info (+0 none, +8 controller, +0xc team) |
| 1808cca40 | client | target's team |
| 180baa650 | client | replay's selected player (DAT_1825603a0) |
| 180c56d50 | client | E = max(m_flEmitSoundTime, _Client) |
| 1808d9430, 180769bb0 | client | observed caster pawn (with DAT_1825651d0) |
| 180c7c160 | client | local pawn |
| 1811faa40 | client | the glow pass (built by 1811d9d30 when r_csgo_enable_glows, after LetterboxBottom) |
| 0x1801295b0 | client | static init of the glow materials |
| 0x180ba92f0 | client | glow colour = m_glowColorOverride / 255 |
| 0x180b78090 | client | copies it to the glow helper scene object +0xd0 (desc 0x182233d10, vtable 0x181c5fb70) |
| 0x180b56b20 | client | the helper's draw |
| 0x181749eb0 | client | linear -> sRGB bytes |
| 0x18006fac5 | particles | PF_TYPE_PARTICLE_NUMBER (case before _NORMALIZED's 0x18006fb34) |
| 180f698d0 | server | EmitSoundByHandle (sets m_flEmitSoundTime) |
| 1803d9790 | server | owner |
| 180249530 | server | spawn (clears it) |
| 1803418e5 / 180341966 | server | other writers (unread) |
| 1800b43e0 | server | sv_grenade_trajectory_time_spectator registration |

## Fields

| Offset | Field |
|---|---|
| projectile +999 | m_iTeamNum |
| projectile +0xde8 | CGlowProperty |
| projectile +0x12ec | vecLastTrailLinePos |
| projectile +0x12f8 | flNextTrailLineTime |
| projectile +0x12fd | m_bCanCreateGrenadeTrail |
| projectile +0x1300 | m_nSnapshotTrajectoryEffectIndex (-1 none) |
| projectile +0x1308 | m_hSnapshotTrajectoryParticleSnapshot |
| projectile +0x1310 | m_arrTrajectoryTrailPoints (CUtlVector<Vector>: count +0x1310, memory +0x1318, alloc +0x1320) |
| projectile +0x1328 | m_arrTrajectoryTrailPointCreationTimes (CUtlVector<float>) |
| projectile +0x1340 | m_flTrajectoryTrailEffectCreationTime |
| pawn +0x1bd x 8 | CGlowProperty |
| pawn +0x1ea0 / +0x1ea4 | m_flEmitSoundTime / m_flEmitSoundTime_Client |
| pawn param_2[0x261] | weapon state (vfn 0x180 == 2: white in-eye) |
| controller +0x6f0 / +0x790 | m_bIsHLTV / picks DAT_1825603a0 |
| server pawn +0x14c4 | m_flEmitSoundTime |
| CGlowProperty +0x40 / +0x44 / +0x48 / +0xf8 | m_glowColorOverride / flashing / last alpha / m_flGlowBackfaceMult |
| PTR_DAT_182230090 +0x30 | curtime |

## Constants

| Value | What |
|---|---|
| sv_grenade_trajectory_prac_trailtime | handle 0x1824c6ee0 |
| sv_grenade_trajectory_time_spectator | 0.0, 0..8, flags 0x282000 (0x1824c6ed0); gamemode_competitive.cfg line 81 and gamemode_rush.cfg set 4 |
| spec_show_xray | 1, flags 0x80080 (0x182570e48) |
| spec_glow_silent_factor (silent) / spec_glow_spike_factor (spike) / spec_glow_full_time (full) / spec_glow_decay_time (decay) / spec_glow_spike_time (st) | 0.4 / 1.2 / 1.0 / 2.0 / 0.0 (registrations 0x1800e70d0..0x1800e7400, handles 0x182570df8 / e08 / e18 / e28 / e38) |
| mp_forcecamera | 0x1825510d0 |
| mp_teammates_are_enemies | 0x1824bcf88 |
| force_spectator_only_tools | handle 0x18257b368 (the object is 0x18257b360, flashbang.md: a cvar's handle is the qword 8 bytes after its object) |
| r_csgo_enable_glows | 1 (0x1825f6240) |
| r_csgo_outline_glow_scaledenom | 1 (0x1825f6250; 1 / 2 / 4 the solid target's divisor) |
| glow_outline_width | 6.0 (0x1825f5e10, "Width of glow outline effect in screen space"; attribute 0x39dda75a on Blur Y, unread by blur.vfx) |
| trail CP 16 | CT (114, 155, 221), else (224, 175, 86) |
| xray colours | teammates-are-enemies (0.949, 0.459, 0.459), CT (0.447, 0.608, 0.867), T (0.878, 0.686, 0.337) |
| 0xcc | the projectile glow's alpha |
| 0x3ff / 1024 | trail points kept (memmove 0x3000 / 0x1000 bytes) |
| 0.05 | trail line interval |
| 0x442583 | param token `public.display_broadcast` (649 of 21541 sound events have it) |
| 0xacbff579 | layer token of the glow helper objects (+0xc4) |
| 0x1824d7640 | stencil render-state override |
| 0x181d2a3d0 / 0.179016 | 13 gaussian weights (passed, unused by this shader) |

Materials: 0x1825f6c50 `materials/dev/csgo_glow_blur.vmat` (blur.vfx F_GAUSSIAN_KERNEL 1, F_SRGB_READ 1), 0x1825f6c48
`materials/dev/bicubicfilter_invalphablended.vmat` (core: sampletexture_bicubic.vfx F_ALPHA_BLEND, F_INVERT_ALPHA),
`materials/dev/downsample_outlineglows.vmat`; objects `materials/dev/glowproperty.vmat` (solidcolor.vfx F_BLEND_MODE 1,
F_DISABLE_STENCIL_WRITE, F_DISABLE_Z_WRITE, F_WRITE_TO_DESTALPHA). `materials/dev/outlines.vmat` (outlines.vfx, an edge
finder) is in pak01 but unnamed in client.dll.

## The grenade trail 1807c81c0

1. +0x12fd off: return. Force end, or the abs origin equal to +0x12ec: +0x12fd = 0 (this call goes on).
2. Simulation time below +0x12f8 with +0x12fd on: return.
3. t = prac_trailtime. Shown = 180ce2420 or t > 0, else: the grenade's team 2 / 3, the local pawn not alive (vfn
   0x4e8), observing and on the grenade's team. t <= 0 and shown: t = time_spectator.
4. t > 0 or the system made: the first time +0x1340 = curtime, the system and CP 16. Every time CP 3 = (t, 1.1, shown
   and spec_show_xray ? 1 : 0). The snapshot made once. Origin appended to +0x1310, `curtime - +0x1340` to +0x1328;
   past 0x3ff each drops its oldest. The snapshot filled from descriptor slot 0 = points (position) and slot 17 =
   times (creation time). Projectile glow type 3 when shown, +0x12fd on and spec_show_xray, else 0; team colour, alpha
   0xcc.
5. +0x12ec = origin; +0x12f8 = simulation time + 0.05.

The vpcf: C_OP_MaintainEmitter (1, snapshot CP 0: its count), C_INIT_InitFromCPSnapshot (position), lifetime x CP 3.x,
radius 5 x CP 3.y, alpha2 = curve(PF_TYPE_PARTICLE_NUMBER: 0, 0.72 at 2, 1 at 5), alpha by age (curve), radius in
0..0.5 / out 0.5..1 of the age, radius x curve(particle number normalized), C_OP_EndCapTimedDecay 10,
C_OP_DifferencePreviousParticle; three C_OP_RenderRopes: beam_cable (overbright 3, GameOverlay), beam_hotwhite (add,
overbright 2, GameOverlay), beam_flame (bloom pass only); colour scale CP 16 x 0.0035, alpha scale CP 3.z, radius scale
0.5. No decay operator: a particle past its life stays (alpha 0) until the system stops.

PF_TYPE_PARTICLE_NUMBER (0x18006fac5): stage (vfn 0xd0 of [rbp+0xa08]) 2 (initializers) -> `coll+0x88 + coll+0x94 +
block x 4 + lane`, else `block x 4 + lane`; lanes 0..3 from xmm6 (coll+0x94 taken as the batch offset).

## The glow 180c9a3a0

1. The first rule that answers sets the glow type 3, else 0. A rule fills rgb, start alpha (param_4: the caller passes
   the last alpha +0x48), end alpha (param_5, 1.0 in), start / end time (param_6 / 7), interpolate (param_8).
2. Alpha: interpolated `(now - start) / (end - start)` when end > start and now > start, else the end's; colour bytes x
   255, alpha x 255. The pawn's children (weapons) get the same type and colour.

### The xray rule 180c7d380

1. spec_show_xray 0: no. The local pawn: an observer pawn (vfn 0xac0) in mode 2 looks through its target; a player pawn
   (vfn 0xab8 not set): none; that pawn not alive (vfn 0x4e8): no. 180cb2100 set: no.
2. The target watched in-eye: white only for a weapon state 2, else no.
3. Not a caster: local pawn alive: no; not observing: no; an enemy under mp_forcecamera != 0: no.
4. Colour by mp_teammates_are_enemies / CT / T, else no. A replay's selected player white.
5. The noise, E = 180c56d50 (max of +0x1ea0, +0x1ea4); silent / spike / full / decay / st the spec_glow_* cvars
   (Constants):

```
now < E + full + decay:
  now < E + full:
    now < E + 2st:
      now < E + st:  now < E: end 1    else: (now, 1.6666 -> now + st, spike)
      else:          (E + st, spike -> E + 2st, 1)
    else:            (E + 2st, 1 -> E + full, 1)
  else:              (E + full, 1 -> E + full + decay, silent)
else:                end silent
both alphas x 0.6
```

- 1808d9120: no local info: no; the same controller: no; mp_teammates_are_enemies: yes; else target team != local.
- 180ce2420: force_spectator_only_tools, the controller's m_bIsHLTV (+0x6f0, schema-checked; the controller's +0x790
  picks DAT_1825603a0 instead), or an observed caster pawn (1808d9430 with DAT_1825651d0, 180769bb0).

m_flEmitSoundTime (server): 180f698d0 sets curtime when the emitter is a player pawn (vfn 0x558) or owned by one, and
the event has `public.display_broadcast` (soundevents' display_broadcast; false in every stack); cleared at spawn.

## The glow pass 1811faa40

1. "Glows: Render Objects Solid Color" into `glowColorHalf` (size / scaledenom; quarter when 4), layer 0xacbff579:
   solidcolor PS out = (tint x vertex colour.rgb x per-view c18, vertex alpha); blend One / One on RGB, SrcBlendAlpha
   Zero (DstBlendAlpha default Zero, as the reference shots' flat fills show): alpha 0 where drawn.
2. "Glows: DownsampleToQuarter" (scaledenom != 4) into `glowColorQuarter`: D_DOWNSAMPLE_MODE = scaledenom != 2: mode 1
   four bilinear taps at +-1 texel around `fragCoord x invDim x 4`, mode 0 one tap at x 2.
3. "Glows: Blur X" into `glowColorQuarter2`, "Blur Y" back: 5 bilinear taps at -3, -1.182425, 0, 1.182425, 3 texels,
   weights 0.004433, 0.296042, 0.39905, 0.296042, 0.004433 (blur.vfx s6; a 7-wide kernel).
4. "Glows: Render Objects into Stencil" ("Depth" target, no colour). Depth state unread; reference shots show a rim,
   not a fill, round a pawn behind a wall.
5. "Glow MSAA Resolve", then "Glows: Stencil To Screen" with 0x1824d7640's stencil test: sampletexture_bicubic (cubic
   B-spline as 4 bilinear taps, 1/6 matrix), SrcBlend One, DstBlend SrcAlpha (F_INVERT_ALPHA), RGB only: `frame =
   glow.rgb + frame x glow.a` outside the stencil.

Colour: m_glowColorOverride / 255 (flashing: x `(0.7 + 0.3 sin(20 t))`) -> helper +0xd0; the draw scales alpha by the
glow range fade and skips alpha 0, multiplies RGB by m_flGlowBackfaceMult for a viewer behind the model's facing, packs
linear to sRGB bytes; solidcolor's vertex shader turns them back to linear.

## Unread

1807c7070 / 1807dfdb0 (when the trail runs), 1807c4bf0 (its end: the glow off, the system stopped?), 0x18084bb82
(client_20261105's third reference), 180c7d290's convar 0x182570df0, the in-eye weapon state, the outline shader,
the GameOverlay layer's depth rule, the stencil pass's depth state.
