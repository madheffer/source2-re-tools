# The landing dip (client.dll 2026-10-15)

The first-person camera sinks after a landing and comes back up: 3 u at most, 0.2 s in all, an ease in-out cubic.
Only the camera's origin moves; EyePosition doesn't, so the shots, the target ID and the crosshair's 2000 u point
(cl_crosshair_recoil: settings.md "The crosshair's drawing") start from the undipped eye while the view matrix is
the dipped camera's. Port: web/src/cs2web/client/core/land-dip.js (test: land-dip-test.mjs), called from
client/core/game.js render on your own live eye.

## Where it runs

- **CCSPlayer_CameraServices' CalcView 180882530** (death-cam.md 1): origin = pawn vfn **0x568** EyePosition, angles =
  vfn 0x570 EyeAngles, then **180c671d0(pawn, &origin, DAT_1821bf098 == -1)** on the origin, then the angle punches
  (180a645f0, 1808a61d0), vfn 0xa98's offset with a hull trace (1808a5910, 8 u) and the ceiling check (abs origin z +
  the hull's max z vs origin z + 8). The flag DAT_1821bf098 == -1 is read by the interpolated-var readers too
  (180160580): taken as the normal view pass (true); with it false the dip is drawn but no state moves.
- **EyePosition** for C_CSPlayerPawn (vtable 0x181c8a138, also C_CSPlayerPawnBase 0x181c87100 / C_BasePlayerPawn
  0x181c49b60) slot 0x568 = **18093c660**: a vehicle's (pawn +0x1328 x 8 -> vfn 0xf0 -> its 0x568), the observer mode
  2 / 3 path with pawn +0x14c5 (180c14130 on vfn 0x998's +0x6cc), else **18015fab0** = GetAbsOrigin (180219a80) + vfn
  **0x5a0 = 180160770**: m_vecViewOffset (+0xf60, schema) read through its interpolated var (180160580(+0xf60, 0,
  -1.0)) and 18016a3d0. The crosshair's 18093c760 (settings.md) takes the same EyePosition.

## 180c671d0

Pawn fields (client-only, not in the schema): +0x15e2 active (byte), +0x15e4 start (curtime), +0x15b4 elapsed,
+0x15b8 the fall velocity kept last; movement services = pawn +0x1330 (m_pMovementServices), its +0x25c
m_flFallVelocity (schema). curtime = PTR_DAT_182230090 +0x30 (README).

1. Start: flag set, not active, `0.1 >= m_flFallVelocity` (comiss with 0x181ada28c 0.1f), and `+0x15b8 > 250`
   (0x181bfde80) and `1024 >= +0x15b8` (0x181b29754): active = 1, start = curtime, **+0x1720 = 2.0f** (a field not
   read yet).
2. Active: with the flag, elapsed = max(curtime - start, 0) (1801b9c30 with a 0). t = clamp(elapsed / 0.2f
   (divss 0x181acaf20), 0, 1) (1801587b0). u = 0.5 > t ? t + t : clamp(1 - ((t - 0.5) + (t - 0.5)), 0, 1) (18015a220).
   e = 0.5 > u ? ((u x 4) x u) x u : 1 - V_powf(2 - (u + u), 3) x 0.5 (0x181ac6088 4, 0x181ac607c 3, 0x181ac6078 2,
   0x181ac6070 0.5). origin z -= e x 3. active = 1 > t (seta).
3. With the flag: still active -> unless origin z - 0.001 (0x181ad0f5c) >= the incoming z (never while dipping),
   return; that case clears active. Not active -> +0x15b8 = m_flFallVelocity (the value a later landing tests).

So a standing jump (lands at ~300 u/s) dips every time; a drop under 250 u/s or over 1024 doesn't.

## Not read yet

- +0x1720 (2.0 at the start): who reads it.
- The observer's in-eye camera (observer services vfn 0x110) for a watched player: whether it runs 180c671d0 too.
