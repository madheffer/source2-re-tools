# Tagging: the slowdown on being hit

server_20261105. weapons.vdata m_flFlinchVelocityModifierLarge / Small.

## Functions

| Address | Module | What |
|---|---|---|
| 180a961f0 | server | damage hook (damage services, CTakeDamageResult*) (caller 180a94400) |
| 180c856b0 | server | fills the services' pawn (+0x38) |
| 180a7ab50 | server | (info, &, &vdata, &): find the attacker's weapon vdata |
| 18102cf10 -> 1809be8c0 | server | grenade definition index -> item -> vdata |
| 180ab76a0 | server | the tag (pawn, large xmm1, small xmm2, ratio xmm3) |
| 180574fa0 | server | queue a prediction message (controller, msg, 0x182121c38, tick, ...) |
| 1801c8ce0 | server | the pawn's controller |
| 180cacc40 / 180c86d00 | server | time -> tick (services' time) |
| 1813b8ef0 | server | time rounded up to a tick (+1 with a fraction) |
| 18097b670 | server | the queued message's handler: controller's pawn (180b55040) -> 180ab76a0(pawn, +0x1c, +0x18, +0x20) |
| 180b55040 | server | the controller's pawn |
| 180c868d0 | server | the active weapon (vfn 0xc20 GetMaxSpeed) |
| 180ae1c90 | server | writes m_flVelocityModifier |
| 1801783c0 | server | `min(a, b) = b <= a ? b : a` |
| 1801783b0 | server | `max(a, b) = a <= b ? b : a` |
| 18017b8d0 | server | `clamp(v, lo, hi) = lo <= v ? (v <= hi ? v : hi) : lo` |
| 1809669f0 | server | CCSGameRules::Think: every player pawn (vfn 0x558 and vfn 0xca8) -> 180ac8880 |
| 180ac8880 | server | the flinch stack's recovery |
| 180460960 | server | Approach(t, v, speed): `speed < t - v` -> v + speed, `t - v < -speed` -> v - speed, else t |
| 180adcb90 | server | PostMove: m_flVelocityModifier + frametime x 0.4 on the ground |
| 1801f7ca0 | server | spawn: both to 1 |
| 180a44500 / 180a44650 | server | observer-target weapon branch (unread) |

## Fields

| Offset | Field |
|---|---|
| CCSPlayerPawn +0x14e0 | m_flVelocityModifier (the map's "runspeed" too) |
| CCSPlayerPawn +0x14dc | m_flFlinchStack |
| CCSWeaponBaseVData +0x838 / +0x83c | m_flFlinchVelocityModifierLarge / Small (0 with no vdata) |
| result +0x48 | m_nDamageFlags (bit 0x2 skips; TakeDamageFlags_t name unread) |
| result +0x20 | m_flDamageDealt |
| services +0x38 | pawn |
| info +0x40 | m_hAbility (as CCSWeaponBase, RTTI 0x181ebdbe0) |
| info +0x38 | m_hInflictor (as CBaseCSGrenadeProjectile, RTTI 0x181ebdc58) |
| info +0x80 | m_flFriendlyFireDamageReductionRatio |
| ability vfn 0xca8, its +0x320 | the ability's vdata |
| projectile +0xb0e | grenade definition index |
| 0x181ec18c0 +0x1470, 0x181ebdc08 (weapon_c4's) | two more classes' items in 180a7ab50 (unread which) |
| message (vtable 0x1819212e8) +0x18 / +0x1c / +0x20 | small / large / ratio |
| weapon services +0xb10 | active weapon |
| movement services (pawn +0xb50) +0x69c | m_flStamina |
| gpGlobals +0x34 | frametime |

## Constants

| Value | What |
|---|---|
| sv_predictable_damage_tag_ticks | object 0x182173a90, int, default 2, flags 0x80000, "Delay player slowdown when damaged by # ticks to reduce misprediction effects" |
| mp_tagging_scale | 0x182175778, float, default 1.0 |
| sv_staminamax | default 80 |
| 1.0 0x181780580, 250 0x18178fe20, 120 0x1817a4470, 130 0x18191a1e0, 80 0x18179bea0, 0.8 0x18178fde4, 170 0x181926a24, 0.08 0x1817ad5d0, 1.2 0x1817ad5dc, 0.25 0x18178fdd8, 0.65 0x18179be5c, 8 0x181780588 | the tag's constants |
| 0.15 0x3e19999a, 0.2 0x3e4ccccd | immediates |
| 40 0x1817ad5f4, 1.05 0x1819218b0 | the projectile's large |
| 0.35 | recovery rate a second |

## The damage hook (180a961f0)

1. Skipped when m_nDamageFlags has bit 0x2.
2. Goes on only if `lVar3 || (lVar4 && 0 < (float)(int)m_flDamageDealt)` (lVar3 the ability as a weapon, lVar4 the inflictor as a projectile): no tag for map damage, fall damage, the C4, a burn without a weapon.
3. 180a7ab50: the ability's vdata, else the projectile's item, else the two other classes. large = +0x838, small = +0x83c.
4. A projectile: `large = min(1.5, (1 - (float)(int)dealt / 40) x 1.05 + large)` (180a963b4..ef: cvttss2si, cvtdq2ps, divss 40, subss from 1.0, mulss 1.05, addss large; 1801783c0 with 1.5 first).
5. sv_predictable_damage_tag_ticks below 1: 180ab76a0(pawn, large, small, ratio) now. Else the message for the pawn's controller through 180574fa0 at tick = 180cacc40(180c86d00(services)) + the cvar.

## The tag (180ab76a0)

Every op as the disassembly orders it (f32):

```
fs     = m_flFlinchStack
stack  = min(fs, min(large, large - (1 - fs) x small))           -> m_flFlinchStack (+0x14dc)
x      = mp_tagging_scale x stack
speed  = the active weapon's GetMaxSpeed (weapon services +0xb10 -> 180c868d0, vfn 0xc20), 250 without one
x      = x x (max(0.15, (speed - 120) / 130) x 0.8 + 0.08)
lo     = max(0.2, (min(1, (speed - 80) / 170) x 1.2 - 0.08) x 0.25)
hi     = maxss(large, 0.65)
v      = clamp(x, lo, hi)
stamina (movement services +0xb50 -> +0x69c) = clamp((1 - v) x 8 + stamina, 0, sv_staminamax)
m_flVelocityModifier = min(m_flVelocityModifier, (v - 1) x ratio + 1)                             (180ae1c90)
```

- The branch at 180ab7790 (no weapon services: vfn 0xcb0, 180a44500 == 2, 180a44650's +0xb10) is an observer's target's (unread).
- Worked: AK-47 (0.4 / 0.55) on a knife holder: stack 0.4, 0.4 x 0.88 = 0.352 in [0.28, 0.65]: 35 % speed, stamina + 5.18. A second hit at once: stack 0.07, under 0.28: 28 %. SMGs' vdata is 0 / 0: every SMG hit floors at lo (0.28 for a 250 weapon).

## The recovery

- 180ac8880 (from 1809669f0): below 1, `stack = Approach(1, stack, frametime x 0.35)`, then `clamp(stack, 0.1, 1)`.
- m_flVelocityModifier: PostMove 180adcb90, +0.4 a second on the ground.
- Spawn 1801f7ca0 sets both to 1.

## Unread

- 180574fa0's queue: when in the victim's command it runs; the client's copy of the message (CS2's client predicts the slowdown at that tick). (damage-prediction.md may hold the queue.)
- The time 180c86d00 reads (services +0x38 -> +0x10 -> +0x38).
- The two other classes in 180a7ab50; the inferno's ability; TakeDamageFlags_t bit 0x2's name; the Think's place in the frame.
