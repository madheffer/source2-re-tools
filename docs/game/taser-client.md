# The Zeus x27 on the client (C_WeaponTaser)

client_20261015.dll (ReVa `/client_20261015.dll`; tools/re rtti.py / vtdump.py / vslot.py / disasm.py on
source2-compiler's tools/re/binaries copy), pak01 2026-11-16. Ported in web/src/weapons/viewmodel.js (the slot, the
gate's dry fire, the charge meter), web/src/cs2web/client/core/game.js (slot3, the predicted rope, the 'taser' event),
web/src/cs2web/client/fx/bullet-fx.js (taserRope / taserBody), web/src/world/body.js (wpnPoint), web/src/ui/hud.js
(the list's row). The server's side (CWeaponTaser's FireBullet 180a2c980, the recharge think) is docs/game/armsrace.md.

## Classes

| What | Where |
|---|---|
| C_WeaponTaser vtable | 0x181c053e8 (RTTI .?AVC_WeaponTaser@@) |
| CEntityWeaponTaserChargeRenderAttribCallback vtable | 0x181bd6828, its one slot 1807e3df0 |
| CEntityViewmodelLeftHandedRenderAttribCallback vtable | 0x181bd6858 (the $ent_viewmodel_lefthanded one, next to it) |
| CBaseHudWeaponSelection vtable | 0x181c7dbd0 |
| CCSHudWeaponSelection vtable | 0x181d21320 |
| CCSGOInput vtable | 0x181c9db20 |
| m_fFireTime | C_WeaponTaser +0x1f50 (param_1 + 0x3ea * 8 in 18082ea00; RTTI NetworkVar_m_fFireTime@C_WeaponTaser) |
| the last fire's tick guard | +0x1f54 (18082e180: one fire a tick, gpGlobals +0x44) |

## The charge meter ($taser_charge)

- **1808077c0** registers the material attribute `$taser_charge` ("0.0 to 1.0", type 2: a float).
- **1807e3df0** (the callback): the entity's (vfn 0x210 class 5) or the viewmodel's owner weapon (class 7: its +0x520
  handle) when vfn 0x528 says it's a weapon; its vdata name (+0x365 * 8) against `weapon_taser` (cached per
  string-table generation +0x34) -> **vfn 0xad8** (18082ea00), else 0; written as a float4 of that value (180802bf0,
  only for a type-2 request).
- **18082ea00** (C_WeaponTaser vfn 0xad8, the charge): `mp_taser_recharge_time` (cvar 0x1824d6b40) < 0 -> 1; the clip
  (vfn 0xa58(0)) >= 1 -> 1; else RemapValClamped(now - m_fFireTime, 0, recharge_time, 0, 1) (1802803b0 with 0 / 1).
- The meter's material (weapons/models/taser/materials/weapon_pist_taser_chargemeter.vmat, csgo_unlitgeneric,
  F_BLEND_MODE 2, F_RENDER_BACKFACES, g_tColor taser_numerals_color) reads it in two dynamic expressions:
  g_vColorTint `return $ent_ammo || .7+frac(time()*6)*.3;` (charged: 1; spent: a 6 Hz flicker 0.7..1) and
  g_vTexCoordOffset `return $ent_ammo ? float2(.9,0) : float2(floor($taser_charge*99)*(1/128),0);` (the numeral strip:
  charged shows the 0.9 cell, else the percentage 0..98 in 1/128 steps). Both are on the second primitive of
  weapon_pist_taser.vmdl's body_hd mesh (462 indices), the bone `taser_meter`.
- Ours: viewmodel.js `taserCharge` (the clip, else 1 - (readyAt - now) / 30, readyAt = the predicted shot's time + 30
  or the snapshot's now + me.tzr), fed to tickCs2Materials as `taser_charge` with `ent_ammo` the Zeus's clip.
  The server's mp_taser_recharge_time rides your snapshot (me.tzt) while you carry one.
- **The `||` of g_vColorTint** (2026-11-16, the compiled vmat_c's expression bytes): `19 <$ent_ammo's hash> 04 0a 00
  12 00` (the variable, then a branch: true to +0x0a, false to +0x12), `07 1.0 02 2a 00` (1.0, jump to the end),
  `07 0.7 ... 15 ... 13` (0.7 + frac(time() x 6) x 0.3): VRF prints that branch as `a || b`, and its value is
  `a ? 1 : b`, not a 0 / 1 truth value. weapons/fp/cs2-material.js's `||` now evaluates so (it gave 1 always:
  the spent meter's 6 Hz flicker never showed). `&&` wasn't in a material read here (left as a truth value).

## slot3: the next weapon in the gear slot

- `slot3` is registered by **1800deec0** (ConCommand at 0x18256aed0, callback 180c1eff0): the split screen's HUD weapon
  selection (0x18256a568[slot], getter 180c0cac0) vfn 0x288.
- **180c1e680** (CBaseHudWeaponSelection vfn 0x288, the slot3 handler; slot1 / 2 / 4 / 5 are its neighbours
  180c1edb0 / ee10 / ee70 / eed0's callees): with the input's mode (+0x58 of 0x18256aeb8) 3 it sends `phys_swap`
  instead; else vfn 0x2d8(..., 3).
- **180c19e30** (vfn 0x2d8): with vfn 0x2e8 true, +0x14 = curtime and **vfn 0x248(slot)**.
- **1811a9cb0** (CCSHudWeaponSelection vfn 0x248, SelectSlot): the local pawn alive (vfn 0x4f0, 0xab8), slot - 1 < 14
  is the gear slot; its weapon services (pawn +0x12f0) usable (18090d6e0); the active weapon's vdata (+0x388):
  gear slot +0x700 == the slot's -> position = +0x704 + 1, else 0; vfn 0x258(gear slot, position) (the weapon there),
  none -> vfn 0x258(gear slot, 0); found -> vfn 0x320 (select it), vfn 0x268, and `Player.WeaponSelectionFoley` from
  the pawn (180c09310) when it isn't the active one.
- So with the knife (GEAR_SLOT_KNIFE position 0) out, slot3 brings out the Zeus (position 1); with the Zeus out, the
  next position is empty and it falls back to position 0, the knife; from anything else, the knife. Ours:
  game.js inGearSlot (lastinv keeps asking for the loadout slot itself). Player.WeaponSelectionFoley: every slot
  key's SelectSlot plays it from your pawn when the weapon it selects isn't the active one (game.js selectSlot's
  `foley`, main.js's slot keys; lastinv isn't SelectSlot). The phys_swap branch: 180c1e680 / 180c1e600 send
  `phys_swap` instead only when the cvar at 0x18256aeb8 is 3 (the Source SDK's hud_fastswitch HUDTYPE_PLUS); its
  value is never 3 here, so slot3 always takes the selection path. The cvar is **hud_fastswitch** (client
  registration 1800ddf70 at 0x18256aeb0, flags 0x80, default 0; slot2 0x180c1e600 and slot4 0x180c1e6f0, vtable
  0x181c7dbd0 slots 0x280 / 0x290, cycle the next / previous weapon at 3, slot3 0x180c1e680 sends "phys_swap"). No
  CS2 cfg sets it (game/csgo/cfg, game/core/cfg) and server.dll has no phys_swap command (the string isn't in it), so
  even at 3 slot3 would send a command the server ignores; this client defines no hud_fastswitch (its console only
  has the cvars it registers), so the value stays the default 0 and the branch can't be reached.
  vfn 0x258 (180c0cc30) takes the lowest position at or after the asked one (docs/game/weapon-select.md).

## The fire (predicted) and the rope

**18082e180** (C_WeaponTaser's fire, once a tick):
- `Weapon_Taser.Single` from the weapon (180c091f0).
- range = vdata +0x830 (m_flRange; 130 without vdata). Start = the shot's eye (+0x14 of the shot info), end = start +
  AngleVectors(the shot angles, +0x20) x range: no spread. The trace 180834ff0 (180a31040's client copy: a line, then
  spheres of 2 and 4 to the end pulled back by their radius; the plain filter first, and a second trace
  with CTraceFilterTaserIgnoreTeammates when the first hit a teammate, then 180835590 on what it hits; ours: game.js
  taserShot runs the server's, sim/src/combat/taser.rs, over the drawn players' boxes).
- A player hit: a 500 (0x43fa0000) damage info (180c02780, DMG 0x100 = shock) handed to 18022e9e0 (the predicted
  impact on the victim).
- The rope's start: the pawn's `weapon_hand_r` attachment (18093ec00) + 7.61985 x its rotated X (the axis 0x1827210f0,
  static (1, 0, 0) from 0x181ada350) + 2.32976 x its rotated Z (0x182721140, (0, 0, 1) from 0x181ad0f90): the
  quaternion rotation written out (t = 2 q.xyz x v, v + w t + q.xyz x t). When the shooter is the local player
  (180c7bdb0), the start is the viewmodel's weapon (+0x1990 handle) `muzzle_flash` attachment (180952890 /
  18093eec0) moved into the world's view (180c770c0: the viewmodel FOV fix-up).
- Then the cstaserrope effect (18082bee0 fills it: start, end, the shooter's handle, the hit entity's handle) is
  dispatched by name (18122a840 "cstaserrope").

**180d1e3d0** (the cstaserrope handler, registered 1800f2370): the shooter (+0x38) and the hit entity (+0x3c) as
alive pawns; `particles/weapons/cs_weapon_fx/weapon_tracers_taser.vpcf` (1807c88e0, attach 2) with CP0 = the start
(+0x14) oriented along normalize(end - start) (181742a00: VectorAngles), CP1 = the end (+0x8), CP3 = (1 when the
shooter is the local player else 0, 1 when it hit a pawn else 0, 0); then started (vfn 0x18). The rope itself is that
system's children (weapon_tracers_taser_wire1a / 1b / wire2, beam_crack textures; materials/particle/beam_taser).
Ours: bullet-fx.js taserRope.

**180d1e300** (another message's handler, 1800f2330): `particles/blood_impact/impact_taser_bodyfx.vpcf` on the
entity at +0x38, attach type 3 (PATTACH_CUSTOMORIGIN_FOLLOW). Ours: bullet-fx.js taserBody, CP0 / CP1 on the
victim's origin, CP0 carrying their model's bones (client/fx/taser-skin.js).

### The victim's body effect: a skinned snapshot

impact_taser_bodyfx.vpcf (m_nMaxParticles 275, m_flConstantLifespan 10, C_OP_StopAfterCPDuration 2 s) has
`m_hSnapshot` particles/characters/models/shared/character_fx/character_taser_bodyfx.vsnap on
`m_nSnapshotControlPoint` 1: an InstantaneousEmitter of 1 x the snapshot's count (24 a frame), then
C_INIT_InitSkinnedPositionFromCPSnapshot (m_bCopyAlpha, m_bSetRadius), InitFromCPSnapshot of colour / radius /
lifespan, InitFloat on lifespan; operators C_OP_MovementSkinnedPositionFromCPSnapshot, Decay, BasicMovement (drag
0.1), InterpolateRadius; C_OP_RenderRopes with beam_crack_02 and a blue gradient: crackles along the body's limbs.
- **The .vsnap** (pak01, 74665 bytes: RED2, DATA (the KV3 stream table), SNAP (73225)): 1440 particles; streams
  position, normal, color, velocity, scratch_vec, lifespan, radius, opacity, rotation, rotation_speed and
  `skinning` (type skinning: a joint-name string list of 33 of the character skeleton's bones, ankle_l ...
  spine_3, and per particle up to four joints with weights; all here are one joint at weight 1). VRF's text export
  writes the skinning stream empty; its `Blocks.ParticleSnapshot.AttributeData` has the values: lasers-bake
  --snapshots (bake/SnapshotBake.cs) writes them to web/public/ze-fx/fx/snapshots/<path>.json (167 KB), the streams
  under CS2's attribute numbers (position 0, lifespan 1, radius 3, rotation 4, rotation_speed 5, color 6, opacity 7,
  scratch_vec 17, normal 21; velocity has none), the joints as names, the skin as 4 joint indices + 4 weights.
- **C_INIT_InitSkinnedPositionFromCPSnapshot** (particles.dll 2026-11-12 b10c5654, the install's; vtable 0x1804f69d8,
  init slot 34 **0x18015d710**): fields +0x1e8 m_nSnapshotControlPointNumber (1), +0x1ec m_nControlPointNumber (0, the
  CP whose model skins it), +0x1f0 m_bRandom, +0x1f4 m_nRandomSeed, +0x1f8 m_bRigid, +0x1f9 m_bSetNormal, +0x1fa
  m_bIgnoreDt, +0x1fc / +0x200 the normal velocity min / max, +0x204 the index mode, +0x380 m_flIncrement, +0x384
  m_nFullLoopIncrement, +0x38c / +0x390 m_flBoneVelocity / Max, +0x394 m_bCopyColor, +0x395 m_bCopyAlpha, +0x396
  m_bSetRadius. Nothing happens unless the snapshot has attributes 31 and 32 (the joints, the weights: their
  stream slots +0xa64 / +0xa68 with the manager's types, vfn 0x120 of 0x180655c60), and 21 / 6 / 7 / 3 for the
  flags that copy them. The joint names (+0xb30 count, +0xb38) map to the CP model's bones (18037c4c0; -1 -> bone 0).
  The CP's bone count (cp +0xbc) 0: the snapshot position copied as it is. The index: sequential (wrap
  ((i / count) x m_nFullLoopIncrement + i) % count, step (int) m_flIncrement) or m_bRandom's table. The skinning
  (0x1800a3b10): weights w0..w2, w3 = clamp(1 - w0 - w1 - w2, 0, 1); each joint naming a bone: that bone's world
  transform times its inverse bind (18035c940), blended (0x1800a2b90); position and previous position = M x the
  snapshot's position; m_bSetRadius: radius x M's largest axis scale (18035d560) unless m_bRigid. The local
  position, joints and weights stay on the particle (attributes 15, 31, 32 at coll +0x350 / +0x3d0 / +0x3d8).
- **C_OP_MovementSkinnedPositionFromCPSnapshot** (vtable 0x180503740, Operate slot 34 **0x180206810**): each frame the
  kept local position skinned again against the CP's bones as they are.
- Ours: fx/particles/functions/ported_skinned.js (the snapshot index kept in attribute 14 instead of 31 / 32: the same
  joints and weights read back from the snapshot), snapshot.js (the asset's joints / skin, setCpSkin), fx/effects.js
  loadSnapshot (bullet-fx.js loads the one it needs), client/fx/taser-skin.js (the drawn body's bones: mesh.matrixWorld
  x bindMatrixInverse x the skeleton's bone matrix x bindMatrix x C, C = CS2 model space to the glb's, (x, z, -y) x
  0.0254).
- **The disassembly** (2026-11-16, tools/re/game/disasm.py on the installed particles.dll): the blend 0x1800a3b10 keeps
  the joints that name a bone (not 0xffff, below the bone count, the previous frame's count when Mprev is blended,
  the cache's) in order and **0x1800a2b90** sums them: 1 the matrix as it is (no weight), 2 w1 M1 + w0 M0, 3 (w1 M1
  + w0 M0) + w2 M2, 4 ((w1 M1 + w0 M0) + w2 M2) + w3 M3 per element. Each bone's matrix 18035c940(the current bone
  table +8, 0x50 apart: +0x20 position / scale, +0x30 quaternion; the inverse binds +0x30, 0x20 apart): rows
  ((a2 b2 + a1 b1) + a0 b0) + a3 in the 4th lane. A point through M (18036ac00 -> 18035ec60): per row (m3 + m1 y)
  + (m2 z + m0 x). The init (0x18015d710, 0x18015e5c7..0x18015ec20): the joints (attribute 31, map[j % joints] %
  bones), the local position (15, the snapshot's), the three weights (32); m_bSetNormal: the normal through M
  (18035ec20) unless m_bRigid, l = ((x x + 1.1920929e-07) + y y) + z z, rsqrtss and one Newton step ((3 - e l e) (e
  0.5)), the normal velocity lerp(min, max, T[c914 + c910++]) x prev dt unless m_bIgnoreDt; m_bSetRadius: radius x
  maxss(maxss(|sx|, |sy|), |sz|) (18035d560); position M x local, previous position M x (local + that velocity)
  (m_bRigid: both 0); the bone velocity (m_flBoneVelocity != 0 and the CP's previous time +0xa4 != -1, Mprev all
  finite): (M.t - Mprev.t) x (1 / (cp +0xa0 - +0xa4)) x m_flBoneVelocity, clamped to m_flBoneVelocityMax when above
  0 (180052250), x prev dt unless m_bIgnoreDt, off the previous position. The operator (0x180206810, 0x1802072b0..):
  each frame every particle takes a snapshot index again (SNAPSHOT_INDEX_DIRECT: (int) m_flReadIndex % count;
  m_bRandom; else from m_nSnapShotStartPoint by (int) m_flIncrement, m_nFullLoopIncrement's wrap) and moves toward
  it by t = m_flInterpolation (per particle; 1): no bones, the snapshot's values; bones, M x local (and the normal,
  the radius) as above. All of it is in ported_skinned.js, float for float; fx/particles/functions/skinned-test.mjs
  checks it on the baked system. The one thing not CS2's bits: rsqrtss's estimate is the CPU's own (Intel and AMD
  differ), so the port takes the exact 1 / sqrt before the same Newton step; and the bone matrices are the drawn
  body's (three's skinning), not CS2's skeleton's.

Precache: 180830770 (both systems).

## Dry fire (server, for the client's prediction)

The Zeus and every gun go through BaseGunFire's empty branch (1809f8a70 at 1809f8ada: m_bFireOnEmpty +0xf50, set
by the primary branch on an empty clip): **180a1e400** (PlayEmptySound, once per command number +0xf34):
`Weapon_Taser.ChargeNotReady` for weapon_taser (its vdata name against the string), `Default.ClipEmpty_Pistol` for
WEAPONTYPE 1, `Default.ClipEmpty_Rifle` otherwise, from the weapon through a PAS filter (180c83a60, attenuation 0.8
180c864b0) less the predicting player (180c8c8d0: its client plays its own); then **180b763d0**(weapon, delay, 0): the
primary clock (+0xeb0 tick / +0xeb4 fraction, 180b3baa0) delay from now, and the secondary (+0xeb8 / +0xebc,
180b3bbe0) too when the vdata's +0x4c6 links the cooldowns; the delay 0.2 (0x3e4ccccd) unless the R8 (vfn 0xd28 =
vdata m_bIsRevolver +0x71e: its cycle); then the dry fire activity (1809f7840: 0x32, the R8 0x66) and
m_bWaitForNoAttack. (1809ffd30, another gate, does the same with 0 delay.) Ours: the sim's gate (fire_gate.rs:
dry_fire, 0.2 s, wait for release); loadout.js's 'dry' -> zoom-events.js: a `snd` to everyone but you;
viewmodel.js's gate (DRY_FIRE_DELAY 0.2, once a press) -> onDry(emptySound) from your pawn (main.js);
weapon-use.js emptySound. The client's 180820310 names ChargeNotReady the same way. The sounds: lasers-bake
--event-sounds Default.ClipEmpty_Pistol / _Rifle into ze-armsrace/sounds (the 'ar' table every mode loads).

## The third person

The worldmodel graph (player/anim/worldmodel.json) tests `weapon_taser` among the pistol branch's weapon_types
(between weapon_fiveseven and weapon_p250), so a body with the Zeus is weapon_category_pistol
(world/anim-graph/params.js). The held model is the viewmodel bake's weapon_stock.glb (pistol_taser), as every gun's.
Another player's rope starts where the server puts it (the cstaserrope's start: server/cs2web/combat/taser-rope.js):
the pawn's weapon_hand_r attachment. Every CS2 agent model has it (lasers-bake --attachments: 80 of pak01's 183 player
models, all 141 agents in data/agents.js; each on hand_R at (-2.6, -1.4, 0), rotation (-0, 0, 1, -4.37e-8): 180
about z; the decompiled vmdl's AttachmentList, VRF Model.Attachments), so the rope leaves the hand, not the gun's
`wpn` bone. A model without it: the pawn's WorldSpaceCenter (vfn 0x2c8, 18015a2f0).

## Assets

- tools/bake-fp.mjs pistol_taser: weapon_pist_taser.vmdl (bones weapon, weapon_offset, taser_meter, ag1_hand_r,
  trigger; attachments muzzle_flash on weapon_offset (4.817, -0.001, -0.719), camera_inventory, keychain, nametag,
  stattrak, weapon_holster_center), clips draw / idle / lookat01 / shoot1 (animation/anims/viewmodel/pistol/
  pistol_taser), graphs viewmodel_gun+taser and viewmodel_inspects+taser.
- lasers-bake --event-sounds: Weapon_Taser.Single / .ChargeReady (+ _Zap) / .ChargeNotReady (+ _Empty) / .Draw /
  .Charging, Player.WeaponSelectionFoley, in web/public/ze-armsrace/sounds (the audio table 'ar').
- lasers-bake --impacts: impact_taser_bodyfx (bake/ImpactBake.cs); the tracer was already there (weapons.vdata).
- The kill feed's and the list's icon: panorama icons/equipment/taser.svg (already in the panorama bake).
