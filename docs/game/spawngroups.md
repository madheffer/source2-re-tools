# Spawn groups: info_spawngroup_load_unload

server_20261105.dll, read with tools/re only (inputs.py, rtti.py, vdiff.py, vtdump.py, schema.py, disasm.py,
callers.py); ReVa was not running. The entity's half is here; the engine's half (engine2 / worldrenderer: the load
itself, where the group's entities and world are placed, what a round restart does) is **not traced**.

A map's `info_spawngroup_load_unload` (mapname `prefabs/<x>`) loads a second world, compiled as
`maps/prefabs/<x>.vpk` beside the map's own vpk in the workshop item, into the running map, and unloads it again.
ze_dark_souls (3387284574): `[PR#]garnilo_vpk` (prefabs/garnilo: the wolf arena's exit and the last section, 349
entities, its own world node, world_physics and lightmaps) and `[PR#]tree_vpk` (prefabs/tree: no vpk in the item).

## The class

`CInfoSpawnGroupLoadUnload`, vtable 0x181996dd8 (base CLogicalEntity 0x1817a6e58; overrides at 0x0, 0x20, 0x48,
0x68, 0x160-0x178 and its own four at 0x770-0x788). `CInfoSpawnGroupLandmark`, vtable 0x181996660: no inputs.

Fields (schema.py --near 0x181e320f0):

| Offset | Field | Keyvalue |
|---|---|---|
| 0x4a8 / 0x4c0 / 0x4d8 / 0x4f0 | m_OnSpawnGroupLoadStarted / LoadFinished / UnloadStarted / UnloadFinished | the outputs |
| 0x508 | m_iszSpawnGroupName | mapname |
| 0x510 | m_iszSpawnGroupFilterName | entityfiltername |
| 0x518 | m_iszLandmarkName | landmark |
| 0x520 | m_sFixedSpawnGroupName | (Spawn: the name with its slashes fixed) |
| 0x528 | m_flTimeoutInterval | timeoutinterval |
| 0x52c | m_bAutoActivate | autoactivate |
| 0x52d | m_bUnloadingStarted | |
| 0x52e | m_bQueueActiveSpawnGroupChange | |
| 0x52f | m_bQueueFinishLoading | |
| 0x530 | the load helper (its +0x18 = entity +0x548: the group's handle) | |

Inputs (inputs.py: the entity-API records at 0x181e31eb0..): each wrapper resolves the entity from its handle and
calls one virtual.

| Input | Wrapper | Virtual |
|---|---|---|
| StartSpawnGroupLoad | 0x180dd5ce0 | vfn 0x770 = 0x180dea580 |
| StartSpawnGroupUnload | 0x180dd60c0 | vfn 0x778 = 0x180dea720 |
| ActivateSpawnGroup | 0x180dd5ef0 | vfn 0x780 = 0x180dea380 |
| SetSpawnGroup | 0x180dd6290 | vfn 0x788 = 0x180dea4c0 |

## What each does

- **Spawn** (vfn 0x48, 0x180df33f0): m_sFixedSpawnGroupName = m_iszSpawnGroupName, FixSlashes('\\'), pooled back
  into m_iszSpawnGroupName; the base Spawn; `0 >= m_flTimeoutInterval` makes it 30.0 (0x41f00000). **Nothing is
  loaded at spawn.**
- **Activate** (vfn 0x68, 0x180de0d40): the base's, then an empty group name: a warning and UTIL_Remove
  (0x180c30c10).
- **StartSpawnGroupLoad** (0x180dea580): strlen(m_iszLandmarkName) <= 0: a warning, nothing. Else a request
  { name, filter name, landmark name, timeout, two flags 1 / 1 } to the helper's 0x1804a87f0; when that returns
  true: m_OnSpawnGroupLoadStarted fires (0x1802a66e0, activator and caller the entity), the think becomes the
  loading think (0x180df34b0, context "CInfoSpawnGroupLoadUnloadSpawnGroupLoadingThink") at the current tick, and
  m_bQueueActiveSpawnGroupChange / m_bQueueFinishLoading are cleared.
- **The load request** (0x1804a87f0, 2 callers: this class and 0x180fe68e0): the engine's group of that name (vfn
  0x2a0 of the object at 0x1821b9010) or the helper's own handle: when either is loaded (engine vfn 0x1f0) or
  loading / waiting (vfn 0x1f8), **false: no second load**. The landmark: FindEntityByName (0x180bfc940) cast to
  the landmark class (0x1816b6d80); none: a warning, false. Its abs origin (0x1803d6f50) and abs angles
  (0x1803d6de0) go into the helper (+0x28, +0x40), then the engine's load (vfn 0x1e0) with a descriptor (the name,
  the filter name, the timeout at +0x33.., the two flag bytes); the handle it returns is kept (+0x18).
- **The loading think** (0x180df34b0), every tick (next think = now):
  - m_bQueueFinishLoading set: once the group is loaded (vfn 0x1f0): the flag clears, a queued active-group change is
    made (0x52e: object 0x182087470's vfn 0x38), the think stops (next think never), the world layer
    "world_layer_base" is shown (vfn 0x68 of the group's layer object).
  - otherwise: ready = 0x1805a17a0(handle), loaded = vfn 0x1f0. Either: **m_OnSpawnGroupLoadFinished fires**. Loaded:
    the think stops (and the layer call). Not loaded, m_bAutoActivate and not queued: the group is activated
    (0x18058af80) and m_bQueueFinishLoading = 1. (Read as written: without autoactivate a ready group fires
    OnSpawnGroupLoadFinished every tick until ActivateSpawnGroup.)
- **ActivateSpawnGroup** (0x180dea380): a handle that is waiting (vfn 0x1f8): activated (0x18058af80), both queue
  flags set (0x101 at 0x52e). Else the group by name (0x18058ac50): none: a warning; loaded: made the active spawn
  group (vfn 0x38), the think stops, the layer call.
- **StartSpawnGroupUnload** (0x180dea720): the group by name (0x18058ac50); found: the think becomes the unloading
  think (0x180df3770) at the current tick. Not found: nothing.
- **The unloading think** (0x180df3770): the group by name. Not found: with m_bUnloadingStarted set, it clears and
  **m_OnSpawnGroupUnloadFinished fires**; the think stops. Found: next think = now; when the engine allows it (vfn
  0x2f8 of 0x1821ba1c0): the first time m_bUnloadingStarted = 1, the unload is asked for (0x182087470's vfn 0x40)
  and **m_OnSpawnGroupUnloadStarted fires**; later, once it is no longer loaded (vfn 0x1f0), the flag clears, the
  think stops and OnSpawnGroupUnloadFinished fires.
- **SetSpawnGroup** (0x180dea4c0): m_iszSpawnGroupName = the parameter (a string variant, pooled).

Helpers: 0x18058ac50 a spawn group's handle by name (11 callers); 0x18058af80 activate a loaded group (4 callers);
0x1805a17a0 "the group's load is ready" (7 callers); 0x1803eb9e0 SetNextThink(tick); 0x1803ee6e0 set the think
function; 0x180927cb0 the entity's current tick; 0x18017ca70 a tick from seconds (with -1: never).

## What the port does (web/src/world/entities/classes/spawngroups.js)

The inputs, the two thinks, the flags and the four outputs as above. In CS2's frame an input runs in the I/O pass
and its think from the next tick's think pass, so: the load's input fires OnSpawnGroupLoadStarted; the next tick's
think finds the group ready, fires OnSpawnGroupLoadFinished and (autoactivate) activates it: **the group's entities
spawn there**; the tick after, the think stops. The unload's input starts the think; the next tick's think removes
the group's entities and world and fires OnSpawnGroupUnloadStarted; the tick after, OnSpawnGroupUnloadFinished.

**Stand-ins** (the engine's half, untraced):

- How long a load, an activation and an unload take. CS2 reads the vpk from disk over frames; here the group is
  ready the tick it is asked for, on the server and every replica alike.
- The group's placement: the landmark's origin and angles are handed to the engine; here the group is placed as
  baked (ze_dark_souls' landmark is at the origin with no angles, and the group has none of its own).
- A round restart: each round here is a new world without the group. CS2's CleanUpMap ([round-restart.md](round-restart.md))
  removes the entities of world group 0 that are off its preserve list, then its respawn pass creates the lumps of
  every flagged spawn group again: so a group that is loaded most likely **stays loaded over a restart with its
  entities made anew** (which world group a loaded prefab is in, and its record's byte +9, are unread).
  ze_dark_souls' own logic_auto sends StartSpawnGroupUnload 1 s into every round, which fits: the difference from
  the port is that first second of a round after one that ended with the group loaded.
- Whether the engine loads a group at map start by itself (the map's world naming it as a child): taken as no (the
  entity's Spawn loads nothing).
- m_flTimeoutInterval, entityfiltername, the engine's "may unload" answer (taken as yes), a group whose vpk the
  item lacks (stays "loading", spawns nothing), a logic_auto inside a group (OnMapSpawn, as for a template).
- The group's world to a trace is "the world" (handle 0x8000), as the map's own; in CS2 it is the group's own
  worldspawn entity.
- A point_template inside a group spawns into its group (CPointTemplate's m_ownerSpawnGroupType unread).

One thing the bake showed: ze_dark_souls' own world_physics already has collision in garnilo's area (a floor 6 u
under the group's by the wolf arena's door), so a player is not always in the void there while the group is
unloaded; the two worlds' collision are both in place while it is loaded, as shipped.
