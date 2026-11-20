# First-person legs

client_20261015; shaders_vulkan_dir.vpk (`csgo_legs_prepass_vulkan_50_{vs,ps}.vcs`, `csgo_character_vulkan_50_vs.vcs`,
reflected with vpkstuff `--glsl-combo`); materialsystem2, scenesystem, rendersystemvulkan.

## Functions

| Address | Module | What |
|---|---|---|
| 1811d7f70 | client | the legs layers (FirstpersonLegsPass1 / Pass2) |
| 18174fe70 | client | projection rebuild (near plane offset) |
| 18016a9f0 | client | attribute map token -> value insert |
| 1811d81a4 | client | builds pass 1's stencil override (four words, bitfield writes: 3, 0x0577, 0x0412, 0x0303) |
| 1811d10e0 | client | "Not Depth Pre-passed" layer: the only other stencil override near it |
| 180c9d440 | client | pawn per-frame scene update: object flags, FirstpersonLegsFade |
| 18021a2c0, 180c7ede0 | client | walk the pawn's attached entities |
| 180b00410 | client | entity +0x56a test (viewmodel parts) |
| 1810d1750, 1810d1950 | client | C_CS2HudModelArms / C_CS2HudModelWeapon vfn 0x30: write +0x56a |
| 180c95630 | client | pawn ShouldDraw in first person: the only cl_firstperson_legs read |
| 180ca1830 | client | legs-view test (with vfn 0x4e8) |
| 180c9d7c9 | client | the fade formula's code |
| 1811c8277 | client | sets FirstPersonLegsDisableDistortion (another view only) |
| 1811c9bba | client | binds g_tBlueNoise (hash 0x88243422) |
| 1811ffe94 | client | blue noise mask (255, 255) |
| 180ae02f0 | client | aim_angle_pitch / _yaw from AngleQuaternion(movement services +0x3d8, +0x3d4, 0) against the pawn's rotation |
| 18006cd2a | scenesystem | -> materialsystem2 vfn 0x140 |
| 180037380 -> 1800168e0 -> 180026430 | materialsystem2 | SetRenderStateForMode; at 1800277cf merges the override |
| 1800b2f80 | rendersystemvulkan | CreateDepthStencilState (vfn 0x8a8 of CRenderDeviceVulkan 1805765c8) |
| 180576498 | rendersystemvulkan | identity enum table (Vulkan enums) |

## Fields

| Offset | Field |
|---|---|
| layer +0x1f0 | attribute map ("FirstpersonLegs" = 1) |
| layer +0x480 | object flags filter, `|= 0x6000000000000` (bits 49, 50) |
| layer +0x6b4 / +0x6c8 | stencil override 0x0303041205770003 / 1 |
| layer +0x6bc / +0x6c9 | the blend state's override, same kind |
| layer +0x690 | pass 2's own render state |
| layer +0x6cc | pass 2 stencil reference 3 |
| entity +0x56a | viewmodel flag (copied to children): no bit 50 |

## Constants

| Value | What |
|---|---|
| r_csgo_gpu_opt_firstpersonlegs_visible_angle 40 | forward . (0, 0, -1) >= cos(40): pitch >= 50 |
| r_csgo_firstpersonlegs_nearz_offset 0.1 | near plane offset |
| 0xd1565d45 | MurmurHash2 of "FirstpersonLegs" |
| 0xafd69318 | FirstpersonLegsFade (MurmurHash2 lower-case, seed 0x31415926) |
| 0x3f90408f | FirstPersonLegsDisableDistortion |
| DAT_1824d7640 | default state (0x0f, 0x77, 0xffff); pass 2 { 0x000b, 0x0122, 0, 0x0003 } |
| 0.01 grey | pass 1 colour (depth write, LessEqual) |
| textures/dev/blue_noise_256.vtex | core's g_tBlueNoise: RGBA8888, 256 x 256, one mip |

## Depth-stencil state bits (1800b2f80)

| Bits | What |
|---|---|
| 0 / 1 / 2-4 | depth test / write / func |
| 5 | reverse-Z swap of the func (LESS <-> GREATER, LEQUAL <-> GEQUAL when reverse-Z: vfn 0x540) |
| 16-18, 19 | front func, its swap |
| 20-22, 23 | back func, its swap |
| 24 | stencil enable |
| 25-27 / 28-30 / 32-34 | front fail / depth fail / pass |
| 35-37 / 38-40 / 41-43 | back fail / depth fail / pass |
| byte 6 / 7 | read / write mask |

VRF's "version 71" table has the front pass at 31-33 and the back ops one bit early; the backend reads the above.
At 1800277cf the shader's own bytes 0-1 (depth) stay, bytes 2-7 come from the override; override byte 0 is the
stencil reference (passed with the state to vfn 0x158).

## The passes

- **FirstpersonLegsPass1**: mode FirstpersonLegsPrepass (`csgo_legs_prepass.vfx`). Depth test, write, LEQUAL; stencil
  ALWAYS (both faces), fail REPLACE, depth fail KEEP, pass REPLACE, read / write mask 3, ref 3: every fragment surviving the discard and the depth test writes stencil 3.
  What the stencil held before pass 1 does not change the result (pass 2 needs depth EQUAL to a pass 1 fragment, so
  other values matter only where pass 2's depth happens to equal the world's).
- **FirstpersonLegsPass2** ("Firstperson Legs"): mode CsgoForward. Depth test + write, EQUAL; stencil EQUAL (both
  faces), ops KEEP, read mask 3, write mask 0, ref 3: shades only where pass 1 left depth and stencil.
- "Not Depth Pre-passed" (1811d10e0): NOT_EQUAL, ref 3, read mask 1, write mask 2, pass REPLACE.
- The view is copied with near + 0.1 and the projection rebuilt; both layers on it.

## The objects (180c9d440)

Walks the pawn and every attached entity; bit 49 on each scene object, bit 50 when in the legs view unless +0x56a
(180b00410). So the whole pawn (arms, hands) and attachments go through both passes. The world weapon's csgo_weapon has
no FirstpersonLegsPrepass mode (modes: Depth, CsgoForward, the tools'), so pass 1 skips it and pass 2 never passes.

## The fade

Local player in the legs view: `38 + 12 clamp((fz + 0.85) / -0.0999999642, 0, 1)`, fz = normalised view forward z;
0 otherwise, and 0 for objects 180b00410 picks.

## Vertex stage (both passes; csgo_character the same)

When fade > 0 and distortion not disabled:
`f = pow(saturate((posOs.z + 1) x 0.0125) x 0.5 x pow(saturate(-fwd.z), 2), 1.5)`; `clip.xy x= 1 + 5f`;
`clip.y -= 200f`; `clip.z -= 40f`; normal + (0, 0, 0.5) sign(f), renormalised; y flipped for Vulkan last. posOs: the
skinned model-space position.

## Prepass pixel shader

    s = smoothstep(fade - 35, fade, |eye - worldPos|) x step(0.8, normalize(posOs - (0, 0, 55)) . (0, 0, -1))
    discard if fma(s x 3, 2, -1.5) + texelFetch(g_tBlueNoise, ivec2(fragCoord) & mask).y < 0

mask = size - 1; fragCoord rows from the top; worldPos the skinned position before the warp (VS passes it relative to
the per-view origin, PS adds it back). Nearer than fade - 35, or outside the 37-degree cone under (0, 0, 55): never
drawn: no depth written, so pass 2 never shades them (chest, shoulders, head, upper arms). Between fade - 35 and fade the
blue noise dithers the edge.

## The hands

Nothing takes them out of the passes; the pose's last tasks are Aim IK (aim-ik.md) and Snap Weapon (wpn back on
hand_R, hand_L back on wpnHand_L). Standing at 85 degrees: P90 hand_R 22.1, hand_L 26.9 units from the eye; AK-47
17.2 / 29.1; Deagle 24.9 / 25.4. Fade 50: no fragment kept under 21.2 units, all past 26.4 (`6 smoothstep - 1.5 + noise >= 0`): a hand in that band shows dithered. The aim input: aim_angle_pitch / _yaw (180ae02f0), the eye angles relative to the body yaw.

## Unread

- The graph runtime's state machine transitions, selectors, value nodes (anim-graph.md "Left").
- Snap Weapon's modes 2 / 3 (weapon_molotov's lighter, weapon_knife_push): the weapon's secondary skeleton.
