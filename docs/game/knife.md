# The knife: its swing's sounds and its gate

server_20261105. weapons.vdata's knives.

## Functions

| Address | Module | What |
|---|---|---|
| 180a2fa80 | server | the swing (this, attack); plays the hit sound after its traces |
| 180a2f170 | server | CKnife PrimaryAttack (vtable slot 0xcf0) = `swing(this, 0)`, returns 0 |
| 180a2f500 | server | CKnife SecondaryAttack (0xcf8) = `swing(this, 1)`, returns 0 |
| 180a0f4b0 | server | ItemPostFrame (0xd00), CCSWeaponBase's (no override) |
| 180a0f050 | server | ItemBusyFrame (0xd08) |
| 180a2b1a0 | server | CKnife Deploy (0xa18) |
| 180a041f0 | server | Holster (0xa20), the base's |
| 180a2d590 | server | slot 0xa88: `mov al, 1` |
| 1809c7bb0 | server | slot 0xd28 |
| 180a2b280 | server | the knife's damage (reads [rbp + 0x420]: the slash's 40 against 25) |
| 180a0fac0 | server | the primary branch of 180a0f4b0 |
| 180a10200 | server | the secondary branch -> 1809f9b80 |
| 180a10140 | server | Reload (refused for a knife) |
| 180a10400 | server | the no-buttons branch |
| 180a23e30 | server | 0x800000000 branch (not read) |
| 1809f9f70 | server | reload-key path (unread) |
| 1809fb150 | server | reload-key test (== 0 to go on) |
| 180b5ceb0 | server | (w, mask): button held |
| 180b5d3c0 / 180b5d470 | server | primary / secondary clock reached |
| 180cacba0 | server | now |
| 1813b8ef0 | server | the clock (tick, ratio) read |
| 1809f5710 | server | inspect, with +0x1038 (not read) |
| 180b7a170 | server | not reached (PrimaryAttack returns 0) |
| 180308890 | server | ticks to seconds (x 0.015625, 0x181784dec) |
| 180927c50 | server | weapon's time domain now (gpGlobals +0x44) |
| 180a2ec50 | server | m_bFirstAttack notify |
| 1809f9910 | server | the clock step (weapon, &info, delay, attack) ([fire-gate.md](fire-gate.md) 3) |
| 180a02c60 | server | GetWeaponAttackTime |
| 1813b9aa0 / 1813b8fb0 | server | tick arithmetic in 1809f9910 |
| 180b763d0 / 180b76450 | server | (delay, 1): primary / secondary clock + delay from itself |
| 1809afbb0 | server | weapon constructor: `mov qword [rdi + 0x4c4], 1` |
| 1809fb560 | server | the base Deploy ([fire-gate.md](fire-gate.md) 5) |
| 18017dc70 | server | curtime + delay |
| 1809f3e40 | server | the knife's sound filter |
| 180c8b610 | server | filter: add the victim |
| 1813aa290 | server | the sound's entity |
| 180f697b0 | server | emit sound |
| 180a30829 | server | the "KnifeSlash" impact |
| 180c8c8d0 | server | the impact decal |

## Fields

| Offset | Field |
|---|---|
| weapon +0xeb0 / +0xeb4 | m_nNextPrimaryAttackTick / ratio |
| weapon +0xeb8 / +0xebc | m_nNextSecondaryAttackTick / ratio |
| weapon +0xefc | gameplay state (!= 0x32 for the reload path) |
| weapon +0xf50 | m_bFireOnEmpty |
| weapon +0xfa8 | reloading |
| weapon +0xfe8 | &info (set by the swing) |
| weapon +0x1038 | inspect time; = curtime after PrimaryAttack |
| weapon +0x10a0 / +0x10b8 | written in the no-buttons branch |
| weapon +0x10c0 | (attack - (now + 1 tick)) (cvtdq2ps + addss) |
| weapon +0x1280 | m_bFirstAttack |
| weapon +0x14d8 | m_iShotsFired (no knife code writes it; Deploy zeroes it) |
| weapon +0x14f0 | m_bWaitForNoAttack |
| weapon +0x4c6 | m_bLinkedCooldowns (knives' vdata leaves the constructor's 0) |
| info +0x38 | set when a clock is before now |
| gamerules +0xd8 | freeze period |
| pawn +0x14be | defusing |
| pawn +0xd40 | blocks the primary |
| pawn +0xb10 | weapon services; +0xc0 m_flNextAttack |
| controller +0x388 | bit 8 read in the secondary branch |
| [rbp+0x14b] | start in solid (the hit test) |
| [rbp+0x98] | the trace's entity (rsi) |
| [rbp+0x420] | byte: the heavy-damage test |

## Constants

| Value | What |
|---|---|
| 0x1819154a0 | CKnife's vtable |
| 1 (0x800), 0x2000, 0x400000000, 0x100000000, 0x800000000 | buttons: attack, attack2, reload, attack3 (unbound), inspect, (unread) |
| 0x400000801 | the "none held" mask for the no-buttons branch |
| 1.0 (0x181780580) | primary delay; Deploy's m_flNextAttack delay |
| 0.4 (0x18178fde0) | secondary delay; the heavy-damage threshold |
| 0.015625 (0x181784dec) | tick interval |
| 9 | weapon type (vfn 0xc60) that skips weapon_fire |
| weapon_knife / weapon_knife_t | m_iMaxClip1 0, m_iMaxClip2 0, m_bIsFullAuto false, m_flDeployDuration 1, no m_bLinkedCooldowns |

## The hit's sound (180a2fa80)

- Hit: fraction < 1 or start in solid (180a30181 / [rbp+0x14b]); a miss (180a30b99) plays nothing here (the whoosh is the viewmodel graph's).
- 180a304ed: the trace entity's vfn 0x558 (IsPlayer):
  - a player (a teammate too: the second trace's plain filter can hit one): by r12d (1 = stab) and r13b (backstab):
    **Weapon_Knife.Hit.Light.Flesh / .Heavy.Flesh / .Light.Backstab.Flesh / .Heavy.Backstab.Flesh** (180a3053e..567);
    filter from the knife (1809f3e40) + the victim (180c8b610); entity **the victim** (1813aa290 on rsi); emitted by
    180f697b0; then the "KnifeSlash" impact (180a30829).
  - else (world, map entity): **Weapon_Knife.HitWall** (180a30868), entity **the knife** (1813aa290 on r14), after the impact decal (180c8c8d0).
- The four .Flesh events chain Thud / .Add events.

## ItemPostFrame for the knife (180a0f4b0)

Clocks: 180cacba0's now against 1813b8ef0(+0xeb0 / +0xeb4, resp. +0xeb8 / +0xebc), ticks then ratios.

1. attack (1) held and primary reached: 180a0fac0: vfn 0xac0(0) (m_iMaxClip1 0) == 0 -> +0xf50 = 1; return 0 in the
   freeze period (gamerules +0xd8), defusing (+0x14be) or pawn +0xd40; +0x14d8 >= 1 and (vfn 0xb98 IsFullAuto false or
   vfn 0xac0(0) == 0): return 0; **+0x14f0 set: return 0**; vfn 0xd28 (revolver) no; vfn 0xc60 != 9: weapon_fire event
   (180a0fbbe..fd45); +0x1038 / 1809f5710; **vfn 0xcf0 PrimaryAttack**; +0x1038 = curtime; returns 0.
2. else 0x400000000 (attack 3).
3. else attack 2 (0x800) held and secondary reached: 180a10200 -> (vfn 0xd28 false) 1809f9b80: the pawn, vfn 0xa88 (true),
   vfn 0xcc8 / controller +0x388 bit 8 / a cvar (return value only), vfn 0xac0(1) (m_iMaxClip2 0) != -1 with vfn
   0xaf0(1) == 0 -> +0xf50 = 1; **vfn 0xcf8 SecondaryAttack**. No m_bWaitForNoAttack test.
4. else reload (0x2000): not reloading (+0xfa8): 1809fb150 == 0 and +0xefc != 0x32 -> 1809f9f70; 180b5d3c0 -> 180a10140.
   The no-attack branch isn't reached.
5. else 0x100000000 (inspect); then with none of 0x400000801 held: 180a10400, **+0xf50 = 0, +0x14f0 = 0, +0x14d8 = 0**,
   the empty reload (vfn 0xa98 false for the knife), +0x10a0 / +0x10b8.
6. 0x800000000 -> 180a23e30.

## The swing before its traces (180a2fa96..180a2fcd3)

1. No pawn, defusing (+0x14be) or freeze period (gamerules +0xd8): return, no clock moved.
2. [rbp + 0x420] = **+0x1280 set, or `(float)(now's tick - +0xeb0) * 0.015625 > 0.4`** (now from 180927c50; int
   subtraction, cvtdq2ps, mulss, comiss; the ratio isn't read); computed for the stab too.
3. +0x1280 = 0 (180a2ec50 notify, 180a2fb88).
4. 1809f9910(weapon, &info, delay, attack), delay 1.0 for attack 1, 0.4 else; +0xfe8 = &info.

## The clock step (1809f9910)

1. now (180cacba0), GetWeaponAttackTime 180a02c60, +0x10c0 = (attack - (now + 1 tick)) (1813b9aa0, 1813b8fb0, cvtdq2ps + addss).
2. With info +0x38, each clock before now (ticks, then ratios: comiss, 0xff) is set to now.
3. 180b763d0(delay, 1) and 180b76450(delay, 1): **both clocks + the delay from themselves** (with m_bLinkedCooldowns
   each would move the other too).

## Deploy (180a2b1a0)

1. Base 1809fb560 (m_iShotsFired 0, m_bWaitForNoAttack 1, both clocks now + m_flDeployDuration (knives: 1) not
   earlier, the pawn's m_flNextAttack); false -> false.
2. Weapon services' (pawn +0xb10) m_flNextAttack (+0xc0) = curtime + 1.0 (18017dc70).
3. **+0x1280 = 1**.

## Unread

The inspect (0x100000000), 1809f9f70, 180a23e30, 1809f5710.
