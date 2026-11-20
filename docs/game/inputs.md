# The input dispatch and the classes' input tables

server_20261105. CS2Fixes src/detours.cpp:408-512 (commit 72ec6b9), zombiereborn.cpp:1483.

## Functions

| Address | Module | What |
|---|---|---|
| 1813a8ed0 | server | CEntityIdentity::AcceptInput (identity, input name, activator, caller, value): pools the name, copies the value into a variant, then 1813ac4d0 with identity +0x10 |
| 18137d560 | server | pool a string (on the entity system's pool, DAT_182331b00 + 0x1f50) |
| 180535520 | server | the string pool: MurmurHash2, seed 0x31415926, over the ASCII-lower-cased text |
| 18054ba10 | server | CBufferString::ToLowerFast, then the hash |
| 180524c70 | server | bucket compare: `_V_strnicmp_fast` and the length |
| 1813ac4d0 | server | dispatch (rcx = { +0 entity, +8 its CEntityClass }) |
| 181373b60 | server | class lookup (class, entity, &name, activator, caller, value, output id): class+0x28 vfn 1 (+0x08); true -> 2; else the base class, recursively; 0 when none |
| 180cdfd30 | server | CBaseEntity vfn 0x88: the component at +0x4a0, 180f10640 (Pulse graph lookup and run) |
| 180f10640 | server | Pulse graph input |
| 181373eb0 | server | build a class's sorted input table |
| 181385ea0 | server | entity system init: 181373eb0 per class from its class dictionary (+0xa98) |
| 181373c30 | server | pool and append { pooled name, entry } (linear duplicate check) |
| 181373630 | server | introsort by pooled pointer |
| 180c40120 | server | CLogicRelay_API::CancelPending (io-queue.md's CancelPending) |
| 180cc4dd0 -> 180cfce50 | server | CBaseEntity_API::Kill -> InputKill |
| 180cc4e40 | server | CBaseEntity_API::KillHierarchy (scene-node.md) |
| 1803a9110 -> 1813aa560 | server | CBaseEntity_SharedAPI::AddOutput -> the AddOutput parser (io-targets.md) |
| 180cd8650 | server | fills CBaseEntity's datamap at run time |
| 181380400 | server | keyvalue unserializer ("IsFieldDescUsedByKeysOrIO") |
| 180600170 | server | CBaseEntity's VScript descriptor (ScriptInputKill etc.) |
| 1806a94c0 | server | logic_relay's VScript descriptor (ScriptTrigger) |
| 18020a7d0 | server | Lua bindings |
| 1800853f0 | server | logic_relay's entity class constructor |
| 18138abb0 | server | CEntitySystem::RegisterEntityClass |
| 181375dd0 | server | pooled class name, inherited flags |
| 1800d83f0 | server | info_particle_system's constructor (stores CParticleSystem from rbp on a branch, 1800d85a8) |
| 180e11760 | server | CLogicCase_API::InValue |
| 180e12060 / 180e123d0 / 180e12770 | server | CLogicCase PickRandom / PickRandomShuffle / ResetShuffle |
| 181389200 | server | intern a string (empty -> null, compared as "") |
| 1802a66e0 | server | fire an output (activator, caller) |
| 180e3e980 | server | fire OnDefault with a string value |

## Fields

| Offset | Field |
|---|---|
| entity +0x4a0 | Pulse component |
| entity system +0xc20 / +0xc18 | input listeners / count |
| entity system +0xa98 | class dictionary |
| DAT_182331a08 | entity class list (linked by +0x108) |
| class +0x28 | input object (set at run time); `[class+0x28]+0xe0` count, `+0xe8` 0x20-byte entries (name at +0) |
| class +0xe8 / +0xf0 | the sorted pooled table |
| class +0x00 | VScript descriptor |
| class +0x58 / +0x60 | class info / the base's class info (`+0x18` its CEntityClass) |
| class +0x68 / +0x70 | pooled class name / flags inherited from the bases |
| class info +0x00 / +0x08 | designer name / class name |
| class info +0x18 / +0x20 | its entity class / the base's class info |
| class info +0x28 / +0x30 | schema binding / datamap |
| SchemaClassInfoData +0x08 | name |
| +0x20 | size (u32) and field count |
| +0x28 | fields (0x20 each: name, type, offset, ...) |
| +0x38 | base list ({ u32 offset, binding* }) |
| +0x40 | datamap |
| typedescription (0x38) +0 / +8 / +0x10 / +0x18 / +0x20 | type / field name / offset / flags / key name |
| CLogicCase +0x4a8 | 32 case strings (8 bytes each) |
| CLogicCase +0x5d0 + 0x18 x i | OnCase outputs |
| CLogicCase +0x8d0 | OnDefault |

Statics: logic_relay's class 0x1820db7e0, class info 0x1820db798, schema binding 0x181dee5f0, datamap 0x181e20180; CBaseEntity's binding 0x181de0270, datamap 0x181e25d40 (34 entries); CPointEntity's datamap 0x181daae88; func_button's designer / class name stored at 1806198fd into 0x18208f300 / 0x18208f308.

## Entity-API binding records

A class's inputs are its "<Class>_API::<Input>" bindings (the records Pulse and cs_script call): 0x50 bytes in .data, one class's in a row. (Which class holds which records is inferred from this grouping, not read from the input object at class+0x28.)

| Offset | What |
|---|---|
| +0x00 | "CLogicRelay_API::Trigger": the input name is the text after `::` |
| +0x08 | display name ("Trigger", "Kill Hierarchy") |
| +0x10 | description |
| +0x18, +0x20 | parameter / return type getters |
| +0x28, +0x30 | metadata count, metadata (e.g. MPulseFunctionHiddenInTool) |
| +0x38 | flags (0x10100; 0x200010100, bit 33, on hidden-in-tool ones) |
| +0x48 | handler |

- CBaseEntity's table also holds the other two `_SharedAPI` records (SetScale, IsMotionEnabled). Getters (GetName, GetAbsOrigin, ...) are in the tables too; as inputs they do nothing a map sees.
- Not inputs: the datamaps (class info +0x30: keyfields only), the VScript descriptors and the Lua bindings (script APIs). MurmurHash tokens of input names don't appear in code: pooled pointers are compared.

## Dispatch (1813ac4d0)

1. 181373b60: the class chain's input objects.
2. Not found: entity vfn 0x88 (Pulse graph; the ZE maps read have none).
3. Not found: the script path after 1813ac5db (a script's `Input<name>`, io-targets.md; calls through the VM's vtable +0x120 / +0x108 / +0xa8 / +0xb8 not followed; the ZE maps read have no scripts).
4. Handled: the entity system's input listeners. Not handled: "unhandled input" logs.

Names match case-insensitively by pooled pointer: `trigger` = `Trigger` = `TRIGGER`.

## Class chains and designer names

- Chains (the bindings' first base): logic_relay = CLogicRelay > CLogicalEntity > CServerOnlyEntity > CBaseEntity > CEntityInstance; prop_dynamic = CDynamicProp > CBreakableProp > CBaseProp > CBaseAnimGraph > CBaseModelEntity > CBaseEntity > CEntityInstance.
- The constructor stores designer and class name into the class info's +0 / +8 (`lea r, [name]; mov qword ptr [rip + X], r`). 493 pairs; info_particle_system's (CParticleSystem) on a branch.

## Inputs CS2's classes don't have (sent by ZE maps; do nothing in CS2)

- Enable / Disable / Toggle / Lock / Unlock / CancelPending are not generic. ze_dark_souls: point_template Enable / Disable, func_physbox Enable, CancelPending to math_counter / logic_case / logic_branch / trigger_hurt / prop_dynamic / point_template, Unlock to filters and a point_worldtext, Start / Stop to info_targets, SetDamage to trigger_multiples sharing a trigger_hurt's name.
- RE3: SetUnbreakable to a rotating door, PickRandom and StopSound to a relay / case, Enable/DisableCameraAll to relays not tagged as CS2Fixes viewcontrols. hold_em: Open to a trigger_once sharing a door's name.
- No CS2 class: game_ui, point_viewcontrol, game_round_end, player_speedmod, player_weaponstrip, point_tesla. CS2Fixes' two are a logic_case / logic_relay underneath, whose other inputs CS2 takes.

## CS2Fixes' AcceptInput detour (before CS2's)

info_map_parameters FireWinCondition (ZR); any input starting "KeyValue" (CustomIO_HandleInput, any entity); IgniteL* and AddScore on a pawn; SetMessage on an env_hudhint; SetModel on a model entity (AsBaseModelEntity); Activate / Deactivate on a logic_case tagged vscripts "game_ui"; EnableCamera / DisableCamera / EnableCameraAll / DisableCameraAll on a logic_relay tagged "point_viewcontrol".

## CLogicCase InValue (180e11760)

1. The parameter is a string (181389200).
2. Each non-null case string compared with `V_stricmp_fast`; the first equal fires its output (1802a66e0 with the input's activator and the entity).
3. No match: OnDefault (180e3e980) with the string as its value.

No number parse: "0.0" is not "0". CS2 maps write counter-fed cases as "0.0", "1.0" (ze_dark_souls: all 50 logic_cases; its ending's overrides "0.0" / "1.0" match its cases "0.0" / "1.0").

## Unread

- The input object at class+0x28: its type and where it is set; its vfn 1's steps (the variant's conversion to the handler's parameter types, +0x18's getter).
- Each class's handlers, family by family.
- How the dispatch turns a float output's value into InValue's string (math_counter OnGetValue -> InValue).
