# CS2's weapon selection: slot keys, invnext / invprev, the binds

client_20261015.dll (ReVa `/client_20261015.dll`; tools/re strva / riprefs / vtdump / disasm on source2-compiler's
tools/re/binaries copy), 2026-11-21. Ported in web/src/cs2web/player/weapon-select.js (the picks, shared),
web/src/cs2web/client/core/weapon-pick.js (the client's HUD selection), web/src/cs2web/player/loadout.js
(currentNade / selectSlot's grenade), web/server/cs2web/grenades/grenades.js afterThrow (GetNextBestWeapon: its trace is
docs/game/grenades.md "After the throw"). The binds are cfg/user_keys_default.vcfg (client/core/binds.js DEFAULTS).
docs/game/taser-client.md "slot3" reads SelectSlot itself.

## The commands

Every one is a ConCommand whose callback reaches the split screen's HUD weapon selection (0x18256a568[slot]) and calls
one of its virtuals (CCSHudWeaponSelection vtable 0x181d21320):

| Command | Registration (string) | Callback | vfn | Function |
|---|---|---|---|---|
| slot4 | 1800def30 (0x181c09a8c) | (taser-client.md: 180c1e6f0 / 180c19e30) | 0x248 | 1811a9cb0 SelectSlot(4) |
| slot6 | 1800df010 (0x181c09a9c) | 180c1f080 | 0x2a0 | 1811aa450: `weapon_hegrenade` |
| slot7 | | | 0x2a8 | 1811aa5d0: `weapon_flashbang` |
| slot8 | | | 0x2b0 | 1811aa6b0: `weapon_smokegrenade` |
| slot9 | | | 0x2b8 | 1811aa790: `weapon_decoy` |
| slot10 | 1800ded70 (0x181c09abc) | 180c1ef60 | 0x2c8 | 1811aa1e0: `weapon_molotov`, else `weapon_incgrenade` (via 1811a9b20) |
| slot11 | 18011ec60 (0x181d208c4) | 1811aad90 (direct) | | `weapon_taser` |
| invnext | 1800de020 (0x181c09b10) | 180c1edb0 | 0x228 | 1811a68c0 |
| invprev | 1800de100 (0x181c09b08) | 180c1ee70 | 0x230 | 1811a6980 |

(slot7..9's registrations weren't read: their vfns sit between slot6's and slot10's in the vtable and name their
classes.) slot12 / slot13 (0x2c0 180c1e5b0 / 0x2d0 180c1e580, 13 / 40 bytes) are the boost (healthshot) and utility
slots; this game has neither.

- **The class pickers** (1811aa450 ...): the local pawn (18096a8f0(0)) alive (vfn 0x4f0) and vfn 0xab8; the class name's
  string token (cached per string-table generation +0x34, 181123940 vfn 0x148); **180902f90**(weapon services
  pawn[0x25e], token) finds the held weapon of that vdata name; 18090d6e0(services) true -> vfn 0x320 (select it:
  1811a9f10 stores its handle at +0x18) and vfn 0x268. No `Player.WeaponSelectionFoley`.
- **invnext / invprev callbacks**: vfn 0x2e8 true -> vfn 0x228 / 0x230; then vfn 0x268 again only when hud_fastswitch
  (0x18256aeb8 +0x58) > 0 (it is 0); +0x14 = curtime.
- **vfn 0x268** (1811a9bc0, confirm): no selected weapon (vfn 0x270) -> `cancelselect`; the selected weapon's vfn 0x998
  false -> `Player.DenyWeaponSelection` from the pawn; else vfn 0x260 (the switch), +0x18 = -1, `cancelselect`.

## The orders

- **vfn 0x258** (180c0cc30, the weapon at a gear slot position): gear slot < 6 and position < 0x14; over the weapon
  services' m_hMyWeapons (+0x48 count, +0x50 handles): vfn 0x9e0 and 0x998 true (hud_fastswitch 2: only 0x9e0), vfn
  0xa08 (gear slot) equal, vfn 0xa10 (position) >= the asked position and <= the best so far: the lowest position at
  or after it, the last of equal ones. (This answers taser-client.md's TODO: "at or after", not exact.)
- **SelectSlot** (vfn 0x248, 1811a9cb0, taser-client.md): gear slot n - 1, the active weapon in it -> position + 1,
  else 0; nothing there -> position 0. So slot4 cycles the grenades in position order and wraps; from any other weapon
  it brings out the lowest position held.
- **1811a7530** (invnext's walk; mode param_4 0 here): m_hMyWeapons, each a C_CSWeaponBase (dynamic cast 1819fc50c),
  vfn 0x998 true; its vdata (+0x388) gear slot +0x700 and position +0x704; the lowest (gear slot, position) strictly
  after the asked one, compares strict (the first of equal keys wins). 1811a68c0: after the active weapon's; none ->
  after (-1, -1), the lowest of all; then vfn 0x320 + vfn 0x268. No foley. (Modes 1..5 filter by vdata +0x520, the
  weapon type: not used by these commands.)
- **1811a77c0** (invprev's): the highest (gear slot, position) strictly before the asked one. 1811a6980: before the
  active one's (its C_CSWeaponBase cast; a non-CS weapon active keeps it), none -> before (0xd, 9999), the highest of
  all; vfn 0x320, vfn 0x268, and `Player.WeaponSelectionFoley` (180c09310) when it isn't the active weapon.
- The gear slots (vdata m_GearSlot): RIFLE 0, PISTOL 1, KNIFE 2, GRENADES 3, C4 4. The positions (weapons.vdata
  m_GearSlotPosition, lib/weapons-cs2.js): hegrenade 0, flashbang 1, smokegrenade 2, decoy 3, molotov / incgrenade 4;
  knife 0, taser 1.
- So invnext from the rifle: pistol, knife, Zeus, HE, flash, smoke, decoy, molotov, C4, the rifle again.

## Ours

- The client picks (it's CS2's client that does: its usercmd carries the weapon). The command's [6] is the loadout slot
  (1..6) or 10 + the grenade's position (move-state.js cleanCmd 0..14); the server's selectSlot takes the grenade at
  that position (loadout.js L.nade, currentNade: the pick, else the lowest position).
- A pick during a throw (the grenade still held, m_bThrowAnimating) waits as m_hSwitchToWeaponAfterThrow
  (combat.js -> L.switchAfterThrow; grenades.md "After the throw").
- TODO(trace): vfn 0x998 (a weapon that can't be selected: skipped by the walks, denied by the confirm) and vfn
  0x9e0 aren't read; every held weapon counts as selectable. slot7..9's registrations, and lastinv (the pawn's
  m_hLastWeapon: the client's own last pick stands in). m_hMyWeapons' order (pickup order): ours lists the knife,
  pistol, primary, Zeus, grenades as bought, C4 (only ties and GetNextBestWeapon's first pick read it).

## Binds

cfg/user_keys_default.vcfg (installed CS2, 2026-11-21) is client/core/binds.js DEFAULTS, key for key in
KeyboardEvent codes (its CTRL / SHIFT are the left keys). Notably MWHEELDOWN invnext, MWHEELUP invprev, 6..9
slot6..slot9, 0 slot10, X slot12. A bind of +jump to a wheel direction is CS2's scroll jump (the tick's jump press,
client/core/input.js). F1 / F2 "vote option1 / 2" are ours (CS2's vote panel answers them).
