# CS2 weapon drops, traced from server.dll 2026-11-05 (RUST_PORT phase 3)

The drop side of [pickups.md](pickups.md): what CS2 does to a weapon when it leaves a player's hands (the drop key, a
death, CS2Fixes' DropWeapon), and the delays DefaultTouch then reads. `svc` = CCSPlayer_WeaponServices (pawn+0xb10),
`pawn` = svc+0x38, `w` = the weapon (CCSWeaponBase). Addresses are server_20261105.dll in the Ghidra project; "read" =
read in the decompiler. Field names are the schema strings in the DLL ("m_nextOwnerTouchTime", ...) put on the offsets
in declaration order (the constructor 1809f3210 lays them out in that order); the schema's own offset table isn't read.

## The weapon's drop fields

| w+ | type | name (schema order) | set by |
|---|---|---|---|
| 0xff8 | bool | m_bCanBePickedUp | 1 in the constructor 1809f3210; never cleared by a drop |
| 0xff9 | bool | (m_bUseCanOverrideNextOwnerTouchTime?) | 0 on a drop and at spawn |
| 0xffc | GameTime | m_nextOwnerTouchTime | drop: curtime + 0.1 (0x3dcccccd, a constant); spawn 180a24ba0: 0 |
| 0x1000 | GameTime | m_nextPrevOwnerTouchTime | drop: curtime + mp_weapon_prev_owner_touch_time; spawn: 0 |
| 0x1008 | GameTime (networked) | m_nextPrevOwnerUseTime | drop: curtime + mp_weapon_prev_owner_touch_time |
| 0x100c | handle | m_hPrevOwner | drop: the owner it falls from (0xffffffff for none) |
| 0x1010 | int | m_nDropTick | drop: the tick (180927c50) |
| 0x1014 | bool | (networked; = w+0xefc != 10) | drop |
| 0xef8 | bool | (dropped) | 1 on a drop, 0 at spawn |
| 0xfb4 | float | (a time) | CSWeaponDrop: a time from svc 180c86d00 (unread) |

**Correction to pickups.md**: +0xff8 isn't "a dropped weapon". It is m_bCanBePickedUp (1 from construction, the
map's `ToggleCanBePickedUp`), and DefaultTouch 1809fb3c0 does nothing at all while it's 0. Inside, for a player
toucher: `curtime < w+0xffc` → no pickup (anyone, the dropper included); the toucher is m_hPrevOwner and
`curtime < w+0x1000` → no pickup. The compare is 18017e2d0 (-1 when curtime is below the stored time).

## Cvars (registrations read)

| cvar | default | registered at | notes |
|---|---|---|---|
| mp_weapon_prev_owner_touch_time | 1.5 (0x3fc00000) | 1800bef30, handle 18212b1b8 | read twice in the drop (+0x1008, +0x1000) |
| mp_weapon_next_owner_touch_time | 1.3 (0x3fa66666, DAT_1817b77c4) | 1800bee90, handle 18212b1a8 | **never read**: the only xrefs are its registration and atexit. The drop's 0.1 s is a constant |
| mp_death_drop_gun | 1 | 18009d480, handle 182119b08 | "0=none, 1=best, 2=current or best, 3=both" |
| mp_death_drop_grenade | 2 | 18009d3c0, handle 182119b28 | "0=none, 1=best, 2=current or best, 3=all grenades" |
| mp_death_drop_c4 | 1 | 18009d260 | bool |
| mp_death_drop_defuser | 1 | 18009d310 | bool |
| mp_death_drop_taser | 1 | 18009d5f0 | bool |
| mp_death_drop_healthshot | 1 | 18009d540 | bool |
| mp_warmup_items_drop_policy | 0xf7 | 1800a4080, handle 182119b68 | bitfield 1 gun, 2 c4, 4 nade, 8 defuser, 16 taser, 32 healthshot |
| mp_drop_knife_enable | 0 | 1800cb310, handle 1821786f0 | bool |
| mp_drop_grenade_enable | 1 | 1800cb260, handle 182178700 | bool |

The death-drop cvars are read through **180926fa0(gamerules, kind)**: kind 0 gun, 1 c4, 2 grenade, 3 defuser, 4 taser,
5 healthshot; during warmup (gamerules+0xd9) a kind whose bit is clear in mp_warmup_items_drop_policy reads 0.

CS2Fixes: `cs2f_drop_map_weapons` (virtual_hooks.cpp:898, default 0 in cfg/cs2fixes.cfg:21). GFL's value isn't in
CS2-ZE-Configs (that repo holds map configs only): **unknown**.

## The functions

- **CCSPlayer_WeaponServices::DropWeapon `180b05300`** (vtable 0x181928778 slot 28 = +0xe0, CS2Fixes' gamedata index 28
  on Windows: verified; BumpWeapon is slot 29 = +0xe8, SelectItem 30 = +0xf0). `(svc, w, Vector* target, Vector* vel)`:
  - no weapon, or w's entity flag bit 9 (+0x10 → +0x30) → nothing;
  - **w vfn 0x9e8 = CCSWeaponBase::Drop(vel or (0,0,0))** (DAT_18177bf80 is three zero floats). `target` is never
    read;
  - 180c85ed0(svc, w): the base services' removal from m_hMyWeapons;
  - w was the active weapon and pawn+0x2d8 (m_lifeState) isn't 1 or 2 → 180b09ee0(svc, 0) picks the next weapon and
    svc vfn 0xf0 (SelectItem) switches to it (the pick order is unread);
  - w+0xfdc = (a gamerules bool 18093d470 clear and 180ad2540(pawn, 0)): unread.
- **CCSWeaponBase::Drop `1809fc590`** (weapon vfn 0x9e8; the guns' 1809fcb10 first clears w+0xfc0 and two timers when
  the vdata's +0x728 is 1, then calls it; grenades 1809b9750, C4 1809fc1e0, unread):
  - m_hPrevOwner (+0x100c) = the owner (180b54f20); m_nDropTick = the tick; +0x1014 as above;
  - the owner's ammo record (180b069d0) gets clip + reserve (vfn 0xaf0 + 0xac0);
  - +0xef8 = 1; 1803ed590 (scene-node unparent, then vfn 0x5e0); 180cf1850 on the collision property;
  - **movetype = 5 (VPHYSICS) when it has a physics body (1803f0260), else 4 (FLYGRAVITY)**; 1803ead30(1.0);
  - effects (+0x3e8) bit 0x20 cleared (vfn 0x6c8), +0x1be = 0x101, 180ceffe0, 180e95a10;
  - +0xfa8 and +0xfbc cleared; 1809f7840(w, 1, 0, 0, 1); 1803ee6e0 (the think cleared);
  - **+0x1008 = curtime + mp_weapon_prev_owner_touch_time; +0x1000 = the same; +0xffc = curtime + 0.1; +0xff9 = 0**
    (curtime = 180927cb0(tick), the sums 18017dc70 are one float add);
  - vfn 0x1b0(0); **1809ff9b0** (below); touch = 1809f5b4c (DefaultTouch's thunk);
  - **the throw: no physics body → SetAbsVelocity(vel) (1803ea4a0); a body → body vfn 0x208(vel) and vfn
    0x228((100, 100, 100)) (the angular velocity, 0x42c80000 each)**;
  - cvar 182119b00 set → +0xefa = 1 (BumpWeapon's check, pickups.md); next think on tick + 1 (+1 more when
    18217bed4); gamerules 18090c810(w) (unread);
  - at the end, a weapon that isn't vfn 0xd98 with no clip (vfn 0xaf0 < 1) whose owner passes vfn 0x550: removed from
    the owner's list and UTIL_Remove'd (180c30c10).
- **1809ff9b0** (the drop's collision): 180d0f2c0 on the collision property (group 0xe, mask 0xc3001; solid 1, or 3
  with +0x360 bit 0), effects bit 0x20 cleared, the game rules' vfn 0x148 → FSOLID 0x200 (the trigger bounds,
  180cf16a0 / 180cf1ab0) and the touch; maxplayers > 1 and spawnflag 0x40000000 (+0x360) → think 180d0bca0 at
  curtime + 30 (0x41f00000; a removal, unread); 1803ea490(1.0).
- **CSWeaponDrop `180b01b60`** `(svc, w, int mode, Vector* vel)`: what the drop key and the death drop call.
  - mode != 2: a weapon whose definition has the "weapon_healthshot" or "grenade" tag with a stack → 180b04ef0 splits
    one off (unread);
  - **180926fa0(gamerules, 0) == 0 (mp_death_drop_gun 0, or warmup without bit 1) and w isn't weapon_c4 → w is
    removed (180c85ed0, UTIL_Remove), not dropped**;
  - mode 0: DropWeapon(svc, w, 0, 0): **no throw, zero velocity**;
  - vel given: clamped to 250 u/s (length over 250 → normalised x 250), then DropWeapon;
  - mode 1 (throw): `f` = AngleVectors(pawn vfn 0x5f0, the eye angles) forward (181470980), f.z += 0.5, normalised;
    speed 250, or 0 when pawn m_lifeState != 0 and w isn't the C4; `v` = pawn GetAbsVelocity (1803d6fb0) x 0.6,
    clamped to length 80; **vel = f x speed + v**; DropWeapon(svc, w, 0, &vel);
  - after: the collision property 180d11090 / 180d101e0(3); w+0x2f2 = 1; 1809f70f0(w, pawn); w+0xfb4 = a time;
  - **180b02490(svc, w)**: with a physics body, body vfn 0x208(pawnVel x 0.5 + (k x 0, k x 0, k x 110)), k = 180b02400:
    1.0, or with the pawn's in-water flag (1803d9e70: pawn+0x412 bit 1 → bit 16) water level (1803d9e40: (int)(pawn+0x404
    x 0x18179be70 + 1.0)) ≥ 3 → 0, 1-2 → 0.25. vfn 0x208 is vphysics2's 180012620 (vtable 1803f44e0): it **adds**
    (rubikon BodyOps.AddVelocity), so the kick sums onto Drop's velocity;
  - 180a25c80 / 180a25530 save and restore 32 bytes on w around the drop (unread); 180235fc0(w, pawn): the
    OnWeaponDrop notification.
- **The throw's float order** (the disassembly 180b01f19..180b02217; sim/src/game/drop.rs): `v` = pawnVel x 0.6
  (0x3f19999a), |v|² = (z z + y y) + x x, `len = sqrtss`; len > 80: inside [1e-17, 1e17] `inv = 1 / len`, each axis x inv,
  then x 80 (out of range: zero length → 0, else 1814738b0, unported); `f` = AngleVectors forward (181470980), f.z + 0.5,
  |f|² = (y y + z z) + x x, normalised the same way; `vel = f x speed + v` per axis (mulss then addss).
- **The body**: CCSWeaponBase::Drop reads it at the start (1803f0260: the scene node's model's +0x200 aggregate, part 0)
  only to choose movetype 4 / 5; **1809ff9b0 creates it**: 180d0f2c0(collision property, (spawnflags & 1) x 2 + 1, 0xe,
  0xc3001): the old physics destroyed (vfn 0x248), FUN_180d0e200 sets group 14 ("weapon": a change to 14 leaves the
  interacts-as bits, unlike 5 → debris or other → touchall), interacts-with |= 0xc3001, solid type 6 (180d10060), movetype
  5 (param 1) or 6, the scene node's motion 1 (dynamic) or 3, then FUN_180d111b0 makes the physics from the model. So
  every drop makes a fresh dynamic body (rubikon/src/Game/Weapon.cs), and Drop's second read (after 1809ff9b0) finds it.
- **vfn 0x228** (vphysics2 1800146e0): angular velocity += v x 0.0174532924 (DAT_1803fdcf0) per axis ((v k) + w), not
  finite or a static body → nothing, |w|² ((x x + y y) + z z) over 0.0048738797 wakes it (BodyOps.AddAngularVelocity).
- **The drop key `180b0b020`** `(svc, w or 0 = the active weapon, bool silent)` (from 180adf5b0, and the +use swap
  180aea0a0 with silent = 1):
  - 180926fa0(gamerules, w is weapon_c4) == 0 → refused ("#SFUI_Notice_CannotDropWeaponDuringWarmup" in warmup);
  - by the item definition's loadout position (+0x338): 0 (melee) only with mp_drop_knife_enable; 1 (C4) and 2-25
    (pistols, SMGs, rifles, heavy) always; 26-31 (grenades) with mp_drop_grenade_enable; 34 always; anything else
    refused; 18093df00 (a game mode) overrides with 1809131d0(pawn). Refused → "#SFUI_Notice_CannotDropWeapon";
  - 180a0ebe0(w, pawn) false → 1809f70f0 and a stat (0xd7); gamerules+0xebf and w+0x1034 clear → w+0x1034 = 1,
    180a23da0 (the buy-time donation);
  - **CSWeaponDrop(svc, w, 1, 0): the throw**; then "#SFUI_Notice_YouDroppedWeapon".
- **The death drop `180b05460`** `(svc, bool, ...)` (called from CCSPlayerPawn's Event_Killed 1802089a0 with 1:
  "cash_stack:death", "#Notice_Teammate_Death_Location"; and from 180918aa0, 180235b60 with 0, bots take 180b04ac0):
  1. every weapon: 180a04090(w) (unread);
  2. weapon_c4 and kind 1 → CSWeaponDrop(mode 1, thrown);
  3. weapon_taser, kind 4 and the bool → CSWeaponDrop(mode 1);
  4. a defuser (kind 3): a new item_defuser / item_cutters, velocity forward x 200 + right x RandomFloat(-50, 50);
  5. the bool, kind 5, weapon_healthshot → mode 0;
  6. guns, by mp_death_drop_gun (Weapon_GetSlot 180c86620(svc, gear slot, -1); gear slot 0 rifle, 1 pistol):
     0: the rifle and pistol are removed (UTIL_Remove); 1 (the default): the rifle with mode 0, or the pistol when
     there's no rifle or its drop failed; 2: as 1 unless the active weapon's gear slot (vdata+0x700) is 0 or 1, then
     no gun here (who drops the active one isn't traced); 3: the rifle, then the pistol, both mode 0;
  7. grenades, by mp_death_drop_grenade: a pin-pulled active grenade is thrown live (1809b9780, 1809b8080; in
     server 2026-10-15 180afd650 -> 1809b17b0, read in winpanel.md "Fun facts" 0x1f, ported: grenades.js deathThrow); 2 (the
     default): else the active grenade (mode 0); 1 or 2 without one: the first carried of the team's fire grenade
     (18023b000), weapon_molotov, weapon_incgrenade, weapon_smokegrenade, weapon_hegrenade, weapon_flashbang,
     weapon_decoy; 3: every grenade, each of its count;
  8. pawn+0xe38 holds a handle and pawn+0xe48+0x218 > 0 → 18035bc40 on it (unread).
  **The knife is never dropped at death**, nor a second gun under the default; what's left goes with the pawn.
- **CS2Fixes' drops** call DropWeapon (slot 28) directly, not CSWeaponDrop: no throw (zero velocity), no
  mp_death_drop_gun removal, but CCSWeaponBase::Drop's delays all the same. `DropMapWeapons` (cbaseplayerpawn.h:42-75:
  every weapon with a hammer id that isn't GEAR_SLOT_KNIFE, teleported to the eye in a 0 s timer) runs on an
  infection (ZR_StripAndGiveKnife) and, with cs2f_drop_map_weapons 1, before a lethal hit (OnTakeDamage_Alive) and in
  CommitSuicide; EntWatch's transfers use it too.

## What this means for server/cs2web/core/items.js

- **Pinned**: any drop leaves the weapon untouchable for 0.1 s for everyone and 1.5 s for its dropper (m_hPrevOwner).
  A pickup sets no delay. The drop key drops the active weapon, never a knife (mp_drop_knife_enable 0), grenades yes.
- **Physics, done (2026-11-09)**: every drop makes the weapon a dynamic rubikon body on every copy (the 'v' / 'k'
  stimuli carry the server's velocities: src/cs2web/sim/weapon-drop.js → sim/src/game/drop.rs; world/entities/classes/
  weapon-body.js): the key's throw (CSWeaponDrop mode 1), a death's mode 0, the C4's mode 1 at a death, each with the
  kick; CS2Fixes' DropWeapon (infection, transfers) with neither; the (100, 100, 100) spin. physics.bin carries every
  weapon's world model physics under its class name (bake/RubikonBake.cs from pak01 weapons.vdata m_szWorldModel).
  Checked: `node web/server/cs2web/core/drop-test.mjs` (the hop, the fall, G flat / up / down / running, the replica on the same
  bits), wasm-oracle (20,000 throws, native = WASM). Left: a weapon body in the map's triggers (physics-touch.js knows
  physboxes), the held weapon's own frame and velocity before the drop, pickup by the body's touch (the reach box
  stays), a removed body stays in the world as a static one with no layers.
- **The body on its bone** (2026-11-10, scene-node.md "VPhysicsUpdate"): every stock weapon's world model binds its
  one part to `weapon_offset` (under the root `weapon`, the model's offset: 3-22 u), so the body is the entity through
  that bone (the pull 180588af0, sv_phys_animated_hierarchy) and the entity the body through its inverse (the push
  1805c9530). weapon-body.js does both from the bake's physics_bones.json (spawn, throw, keyframed drive, teleport,
  follow); the entity is pushed every tick its body is awake. Checked: weapon-bone-test.mjs on all four maps. Left:
  the bones' reference pose for the weapon's set-up bones (180ca5f30); the creation (1809ff9b0 -> 180d0f2c0) taken to
  place the body as the pull does.
- **Unknown**: where a held weapon's world position is when it's unparented (1803ed590: the scene node keeps its
  transform? the bone-merged hand position?); GFL's cs2f_drop_map_weapons (items.js drops every non-knife map item at
  a death, which is cs2f_drop_map_weapons 1's DropMapWeapons; with 0, CS2's own death drop keeps only the best gun and
  one grenade, and a map pistol under a rifle would vanish); who drops the active gun under mp_death_drop_gun 2;
  Weapon_Equip's writes to these fields; 180b09ee0's next-weapon pick order.

## GFL's values (read on GFL by the owner, 2026-11-09: docs/GFL_CVARS.md)

mp_death_drop_gun 1, mp_death_drop_grenade 2, mp_death_drop_c4 / _defuser / _healthshot / _taser true,
mp_weapon_prev_owner_touch_time 1.5, mp_drop_knife_enable false, mp_drop_grenade_enable true,
sv_extract_ammo_from_dropped_weapons false: all CS2's defaults. So a death drops the best gun and one grenade (the
one in hand, else the first carried of the team's fire grenade, molotov, incendiary, smoke, HE, flash, decoy: 180b05460
step 7, read 2026-11-09; the team string's function 18023b000 doesn't resolve here, the code's own fallback
weapon_molotov stands), never the knife; a zombie's knife item dies with it (EntWatch); C4 items drop and can be picked
up, with EntWatch's glow. (An earlier note here had every grenade dropping, mode 3, from the owner's account: the cvar
reads 2.) server/cs2web/core/items.js dropAll / deathGrenades.
