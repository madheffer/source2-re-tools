# Weapon drops

server_20261105 ("read" = read in the decompiler); vphysics2 for the body calls. CS2Fixes: virtual_hooks.cpp:898, cbaseplayerpawn.h:42-75, cfg/cs2fixes.cfg:21. The drop side of [pickups.md](pickups.md): what happens to a weapon when it leaves a player's hands (the drop key, a death, CS2Fixes' DropWeapon), and the delays DefaultTouch then reads. `svc` = CCSPlayer_WeaponServices (pawn+0xb10), `pawn` = svc+0x38, `w` = the weapon (CCSWeaponBase).

## Functions

| Address | Module | What |
|---|---|---|
| 1809f3210 | server | CCSWeaponBase constructor (lays the fields out in schema declaration order) |
| 180a24ba0 | server | weapon spawn: +0xffc / +0x1000 = 0 |
| 1809fb3c0 | server | DefaultTouch (thunk 1809f5b4c) |
| 18017e2d0 | server | f32 compare (-1 when curtime is below the stored time) |
| 180926fa0 | server | (gamerules, kind): the death-drop cvar for kind 0 gun, 1 c4, 2 grenade, 3 defuser, 4 taser, 5 healthshot; in warmup (gamerules+0xd9) a kind whose bit is clear in mp_warmup_items_drop_policy reads 0 |
| 180b05300 | server | CCSPlayer_WeaponServices::DropWeapon (svc, w, Vector* target, Vector* vel) (vtable 0x181928778 slot 28 = +0xe0; CS2Fixes' gamedata index 28 on Windows: verified) |
| 180c85ed0 | server | base services' removal from m_hMyWeapons |
| 180b09ee0 | server | (svc, 0): next weapon pick (order unread) |
| 18093d470 | server | gamerules bool (w+0xfdc, unread) |
| 180ad2540 | server | (pawn, 0) (w+0xfdc, unread) |
| 1809fc590 | server | CCSWeaponBase::Drop (weapon vfn 0x9e8) |
| 1809fcb10 | server | the guns' Drop: clears w+0xfc0 and two timers when vdata +0x728 is 1, then 1809fc590 |
| 1809b9750 | server | grenades' Drop (unread) |
| 1809fc1e0 | server | C4's Drop (unread) |
| 180b54f20 | server | owner |
| 180927c50 | server | the tick |
| 180927cb0 | server | curtime (tick) |
| 18017dc70 | server | one float add |
| 180b069d0 | server | the owner's ammo record |
| 1803ed590 | server | scene-node unparent, then vfn 0x5e0 |
| 180cf1850 | server | on the collision property (Drop) |
| 1803f0260 | server | has a physics body (the scene node's model's +0x200 aggregate, part 0) |
| 1803ead30 | server | (1.0) |
| 180ceffe0 / 180e95a10 | server | called in Drop |
| 1809f7840 | server | (w, 1, 0, 0, 1): gameplay activity |
| 1803ee6e0 | server | think cleared |
| 1809ff9b0 | server | the drop's collision (creates the body) |
| 1803ea4a0 | server | SetAbsVelocity |
| 18090c810 | server | gamerules (w) (unread) |
| 180c30c10 | server | UTIL_Remove |
| 180d0f2c0 | server | (collision property, solid, group, mask): new physics |
| 180d10060 | server | solid type 6 |
| FUN_180d0e200 | server | sets the collision group |
| FUN_180d111b0 | server | makes the physics from the model |
| 180cf16a0 / 180cf1ab0 | server | trigger bounds (FSOLID 0x200) |
| 180d0bca0 | server | think at curtime + 30 (a removal, unread) |
| 1803ea490 | server | (1.0) |
| 180b01b60 | server | CSWeaponDrop (svc, w, int mode, Vector* vel): the drop key and the death drop |
| 180b04ef0 | server | splits one off a stack (unread) |
| 181470980 | server | AngleVectors |
| 1803d6fb0 | server | GetAbsVelocity |
| 1814738b0 | server | normalise for lengths outside [1e-17, 1e17] |
| 180d11090 / 180d101e0 | server | collision property after a drop ((3)) |
| 1809f70f0 | server | (w, pawn) |
| 180c86d00 | server | svc time for w+0xfb4 (unread) |
| 180b02490 | server | (svc, w): the kick |
| 180b02400 | server | the kick's k |
| 1803d9e70 | server | in water (pawn+0x412 bit 1 -> bit 16) |
| 1803d9e40 | server | water level: `(int)(pawn+0x404 x 0x18179be70 + 1.0)` |
| 180a25c80 / 180a25530 | server | save / restore 32 bytes on w around the drop (unread) |
| 180235fc0 | server | (w, pawn): OnWeaponDrop |
| 180012620 | vphysics2 | body vfn 0x208 (vtable 1803f44e0): adds velocity |
| 1800146e0 | vphysics2 | body vfn 0x228: adds angular velocity |
| 180b0b020 | server | the drop key (svc, w or 0 = the active weapon, bool silent) (from 180adf5b0; +use swap 180aea0a0 with silent 1) |
| 18093df00 / 1809131d0 | server | a game mode's override of the drop test (pawn) |
| 180a0ebe0 | server | (w, pawn) |
| 180a23da0 | server | buy-time donation |
| 180b05460 | server | the death drop (svc, bool, ...) |
| 1802089a0 | server | CCSPlayerPawn Event_Killed (calls the death drop with 1) |
| 180918aa0 / 180235b60 | server | call the death drop with 0 |
| 180b04ac0 | server | bots' death drop |
| 180a04090 | server | (w) on every weapon at death (unread) |
| 180c86620 | server | Weapon_GetSlot(svc, gear slot, -1) |
| 1809b9780 / 1809b8080 | server | a pin-pulled grenade thrown live at death (server_20261015: 180afd650 -> 1809b17b0, [winpanel.md](winpanel.md) "Fun facts" 0x1f) |
| 18023b000 | server | the team's fire grenade (doesn't resolve; the fallback weapon_molotov stands) |
| 18035bc40 | server | on pawn+0xe38's handle at death (unread) |
| 180588af0 / 1805c9530 | server | the body's pull / push through its bone (sv_phys_animated_hierarchy; scene-node.md "VPhysicsUpdate") |
| 180ca5f30 | server | the weapon's set-up bones (reference pose unread) |
| 1800bef30 / 1800bee90 / 18009d480 / 18009d3c0 / 18009d260 / 18009d310 / 18009d5f0 / 18009d540 / 1800a4080 / 1800cb310 / 1800cb260 | server | cvar registrations (below) |

## Fields

Names are the DLL's schema strings put on the offsets in declaration order (the schema's own offset table isn't read).

| Offset | Field |
|---|---|
| w+0xff8 | bool m_bCanBePickedUp: 1 in the constructor (the map's `ToggleCanBePickedUp`); never cleared by a drop; DefaultTouch does nothing while 0 |
| w+0xff9 | bool (m_bUseCanOverrideNextOwnerTouchTime?): 0 on a drop and at spawn |
| w+0xffc | GameTime m_nextOwnerTouchTime: drop curtime + 0.1; spawn 0 |
| w+0x1000 | GameTime m_nextPrevOwnerTouchTime: drop curtime + mp_weapon_prev_owner_touch_time; spawn 0 |
| w+0x1008 | GameTime (networked) m_nextPrevOwnerUseTime: drop curtime + mp_weapon_prev_owner_touch_time |
| w+0x100c | m_hPrevOwner: the owner it falls from (0xffffffff none) |
| w+0x1010 | int m_nDropTick |
| w+0x1014 | bool (networked) = w+0xefc != 10, on a drop |
| w+0xef8 | bool (dropped): 1 on a drop, 0 at spawn |
| w+0xefa | set to 1 when cvar 182119b00 is set (BumpWeapon's check, pickups.md) |
| w+0xfb4 | float, a time from 180c86d00 (CSWeaponDrop) |
| w+0xfa8 / +0xfbc | m_bInReload / m_bIsHauledBack: cleared by Drop |
| w+0xfc0 | cleared by the guns' Drop |
| w+0xfdc | (18093d470 clear and 180ad2540(pawn, 0)), unread |
| w+0x1034 | buy-time donation flag |
| w+0x2f2 | 1 after CSWeaponDrop |
| w+0x3e8 | effects (bit 0x20 cleared) |
| w+0x1be | = 0x101 |
| w+0x360 | spawnflags (bit 0: solid 3; 0x40000000: the 30 s think) |
| w+0x10 -> +0x30 bit 9 | entity flag: DropWeapon does nothing |
| vdata +0x728 | the guns' Drop clear |
| vdata +0x700 | gear slot (0 rifle, 1 pistol) |
| item definition +0x338 | loadout position |
| pawn +0x2d8 | m_lifeState |
| pawn +0xe38 / +0xe48+0x218 | death-drop handle / count |
| gamerules +0xd9 | warmup |
| gamerules +0xebf | buy-time donation gate |

## Constants

| Cvar | Default | Registered / handle | Notes |
|---|---|---|---|
| mp_weapon_prev_owner_touch_time | 1.5 (0x3fc00000) | 1800bef30, 18212b1b8 | read twice in the drop (+0x1008, +0x1000) |
| mp_weapon_next_owner_touch_time | 1.3 (0x3fa66666, DAT_1817b77c4) | 1800bee90, 18212b1a8 | never read (only its registration and atexit); the drop's 0.1 s is a constant |
| mp_death_drop_gun | 1 | 18009d480, 182119b08 | "0=none, 1=best, 2=current or best, 3=both" |
| mp_death_drop_grenade | 2 | 18009d3c0, 182119b28 | "0=none, 1=best, 2=current or best, 3=all grenades" |
| mp_death_drop_c4 | 1 | 18009d260 | bool |
| mp_death_drop_defuser | 1 | 18009d310 | bool |
| mp_death_drop_taser | 1 | 18009d5f0 | bool |
| mp_death_drop_healthshot | 1 | 18009d540 | bool |
| mp_warmup_items_drop_policy | 0xf7 | 1800a4080, 182119b68 | bits 1 gun, 2 c4, 4 nade, 8 defuser, 16 taser, 32 healthshot |
| mp_drop_knife_enable | 0 | 1800cb310, 1821786f0 | bool |
| mp_drop_grenade_enable | 1 | 1800cb260, 182178700 | bool |
| cs2f_drop_map_weapons (CS2Fixes) | 0 | virtual_hooks.cpp:898, cfg/cs2fixes.cfg:21 | GFL's value unknown (CS2-ZE-Configs holds map configs only) |

| Value | What |
|---|---|
| 0.1 (0x3dcccccd) | m_nextOwnerTouchTime delay |
| DAT_18177bf80 | (0, 0, 0) |
| (100, 100, 100) (0x42c80000 each) | drop angular velocity |
| 0.6 (0x3f19999a) | pawn velocity scale in the throw |
| 80 | the throw's pawn-velocity clamp |
| 250 | throw speed; a given vel clamped to 250 |
| 0.5 | f.z added |
| 110, 0.5 | kick: up / pawn velocity scale |
| 0.0174532924 (DAT_1803fdcf0) | degrees -> radians in vfn 0x228 |
| 0.0048738797 | vfn 0x228's wake threshold on \|w\|² |
| 30 (0x41f00000) | the removal think delay |
| 0xe (14), 0xc3001 | collision group "weapon", interacts-with mask |
| 0x18179be70 | water level scale |
| 0xd7 | stat on a refused drop |

## DefaultTouch (1809fb3c0), a player toucher

`curtime < w+0xffc` -> no pickup (anyone, the dropper included); the toucher is m_hPrevOwner and `curtime < w+0x1000` -> no pickup. (+0xff8 is m_bCanBePickedUp, not "dropped".) A pickup sets no delay.

## DropWeapon (180b05300)

1. No weapon, or entity flag bit 9 -> nothing.
2. `w vfn 0x9e8 = Drop(vel or (0,0,0))`. `target` is never read.
3. 180c85ed0(svc, w).
4. w was active and m_lifeState isn't 1 or 2 -> 180b09ee0(svc, 0) and svc vfn 0xf0 (SelectItem) switches to it.
5. w+0xfdc (unread).

Slots: DropWeapon 28 (+0xe0), BumpWeapon 29 (+0xe8), SelectItem 30 (+0xf0).

## Drop (1809fc590)

1. m_hPrevOwner = the owner (180b54f20); m_nDropTick = the tick; +0x1014.
2. The owner's ammo record (180b069d0) gets clip + reserve (vfn 0xaf0 + 0xac0).
3. +0xef8 = 1; 1803ed590; 180cf1850.
4. movetype = 5 (VPHYSICS) with a physics body (1803f0260), else 4 (FLYGRAVITY); 1803ead30(1.0).
5. Effects bit 0x20 cleared (vfn 0x6c8), +0x1be = 0x101, 180ceffe0, 180e95a10.
6. +0xfa8, +0xfbc cleared; 1809f7840(w, 1, 0, 0, 1); 1803ee6e0.
7. +0x1008 = curtime + mp_weapon_prev_owner_touch_time; +0x1000 = the same; +0xffc = curtime + 0.1; +0xff9 = 0 (one float add each).
8. vfn 0x1b0(0); 1809ff9b0; touch = 1809f5b4c.
9. The throw: no body -> SetAbsVelocity(vel); a body -> body vfn 0x208(vel) and vfn 0x228((100, 100, 100)).
10. Cvar 182119b00 set -> +0xefa = 1; next think on tick + 1 (+1 more when 18217bed4); 18090c810(w).
11. A weapon that isn't vfn 0xd98 with no clip (vfn 0xaf0 < 1) whose owner passes vfn 0x550: removed from the owner's list and UTIL_Remove'd.

## The body (1809ff9b0)

1. 180d0f2c0(collision property, `(spawnflags & 1) x 2 + 1`, 0xe, 0xc3001): the old physics destroyed (vfn 0x248), FUN_180d0e200 sets group 14 (a change to 14 leaves the interacts-as bits, unlike 5 -> debris or other -> touchall), interacts-with |= 0xc3001, solid type 6 (180d10060), movetype 5 (param 1) or 6, the scene node's motion 1 (dynamic) or 3, then FUN_180d111b0 makes the physics from the model. Every drop makes a fresh dynamic body; Drop's second read (after 1809ff9b0) finds it; its first read only picks movetype 4 / 5.
2. Effects bit 0x20 cleared; game rules vfn 0x148 -> FSOLID 0x200 (180cf16a0 / 180cf1ab0) and the touch.
3. maxplayers > 1 and spawnflag 0x40000000 -> think 180d0bca0 at curtime + 30.
4. 1803ea490(1.0).

Every stock weapon's world model binds its one part to `weapon_offset` (under the root `weapon`, the model's offset: 3-22 u): the body is the entity through that bone (pull 180588af0) and the entity the body through its inverse (push 1805c9530).

vfn 0x228 (1800146e0): not finite or a static body -> nothing; angular velocity += `(v k) + w` per axis, k = 0.0174532924; `|w|² = (x x + y y) + z z` over 0.0048738797 wakes it. vfn 0x208 (180012620) adds, so the kick sums onto Drop's velocity.

## CSWeaponDrop (180b01b60)

1. mode != 2: a definition with the "weapon_healthshot" or "grenade" tag with a stack -> 180b04ef0 splits one off.
2. 180926fa0(gamerules, 0) == 0 (mp_death_drop_gun 0, or warmup without bit 1) and w isn't weapon_c4 -> removed (180c85ed0, UTIL_Remove), not dropped.
3. mode 0: DropWeapon(svc, w, 0, 0): no throw, zero velocity.
4. vel given: clamped to 250 u/s (over 250 -> normalised x 250), then DropWeapon.
5. mode 1 (throw): `vel = f x speed + v`; DropWeapon(svc, w, 0, &vel). Speed 250, or 0 when m_lifeState != 0 and w isn't the C4.
6. After: 180d11090 / 180d101e0(3); w+0x2f2 = 1; 1809f70f0(w, pawn); w+0xfb4 = a time.
7. 180b02490: with a body, body vfn 0x208(`pawnVel x 0.5 + (k x 0, k x 0, k x 110)`); k = 1.0, or in water (1803d9e70) at water level >= 3 -> 0, 1-2 -> 0.25.
8. 180a25c80 / 180a25530 around the drop; 180235fc0(w, pawn).

The throw's float order (disassembly 180b01f19..180b02217):

1. `v = pawnVel x 0.6`; `|v|² = (z z + y y) + x x`; `len = sqrtss`.
2. len > 80: inside [1e-17, 1e17] `inv = 1 / len`, each axis x inv, then x 80 (outside: zero length -> 0, else 1814738b0).
3. `f` = AngleVectors(pawn vfn 0x5f0, the eye angles) forward; `f.z + 0.5`; `|f|² = (y y + z z) + x x`, normalised the same way.
4. `vel = f x speed + v` per axis (mulss then addss).

## The drop key (180b0b020)

1. 180926fa0(gamerules, w is weapon_c4) == 0 -> refused ("#SFUI_Notice_CannotDropWeaponDuringWarmup" in warmup).
2. By loadout position (+0x338): 0 (melee) only with mp_drop_knife_enable; 1 (C4) and 2-25 (pistols, SMGs, rifles, heavy) always; 26-31 (grenades) with mp_drop_grenade_enable; 34 always; else refused; 18093df00 (a game mode) overrides with 1809131d0(pawn). Refused -> "#SFUI_Notice_CannotDropWeapon".
3. 180a0ebe0(w, pawn) false -> 1809f70f0 and stat 0xd7; gamerules+0xebf and w+0x1034 clear -> w+0x1034 = 1, 180a23da0.
4. CSWeaponDrop(svc, w, 1, 0); then "#SFUI_Notice_YouDroppedWeapon".

## The death drop (180b05460)

Event_Killed calls it with 1 ("cash_stack:death", "#Notice_Teammate_Death_Location"); 180918aa0, 180235b60 with 0; bots take 180b04ac0.

1. Every weapon: 180a04090(w).
2. weapon_c4 and kind 1 -> CSWeaponDrop(mode 1).
3. weapon_taser, kind 4 and the bool -> mode 1.
4. A defuser (kind 3): a new item_defuser / item_cutters, velocity `forward x 200 + right x RandomFloat(-50, 50)`.
5. The bool, kind 5, weapon_healthshot -> mode 0.
6. Guns by mp_death_drop_gun (180c86620): 0: rifle and pistol removed; 1: the rifle (mode 0), or the pistol when there's no rifle or its drop failed; 2: as 1 unless the active weapon's gear slot is 0 or 1, then no gun here (who drops the active one isn't traced); 3: rifle then pistol, both mode 0.
7. Grenades by mp_death_drop_grenade: a pin-pulled active grenade is thrown live (1809b9780, 1809b8080); 2: else the active grenade (mode 0); 1 or 2 without one: the first carried of the team's fire grenade (18023b000), weapon_molotov, weapon_incgrenade, weapon_smokegrenade, weapon_hegrenade, weapon_flashbang, weapon_decoy; 3: every grenade, each of its count.
8. pawn+0xe38 holds a handle and pawn+0xe48+0x218 > 0 -> 18035bc40.

The knife is never dropped at death, nor a second gun under the default; what's left goes with the pawn.

## CS2Fixes

Its drops call DropWeapon (slot 28) directly, not CSWeaponDrop: no throw (zero velocity), no mp_death_drop_gun removal, Drop's delays all the same. `DropMapWeapons` (cbaseplayerpawn.h:42-75: every weapon with a hammer id that isn't GEAR_SLOT_KNIFE, teleported to the eye in a 0 s timer) runs on an infection (ZR_StripAndGiveKnife) and, with cs2f_drop_map_weapons 1, before a lethal hit (OnTakeDamage_Alive) and in CommitSuicide; EntWatch's transfers use it too.

## GFL's values (read on GFL, 2026-11-09)

mp_death_drop_gun 1, mp_death_drop_grenade 2, mp_death_drop_c4 / _defuser / _healthshot / _taser true, mp_weapon_prev_owner_touch_time 1.5, mp_drop_knife_enable false, mp_drop_grenade_enable true, sv_extract_ammo_from_dropped_weapons false: all CS2's defaults.

## Unread

- Where a held weapon's world position is when it's unparented (1803ed590: the scene node keeps its transform? the bone-merged hand position?).
- GFL's cs2f_drop_map_weapons; who drops the active gun under mp_death_drop_gun 2; Weapon_Equip's writes to these fields; 180b09ee0's pick order.
- 180ca5f30's reference pose; the drops of grenades (1809b9750) and C4 (1809fc1e0); 180b04ef0, 18090c810, 180d0bca0, 180a04090, 18035bc40, 180a25c80 / 180a25530.
