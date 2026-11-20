# The landing dip

client_20261015.

The first-person camera sinks after a landing and comes back up: 3 u at most, 0.2 s in all, an ease in-out cubic. Only
the camera's origin moves; EyePosition doesn't, so shots, target ID and the crosshair's 2000 u point (cl_crosshair_recoil:
settings.md "The crosshair's drawing") start from the undipped eye while the view matrix is the dipped camera's.

## Functions

| Address | Module | What |
|---|---|---|
| 180882530 | client | CCSPlayer_CameraServices CalcView (death-cam.md 1) |
| 180c671d0 | client | the dip (pawn, &origin, DAT_1821bf098 == -1) |
| 180a645f0, 1808a61d0 | client | the angle punches (after the dip) |
| 1808a5910 | client | hull trace for vfn 0xa98's offset (8 u) |
| 180160580 | client | interpolated-var reader (also reads the DAT_1821bf098 flag) |
| 18093c660 | client | EyePosition: slot 0x568 of C_CSPlayerPawn, also of C_CSPlayerPawnBase and C_BasePlayerPawn |
| 18015fab0 | client | GetAbsOrigin (180219a80) + vfn 0x5a0 |
| 180160770 | client | vfn 0x5a0: m_vecViewOffset via 180160580(+0xf60, 0, -1.0) and 18016a3d0 |
| 180c14130 | client | observer path (on vfn 0x998's +0x6cc) |
| 18093c760 | client | the crosshair's point (settings.md): same EyePosition |
| 1801b9c30 | client | max (with 0) |
| 1801587b0 | client | clamp |
| 18015a220 | client | the in-out step |

## Fields

| Offset | Field |
|---|---|
| vtables | C_CSPlayerPawn 0x181c8a138, C_CSPlayerPawnBase 0x181c87100, C_BasePlayerPawn 0x181c49b60 |
| pawn +0x1328 x 8 | vehicle (-> vfn 0xf0 -> its 0x568) |
| pawn +0x14c5 | observer mode 2 / 3 path |
| pawn +0xf60 | m_vecViewOffset (schema) |
| pawn +0x15e2 | dip active (byte; client-only) |
| pawn +0x15e4 | dip start (curtime) |
| pawn +0x15b4 | elapsed |
| pawn +0x15b8 | the fall velocity kept last |
| pawn +0x1720 | set 2.0f at the start (reader unread) |
| pawn +0x1330 | m_pMovementServices; its +0x25c m_flFallVelocity |
| PTR_DAT_182230090 +0x30 | curtime |

## Constants

| Value | What |
|---|---|
| 0x181ada28c 0.1f | max m_flFallVelocity to start |
| 0x181bfde80 250 / 0x181b29754 1024 | +0x15b8 range (> 250, <= 1024) |
| 0x181acaf20 0.2f | duration (divss) |
| 0x181ac6088 4, 0x181ac607c 3, 0x181ac6078 2, 0x181ac6070 0.5 | the cubic |
| 0x181ad0f5c 0.001 | end test |
| 3 | depth |

## CalcView (180882530)

origin = vfn 0x568 EyePosition, angles = vfn 0x570 EyeAngles; 180c671d0 on the origin; the angle punches; vfn 0xa98's
offset with a hull trace (8 u) and the ceiling check (abs origin z + hull max z vs origin z + 8). DAT_1821bf098 == -1 is
taken as the normal view pass (true); false: the dip is drawn but no state moves.

EyePosition 18093c660: a vehicle's; the observer mode 2 / 3 path; else 18015fab0.

## 180c671d0

1. Start: flag set, not active, `0.1 >= m_flFallVelocity` (comiss), `+0x15b8 > 250` and `1024 >= +0x15b8`: active = 1,
   start = curtime, +0x1720 = 2.0f.
2. Active, with the flag: elapsed = max(curtime - start, 0). t = clamp(elapsed / 0.2f, 0, 1).
   `u = 0.5 > t ? t + t : clamp(1 - ((t - 0.5) + (t - 0.5)), 0, 1)`.
   `e = 0.5 > u ? ((u * 4) * u) * u : 1 - V_powf(2 - (u + u), 3) * 0.5`. origin z -= `e * 3`. active = `1 > t` (seta).
3. With the flag: still active -> return unless origin z - 0.001 >= the incoming z (never while dipping), which clears
   active. Not active -> +0x15b8 = m_flFallVelocity (what the next landing tests).

A standing jump (lands at ~300 u/s) dips every time; under 250 u/s or over 1024 doesn't.

## Unread

- +0x1720 (2.0 at the start): who reads it.
- The observer's in-eye camera (observer services vfn 0x110) for a watched player: whether it runs 180c671d0.
