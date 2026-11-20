# The knife: its swing's sounds and its gate (traced 2026-11-11; server/cs2web/combat/combat.js knife, client/core/game.js knifehit, sim/src/combat/knife_gate.rs)

server_20261105.dll, tools/re (fnstrings.py, disasm.py). The swing itself (reach, traces, backstab, damage) is in
sim/src/combat/knife.rs's header; this is what 180a2fa80 plays once it hit.

- A hit is a fraction below 1 or a start in solid (180a30181 / [rbp+0x14b]); a miss (180a30b99) plays nothing here
  (the swing's whoosh is the viewmodel graph's).
- rsi = the trace's entity ([rbp+0x98]). 180a304ed: **its vfn 0x558 (IsPlayer)**:
  - a player (a teammate too: the second trace's plain filter can hit one): the name by r12d (1 = the stab) and r13b
    (the backstab): **Weapon_Knife.Hit.Light.Flesh / .Heavy.Flesh / .Light.Backstab.Flesh / .Heavy.Backstab.Flesh**
    (180a3053e..567), the filter from the knife (1809f3e40) with the victim added (180c8b610), the sound's entity
    **the victim** (1813aa290 on rsi), emitted by 180f697b0; then the "KnifeSlash" impact (180a30829);
  - anything else (the world, a map entity): **Weapon_Knife.HitWall** (180a30868), its entity **the knife**
    (1813aa290 on r14), after the impact decal (180c8c8d0).
- The port played Weapon_Knife.Hit (CS:GO's flesh hit) for every hit, so a wall slash sounded like stabbing someone
  (yourself, hugging a wall). Now the server's `knifehit` event names the victim (`v`), the stab (`h`) and the backstab
  (`b`); the client plays HitWall from the attacker or the .Flesh event from the victim.
- The four .Flesh events are in the stock sound bake (bake/SoundBake.cs StockEvents, rebaked 2026-11-11 with their
  chained Thud / .Add events and 30 files). Left: the impact effects (KnifeSlash, the decal) aren't drawn.

## The gate (traced 2026-11-11, the "knife-interp" session; sim/src/combat/knife_gate.rs, src/cs2web/player/loadout.js knifeFire)

server_20261105.dll, tools/re (rtti, vslot, disasm) and Ghidra ReVa. **CKnife's vtable 0x1819154a0**: slot 0xcf0
PrimaryAttack **180a2f170** = `swing(this, 0)`, 0xcf8 SecondaryAttack **180a2f500** = `swing(this, 1)`, both return 0;
0xd00 ItemPostFrame = CCSWeaponBase's **180a0f4b0** (no override), 0xd08 ItemBusyFrame 180a0f050, 0xa18 Deploy
**180a2b1a0**, 0xa20 Holster 180a041f0 (the base's), 0xa88 **180a2d590** (`mov al, 1`), 0xd28 1809c7bb0.

**180a0f4b0 for the knife**, in order (180b5ceb0(w, mask): the button held; 180b5d3c0 / 180b5d470: the primary /
secondary clock reached, 180cacba0's now against 1813b8ef0(+0xeb0 / +0xeb4, resp. +0xeb8 / +0xebc), ticks then ratios):
1. attack (1) held and the primary reached: **180a0fac0** (the primary branch): vfn 0xac0(0) (m_iMaxClip1: the
   knife's 0) == 0 -> m_bFireOnEmpty (+0xf50) = 1; return 0 in the freeze period (gamerules +0xd8), defusing (pawn
   +0x14be) or pawn +0xd40; m_iShotsFired (+0x14d8) >= 1 and (vfn 0xb98 IsFullAuto false or vfn 0xac0(0) == 0): return
   0 (the knife is neither: no knife code writes +0x14d8, Deploy zeroes it); **m_bWaitForNoAttack (+0x14f0): return 0**;
   vfn 0xd28 (revolver) no; vfn 0xc60 (the weapon type) != 9: the weapon_fire event (180a0fbbe..fd45); +0x1038 / 1809f5710
   (inspect, not read); **vfn 0xcf0, PrimaryAttack**; +0x1038 = curtime; returns PrimaryAttack's 0 (so no 180b7a170).
2. else 0x400000000 (attack 3: unbound).
3. else attack 2 (0x800) held and the secondary reached: 180a10200 -> (vfn 0xd28 false) 1809f9b80: the pawn, vfn
   0xa88 (true), vfn 0xcc8 / the controller +0x388 bit 8 / a cvar (the return value only), vfn 0xac0(1) (m_iMaxClip2 0)
   != -1 with vfn 0xaf0(1) == 0 -> m_bFireOnEmpty = 1; **vfn 0xcf8, SecondaryAttack**. No m_bWaitForNoAttack test.
4. else the reload key (0x2000): not reloading (+0xfa8): 1809fb150 == 0 and gameplay state (+0xefc) != 0x32 -> 1809f9f70
   (unread); 180b5d3c0 -> 180a10140 (Reload: refused for a knife). The no-attack branch isn't reached.
5. else 0x100000000 (inspect, not ported); then with none of 0x400000801 held: 180a10400, **m_bFireOnEmpty = 0,
   m_bWaitForNoAttack = 0, m_iShotsFired = 0**, the empty reload (vfn 0xa98 false for the knife), +0x10a0 / +0x10b8.
6. 0x800000000 -> 180a23e30 (not read).

**The swing 180a2fa80 before its traces** (180a2fa96..180a2fcd3): no pawn, defusing (+0x14be) or the freeze period
(gamerules +0xd8): return at once, no clock moved. The byte [rbp + 0x420], read by the damage 180a2b280 (the slash's
40 against 25): **m_bFirstAttack (+0x1280) set, or (float)(now's tick - m_nNextPrimaryAttackTick (+0xeb0)) x
0.015625 (180308890: 0x181784dec) > 0.4 (0x18178fde0)**: now from the weapon's time domain (180927c50: gpGlobals +0x44),
an int subtraction, cvtdq2ps, mulss, comiss; the ratio isn't read; computed for the stab too. m_bFirstAttack = 0
(180a2ec50 notify, 180a2fb88). Then **1809f9910(weapon, &info, delay, attack)** with delay 1.0 (0x181780580) for attack
1, 0.4 (the same 0x18178fde0) else, and weapon +0xfe8 = &info. **1809f9910** (fire-gate.md 3's clock step,
fire_gate.rs `clock_step`): now (180cacba0), GetWeaponAttackTime 180a02c60, +0x10c0 = (attack - (now + 1 tick))
(1813b9aa0, 1813b8fb0, cvtdq2ps + addss), with info +0x38 set each clock before now (ticks, then ratios: comiss, 0xff)
set to now, then 180b763d0(delay, 1) and 180b76450(delay, 1): **both clocks + the delay from themselves** (with
m_bLinkedCooldowns each would move the other too: the knives' vdata leaves +0x4c6 at the constructor's 0, 1809afbb0's
`mov qword [rdi + 0x4c4], 1`).

**The knife's Deploy 180a2b1a0**: the base 1809fb560 (fire-gate.md 5: m_iShotsFired 0, m_bWaitForNoAttack 1, both
clocks now + m_flDeployDuration (weapons.vdata's knives: 1) not earlier, the pawn's m_flNextAttack), false -> false;
then the weapon services' (pawn +0xb10) m_flNextAttack (+0xc0) = curtime + 1.0 (0x181780580, 18017dc70), and
**m_bFirstAttack (+0x1280) = 1**.

weapons.vdata's knives (lasers-bake --weapons, lib/weapons-cs2.js CS2_KNIVES): weapon_knife / weapon_knife_t
m_iMaxClip1 0, m_iMaxClip2 0, m_bIsFullAuto false, m_flDeployDuration 1, no m_bLinkedCooldowns.

The port had KNIFE's cycles in seconds on one clock (L.nextAttack), a held slash swinging after a draw, and the slash's
40 / 25 from the last swing's own time (combat.js p.knifeTick). Checked: cargo test knife_gate (3), fire-gate-test 9,
sim-test ze_hold_em_p 12 90 (knife infections). Not ported: the inspect (0x100000000), 1809f9f70, the weapon_fire
event for a knife, the client viewmodel's knife on its frame clock (it follows the same rules there).
