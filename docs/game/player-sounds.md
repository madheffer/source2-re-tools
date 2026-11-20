# Player and physics sounds: who hears which sound event

server_20261105.dll (image base 0x180000000) unless said; client_20261105.dll for the client cvars. Read 2026-11-12
(decompiler for the flow, tools/re for strings, callers, slots and schema offsets). The port: web/server/cs2web/
damage-sounds.js, web/src/cs2web/player/player-sounds.js, server/cs2web/core/items.js `touched` (the pickup), hit-sounds-test.mjs.
The physics impact sounds (a dropped weapon's) are sections 5 (the server) and 6 (vphysics2's events); their port:
rubikon/src/Simulation/CollisionEvents.cs, web/src/world/impact-sounds.js, audio/surfaces.js `impact`,
src/cs2web/world/impact-sounds-test.mjs.

## 1. The pieces

| What | Where |
|---|---|
| EmitSound(out*, filter*, entity index, EmitSound_t*) | `180f69780` (EmitSound_t: +0 name, +0x14 volume = 1.0, +0x28 = 100; README) |
| an entity's EmitSound(entity, out*, name, 0, 0, 1, 0) | `180f695d0` |
| CRecipientFilter ctor | `180c83dd0`; the mask is at filter +8 (two u32 words, bit = slot), +0x10 a predicting client's slot, +0x16 "skip the predicting player" |
| AddAllPlayers | `180c84870`: every controller whose connection state (+0x514) is 0 or 3 |
| AddRecipient(player, withObservers) | `180c84e00`: the player, and with the flag every controller whose pawn observes that player (observer services vfn 0xb8 mode == 2, vfn 200 target == the player) |
| RemoveRecipient(player) | `180c8b6a0`: the player and, the same way, whoever observes them in mode 2 |
| RemoveRecipient(controller) | `180c8b610`: clears one bit |
| add the HLTV | `180c84a60`: controllers with m_bIsHLTV (+0x510) |
| the PAS filter with an attenuation | `180c83a60` (vtable 1818e4a70) + `180c864b0(filter, entity, 0.8)`: vfn 0x560 true -> that one recipient (`180c84c60`), else `180c861f0(filter, entity vfn 0x6b8's point, attenuation)` (unread: who is in earshot) |
| one PAS sound from a pawn | `180a77710(pawn, excluded controller, name)`: the filter above, minus the controller, EmitSound from the pawn's index, with the global 181e23e88 set to 1 around it |
| the attacker a server need not tell | `180a77f60(info, head)`: the info's attacker (+0x3c) when it is a player pawn that is also the inflictor (+0x38) and whose controller's block at +0x708 has the byte +0x49 (body) / +0x4a (head) set -> that controller, else 0. Read as the client's cl_predict_body_shot_fx / cl_predict_head_shot_fx (client.dll registers both at 1800ad583 / 1800ad633, client-side userinfo, the defaults read as 0): a client that predicts its hit effects is left out of the server's copy |
| smoke on a line | `1809bff80(from*, to*, 0)`: sums over the active smoke grenades (list head 181faa578, next +0xb60, active +0xb6c) |

Schema offsets used (tools/re/game/schema.py): m_bHasHelmet item services +0x49 (the pawn's m_pItemServices +0xb18),
m_ArmorValue pawn +0x1514, m_bHasFemaleVoice pawn +0xe6a, m_MoveType entity +0x2f5 (`1803d95f0`), m_bFreezePeriod
game rules +0xd8. The damage info: +0x38 inflictor, +0x3c attacker (handles), +0x4c the damage type bits, +0x68 the
trace, +0x7c the solids shot through before the hit (shots.md). The damage result: +0 the info, +0x20 m_flDamageDealt.

## 2. A hit: the damage services' post `180a94400` -> `180a95310(services, result, armored)`

The post (OnTakeDamage_Alive's, shots.md) first sets pawn +0x1494 when armor was hit and none is left, then:
`armorDmg = services +0x4c` (dmg_armor of this hit); **no sound when `type & (armorDmg < 1 ? 0x20 : 0x28)`**: a fall
(DMG_FALL 0x20) never, a burn (DMG_BURN 8) not when the armor took part of it. Else `180a95310(services, result,
armorDmg > 0)`, in order:

1. hit group = the trace's (`180cacf80`) only when `type & DMG_BULLET (2)` and the info has a trace; **head = (group
   == 1)**. excluded = `180a77f60(info, head)`.
2. `type & 8` (burn): `Player.BurnDamage` (armored: `Player.BurnDamageKevlar`) by `180a77710`; done.
3. `type & 0x80` (DMG_CLUB): `Flesh.BulletImpact` (armored: `Player.DamageKevlar`) the same way; done.
4. the victim's health (`180cf7020`) < 1: nothing (the death's sounds play instead).
5. `(int)m_flDamageDealt <= 0`: `Player.DamageKevlar` by `180a77710`; done.
6. attacker = the info's attacker if it is a player (vfn 0x558 and 0xca8), else none.
7. **The attacker's feedback** needs: an attacker, `type & 6` (bullet or slash), then a line from the attacker's eye
   (vfn 0x5e8) to the victim's (filter vtable 18178c240, the two pawns passed to `1801d6c60`; mask unread) and
   `(info +0x7c == 0 || (fraction >= 1.0 && !startsolid))`, then `1809bff80(attacker eye, victim eye) < 1.4`.
8. **Not the head**:
   - feedback: filter = AddRecipient(attacker, observers) minus `excluded`; `Player.DamageBody.AttackerFeedback`, with
     `type & 4` (slash) `Player.DamageBody.Knife.AttackerFeedback`; armored: `Player.DamageBodyArmor.AttackerFeedback` /
     `...Armor.Knife.AttackerFeedback`. Emitted from the victim's index (`180c8cbc0`); the params' +0x24 gets
     `180590da0(181ff56c8, attacker, victim's 1803d6f50)` (unread).
   - onlookers: AddAllPlayers, RemoveRecipient(attacker) only if the feedback played, RemoveRecipient(victim), the
     HLTV added: `Player.DamageBody.Onlooker` / `Player.DamageBodyArmor.Onlooker`, from the victim's index.
   - the victim: AddRecipient(victim, observers): `Player.DamageBody.Victim` / `Player.DamageBodyArmor.Victim`,
     **from the attacker's index** when there is one (`1813aa290`), else the victim's. Then a sound parameter on it:
     `1805c0a60(181ff56a0, filter, the sound's handle, 0xdd82057c, { type 3, 4 bytes: 1802143f0(victim) })` (the
     parameter's name and use are unread).
9. **The head** (armored here = the victim's m_bHasHelmet, not the armor hit):
   - the victim: `Player.DamageHeadShot.Victim` / `Player.DamageHeadShotArmor.Victim`, from the victim's index.
   - feedback (the same gate): `Player.DamageHeadShot.AttackerFeedback` / `...HeadShotArmor.AttackerFeedback`, then
     the same 0xdd82057c parameter with `1802143f0(attacker)`.
   - onlookers as above: `Player.DamageHeadShot.Onlooker` / `Player.DamageHeadShotArmor.Onlooker`.

Every EmitSound_t here has volume 1.0 and +0x28 = 100; a damage without an attacker still plays the victim's and the
onlookers' events (a map's generic trigger_hurt).

## 3. A death: `CCSPlayerPawn::Event_Killed 1802089a0` -> `180ac13d0(pawn, info)` first, before the armor is zeroed

attackerEnt = the info's attacker (any entity); attacker = it when a player. Head and excluded as in a hit.

- **Head**: no attackerEnt -> nothing. Else `Player.DeathHeadShot.AttackerFeedback` (helmet: `...HeadShotArmor...`) to
  AddRecipient(attackerEnt, observers) minus excluded; then, only with a player attacker, the onlookers'
  `Player.DeathHeadShot[Armor].Onlooker` (all, minus the victim and the attacker, plus the HLTV) and the victim's
  `Player.DeathHeadShot[Armor].Victim`. All from the victim's index. Done.
- **Else**: name = `Player.Death` (`Player.DeathFem` with m_bHasFemaleVoice); `type == 0x100` exactly (DMG_SHOCK):
  `Player.DeathTaser` / `Player.DeathTaser_F`. It plays (the PAS filter, attenuation 0.8, from the pawn) when there is
  no attackerEnt, or when the attackerEnt's class isn't derived from the class at `18212afd8` (the walk over the entity
  class's bases: identity +8, +0x60 / +0x18). **That class is read as CCSPlayerPawn** from its other users (the
  weapons' owner casts `180a01880` / `180a019e0` / `180a01b40`, `180b0a700`) but not confirmed by name: UNSETTLED.
  So a player's kill has no `Player.Death`.
- then armored = `m_ArmorValue > 0` and the hit group is 0, 2, 3, 4, 5 or 8 (the legs 6 / 7 aren't; the group is 0
  unless a bullet's trace). With a player attacker: the victim's `Player.DeathBody.Victim` / `...BodyArmor.Victim`
  and the onlookers' `Player.DeathBody[Armor].Onlooker`; with any attackerEnt the feedback
  `Player.DeathBody[Armor].AttackerFeedback` (minus excluded). No line / smoke gate on a death's feedback, and no
  Knife variant.

## 4. A pickup: `CCSPlayer_WeaponServices::BumpWeapon 180b1c290`'s tail (pickups.md has the rest)

`silent = 18024b730(_, pawn)`: 1 when the game rules exist, **m_bFreezePeriod is 0** and the pawn's velocity
(`1803d6fb0`) has a 2D length (`1801cd370`: sqrtss(vy vy + vx vx)) **< 135.2**. It is item_pickup's `silent` field, and
when 0 the pawn (`180b0a410`) emits by `180f695d0`: `Player.PickupGrenadeAudible` for a CSWeaponType 9 (grenade),
`Player.PickupC4` for type 7 (vdata +0x520), else `Player.PickupWeaponAudible`.

Unread: `Player.PickupWeapon` (server: 180a6ee50, 180a6f6f0, 180ac8330, 180aea0a0; the ammo extraction's is in
pickups.md) and the picker's own `Player.PickupWeaponSilent` (client.dll 180c77710, on item_pickup presumably).
`Player.PickupWeapon` was named by items.js but baked into no table until 2026-11-17 (silent): it is in ze-fx/sounds
now (SoundBake.cs GrenadeEvents; one file, items/pickup_weapon_02.wav, volume 0.7).

### Armour: `CItemKevlar` / `CItemAssaultSuit` MyTouch (read 2026-11-17)

vtable slot **0x9a8** (309; tools/re/game/vtowner.py): `CItemKevlar` vtable 0x1817892f0 -> **1801b3820**, `CItemAssaultSuit`
vtable 0x181787380 -> **1801b36b0**. (item, pawn): nothing unless the pawn's vfn 0x558 and vfn 0xca8 are both true
(unread: presumably IsPlayer / IsAlive). Then:

- the suit only: the item services' (pawn +0x163*8 = +0xb18) m_bHasHelmet (+0x49) = 1 (1801b3d70 the network change);
- both: m_ArmorValue (+0x1514) = 100 (1801b3c30 the change); kevlar leaves the helmet as it was;
- 18023a540(pawn) (unread);
- if the pawn's vfn 0x550 is true (unread): a CRecipientFilter (180c83dd0, vtable 181785ca8) with **AddAllPlayers**
  (180c84870), the *item's* entity index (1813aa290), and EmitSound (180f697b0, volume 1.0f) of
  `Player.EquipArmor_CT` for team 3 (pawn +0x344) else `Player.EquipArmor_T`;
- returns 1 (taken), 0 when the gate failed.

How a game_player_equip / GiveNamedItem armour reaches it: GiveNamedItem (180ab85f0) with no position (param 6 null)
sets the weapon services' +0xd8 to 1, and for an entity that isn't a weapon (its dynamic cast, 1816b6d80 to the weapon type 181effb00, is null; a weapon goes to 180e36650)
calls its vfn **0x4b8** with the pawn: CBaseEntity::Touch 1803eeac0 (both items' slot), which runs the entity's
m_pfnTouch (+0x2b0) and the other's vfn 0x4c8 / 0x4b8. TODO(trace): which function m_pfnTouch holds for a CItem (the
MyTouch caller: vcalls.py 0x9a8 lists 15 call sites, none read). The buy menu's armour does not come here: item_kevlar
180a6f6f0 / item_assaultsuit 180a6ee50 play Player.PickupWeapon (buy.md; from the pawn, 180f695d0, with no silent test: item_pickup's silent is 0; cs2-buy.js, buy-test.mjs). Port: server/cs2web/core/game.js
mapPlayerEvent 'equip' (equip-armor-test.mjs); the sound is sent from the pawn (the item spawns on it: 180ab85f0 takes
the pawn's origin + 5 z, then 180571ca0, unread) to everyone.

### Nearly empty: the low-ammo click (client_20261105.dll, read 2026-11-17 with tools/re, not in Ghidra)

WeaponSound_t's names (server table 0x181956c..: 32-byte {name*, value} entries): WEAPON_SOUND_NEARLYEMPTY = **12**,
IMPACT 13, REFLECT 14, SECONDARY_IMPACT 15, SECONDARY_REFLECT 16, RELOAD 17, SINGLE_ACCURATE 18, ZOOM_IN 19 (fire-gate.md's
0x13), ZOOM_OUT 20, RADIO_USE 23 (0x17, grenades.md). The legacy script keys (client 0x1821d70b0: empty, ..., nearlyempty,
reload, single_shot_accurate) are items_game.txt's `sound_nearlyempty "Default.nearlyempty"` (44 prefabs); weapons.vdata
sets m_aShootSounds NEARLYEMPTY -> Default.nearlyempty on the guns. The weapon vdata's sound map is at +0x4f8 (count
+0x504, elements +0x508, 0x28 each) on both sides; its find is server 1809aec60 / client 1807c3d20.

The server reads slot 12 nowhere (1809aec60's eight callers: the zoom 1809c05c0 / 1809c0660, 1809c0760, the grenades
1809d3cd0 / 1809d4a50, the vdata parse 180c9e320 / 5b0 / 7e0). The client plays it in **FX_FireBullets 180d25990**
(weapon = its rdx, kept in r12), right after the shot's own sound (180d25dcf: 180d26730 with the shot's slot, SINGLE
or 0x12 SINGLE_ACCURATE):

- `weapon_near_empty_sound` on: its handle 0x1825c3ec0, `+0x58` the value (registered by client 1800f5c00 and server
  180056a10: flags **0x6000** = replicated 0x2000 + cheat 0x4000, default **1**, no help text);
- the weapon not null; its vfn **0xa48**(0) > 1 (the max clip: read by use, it must exceed 1 and divides);
- `f32(vfn 0xa58(0)) / f32(vfn 0xa48(0)) <= 0.2f` (`comiss` 0x181acff20 = 0.2f against the quotient; the clip over the
  max clip, both cvtdq2ps);
- then **180d26730(the same player / entity, weapon, 12, the shot's r9, volume = the shot's xmm7, sound level 100
  (0x64), the shot's [rbp+0x518])**. 180d26730 (client): the weapon's vdata (1807cd090), the slot's event name through
  1807c3d20, then the emit (its tail unread).

FX_FireBullets runs before BaseGunFire's Clip1 - 1 (fire-gate.md: FX_FireBullets, ..., Clip1 - 1), so the clip it
reads still holds this round: a 30-round mag clicks on its last 6 rounds, a 5-round AWP on its last. Port:
client/core/sounds.js nearEmptySound, called from game.js onShot with the viewmodel's clip + 1 (the viewmodel takes the
round before its onShot); near-empty-test.mjs; the cvar in console/game.js (readonly: the server's, ours is 1).
TODO(trace): who calls FX_FireBullets on a copy that doesn't own the gun (the others' shots: whether their clip is
known there; ours plays the click for your own gun only), and 180d26730's emit (who hears it: the event is positional,
1100 u). Default.NearlyEmpty: lowammo_01.wav, volume 1.5, delay 0.05 s, position_offset z 60 (not applied, as for
every event).

### The accurate shot: the shot's slot and pitch (client_20261105.dll FX_FireBullets 180d25990, read 2026-11-18)

At 180d259c1 `a = min(1.0f, the inaccuracy argument [rbp+0x4e8])` (minss). Before the shot's sound (180d25d03):
- `shift = min(a, snd_max_pitch_shift_inaccuracy) x vdata m_flInaccuracyPitchShift (+0x7e0)` (minss, mulss); the
  cvar's handle is 1825c3ee8 (registered at 1800f5700: default **0.08f**, no flags, no help);
- the slot argument ([rbp+0x508]) is **2** (WEAPON_SOUND_SINGLE) and vdata **m_flInaccuracyAltSoundThreshold
  (+0x7e4) > 0 and > a** (two comiss / jbe): the slot becomes **0x12** (WEAPON_SOUND_SINGLE_ACCURATE) and the shift 0;
- the pitch passed to 180d26730 is `100 + (int)shift` (cvttss2si; add 0x64); the volume is 0 when [rbp+0x528] is 0.

weapons.vdata sets the two numbers on the Negev alone (-50 and 0.02; 83 other entries are 0) and its
WEAPON_SOUND_SINGLE_ACCURATE is `Weapon_Negev.SingleFocused` (items_game's `sound_single_shot_accurate` says the
same). So: under 0.02 the focused shot at pitch 100; from 0.02 the plain shot at 99 down to 96 (0.08 and over). On our
server a standing spray reads 0.0102 (focused), 0.027..0.047 for shots 2..12 (pitch 99 / 98), then 0.016 from shot 13
(focused while held): combat/shot-sound-event-test.mjs.

Port: client/core/sounds.js `shotSound` (your own shot from the predicted accuracy, GunAccuracy.peek; others' from the
fire event's `ia`, which combat.js sends only for a gun that sets either number), WeaponBake's fireSoundAccurate /
inaccuracyAltSoundThreshold / inaccuracyPitchShift, the cvar in console/game.js, shot-sound-test.mjs. A silenced
shot's slot is SPECIAL1 (9), never 2: taken from the bake's sound pick (fire-gate.md), no silenced gun has an
accurate sound.

### Ricochet: the bullet impact's second sound (client_20261105.dll 180b9b490 [client_20261015 180b99a70], read 2026-11-18)

The impact effect's sound function (called from 180d27a20 in the 10-15 build; (this, the trace's record, the impact's
data)). The surface is the record's own (+0) or, for a fraction >= 1 without the flag +0xbb / the same entity with a
non-zero surface index, the physics properties' by the data's index (+0x4c): vphysics2's CPhysSurfaceProperties
(schema, vphysics2_20261103: m_audioSounds +0x48 with m_bulletImpact +0x20 and m_meleeImpact +0x40; m_audioParams
+0xa8 with m_flOcclusionFactor +0x1c).
- the name: the data's damage type bit 0x80 (DMG_CLUB) and a non-empty m_meleeImpact (+0x88), else m_bulletImpact
  (+0x68). **Empty: return** (no ricochet either).
- the impact sound is queued (a 0x48-byte job to 1827a2190's vfn 0x428: position, the name, the data's fields);
- **`RandomFloat(0, 100) <= r_impact_ricochet_chance x (surface +0xc4 x 100)`** (180b9b66f..180b9b6a2: the cvar's
  handle 182566f30, registered at 1800d42f0 with default **0.3f**, flags 0x4000 cheat; mulss 100, mulss the cvar;
  comiss chance, roll; jb skips): **`FX_RicochetSound.Ricochet`** at the impact's position, volume 1.0, pitch 100
  (180c0ae30). +0xc4 is m_audioParams.m_flOcclusionFactor: the .vsurf's `audioparams.occlusionFactor` (1.0 on 111 of
  the 164 stock surfaces: 30 %; 0.0 on 22: never; 0.8 on 24; 0.2, 0.7 x 2, 1.025 .. 1.1 on the rest).

The second user of the name, 18122ed70 [18122a370], is an effect handler (a position and a normal from its data, the
sound from the entity through 180c1b230): its dispatcher isn't read (nothing found that sends it).

Port: audio/ricochet.js (the roll: Math.random for tier0's unseeded RandomFloat), audio.js bulletImpact, the surface's
`occlusion` in surfaces.json (bake/SurfaceBake.cs; tools/surface-occlusion.mjs added it to the 33 baked maps'
tables; `woodladder`, not in the stock file read, stays 1), the cvar in console/game.js, shot-sound-test.mjs.

### The vdata sound slots, and items_game's sound keys nobody reads (read 2026-11-18)

The weapon vdata's m_aShootSounds find (server 1809aec60 / client 1807c3d20) has these callers and no others: the
zoom's (server 1809c05c0 / 1809c0660; client 1807cf6c0 / 1807cf760), the decoy's shot (1809c0760, the thrower's
gun's slot 2 or 9), StartGrenadeThrow (server 1809d3cd0 at 1809d401c, client 1807dfaa0: **slot 2**), ThrowGrenade
(1809d4a50: the radio's slot 0x17), the client's 180d26730 (its two callers both in FX_FireBullets) and the KV3 map's
parse (180c9e320 / 180c9e5b0).

items_game.txt's `visuals` keys `sound_single_shot` / `sound_nearlyempty` / ... (the legacy names' table at server
181dbd890, 16-byte {name, WeaponSound_t} entries: empty 0, secondary_empty 1, single_shot 2, ...) are parsed into the
item definition's visuals at **+0xf8 + slot x 8** (server 18101cf10 at 18101d8dc, client 181115d80) and **read by
nothing**: no instruction in either DLL loads `[reg + index x 8 + 0xf8]` but the two stores (a byte scan; the one
other match, client 181651818, is libjpeg's table). So a sound named only there never plays:
- **`Flashbang.Throw`, `HEGrenade.Throw`, `IncGrenade.Throw`** (the grenade prefabs' sound_single_shot): the grenades'
  vdata has no WEAPON_SOUND_SINGLE (only RADIO_USE and NEARLYEMPTY), so StartGrenadeThrow's slot 2 finds nothing and
  emits nothing. (The throw you hear is the viewmodel clip's Weapon_*.Throw / *.Throw event.)
- **`c4.plant`**: weapon_c4's vdata WEAPON_SOUND_SINGLE, but slot 2 is only read for a grenade's throw, a decoy's gun
  and a bullet shot; the C4 fires none of them (the plant's sounds are c4.initiate / c4.plantquiet: c4.md).

### Drowning: CCSPlayer_WaterServices' think (read 2026-11-17)

Vtable 0x181928258; slot **0x60** = 180b1d420 (a jmp) -> **180b25450**, run by CBasePlayerPawn::PreThink (180d079f0)
walking the pawn's components (+0xb58, next +0x40): once per command, before its movement. Fields (schema):
m_NextDrownDamageTime +0x48, m_nDrownDmgRate +0x4c, m_AirFinishedTime +0x50 (GameTime_t), m_flWaterJumpTime +0x54,
m_vecWaterJumpVel +0x58, m_flSwimSoundTime +0x64. Constructor 180afd350: both times 0 (18017ca80), +0x68 0, +0x6c -1,
+0x70 / +0x74 0; the rate is left. Slot 0xc8 (**180b1e110**, the reset): +0x50 = 0.0f, +0x4c = 2. Slot 0xc0
(180b02680): false. Slot 0xb8 (180b1c0f0) is the water-level change callback (pawn vfn 0x698 180b67370: the wade
sounds, ported in world/water-move.js).

180b25450: m_nActualMoveType (+0x2f5, 1803d95f0) 7 (noclip) without a move parent (1803d95d0): the reset, done.
m_iHealth (180cf7020) >= 0 and alive (vfn 0x550), else nothing. **m_flWaterLevel (pawn +0x404) != 1.0** (or slot
0xc0): when m_AirFinishedTime != 0 and < now (18017e2d0), **Player.DrownStart** from the pawn (180f695d0); the reset.
Fully under: m_AirFinishedTime 0 -> now + 12.0f (18017dc70); then when it's < now and m_fFlags (+0x388) has no 0x4000
(FL_GODMODE) and m_NextDrownDamageTime < now: the rate + 1 (at most 5) as the damage, CTakeDamageInfo (180fba3a0)
with the world as inflictor and attacker (180c10aa0(0x18218b950, 0)) and **DMG_DROWN 0x4000**, TakeDamageOld
(1803ed610), m_NextDrownDamageTime = now + 1.0f. now = 180c86d00's tick x interval (180927cb0). So: 12 s of air,
then 3, 4, 5, 5 ... a second apart (65 ticks: the compares are strict), the gasp on surfacing after the air ran out.
Port: server/cs2web/core/drowning.js (drowning-test.mjs), game.js preThink before p.move. UNSETTLED: a player's move
parent (none here); the rate before the first reset (0 here); a respawn's reset of the services (respawn 180249530
doesn't call them directly: the state stays with the pawn, as CS2 keeps the pawn).

### Fall damage and Player.DamageFall (read 2026-11-17)

CheckFalling (180abb840) out of water, after a moving-down ground's speed is taken off (svc +0x25c) and floored at
0.1: above 580 (`!(580 > f) && f > 580`) it calls **180adc190**(mv) (return ignored), then the impact punch 1.0.
180adc190: the pawn (mv +4's handle) a player (vfn 0x558) and alive (vfn 0xca8), its movement services (+0xb50);
damage = **sv_falldamage_scale x ((svc+0x25c - 580) x 0.23809524f)** (1800c93b0: "sv_falldamage_scale", default 1.0;
the multiply order from the disassembly at 180adc268); only when > 0: CTakeDamageInfo (world, world, damage,
**DMG_FALL 0x20**), TakeDamageOld, then **18020a500** (pawn vfn 0x98): **Player.DamageFall.Fem** when m_bHasFemaleVoice
else **Player.DamageFall**, from the pawn (180f695d0) whether or not the hit killed; a death then fades the screen
(180feb800: black, hold 10000, flags 10) only when CCSGameRules vfn 0x200 is true: 1809236a0 returns false. The client
names neither sound. Port: server/cs2web/core/fall-damage.js (fall-damage-test.mjs), the mover's onLand (the sim's
`landed`, only out of water: move-sim.js) from game.js addPlayer. **Until 2026-11-17 the server had no player fall
damage at all** (BUGFIXES.md).

### Female voice: m_bHasFemaleVoice (read 2026-11-17)

Pawn +0xe6a, set by **1801ff590** (the agent model's setup): m_strVOPrefix (+0xe70) from the agent item's definition
(+0x3a8, CUtlString::Set), then m_bHasFemaleVoice = V_stristr_fast(prefix, "_fem") || IsEqual_CaseSensitive
("fbihrt_epic") || IsEqual_CaseSensitive("swat_epic") (tier0 imports, tools/re/game/impat.py). items_game's vo_prefix values:
balkan_epic, ctm_gsg9, fbihrt_epic, gendarmerie_fem_epic, gendarmerie_male, jungle_fem, jungle_fem_epic, jungle_male,
jungle_male_epic, leet_epic, professional_epic, professional_fem, seal_diver_01..03, seal_epic, seal_fem, swat_epic,
swat_fem; the base agents (tm_phoenix, ctm_sas) have none. Readers: the death (180ac165a: Player.DeathFem /
Player.DeathTaser_F), the fall (18020a500), the jump throw (1809c8542, 1809d3f4d: BaseGrenade.JumpThrowF / M). Port:
src/cs2web/player/female-voice.js (p.voPrefix: '' for every player here, so all are male until econ agents exist).

### A jump throw's grunt (read 2026-11-17)

Both places that set m_bJumpThrow (+0x1283) play it: StartGrenadeThrow (1809d3cd0) at 1809d3efc whenever the release
is inside the jump window (180ad2570, 0.1), m_bJumpThrow already set or not; the ItemPostFrame branch (1809c8320) at
1809c8522 when it wasn't set. A CRecipientFilter (180c83dd0: +0x10 -1, +0x14 0xff, "skip the predicting player" off)
with AddAllPlayers (180c84870) and no prediction rule (180c8c8d0 isn't called), the grenade's entity index (1813aa290),
EmitSound 180f697b0 of **BaseGrenade.JumpThrowF** with m_bHasFemaleVoice (of the owner: 180a02230 in StartGrenadeThrow)
else **BaseGrenade.JumpThrowM**. The client names neither (only m_bJumpThrow): everyone hears the server's, the
thrower too. Port: sim/grenade-hold.js sets N.jumpSound at both, server/cs2web/grenades/grenades.js sends it.

### Your own silent pickup: Player.PickupWeaponSilent (read 2026-11-17)

The pawn's game event handler (client 180c77710; the pawn at this - 0x14c8): for "item_pickup" when the event's userid
is this pawn's and this pawn is the local player's live pawn (180c7781f..: [rbp+0x130]), with `silent` set:
**Player.PickupWeaponSilent** from the pawn (180c0ad30). item_pickup's silent is BumpWeapon's / GiveDefuser's
(18024b730, section 4). Port: server/cs2web/core/items.js silentToPicker (our server sends no item_pickup: the sound
goes to the picker alone).

### Named by CS2 but never played, or not here (read 2026-11-17)

- **BaseEntity.EnterWater / ExitWater**: PhysicsCheckWaterTransition (server 180e8eda0, client 180bae330), from
  PhysicsToss / PhysicsCustom only (180e904c0 / 180e8f1f0: grenades), and CBaseGrenade's bounce touch (server 1808c0940,
  client 1807214b0) instead of its bounce sound: all read the water type (1803d9e70), which a grenade never gets
  (grenade-sim.js: SetWaterType only from the player's CheckWater and the VPHYSICS fluid touch 180d05340, which plays
  nothing). Never played.
- **Underwater.BulletImpact**: FX_TracerSound's type 0x10, which no caller passes (tracer-sound.md).
- **Bounce.Glass / Metal / Flesh / Wood / Shrapnel / Shell / Concrete / ShotgunShell** (+ 0x400 / 0x800 forms): a
  C_LocalTempEntity's hit-surface sound (client 180c30510, from its frame 180c2d7b0 = vtable 0x181c86658 slot 0x8d0) by
  its sound flags (+0x1284: 1 glass, 2 metal, 4 flesh, 8 wood, 0x10 shrapnel, 0x20 shell, 0x40 concrete, 0x80 / 0x1000
  shotgun shell); nothing writes a temp entity's +0x1284 (fieldwrites: the six stores are other classes' network
  setters) and neither DLL has the BreakModel / EjectBrass temp entities that set them. Never played (CS2's shells are
  particles).
- **BaseCombatCharacter.AmmoPickup**: GiveAmmo (server 180c86d20: m_iAmmo[type] + count up to the max, the sound from
  the pawn unless told not to; from 180b61580 = CBasePlayerWeapon slot 0xaf8 and 180b7a440); the event's volume is 0.0
  (game_sounds_player): silent in CS2.
- **Player.DenyWeaponSelection**: CCSHudWeaponSelection::SelectWeapon (client 1811ae590, slot 0x268; 10-15 1811a9bc0)
  when the selected weapon's CanBeSelected (vfn 0x998: 180805ce0 = an owner and vfn 0x9e0; the knife 18082f260 true)
  fails: vfn 0x9e0 is true for guns, the C4 and the Zeus (1807e24a0), and for a grenade (1807e2450) (UsesClip and clip
  > 0) or reserve > 0. Only a spent grenade still held fails. **Every caller pre-filters** (read 2026-11-18 in the
  10-15 build, vtable 0x181d21320): SelectSlot (slot 0x248, 1811a9cb0, from the slot keys and the per-grenade binds
  0x288.. -> 0x2d8 180c19e30 with the slot) takes GetNextActivePos (0x258, 180c0cc30), which keeps only weapons with
  vfn 0x9e0 and CanBeSelected (with **hud_fastswitch** 2, 0x9e0 alone: client 1800dded0, default not 2); next / prev
  (0x228 1811a68c0, 0x230 1811a6980 via 1811a7530 / 1811a77c0) and 0x2f0 / 0x2f8 / 0x300 (1811a5f30, 1811a5ac0,
  1811a6450) all test CanBeSelected (vfn 0x998) before SelectWeapon. So the deny needs a candidate that passed 0x9e0
  but has no owner (180943870 null) under hud_fastswitch 2: a weapon in your list with its owner already cleared, a
  transient network state our client never has. **Not played in normal play; nothing to port.** SelectSlot plays
  Player.WeaponSelectionFoley when the pick isn't the active weapon (already baked for Arms Race).

### Ragdolls' and the client's own bodies' impact sounds (read 2026-11-18)

The client runs its own physics events: the dispatcher **1803ae000** (client) calls **1803ce260**(system, &scratch,
event, index) for both bodies (index 0 and 1) of a collision event (flag bit 0) unless its +0x77 byte is set.
1803ce260 (the client's twin of the server's 1805a9c70): speed = **|(vz nz + vy ny) + vx nx|** (1803b7840: the
event's +0x38.. vectors, no mass or speed scale) and nothing unless **speed > 70.0** (the server has no such floor);
event +0xf8 must hold a list with a non-zero count; the body (event +8) must be dynamic (vfn 0x20 == 2); the body's
entity (vfn 0x478 -> the entity list) must exist (a client-side entity: the death ragdolls are); the surface (event
+0x20 + index x 4) non-zero; volume = **min(1, speed^2 x 9.765625e-06)**; then the queue **1803a3bc0**(system, the
other entity, 0, the body (event +8 + index x 8), the surface, the other surface (+0x24 / +0x20), volume, speed, the
contact point event +0x28) (the server's queue 180575ab0's twin; the client flush is unread). So CS2's ragdolls do
play their surface's impacts (a player model's ragdoll surface: flesh, so Flesh.ImpactHard / ImpactSoft, the
impact-speed volume curve of the event) when a part hits at more than 70 u/s. **Not ported**: ours play none
(world/ragdoll-world.js gives no collision events to the sound side). TODO: the client's queue and flush (1803a3bc0,
its flush's caller), which surface a ragdoll part's shape has (the model's physics data), the event's +0xf8 list,
then the ragdoll world's contact starts with their speed (rubikon CollisionEvents as world/impact-sounds.js uses).
- **Player.Surf.***: client 1808de830, gated by **sv_surf_sounds** (1800b2e70: replicated 0x82000, default 0, "Should
  we try to play sounds for surf?") and surf_speed_slow / med / fast: off in CS2 unless a server sets it. GFL's value is
  unread (docs/GFL_CVARS.md).
- **Glass.Strain**: CBrokenGlassTrap (server 1808d6e70, vtable 0x1818aff68 slot 0x48: the cash stack model) -> 1808c0d90:
  a player within 30 u looking down past 34 degrees (or the trap moving): the sound from the player, the
  molotov_broken_glass particle, the trap removed. No such entity here.
- **DogTags.Pickup / PickupDeny**: CItemDogtags (1809c8eb0, slot 0x9a8) and the cash stack touch (1808c63a0);
  **ItemSoda.Bounce** (180d3d490), **Metal.SawbladeStick** (180bc68b0), **SprayCan.Shake / Paint** (18024cb10, graffiti):
  entities and modes this game doesn't have.

## 5. Physics impact sounds (a dropped weapon hitting the floor): the server

The data: a weapon's world model shapes carry a surface property (`WeaponRifle`, `WeaponPistol`, `WeaponSMG`,
`WeaponSniper`, `WeaponShotgun`, `WeaponHeavy`, `WeaponKnife`, `WeaponC4`, the grenades'), whose impactHard /
impactSoft events are `weapon.Rifle.Impact` ... (game_sounds_physics.vsndevts: csgo_mega, mixgroup Physics, `volume
1.5`, block_duration 0.2, block_distance 25, block_match_entity, instance_limit 3, a child `weapon.Rifle.Impact.
Rattles`, and **`use_impact_speed_input_volume_mapping_curve`** with `impact_speed_input_volume_mapping_curve`
(0 -> 0.114, 203.1 -> 0.305, 408.6 -> 1.0)). The bake's surfaces.json already has the names per surface.

The code path:

- **The dispatcher `180582670(physics game system, world)`**: the physics world's events (world vfn 0x3d0; 0x100 bytes
  each: +0 flags, +8 / +0x10 the bodies, +0x18 / +0x1c the entities' handles, +0x20 / +0x24 the surface indices).
  Flag 1 = a collision, 4 = a start touch, 8 / 0x10 others. For a collision it builds the game's event (+0 / +8 the
  bodies, +0x10 / +0x14 the surfaces, **+0x18 = 10.0** (the time since the pair's last collision is not kept),
  **+0x1c the collision speed = |n . v| x (scaleA + scaleB) / 2** with the contact's vectors from `180571240` and each
  body's vfn 0x430 scale, +0xd8 / +0xe0 the entities), and calls each entity's **VPhysicsCollision (vfn 0x278)**.
  Which contacts vphysics2 turns into a collision event: section 6. The exact speed (180582b90..180582bf1):
  `|((Vy Ny + Vz Nz) + Vx Nx)| x ((tsA + 0 + tsB) x 0.5)`, V and N from the adaptor `180593af0` (section 6).
- **vfn 0x278 `180d1a340`** (CBaseEntity's; the weapons, CPhysicsProp's sound slot too): vfn 0x280, then clears flag
  0x40 of m_fFlags-like +0x414 on an entity slower than 1 u/s.
- **vfn 0x280 `180d1a420(entity, index, event)`** (every weapon class and CBaseEntity: vslot of CAK47 1818f1b98,
  CCSWeaponBase 1818ec818, CKnife 1819154a0, CHEGrenade 181914520): needs the other entity, either one's m_MoveType
  == 5 (VPHYSICS), and (event +0x18 >= 0.5 or the other isn't itself). Both surfaces' game material
  (`180c00e80`: index at surface +0x10 into the table at 18218e4f8 +0x28) must differ from the id at `181e27f58`
  (unread which material: a silent one). Then **`1805a9c70(system 181ff5690, entity, body, other body, surface, other
  surface, speed, 1.0)`**, then the impact effects (`180e8df50` / `180e8dde0` by `181e27f5c` / `181e27f60`).
- A second caller `180cbd840`: an entity hit by a dynamic body (the other's vfn 0x20 == 2) whose own surface has
  +0xc0 > 0 (read as the audio block's m_flStaticImpactVolume): the same call with that as the scale.
- **`1805a9c70`**: `volume = min(1, speed x speed x 9.765625e-06 x scale)` (1 / 320 squared), then the queue
  `180575ab0(system, entity, entity index, body, other body, surface, other surface, volume, speed, 0)` and the
  listeners at system +0x510 / +0x518.
- **The queue `180575ab0`** (entries of 0x28 bytes at system +0x4d0, count +0x4c8: +0 entity handle, +4 entity index,
  +8 volume, +0xc speed, +0x10 the other body's mass (vfn 0x128 when its vfn 0x20 == 2, else 500.0), +0x14 surface,
  +0x18 other surface, +0x1c position): `speed += 0.0001`; an entry already queued with the same surface, or any
  entry once more than 4 are queued, absorbs the new one (if its volume is lower it takes the new position, entity
  and other surface; mass = max; volume += the new one; speed = max) and that is all; else a new entry. The position
  is the argument, else the body's (vfn 400), else the entity's origin.
- **The flush `1805ad380`** (CPhysicsGameSystem, vtable 1818078c8 slot 34; also from 1805c83b0): the frame time is
  summed at system +0xd8 and **past 0.05 s** every entry plays, last first: surface = the props (`1823ab5c0` vfn 0xb8,
  Get vfn 8); nothing without a hard sound (surface +0x50). `under = hardVelocityThreshold (surface +0xbc) > 0 &&
  speed < it`. No soft sound (+0x48): skipped when `sv_phys_sound_disable_impact_sounds_under_hard_threshold`
  (object 181ff5818, default false) and `under`, else the hard one. With a soft sound: the soft one when the other
  surface's hardness (+0xac) < this surface's hard threshold (+0xb8), or `under`; else the hard one. Played by
  `1805aa5b0(out, name, entry, other surface's +0xac)`. Then the second queue (+0x4e8, 0x10-byte entries: position,
  surface) plays each surface's +0x78 sound (its break sound; queued by `1805a9a30`, entries of one surface averaged
  once 3 are queued) at volume 1.0 by `1805aaaf0`.
- **`1805aa5b0`**: starts the event (`1805c4680`) for a filter at the entry's position (`thunk 180c84870(filter,
  position)`), then sets its parameters by hash: 0x5a7cce4d = the position (12 bytes), 0x2d8464af = the volume (+8),
  0x41a38e55 = the speed (+0xc: what the event's impact_speed curve reads), 0x4c2cbe7f = the other surface's hardness,
  and one more from +0x10. The names behind the hashes aren't found (tools/re/game/strtoken.py on the obvious ones: none).

The surface data (surfaceproperties.vsurf, 164 surfaces): audioparams has audioreflectivity, audiohardnessfactor (0,
0.2, 0.25, 0.5 or 1.0; 138 are 1.0), audioroughnessfactor, scrapeRoughThreshold, **impactHardThreshold 0.5 on every
one**, occlusionFactor; none has a hard-velocity threshold or a static impact volume, and none names a game material.
So with stock data: the world's own side (CWorld's vfn 0x278 is `180cbd840`, which needs its surface's +0xc0 > 0)
never plays, `under` is never true, and the hard / soft choice is "soft against a surface of hardness < 0.5".

The sound's volume: csgo_mega's stack has one impact input, `public.impact_speed_input`, into a math_curve_2d
(`impact_speed_input_volume_mapping_curve`, run when `use_impact_speed_input_volume_mapping_curve`) multiplied into
the volume chain (soundstacks_csgo_*.vsndstck: `impact_speed_input_volume_mapping_curve_mult`). The parameter hashes
above don't match MurmurHash2 of the obvious names with seed 0x31415926 or 0x53524332: which hash is the speed's is
inferred (0x41a38e55, the entry's +0xc), and whether the 0x2d8464af volume (min(1, speed^2 / 320^2)) reaches the
event's volume is UNSETTLED (not applied in the port).

## 6. vphysics2's collision events (vphysics2_20260924.dll, the build rubikon ports)

- **When** (the collide post-pass's Began list, and the TOI flush's): a contact that starts touching and whose flags
  (+0x74) have 2 goes to `1801fe920(world's tracker, contact, flag)`. The flag is set at the contact's creation when
  the pair's flags (+0x78) keep any of 0x1c, which `1802faf00` leaves only when both shapes' function masks have 4
  and their entity ids differ (and the group table's entry has them: 0x15 / 0x14 for nearly every pair).
- **`1801fe920`**: the body pair's entry in the tracker's table (keyed by the two bodies' ids; +8 counts its touching
  contacts). A new pair: a record in the first list (tracker +0). An existing pair: a record in the second list
  (tracker +0x18) only when the contact is solid (+0x78 bit 0). Flags 8 pairs also join the persist list. Then the
  contact's +0x74 |= 4 (so its end reaches `1801feca0`).
- **The record `1801fa810`** (0x70 bytes): both bodies' frames (+0 / +0x20: origin and scale, +0x10 / +0x30 the
  orientation), +0x40 the contact, +0x48 its manifold cache (ref counted), and with a manifold its first one's
  friction anchor (manifold +4 -> record +0x50) and normal (+0x10 -> +0x5c); without one, the two origins' midpoint and
  their direction.
- **The game's read, world vfn 0x3d0 `180059170`** (after the step): the first list's records become events with
  flags `(solid) | 4` (start touch, and collision when solid), the second list's flags 1 (collision), the persist
  list's 8, ended pairs' 0x10. **So every solid contact that starts touching is one collision event.**
- **The event `180058a90`** (0x100 bytes): +8 / +0x10 the bodies' wrappers, +0x18 / +0x1c the bodies' first dword (the
  entity handle), +0x20 / +0x24 each side's surface property (`18000b970(shape, sub shape, triangle)` record +0x24: a
  hull's own; a mesh triangle's through the mesh's per-triangle material bytes, the triangle from the first manifold
  point's sub shape), +0x28 the point, +0x34 the normal, +0x80 / +0x8c the linear and +0x98 / +0xa4 the angular
  velocities **the frame started with** (body +0x220 / +0x22c) when the frame origin is set (+0x1f8 != FLT_MAX), else
  the current ones (+0x108 / +0x114); +0xb0.. the current ones again.
- **The server's adaptor `180571240` -> `180593af0`**: with a manifold, V = (vA + wA x (P - cA)) - (vB + wB x (P -
  cB)), c the body wrapper's vfn 0x148 (`180011d60`: body +0xfc, its position), in the order
  `Vx = ((rAz wAy - rAy wAz) + vAx) - ((wBy rBz - wBz rBy) + vBx)`, and so on round the axes. The wrapper's vfn 0x430
  (`180011320`) is body +0x9c, the time scale the speed is multiplied by.

The port (rubikon `CollisionEvents`): this port gives every shape entity id -1, so no pair keeps its touch bits and
the event branches of the contact code stay unreached; the recorder tests the pair itself (each body its own entity)
at the same two places and leaves the contact's flags alone, so the simulation is what it was (impact-sounds-test: a
replica that records nothing ends on the same world hash). UNSETTLED: the triangle read when the mesh is the first
shape (here it is always the second); the pair table, start-touch, persist and end events aren't made (physics-touch.js
has its own touches). Not checked against the native DLL (no oracle for events yet).
