# switchhands: changing the viewmodel's hand

server_20261105 (sha256 70c66e85...), client_20261105 (sha256 92794218 52772522...); disassembly only, no decompiler. game/csgo/cfg/user_keys_default.vcfg:29 `"h" "switchhands"` (`:27` `"f" "+lookatweapon"`).

H flips the hand the client wants; the usercmd carries it (`left_hand_desired`); the server's weapon timing graph sees it differ from the pawn's `m_bLeftHanded` and calls Weapon_Switch on the held weapon with reason 4, which flips the hand, stamps `m_fSwitchedHandednessTime` and holsters and redeploys the same weapon (the draw plays again, with its attack lock). The client draws the arms mirrored and for 0.2 s after the stamp dips them 40 degrees.

## Functions

| Address | Module | What |
|---|---|---|
| 1800e7720 | client | registers `switchhands` (flags 0x80000, no help) -> 180ca4700 (toggle) |
| 1800e7790 | client | registers `switchhandsleft` -> 180ca4780 (set left) |
| 1800e7800 | client | registers `switchhandsright` -> 180ca47f0 (set right) |
| 1800e47a0 | client | registers `cl_prefer_lefthanded` |
| 180ca4700 / 180ca4780 / 180ca47f0 | client | the callbacks |
| 18096c1c0 | client | (0): local pawn |
| 18094f530 | client | C_CSPlayerPawn vfn 0x4f0: true |
| 1808eba40 | client | pawn vfn 0xab8: true |
| 1808ce260 | client | active weapon |
| 1807c8970 | client | weapon vfn 0xae8 (every class): can switch hands (the server's 0xb48) |
| 180c60cb0 | client | C_CSPlayerPawn constructor (+0x1ecc word store; +0x1db8) |
| 180c61428 | client | writes +0x1ecc |
| 180c77b17 | client | game-event handler (`player_spawn`, `player_death`, `round_start` ...): +0x1ecc = cl_prefer_lefthanded (ConVar +0x58) |
| 18141c380 | client | command builder: pawn +0x1ecc -> left_hand_desired |
| 180b06e70 | server | CCSPlayerWeaponTimingGraph::RunTick inlined at 180b071c8 (shared/cstrike15/cs_player_weapontiminggraph.cpp); reads +0x1460 at 180b071dc |
| 180904000 | client | the timing graph (called from 1808cd040); reads +0x1db8 at 180904189 |
| 180c10aa0 | server | entity by handle |
| 180c86ed0 | server | owned weapon test |
| 180c868d0 | server | GetActiveWeapon |
| 180b23d70 | server | Weapon_Switch (weapon services vfn 0xf0); client 180915d60 |
| 180b23cc0 | server | Weapon_Switch's other path (checks vfn 0xa08 at 180b23d1a) |
| 180b02930 / 1802354b0 | server | the ordinary switch to another weapon (with Holster / vfn 0xc0 / Deploy / vfn 0x108 / 0x100) |
| 1809b5150 | server | weapon vfn 0xb48 (every class) = vfn 0xb40 && vfn 0xa08 |
| 1809b5140 | server | vfn 0xce8: false (every class but CBaseCSGrenade) |
| 1809b50d0 | server | CBaseCSGrenade vfn 0xce8: a handle test at +0x12a4 |
| 1809d4320 | server | vfn 0xb40 "can be left-handed": true (CCSWeaponBase, CCSWeaponBaseGun, CKnife, CBaseCSGrenade, CWeaponElite, CWeaponTaser) |
| 180a25520 | server | CC4 vfn 0xb40: false |
| 1809b50c0 | server | vfn 0xa08 "can be put away": true (CCSWeaponBase, CKnife, grenades, CC4) |
| 1809f9f20 | server | vfn 0xa08 of CCSWeaponBaseGun / Elite / Taser |
| 1809c7b10 | server | vfn 0xd20 HasBurstMode = m_bBurstMode |
| 1809f3c95 | server | weapon vdata constructor: m_bAllowBurstHolster default 1 |
| 180b0a410 | server | pawn of the weapon services |
| 180ae5400 | server | SwitchHandedness (client 1808e8560) |
| 180927cb0 | server | game time (client 18075e860) |
| 180249530 | server | CCSPlayerPawn Respawn (vfn 0xaf8; hand at 18024980a, cl_prefer_lefthanded at 180249847) |
| 1801f7ca0 | server | CCSPlayerPawn constructor |
| 180352350 | server | lea of +0x1464 into 18017e2d0 / 180cb56b0 (network / save plumbing) |
| 1808da750 | client | IsViewmodelLeftHanded |
| 1808550e0 / 180855180 | client | observer mode (2 in-eye) / observer target |
| 1810cd000 | client | viewmodel offsets (viewmodel_offset_x negated) |
| 1810d7910 | client | C_CS2HudModelArms::UpdateAndSetupView (hudmodel.cpp); the dip at 1810d7dda |
| 18015c720 | client | a - b |
| 1802804f0 | client | RemapValClamped |
| 18026fb30 | client | SimpleSpline: `x^2 (3 - (x + x))` |
| 18022b5b0 / 180a10d10 | client | SetAbsAngles -> scene node (+0xd4) |
| 18022b7b0 / 180a111a0 | client | SetAbsOrigin -> scene node (+0xc8) |
| 1810cc380 | client | arms bob / lag |
| 1808281f0 | client | C_C4 vfn 0xae0: false |
| 1807dfe00 | client | C_Knife vfn 0xae0: true |

## IsViewmodelLeftHanded's 15 callers (client)

| Address | What |
|---|---|
| 1810cb250 | C_CS2HudModelArms AG2_PushAnimTransformsToSkeletonInstance |
| 1810cc380, 1810d3730, 1810d5720 | C_CS2HudModelArms |
| 1810d2e30 | C_CS2HudModelWeapon |
| 1810d3190 / 1810d8a80 | C_CS2HudModelWeapon: the keychain |
| 1810d3d10 | C_CS2HudModelWeapon: the Elite holster / taser meter |
| 1807e5a50 | CEntityViewmodelLeftHandedRenderAttribCallback (`$ent_viewmodel_lefthanded`) |
| 181203980 | CreatePerViewConstantBufferCsgo |
| 1810cd000 | the viewmodel offset |
| 18081e900 | a weapon's attachment query (interface slot 0 on every weapon class): its 30 / -30 degree swing at 18081f37b only for owner == the local pawn (180c7dcb0, at 18081f26a), within 0.3 s of the weapon's +0xe8; which attachment ([weapon +0x234]) unread |
| 180902c40 | cs_player_weaponservices, muzzle flash / tracer start: only for the local pawn (18090307f) with no hud model (18080dd10 / 180831710); else the hud model's own path, flag 0; others flag 0 |
| 180c9f500 | a pawn's pass over its attached entities (18021a400 / 180c80cd0): the hand only for a child with m_bRenderWithViewModels (180b01cf0) and vfn 0x210 == 7 |

## Vtables

| Class | Module | Vtable |
|---|---|---|
| CCSWeaponBase | server | 0x1818ec818 |
| CCSWeaponBaseGun | server | 0x1818f0d38 |
| CKnife | server | 0x1819154a0 |
| CBaseCSGrenade | server | 0x1818e7f18 |
| CC4 | server | 0x1818ef218 |
| CWeaponElite | server | 0x181912698 |
| CWeaponTaser | server | 0x181919110 |
| C_CSWeaponBase | client | 0x181bde520 |
| C_C4 | client | 0x181be0300 |
| C_CSWeaponBaseGun | client | 0x181be1e80 |
| C_Knife | client | 0x181c068e0 |
| C_CSPlayerPawn | client | 0x181c8f288 |

The client's weapon slots run 0x60 below the server's (0xae0 / 0xae8 = 0xb40 / 0xb48).

## Fields

| Offset | Field |
|---|---|
| CCSPlayerPawn +0x1460 (client +0x1db8) | m_bLeftHanded |
| CCSPlayerPawn +0x1464 (client +0x1dbc) | m_fSwitchedHandednessTime |
| CCSPlayerPawn +0x1468.. / +0x1474 | m_flViewmodelOffsetX/Y/Z / m_flViewmodelFOV |
| C_CSPlayerPawn +0x1ecc | the client's wanted hand (not a schema field: between m_ignoreLadderJumpTime 0x1ec8 and m_bKilledByHeadshot 0x1ecd) |
| usercmd +0x40 / +0x48 | CBaseUserCmdPB `base` (the default instance when null) / left_hand_desired |
| base +0x68 | weaponselect |
| weapon +0xf9c | m_bBurstMode |
| weapon vdata +0x7d0 | m_bAllowBurstHolster |
| weapon +0x1284 | m_iBurstShotsRemaining |
| C_BaseEntity +0x56a | m_bRenderWithViewModels |

## Constants

| Value | What |
|---|---|
| `cl_prefer_lefthanded` | bool, flags 0x8288, default false, "Left handed preference"; a userinfo convar |
| `left_hand_desired` | CSGOUserCmdPB field 9, optional bool, default false (descriptor at client file offset 0x1bd0229: `0a 11 "left_hand_desired" 18 09 20 01 28 08 3a 05 "false"`), after attack1/attack2_start_history_index |
| 0x181afcd90 | client WeaponSwitchReason_t table: 0 eDrawn, 1 eEquipped, 2 eUserInitiatedSwitchToLast, 3 eUserInitiatedUIKeyPress, 4 eUserInitiatedSwitchHands |
| 40.0 (0x181ba779c) | dip degrees |
| 0.2 (0x181acff20) | dip time |
| 0.0 (0x181781734) | m_fSwitchedHandednessTime at Respawn |
| 0x181cecb70 / 0x181cecb80 | client `lefthand` / `righthand` strings: no code reference |

## The client commands (180ca4700 / 180ca4780 / 180ca47f0)

1. Local pawn (18096c1c0(0)); vfn 0x4f0 and vfn 0xab8 true.
2. New wanted hand: toggle `!pawn+0x1ecc`; left / right 1 / 0 (nothing if already so).
3. The active weapon (1808ce260) passes vfn 0xae8.
4. pawn +0x1ecc = new.

## The timing graph (RunTick), command r15, pawn r12

- `base.weaponselect` > 0: the entity (180c10aa0), as a weapon (vfn 0x5a8), owned (180c86ed0): Weapon_Switch with reason `desired != m_bLeftHanded ? 4 : 0`.
- else, desired != m_bLeftHanded: Weapon_Switch(GetActiveWeapon, 4).

## Weapon_Switch (180b23d70), weapon == the active one

- vfn 0xb48 and reason 4: SwitchHandedness (180ae5400 on the pawn via 180b0a410), then the weapon's Holster (vfn 0xa20, edx 0; [holster.md](holster.md)) and Deploy (vfn 0xa18, fire-gate.md 5); returns its result.
- else vfn 0xce8: Deploy. Else false.

vfn 0xa08 of the guns (1809f9f20): false when HasBurstMode and !m_bAllowBurstHolster and m_iBurstShotsRemaining >= 1. Every stock gun has m_bAllowBurstHolster true, so only the C4 refuses in stock CS2.

## SwitchHandedness (180ae5400 / client 1808e8560)

m_bLeftHanded = !m_bLeftHanded (network-state change on change); m_fSwitchedHandednessTime = now (written only when it differs).

## Spawn (180249530)

Pawn vfn 0xc20 (a bot) -> right-handed, else userinfo `cl_prefer_lefthanded` == 1; m_bLeftHanded set when it changes; m_fSwitchedHandednessTime = 0.0.

Pawn constructor (1801f7ca0): m_bLeftHanded 0, m_fSwitchedHandednessTime 0.0, m_flViewmodelOffsetX/Y/Z 1 / 1 / -1, m_flViewmodelFOV 60.

## The client's draw

- IsViewmodelLeftHanded (1808da750): m_bLeftHanded, the active weapon (yours, or the in-eye spectate target's), and its vfn 0xae0 (never the C4).
- The dip (1810d7910 at 1810d7dda), when the pawn passes vfn 0x4f0 / 0xab8:
  1. `e = now - m_fSwitchedHandednessTime` (18015c720)
  2. `v = RemapValClamped(e, 0, 0.2, 1, 0)` (1802804f0: `t = max((e - 0) / (0.2 - 0), 0)`, `min(t, 1)`, `C + (D - C) t`)
  3. v > 0: the arms' angles [rbp-0x49] pitch `+= SimpleSpline(v) x 40.0`.
  [rbp-0x49] is the angles (SetAbsAngles, +0xd4), [rbp-0x39] the origin (SetAbsOrigin, +0xc8); 1810cc380 (bob / lag) and 1810cd000 (offsets) run first, so the pitch adds after them.

## Third person: nothing

The hand never reaches a body or a world model: everyone, you included in third person, holds right-handed. Every code access to the fields: server +0x1460 / +0x1464 in 1801f7ca0, 180249530, 180ae5400, 180b071dc, 180352350 (address only); client +0x1db8 in 180c60cb0, 1808da750, 1808e8560, 180904189. The third-person anim graph (worldmodel*.json) has no hand parameter (its control parameters are action, attack / deploy / idle variations, weapon_*, move_*, aim angles, flinch, ladder, ik feet and the like); its only hand names are the WPN_DISABLE_HAND_IK / WPN_DISABLE_LEFT_HAND_IK events.

## Unread

- 18081e900's local-only 30 degree attachment swing: which attachment.
- The flags of `switchhands` (0x80000) and `cl_prefer_lefthanded` (0x8288): recorded, not decoded.
