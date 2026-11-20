# Holster: putting a weapon away (traced 2026-11-11)

Build: **server_20261105.dll** (sha256 70c66e85...). Tools: tools/re/game/vslot.py, disasm_consts.py, schema.py, xref.py,
fnstrings.py. Called by Weapon_Switch (weapon services vfn 0xf0, 180b23d70; switchhands.md 3) on the weapon being
put away, before the new one's Deploy (vfn 0xa18, fire-gate.md 5); a switchhands holsters and redeploys the same one.

## The slots

Weapon **vfn 0xa20 = 180a041f0** for every class read (CCSWeaponBase 0x1818ec818, CCSWeaponBaseGun 0x1818f0d38,
CKnife 0x1819154a0, CBaseCSGrenade 0x1818e7f18, CC4 0x1818ef218, CWeaponElite 0x181912698, CWeaponTaser
0x181919110): `jmp [vtable + 0xd40]`. vfn 0xd40:

| Class | vfn 0xd40 |
|---|---|
| CCSWeaponBase, CKnife | **180a04200** (the base) |
| CCSWeaponBaseGun, CWeaponElite | **180a042f0** (the gun's, then the base) |
| CC4 | **180a041c0**: m_bStartedArming (+0x12c9) -> 1809f6a20 (the arming called off, unread); then the base |
| CWeaponTaser | **180a2d5a0**: mp_taser_recharge_time (cvar 0x182136e70, "Determines recharge time for taser. -1 = disabled.", value at ConVar +0x58 by 180187770) < 0 and vfn 0xaa8 (180b7c4a0: the ammo checks over vfn 0xa98 / 0xaa0 / 0xa88) and an owner with weapon services: 180b01b60(services, weapon, 0, 0) (unread: the taser leaves); then the gun's |
| CBaseCSGrenade | **1809c1000** |

## The base, 180a04200

1. No owner pawn (180b54f20): nothing.
2. **m_bInReload** (+0xfa8) = 0; **m_bIsHauledBack** (+0xfbc) = 0 (each a network-state change when it changes).
3. vfn 0xd98 (180a0f020 true for every class but CBaseCSGrenade's 1809c8290 false): true -> step 5.
4. (Grenades) vfn 0xaf0(0) (180b55740: the ammo count, +0xec8[i] or the owner's) <= 0 and the pawn's vfn 0x550
   (1801541a0: pawn +0x2d8 == 0): the weapon services drop it (180c85ed0) and it is removed (180c30c10): **an empty
   grenade goes when put away**. Returns.
5. **1809f7840(weapon, activity 0xa, flags 0, 0, force 1)**: the gameplay activity "holster" (m_iWeaponGameplayAnimState);
   flags 0, so no attack clock moves (fire-gate.md 5's 180a276f0 runs only for flags & 0x1b).

## The gun's, 180a042f0

1. **A silencer switch in progress** (ported 2026-11-11: src/cs2web/sim/zoom.js holsterZoom): now (180927cb0) compared with m_flTimeSilencerSwitchComplete (+0xfc0) by
   18017e2d0 (-1 when +0xfc0 > now, 1 when now > +0xfc0, 0 equal, 0x80 unordered); unless now is past it:
   +0xfc0 = 0, **both attack clocks = now** (180b763d0 / 180b76450 with 0.0, mode 0).
2. vfn 0xcc8 (has zoom levels, fire-gate.md 5): **m_zoomLevel** (+0x1280) = 0, **m_weaponMode** (+0xf70) = 0.
3. The base.

## The grenade's, 1809c1000

**m_bRedraw** (+0x1280), **m_bPinPulled** (+0x1282), **m_bJumpThrow** (+0x1283) = 0, **m_fThrowTime** (+0x1288) =
0.0; with an owner (180a02230) and vfn 0xaf0(0) <= 0: dropped and removed (180c85ed0, 180c30c10); then the base (its
step 4 checks again).

Fields (schema.py, CCSWeaponBase): m_weaponMode 0xf70, m_bBurstMode 0xf9c, m_bInReload 0xfa8, m_nDeployTick 0xfac,
m_bIsHauledBack 0xfbc, m_bSilencerOn 0xfbd, m_flTimeSilencerSwitchComplete 0xfc0, m_iBurstShotsRemaining 0x1284,
m_zoomLevel 0x1280 (the gun's); CBaseCSGrenade m_bRedraw 0x1280, m_bIsHeldByPlayer 0x1281, m_bPinPulled 0x1282,
m_bJumpThrow 0x1283, m_bThrowAnimating 0x1284, m_fThrowTime 0x1288, m_flThrowStrength 0x128c; CC4 m_bStartedArming
0x12c9.

## What the port does

src/cs2web/player/loadout.js `holster(L)`, run by selectSlot on the old weapon and by switchhands before Deploy: the reload
lost, the R8's hammer down (L.rev.hauled), a grenade's pin back and throw called off (L.nade). The viewmodel's
_deploy does the same on the client (its _nade, _rev.hauled). The silencer switch and zoom resets are ported (src/cs2web/sim/zoom.js holsterZoom, 2026-11-11). Not ported: the
C4's arming abort (1809f6a20 unread; no planting here), the taser's drop, the
empty grenade's removal (a thrown grenade already leaves the slot), the holster activity.
