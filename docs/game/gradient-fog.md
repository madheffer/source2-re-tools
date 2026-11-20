# env_gradient_fog: C_GradientFog in client.dll

Read 2026-11-18 from client_20261015.dll (disassembly, tools/re: schema, rtti, fieldwrites, fnat, disasm, riprefs,
fnstrings, vtowner) and server_20261105.dll (the enabled flag only). Ported in
web/src/world/entities/classes/fog.js (the fields, the cooking, the blend) and web/src/world/lighting.js (the
uniforms). The question that started it: is `fogcolor` gamma-decoded? Yes.

## The class

C_GradientFog, vtable 0x181adbf60. Fields (schema.py --near 0x1821c6340):

| Offset | Field | |
|---|---|---|
| 0x600 | m_hGradientFogTexture | |
| 0x608 | m_flFogStartDistance | FogStateChanged |
| 0x60c | m_flFogEndDistance | FogStateChanged |
| 0x610 | m_bHeightFogEnabled | FogStateChanged |
| 0x614 | m_flFogStartHeight | FogStateChanged |
| 0x618 | m_flFogEndHeight | FogStateChanged |
| 0x61c | m_flFarZ | FogStateChanged |
| 0x620 | m_flFogMaxOpacity | FogStateChanged |
| 0x624 | m_flFogFalloffExponent | FogStateChanged |
| 0x628 | m_flFogVerticalExponent | FogStateChanged |
| 0x62c | m_fogColor (Color: r g b a bytes) | FogStateChanged |
| 0x630 | m_flFogStrength | FogStateChanged |
| 0x634 | m_flFadeTime | FogStateChanged |
| 0x638 | m_bStartDisabled | |
| 0x639 | m_bIsEnabled | no callback |
| 0x63a | m_bGradientFogNeedsTextures | |
| 0x63c | (not in the schema) a distance scale, 1 unless set at spawn (below) | |
| 0x640 | (not in the schema) the blend's start time, -1: no blend | |
| 0x644 | (not in the schema) the cooked values the blend starts from, 0x28 bytes | |
| 0x66c | (not in the schema) the cooked values drawn now, 0x28 bytes | |

The twelve fields marked FogStateChanged carry that network change callback (the schema registration in
0x18027cd77..0x18027ddde names each field and then the callback: fnstrings.py over 0x18027d900..0x18027ddde);
m_bStartDisabled and m_bIsEnabled do not.

server.dll (server_20261105): CGradientFog vtable 0x1817d2ba8, m_fogColor 0x4d4, m_bIsEnabled 0x4e1.

## The cooked values: 0x180275400 (C_GradientFog *, out *) -> out

A 0x28-byte record, `s` = the scale at +0x63c:

| Out | Value |
|---|---|
| +0x00 | s x m_flFogStartDistance |
| +0x04 | s x m_flFogEndDistance |
| +0x08 | m_bHeightFogEnabled ? s x m_flFogStartHeight : 0 |
| +0x0c | m_bHeightFogEnabled ? s x m_flFogEndHeight : 0 |
| +0x10 | m_flFogMaxOpacity |
| +0x14 | m_flFogFalloffExponent |
| +0x18 | m_bHeightFogEnabled ? m_flFogVerticalExponent : 0 |
| +0x1c | linear red x m_flFogStrength |
| +0x20 | linear green x m_flFogStrength |
| +0x24 | linear blue x m_flFogStrength |

The colour goes through 0x18174a050 first (the helper barn-lights.md already lists: a Color's sRGB bytes -> linear
floats). Per channel, in this order:

    c = (float)byte x 0.00392156886         ; [0x181ada27c]
    c = c < 0 ? 0 : min(1, c)
    c = c <= 0.0404499993 ? c / 12.9200001  ; [0x181e0c4c4], [0x181e0c514]
                          : V_powf((c + 0.0549999997) / 1.05499995, 2.4000001)   ; tier0.dll!V_powf (import 0x181aad530)

then x m_flFogStrength (`mulss strength, channel`). Alpha is not read.

So `fogcolor 10 16 32` at strength 1 is (0.00304, 0.00518, 0.01444) linear, not (0.0392, 0.0627, 0.1255) as VRF's
SceneGradientFog takes it (GetColor32Property / 255, no decode): VRF's fog is 8 to 13 times too bright for a dark
colour.

## Spawn: 0x180271810 (vtable slot 13, +0x68)

- m_bIsEnabled = !m_bStartDisabled.
- m_bGradientFogNeedsTextures from a global's virtual (+0x4a8), unread.
- Enabled and the entity's +0x10 -> +0x38 == 0 (an id: 0 looks like the main world; a fog of another id is put in a
  hash table at 0x1821c6500 keyed by it, 0x18026f0d0 / 0x18026eca0): the global 0x182388590 = this fog (the drawn
  one).
- The scale +0x63c = 1; then, only for id 0, every `sky_camera` entity (0x1809dfb70 walks them by class name) of
  id 0 whose int16 at +0x608 (its scale) is > 0 sets it to 1 / scale. A map's own fog has no sky_camera beside it
  (the 3D skybox is another world), so 1. UNREAD: what id +0x38 is exactly, and where a skybox world's fog is drawn.
- The cooked values (0x180275400) into both +0x644 (from) and +0x66c (now); +0x640 = -1.

## A field changes: FogStateChanged 0x18027fd10

    from (+0x644) = now (+0x66c);  +0x640 = the current time (global [0x182230090] + 0x30)

Registered by 0x18026f930 for class "C_GradientFog".

## Every frame: 0x180272420 (vtable slot 146, +0x490)

- Not enabled: if this fog is the drawn one (0x182388590, id 0) the global is cleared (another id: taken out of the
  table, 0x18026ee70). Nothing fades: Disable takes the fog off at once.
- Enabled, id 0: the global = this fog. With several enabled, the one whose update ran last in the frame is drawn:
  the last one spawned ("Several fogs" below).
- +0x640 > 0 (a blend runs): target = the cooked values of the fields now (0x180275400);

      t = m_flFadeTime > 0 ? clamp((now - start) / m_flFadeTime, 0, 1) : 1      ; 0x1801587b0 is the clamp
      t < 1:  now = from + (target - from) x t, each of the ten floats (0x18027f630)
      else:   now = from = target, +0x640 = -1

  The fade time is read each frame, not kept from the blend's start, and the blend is of the cooked values: the
  colour blends linear and already times its strength.

## Several fogs: which one is drawn

There is no priority, blend or distance test between gradient fogs: one pointer per world group, written by the
fogs themselves.

- The id at entity +0x10 -> +0x38 is CEntityIdentity::m_worldGroupId. Group 0 (the main world) uses the global
  0x182388590 (a C_GradientFog *); any other group has its fog in the hash table 0x1821c6500 keyed by the group.
- The frame update is a think, not a per-frame virtual call: Spawn ends with
  `0x180ae7d50(this, 0x18015c5fc, -1293.0, 0)`, where 0x18015c5fc is the thunk `mov rax,[rcx]; jmp [rax+0x490]`
  (slot 146) and -1293.0 ([0x181ac60b4]) is the "every frame" think time. 0x180ae7d50 hands it to the client think
  manager (0x182233c30) through 0x180b808e0. Slot 146 of C_BaseEntity is an empty `ret` (0x180ae6890).
- 0x180b808e0 (manager, entity handle, context, function, time): a new think takes a node of the linked list at
  manager +0x18 (0x28-byte nodes: handle, context, function +8, next time +0x10, last time +0x14, world group +0x18,
  a run stamp +0x1c; prev +0x20, next +0x22) through 0x180b73290 with "before" = 0xffff: linked at the tail
  (head at list +0x10, tail +0x12). While the thinks are being run (manager +0x4c) the change is queued instead
  (+0x30).
- The runner 0x180b7b220 (called from 0x180b820f0) walks the list from its head by `next`, gathers the due thinks
  into an array in that order, then calls each (`call [node+8]` with the entity). 0x180b5f630 first gathers the think
  of the entity that 0x18021c9b0 returns for it (taken as its parent: only the recursion was read), so a parent
  thinks before its child.
- So the thinks run in the order the fogs spawned, each enabled one of group 0 stores itself in the global, and the
  last store stands: **the last-spawned enabled fog is the drawn one**. A disabled fog clears the global only when
  it is the drawn one; an earlier enabled fog has already stored itself that frame, so disabling the last one hands
  the view to the enabled one before it within the same frame. Enabling or disabling takes hold at the fog's next
  think (the next frame).
- Spawn itself also stores an enabled group-0 fog in the global (0x18027186f), the same order.
- The reader 0x180283790 (a view's fog): given the view's list of world groups, the first group with a fog in the
  table wins (0x1802832e0 copies its values), else the global's fog; none: the fog block is zeroed.

UNREAD: the order the client spawns a map's entities in (ours: the map's entity order), 0x18021c9b0, and how a
world group other than 0 comes to be in a view's list (a 3D skybox's world, by the sky_camera scale at Spawn).

## Enable / Disable (server.dll)

0x1803f5910 (to 1) and 0x1803f5ab0 (to 0), the script bindings ("CGradientFog" at 0x1817d1b20; 0x1803f5910 read
whole), set m_bIsEnabled (0x4e1) through the network setter 0x180440080 and do nothing else. 0x1804309b0 and
0x180445670 store a flag argument there the same way (taken as the Enable / Disable inputs: only their store was
read). The flag has no callback on the client: the fog goes on or off at once, its blend state untouched.

## Unread

- Past the reader 0x180283790 ("Several fogs"): how the values it copies (0x1802832e0) become the scene's fog
  constants, and the pixel program's own maths (ours is VRF's fog.slang: the distance and height terms biased, scaled, raised to their exponents, times
  the max opacity).
- m_flFarZ's reader (it is not among the cooked values: ours uses the field as it is).
- The server's Set* input handlers (taken as plain setters of the networked fields).
- m_hGradientFogTexture / m_bGradientFogNeedsTextures.
