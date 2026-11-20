# Spawn groups: info_spawngroup_load_unload

server_20261105 (tools/re only). The entity's half; the engine's half (engine2 / worldrenderer: the load itself, the
placement of the group's entities and world, what a round restart does) is not traced.

A map's `info_spawngroup_load_unload` (mapname `prefabs/<x>`) loads a second world, compiled as `maps/prefabs/<x>.vpk`
beside the map's vpk in the workshop item, into the running map, and unloads it again. ze_dark_souls (3387284574):
`[PR#]garnilo_vpk` (prefabs/garnilo: the wolf arena's exit and the last section, 349 entities, its own world node,
world_physics and lightmaps) and `[PR#]tree_vpk` (prefabs/tree: no vpk in the item).

## Functions

| Address | Module | What |
|---|---|---|
| 0x180df33f0 | server | Spawn (vfn 0x48) |
| 0x180de0d40 | server | Activate (vfn 0x68) |
| 0x180dd5ce0 -> 0x180dea580 | server | StartSpawnGroupLoad (wrapper -> vfn 0x770) |
| 0x180dd60c0 -> 0x180dea720 | server | StartSpawnGroupUnload (-> vfn 0x778) |
| 0x180dd5ef0 -> 0x180dea380 | server | ActivateSpawnGroup (-> vfn 0x780) |
| 0x180dd6290 -> 0x180dea4c0 | server | SetSpawnGroup (-> vfn 0x788): m_iszSpawnGroupName = the parameter (string variant, pooled) |
| 0x1804a87f0 | server | the load request (2 callers: this class and 0x180fe68e0) |
| 0x180df34b0 | server | loading think ("CInfoSpawnGroupLoadUnloadSpawnGroupLoadingThink") |
| 0x180df3770 | server | unloading think |
| 0x180c30c10 | server | UTIL_Remove |
| 0x1802a66e0 | server | fire an output |
| 0x180bfc940 | server | FindEntityByName |
| 0x1816b6d80 | server | cast to the landmark class |
| 0x1803d6f50 / 0x1803d6de0 | server | abs origin / abs angles |
| 0x18058ac50 | server | a spawn group's handle by name (11 callers) |
| 0x18058af80 | server | activate a loaded group (4 callers) |
| 0x1805a17a0 | server | the group's load is ready (7 callers) |
| 0x1803eb9e0 | server | SetNextThink(tick) |
| 0x1803ee6e0 | server | set the think function |
| 0x180927cb0 | server | the entity's current tick |
| 0x18017ca70 | server | tick from seconds (-1: never) |

## Fields

`CInfoSpawnGroupLoadUnload` vtable 0x181996dd8 (base CLogicalEntity 0x1817a6e58; overrides 0x0, 0x20, 0x48, 0x68,
0x160-0x178 and its own four at 0x770-0x788). `CInfoSpawnGroupLandmark` vtable 0x181996660: no inputs. Schema near
0x181e320f0; input records at 0x181e31eb0.. (each wrapper resolves the entity from its handle and calls one virtual).

| Offset | Field |
|---|---|
| 0x4a8 / 0x4c0 / 0x4d8 / 0x4f0 | m_OnSpawnGroupLoadStarted / LoadFinished / UnloadStarted / UnloadFinished |
| 0x508 | m_iszSpawnGroupName (mapname) |
| 0x510 | m_iszSpawnGroupFilterName (entityfiltername) |
| 0x518 | m_iszLandmarkName (landmark) |
| 0x520 | m_sFixedSpawnGroupName |
| 0x528 | m_flTimeoutInterval (timeoutinterval) |
| 0x52c | m_bAutoActivate (autoactivate) |
| 0x52d | m_bUnloadingStarted |
| 0x52e | m_bQueueActiveSpawnGroupChange |
| 0x52f | m_bQueueFinishLoading |
| 0x530 | load helper (+0x18 = entity +0x548: the group's handle; +0x28 / +0x40 landmark origin / angles) |
| 0x1821ba010 | engine object (pointer): vfn 0x2a0 group by name, 0x1f0 loaded, 0x1f8 loading / waiting (0x1804a87f0's `mov rcx, [rip + 0x1d117b0]` at 1804a8859: the old notes' 0x1821b9010 was a slip; checked against the disassembly) |
| 0x1823ab630 | object (pointer) whose vfn 0x1e0 is the load (1804a8a1f / 1804a8aa3 in 0x1804a87f0; checked against the disassembly) |
| 0x182087470 | object: vfn 0x38 make active group, 0x40 unload |
| 0x1821ba1c0 | vfn 0x2f8: engine allows unload |

## Constants

| Value | What |
|---|---|
| 30.0 (0x41f00000) | timeout when `0 >= m_flTimeoutInterval` |
| 0x101 at 0x52e | both queue flags |
| "world_layer_base" | layer shown (vfn 0x68 of the group's layer object) |

## What each does

- **Spawn**: m_sFixedSpawnGroupName = m_iszSpawnGroupName, FixSlashes('\\'), pooled back into m_iszSpawnGroupName; base
  Spawn; timeout fix. Nothing is loaded at spawn.
- **Activate**: the base's; an empty group name: a warning and UTIL_Remove.
- **StartSpawnGroupLoad**: strlen(m_iszLandmarkName) <= 0: a warning, nothing. Else a request { name, filter name,
  landmark name, timeout, two flags 1 / 1 } to 0x1804a87f0; true: m_OnSpawnGroupLoadStarted (activator and caller the
  entity), think = loading think at the current tick, m_bQueueActiveSpawnGroupChange / m_bQueueFinishLoading cleared.
- **Load request** (0x1804a87f0): the engine's group of that name or the helper's handle: loaded (vfn 0x1f0) or loading
  / waiting (vfn 0x1f8) -> false (no second load). Landmark by name cast; none: a warning, false. Its abs origin and
  angles into the helper (+0x28, +0x40), then the engine's load (vfn 0x1e0) with a descriptor (name, filter name, the
  timeout at +0x33.., the two flag bytes); the returned handle kept (+0x18).
- **Loading think**, every tick (next think = now):
  - m_bQueueFinishLoading set: once loaded (vfn 0x1f0): flag clears, a queued active-group change made (0x52e: vfn 0x38),
    think stops (never), "world_layer_base" shown.
  - Otherwise: ready = 0x1805a17a0(handle), loaded = vfn 0x1f0. Either: m_OnSpawnGroupLoadFinished fires. Loaded: think
    stops (and the layer call). Not loaded, m_bAutoActivate, not queued: activated (0x18058af80), m_bQueueFinishLoading
    = 1. (As written: without autoactivate a ready group fires OnSpawnGroupLoadFinished every tick until
    ActivateSpawnGroup.)
- **ActivateSpawnGroup**: a waiting handle (vfn 0x1f8): activated, both queue flags set (0x101 at 0x52e). Else by name
  (0x18058ac50): none: a warning; loaded: made the active spawn group (vfn 0x38), think stops, the layer call.
- **StartSpawnGroupUnload**: by name; found: think = unloading think at the current tick. Not found: nothing.
- **Unloading think**: by name. Not found: with m_bUnloadingStarted, it clears and m_OnSpawnGroupUnloadFinished fires;
  think stops. Found: next think = now; when 0x1821ba1c0 vfn 0x2f8 allows: the first time m_bUnloadingStarted = 1, the
  unload asked (0x182087470 vfn 0x40), m_OnSpawnGroupUnloadStarted fires; later, once no longer loaded, the flag
  clears, think stops, OnSpawnGroupUnloadFinished fires.

Frame order: an input runs in the I/O pass, its think from the next tick's think pass.

## Round restart

CleanUpMap (round-restart.md) removes world group 0's entities off its preserve list, then its respawn pass creates the
lumps of every flagged spawn group again: a loaded group most likely stays loaded over a restart with its entities made
anew (which world group a loaded prefab is in, and its record's byte +9, are unread). ze_dark_souls' logic_auto sends
StartSpawnGroupUnload 1 s into every round.

ze_dark_souls' world_physics already has collision in garnilo's area (a floor 6 u under the group's by the wolf arena's
door); both worlds' collision are in place while the group is loaded.

## Unread

- How long a load, an activation and an unload take (CS2 reads the vpk over frames).
- The placement: the landmark's origin and angles are handed to the engine (ze_dark_souls' landmark is at the origin
  with no angles).
- Whether the engine loads a group at map start by itself (taken as no: Spawn loads nothing).
- m_flTimeoutInterval's use, entityfiltername, the engine's "may unload" answer, a group whose vpk the item lacks, a
  logic_auto inside a group.
- The group's world to a trace: in CS2 the group's own worldspawn entity, not the map's world (handle 0x8000); how
  traces treat it is unread.
- A group whose vpk the workshop item lacks (prefabs/tree): what the engine does (taken as: stays loading, spawns
  nothing).
- A point_template inside a group (CPointTemplate's m_ownerSpawnGroupType).
