# Map damage, heals, filters and a few base inputs (server_20261105.dll, 2026-11-14)

What a map's damage does to a player in CS2 (trigger_hurt, point_hurt, a mover's Blocked), the heal path, the
filters ze_dark_souls leans on (filter_multi's ten slots, filter_proximity, filter_activator_attribute_int and the
CS2Fixes Steam ID attribute it tests), and CBaseEntity FollowEntity / AddAttribute and func_movelinear
TeleportToTarget. Read with tools/re (rtti, vslot, vdiff, disasm, schema, inputs). The 2026-09-23 build's
addresses for the same functions are in rubikon/CS2_RUNTIME.md "Physboxes in hurt, push and teleport triggers".

## CTriggerHurt (vtable 0x18183f7b8)

Fields (schema): m_flOriginalDamage +0x9c8, m_flDamage +0x9cc (the current damage), m_flDamageCap +0x9d0,
m_flLastDmgTime +0x9d4, m_flForgiveDelay +0x9d8, m_bitsDamageInflict +0x9dc (`damagetype`), m_damageModel +0x9e0,
m_bNoDmgForce +0x9e4, m_vDamageForce +0x9e8, m_thinkAlways +0x9f4, m_hurtThinkPeriod +0x9f8 (not read by the think),
m_OnHurt +0xa00, m_OnHurtPlayer +0xa18, m_hurtEntities +0xa30. The touch list is CBaseTrigger's +0x990 / +0x998.

| Slot / address | What |
|---|---|
| 0x878 `1803e5db0` | CBaseTrigger's flag test (PassesTriggerFilters): 64 anything; 1 a client (the entity's flags +0x388 bit 7); 2 NPCs (+0x2f1 in 1..2); 0x2000 the collision's interacts-as bit 38; 8 move type VPHYSICS (+0x2f5 == 5); 0x400 collision group 5 or 6; then for a player (vfn 0x558) 0x20 / 0x200 the vehicle conditions (+0x388 bit 12, 180cfa4f0); then the filter (m_hFilter +0x9b0, 180bbf960). **No other bit is read: spawnflag 0x1000 (4096, Hammer's "disallow bots" in Source 1) does nothing**, so bots touch every trigger players do |
| 0x888 `180fdbc60` | StartTouch's hook: 1803e55c0, then with no think (m_pfnThink +0x288 null) SetThink(HurtThink) and SetNextThink(this tick) |
| `180fce8c0` | HurtThink: n = HurtAllTouchers(0.5); n <= 0: SetThink(null); else the next think at now + 0.5, or now (+0) with m_thinkAlways |
| `180fce460` | HurtAllTouchers(dt): model 1: if now > m_flLastDmgTime + m_flForgiveDelay, m_flDamage = m_flOriginalDamage; damage = m_flDamage, x dt unless model 1; **m_flLastDmgTime = now (every pass, hurt or not)**; m_hurtEntities cleared; each toucher in list order through HurtEntity (vfn 0x8c0), counted when it returns true; model 1 with n > 0: m_flDamage = min(m_flDamage + m_flDamage, m_flDamageCap) |
| 0x8c0 `180fce600` | HurtEntity(other, damage): the flag test (vfn 0x878) and other's m_takedamage (+0x2e0) or false. damage < 0: other's TakeHealth(-damage, m_bitsDamageInflict) (vfn 0x3f0). Else a CTakeDamageInfo (180fba3a0: inflictor and attacker the trigger, damage, type +0x9dc), vfn 0x8b8 on it, its force zero with m_bNoDmgForce, m_vDamageForce when non-zero, else GuessDamageForce (180fcd1d0) toward the target; TakeDamageOld (1803ed610, no result). Then **OnHurtPlayer (+0xa18) when other is a player pawn (vfn 0x558), else OnHurt (+0xa00): one, never both**; other joins m_hurtEntities; true |
| 0x890 `180fdafc0` | EndTouch's hook: an entity not in m_hurtEntities takes HurtEntity(m_flDamage x 0.5), then CBaseTrigger's EndTouch (1803e5360) |

The class's one input, **SetDamage** (`180fa1350`): the parameter as a float (18020d1c0) into m_flDamage (+0x9cc)
only; m_flOriginalDamage keeps its spawn value (model 1 forgives back to it).

Constants: 0.5 at 0x180fce8d6 + 0x7b1ca6 and 0x180fdb05e + 0x7a551e. Ported: world/entities/classes/triggers.js
(hurtAllTouchers, hurtThink, hurtPlayer, hurtBox, hurtEndTouch).

## What the damage does to a player

TakeDamageOld with that info goes the bullet's way (docs/game/shots.md 4): the pawn's damage services `180a93f70`.
In **180a88f30** (armor) the hit group is 0 (generic) unless the type has DMG_BULLET (2) and the info has a trace
(info +0x68 -> 180cacf80), so a map's damage is generic: armored when the pawn has armor and the type is 0 or has a
0xc6 bit (bullet, slash, blast, club), unless the info's +0x70 bit 18; ratio 0.5 (no weapon: 180a7ab50 finds none);
then TakeDamageOld's floor with the fraction carried in m_flDamageAccumulator (a trigger_hurt of 15, 7.5 a think,
costs 7 then 8). The hit group step (180a89430) runs only with a trace. CS2Fixes' TakeDamageOld detour
(detours.cpp:103-175) changes nothing here (block-all, the block-damage attacker fix for movers and point_hurt, the
molotov / grenade cases, prop damage scale); ZR's knockback needs DMG_BULLET or DMG_SLASH with a hitbox.
Ported: server/cs2web/core/game.js hurt -> combat.js hurtPlayer (no attacker, hit group 0, no weapon, the source's type).

**Blocked** (vfn 0x4d8): CFuncMoveLinear `180d8dd60` (m_flBlockDamage +0x908), CBaseDoor `180d3c470` (+0x924):
when the block damage is non-zero, a CTakeDamageInfo of DMG_CRUSH (1), the mover the inflictor, the attacker its
m_hActivator (+0x8a4) when that is a pawn (vfn 0x558) else the mover (CS2Fixes' cs2f_fix_block_dmg, off by default,
turns a pawn attacker back into the world), then TakeDamageOld on the blocker. CFuncRotating's is `180d8de90` (not read). Ported: game.js crushed movers' hurt with type 1.

**CPointHurt** (vtable 0x1819d53f8; inputs TurnOn 180ea9390, TurnOff 180ea9a00, Toggle 180ea9c00, Hurt 180ea9f20):
m_nDamage +0x4a8 (an int), m_bitsDamageType +0x4ac, m_flRadius +0x4b0, m_flDelay +0x4b4, m_strTarget +0x4b8,
m_pActivator +0x4c0. Hurt stores the activator's handle in m_pActivator and runs the hurt (180eccfc0): damage =
cvtdq2ps(m_nDamage); with a target, each entity the name finds (18137ab40, with the activator) through
TakeDamageOld with a guessed force; with none, RadiusDamage over m_flRadius at the abs origin (180fb9d90 ->
180df0300; not ported). Then the next think at now + m_flDelay. Ported: classes/beams.js point_hurt (the int).

## TakeHealth

CCSPlayerPawn vfn 0x3f0 `180d15bc0` (CBaseEntity's `180d15b30` is the same without the tail): m_takedamage (+0x2e0)
0 -> 0. max = vfn 0x5c8 (the max health); health (+0x2d0) < max: add = min(cvttss2si(amount), max - health), health
+= add (1803e4060 the change callback). A pawn at or above its max gains nothing (and is not lowered). The pawn's
tail: with a gamerules flag (+0x58) and health > 1, 1803ce320(pawn, 0x40000000). Ported: game.js heal (a
trigger_hurt of -5 heals 2 a think; -20 heals 10).

## Filters

`CBaseFilter` vtable 0x181938240; PassesFilterImpl is slot 0x770 (the base's `180bbf990` returns true).

- **CFilterMultiple** (0x1819389c8) `180bbfda0`: m_nFilterType +0x4e0, m_iFilterName[10], m_hFilter[10] +0x538.
  Each of the ten slots in order: a handle that finds no entity is skipped; the filter's PassesFilterImpl (vfn 0x770)
  with its own m_bNegated (+0x4a8) applied. AND (0): false at the first that fails, else true; OR (1): true at the
  first that passes, else false. Ported: triggers.js filterPasses (the handles resolved at each test: TODO, CS2
  resolves them when the filter activates).
- **CFilterProximity** (0x181939150) `180bc0070`: m_flRadius +0x4e0 (`filter_radius`). r <= 0 (comiss 0 >= r):
  true. No entity: false. Else d = the filter's abs origin - the entity's (1803d6f50 both), r x r > (dy x dy + dx x
  dx) + dz x dz, f32. Ported: triggers.js.
- **CFilterAttributeInt** (0x181940350) `180bbf9a0`: no entity: false. m_sAttributeName (+0x4e0, `filterattribute`):
  its CUtlStringToken (180154650: murmur2 of the string with seed len ^ 0x31415926; whether it folds case is unread)
  looked up in the entity identity's attribute table (+0x10 -> +0x48, made empty on first use) by 180b97870: a
  missing name is the default (0), type 1 an int at +8, type 2 a float cvttss2si'd; passes when > 0. Ported:
  triggers.js (the entity's `attrs`).

## CBaseEntity inputs

- **AddAttribute** `180cc6400` -> `180cfc5e0`: the parameter string (whole) is the attribute's name, its token as
  above; the identity's table (+0x48) made if missing; 1803ead90 sets it to int 1; then vfn 0x150.
  **RemoveAttribute** `180cc64e0` (not read past the dispatch). Ported: keyvalues.js playerInput (players only: no
  map entity on the baked maps is sent one).
- **CS2Fixes' SetSteamIdAttribute** (playermanager.cpp:573-592): with `cs2f_map_steamids_enable` (default 0;
  GFL's mapcfg/ze_dark_souls.cfg sets 1), an authenticated player who isn't a bot or HLTV gets
  AcceptInput("AddAttribute", "<SteamID64>") on the pawn and the controller, at authentication (playermanager.cpp:125)
  and in OnPlayerSpawn's 0 s CTimer (events.cpp:122-131). Ported: server/cs2web/modes/ze/gfl-mapcfg.js.
- **FollowEntity** `180cc5340` -> `180cfcc00`: the name found by FindEntityByName (180bfca30, with the activator and
  caller); no entity: a console message. Then `1803d6ab0`(this, target, true) -> `1803d6b40`(this, target, token):
  token 0x1c9748e6 (bone merge) when the target's model state has a model (+0x1c0), else 0. With a target: unless
  either entity has bit 9 of its identity flags, the target's +0x1be = 0x101 and the node's SetParent (180180300,
  no transform: the world transform kept, docs/game/scene-node.md), then the physics and effects refresh
  (180cee2e0, 180c27c70 / 180c27b20). With none (1803d6d3e): only a follower (move type NONE and its node's +0xec)
  is let go (180180300 with a null parent). Ported: engine.js (the bone-merge pose not followed; +0xec read as
  "made a follower by this input").

## CFuncMoveLinear TeleportToTarget

`180d77fc0` -> `180dadce0`: m_hActivator (+0x8a4) = the activator; the parameter's entity (FindEntityByName
180bfc940 with the activator and caller); none: done. Else Teleport (vfn 0x528) to its abs origin with no angles and
no velocity; m_flStartPosition (+0x90c) = 0; o = the local origin (1803d91a0); step = m_flMoveDistance (+0x854) x
m_vecMoveDirParentSpace (+0x8e0); m_vecPosition1 (+0x864) = o - step x 0; m_vecPosition2 (+0x870) = step + pos1;
m_vecFinalDest (+0x8a8) = o; all f32 (mulss / subss / addss in that order). Ported: classes/movers.js.

## Unread

- CTriggerHurt vfn 0x8b8 on the damage info (before TakeDamageOld) and 1803e55c0 in the start hook.
- GuessDamageForce (180fcd1d0) and what the force does to a pawn (nothing on health).
- CFuncRotating's Blocked (180d8de90).
- RemoveAttribute's body; CUtlStringToken's case rule (180154650).
- point_entity_finder FindEntity (`180ea77c0`): the method's search and OnFoundEntity's activator / caller.
