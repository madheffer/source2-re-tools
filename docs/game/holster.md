# Holster: putting a weapon away

server_20261105 (sha256 70c66e85...). Called by Weapon_Switch (weapon services vfn 0xf0, 180b23d70; switchhands.md 3) on the weapon being put away, before the new one's Deploy (vfn 0xa18, fire-gate.md 5); a switchhands holsters and redeploys the same one.

## Functions

| Address | Module | What |
|---|---|---|
| 180a041f0 | server | weapon vfn 0xa20 for every class read: `jmp [vtable + 0xd40]` |
| 180a04200 | server | vfn 0xd40, the base (CCSWeaponBase, CKnife) |
| 180a042f0 | server | vfn 0xd40, the gun's (CCSWeaponBaseGun, CWeaponElite), then the base |
| 180a041c0 | server | vfn 0xd40, CC4: m_bStartedArming -> 1809f6a20; then the base |
| 1809f6a20 | server | C4 arming called off (unread) |
| 180a2d5a0 | server | vfn 0xd40, CWeaponTaser: the taser leaves, then the gun's |
| 180187770 | server | ConVar value (+0x58) |
| 180b7c4a0 | server | weapon vfn 0xaa8: the ammo checks over vfn 0xa98 / 0xaa0 / 0xa88 |
| 180b01b60 | server | (services, weapon, 0, 0): the taser leaves (unread) |
| 1809c1000 | server | vfn 0xd40, CBaseCSGrenade |
| 180b54f20 | server | owner pawn |
| 180a0f020 | server | vfn 0xd98: true (every class but CBaseCSGrenade) |
| 1809c8290 | server | vfn 0xd98 of CBaseCSGrenade: false |
| 180b55740 | server | vfn 0xaf0(i): the ammo count (+0xec8[i] or the owner's) |
| 1801541a0 | server | pawn vfn 0x550: pawn +0x2d8 == 0 |
| 180c85ed0 | server | weapon services drop |
| 180c30c10 | server | remove entity |
| 1809f7840 | server | (weapon, activity, flags, 0, force): set the gameplay activity (m_iWeaponGameplayAnimState) |
| 180a276f0 | server | attack clocks move (fire-gate.md 5): only for flags & 0x1b |
| 180927cb0 | server | now |
| 18017e2d0 | server | f32 three-way compare of now with +0xfc0: -1 when +0xfc0 > now, 1 when now > +0xfc0, 0 equal, 0x80 unordered |
| 180b763d0 / 180b76450 | server | set the attack clocks (value, mode) |
| 180a02230 | server | grenade's owner |

## Vtables

| Class | Vtable | vfn 0xd40 |
|---|---|---|
| CCSWeaponBase | 0x1818ec818 | 180a04200 |
| CKnife | 0x1819154a0 | 180a04200 |
| CCSWeaponBaseGun | 0x1818f0d38 | 180a042f0 |
| CWeaponElite | 0x181912698 | 180a042f0 |
| CC4 | 0x1818ef218 | 180a041c0 |
| CWeaponTaser | 0x181919110 | 180a2d5a0 |
| CBaseCSGrenade | 0x1818e7f18 | 1809c1000 |

## Fields

| Offset | Field |
|---|---|
| CCSWeaponBase +0xf70 | m_weaponMode |
| CCSWeaponBase +0xf9c | m_bBurstMode |
| CCSWeaponBase +0xfa8 | m_bInReload |
| CCSWeaponBase +0xfac | m_nDeployTick |
| CCSWeaponBase +0xfbc | m_bIsHauledBack |
| CCSWeaponBase +0xfbd | m_bSilencerOn |
| CCSWeaponBase +0xfc0 | m_flTimeSilencerSwitchComplete |
| gun +0x1280 | m_zoomLevel |
| gun +0x1284 | m_iBurstShotsRemaining |
| CBaseCSGrenade +0x1280 | m_bRedraw |
| CBaseCSGrenade +0x1281 | m_bIsHeldByPlayer |
| CBaseCSGrenade +0x1282 | m_bPinPulled |
| CBaseCSGrenade +0x1283 | m_bJumpThrow |
| CBaseCSGrenade +0x1284 | m_bThrowAnimating |
| CBaseCSGrenade +0x1288 | m_fThrowTime |
| CBaseCSGrenade +0x128c | m_flThrowStrength |
| CC4 +0x12c9 | m_bStartedArming |
| weapon +0xec8[i] | ammo |
| pawn +0x2d8 | read by vfn 0x550 (== 0) |

## Constants

| Value | What |
|---|---|
| mp_taser_recharge_time (cvar 0x182136e70) | "Determines recharge time for taser. -1 = disabled." |
| activity 0xa | holster |

## The base (180a04200)

1. No owner pawn (180b54f20): nothing.
2. m_bInReload = 0; m_bIsHauledBack = 0 (each a network-state change when it changes).
3. vfn 0xd98 true -> step 5.
4. (Grenades) vfn 0xaf0(0) <= 0 and pawn vfn 0x550: dropped (180c85ed0) and removed (180c30c10): an empty grenade goes when put away. Returns.
5. `1809f7840(weapon, 0xa, flags 0, 0, force 1)`: flags 0, so no attack clock moves.

## The gun's (180a042f0)

1. Silencer switch in progress: now (180927cb0) compared with m_flTimeSilencerSwitchComplete (+0xfc0) by 18017e2d0; unless now is past it: +0xfc0 = 0, both attack clocks = now (180b763d0 / 180b76450 with 0.0, mode 0).
2. vfn 0xcc8 (has zoom levels, fire-gate.md 5): m_zoomLevel = 0, m_weaponMode = 0.
3. The base.

## CWeaponTaser (180a2d5a0)

mp_taser_recharge_time < 0 and vfn 0xaa8 and an owner with weapon services: 180b01b60(services, weapon, 0, 0); then the gun's.

## The grenade's (1809c1000)

m_bRedraw, m_bPinPulled, m_bJumpThrow = 0, m_fThrowTime = 0.0; with an owner (180a02230) and vfn 0xaf0(0) <= 0: dropped and removed (180c85ed0, 180c30c10); then the base (its step 4 checks again).

## Unread

1809f6a20 (the C4's arming abort); 180b01b60 (the taser's leaving).
