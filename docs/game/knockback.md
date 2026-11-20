# ZR's knockback

CS2Fixes ZombieReborn (github.com/Source2ZE/CS2Fixes, commit 72ec6b9, 2026-04-21): zombiereborn.cpp, the Linux object `dockerbuild/cs2fixes.cs2/linux-x86_64/src_zombiereborn.o` and hl2sdk-cs2's prebuilt `sdk/lib/linux64/mathlib.a` (mathlib_base.o), read with an ELF symbol + relocation dump (constants from `.LCPI*`) and capstone. CS2 side: server_20261105.

## Functions

| Address | Module | What |
|---|---|---|
| ZR_OnPlayerTakeDamage | zombiereborn.cpp:1595-1643 | bullet knockback, after TakeDamageOld (from Detour_CBaseEntity_TakeDamageOld, detours.cpp:157-159) |
| ZR_Hook_OnTakeDamage_Alive | zombiereborn.cpp:1416-1459 | grenade knockback / napalm; pre-hook on OnTakeDamage_Alive (cs2fixes.cpp:1043-1050, `pDamageResult->m_pOriginatingInfo`) |
| ZR_ApplyKnockback | src_zombiereborn.o, 920 bytes | the bullet push |
| ZR_ApplyKnockbackExplosion | src_zombiereborn.o, 570 bytes | the grenade push |
| AngleVectors(const QAngle&, Vector*) | mathlib_base.o, 122 bytes | forward (three-vector overload 297 bytes, the same per angle) |
| VectorNormalize(Vector&) | mathlib_base.o, 89 bytes | returns len |
| 1803ed610 | server | CS2's TakeDamageOld |
| 180a93f70 | server | damage services' OnTakeDamage (hit group, friendly fire, armor; writes the scaled damage to info+0x44: shots.md 4) |
| 180a2fa80 | server | CKnife's swing (shots.md 7) |
| 180c2f3c0 | server | TraceShape |
| 1814a32c0 | server | clears a trace result |
| 180bee540 | server | fills the trace result from the physics hit |
| 180cacf80 | server | hit group of a trace (falls back to the shape at +0x20 through 180b539b0) |

## Fields

| Offset | Field |
|---|---|
| info +0x68 | m_pTrace |
| info +0x44 | m_flDamage (after armor, in the pre-hook) |
| trace +0x0 / +0x8 / +0x10 | surface / entity / m_pHitbox |
| trace +0x18 / +0x20 | body / shape |
| trace +0x30.. | contents |
| trace +0x78 / +0x84 | start / end |
| trace +0xac | fraction |
| trace +0xb8.. | flags |

## Constants

| Value | What |
|---|---|
| 1.0 (.LCPI62_0) | hit group scale when FindHitgroupIndex finds none (hitgroups.cfg upstream: 1.0 every group) |
| 36.0 (.LCPI63_0 0x42100000) | explosion direction z lift |
| 0x3c8efa35 | deg -> rad (f32) |
| 1.1920929e-07 (.LCPI2_0 0x34000000, FLT_EPSILON), 1.0 (.LCPI2_1 0x3f800000) | VectorNormalize |
| hegrenade_projectile 3.0, inferno 5.0 | weapons.cfg (FindWeapon on the inflictor's class name) |
| 0x37f | Linux's default x87 control word (64-bit significand); Windows' default is 53-bit |

## Bullets (ZR_OnPlayerTakeDamage)

- Runs after CS2's TakeDamageOld returns (after the health loss and any death), when `pResult->m_flDamageDealt > 0` and not suppressed; `damage = m_flDamageDealt` (the floored loss, not clamped to the health left: shots.md 4).
- Returns unless `m_bitsDamageType & (DMG_BULLET | DMG_SLASH)`, `m_pTrace` and `m_pTrace->m_pHitbox` set, the attacker a pawn, the ability (weapon) exists, attacker CT and victim T.
- Then `ZR_ApplyKnockback(attacker, victim, damage, weapon, hitgroup = the hitbox's m_nGroupId, class)` with the victim's ZR class knockback (1.0 otherwise).
- **A knife pushes no zombie**: CKnife's swing points info+0x68 at its own TraceShape result (the store `pppuStack_230 = &local_378` at the TakeDamageOld call, 180a30...: `local_298` the info, `local_378` the trace). 180bee540 never writes +0x10 (m_pHitbox); only the hitbox system's interval trace (shots.md 1-2) does.

## Grenades (ZR_Hook_OnTakeDamage_Alive)

- Runs after 180a93f70, so `pInfo->m_flDamage` is after armor.
- CT attacker on a T victim, inflictor class starting "hegrenade" (the projectile) or "inferno":
  1. HE napalm: `clamp(m_flDamage / zr_napalm_full_damage x zr_napalm_burn_duration, 0, duration)`, IgnitePawn with DMG_FALL.
  2. `ZR_ApplyKnockbackExplosion(inflictor, victim, (int) m_flDamage, inferno)`.
- A zombie's knife on a human returns true from the same pre-hook (infect, damage suppressed).

## ZR_ApplyKnockback

```
movss  xmm0, [rbp-0x34]        ; flDamage
mulss  xmm0, [rax]             ; x zr_knockback_scale
movss  xmm1, [rbp-0x30]        ; the weapon's flKnockback
mulss  xmm1, xmm0
movss  xmm0, [rbp-0x2c]        ; the hit group's (1.0, .LCPI62_0, when FindHitgroupIndex finds none)
mulss  xmm0, xmm1
mulss  xmm2([rbp-0x60]), xmm0  ; x classknockback
mulps  (x, y) by it; mulss z   ; vecKnockback (from AngleVectors(m_angEyeAngles))
addps / addss m_vecAbsVelocity ; then m_vecAbsVelocity_prop::Set
```

- `s = (((damage x scale) x weapon) x hitgroup) x class` in f32, `velocity += forward x s`.
- The ground flag is untouched: CS2's movement leaves the ground from the velocity on the victim's next command (sv_optimizedmovement prelude: `vz > 250`).

## ZR_ApplyKnockbackExplosion

1. `d = victim.GetAbsOrigin() - projectile.GetAbsOrigin()` (subps, subss), `d.z += 36.0`.
2. `VectorNormalize(d)`; then `d.z = 0` when bMolotov (inferno).
3. `s = ((float) iDamage (cvtsi2ss) x scale) x weapon`, `velocity += d x s`.

## mathlib

- AngleVectors: `rad = angle x 0x3c8efa35` (f32 mulss), `cvtss2sd`, `fld qword`, `fsincos` (x87: SinCos's POSIX branch, mathlib.h:385-410).
  - Yaw: stored `fstp qword` (cos then sin), narrowed by `cvtpd2ps`: two roundings (64-bit significand -> 53 -> 24).
  - Pitch: `fxch; fstp dword` (sin), `fstp dword` (cos): one rounding (64 -> 24).
  - `forward = (cp x cy, cp x sy, -sp)` (movsldup cp x (cy, sy); xorps the sign).
- VectorNormalize: `len = sqrtss((x x + y y) + z z)` (mulps, movshdup, addss), `inv = 1.0 / (len + 1.1920929e-07)`, `v x inv` (mulps, mulss); a zero vector stays zero.
- fsincos vs a model (sin / cos in double-double, reduction by pi/2, rounded to 64 then 53 / 24 bits): the real instruction under `fldcw 0x37f` on an AMD Ryzen 7 7800X3D over 40,238,266 arguments (1/64-degree grid over +-1080, 2,000 ulps around every multiple of 90, 20M random in +-180, 20M in +-1e6) differs in 0 once narrowed to f32, with either reduction constant (the x87's 66-bit pi 0xc90fdaa22168c234c or true pi).

## Unread

- fsincos on other CPU vendors (documented to differ in last bits; checked on AMD only).
- Arguments past 2^40 radians (the x87 reduces up to 2^63).
- GFL's build vs this dockerbuild object (same source, same mathlib.a); GFL's own weapons.cfg / hitgroups.cfg aren't public.
- `m_vecAbsVelocity` on the pawn read as the movement's velocity (taken as so; SetupMove's read: movement.md).
