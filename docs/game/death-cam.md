# The death camera (client_20261015, server_20261105)

client_20261015.dll (image base 0x180000000) unless said; read 2026-11-16. The port: web/src/cs2web/client/core/death-cam.js
(the camera), death-cam-post.js (the post weights and the audio fade), checked by death-cam-test.mjs against
tools/re/game/deathcam_oracle.py (client.dll's own maths under Unicorn with the real tier0: 8000 cases, bit for bit). The
timing (how long you stay on your pawn, the skip) was already in src/cs2web/sim/deathcam.js (docs/game/armsrace.md).

## 1. Where it runs

- **CViewRender::SetUpView** (vfn 0x98 of CViewRender, vtable 0x181c7d1f8: 180c1a710) -> the client mode's view setup
  (ClientModeCSNormal vfn 0x78, 180b9c970) -> the local controller's camera services (controller +0x1328) **vfn 0x108**
  (180882a00: the menu camera 180cb2100 when one is up, else 180a64570) -> the pawn's observer services (pawn +0x1308)
  vfn 0x110 when its mode (vfn 0xf0) is not 0, else the camera services' **vfn 0x110 = 180882530**
  (CCSPlayer_CameraServices, vtable 0x181c0d518 slot 34).
- The view's origin / angles (+0x4a0 / +0x4b8 of the per-slot view, CViewRender +0x10 + slot x 0x990) go in as the
  CalcView's in/out arguments and are never reset between frames (only CViewRender's init writes the angles,
  180c1a3a0): CalcView starts from last frame's shown view. The port keeps `shownView` (game.js render).
- **180882530**: pawn (+0x38) not alive (vfn 0x4e8) and curtime (18075d250) - m_flDeathTime (pawn +0x1458) > 0.0625
  (0x181c0e8ac) -> **the death cam 1808818a0**, return. Else m_flDeathCamTilt (+0x2b0) = 0, m_hDeathCamBounds (+0x2b4)
  = -1, m_bDeathCamBoundsSearched (+0x2b8) = 0, and the eye path (vfn 0x568 EyePosition, 0x570 EyeAngles, ...).
- Which pawn: the observer services' validity check **1808587c0** keeps your own pawn (handle at services +0x4c)
  valid until m_flDeathTime + spec_freeze_deathanim_time + spec_freeze_time + spec_freeze_traveltime (cvar objects
  0x18252b7b8 / 0x18252b788 / 0x18252b798); another player's dead pawn is never a valid target, so only your own
  death has a death cam.

## 2. The camera (1808818a0)

Camera services fields (schema): m_flDeathCamTilt +0x2b0, m_hDeathCamBounds +0x2b4, m_bDeathCamBoundsSearched +0x2b8
(beside m_iFOV +0x298). Pawn: m_flDeathTime +0x1458, m_qDeathEyeAngles +0x1da8 (pitch, yaw, roll; roll at +0x1db0),
m_hOwnerEntity +0x520.

1. bone = 180952970(pawn, 0x9b0e3fd): the bone index by CUtlStringToken ("pelvis"); -1 (or no pawn) -> tilt = 0.
2. tilt == 0 (ucomiss, so not for NaN) -> tilt = RandomFloat(4, 10) (tier0 import 0x181aad678; 4 at 0x181ac6088,
   10 at 0x181ad0f70), RandomInt(0, 1) (0x181aad4a8) != 0 -> tilt negated (xorps -0). With no pelvis the tilt is
   drawn again every frame.
3. s = **180889e20**(curtime - m_flDeathTime) (subss straight, not 18015c5e0): t = (e - 0.0625) / spec_freeze_traveltime
   (0.3, read 180160b10: [obj + 8] + 0x58); t = clamp(t, 0, 1) (18015a220); u = t x 0.5 + 0.5;
   r = ((u x 3) x u - ((u + u) x u) x u) - 0.5; return r + r.
4. roll = m_qDeathEyeAngles.roll + (((tilt - 0) x s) + 0); dist = (death_chase_distance - 16) x s + 16:
   **death_chase_distance** (object 0x18252dee0, registered 1800ae000: 76, flags 2 = development only: always 76).
5. The centre o: bone >= 0 -> 18093f490(pawn, bone) (the skeleton's world position of the bone) + **180ac12b0()**
   +0x60 (the game rules' vfn 0x118 GetViewVectors, else the static g_CSViewVectors 0x182557c50: m_vDeadViewHeight
   at +0x60 = (0, 0, 14), set by 1800c3fd0), per axis bone + view; no bone -> the incoming view origin.
6. Water under the centre: TraceLine **180200f20**(0x182227058, start, end, filter, trace) from (o.x, o.y, (o.z - 11) +
   64) to (o.x, o.y, o.z - 11); the filter: vtable 0x181ad4838, interacts-with 0x18000 (water 0x8000 | slime 0x10000),
   collision group 5, flags (b & 0xc9) | 0x49 | 4, +0x40 = 0 (no entity iteration), entity ids 1809dd600(pawn) and its
   owner's (m_hOwnerEntity, -1 when the collision property's +0x5a & 4), hierarchy 1809ea740(pawn). **DidHit
   180360720**: fraction (+0xac) < 1 or start solid (+0xbb). Hit -> o.z = endpos.z (+0x8c) + 11 (0x181c0e8f0).
7. fwd = AngleVectors(the incoming angles) (181740910); cam = (-dist) x fwd + o (per axis: (-dist x f) + o).
8. Water under the camera: the same line from (c.x, c.y, (c.z - 10) + 64) to (c.x, c.y, c.z - 10). Hit -> d = cam - o,
   h = (endpos.z + 10) - o.z; when 0 > d.z and h > d.z and 0 >= h: d.x, d.y x= h / d.z; cam = (o.x + d.x, o.y + d.y,
   h + o.z) (the hit always sets cam.z).
9. **1808a5910**(out, pawn, &o, &cam, 9.0): a box ray (-9, -9, -9) .. (9, 9, 9) (18036ddb0) from o to cam, filter
   interacts-with 1 (solid), group 5, flags 0x49, +0x40 0, the pawn's ids (180a1a000 TraceShape); fraction (+0xac)
   >= 1 -> cam itself, else the endpos (+0x84). (180b140c0(0) / 180b072b0 bracket it.) The result is the origin.
10. Angles = (m_qDeathEyeAngles.pitch, .yaw, roll); FOV = the services' vfn 0x118.
11. point_deathcam_bounds (C_PointDeathcamBounds, client-only; keyvalues box_mins / box_maxs / lerp_distance: m_vBoxMins
    +0x600, m_vBoxMaxs +0x60c, m_flLerpDistance +0x618): once a death (+0x2b8), the first in 1809dfb70's classname
    walk whose box holds the origin (**180ce3c50**: 1801e2ec0 WorldToEntitySpace, then mins <= l <= maxs per axis) is
    kept in +0x2b4. Each frame with one: origin = **180ce2950** (l = WorldToEntitySpace(origin), per axis
    maxss(mins, minss(l, maxs)), back: zero abs angles (18015c580 against 0x181ac29d8) -> scale x l + abs origin, else
    the transform's rotation (t = 2 q x l, q x t + (w t + l)) x scale + position); moved = |clamped - origin|
    ((dy^2 + dz^2) + dx^2); moved > 0, lerp > 0 and a pelvis -> look = VectorAngles(pelvis - origin) (181742a00, the
    bone's raw position, without the dead view height), k = **1817438a0**(clamp(moved / lerp, 0, 1)) =
    (1 - V_cosf(x x 3.1415927)) x 0.5; pitch / yaw = **AngleDiff 18173cb10**(look, death angle) x k + death angle.
    No map we bake has one (de_*, cs_*, ar_*, ze_* checked 2026-11-16).

**1801e2ec0** WorldToEntitySpace: zero abs angles: (p - abs origin) x (1 / scale). Else the node's CTransform
(180218900: position, scale +0xc, quaternion +0x10): q' = q x (-1, -1, -1, 1) (0x1822903c0), normalised lane-wise by
sqrt(dpps 0xff) (a zero length as 2^-23, 0x182290350); k = 1 / scale (scale 0 -> 2^23 0x181acaf44, scale 1 -> no
multiply); inverse position = -(rotate(q', position) x k); result = rotate(q', p) x k + inverse position, with
rotate(q, v) = q x t + (v + w t), t = 2 (q x v) (each cross lane a x b - c x d).

**181742a00** VectorAngles: y == 0 and x == 0 -> (z > 0 ? 270 : 90, 0, 0); else yaw = V_atan2f(y, x) x 57.2957764,
+ 360 when below 0; pitch = V_atan2f(-z, sqrtss(x x + y y)) x 57.2957764, + 360 when below 0; roll 0.
**18173cb10** AngleDiff(dest, src): d = V_fmodf(dest - src, 360); dest > src: d >= 180 -> d - 360; else d <= -180 -> d + 360.

## 3. The server's half (server_20261105)

- Event_Killed's part **180208400**: m_flDeathTime (pawn +0xc7c) = curtime, m_qDeathEyeAngles (+0x1454) = vfn 0x5f0
  (CCSPlayerPawn: 180b4f890: a vehicle's (+0xb48) or the move parent's composition (1803d95d0), else vfn 0x5f8, the
  pawn's m_angEyeAngles +0x15b4).
- **PlayerKilled 180912130** sets m_bKilledByHeadshot (+0x14f8) from the kill's headshot; Spawn (180249530) clears it.
- Ours: game.js kill() keeps the tick, [pitch, yaw, 0] (our pawns have no parent or vehicle) and the headshot;
  snapshots.js deathSnap sends `dth` with your own state while dead.

## 4. The overlays and the audio fade (ClientModeCSNormal::Update)

**180d0c420** (ClientModeCSNormal vfn 0x130, every frame) -> **180d0d540**; object fields (the client mode):

| field | overlay (.vpost under lighting/postprocessing/, table 1800f0e50) | weight |
|---|---|---|
| +0x118 | effects/in_buy_menu | 1 when the local pawn (180c7c160) is alive (vfn 0xab8) and has m_bIsBuyMenuOpen (+0x15ea) |
| +0x11c | effects/round_end_via_bombing | 0 every frame in this build: the step 1/64 toward 1 needs the client mode's +0x9c == 3, an observed pawn and 18094dc60 false, but 18094dc60 is `mov al, 1; ret` (post-layers.md 4) |
| +0x120 | effects/death_cam_phase1 | below |
| +0x124 | effects/death_cam_phase1_low_violence | the same, under the low-violence launch option (180aca8d0: CommandLine token 0xcdbd1292) |
| +0x128 | effects/death_cam_phase2 | below |
| +0x12c | effects/hltv_replay_fade | 1821fffd0's value |
| +0x130 | effects/hltv_replay | spec_replay_colorcorrection (0.5, 0x182579310) while 1804ffb20 |

(cc_freeze_ct / cc_freeze_t lead the table, set elsewhere.) Each weight goes to the post-processing state of the view
(18254eae8 vfn 0 -> vfn 0x68(slot)) vfn 0x48(the overlay's handle +0xe0 .. +0x110, weight); all 0 under
**cl_disable_postprocessing** (0x182579320, 0) or with a menu camera (180cb2100).

The dead pawn **180c7ae00**: the local controller (18096a8f0(0)), connected (vfn 0x4f0): its pawn, or when it observes
(vfn 0xac0) in the eye (180853840 == 2) the observed pawn (1808538e0); returned only when that pawn is dead.

- dead pawn: **cl_instant_death_anim** (0x182579330, 0) -> phase1 = 1. Else e = curtime - m_flDeathTime;
  a = clamp(e x 4, 0, 1) (1801587b0); m_bKilledByHeadshot (pawn +0x1ec5) ? x = e : x = e - (spec_freeze_time - 0.5);
  p2 = clamp(x + x, 0, 1); phase1 = max(a, phase1) (1801b9c30); phase2 = p2, unless mp_forcecamera (0x1825510d0) is 1,
  no C_PlantedC4 exists (0x18252d104: the count, C_PlantedC4's constructor 180cab7f0 adds one) and 18089c6f0(the pawn's
  controller (pawn +0x1560), the local team) is true -> phase2 steps toward 0.
- **18089c6f0**(controller, team): the controller is on the team with a pawn (+0x92c), and no other controller of the
  team (180acac70 over maxclients) has a living pawn or a pawn that died later (m_flDeathTime compared, 1801befe0):
  the last of the team to die.
- no dead pawn: the trueview replay (CPrediction 0x182565620, 180bdb2d0: +0xd4 set, +0x50 == 1, +0x58's +0x10 > 1)
  -> phase1 = 1 (0.4 with **cl_trueview_show_doa_predictions**, 0x182565860, 1); else phase1 = 0 and phase2 steps.
- the step: phase2 < 0 -> min(0, phase2 + 0.03125); > 0 -> max(0, phase2 - 0.03125) (0x181ad0f60).
- The phase-1 key not in use is zeroed first (+0x120 or +0x124).

**180d0ef50** DeathFadeLayer: T1 = max(cl_deathcam_audio_mix_phase1_fade_time (2, 0x182579350), 0.001), T2 =
max(_phase2_fade_time (0.4, 0x182579370), 0.001); without **cl_disable_deathcam_audio_mix_fade_out** (0x182579340, 0):
phase1 > 0 and phase2 <= 0 -> +0x158 = 0, start +0x154 = curtime if 0, p1 = clamp((curtime - start) / T1, 0, 1);
phase2 > 0 -> the same start, p1 = 1, p2 = clamp((curtime - start) / T2, 0, 1) (the start is phase 1's: phase 2's
progress counts from it). Neither, with +0x15c > 0 and both phases <= 0: +0x154 / +0x158 = 0. v = minss(_phase2_fade_amount
(0.5, 0x182579380) x p2 + _phase1_fade_amount (0.15, 0x182579360) x p1, 1); changed -> +0x15c = v, the soundsystem's vfn
0x150(DeathFadeLayer, v) (the layer's handle from vfn 0x148 once).

The port: death-cam-post.js computes all three weights and the fade each frame (game.js deathPostFrame; the dead pawn
is yours while the death cam holds it, the hold flag comes from the server); DeathFadeLayer is applied (audio.js
deathMix). The overlays are drawn (2026-11-17): game.js hands the weights to world/tonemap.js, whose
CPostProcessingState port (world/post-layers.js) composes them over the volume's layer as materialsystem2 does; the
composition, the groups and the .vposts' contents are in [post-layers.md](post-layers.md). Not drawn yet: the local
contrast death_cam_phase1 carries (post-layers.md "Unread").

## Unread

- Local contrast's input (post-layers.md "Unread").
- The name of the low-violence launch option (token 0xcdbd1292 isn't any string in client or engine2).
