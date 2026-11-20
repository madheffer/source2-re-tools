# ZR's knockback (traced 2026-11-11; sim/src/combat/knockback.rs, sim/src/math/x87.rs)

ZombieReborn's knockback isn't CS2's code: it's CS2Fixes' plugin on top. Its truth is GFL's Linux build of it, so it
was read from the compiled objects, not only the C++: CS2Fixes (github.com/Source2ZE/CS2Fixes) at commit 72ec6b9 (2026-04-21), the Linux
object `dockerbuild/cs2fixes.cs2/linux-x86_64/src_zombiereborn.o` and the prebuilt `sdk/lib/linux64/mathlib.a` the
plugin links (hl2sdk-cs2's mathlib). Read with a small ELF reader and capstone (no objdump on this machine): the
scripts are an ELF64 symbol + relocation dump (constants resolved from `.LCPI*`) and a GNU ar extractor; any
`python` + capstone does it.

## 1. Where ZR pushes, and with which damage

- **Bullets** (and in principle knives): `ZR_OnPlayerTakeDamage` (zombiereborn.cpp:1595-1643), called from CS2Fixes'
  `Detour_CBaseEntity_TakeDamageOld` (detours.cpp:157-159) **after** CS2's TakeDamageOld (`1803ed610`) returns, so
  after the health loss and any death, when `pResult->m_flDamageDealt > 0` and the damage wasn't suppressed, with
  `damage = m_flDamageDealt` (the floored loss, not clamped to the health left: shots.md 4). It returns unless
  `m_bitsDamageType & (DMG_BULLET | DMG_SLASH)`, `m_pTrace` and **`m_pTrace->m_pHitbox`** are set, the attacker is a
  pawn, the ability (weapon) exists, and the attacker is CT and the victim T. Then the class knockback (the
  victim's ZR zombie class, 1.0 otherwise) and `ZR_ApplyKnockback(attacker, victim, damage, weapon, hitgroup = the
  hitbox's m_nGroupId, class)`.
- **The knife has no hitbox**: CKnife's swing (`180a2fa80`, shots.md 7) points the damage info's trace (`info+0x68`)
  at its own TraceShape result (the store `pppuStack_230 = &local_378` at the TakeDamageOld call, `180a30...`:
  `local_298` is the info, `local_378` the trace). TraceShape (`180c2f3c0`) clears the result (`1814a32c0`) and
  fills it from the physics hit in `180bee540`: +0x0 the surface, +0x8 the entity, +0x18 / +0x20 the body / shape,
  +0x30.. the contents, +0x78 / +0x84 start / end, +0xac the fraction, +0xb8.. flags; **+0x10 (m_pHitbox) is never
  written**. Only the hitbox system's interval trace (shots.md 1-2) sets it. So `m_pHitbox` is null for every knife
  hit and ZR returns before the push: **a knife pushes no zombie** (the hit group still comes out of `180cacf80`,
  which falls back to the shape at +0x20 through `180b539b0`). The JS port pushed knife hits; it doesn't now.
- **Grenades**: `ZR_Hook_OnTakeDamage_Alive` (zombiereborn.cpp:1416-1459), CS2Fixes' pre-hook on the pawn's
  OnTakeDamage_Alive (cs2fixes.cpp:1043-1050, `pDamageResult->m_pOriginatingInfo`). It runs after the damage
  services' OnTakeDamage (`180a93f70`: hit group, friendly fire, armor, which write the scaled damage back to
  `info+0x44`, shots.md 4), so `pInfo->m_flDamage` there is the damage **after armor**. For a CT attacker on a T
  victim, an inflictor class starting "hegrenade" (the projectile) or "inferno": first the napalm (an HE:
  `clamp(m_flDamage / zr_napalm_full_damage x zr_napalm_burn_duration, 0, duration)`, IgnitePawn with DMG_FALL),
  then `ZR_ApplyKnockbackExplosion(inflictor, victim, (int) m_flDamage, inferno)`. The JS port took the damage before
  armor for both; now it's the sim's `loss.damage` (after armor).
- A zombie's knife on a human returns true from the same pre-hook (infect, the damage suppressed): unchanged.

## 2. ZR_ApplyKnockback (src_zombiereborn.o, 920 bytes)

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

So `s = (((damage x scale) x weapon) x hitgroup) x class` in f32, `velocity += forward x s`. Nothing touches the
ground flag: CS2's movement leaves the ground from the velocity on the victim's next command (with
sv_optimizedmovement, the prelude's `vz > 250`, sim/src/movement/prelude.rs). The JS port also cleared onGround for
any upward push; gone.

## 3. ZR_ApplyKnockbackExplosion (src_zombiereborn.o, 570 bytes)

`d = victim.GetAbsOrigin() - projectile.GetAbsOrigin()` (subps, subss), `d.z += 36.0` (.LCPI63_0 0x42100000),
`VectorNormalize(d)`, `d.z = 0` when bMolotov (the inferno; after normalising), `s = ((float) iDamage (cvtsi2ss) x
scale) x weapon`, `velocity += d x s`. weapons.cfg: hegrenade_projectile 3.0, inferno 5.0 (FindWeapon on the
inflictor's class name).

## 4. mathlib.a (hl2sdk-cs2's prebuilt Linux mathlib, mathlib_base.o)

- **`AngleVectors(const QAngle&, Vector* forward)`** (122 bytes): `rad = angle x 0x3c8efa35` (f32 mulss),
  `cvtss2sd`, `fld qword`, `fsincos` (the x87: SinCos's POSIX branch, mathlib.h:385-410). The yaw's results are stored
  `fstp qword` (cos then sin) and narrowed with `cvtpd2ps`: **two roundings** (64-bit significand -> 53 -> 24). The
  pitch's go `fxch; fstp dword` (sin), `fstp dword` (cos): **one rounding** (64 -> 24). `forward = (cp x cy, cp x sy,
  -sp)` (movsldup cp x (cy, sy); xorps the sign). The three-vector overload (297 bytes) does the same per angle.
- **`VectorNormalize(Vector&)`** (89 bytes): `len = sqrtss((x x + y y) + z z)` (mulps, movshdup, addss), `inv = 1.0 /
  (len + 1.1920929e-07)` (.LCPI2_1 0x3f800000, .LCPI2_0 0x34000000 FLT_EPSILON), `v x inv` (mulps, mulss); returns
  len. A zero vector stays zero.
- The FPU's precision control: Linux's default 0x37f (64-bit significand). Windows' default is 53-bit, so the native
  check sets 0x37f itself.

## 5. The model and its check

`math/x87.rs` computes sin / cos of the f64 argument in double-double arithmetic (reduction by pi/2 in exact f64
parts, Taylor series), rounds to 64 bits (the x87 register), then to 53 and 24 as each store does
(round-to-nearest-even). The reduction constant is selectable: the x87's documented 66-bit pi (0xc90fdaa22168c234c,
Intel's) or the true pi. **`x87_check` runs the real instruction** (inline asm, `fldcw 0x37f`, the same loads and
stores) on this machine (AMD Ryzen 7 7800X3D) over 40,238,266 arguments (a 1/64-degree grid over +-1080, 2,000 ulps
around every multiple of 90, 20M random angles in +-180 and 20M in the command's +-1e6): **0 differ** with either
constant once narrowed to f32 (the reduction's last bits never reach the f32). `knockback-test.mjs` replays 200,000
ZR_ApplyKnockback cases computed with the real instruction through the .wasm: 0 differ.

## Still open

- GFL's own CPU: fsincos is documented to differ between vendors in its last bits; checked on this AMD only (the f32
  narrowing hides the reduction constant here).
- Arguments past 2^40 radians aren't modelled (the x87 reduces up to 2^63; the command's yaw stops at 1e6 degrees).
- GFL's build could differ from this checkout's dockerbuild object (same source, the same mathlib.a).
- ZR's hitgroups.cfg (1.0 for every group upstream); GFL's own weapons.cfg / hitgroups.cfg aren't public.
- `m_vecAbsVelocity` set on the pawn: the movement reads it as its velocity (taken as so; SetupMove's read of it is
  movement.md's).
