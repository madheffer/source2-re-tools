# Map damage, heals, filters, a few base inputs

server_20261105. CS2Fixes detours.cpp:103-175, playermanager.cpp:125, 573-592, events.cpp:122-131; GFL mapcfg/ze_dark_souls.cfg. The 2026-09-23 build's addresses: rubikon/CS2_RUNTIME.md "Physboxes in hurt, push and teleport triggers".

## Functions

| Address | Module | What |
|---|---|---|
| 1803e5db0 | server | CBaseTrigger vfn 0x878 PassesTriggerFilters (flag test) |
| 180cfa4f0 | server | vehicle condition (flag test 0x20 / 0x200) |
| 180bbf960 | server | trigger filter (m_hFilter) test |
| 180fdbc60 | server | CTriggerHurt vfn 0x888 StartTouch hook |
| 1803e55c0 | server | called first in the start hook (unread) |
| 180fce8c0 | server | HurtThink |
| 180fce460 | server | HurtAllTouchers(dt) |
| 180fce600 | server | vfn 0x8c0 HurtEntity(other, damage) |
| 180fba3a0 | server | CTakeDamageInfo ctor (inflictor, attacker, damage, type) |
| 180fcd1d0 | server | GuessDamageForce |
| 1803ed610 | server | TakeDamageOld (no result) |
| 180fdafc0 | server | vfn 0x890 EndTouch hook |
| 1803e5360 | server | CBaseTrigger EndTouch |
| 180fa1350 | server | CTriggerHurt input SetDamage |
| 18020d1c0 | server | parameter as float |
| 180a93f70 | server | pawn damage services (shots.md 4) |
| 180a88f30 | server | armor step |
| 180cacf80 | server | info +0x68 trace |
| 180a7ab50 | server | finds the weapon (none here) |
| 180a89430 | server | hit group step (only with a trace) |
| 180d8dd60 | server | CFuncMoveLinear Blocked (vfn 0x4d8) |
| 180d3c470 | server | CBaseDoor Blocked |
| 180d8de90 | server | CFuncRotating Blocked (unread) |
| 180ea9390 / 180ea9a00 / 180ea9c00 / 180ea9f20 | server | CPointHurt TurnOn / TurnOff / Toggle / Hurt |
| 180eccfc0 | server | point_hurt's hurt |
| 18137ab40 | server | name search (with the activator) |
| 180fb9d90 -> 180df0300 | server | RadiusDamage |
| 180d15bc0 | server | CCSPlayerPawn vfn 0x3f0 TakeHealth |
| 180d15b30 | server | CBaseEntity TakeHealth (without the tail) |
| 1803e4060 | server | health change callback |
| 1803ce320 | server | (pawn, 0x40000000) in TakeHealth's tail |
| 180bbf990 | server | CBaseFilter PassesFilterImpl (vfn 0x770): true |
| 180bbfda0 | server | CFilterMultiple PassesFilterImpl |
| 180bc0070 | server | CFilterProximity PassesFilterImpl |
| 1803d6f50 | server | abs origin |
| 180bbf9a0 | server | CFilterAttributeInt PassesFilterImpl |
| 180154650 | server | CUtlStringToken: murmur2, seed len ^ 0x31415926 (case folding unread) |
| 180b97870 | server | attribute table lookup |
| 180cc6400 -> 180cfc5e0 | server | input AddAttribute |
| 1803ead90 | server | set attribute to int 1 |
| 180cc64e0 | server | input RemoveAttribute (unread past the dispatch) |
| 180cc5340 -> 180cfcc00 | server | input FollowEntity |
| 180bfca30 | server | FindEntityByName (activator, caller) |
| 1803d6ab0 -> 1803d6b40 | server | follow (this, target, true) -> (this, target, token) |
| 180180300 | server | node SetParent (no transform: world transform kept, scene-node.md) |
| 180cee2e0, 180c27c70 / 180c27b20 | server | physics / effects refresh |
| 1803d6d3e | server | follow with no target branch |
| 180d77fc0 -> 180dadce0 | server | CFuncMoveLinear input TeleportToTarget |
| 180bfc940 | server | FindEntityByName (activator, caller) |
| 1803d91a0 | server | local origin |
| 180ea77c0 | server | point_entity_finder FindEntity (unread) |

## Fields

| Offset | Field |
|---|---|
| CTriggerHurt (vtable 0x18183f7b8) +0x9c8 | m_flOriginalDamage |
| +0x9cc | m_flDamage (current) |
| +0x9d0 | m_flDamageCap |
| +0x9d4 | m_flLastDmgTime |
| +0x9d8 | m_flForgiveDelay |
| +0x9dc | m_bitsDamageInflict (`damagetype`) |
| +0x9e0 | m_damageModel |
| +0x9e4 | m_bNoDmgForce |
| +0x9e8 | m_vDamageForce |
| +0x9f4 | m_thinkAlways |
| +0x9f8 | m_hurtThinkPeriod (not read by the think) |
| +0xa00 / +0xa18 | m_OnHurt / m_OnHurtPlayer |
| +0xa30 | m_hurtEntities |
| CBaseTrigger +0x990 / +0x998 | touch list |
| CBaseTrigger +0x9b0 | m_hFilter |
| entity +0x288 | m_pfnThink |
| entity +0x388 | flags (bit 7 client, bit 12 vehicle) |
| entity +0x2f1 | NPC (1..2) |
| entity +0x2f5 | move type (5 VPHYSICS) |
| entity +0x2e0 | m_takedamage |
| entity +0x2d0 | health |
| damage info +0x68 / +0x70 | trace / flags (bit 18: no armor) |
| CFuncMoveLinear +0x908 | m_flBlockDamage |
| CBaseDoor +0x924 | block damage |
| mover +0x8a4 | m_hActivator |
| CPointHurt (vtable 0x1819d53f8) +0x4a8 | m_nDamage (int) |
| +0x4ac / +0x4b0 / +0x4b4 / +0x4b8 / +0x4c0 | m_bitsDamageType / m_flRadius / m_flDelay / m_strTarget / m_pActivator |
| CFilterMultiple (0x1819389c8) +0x4e0 | m_nFilterType; m_iFilterName[10]; m_hFilter[10] +0x538 |
| filter +0x4a8 | m_bNegated |
| CFilterProximity (0x181939150) +0x4e0 | m_flRadius (`filter_radius`) |
| CFilterAttributeInt (0x181940350) +0x4e0 | m_sAttributeName (`filterattribute`) |
| identity +0x10 -> +0x48 | attribute table (made empty on first use); entry type 1 int at +8, type 2 float |
| model state +0x1c0 | model |
| target +0x1be | set 0x101 by FollowEntity |
| node +0xec | follower flag (released with no target) |
| CFuncMoveLinear +0x90c / +0x854 / +0x8e0 / +0x864 / +0x870 / +0x8a8 | m_flStartPosition / m_flMoveDistance / m_vecMoveDirParentSpace / m_vecPosition1 / m_vecPosition2 / m_vecFinalDest |

## Constants

| Value | What |
|---|---|
| 0.5 | hurt think period / damage scale (at 0x180fce8d6 + 0x7b1ca6 and 0x180fdb05e + 0x7a551e) |
| 64, 1, 2, 0x2000, 8, 0x400, 0x20 / 0x200 | trigger flags: anything, clients, NPCs, interacts-as bit 38, VPHYSICS, collision group 5 or 6, vehicle conditions |
| 0x1000 (4096) | Source 1's "disallow bots": not read (bots touch every trigger) |
| DMG_BULLET 2, DMG_CRUSH 1, blast 0x40, 0xc6 | damage bits (0xc6: bullet, slash, blast, club) |
| 0.5 | armor ratio with no weapon |
| 0x1c9748e6 | bone merge token |
| cs2f_map_steamids_enable | CS2Fixes, default 0 (GFL ze_dark_souls 1) |
| cs2f_fix_block_dmg | CS2Fixes, off by default |

## PassesTriggerFilters (1803e5db0)

- 64 anything; 1 a client (+0x388 bit 7); 2 NPCs; 0x2000 interacts-as bit 38; 8 move type VPHYSICS; 0x400 collision group 5 or 6; then for a player (vfn 0x558) 0x20 / 0x200 vehicle conditions (+0x388 bit 12, 180cfa4f0); then the filter. No other bit read.

## CTriggerHurt

- StartTouch hook: 1803e55c0; with no think, SetThink(HurtThink), next think this tick.
- HurtThink: `n = HurtAllTouchers(0.5)`; n <= 0: SetThink(null); else next think now + 0.5, or now (+0) with m_thinkAlways.
- HurtAllTouchers(dt): model 1: if `now > m_flLastDmgTime + m_flForgiveDelay`, m_flDamage = m_flOriginalDamage; damage = m_flDamage, x dt unless model 1; **m_flLastDmgTime = now every pass**; m_hurtEntities cleared; each toucher in list order through HurtEntity, counted when true; model 1 with n > 0: `m_flDamage = min(m_flDamage + m_flDamage, m_flDamageCap)`.
- HurtEntity: flag test and m_takedamage, else false. damage < 0: TakeHealth(-damage, m_bitsDamageInflict). Else a CTakeDamageInfo (the trigger as inflictor and attacker, type +0x9dc), vfn 0x8b8 on it; force zero with m_bNoDmgForce, m_vDamageForce when non-zero, else GuessDamageForce; TakeDamageOld. Then **OnHurtPlayer for a player pawn, else OnHurt: never both**; other joins m_hurtEntities; true.
- EndTouch hook: an entity not in m_hurtEntities takes HurtEntity(m_flDamage x 0.5), then 1803e5360.
- SetDamage: into m_flDamage only; m_flOriginalDamage keeps its spawn value (model 1 forgives back to it).

## A map's damage on a player

- TakeDamageOld goes the bullet's way (shots.md 4). In 180a88f30 the hit group is 0 (generic) unless the type has DMG_BULLET and the info has a trace (+0x68).
- Armored when the pawn has armor and the type is 0 or has a 0xc6 bit, unless info +0x70 bit 18; ratio 0.5. Then TakeDamageOld's floor with the fraction in m_flDamageAccumulator (a trigger_hurt of 15, 7.5 a think, costs 7 then 8).
- The hit group step (180a89430) runs only with a trace.
- CS2Fixes' TakeDamageOld detour (detours.cpp:103-175: block-all, the block-damage attacker fix for movers and point_hurt, the molotov / grenade cases, prop damage scale) changes nothing here; ZR's knockback needs DMG_BULLET or DMG_SLASH with a hitbox.

## Blocked (vfn 0x4d8)

- Block damage non-zero: CTakeDamageInfo of DMG_CRUSH, the mover the inflictor, the attacker its m_hActivator when that is a pawn (vfn 0x558) else the mover (cs2f_fix_block_dmg turns a pawn attacker back into the world); TakeDamageOld on the blocker.

## CPointHurt

- Hurt stores the activator's handle in m_pActivator and runs 180eccfc0: `damage = cvtdq2ps(m_nDamage)`; a target: each entity 18137ab40 finds, TakeDamageOld with a guessed force; none: RadiusDamage over m_flRadius at the abs origin. Next think now + m_flDelay.

## TakeHealth (180d15bc0)

- m_takedamage 0 -> 0. max = vfn 0x5c8; health < max: `add = min(cvttss2si(amount), max - health)`, health += add (1803e4060). At or above max: nothing (not lowered).
- The pawn's tail: with a gamerules flag (+0x58) and health > 1, 1803ce320(pawn, 0x40000000).
- A trigger_hurt of -5 heals 2 a think; -20 heals 10.

## Filters

- CBaseFilter vtable 0x181938240; PassesFilterImpl slot 0x770.
- **CFilterMultiple**: each of the ten slots in order: a handle with no entity skipped; the filter's PassesFilterImpl with its own m_bNegated. AND (0): false at the first fail, else true; OR (1): true at the first pass, else false. The handles are resolved when the filter activates.
- **CFilterProximity**: r <= 0 (comiss 0 >= r): true. No entity: false. Else d = the filter's abs origin - the entity's, `r x r > (dy x dy + dx x dx) + dz x dz`, f32.
- **CFilterAttributeInt**: no entity: false. The name's token looked up in the identity's table: missing = 0, type 1 int, type 2 float cvttss2si'd; passes when > 0.

## CBaseEntity inputs

- **AddAttribute**: the whole parameter is the name; token; table made if missing; 1803ead90 sets int 1; vfn 0x150.
- **CS2Fixes SetSteamIdAttribute** (playermanager.cpp:573-592): with cs2f_map_steamids_enable, an authenticated non-bot non-HLTV player gets AcceptInput("AddAttribute", "<SteamID64>") on the pawn and the controller, at authentication (playermanager.cpp:125) and in OnPlayerSpawn's 0 s CTimer (events.cpp:122-131).
- **FollowEntity**: FindEntityByName; none: a console message. Then 1803d6ab0 -> 1803d6b40: token 0x1c9748e6 (bone merge) when the target has a model (+0x1c0), else 0. With a target: unless either has identity flag bit 9, target +0x1be = 0x101 and SetParent (180180300), then 180cee2e0, 180c27c70 / 180c27b20. With none (1803d6d3e): only a follower (move type NONE and node +0xec) is let go (SetParent null).

## CFuncMoveLinear TeleportToTarget (180dadce0)

1. m_hActivator = the activator; FindEntityByName (180bfc940); none: done.
2. Teleport (vfn 0x528) to its abs origin, no angles, no velocity; m_flStartPosition = 0.
3. `o` = local origin; `step = m_flMoveDistance x m_vecMoveDirParentSpace`; `m_vecPosition1 = o - step x 0`; `m_vecPosition2 = step + pos1`; m_vecFinalDest = o; all f32 (mulss / subss / addss in that order).

## Unread

- CTriggerHurt vfn 0x8b8 on the damage info; 1803e55c0 in the start hook.
- GuessDamageForce (180fcd1d0) and what the force does to a pawn.
- CFuncRotating's Blocked (180d8de90).
- RemoveAttribute's body; CUtlStringToken's case rule (180154650).
- point_entity_finder FindEntity (180ea77c0): its search and OnFoundEntity's activator / caller.
- FollowEntity's bone-merge pose; node +0xec's meaning (taken as "made a follower by this input").
