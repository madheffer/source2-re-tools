# Entity indices: how CS2 hands them out (server_20261105.dll, 2026-11-11)

Traced with Ghidra ReVa (the shared headless server) and tools/re. Asked for because the stuck check picks its command
by (the command's number + the pawn's entity index) & 63 (movement.md "CheckStuck", sim/src/movement/stuck.rs).

## The path

- **CreateEntityByName 180bef630** (CS2Fixes' gamedata signature `48 83 EC 48 C6 44 24 30 00`) =
  18137f420(the entity system 0x182331b00, -1, name, 0, param_2, -1, 0).
- **18137f420**: the class by designer name (181383a60; "Attempted to create unknown entity classname"), not spawnable
  (class +0x58 +0x10 bit 0) refused, else 18137f1a0.
- **18137f1a0** (class info at param_3): a class whose +0x70 has bit 3 takes its fixed handle from +0x100, else one
  from +0x60's +0x18 (181385670) if set; that handle forces the index (& 0x7fff) and the serial (>> 15). Then
  **networked** = the class has a network serializer (+0xe0 != 0) and isn't flagged server-only (+0x70 bit 0), with
  the entity system's +0xc44 clear or an index forced (param_5 0 / 1 / 2 refine it). Then 18137d5d0.
- **AllocateEntityIdentity 18137d5d0** (entitysystem.cpp:0x681): a forced index must be networked and < 0x4000 ("Bad
  entity index", "Bad entity serial number" over 0x1ffff); then the list's slot (18137cd30(es + 0x10, ...)); a forced
  slot in use: "Entity allocation failed since it forced slot %d, which is currently used by entity".
- **The slot, 18137cd30(list = es + 0x10, networked, index, serial, ...)**: the list holds 64 chunk pointers (+0 ..,
  networked chunks of 512 0x70-byte CEntityIdentity, indices 0..0x3fff) and 32 non-networked ones (+0x100.., indices
  0x4000 + ..). Free lists, each a doubly linked list through identity +0x50 (towards newer) / +0x58 (towards older):
  networked at list +0x238 (oldest) / +0x240 (newest) / +0x248 count, non-networked at +0x250 / +0x258 / +0x260.
  - Not forced: the networked list's **oldest** (+0x238) is taken; an empty list first gets a new chunk
    (18137d1c0). Non-networked likewise from +0x250.
  - Forced (an index): that identity is unlinked from wherever it sits in the free list.
  - The index is the identity's place in its chunk (+0x10's low 15 bits); the "in use" bitmap at list +0x274; the
    identity then joins the active list (+0x200 / +0x208 / +0x210 / +0x218).
- **A new chunk, 18137d1c0(list, networked)**: the first chunk pointer that's null below (+0x268 networked /
  +0x26c non-networked) / 512 (+ 32 for non-networked); 512 identities, each serial = RandomInt(0, 0x1ffff) (tier0's
  random stream) << 15, **appended at the newest end in index order**. "ConcreteEntityList: approaching limit"; out:
  "Ran out of %snetworkable entities!".
- **Release, 181385050(list, identity, bump serial)**: the in-use bit cleared, off the active list; a networked index
  `> list +0x270 + 1` goes back through 180be7130, **appended at the newest end** (the reserve and the one index past
  it never return); a non-networked one likewise to its list; the serial + 1 (& 0x1ffff) when asked.
- **The list's size, 181379f10** (CEntitySystem's constructor): gameinfo Engine2 MaxNetworkableEntities /
  MaxNonNetworkableEntities (default 0x4000 each, rounded up to 512) into list +0x268 / +0x26c; one networked and one
  non-networked chunk made at once; list +0x270 = 0.
- **PreservePlayerNetworkables 180c065e0** ("SV:  PreservePlayerNetworkables(%d)", from the server's level start, its
  count the message's +0x78: the player slots): list +0x270 = n and indices 0..n unlinked from the free list (fatal
  if any is in use), so the world (0) and the controllers (slot + 1, forced) never come off the queue.

## What that makes a pawn's index

Networked indices are a FIFO: after the reserve (0..maxplayers) every networked entity takes the oldest free index, a
freed index queues behind every index still free (the chunk's never-used ones first), and a new chunk opens only when
the queue is empty (so the freed ones are reused before indices past 511 appear). So a pawn's index is the queue's head when CCSPlayerController made it: maxplayers + 1 + every networked
entity created before it on this map (the map's networked entities in their spawn order, the server's own: gamerules
proxy, team managers, ..., weapons, projectiles, effects), wrapped through the freed ones once the first 512 run out.

The port doesn't reproduce that: its entities have their own ids, it doesn't know which classes CS2 networks (class
+0xe0 / +0x70 are filled at runtime), and it doesn't create the server's own entities. The player's id stands in for
the index (src/cs2web/sim/move-sim.js word 139); it only decides which of each 64 commands runs the stuck check.

## Captured on a real server (2026-11-11, tools/capture)

A local CS2 dedicated server (the Steam install's cs2.exe, `-dedicated -insecure -usercon -maxplayers 64 -ip 127.0.0.1
+sv_lan 1 +rcon_password ...`, casual), driven over RCON by `tools/capture/entities.mjs`: `ent_find <c>` (a cheat
command: `sv_cheats 1`; it prints `'class' : 'name' (entindex N)`, server.dll 1803f2260) once per letter and digit,
merged by index. CS2's RCON answers a frame after the command (tools/capture/rcon.mjs waits for the packets to stop);
`-condebug` floods console.log with "CTextConsoleWin::GetLine" lines when the server has no console window, so it's
left off. An empty server hibernates (`sv_hibernate_when_empty 0`); bots need `bot_join_after_player 0` and a nav
mesh, which the ZE maps don't ship (no bot joins on ze_atix_panic_2017_p; de_dust2 used for the players).

What it showed:
- **ze_atix_panic_2017_p at load**: 0 worldent; 1..64 free (the reserve, 64 slots); 65..68 cs_team_manager x 4, 69
  cs_player_manager, 70 cs_gamerules, 71..73 vote_controller x 3 (the server's own, before the map's); the map's
  networked entities from 74. 424-426 networked, ~126 not (16385 and up).
- **Networked classes seen** (index < 0x4000): cs_gamerules cs_minimap_boundary cs_player_manager cs_team_manager
  env_cubemap_fog env_particle_glow env_shake env_sky env_soundscape env_soundscape_triggerable env_spark env_wind
  func_breakable func_brush func_button func_buyzone func_door func_rotating func_tracktrain func_water
  info_particle_system info_target info_teleport_destination light_barn light_omni2 logic_auto path_track
  point_servercommand point_soundevent post_processing_volume prop_door_rotating prop_dynamic prop_physics_override
  sky_camera skybox_reference trigger_hurt trigger_multiple trigger_once trigger_push trigger_soundscape
  trigger_teleport vote_controller worldent; and on de_dust2 cs_player_controller, player (CCSPlayerPawn), observer
  (CCSObserverPawn), weapon_*, prop_physics_multiplayer. **Not networked**: env_fade filter_* info_player_*
  logic_branch logic_case logic_compare logic_relay logic_timer math_counter point_nav_walkable point_teleport
  point_template.
- **The map's order isn't the lump order**: atix's light lump (236#entityLumpName) comes first, its 8 lights in the
  order 0, 2, 6, 4, 1, 3, 5, 7; 41 of 416 networked map entities fall out of the bake's lump order and 18
  prop_dynamics don't match a lump entity by class and name (names match once Hammer's "[PR#]" prefab prefix is
  dropped: CS2 strips it). The spawn group's creation order is untraced.
- **Players (de_dust2, 12 bots)**: controllers at 1..12 (slot + 1); each bot a `player` and an `observer` pawn, two
  consecutive indices (288 / 289, 290 / 291, ...), weapons in between; after `mp_restartgame` the pawns keep their
  indices and the weapons are new.
- **The queue lives across map changes**: after atix, de_dust2's own server entities came out at 491..499 (the FIFO
  went on from where atix left it). So a live server's pawn index depends on everything it created since it booted,
  on every map it ran: no game state the port has (or a client could see) fixes it. The stand-in stays; a model of the
  allocator would only be right for a server that started on this map with nothing before it.

Also a stand-in for the same reason: CS2Fixes' game_ui keys its static s_repository by the logic_case's handle
(index | serial << 15), whose walk order decides which of two game_uis thinks first (server/cs2web/cs2fixes/entities/gameui.js: 0x4000 +
the port's entity id, the round's number as serial; the map itself is libstdc++'s, src/lib/std-unordered-map.js).

Unread: when a pawn is created and (CCSPlayerController's pawn creation; a round restart keeps it: captured), which of
the server's own entities exist and their order against the map's spawn group, 181385670 (a class's handle from its
+0x60), the +0xc44 flag, param_5's callers.
