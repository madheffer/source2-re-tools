# Tagging: the slowdown on being hit (server_20261105, traced 2026-11-20, session "nade-players")

A hit slows its victim through m_flVelocityModifier (CCSPlayerPawn +0x14e0, the map's "runspeed" too) and adds to the
movement services' m_flStamina. How much depends on the attacker's weapon (weapons.vdata
m_flFlinchVelocityModifierLarge / Small, CCSWeaponBaseVData +0x838 / +0x83c), on how hard the victim was hit lately
(m_flFlinchStack, pawn +0x14dc) and on the victim's own weapon speed. Ported in web/server/cs2web/combat/tagging.js
(tagging-test.mjs); the movement's recovery of the modifier was already CS2's (sim/src/movement/post.rs: PostMove
180adcb90, +frametime x 0.4 on the ground).

## The damage hook 180a961f0(damage services, CTakeDamageResult*) (caller 180a94400)

- Skipped when the result's m_nDamageFlags (+0x48) has bit 0x2 (TakeDamageFlags_t: name unread).
- The pawn: services +0x38 (180c856b0 fills it).
- lVar3 = m_hAbility (info +0x40) as a CCSWeaponBase (RTTI 0x181ebdbe0), lVar4 = m_hInflictor (info +0x38) as a
  CBaseCSGrenadeProjectile (0x181ebdc58). Only `lVar3 || (lVar4 && 0 < (float)(int)m_flDamageDealt)` (result +0x20)
  goes on: no tag for the map's damage, fall damage, the C4, a burn without a weapon.
- **180a7ab50(info, &, &vdata, &)** finds the vdata: the ability's (vfn 0xca8, its +0x320), else the projectile's item
  (projectile +0xb0e: the grenade's definition index -> 18102cf10 -> 1809be8c0), else two more classes (0x181ec18c0
  with its +0x1470 item, 0x181ebdc08 with weapon_c4's: unread which). large = vdata +0x838 (0 with none), small =
  +0x83c.
- A projectile: `large = min(1.5, (1 - (float)(int)dealt / 40) x 1.05 + large)` (180a963b4..ef: cvttss2si,
  cvtdq2ps, divss 40 0x1817ad5f4, subss from 1.0, mulss 1.05 0x1819218b0, addss large; 1801783c0 with 1.5 first).
- **sv_predictable_damage_tag_ticks** (object 0x182173a90, int, default **2**, flags 0x80000, "Delay player slowdown
  when damaged by # ticks to reduce misprediction effects"): below 1 -> 180ab76a0(pawn, large, small, info +0x80
  m_flFriendlyFireDamageReductionRatio) now; else a message (vtable 0x1819212e8: +0x18 small, +0x1c large, +0x20 the
  ratio) for the pawn's controller (1801c8ce0) through 180574fa0(controller, msg, 0x182121c38, tick, ...) with
  tick = 180cacc40(180c86d00(services)) + the cvar (a time rounded up to a tick: 1813b8ef0, +1 with a fraction).
  Its handler **18097b670**: the controller's pawn (180b55040) -> 180ab76a0(pawn, +0x1c, +0x18, +0x20).
  UNREAD: 180574fa0's queue (when in the victim's command it runs; the client's copy of the message, which lets CS2's
  client predict the slowdown at that tick), the time 180c86d00 reads (services +0x38 -> +0x10 -> +0x38).

## The tag 180ab76a0(pawn, large xmm1, small xmm2, ratio xmm3)

Every op as the disassembly orders it (f32), with 1801783c0 `min(a, b) = b <= a ? b : a`, 1801783b0
`max(a, b) = a <= b ? b : a`, 18017b8d0 `clamp(v, lo, hi) = lo <= v ? (v <= hi ? v : hi) : lo`:

```
fs     = m_flFlinchStack
stack  = min(fs, min(large, large - (1 - fs) x small))           -> m_flFlinchStack (+0x14dc)
x      = mp_tagging_scale x stack                                  (mp_tagging_scale 0x182175778: float, default 1.0)
speed  = the active weapon's GetMaxSpeed (weapon services +0xb10 -> 180c868d0, vfn 0xc20), 250 without one
x      = x x (max(0.15, (speed - 120) / 130) x 0.8 + 0.08)
lo     = max(0.2, (min(1, (speed - 80) / 170) x 1.2 - 0.08) x 0.25)
hi     = maxss(large, 0.65)
v      = clamp(x, lo, hi)
stamina (movement services +0xb50 -> +0x69c) = clamp((1 - v) x 8 + stamina, 0, sv_staminamax)   (default 80)
m_flVelocityModifier = min(m_flVelocityModifier, (v - 1) x ratio + 1)                             (180ae1c90)
```

The weapon branch at 180ab7790 (no weapon services: vfn 0xcb0, 180a44500 == 2, 180a44650's +0xb10) is an observer's
target's: unread, not needed for a pawn. Constants: 1.0 0x181780580, 250 0x18178fe20, 120 0x1817a4470, 130
0x18191a1e0, 80 0x18179bea0, 0.8 0x18178fde4, 170 0x181926a24, 0.08 0x1817ad5d0, 1.2 0x1817ad5dc, 0.25 0x18178fdd8,
0.65 0x18179be5c, 8 0x181780588, 0.15 0x3e19999a and 0.2 0x3e4ccccd as immediates.

Worked: an AK-47 hit (0.4 / 0.55) on a knife holder: stack 0.4, 0.4 x 0.88 = 0.352 in [0.28, 0.65]: 35 % speed,
stamina + 5.18. A second hit at once: stack 0.07, the product under 0.28: 28 %. SMGs' vdata says 0 / 0: every SMG
hit floors the victim at lo (0.28 for a 250 weapon).

## The recovery

- **CCSGameRules::Think 1809669f0** walks every player pawn (vfn 0x558 and vfn 0xca8) and calls **180ac8880**:
  below 1, `stack = Approach(1, stack, gpGlobals frametime (+0x34) x 0.35)` (180460960: `speed < t - v` -> v + speed,
  `t - v < -speed` -> v - speed, else t), then `clamp(stack, 0.1, 1)`.
- The velocity modifier: PostMove's +0.4 a second on the ground (sim/src/movement/post.rs).
- The spawn (1801f7ca0) sets both to 1.

## The port and what's left

- tagging.js flinchOf / tag / Tagging (hit after hurtPlayer's health, due() in game.js preThink before each command's
  movement, think() at the frame's start, reset() at the spawn); the bake carries the guns' flinchLarge / flinchSmall
  (WeaponBake.cs), the grenades' and knives' raw vdata fields and their m_flMaxSpeed pair.
- Stand-ins: the queue runs before the victim's first command at or after its tick (180574fa0 unread); the client
  learns the slowdown from the acked move state (runSpeed), a round trip after the server applies it (CS2's client gets
  the message and predicts it); the Think's place in the frame (the tick's start here); the inferno's damage (its
  ability unread: no tag); m_nDamageFlags bit 0x2 (nothing here sets it); teammates take no damage in a team match
  (comp.js), so the ratio is always 1.
