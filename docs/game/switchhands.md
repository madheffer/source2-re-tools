# switchhands: changing the viewmodel's hand (traced 2026-11-11)

Builds: **server_20261105.dll** (sha256 70c66e85...) and **client_20261105.dll** (sha256 92794218 52772522...,
archived in tools/re/binaries), both from the 2026-11-05 CS2 update. Tools: tools/re/game/xref.py, disasm.py,
disasm_consts.py, fieldwrites.py, schema.py, rtti.py, vslot.py, callers.py. ReVa was down; nothing here came from a
decompiler.

The short version: **H runs `switchhands`**, which flips the hand the client *wants*; the usercmd carries it
(`left_hand_desired`); the server's weapon timing graph sees it differ from the pawn's networked `m_bLeftHanded` and
calls Weapon_Switch on the held weapon with reason `eUserInitiatedSwitchHands`, which flips the hand, stamps
`m_fSwitchedHandednessTime` and **holsters and redeploys the same weapon** (the draw plays again, with its attack
lock). The client draws the arms mirrored, and for 0.2 s after the stamp **dips them 40 degrees** and brings them
back up.

## 1. The commands and the convar (client)

`game/csgo/cfg/user_keys_default.vcfg:29`: `"h" "switchhands"` (`:27` `"f" "+lookatweapon"`).

| Registration | Callback | What |
|---|---|---|
| 1800e7720 `switchhands` (flags 0x80000, no help) | **180ca4700** | toggle |
| 1800e7790 `switchhandsleft` | **180ca4780** | set left |
| 1800e7800 `switchhandsright` | **180ca47f0** | set right |
| 1800e47a0 `cl_prefer_lefthanded` (bool, flags 0x8288, default false, "Left handed preference") | | the spawn's hand |

Each callback: the local pawn (18096c1c0(0)); its vfn 0x4f0 (C_CSPlayerPawn 18094f530: true) and vfn 0xab8
(1808eba40: true); the new wanted hand (toggle: `!pawn+0x1ecc`; left/right: 1/0, nothing if already so); the active
weapon (1808ce260); **weapon vfn 0xae8** (1807c8970, every class: the client's "can switch hands", the server's 0xb48
below); then **pawn +0x1ecc = new**. +0x1ecc is not a schema field (between m_ignoreLadderJumpTime 0x1ec8 and
m_bKilledByHeadshot 0x1ecd): the client's wanted hand. Its other writers: 180c60cb0 (the constructor, a word store),
180c61428, and **180c77b17**: on a game event (the handler that names `player_spawn`, `player_death`,
`round_start` ...) +0x1ecc = cl_prefer_lefthanded's value (its ConVar +0x58).

## 2. The usercmd

`CSGOUserCmdPB.left_hand_desired`: **field 9, optional bool, default false** (the descriptor at client file offset
0x1bd0229: `0a 11 "left_hand_desired" 18 09 20 01 28 08 3a 05 "false"`), after attack1/attack2_start_history_index.
The command builder (18141c380) reads pawn +0x1ecc into it.

## 3. The server's switch

**CCSPlayerWeaponTimingGraph::RunTick** (shared/cstrike15/cs_player_weapontiminggraph.cpp; the server's copy is
inlined in 180b06e70 at 180b071c8, the client's in 180904000, called from 1808cd040). With the command r15
(`+0x40` its CBaseUserCmdPB `base`, the default instance when null; `+0x48` left_hand_desired) and the pawn r12:
- `base.weaponselect` (+0x68) > 0: the entity (180c10aa0), as a weapon (vfn 0x5a8), owned (180c86ed0): Weapon_Switch
  (weapon services vfn 0xf0) with reason **desired != m_bLeftHanded ? 4 : 0**.
- else, desired != m_bLeftHanded: Weapon_Switch(GetActiveWeapon 180c868d0, **4**).

`WeaponSwitchReason_t` (client enum table 0x181afcd90): 0 eDrawn, 1 eEquipped, 2 eUserInitiatedSwitchToLast,
3 eUserInitiatedUIKeyPress, **4 eUserInitiatedSwitchHands**.

**Weapon_Switch** (weapon services vfn 0xf0; server **180b23d70**, client 180915d60), weapon == the active one:
- weapon **vfn 0xb48** (1809b5150, every class) and reason 4: **SwitchHandedness** (pawn via 180b0a410,
  **180ae5400**), then the active weapon's **Holster** (vfn 0xa20, edx 0) and **Deploy** (vfn 0xa18, fire-gate.md 5);
  returns its result.
- else weapon vfn 0xce8 (1809b5140 false for every class but CBaseCSGrenade's 1809b50d0, a handle test at +0x12a4):
  Deploy. Else false.
(Another weapon: the ordinary switch, 180b02930 / Holster / vfn 0xc0 / Deploy / vfn 0x108 / 0x100 / 1802354b0.)

**vfn 0xb48** 1809b5150 = vfn 0xb40 && vfn 0xa08:
- vfn 0xb40 "can be left-handed": 1809d4320 true for CCSWeaponBase, CCSWeaponBaseGun, CKnife, CBaseCSGrenade,
  CWeaponElite, CWeaponTaser; **CC4 180a25520 false**.
- vfn 0xa08 "can be put away": 1809b50c0 true (CCSWeaponBase, CKnife, grenades, CC4); CCSWeaponBaseGun / Elite /
  Taser **1809f9f20**: false when HasBurstMode (vfn 0xd20 = m_bBurstMode +0xf9c, 1809c7b10) and !vdata
  **m_bAllowBurstHolster** (+0x7d0; the vdata constructor's default 1, 1809f3c95) and m_iBurstShotsRemaining
  (+0x1284) >= 1. Every stock gun has m_bAllowBurstHolster true (weapons-cs2.js allowBurstHolster), so only the C4
  refuses in stock CS2. Weapon_Switch's other path checks vfn 0xa08 too (180b23d1a in 180b23cc0).

Vtables (server): CCSWeaponBase 0x1818ec818, CCSWeaponBaseGun 0x1818f0d38, CKnife 0x1819154a0, CBaseCSGrenade
0x1818e7f18, CC4 0x1818ef218, CWeaponElite 0x181912698, CWeaponTaser 0x181919110. Client: C_CSWeaponBase 0x181bde520,
C_C4 0x181be0300 (vfn 0xae0 1808281f0 false), C_CSWeaponBaseGun 0x181be1e80, C_Knife 0x181c068e0 (vfn 0xae0
1807dfe00 true), C_CSPlayerPawn 0x181c8f288. The client's slots run 0x60 below the server's for these (0xae0 / 0xae8
= 0xb40 / 0xb48).

**SwitchHandedness** (server 180ae5400, client 1808e8560): m_bLeftHanded = !m_bLeftHanded (network-state change on
change), **m_fSwitchedHandednessTime = now** (180927cb0 / client 18075e860: the game time; written only when it
differs).

Fields (schema.py): server CCSPlayerPawn m_bLeftHanded **+0x1460**, m_fSwitchedHandednessTime **+0x1464**
(then m_flViewmodelOffsetX/Y/Z +0x1468.., m_flViewmodelFOV +0x1474); client C_CSPlayerPawn +0x1db8 / +0x1dbc.

## 4. What the client draws

- **IsViewmodelLeftHanded** (client 1808da750): m_bLeftHanded, the active weapon (yours, or the in-eye spectate
  target's: observer mode 1808550e0 == 2, target 180855180), and its **vfn 0xae0** (can be left-handed: never the C4).
  Its 15 callers include the viewmodel offset (1810cd000: viewmodel_offset_x negated) and the render attribute
  `$ent_viewmodel_lefthanded` (CEntityViewmodelLeftHandedRenderAttribCallback).
- **The dip** (C_CS2HudModelArms::UpdateAndSetupView, hudmodel.cpp, 1810d7910; at 1810d7dda): when the pawn passes
  vfn 0x4f0 / 0xab8, `e = now - m_fSwitchedHandednessTime` (18015c720: a - b), `v = RemapValClamped(e, 0, 0.2, 1, 0)`
  (1802804f0: t = max((e - 0) / (0.2 - 0), 0), min(t, 1), `C + (D - C) t`), and when **v > 0**: the arms' angles
  [rbp-0x49] pitch **+= SimpleSpline(v) x 40.0** (18026fb30: `x^2 (3 - (x + x))`; 40.0 at 0x181ba779c, 0.2 at
  0x181acff20). [rbp-0x49] is the angles (SetAbsAngles 18022b5b0 -> scene node 180a10d10, +0xd4) and [rbp-0x39] the
  origin (SetAbsOrigin 18022b7b0 -> 180a111a0, +0xc8); 1810cc380 (bob / lag) and 1810cd000 (the offsets) run first.
  So the hands drop 40 degrees at the switch and come back up over 0.2 s.

## 5. Spawn

CCSPlayerPawn Respawn (vfn 0xaf8, **180249530**; at 18024980a): pawn vfn 0xc20 (a bot) -> right-handed, else the
client's userinfo convar `cl_prefer_lefthanded` (180249847, value == 1); m_bLeftHanded set when it changes,
**m_fSwitchedHandednessTime = 0.0** (0x181781734).

## What the port does

- src/cs2web/sim/move-state.js cleanCmd [12] left_hand_desired; src/cs2web/client/core/game.js sends `leftWant` in every command,
  sets it to cl_prefer_lefthanded on each spawn, and `switchHands(mode)` (H, the switchhands* console commands)
  flips it under the client's check (a held weapon, not the C4).
- server/cs2web/combat/combat.js `switchHands`: section 3's else branch (and weaponselect == the held slot); src/cs2web/player/loadout.js
  `canSwitchHands` (vfn 0xb48) and `deploy` (Deploy, split out of selectSlot). server/cs2web/core/game.js Respawn sets
  p.leftHanded from the 'userinfo' message (bots right-handed); the snapshot's `me.lh`.
- src/weapons/viewmodel.js `setHand`: the predicted switch's redeploy, the mirror (fp.js scale.x -1 and offset_x
  negated, both pre-existing) only off the C4, `$ent_viewmodel_lefthanded`, and `_handDip` (section 4).

## 6. Third person: nothing (traced 2026-11-11)

The hand never reaches a body or a world model; everyone, you included in third person, holds right-handed.
- Every code access to the field: server +0x1460 / +0x1464: the pawn's constructor (1801f7ca0: m_bLeftHanded 0,
  m_fSwitchedHandednessTime 0.0, then m_flViewmodelOffsetX/Y/Z 1 / 1 / -1, m_flViewmodelFOV 60), Respawn (180249530),
  SwitchHandedness (180ae5400), the timing graph (180b071dc), and 180352350 (a lea of +0x1464 into 18017e2d0 /
  180cb56b0, the field's address only: network / save plumbing). Client +0x1db8: the constructor 180c60cb0,
  IsViewmodelLeftHanded 1808da750, SwitchHandedness 1808e8560, the timing graph 180904189. Nothing else reads it.
- IsViewmodelLeftHanded's 15 callers (by vtable owner or profiler string): C_CS2HudModelArms (1810cb250
  AG2_PushAnimTransformsToSkeletonInstance, 1810cc380, 1810d3730, 1810d5720), C_CS2HudModelWeapon (1810d2e30,
  1810d3190 / 1810d8a80 the keychain, 1810d3d10 the Elite holster / taser meter), the render attribute callback
  (1807e5a50, CEntityViewmodelLeftHandedRenderAttribCallback), the per-view constant buffer (181203980,
  CreatePerViewConstantBufferCsgo), and three that are gated to first person:
  - 18081e900 (a weapon's attachment query, interface slot 0 on every weapon class): its 30 / -30 degree swing at
    18081f37b only for the owner == the local pawn (180c7dcb0, at 18081f26a), within 0.3 s of the weapon's +0xe8.
    Unread which attachment ([weapon +0x234]).
  - 180902c40 (cs_player_weaponservices, the muzzle flash / tracer start): only for the local pawn (18090307f), and
    only when it has no hud model (18080dd10 / 180831710); else the hud model's own path, flag 0; others flag 0.
  - 180c9f500 (a pawn's pass over its attached entities, 18021a400 / 180c80cd0): the hand only for a child with
    **m_bRenderWithViewModels** (C_BaseEntity +0x56a, 180b01cf0) and vfn 0x210 == 7.
- The third-person anim graph (web/public/player/anim/worldmodel*.json, CS2's) has no hand parameter: its control
  parameters are action, attack / deploy / idle variations, weapon_*, move_*, aim angles, flinch, ladder, ik feet and
  the like; its only hand names are the WPN_DISABLE_HAND_IK / WPN_DISABLE_LEFT_HAND_IK events. The `lefthand` /
  `righthand` strings at client 0x181cecb70 / 0x181cecb80 have no code reference (data only).

## Still unread / stand-ins

- Holster (vfn 0xa20): traced in holster.md (the reload, the R8 hammer, a grenade's pin; the silencer / zoom / C4 / taser parts not ported).
- 18081e900's local-only 30 degree attachment swing (above): which attachment it is, not ported.
- The dip composes with the bob / lag differently here: it turns the camera about root_motion before
  viewmodel.js's own bob / lag (which are stand-ins themselves: CS:GO cl_bob numbers), where CS2 adds the pitch to
  the arms' angles after 1810cc380.
- The dip's clock is the viewmodel's (the switch as predicted), not the server's stamp; CS2's client predicts the
  stamp the same way.
- The flags of `switchhands` (0x80000) and `cl_prefer_lefthanded` (0x8288) are recorded, not decoded.
