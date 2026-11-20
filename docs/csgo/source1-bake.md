# The Source 1 BSP bake (`lasers-bake --source1`)

A CS:GO map (VBSP 21, first ze_crazykart_v4) written as the files a CS2 map bake has, so it runs on CS2's rules. Truth
sources: the CS2 maps' own physics.bin / world attributes (ze_resident_evil_3, ze_atix_panic_2017_p, de_dust2),
source2-compiler's ported builders (RnHullBuilder, RnMeshBuilder, QuickHull, MeshWeld; its MaterialCollision table,
physicsbuilder 180ba72b0), CS2's pak01 scripts/surfaceproperties.vsurf.

## Constants

| Value | What |
|---|---|
| part flags 2, mass 0 | CS2 world_physics: one part of hulls + meshes |
| part flags 0, mass 0, attribute `default` | CS2 brush entity model (a trigger's too: the class decides what touches it) |
| angle 5, min thickness 1 | the map builder's hull options (FUN_18131efc0); then the compile's ShapePoints check (quickhull at tolerance 0); no RegionSvm on world hulls |
| 1/32 | displacement mesh weld |
| 1977497166 | CS2 surface hash `default` (no CS2 surface of that name) |
| 0x80000 / 0x100000 | CS:GO grenade / drone clip contents (taken as; CS:GO's bspflags not read) |
| TEXCOORD_1 | CS2 world glb's lightmap channel |
| RGBM, range 8 | irradiance |
| snd_refdb 60, refdist 36, gain_min 0.01 | Source's calc_falloff for a soundlevel |

## Source 1 -> CS2

| Source 1 | CS2 |
|---|---|
| World brushes (model 0) | physics.bin model `world`, one part (flags 2), an RnHull per brush from its corner points (sides clipped by each other); RnHullBuilder with the map builder's options, then RnHullCreate |
| A brush the map builder refuses | RnHullCreate on the points (a box: RnHullCreateBox), else a closed RnMesh of its faces. Thin slabs far wider than thick (1-unit kart floors 3000 units across) are flat to the builder's scaled quickhull (its extrusion is MinThickness / 2^k). ze_crazykart_v4: 84 brushes, 29 as meshes, none dropped |
| Brush contents | collision attributes as a CS2 world_physics carries them: SOLID / MOVEABLE -> `Default`, no tags (`default` in an entity model); every side sky or a non-drawing tool -> `["sky"]` conditionallysolid; WINDOW -> `["window"]` (vbsp makes a translucent solid WINDOW; CS2 tags a translucent drawn material window); GRATE -> `["passbullets"]`; LADDER / MONSTERCLIP / PLAYERCLIP -> `ladder`, `npcclip`, `playerclip` (alphabetical, as CS2's toolsclip / toolsplayerclip / ladder sets); WATER `["water"]`; SLIME `["slime"]`; BLOCKLOS `["blocklos"]`; grenade / drone clip -> `csgo_grenadeclip` / `csgo_droneclip`. Group names compare case-insensitively |
| Displacements | one RnMesh in `world` (weld 1/32, BVH); a triangle's material indexes the aggregate's surface list (CS2 worlds keep terrain as meshes: 2-14 beside the hulls) |
| Static props (sprp) solid 6 / 2 | hulls in `world` (CS2 compiles static props into world_physics): each .phy convex piece placed; SOLID_BBOX (or no .phy) the studiohdr hull_min / max box; surface the .phy text's "surfaceprop" |
| Brush entity `*N` | `maps/<map>/entities/brush_<n>.vmdl`; one part, a hull per brush in model space (vbsp compiles a brush entity about its origin). A brush with no collision contents still bounds a trigger / illusionary entity (`default`) |
| Studio model `models/x.mdl` | `models/x.vmdl` (CS2 names every model .vmdl); the .phy's first solid's pieces as hulls, mass from its text (`mass`), attribute `Default` |
| $surfaceprop | CS2 surface hash by name; a brush's surface is the material most of its sides use |
| Faces | world glb (TEXCOORD_0 texture, TEXCOORD_1 lightmap atlas UV) |
| HDR lightmaps (LUMP_LIGHTING_HDR, style 0) | RGBM irradiance (range 8, uvScale 1). CS2's shading is albedo x irradiance, Source's LightmappedGeneric albedo x lightmap: the same product. No directional / shadow maps (Source 1 has none). Static props: per-vertex ambient-cube light (COLOR_0). Entity models: the sky ambient (no light probes: a stand-in) |
| light_environment | CS2 keys: `color` / `brightness` (= `_light` rgb, brightness / 255), `skycolor` / `skyintensity` (`_ambient`), pitch from `pitch`, `directlight 1` (vrad bakes the sun into the lightmap) |
| Entity lump | outputs (ESC-separated) as I/O; point_template's Template01-16 members moved into lump `tpl_<n>` (the template's `entitylumpname`), placed relative to the template, `&0000` on names and I/O targets / params unless spawnflags 2, removed from the world unless spawnflags 1; each member keeps its BSP place as `csgo_origin` / `csgo_angles` (CS:GO's CPointTemplate placement in floats: ../crazykart/ivp-physbox.md 8); a lone `angle` as `angles` |
| Sounds | `csgo_mega` events, `curve` = Source's falloff for the soundlevel, `soundlevel` and `music` kept |
| .pcf, env_sprite textures, skyname | fx, sprites (no CS2 class for env_sprite), sky faces rt/bk/lf/ft/up/dn (stand-in: not drawn as an env_sky) |

Not baked: the 3D skybox's scaled view, cubemap reflections, vis, radar, color correction.

## ze_crazykart_v4

- 332 brush models, 5368 brushes, 56 displacements, 171 static props (143 solid). physics.bin 3.2 MB: world 3631
  brush hulls + 7168 displacement triangles + 713 static prop hulls, 331 brush models, 6 studio models; world glb 35 MB.
- Spawns at z -15864 (players stand at -15872).
- Classes with no CS2 handler: light (910), point_worldtext (69), func_illusionary (28), info_teleport_destination
  (16), env_sprite (14), env_steam (11), env_spritetrail (8), skybox_swapper (6), logic_eventlistener (6),
  func_precipitation (3), point_viewcontrol_multiplayer (2), point_broadcastclientcommand, func_buyzone,
  info_game_event_proxy, game_weapon_manager, game_score, env_tonemap_controller, filter_damage_type, sky_camera,
  info_player_start, light_environment, game_ui (CS:GO's class), worldspawn.
- 13 VScripts (luffaren/...: kartcontroller, the shells, star, artillery, bossbreak, manager, filter, zestagewinner);
  527 RunScriptCode / CallScriptFunction connections.

## Unread

- What CS2's map builder does with a mesh piece in place of a refused brush.
- CS:GO's bspflags (the grenade / drone clip contents values).
