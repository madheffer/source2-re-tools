# Zeus x27 on the client (C_WeaponTaser)

client_20261015; particles.dll 2026-11-12 (b10c5654, the install's); pak01 2026-11-16. The server's side (CWeaponTaser FireBullet 180a2c980, the recharge think): [armsrace.md](armsrace.md).

## Functions

| Address | Module | What |
|---|---|---|
| 1807e3df0 | client | CEntityWeaponTaserChargeRenderAttribCallback's one slot: `$taser_charge` |
| 1808077c0 | client | registers `$taser_charge` ("0.0 to 1.0", type 2 float) |
| 180802bf0 | client | write a float4 (type-2 request only) |
| 18082ea00 | client | C_WeaponTaser vfn 0xad8: the charge |
| 1802803b0 | client | RemapValClamped |
| 1800deec0 | client | registers `slot3` (ConCommand at 0x18256aed0, callback 180c1eff0) |
| 180c0cac0 | client | getter of the HUD weapon selection (0x18256a568[slot]) |
| 180c1e680 | client | CBaseHudWeaponSelection vfn 0x288: slot3 handler (mode 3: `phys_swap`) |
| 180c1edb0 / ee10 / ee70 / eed0 | client | slot1 / 2 / 4 / 5 callbacks' neighbours |
| 0x180c1e600 / 0x180c1e6f0 | client | slot2 / slot4 handlers (vtable 0x181c7dbd0 slots 0x280 / 0x290: cycle next / previous at 3) |
| 180c19e30 | client | vfn 0x2d8: with vfn 0x2e8 true, +0x14 = curtime and vfn 0x248(slot) |
| 1811a9cb0 | client | CCSHudWeaponSelection vfn 0x248 SelectSlot |
| 18090d6e0 | client | weapon services usable |
| 180c0cc30 | client | vfn 0x258 the weapon at (gear slot, position): lowest at or after (weapon-select.md) |
| 180c09310 | client | `Player.WeaponSelectionFoley` from the pawn |
| 1800ddf70 | client | hud_fastswitch registration |
| 18082e180 | client | C_WeaponTaser fire (once a tick) |
| 180c091f0 | client | `Weapon_Taser.Single` from the weapon |
| 180834ff0 | client | the trace (client copy of server 180a31040) |
| 180835590 | client | on what the trace hits |
| 180c02780 | client | damage info ctor |
| 18022e9e0 | client | predicted impact on the victim (damage-prediction.md) |
| 18093ec00 | client | attachment `weapon_hand_r` |
| 180c7bdb0 | client | shooter is the local player |
| 180952890 / 18093eec0 | client | viewmodel `muzzle_flash` attachment |
| 180c770c0 | client | viewmodel FOV fix-up into the world view |
| 18082bee0 | client | fill cstaserrope (start, end, shooter, hit entity) |
| 18122a840 | client | dispatch effect by name ("cstaserrope") |
| 180d1e3d0 | client | cstaserrope handler (registered 1800f2370) |
| 1807c88e0 | client | create particle (attach 2) |
| 181742a00 | client | VectorAngles |
| 180d1e300 | client | body fx handler (registered 1800f2330) |
| 180830770 | client | precache (both systems) |
| 180820310 | client | names ChargeNotReady (client empty sound) |
| 18015a2f0 | client | WorldSpaceCenter (vfn 0x2c8) |
| 0x18015d710 | particles | C_INIT_InitSkinnedPositionFromCPSnapshot init (slot 34) |
| 0x180655c60 | particles | attribute manager (vfn 0x120: stream types) |
| 18037c4c0 | particles | joint name -> bone (-1 -> bone 0) |
| 0x1800a3b10 | particles | skinning blend |
| 0x1800a2b90 | particles | weighted matrix sum |
| 18035c940 | particles | bone world x inverse bind |
| 18035d560 | particles | largest axis scale |
| 18036ac00 -> 18035ec60 | particles | point through M |
| 18035ec20 | particles | normal through M |
| 180052250 | particles | clamp to max |
| 0x180206810 | particles | C_OP_MovementSkinnedPositionFromCPSnapshot Operate (slot 34) |
| 1809f8a70 (1809f8ada) | server | BaseGunFire's empty branch |
| 180a1e400 | server | PlayEmptySound (once per command number +0xf34) |
| 180c83a60 | server | PAS filter |
| 180c864b0 | server | attenuation 0.8 |
| 180c8c8d0 | server | less the predicting player |
| 180b763d0 | server | (weapon, delay, 0): set the attack clocks |
| 180b3baa0 / 180b3bbe0 | server | primary / secondary clock set |
| 1809f7840 | server | dry fire activity |
| 1809ffd30 | server | another gate: same with 0 delay |

## Classes and fields

| Offset / vtable | What |
|---|---|
| 0x181c053e8 | C_WeaponTaser vtable (RTTI .?AVC_WeaponTaser@@) |
| 0x181bd6828 | CEntityWeaponTaserChargeRenderAttribCallback vtable |
| 0x181bd6858 | CEntityViewmodelLeftHandedRenderAttribCallback vtable ($ent_viewmodel_lefthanded) |
| 0x181c7dbd0 | CBaseHudWeaponSelection vtable |
| 0x181d21320 | CCSHudWeaponSelection vtable |
| 0x181c9db20 | CCSGOInput vtable |
| C_WeaponTaser +0x1f50 | m_fFireTime (param_1 + 0x3ea * 8 in 18082ea00; NetworkVar_m_fFireTime@C_WeaponTaser) |
| +0x1f54 | last fire's tick guard (gpGlobals +0x44) |
| viewmodel +0x520 | owner weapon handle |
| entity +0x365 * 8 | vdata name |
| string table +0x34 | generation (token cache) |
| 0x18256aeb8 +0x58 | hud_fastswitch value (registration at 0x18256aeb0, flags 0x80, default 0) |
| pawn +0x12f0 | weapon services |
| weapon +0x388 | vdata; +0x700 gear slot, +0x704 position |
| vdata +0x830 | m_flRange (130 without vdata) |
| shot info +0x14 / +0x20 | eye / angles |
| pawn viewmodel +0x1990 | viewmodel weapon handle |
| cstaserrope +0x38 / +0x3c / +0x14 / +0x8 | shooter / hit entity / start / end |
| weapon +0xf50 | m_bFireOnEmpty |
| weapon +0xeb0 / +0xeb4 | primary clock tick / fraction |
| weapon +0xeb8 / +0xebc | secondary clock |
| vdata +0x4c6 | links the cooldowns |
| vdata +0x71e | m_bIsRevolver (vfn 0xd28) |

## Constants

| Value | What |
|---|---|
| mp_taser_recharge_time | cvar 0x1824d6b40; < 0 -> charge 1 |
| 500 (0x43fa0000), DMG 0x100 (shock) | the hit's damage info |
| 2 / 4 | sphere radii of the trace |
| 7.61985 / 2.32976 | rope start offsets along the hand's X (axis 0x1827210f0, static (1, 0, 0) from 0x181ada350) / Z (0x182721140, (0, 0, 1) from 0x181ad0f90) |
| 0.2 (0x3e4ccccd) | dry fire delay (R8: its cycle) |
| 0x32 / 0x66 | dry fire activity / the R8's |
| 0.8 | empty sound attenuation |
| 3 | hud_fastswitch value for the phys_swap branch (HUDTYPE_PLUS) |
| 14 | slot - 1 bound |

## The charge meter ($taser_charge)

- 1807e3df0: the entity (vfn 0x210 class 5) or the viewmodel's owner weapon (class 7) when vfn 0x528 says it's a weapon; its vdata name against `weapon_taser` (cached) -> vfn 0xad8, else 0.
- 18082ea00: `mp_taser_recharge_time < 0` -> 1; clip (vfn 0xa58(0)) >= 1 -> 1; else `RemapValClamped(now - m_fFireTime, 0, recharge_time, 0, 1)`.
- Material weapons/models/taser/materials/weapon_pist_taser_chargemeter.vmat (csgo_unlitgeneric, F_BLEND_MODE 2, F_RENDER_BACKFACES, g_tColor taser_numerals_color):
  - g_vColorTint `return $ent_ammo || .7+frac(time()*6)*.3;` (charged 1; spent a 6 Hz flicker 0.7..1).
  - g_vTexCoordOffset `return $ent_ammo ? float2(.9,0) : float2(floor($taser_charge*99)*(1/128),0);` (charged: the 0.9 cell; else 0..98 in 1/128 steps).
  - On the second primitive of weapon_pist_taser.vmdl's body_hd mesh (462 indices), bone `taser_meter`.
- The `||` in the compiled vmat_c: `19 <$ent_ammo's hash> 04 0a 00 12 00` (the variable, then a branch: true to +0x0a, false to +0x12), `07 1.0 02 2a 00` (1.0, jump to the end), `07 0.7 ... 15 ... 13` (0.7 + frac(time() x 6) x 0.3). VRF prints it as `a || b`; its value is `a ? 1 : b`, not a 0 / 1 truth value. (`&&` not met.)

## slot3

1. 180c1e680 (vfn 0x288): input mode (0x18256aeb8 +0x58, hud_fastswitch) 3 -> sends `phys_swap`; else vfn 0x2d8(..., 3).
2. 180c19e30: vfn 0x2e8 true -> +0x14 = curtime, vfn 0x248(slot).
3. SelectSlot (1811a9cb0): local pawn alive (vfn 0x4f0, 0xab8), `slot - 1 < 14` is the gear slot; weapon services usable; the active weapon's gear slot == the slot's -> position = +0x704 + 1, else 0; vfn 0x258(gear slot, position), none -> vfn 0x258(gear slot, 0); found -> vfn 0x320 (select), vfn 0x268, `Player.WeaponSelectionFoley` (180c09310) when it isn't the active one.

- Knife out (GEAR_SLOT_KNIFE position 0): slot3 brings the Zeus (position 1); Zeus out: next position empty, falls back to the knife; from anything else, the knife.
- No CS2 cfg sets hud_fastswitch (game/csgo/cfg, game/core/cfg); server.dll has no phys_swap command (the string isn't in it); the branch is unreachable at the default 0.

## The fire (18082e180) and the rope

1. `Weapon_Taser.Single` from the weapon.
2. range = vdata +0x830 (130 without). Start = the shot's eye, end = start + AngleVectors(shot angles) x range: no spread.
3. Trace 180834ff0: a line, then spheres of 2 and 4 to the end pulled back by their radius; the plain filter first, then CTraceFilterTaserIgnoreTeammates when the first hit a teammate; 180835590 on what it hits.
4. A player hit: a 500 damage info (DMG 0x100) to 18022e9e0.
5. Rope start: the pawn's `weapon_hand_r` attachment + 7.61985 x its rotated X + 2.32976 x its rotated Z (quaternion rotation written out: `t = 2 q.xyz x v`, `v + w t + q.xyz x t`). Local shooter: the viewmodel weapon's `muzzle_flash` attachment moved into the world view (180c770c0).
6. cstaserrope filled (18082bee0) and dispatched by name (18122a840).

- **180d1e3d0** (cstaserrope): shooter and hit entity as alive pawns; `particles/weapons/cs_weapon_fx/weapon_tracers_taser.vpcf` (attach 2) with CP0 = start oriented along normalize(end - start), CP1 = end, CP3 = (1 when the shooter is the local player else 0, 1 when it hit a pawn else 0, 0); started (vfn 0x18). Children: weapon_tracers_taser_wire1a / 1b / wire2 (beam_crack textures; materials/particle/beam_taser).
- **180d1e300**: `particles/blood_impact/impact_taser_bodyfx.vpcf` on the entity at +0x38, attach type 3 (PATTACH_CUSTOMORIGIN_FOLLOW).

## The victim's body effect (skinned snapshot)

- impact_taser_bodyfx.vpcf: m_nMaxParticles 275, m_flConstantLifespan 10, C_OP_StopAfterCPDuration 2 s; `m_hSnapshot` particles/characters/models/shared/character_fx/character_taser_bodyfx.vsnap on `m_nSnapshotControlPoint` 1; an InstantaneousEmitter of 1 x the snapshot's count (24 a frame); C_INIT_InitSkinnedPositionFromCPSnapshot (m_bCopyAlpha, m_bSetRadius), InitFromCPSnapshot of colour / radius / lifespan, InitFloat on lifespan; operators C_OP_MovementSkinnedPositionFromCPSnapshot, Decay, BasicMovement (drag 0.1), InterpolateRadius; C_OP_RenderRopes with beam_crack_02 and a blue gradient.
- The .vsnap (pak01, 74665 bytes: RED2, DATA (KV3 stream table), SNAP (73225)): 1440 particles; streams position, normal, color, velocity, scratch_vec, lifespan, radius, opacity, rotation, rotation_speed, `skinning` (a joint-name list of 33 skeleton bones, ankle_l ... spine_3; per particle up to four joints with weights; all here one joint at weight 1). VRF's text export writes the skinning stream empty; `Blocks.ParticleSnapshot.AttributeData` has the values. Attribute numbers: position 0, lifespan 1, radius 3, rotation 4, rotation_speed 5, color 6, opacity 7, scratch_vec 17, normal 21 (velocity none); joints 31, weights 32.

### C_INIT_InitSkinnedPositionFromCPSnapshot (vtable 0x1804f69d8, init 0x18015d710)

| Offset | Field |
|---|---|
| +0x1e8 | m_nSnapshotControlPointNumber (1) |
| +0x1ec | m_nControlPointNumber (0, the CP whose model skins it) |
| +0x1f0 / +0x1f4 | m_bRandom / m_nRandomSeed |
| +0x1f8 / +0x1f9 / +0x1fa | m_bRigid / m_bSetNormal / m_bIgnoreDt |
| +0x1fc / +0x200 | normal velocity min / max |
| +0x204 | index mode |
| +0x380 / +0x384 | m_flIncrement / m_nFullLoopIncrement |
| +0x38c / +0x390 | m_flBoneVelocity / m_flBoneVelocityMax |
| +0x394 / +0x395 / +0x396 | m_bCopyColor / m_bCopyAlpha / m_bSetRadius |
| snapshot +0xa64 / +0xa68 | stream slots of attributes 31 / 32 |
| snapshot +0xb30 / +0xb38 | joint name count / names |
| cp +0xbc | bone count |
| cp +0xa0 / +0xa4 | time / previous time (-1 none) |
| coll +0x350 / +0x3d0 / +0x3d8 | attributes 15 (local position), 31, 32 on the particle |

1. Nothing unless the snapshot has attributes 31 and 32, and 21 / 6 / 7 / 3 for the flags that copy them.
2. Joint names map to the CP model's bones (18037c4c0). CP bone count 0: the snapshot position copied as is.
3. Index: sequential (wrap `((i / count) x m_nFullLoopIncrement + i) % count`, step (int) m_flIncrement) or m_bRandom's table.
4. Skinning (0x1800a3b10): weights w0..w2, `w3 = clamp(1 - w0 - w1 - w2, 0, 1)`; joints that name a bone kept in order (not 0xffff, below the bone count; the previous frame's count when Mprev is blended; the cache's). 0x1800a2b90 sums: 1 the matrix as is (no weight), 2 `w1 M1 + w0 M0`, 3 `(w1 M1 + w0 M0) + w2 M2`, 4 `((w1 M1 + w0 M0) + w2 M2) + w3 M3` per element.
5. Each bone's matrix (18035c940: current bone table +8, 0x50 apart: +0x20 position / scale, +0x30 quaternion; inverse binds +0x30, 0x20 apart): rows `((a2 b2 + a1 b1) + a0 b0) + a3` in the 4th lane. A point through M: per row `(m3 + m1 y) + (m2 z + m0 x)`.
6. Init body (0x18015e5c7..0x18015ec20): joints (attribute 31, `map[j % joints] % bones`), local position (15, the snapshot's), the three weights (32).
7. m_bSetNormal: normal through M unless m_bRigid; `l = ((x x + 1.1920929e-07) + y y) + z z`, rsqrtss and one Newton step `((3 - e l e) (e 0.5))`; normal velocity `lerp(min, max, T[c914 + c910++]) x prev dt` unless m_bIgnoreDt.
8. m_bSetRadius: `radius x maxss(maxss(|sx|, |sy|), |sz|)` unless m_bRigid.
9. Position M x local; previous position M x (local + that velocity) (m_bRigid: both 0).
10. Bone velocity (m_flBoneVelocity != 0, cp +0xa4 != -1, Mprev all finite): `(M.t - Mprev.t) x (1 / (cp +0xa0 - +0xa4)) x m_flBoneVelocity`, clamped to m_flBoneVelocityMax when above 0, x prev dt unless m_bIgnoreDt, off the previous position.
- rsqrtss's estimate is the CPU's own (Intel and AMD differ).

### C_OP_MovementSkinnedPositionFromCPSnapshot (vtable 0x180503740, Operate 0x180206810, body 0x1802072b0..)

- Each frame every particle takes a snapshot index again (SNAPSHOT_INDEX_DIRECT: `(int) m_flReadIndex % count`; m_bRandom; else from m_nSnapShotStartPoint by (int) m_flIncrement, m_nFullLoopIncrement's wrap) and moves toward it by `t = m_flInterpolation` (per particle; 1): no bones, the snapshot's values; bones, M x local (and the normal, the radius) as in the init.

## Dry fire (server)

1. BaseGunFire's empty branch (m_bFireOnEmpty, set by the primary branch on an empty clip): 180a1e400 once per command number: `Weapon_Taser.ChargeNotReady` for weapon_taser (vdata name), `Default.ClipEmpty_Pistol` for WEAPONTYPE 1, `Default.ClipEmpty_Rifle` otherwise; from the weapon through a PAS filter (attenuation 0.8) less the predicting player (its client plays its own).
2. 180b763d0(weapon, delay, 0): the primary clock delay from now, and the secondary too when vdata +0x4c6 links the cooldowns; delay 0.2 unless the R8 (its cycle).
3. Dry fire activity (0x32, R8 0x66), m_bWaitForNoAttack.

## Third person

- worldmodel graph (player/anim/worldmodel.json) tests `weapon_taser` among the pistol branch's weapon_types (between weapon_fiveseven and weapon_p250): weapon_category_pistol.
- Another player's rope starts at the server's cstaserrope start: the pawn's weapon_hand_r attachment. Every agent model has it (80 of pak01's 183 player models, all 141 agents; on hand_R at (-2.6, -1.4, 0), rotation (-0, 0, 1, -4.37e-8): 180 about z; vmdl AttachmentList), so the rope leaves the hand, not the gun's `wpn` bone. Without it: WorldSpaceCenter (vfn 0x2c8, 18015a2f0).

## Assets

- weapon_pist_taser.vmdl: bones weapon, weapon_offset, taser_meter, ag1_hand_r, trigger; attachments muzzle_flash on weapon_offset (4.817, -0.001, -0.719), camera_inventory, keychain, nametag, stattrak, weapon_holster_center; clips draw / idle / lookat01 / shoot1 (animation/anims/viewmodel/pistol/pistol_taser); graphs viewmodel_gun+taser, viewmodel_inspects+taser.
- Sounds: Weapon_Taser.Single / .ChargeReady (+ _Zap) / .ChargeNotReady (+ _Empty) / .Draw / .Charging, Player.WeaponSelectionFoley, Default.ClipEmpty_Pistol / _Rifle.
- Kill feed / list icon: panorama icons/equipment/taser.svg.
