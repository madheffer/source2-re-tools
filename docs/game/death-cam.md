# Death camera

client_20261015 (image base 0x180000000) unless said; server_20261105. Timing (how long you stay on your pawn, the skip):
[armsrace.md](armsrace.md). Post layers: [post-layers.md](post-layers.md).

## Functions

| Address | Module | What |
|---|---|---|
| 180c1a710 | client | CViewRender::SetUpView (vfn 0x98, vtable 0x181c7d1f8) |
| 180c1a3a0 | client | CViewRender init (the only writer of the view angles) |
| 180b9c970 | client | ClientModeCSNormal vfn 0x78: view setup |
| 180882a00 | client | camera services (controller +0x1328) vfn 0x108: menu camera 180cb2100 when up, else 180a64570 |
| 180882530 | client | CCSPlayer_CameraServices vfn 0x110 (vtable 0x181c0d518 slot 34) |
| 1808818a0 | client | the death cam |
| 1808587c0 | client | observer services' target validity check |
| 18075d250 | client | curtime |
| 180952970 | client | bone index by CUtlStringToken (pawn, 0x9b0e3fd "pelvis") |
| 180889e20 | client | the camera's ease s(e) |
| 180160b10 | client | float cvar read ([obj + 8] + 0x58) |
| 18015a220 / 1801587b0 | client | clamp |
| 18093f490 | client | bone's world position (pawn, bone) |
| 180ac12b0 | client | view vectors: gamerules vfn 0x118 GetViewVectors, else g_CSViewVectors 0x182557c50 |
| 1800c3fd0 | client | sets g_CSViewVectors |
| 180200f20 | client | TraceLine(0x182227058, start, end, filter, trace) |
| 180360720 | client | DidHit: fraction (+0xac) < 1 or start solid (+0xbb) |
| 1809dd600 / 1809ea740 | client | entity ids / hierarchy for the filter |
| 181740910 | client | AngleVectors |
| 1808a5910 | client | (out, pawn, &o, &cam, 9.0): box ray to the camera |
| 18036ddb0 | client | box ray setup |
| 180a1a000 | client | TraceShape |
| 180b140c0 / 180b072b0 | client | bracket the box ray |
| 1809dfb70 | client | classname walk |
| 180ce3c50 | client | point inside a deathcam bounds box |
| 180ce2950 | client | clamp into the box |
| 1801e2ec0 | client | WorldToEntitySpace |
| 180218900 | client | node CTransform (position, scale +0xc, quaternion +0x10) |
| 18015c580 | client | zero abs angles test (against 0x181ac29d8) |
| 181742a00 | client | VectorAngles |
| 1817438a0 | client | `(1 - V_cosf(x x 3.1415927)) x 0.5` |
| 18173cb10 | client | AngleDiff(dest, src) |
| 180d0c420 -> 180d0d540 | client | ClientModeCSNormal vfn 0x130 (every frame): the overlay weights |
| 180c7ae00 | client | the dead pawn |
| 18096a8f0 | client | local controller (0) |
| 180853840 / 1808538e0 | client | observer mode / target |
| 180c7c160 | client | local pawn |
| 18094dc60 | client | `mov al, 1; ret` |
| 180aca8d0 | client | low-violence (CommandLine token 0xcdbd1292) |
| 1804ffb20 | client | gates the hltv_replay weight |
| 18089c6f0 | client | (controller, team): the last of the team to die |
| 180acac70 | client | controller by index |
| 1801befe0 | client | float compare |
| 1801b9c30 | client | max |
| 180cab7f0 | client | C_PlantedC4 constructor (adds to the count) |
| 180bdb2d0 | client | trueview replay test (CPrediction 0x182565620: +0xd4 set, +0x50 == 1, +0x58's +0x10 > 1) |
| 180d0ef50 | client | DeathFadeLayer |
| 180208400 | server | Event_Killed's part: death time / angles |
| 180b4f890 | server | CCSPlayerPawn vfn 0x5f0: a vehicle's (+0xb48) or the move parent's composition (1803d95d0), else vfn 0x5f8 (m_angEyeAngles +0x15b4) |
| 180912130 | server | PlayerKilled: m_bKilledByHeadshot (+0x14f8) |
| 180249530 | server | Spawn (clears it) |

## Fields

| Offset | Field |
|---|---|
| view (CViewRender +0x10 + slot x 0x990) +0x4a0 / +0x4b8 | origin / angles: CalcView's in / out, never reset between frames (starts from last frame's view) |
| camera services +0x298 | m_iFOV |
| +0x2b0 | m_flDeathCamTilt |
| +0x2b4 | m_hDeathCamBounds |
| +0x2b8 | m_bDeathCamBoundsSearched |
| camera services +0x38 | the pawn (read by 180882530) |
| pawn +0x1308 | observer services |
| client pawn +0x1458 | m_flDeathTime |
| client pawn +0x1da8 | m_qDeathEyeAngles (roll +0x1db0) |
| client pawn +0x520 | m_hOwnerEntity |
| client pawn +0x1ec5 | m_bKilledByHeadshot |
| client pawn +0x15ea | m_bIsBuyMenuOpen |
| client pawn +0x1560 | controller |
| controller +0x92c | pawn |
| observer services +0x4c | own pawn handle |
| server pawn +0xc7c / +0x1454 / +0x14f8 | m_flDeathTime / m_qDeathEyeAngles / m_bKilledByHeadshot |
| g_CSViewVectors +0x60 | m_vDeadViewHeight (0, 0, 14) |
| C_PointDeathcamBounds +0x600 / +0x60c / +0x618 | m_vBoxMins / m_vBoxMaxs / m_flLerpDistance (keyvalues box_mins / box_maxs / lerp_distance; client-only) |
| client mode +0x9c | == 3 for round_end_via_bombing |
| client mode +0x118..+0x130 | overlay weights (below) |
| client mode +0x154 / +0x158 / +0x15c | fade start / ... / last fade value |
| collision +0x5a & 4 | owner id -1 |

## Constants

| Value | What |
|---|---|
| 0.0625 (0x181c0e8ac) | death cam starts after this many seconds |
| 4 (0x181ac6088) / 10 (0x181ad0f70) | tilt RandomFloat range |
| 0x181aad678 / 0x181aad4a8 | tier0 RandomFloat / RandomInt imports |
| 11 (0x181c0e8f0) / 10 / 64 | water probe offsets |
| 9.0 | camera box half-size |
| 0x181ad4838 | water filter vtable: interacts-with 0x18000 (water 0x8000 \| slime 0x10000), group 5, flags `(b & 0xc9) \| 0x49 \| 4`, +0x40 = 0 |
| 57.2957764 | rad -> deg |
| 0x1822903c0 | (-1, -1, -1, 1) |
| 0x182290350 / 0x181acaf44 | 2^-23 / 2^23 |
| 0.03125 (0x181ad0f60) | phase2 step |
| death_chase_distance | 76 (object 0x18252dee0, registered 1800ae000, flags 2 = development only) |
| spec_freeze_traveltime | 0.3 (0x18252b798) |
| spec_freeze_deathanim_time / spec_freeze_time | objects 0x18252b7b8 / 0x18252b788 |
| spec_replay_colorcorrection | 0.5 (0x182579310) |
| cl_disable_postprocessing | 0 (0x182579320) |
| cl_instant_death_anim | 0 (0x182579330) |
| cl_disable_deathcam_audio_mix_fade_out | 0 (0x182579340) |
| cl_deathcam_audio_mix_phase1_fade_time / _phase2_fade_time | 2 (0x182579350) / 0.4 (0x182579370) |
| _phase1_fade_amount / _phase2_fade_amount | 0.15 (0x182579360) / 0.5 (0x182579380) |
| mp_forcecamera | 0x1825510d0 |
| cl_trueview_show_doa_predictions | 1 (0x182565860) |
| 0x18252d104 | C_PlantedC4 count |
| 1821fffd0 | hltv_replay_fade value |
| 18254eae8 | post-processing state (vfn 0 -> vfn 0x68(slot)), vfn 0x48(handle, weight) |

### Overlays (.vpost under lighting/postprocessing/, table 1800f0e50; handles +0xe0 .. +0x110)

| Field | Overlay | Weight |
|---|---|---|
| +0x118 | effects/in_buy_menu | 1 when the local pawn is alive (vfn 0xab8) and m_bIsBuyMenuOpen |
| +0x11c | effects/round_end_via_bombing | 0 every frame: the 1/64 step toward 1 needs +0x9c == 3, an observed pawn and 18094dc60 false, but 18094dc60 is `mov al, 1; ret` (post-layers.md 4) |
| +0x120 | effects/death_cam_phase1 | below |
| +0x124 | effects/death_cam_phase1_low_violence | the same, under low violence |
| +0x128 | effects/death_cam_phase2 | below |
| +0x12c | effects/hltv_replay_fade | 1821fffd0's value |
| +0x130 | effects/hltv_replay | spec_replay_colorcorrection while 1804ffb20 |

cc_freeze_ct / cc_freeze_t lead the table (set elsewhere). All 0 under cl_disable_postprocessing or with a menu camera.

## Where it runs

1. SetUpView -> 180b9c970 -> camera services vfn 0x108 -> observer services vfn 0x110 when its mode (vfn 0xf0) != 0,
   else 180882530.
2. 180882530: pawn not alive (vfn 0x4e8) and `curtime - m_flDeathTime > 0.0625` -> 1808818a0, return. Else tilt = 0,
   bounds = -1, searched = 0, the eye path (vfn 0x568 EyePosition, 0x570 EyeAngles, ...).
3. 1808587c0 keeps your own pawn valid until `m_flDeathTime + spec_freeze_deathanim_time + spec_freeze_time +
   spec_freeze_traveltime`; another player's dead pawn is never valid: only your own death has a death cam.

## The camera 1808818a0

1. bone = 180952970(pawn, 0x9b0e3fd); -1 (or no pawn) -> tilt = 0.
2. tilt == 0 (ucomiss: not for NaN) -> tilt = RandomFloat(4, 10), RandomInt(0, 1) != 0 -> negated (xorps -0). No pelvis:
   drawn again every frame.
3. s = 180889e20(curtime - m_flDeathTime) (subss, not 18015c5e0): `t = (e - 0.0625) / spec_freeze_traveltime`; t =
   clamp(t, 0, 1); `u = t x 0.5 + 0.5`; `r = ((u x 3) x u - ((u + u) x u) x u) - 0.5`; return `r + r`.
4. `roll = m_qDeathEyeAngles.roll + (((tilt - 0) x s) + 0)`; `dist = (death_chase_distance - 16) x s + 16`.
5. Centre o: bone >= 0 -> 18093f490(pawn, bone) + m_vDeadViewHeight per axis (bone + view); no bone -> the incoming view
   origin.
6. Water under o: TraceLine from `(o.x, o.y, (o.z - 11) + 64)` to `(o.x, o.y, o.z - 11)`; filter ids 1809dd600(pawn) and
   its owner's, hierarchy 1809ea740(pawn). Hit -> o.z = endpos.z (+0x8c) + 11.
7. fwd = AngleVectors(incoming angles); cam = `(-dist x f) + o` per axis.
8. Water under cam: from `(c.x, c.y, (c.z - 10) + 64)` to `(c.x, c.y, c.z - 10)`. Hit -> d = cam - o, `h = (endpos.z +
   10) - o.z`; `0 > d.z and h > d.z and 0 >= h`: d.x, d.y x= h / d.z; cam = `(o.x + d.x, o.y + d.y, h + o.z)` (a hit
   always sets cam.z).
9. 1808a5910: box (-9, -9, -9) .. (9, 9, 9) from o to cam, interacts-with 1 (solid), group 5, flags 0x49, +0x40 0, the
   pawn's ids; fraction >= 1 -> cam, else endpos (+0x84). The origin.
10. Angles = (death pitch, death yaw, roll); FOV = services vfn 0x118.
11. point_deathcam_bounds: once a death (+0x2b8), the first (1809dfb70) whose box holds the origin (180ce3c50:
    WorldToEntitySpace, mins <= l <= maxs) goes to +0x2b4. Each frame with one: origin = 180ce2950 (l =
    WorldToEntitySpace(origin), per axis maxss(mins, minss(l, maxs)), back: zero abs angles -> `scale x l + abs origin`,
    else `t = 2 q x l`, `q x t + (w t + l)`, x scale + position); `moved = |clamped - origin|` (`(dy^2 + dz^2) + dx^2`);
    moved > 0, lerp > 0 and a pelvis -> look = VectorAngles(pelvis - origin) (the raw bone, no dead view height), k =
    1817438a0(clamp(moved / lerp, 0, 1)); pitch / yaw = `AngleDiff(look, death angle) x k + death angle`. (No de_, cs_,
    ar_, ze_ map checked has one.)

## Math helpers

- WorldToEntitySpace 1801e2ec0: zero abs angles: `(p - abs origin) x (1 / scale)`. Else q' = q x (-1, -1, -1, 1),
  normalised lane-wise by sqrt(dpps 0xff) (a zero length as 2^-23); k = 1 / scale (scale 0 -> 2^23, scale 1 -> no
  multiply); inverse position = `-(rotate(q', position) x k)`; result = `rotate(q', p) x k + inverse position`;
  `rotate(q, v) = q x t + (v + w t)`, `t = 2 (q x v)` (each cross lane `a x b - c x d`).
- VectorAngles 181742a00: y == 0 and x == 0 -> (z > 0 ? 270 : 90, 0, 0); else yaw = `V_atan2f(y, x) x 57.2957764`, + 360
  below 0; pitch = `V_atan2f(-z, sqrtss(x x + y y)) x 57.2957764`, + 360 below 0; roll 0.
- AngleDiff 18173cb10(dest, src): `d = V_fmodf(dest - src, 360)`; dest > src: d >= 180 -> d - 360; else d <= -180 -> d +
  360.

## The server's half

- 180208400: m_flDeathTime = curtime, m_qDeathEyeAngles = vfn 0x5f0 (180b4f890).
- 180912130 sets m_bKilledByHeadshot from the kill's headshot; Spawn 180249530 clears it.

## Overlay weights 180d0d540 (ClientModeCSNormal::Update)

1. Dead pawn 180c7ae00: the local controller, connected (vfn 0x4f0): its pawn, or when observing (vfn 0xac0) in the eye
   (mode 2) the observed pawn; returned only when dead.
2. Dead pawn: cl_instant_death_anim -> phase1 = 1. Else `e = curtime - m_flDeathTime`; `a = clamp(e x 4, 0, 1)`;
   headshot ? `x = e` : `x = e - (spec_freeze_time - 0.5)`; `p2 = clamp(x + x, 0, 1)`; phase1 = max(a, phase1); phase2 =
   p2, unless mp_forcecamera is 1, no C_PlantedC4 exists and 18089c6f0(pawn's controller, local team) -> phase2 steps
   toward 0.
3. 18089c6f0: the controller is on the team with a pawn (+0x92c), and no other controller of the team (over
   maxclients) has a living pawn or one that died later.
4. No dead pawn: trueview replay (180bdb2d0) -> phase1 = 1 (0.4 with cl_trueview_show_doa_predictions); else phase1 = 0
   and phase2 steps.
5. Step: phase2 < 0 -> min(0, phase2 + 0.03125); > 0 -> max(0, phase2 - 0.03125).
6. The phase-1 key not in use is zeroed first (+0x120 or +0x124).

## DeathFadeLayer 180d0ef50

1. T1 = max(phase1_fade_time, 0.001), T2 = max(phase2_fade_time, 0.001).
2. Without cl_disable_deathcam_audio_mix_fade_out: phase1 > 0 and phase2 <= 0 -> +0x158 = 0, start +0x154 = curtime if
   0, `p1 = clamp((curtime - start) / T1, 0, 1)`; phase2 > 0 -> the same start, p1 = 1, `p2 = clamp((curtime - start) /
   T2, 0, 1)` (counted from phase 1's start). Neither, with +0x15c > 0 and both <= 0: +0x154 / +0x158 = 0.
3. `v = minss(phase2_fade_amount x p2 + phase1_fade_amount x p1, 1)`; changed -> +0x15c = v, soundsystem vfn
   0x150(DeathFadeLayer, v) (the layer's handle from vfn 0x148 once).

## Unread

- Local contrast's input (death_cam_phase1 carries it: post-layers.md "Unread").
- The low-violence launch option's name (token 0xcdbd1292 is no string in client or engine2).
