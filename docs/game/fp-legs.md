# CS2's first-person legs, traced from client.dll 2026-10-15 and the shipped shaders

The port: `web/src/world/body-legs.js` (both passes, the fade), `world/body.js` (turns them on in first person),
`tools/bake-legs.mjs` (the blue noise texture). Shaders reflected from CS2's `shaders_vulkan_dir.vpk` with vpkstuff's
VpkStuff.Backend (`--glsl-combo`): `csgo_legs_prepass_vulkan_50_{vs,ps}.vcs`, `csgo_character_vulkan_50_vs.vcs`.

## When (FUN_1811d7f70, the legs layers)

Skipped unless forward . (0, 0, -1) >= cos(r_csgo_gpu_opt_firstpersonlegs_visible_angle = 40): pitch >= 50. The
view is copied with its near plane + r_csgo_firstpersonlegs_nearz_offset (0.1) and the projection rebuilt
(FUN_18174fe70). Two layers on that view. Each sets the layer attribute "FirstpersonLegs" = 1 (layer +0x1f0, an
attribute map: 18016a9f0 is a token -> value insert; 0xd1565d45 = MurmurHash2 of the name) and takes the objects with
flag bits 49 and 50 (+0x480 |= 0x6000000000000).

- **FirstpersonLegsPass1**: the material's FirstpersonLegsPrepass mode (`csgo_legs_prepass.vfx`), colour 0.01 grey
  with depth write, LessEqual (the shader's own state), and a stencil override (layer +0x6b4 = 0x0303041205770003,
  +0x6c8 = 1; built at 1811d81a4 as four words with bitfield writes: 3, 0x0577, 0x0412, 0x0303).
- **FirstpersonLegsPass2** ("Firstperson Legs"): the CsgoForward mode with its own state (+0x690), created from the
  default (0x0f, 0x77, 0xffff: DAT_1824d7640) as { 0x000b, 0x0122, 0, 0x0003 }; stencil reference 3 (+0x6cc).

### The stencil

The override goes to materialsystem2's SetRenderStateForMode (scenesystem 18006cd2a -> vfn 0x140 = 180037380 ->
1800168e0 -> 180026430). At 1800277cf it keeps the shader's own depth-stencil bytes 0-1 (the depth test, write and
func) and takes bytes 2-7 from the override; the override's byte 0 is the stencil reference (passed with the state to
vfn 0x158). (+0x6bc / +0x6c9 is a second override of the same kind, the blend state's.)

The bits, from rendersystemvulkan's CreateDepthStencilState (1800b2f80, vfn 0x8a8 of CRenderDeviceVulkan 1805765c8):
0 depth test, 1 depth write, 2-4 depth func, 5 reverse-Z swap of it (LESS <-> GREATER, LEQUAL <-> GEQUAL when the
device is reverse-Z: vfn 0x540); 16-18 front func, 19 its swap; 20-22 back func, 23 its swap; 24 stencil enable;
25-27 front fail, 28-30 front depth fail, 32-34 front pass; 35-37 back fail, 38-40 back depth fail, 41-43 back pass;
byte 6 read mask, byte 7 write mask. The enums are Vulkan's (an identity table at 180576498). VRF's "version 71" table
has the front pass at 31-33 and the back ops one bit early: the backend reads 32-34, 35-37, 38-40, 41-43, matching
the word-sized bitfield writes the client compiles.

- Pass 1: the prepass shader's depth (test, write, LEQUAL) + stencil enabled, func ALWAYS (both faces), fail REPLACE,
  depth fail KEEP, pass REPLACE, read / write mask 3, reference 3: every fragment that survives the discard and the
  depth test writes stencil 3.
- Pass 2: depth test + write, func EQUAL; stencil enabled, EQUAL (both faces), ops KEEP, read mask 3, write mask 0,
  reference 3: it shades only where pass 1 left its depth and its stencil.

What the stencil's bits 0-1 hold before pass 1 doesn't change the result: pass 1 writes 3 wherever pass 2 can pass
the depth test (pass 2 needs depth EQUAL to a pass 1 fragment), so other values only matter where pass 2's depth
happens to equal the world's. The only other client override near it is the "Not Depth Pre-passed" layer's
(FUN_1811d10e0: NOT_EQUAL, ref 3, read mask 1, write mask 2, pass REPLACE). Ours: three's stencil on both materials
(body-legs.js); the HDR target has a stencil buffer (render.js) and scenecopy.js copies its depth into a
DEPTH24_STENCIL8 texture to match.

### The objects

FUN_180c9d440 (the pawn's per-frame scene update) walks the pawn and every entity attached to it (FUN_18021a2c0,
FUN_180c7ede0) and sets bit 49 on each scene object, and bit 50 when in the legs view unless the entity's +0x56a is
set (FUN_180b00410); +0x56a is written only by C_CS2HudModelArms / C_CS2HudModelWeapon (vfn 0x30: 1810d1750,
1810d1950, the viewmodel) and copied to their children. So the whole pawn, its arms and hands included, and its
attachments go through both passes. The world weapon is one, but csgo_weapon has no FirstpersonLegsPrepass mode
(its modes: Depth, CsgoForward, the tools'), so pass 1 skips it and pass 2's EQUAL tests never pass: it never shows
(our first-person body hides it: body.js). cl_firstperson_legs itself only gates the pawn's ShouldDraw in first person
(FUN_180c95630).

## The fade (the pawn's scene attributes, FUN_180c9d440)

FirstpersonLegsFade (attribute hash 0xafd69318, MurmurHash2 of the lower-case name, seed 0x31415926) is written on the
pawn's scene objects: for the local player in the legs view (vfn 0x4e8 and FUN_180ca1830), 38 + 12 clamp((fz + 0.85) /
-0.0999999642, 0, 1) with fz the normalised view forward's z (180c9d7c9 ..); 0 otherwise, and 0 for objects
FUN_180b00410 picks. FirstPersonLegsDisableDistortion (0x3f90408f) is set only on another view (1811c8277).

## The vertex stage (both passes; csgo_character's is the same)

When the fade > 0 and distortion isn't disabled: f = pow(saturate((posOs.z + 1) x 0.0125) x 0.5 x pow(saturate(-fwd.z),
2), 1.5); clip.xy x= 1 + 5f; clip.y -= 200f; clip.z -= 40f; the normal + (0, 0, 0.5) sign(f), renormalised; y flipped
for Vulkan last. posOs: the posed model-space position (characters are skinned before this stage).

## The prepass's pixel shader

    s = smoothstep(fade - 35, fade, |eye - worldPos|) x step(0.8, normalize(posOs - (0, 0, 55)) . (0, 0, -1))
    discard if fma(s x 3, 2, -1.5) + texelFetch(g_tBlueNoise, ivec2(fragCoord) & mask).y < 0

g_tBlueNoise is core's `textures/dev/blue_noise_256.vtex` (RGBA8888, 256 x 256, one mip; bound with hash 0x88243422 at
1811c9bba); mask = its size - 1 (1811ffe94: (255, 255)). fragCoord rows run from the top (Vulkan). worldPos is the
skinned position before the warp (the VS passes it relative to the per-view origin and the PS adds it back).

Fragments nearer the eye than fade - 35, or outside the 37-degree cone under the chest point (0, 0, 55), never write
depth, so pass 2 never shades them: the chest, shoulders, head and upper arms. Between fade - 35 and fade the blue
noise dithers the edge.

## The hands

Nothing takes the hands out of the passes (above): what shows of them is the prepass rule on where the pose puts them.
The pose's last tasks are CS2's: the Aim IK (aim-ik.md, bit for bit) and Snap Weapon (snap-cs.js: wpn back on hand_R,
hand_L back on wpnHand_L; on a standing pose it moves the left hand by ~3e-5 since the Aim IK already put it there).
The aim input is CS2's: FUN_180ae02f0 makes aim_angle_pitch / _yaw from AngleQuaternion(movement services +0x3d8,
+0x3d4, 0) against the pawn's rotation, the eye angles relative to the body yaw (params.js). Standing at 85°: P90
hand_R 22.1, hand_L 26.9 units from the eye; AK-47 17.2 / 29.1; Deagle 24.9 / 25.4. With the fade at 50 the blue
noise keeps none of a fragment under 21.2 units and all of it past 26.4 (6 smoothstep - 1.5 + noise >= 0), so a hand
in that band shows dithered, as CS2 draws it for that pose.

## Left

- The pose's own inputs that aren't checked against the DLL: the graph runtime's state machine transitions, selectors
  and value nodes (anim-graph.md "Left"). Snap Weapon is built from checked transforms in the disassembly's order,
  not run against the DLL as a whole.
- Snap Weapon's modes 2 / 3 (weapon_molotov's lighter, weapon_knife_push) pose the weapon's own secondary skeleton,
  which isn't posed here.
