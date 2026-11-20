# Weapon selection (slot keys, invnext / invprev, binds)

client_20261015. cfg/user_keys_default.vcfg (installed CS2, 2026-11-21). SelectSlot itself: [taser-client.md](taser-client.md) "slot3"; GetNextBestWeapon after a throw: [grenades.md](grenades.md) "After the throw".

## Functions

| Address | Module | What |
|---|---|---|
| 0x18256a568[slot] | client | the split screen's HUD weapon selection (CCSHudWeaponSelection, vtable 0x181d21320) |
| 1811a9cb0 | client | vfn 0x248 SelectSlot(n) |
| 1811aa450 | client | vfn 0x2a0: `weapon_hegrenade` |
| 1811aa5d0 | client | vfn 0x2a8: `weapon_flashbang` |
| 1811aa6b0 | client | vfn 0x2b0: `weapon_smokegrenade` |
| 1811aa790 | client | vfn 0x2b8: `weapon_decoy` |
| 1811aa1e0 | client | vfn 0x2c8: `weapon_molotov`, else `weapon_incgrenade` (via 1811a9b20) |
| 1811aad90 | client | slot11 callback (direct): `weapon_taser` |
| 1811a68c0 | client | vfn 0x228 invnext |
| 1811a6980 | client | vfn 0x230 invprev |
| 180c1e5b0 / 180c1e580 | client | vfn 0x2c0 slot12 / vfn 0x2d0 slot13 (13 / 40 bytes): boost (healthshot) / utility slots |
| 1811a9bc0 | client | vfn 0x268 confirm |
| 180c0cc30 | client | vfn 0x258: the weapon at a gear slot position |
| 1811a7530 | client | invnext's walk (mode param_4) |
| 1811a77c0 | client | invprev's walk |
| 1811a9f10 | client | vfn 0x320 select: stores the handle at +0x18 |
| 18096a8f0 | client | local pawn (0) |
| 181123940 | client | string token (vfn 0x148), cached per string-table generation +0x34 |
| 180902f90 | client | held weapon of a vdata name (weapon services pawn[0x25e], token) |
| 18090d6e0 | client | (services) gate before selecting |
| 180c09310 | client | `Player.WeaponSelectionFoley` |
| 1819fc50c | client | C_CSWeaponBase dynamic cast |

## Commands

| Command | Registration (string) | Callback | vfn |
|---|---|---|---|
| slot4 | 1800def30 (0x181c09a8c) | taser-client.md: 180c1e6f0 / 180c19e30 | 0x248 SelectSlot(4) |
| slot6 | 1800df010 (0x181c09a9c) | 180c1f080 | 0x2a0 |
| slot7 / slot8 / slot9 | not read (their vfns sit between slot6's and slot10's) | | 0x2a8 / 0x2b0 / 0x2b8 |
| slot10 | 1800ded70 (0x181c09abc) | 180c1ef60 | 0x2c8 |
| slot11 | 18011ec60 (0x181d208c4) | 1811aad90 | |
| invnext | 1800de020 (0x181c09b10) | 180c1edb0 | 0x228 |
| invprev | 1800de100 (0x181c09b08) | 180c1ee70 | 0x230 |

## Fields

| Offset | Field |
|---|---|
| selection +0x18 | selected weapon handle (-1 none) |
| selection +0x14 | curtime of the last invnext / invprev |
| weapon services +0x48 / +0x50 | m_hMyWeapons count / handles |
| weapon +0x388 | vdata |
| vdata +0x700 / +0x704 | gear slot / gear slot position |
| vdata +0x520 | weapon type (walk modes 1..5) |
| 0x18256aeb8 +0x58 | hud_fastswitch (0) |

## Constants

| Value | What |
|---|---|
| RIFLE 0, PISTOL 1, KNIFE 2, GRENADES 3, C4 4 | gear slots (vdata m_GearSlot) |
| hegrenade 0, flashbang 1, smokegrenade 2, decoy 3, molotov / incgrenade 4; knife 0, taser 1 | positions (weapons.vdata m_GearSlotPosition) |
| (0xd, 9999) | invprev's start key when nothing is active |

## The class pickers (1811aa450 ...)

- Local pawn alive (vfn 0x4f0) and vfn 0xab8; 180902f90 finds the held weapon; 18090d6e0(services) true -> vfn 0x320 and vfn 0x268. No `Player.WeaponSelectionFoley`.

## invnext / invprev callbacks

- vfn 0x2e8 true -> vfn 0x228 / 0x230; then vfn 0x268 only when hud_fastswitch > 0; +0x14 = curtime.

## Confirm (vfn 0x268, 1811a9bc0)

- No selected weapon (vfn 0x270) -> `cancelselect`; selected weapon's vfn 0x998 false -> `Player.DenyWeaponSelection` from the pawn; else vfn 0x260 (the switch), +0x18 = -1, `cancelselect`.

## The orders

- **vfn 0x258** (180c0cc30): gear slot < 6 and position < 0x14; over m_hMyWeapons: vfn 0x9e0 and 0x998 true (hud_fastswitch 2: only 0x9e0), vfn 0xa08 (gear slot) equal, vfn 0xa10 (position) >= the asked and <= the best so far: the lowest position at or after the asked one, the last of equal ones.
- **SelectSlot** (1811a9cb0): gear slot n - 1; the active weapon in it -> position + 1, else 0; nothing there -> position 0. slot4 cycles the grenades in position order and wraps; from another weapon it brings out the lowest position.
- **1811a7530** (mode 0 here): each m_hMyWeapons entry a C_CSWeaponBase, vfn 0x998 true; the lowest (gear slot, position) strictly after the asked one, strict compares (first of equal keys wins). 1811a68c0: after the active weapon's; none -> after (-1, -1); then vfn 0x320 + vfn 0x268. No foley. Modes 1..5 filter by vdata +0x520 (unused here).
- **1811a77c0**: the highest (gear slot, position) strictly before the asked one. 1811a6980: before the active one's (a non-CS weapon active keeps it), none -> before (0xd, 9999); vfn 0x320, vfn 0x268, and `Player.WeaponSelectionFoley` (180c09310) when it isn't the active weapon.
- invnext from the rifle: pistol, knife, Zeus, HE, flash, smoke, decoy, molotov, C4, rifle.
- A pick during a throw waits as m_hSwitchToWeaponAfterThrow (grenades.md "After the throw").

## Binds (cfg/user_keys_default.vcfg)

- MWHEELDOWN invnext, MWHEELUP invprev, 6..9 slot6..slot9, 0 slot10, X slot12. +jump on a wheel direction is the scroll jump (the tick's jump press).

## Unread

- vfn 0x998 (a weapon that can't be selected) and vfn 0x9e0.
- slot7..9's registrations.
- lastinv (the pawn's m_hLastWeapon).
- m_hMyWeapons' order (pickup order).
