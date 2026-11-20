# env_gradient_fog (C_GradientFog)

client_20261015, server_20261105 (the enabled flag only).

## Functions

| Address | Module | What |
|---|---|---|
| 0x180275400 | client | cook (C_GradientFog *, out *) -> out: the 0x28-byte record |
| 0x18174a050 | client | a Color's sRGB bytes -> linear floats ([barn-lights.md](barn-lights.md)) |
| 0x180271810 | client | Spawn (vtable slot 13, +0x68) |
| 0x18026f0d0 / 0x18026eca0 | client | put a fog of another world group into the hash table 0x1821c6500 |
| 0x18026ee70 | client | take a fog out of the table |
| 0x1809dfb70 | client | walks entities by class name (`sky_camera`) |
| 0x18027fd10 | client | FogStateChanged (network change callback) |
| 0x18026f930 | client | registers FogStateChanged for class "C_GradientFog" |
| 0x18027cd77..0x18027ddde | client | the schema registration (fields, then the callback; fnstrings.py over 0x18027d900..0x18027ddde) |
| 0x180272420 | client | frame update (vtable slot 146, +0x490) |
| 0x1801587b0 | client | clamp |
| 0x18027f630 | client | lerp the ten floats |
| 0x180ae7d50 | client | schedule a think (this, function, time, 0) |
| 0x18015c5fc | client | thunk `mov rax,[rcx]; jmp [rax+0x490]` (slot 146) |
| 0x180ae6890 | client | C_BaseEntity slot 146: empty `ret` |
| 0x180b808e0 | client | think manager add (manager, entity handle, context, function, time) |
| 0x180b73290 | client | link a think node ("before" = 0xffff: at the tail) |
| 0x180b7b220 | client | think runner (called from 0x180b820f0) |
| 0x180b820f0 | client | calls the runner |
| 0x180b5f630 | client | gathers the parent's think first (0x18021c9b0's entity) |
| 0x18021c9b0 | client | the entity's parent (taken as: only the recursion was read) |
| 0x18027186f | client | Spawn's store of an enabled group-0 fog in the global |
| 0x180283790 | client | a view's fog reader |
| 0x1802832e0 | client | copies a fog's values |
| 0x1803f5910 / 0x1803f5ab0 | server | script bindings Enable (to 1) / Disable (to 0) ("CGradientFog" at 0x1817d1b20; 0x1803f5910 read whole) |
| 0x180440080 | server | the network setter |
| 0x1804309b0 / 0x180445670 | server | store a flag argument at 0x4e1 (taken as the Enable / Disable inputs: only their store read) |

## Fields

C_GradientFog, vtable 0x181adbf60 (schema.py --near 0x1821c6340). FC = FogStateChanged callback.

| Offset | Field |
|---|---|
| 0x600 | m_hGradientFogTexture |
| 0x608 | m_flFogStartDistance (FC) |
| 0x60c | m_flFogEndDistance (FC) |
| 0x610 | m_bHeightFogEnabled (FC) |
| 0x614 | m_flFogStartHeight (FC) |
| 0x618 | m_flFogEndHeight (FC) |
| 0x61c | m_flFarZ (FC) |
| 0x620 | m_flFogMaxOpacity (FC) |
| 0x624 | m_flFogFalloffExponent (FC) |
| 0x628 | m_flFogVerticalExponent (FC) |
| 0x62c | m_fogColor (Color: r g b a bytes) (FC) |
| 0x630 | m_flFogStrength (FC) |
| 0x634 | m_flFadeTime (FC) |
| 0x638 | m_bStartDisabled (no callback) |
| 0x639 | m_bIsEnabled (no callback) |
| 0x63a | m_bGradientFogNeedsTextures |
| 0x63c | (not in schema) distance scale, 1 unless set at spawn |
| 0x640 | (not in schema) blend start time, -1: no blend |
| 0x644 | (not in schema) cooked values the blend starts from, 0x28 bytes |
| 0x66c | (not in schema) cooked values drawn now, 0x28 bytes |
| entity +0x10 -> +0x38 | CEntityIdentity::m_worldGroupId (0: the main world) |
| sky_camera int16 +0x608 | its scale |
| think node (0x28 bytes) | handle, context, function +8, next time +0x10, last time +0x14, world group +0x18, run stamp +0x1c, prev +0x20, next +0x22 |
| think manager +0x10 / +0x12 | list head / tail (list at +0x18) |
| think manager +0x4c / +0x30 | running thinks / queued changes |
| server CGradientFog (vtable 0x1817d2ba8) | m_fogColor 0x4d4, m_bIsEnabled 0x4e1 |

## Constants

| Value | What |
|---|---|
| 0x182388590 | global: the drawn fog of world group 0 (C_GradientFog *) |
| 0x1821c6500 | hash table: fog per other world group |
| 0x182233c30 | client think manager |
| [0x182230090] + 0x30 | the current time |
| -1293.0 ([0x181ac60b4]) | "every frame" think time |
| 0.00392156886 ([0x181ada27c]) | 1 / 255 |
| 0.0404499993 / 12.9200001 ([0x181e0c4c4], [0x181e0c514]) | sRGB linear segment |
| 0.0549999997 / 1.05499995 / 2.4000001 | sRGB power segment |
| tier0 V_powf (import 0x181aad530) | |

## Cooked record (0x180275400)

`s` = +0x63c.

| Out | Value |
|---|---|
| +0x00 | s x m_flFogStartDistance |
| +0x04 | s x m_flFogEndDistance |
| +0x08 | m_bHeightFogEnabled ? s x m_flFogStartHeight : 0 |
| +0x0c | m_bHeightFogEnabled ? s x m_flFogEndHeight : 0 |
| +0x10 | m_flFogMaxOpacity |
| +0x14 | m_flFogFalloffExponent |
| +0x18 | m_bHeightFogEnabled ? m_flFogVerticalExponent : 0 |
| +0x1c / +0x20 / +0x24 | linear red / green / blue x m_flFogStrength |

Colour, per channel, in this order (alpha not read):

    c = (float)byte x 0.00392156886
    c = c < 0 ? 0 : min(1, c)
    c = c <= 0.0404499993 ? c / 12.9200001
                          : V_powf((c + 0.0549999997) / 1.05499995, 2.4000001)

then `mulss strength, channel`. `fogcolor 10 16 32` at strength 1 = (0.00304, 0.00518, 0.01444) linear, not (0.0392,
0.0627, 0.1255) as VRF's SceneGradientFog takes it (GetColor32Property / 255, no decode).

## Spawn (0x180271810)

1. m_bIsEnabled = !m_bStartDisabled. m_bGradientFogNeedsTextures from a global's virtual (+0x4a8), unread.
2. Enabled: world group 0 -> the global 0x182388590 = this; another group -> the hash table.
3. +0x63c = 1; then, only for group 0, every `sky_camera` of group 0 with scale > 0 sets it to 1 / scale.
4. Cooked values into +0x644 and +0x66c; +0x640 = -1.
5. Ends with `0x180ae7d50(this, 0x18015c5fc, -1293.0, 0)`: the frame update as a think.

## FogStateChanged (0x18027fd10)

    from (+0x644) = now (+0x66c);  +0x640 = the current time

## Frame update (0x180272420)

1. Not enabled: the drawn one (group 0) clears the global; another group: out of the table. Nothing fades.
2. Enabled, group 0: the global = this fog.
3. +0x640 > 0: target = cook(fields now);

       t = m_flFadeTime > 0 ? clamp((now - start) / m_flFadeTime, 0, 1) : 1
       t < 1:  now = from + (target - from) x t, each of the ten floats
       else:   now = from = target, +0x640 = -1

   The fade time is read each frame; the blend is of the cooked values (colour linear, already times strength).

## Which fog is drawn

- No priority, blend or distance test: one pointer per world group, written by the fogs.
- 0x180b808e0: a new think takes a node through 0x180b73290, linked at the tail; while thinks run (+0x4c) the change is queued (+0x30).
- 0x180b7b220 walks the list from its head by `next`, gathers the due thinks in that order, calls each (`call [node+8]` with the entity). 0x180b5f630 gathers the parent's think first: a parent thinks before its child.
- So thinks run in spawn order and **the last-spawned enabled fog is the drawn one**. A disabled fog clears the global only when it is the drawn one; an earlier enabled fog has already stored itself that frame, so disabling the last hands the view to the enabled one before it within the same frame. Enable / disable takes hold at the fog's next think (the next frame).
- 0x180283790: given the view's world groups, the first with a fog in the table wins (0x1802832e0 copies), else the global's fog; none: the fog block is zeroed.

## Enable / Disable (server)

0x1803f5910 / 0x1803f5ab0 set m_bIsEnabled (0x4e1) through 0x180440080 and nothing else. No client callback: on or off
at once, blend state untouched.

## Unread

- How 0x1802832e0's values become the scene's fog constants; the pixel program's maths.
- m_flFarZ's reader (not among the cooked values).
- The server's Set* input handlers (taken as plain setters).
- m_hGradientFogTexture / m_bGradientFogNeedsTextures.
- The client's entity spawn order; 0x18021c9b0; how a world group other than 0 enters a view's list (a 3D skybox's world, by the sky_camera scale); where a skybox world's fog is drawn.
