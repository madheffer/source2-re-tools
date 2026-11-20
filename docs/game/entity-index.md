# Entity indices: how CS2 hands them out

server_20261105; captured on a local dedicated server 2026-11-11. Needed by the stuck check: its command is picked by (the command's number + the pawn's entity index) & 63 ([movement.md](movement.md) "CheckStuck").

## Functions

| Address | Module | What |
|---|---|---|
| 180bef630 | server | CreateEntityByName (CS2Fixes' signature `48 83 EC 48 C6 44 24 30 00`) = 18137f420(entity system 0x182331b00, -1, name, 0, param_2, -1, 0) |
| 18137f420 | server | class by designer name (181383a60; "Attempted to create unknown entity classname"); not spawnable (class +0x58 +0x10 bit 0) refused; else 18137f1a0 |
| 181383a60 | server | class by designer name |
| 18137f1a0 | server | (class info at param_3): forced handle, networked test, then 18137d5d0 |
| 181385670 | server | a class's handle from its +0x60 (+0x18) (unread) |
| 18137d5d0 | server | AllocateEntityIdentity (entitysystem.cpp:0x681) |
| 18137cd30 | server | the slot (list = es + 0x10, networked, index, serial, ...) |
| 18137d1c0 | server | a new chunk (list, networked) |
| 181385050 | server | release (list, identity, bump serial) |
| 180be7130 | server | networked index back to the free list |
| 181379f10 | server | CEntitySystem's constructor: the list's size |
| 180c065e0 | server | PreservePlayerNetworkables ("SV:  PreservePlayerNetworkables(%d)", from the level start; count = the message's +0x78: the player slots) |
| 1803f2260 | server | `ent_find` (prints `'class' : 'name' (entindex N)`; cheat) |

## Fields

| Offset | Field |
|---|---|
| class +0x58 +0x10 bit 0 | not spawnable |
| class +0x70 bit 3 | fixed handle at +0x100 |
| class +0x70 bit 0 | server-only |
| class +0x60 (+0x18) | handle source (181385670) |
| class +0xe0 | network serializer (!= 0: networked) |
| entity system +0xc44 | flag: networked only with it clear or an index forced |
| es +0x10 | the entity list |
| list +0 .. | 64 networked chunk pointers (512 0x70-byte CEntityIdentity each, indices 0..0x3fff) |
| list +0x100 .. | 32 non-networked chunk pointers (indices 0x4000 + ..) |
| identity +0x50 / +0x58 | free-list links towards newer / older |
| identity +0x10 | low 15 bits: the index |
| list +0x200 / +0x208 / +0x210 / +0x218 | active list |
| list +0x238 / +0x240 / +0x248 | networked free list: oldest / newest / count |
| list +0x250 / +0x258 / +0x260 | non-networked free list: oldest / newest / count |
| list +0x268 / +0x26c | MaxNetworkableEntities / MaxNonNetworkableEntities |
| list +0x270 | reserved networked count (PreservePlayerNetworkables) |
| list +0x274 | "in use" bitmap |

## Constants

| Value | What |
|---|---|
| handle & 0x7fff / >> 15 | index / serial |
| 0x4000 | networked index limit ("Bad entity index") |
| 0x1ffff | serial limit ("Bad entity serial number"); serial = RandomInt(0, 0x1ffff) << 15 (tier0's random stream) |
| 512 | identities a chunk |
| 0x4000 each | gameinfo Engine2 MaxNetworkableEntities / MaxNonNetworkableEntities default (rounded up to 512) |

## The path

1. 18137f1a0: a class with +0x70 bit 3 takes its fixed handle from +0x100, else one from +0x60's +0x18 (181385670) if set; that handle forces the index and serial. Networked = +0xe0 != 0 and not +0x70 bit 0, with es +0xc44 clear or an index forced (param_5 0 / 1 / 2 refine it).
2. 18137d5d0: a forced index must be networked and < 0x4000; then 18137cd30; a forced slot in use: "Entity allocation failed since it forced slot %d, which is currently used by entity".
3. 18137cd30: not forced: the networked free list's oldest (+0x238) is taken (an empty list first gets 18137d1c0); non-networked likewise from +0x250. Forced: that identity is unlinked from wherever it sits in the free list. The in-use bit set; the identity joins the active list.
4. 18137d1c0: the first null chunk pointer below (+0x268 / +0x26c) / 512 (+ 32 for non-networked); 512 identities, each a random serial, appended at the newest end in index order. "ConcreteEntityList: approaching limit"; out: "Ran out of %snetworkable entities!".
5. 181385050: the in-use bit cleared, off the active list; a networked index `> list +0x270 + 1` goes back through 180be7130, appended at the newest end (the reserve and the one index past it never return); a non-networked one likewise; serial + 1 (& 0x1ffff) when asked.
6. 181379f10: sizes into +0x268 / +0x26c; one networked and one non-networked chunk made at once; +0x270 = 0.
7. 180c065e0: +0x270 = n and indices 0..n unlinked from the free list (fatal if any is in use): the world (0) and the controllers (slot + 1, forced) never come off the queue.

## A pawn's index

Networked indices are a FIFO: after the reserve (0..maxplayers) every networked entity takes the oldest free index, a freed index queues behind every index still free (a chunk's never-used ones first), and a new chunk opens only when the queue is empty (so freed ones are reused before indices past 511 appear). A pawn's index = maxplayers + 1 + every networked entity created before it since the server booted (the map's networked entities in spawn order, the server's own: gamerules proxy, team managers, ..., weapons, projectiles, effects), wrapped through the freed ones once the first 512 run out. It depends on every map the server ran: no game state fixes it.

CS2Fixes' game_ui keys its static s_repository by the logic_case's handle (index | serial << 15): its walk order (libstdc++'s unordered_map) decides which of two game_uis thinks first, so it depends on the same.

## Captured (local dedicated server)

`cs2.exe -dedicated -insecure -usercon -maxplayers 64 -ip 127.0.0.1 +sv_lan 1 +rcon_password ...`, casual; `ent_find <c>` (needs `sv_cheats 1`) once per letter and digit over RCON, merged by index. RCON answers a frame after the command. `-condebug` floods console.log with "CTextConsoleWin::GetLine" without a console window. An empty server hibernates (`sv_hibernate_when_empty 0`); bots need `bot_join_after_player 0` and a nav mesh (the ZE maps ship none; de_dust2 for players).

- ze_atix_panic_2017_p at load: 0 worldent; 1..64 free (the reserve); 65..68 cs_team_manager x 4, 69 cs_player_manager, 70 cs_gamerules, 71..73 vote_controller x 3 (the server's own, before the map's); the map's networked entities from 74. 424-426 networked, ~126 not (16385 and up).
- Networked (index < 0x4000): cs_gamerules cs_minimap_boundary cs_player_manager cs_team_manager env_cubemap_fog env_particle_glow env_shake env_sky env_soundscape env_soundscape_triggerable env_spark env_wind func_breakable func_brush func_button func_buyzone func_door func_rotating func_tracktrain func_water info_particle_system info_target info_teleport_destination light_barn light_omni2 logic_auto path_track point_servercommand point_soundevent post_processing_volume prop_door_rotating prop_dynamic prop_physics_override sky_camera skybox_reference trigger_hurt trigger_multiple trigger_once trigger_push trigger_soundscape trigger_teleport vote_controller worldent; on de_dust2 cs_player_controller, player (CCSPlayerPawn), observer (CCSObserverPawn), weapon_*, prop_physics_multiplayer.
- Not networked: env_fade filter_* info_player_* logic_branch logic_case logic_compare logic_relay logic_timer math_counter point_nav_walkable point_teleport point_template.
- The map's order isn't the lump order: atix's light lump (236#entityLumpName) first, its 8 lights in the order 0, 2, 6, 4, 1, 3, 5, 7; 41 of 416 networked map entities out of lump order; 18 prop_dynamics match a lump entity by name only once Hammer's "[PR#]" prefab prefix is dropped (CS2 strips it).
- de_dust2, 12 bots: controllers at 1..12 (slot + 1); each bot a `player` and an `observer` pawn on two consecutive indices (288 / 289, 290 / 291, ...), weapons in between; after `mp_restartgame` the pawns keep their indices and the weapons are new.
- The queue lives across map changes: after atix, de_dust2's own server entities came out at 491..499.

## Unread

- When a pawn is created (CCSPlayerController's pawn creation; a round restart keeps it: captured).
- Which of the server's own entities exist and their order against the map's spawn group; the spawn group's creation order.
- 181385670, the +0xc44 flag, param_5's callers.
