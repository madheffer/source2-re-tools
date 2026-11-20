# The Source 1 BSP bake (`lasers-bake --source1`)

A CS:GO map (VBSP 21) baked by hand into the CS2 map folder our runtime plays, so it runs on CS2's rules unchanged
and its mechanics are ported by hand on top (first map: ze_crazykart_v4). No resourcecompiler / s2port route: the
bake writes the files the CS2 bake writes, cooked with the CS2 builders source2-compiler ported. No `"engine"` switch
anywhere: the runtime has only CS2's rules.

```bash
dotnet build bake -c Release
./bake/bin/Release/net10.0/lasers-bake.exe --source1 <map.bsp> <scratch maps dir> [--csgo "<csgo legacy>/csgo"] [--cs2 <game/csgo>]
# then copy <scratch>/<map> into web/public/maps and: node tools/bake-map.mjs --steps index (= node tools/index-maps.mjs)
```

`S1_HULL_DEBUG=1` logs every brush neither hull path nor the mesh fallback takes.

Code: bake/Source1/ (restored from 1d50005^, the trainer's Source 1 bake, then adapted): Source1Bake.cs (the run),
Source1Physics.cs (physics.bin), Source1Derived.cs (collision.bin, collision_fx*, hulls.json from the same shapes),
Entities.cs, FaceMesh.cs, PropBake.cs, Source1Sounds.cs, Source1Particles.cs, SpriteBake.cs; bake/Source1/Rn/
source2-compiler's hull and mesh builders (copied at e4e906b: QuickHull, HullSimplifier, RegionSvm, RnHullBuilder,
RnMeshBuilder, MeshWeld, MeshGjk, LightCrt, VectorNormalizeSlow, both CrtMath ports, and Gjk.Tetrahedron with its
Vec3). They define RnHull / RnMesh / RegionSvm, so the bake compiles them instead of rubikon's builder-less copies
(rubikon/src/Physics/RnShapes.cs, RnHullBuilder.cs); PhysFile.cs and Tier0Strings.cs still come from rubikon/.

## What each Source 1 thing becomes

| Source 1 | CS2 map folder | Why / truth |
|---|---|---|
| World brushes (model 0) | `physics.bin` model `world`, one part (flags 2), one RnHull per brush | CS2's world_physics is one part of hulls + meshes (every CS2 map in web/public/maps: part flags 2, mass 0). Each brush's corner points (its sides clipped by each other, BrushGeometry.Solid) go through BrushHulls.Build's pipeline: RnHullBuilder.BuildHull with `Options.MapBuilder` (angle 5, min thickness 1: FUN_18131efc0's), the compile's ShapePoints check (quickhull at tolerance 0), RnHullBuilder.Create with `Options.Compile`, Transform(identity). No RegionSvm: none of the CS2 bakes' world hulls carry one |
| A brush the map builder refuses | RnHullCreate on the points (a box's corners: RnHullCreateBox), else a closed RnMesh of its faces | Thin slabs far wider than thick (1-unit kart floors 3000 units across) are flat to the builder's scaled quickhull (its extrusion is MinThickness / 2^k, too small at that scale). ze_crazykart_v4: 84 brushes take the fallbacks, 29 as meshes, none dropped. TODO: what CS2's map builder does with such a mesh piece is not traced |
| Brush contents | the hull's collision attribute (strings as a CS2 world_physics carries them) | Read off the CS2 maps' own world attribute sets (ze_resident_evil_3, ze_atix_panic_2017_p, de_dust2) and source2-compiler's MaterialCollision table (physicsbuilder 180ba72b0): SOLID / MOVEABLE -> `Default` with no tags (world; `default` in an entity model); a brush whose every side is sky or a non-drawing tool -> `["sky"]` conditionallysolid; WINDOW -> `["window"]` (vbsp makes a translucent solid WINDOW; CS2 tags a translucent drawn material window); GRATE -> `["passbullets"]`; LADDER / MONSTERCLIP / PLAYERCLIP -> `ladder`, `npcclip`, `playerclip` (alphabetical, as CS2's toolsclip / toolsplayerclip / ladder sets are); WATER -> `["water"]`; SLIME -> `["slime"]`; BLOCKLOS -> `["blocklos"]`; the CS:GO grenade / drone clip contents (0x80000 / 0x100000, TODO(trace): CS:GO's bspflags not read) -> `csgo_grenadeclip` / `csgo_droneclip`. Group names compare case-insensitively (Tier0Strings.EqualsAscii), the runtime's bits come from CollisionRules |
| Displacements | one RnMesh in `world` (RnMeshBuilder.Create: weld 1/32, BVH), per-triangle material = the face material's surface index | CS2 worlds keep terrain as meshes (the CS2 bakes: 2-14 meshes beside the hulls); a mesh triangle's material indexes the aggregate's surface list (RubikonBake / Program.AppendTriangles) |
| Static props (sprp lump) solid 6 / 2 | hulls in `world`: each .phy convex piece placed (RnHullCreate per piece); SOLID_BBOX (or no .phy) the model's hull box (studiohdr hull_min / max) placed | CS2 compiles static props into world_physics. Surface: the .phy text section's "surfaceprop" |
| Brush entity model `*N` | `maps/<map>/entities/brush_<n>.vmdl` (entity `model`, physics.bin key, hulls.json key, models/...glb); one part (flags 0, mass 0), a hull per brush, model space | CS2 brush entity models in physics.bin: one part, flags 0, mass 0, attributes `default` (a trigger's too: the class decides what touches it). vbsp compiles a brush entity about its origin, so its brushes are already local. A brush with no collision contents still bounds a trigger / illusionary entity (`default`) |
| Entity studio model `models/x.mdl` | `models/x.vmdl` everywhere (entity key, physics.bin, hulls.json, models/models/x.glb, animations.json) | CS2 names every model .vmdl; the runtime maps `.vmdl` -> `.glb`. Physics: the .phy's first solid's pieces as hulls, mass from its text section (`mass`), attribute `Default` |
| $surfaceprop | CS2 surface hash by name (scripts/surfaceproperties.vsurf of CS2's pak01, SurfaceBake.Load), `default` (1977497166) when CS2 has no such name | The brush's surface: the material most of its sides use. physics.bin's surfaces: RubikonBake.Surfaces over the used hashes |
| Faces | world/<map>.glb (TEXCOORD_0 texture, TEXCOORD_1 lightmap atlas UV), brush entity glbs | The CS2 world glb's lightmap channel is TEXCOORD_1 (world/lighting.js `irr.channel = 1`); no occlusion slot (the old Source 1 renderer path is gone) |
| HDR lightmaps (LUMP_LIGHTING_HDR, style 0) | `lighting/lighting.json` + `lighting/irradiance.png` (RGBM, range 8, uvScale 1) | world/lightmaps.js takes an RGBM PNG irradiance at the high tier too; CS2's shading is albedo x irradiance (lighting.js multiplies by pi for three's Lambert, as for CS2 bakes), Source's LightmappedGeneric is albedo x lightmap: the same product. No directional / shadow maps (Source 1 has none): the CS2_DIRECTIONAL path is off. Static props: per-vertex ambient-cube light (COLOR_0) and the atlas's white luxel as their lightmap UV. Stand-in: entity models get the sky ambient (no light probes) |
| light_environment | CS2 keys added beside the Source ones: `color` / `brightness` (= `_light` rgb, brightness / 255), `skycolor` / `skyintensity` (`_ambient`), angles' pitch from `pitch`, `directlight 1` | lighting.js reads CS2's keys; vrad bakes the sun into the lightmap, so the runtime sun stays off (directlight 1 with no bakedshadowindex) |
| Entity lump | `entities.json` `{ lumps: { default_ents, tpl_<n> } }`, `{ kv, io }`, keys lower case | Entities.cs: outputs (ESC-separated) as io; point_template's Template01-16 members moved into `tpl_<n>` (the template's `entitylumpname`), placed relative to the template, `&0000` on names and I/O targets / params unless spawnflags 2, removed from the world unless spawnflags 1; each member also keeps its own BSP place as `csgo_origin` / `csgo_angles` (CS:GO's CPointTemplate placement in floats on that map: docs/crazykart/ivp-physbox.md 8); a lone `angle` as `angles`. Everything else (VScript, RunScriptCode, CS:GO-only classes) as the map has it, for the hand ports |
| Sounds the entities name | `soundevents.json` + `sounds/` | Source1Sounds.cs; each event typed `csgo_mega` with `curve` = Source's falloff for its soundlevel (calc_falloff, snd_refdb 60 / refdist 36 / gain_min 0.01), `soundlevel` and `music` kept for the hand ports |
| .pcf particle systems | `fx/` | Source1Particles.cs (unchanged) |
| env_sprite textures | `sprites/` | data for env_sprite's hand port (no CS2 class) |
| worldspawn skyname | `sky/<rt,bk,lf,ft,up,dn>.png`, manifest `sky2d` | Stand-in: not drawn (CS2 draws an env_sky's material from lighting.json skies); a hand port can turn them into an env_sky + `rgbm-faces` sky |

Not baked: the 3D skybox's scaled view (its area's brushwork sits in the world glb where it was built), cubemap
reflections, vis.bin, chunks / tiers (the world is one 35 MB glb), radar, the color correction.

## ze_crazykart_v4

332 brush models, 5368 brushes, 56 displacements, 171 static props (143 solid). physics.bin 3.2 MB: world 3631 brush
hulls + 7168 displacement triangles + 713 static prop hulls, 331 brush models, 6 studio models. sim-test: 4 bots stand
at z -15872 under spawns at -15864 and walk; the browser loads it, walks, lightmaps on, no console errors.

Classes with no handler in web/src/world/entities (registry): light (910, baked), point_worldtext (69),
func_illusionary (28), info_teleport_destination (16, a target only), env_sprite (14), env_steam (11),
env_spritetrail (8), skybox_swapper (6), logic_eventlistener (6), func_precipitation (3),
point_viewcontrol_multiplayer (2), point_broadcastclientcommand, func_buyzone, info_game_event_proxy,
game_weapon_manager, game_score, env_tonemap_controller, filter_damage_type, sky_camera, info_player_start,
light_environment (read by the lighting only), game_ui (CS:GO's class; ours is CS2Fixes' logic_case form), worldspawn.
13 VScripts (luffaren/...: kartcontroller, the shells, star, artillery, bossbreak, manager, filter, zestagewinner),
527 RunScriptCode / CallScriptFunction connections.
