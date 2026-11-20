# ze_crazykart's item physboxes on IVP (CS:GO legacy server.dll / vphysics.dll, read 2026-11-18)

The items (green and red shell, banana, star, mushroom, bomb, bombz, repair: one func_physbox each, made by their
templates when a kart uses one) run on the round's IVP world, as the karts do (csgo/physics/ivp-body.js IvpKartBody with
`physbox`, sim/src/ivp/kart_world.rs add_physbox, csgo/physics/ivp-world.js addPhysbox, ABI ze_kart_physbox). The boss's 16
boss_hurter and the two vote buttons are parented physboxes, which follow their parent, so they make no body.

## 1. CPhysBox::Spawn (vtable 0x108acf58 slot 25, 0x1031ca00)

- The class: func_physbox's factory (CEntityFactory<CPhysBox>, vtable 0x108ae3bc slot 0 0x10320ed0) allocates 0x52c
  bytes and runs the ctor 0x10321160 (vtable 0x108acf58). There is no `.?AVCPhysBox@@` RTTI name.
- The cvar-scaled health fields, 0x1028b440, then the model (slot 0x68) and +0x22c from +0x230.
- Spawnflags +0x31c: **0x4000 -> SetCollisionGroup(1)** (DEBRIS, 0x1020a440). 0x40000 sets +0xd4 |= 0x200000. Then
  SetSolid(6) (SOLID_VPHYSICS, 0x10234040). `notsolid` (+0x460) gives FSOLID_NOT_SOLID. Then CreateVPhysics (slot
  0x268 / 4 = 154).
- Every item's spawnflags have 0x4000 (8416257 = 0x806c01; the shells' 8449025 = 0x80ec01 add 0x8000). So every item
  is group 1, and the game rules never let it collide with a kart (group 2) or another item (ivp-pileup.md 8).

## 2. CPhysBox::CreateVPhysics (slot 154, 0x1031ce60)

1. **PhysModelParseSolid** (0x1031a000, the model index, solid -1): the model's vcollide key text, its "solid"
   block parsed over g_PhysDefaultObjectParams (mass 1, inertia 1, damping 0.1, rotdamping 0.1, rotInertiaLimit 0.05,
   drag 1). The keys are read by vphysics' ParseSolid 0x100338c0: index (+0x60c, atoi), name, parent, surfaceprop
   (+0x400), mass (+0x618), massCenterOverride ("%f %f %f"), inertia (+0x61c), damping (+0x620), rotdamping (+0x624),
   volume (+0x634), drag (+0x638); anything else goes to the handler. The item brushes carry `mass`, `surfaceprop
   "default"` and `volume`: brush 310 (green shell) mass 115.057861, brush 308 (banana) 201.670349.
2. `massscale` (+0x444) > 0: mass x massscale, unclamped. Every item has 0.
3. 0x102f8000(&solid): a lookup of the entity's model (+0xdc) in a 32-byte-entry table (0x10a4c5fc, count
   0x10a4c608). TODO(trace): what the table holds and who fills it. The port doesn't run it.
4. **PhysSolidOverride 0x102f7de0** (overridescript +0x448): `solid { ` + each comma-separated token quoted + `}`,
   parsed by the text key parser (collision slot 39), ParseSolid with a handler whose SetDefaults does nothing
   (vtable 0x108a817c: slot 0 0x101d38d0, slot 1 0x10059d70 a bare `ret 4`). So only the keys given change;
   enableCollisions (+0x63c) is saved and put back. The shells: `damping,10,rotdamping,10`; the star: `rotdamping,10`.
5. 0x1031cd80: the model's bounds (modelinfo slot 0x5c). When the longest extent / the length of the other two (the
   longest zeroed) is above 9, a damping below 1 becomes 1. No item is that thin. TODO(trace): not ported.
6. **VPhysicsInitNormal 0x102082c0** (GetSolid, GetSolidFlags, createAsleep 1, &solid) -> PhysModelCreate: a
   CreatePolyObject (env slot 7) with the surfaceprop's index, created asleep.
7. `damagetype` (+0x440) 1: gameflags | 1.
8. Spawnflag **0x1000 clear: Wake** (slot 24). **0x8000** (or a damage / force to enable motion > 0): EnableMotion(false)
   (slot 15).

## 3. The port

- sim/src/ivp/solid_keys.rs: ParseFile / ParseKeyvalue in Rust (as tools/kart-ivp-surfaces.mjs ports them), ParseSolid's
  keys over DEFAULT's numbers, PhysSolidOverride.
- KartWorld::add_physbox runs steps 1, 2, 4, 6 and 8 in add_kart's order. Only the "default" surfaceprop is known
  there, and a massCenterOverride is refused.
- The game (csgo/maps/ze_crazykart/install.js physboxBody): an unparented func_physbox of a brush model becomes an IvpKartBody in physbox
  mode: its thrusters, keepupright, Wake / Sleep / EnableMotion inputs, teleports and DestroyObject as the kart's;
  csgo/physics/standin-body.js's stand-in after a trap.

## 4. Checked

- The oracle's `physbox` line (Physbox.cs: the same steps through the DLL, sharing Shadows.ParseModel with the movers).
- scenarios/physbox-world.txt: a banana and a green shell on the map's world with the kart, the kart driving through
  the banana and the shell thrown. 300 ticks of what the game reads, bit-identical in kart_world_check. ivp_check
  leaves physbox scenarios to kart_world_check.
- kart-map-test's items spawn on IVP (the shells pinned by 0x8000 until their scripts' EnableMotion), and the recorded
  round replays natively.
- The browser on ze_crazykart_v4, rounds 2-4: drift bad 0.

## 5. A shell's drive (checked 2026-11-18)

A shell carries a forward phys_thruster (spawnflags 50: 0x2 linear, 0x10 force x mass, 0x20 no local origin; force
2500), a down one (50, force 1000, angles 90 0 0) and a phys_keepupright (limit 1000), all attached to its physbox.
greenshell.nut's Start (csgo/maps/ze_crazykart/items.js GreenShell):
1. the down thruster gets its force and an Activate 0.01 s on;
2. EnableMotion on the physbox, which spawned pinned by 0x8000;
3. the forward thruster is aimed (SetForwardVector), gets its force and an Activate 0.01 s on.

Its 0.05 s Tick toggles the down thruster (pressDown's trace), and a bounce re-aims the forward one: Deactivate, a
new forward, then Activate 0.01 s on. The oracle's thrusters and uprights now take a body (`@<name>` on the
`thruster` / `upright` lines; their events act on that body). scenarios/shell-world.txt runs that sequence at fixed
ticks on the map's world with the kart in the shell's way: 240 ticks of what the game reads, bit-identical in
kart_world_check (its thrusters and uprights take the same `@`).

## 6. Left

- Steps 3, 5 and 7; a surfaceprop other than "default".
- A parented template member's placement (AddTemplate reads its abs origin through the parent): 58 of the map's
  members, none of them a body or a part; they keep CS2's placement.
- UTIL_StringToFloatArray's own parse (the SDK's atof of each token here).

## 7. A thruster's frame and SetForwardVector (2026-11-18, checked natively)

server.dll's own float math, ported in sim/src/math/csgo_mathlib.rs:

- **CPhysForce::Activate** finds attach1, then calls **OnActivate** (CPhysThruster vtable 0x108a4d40, slot 201 = +0x324).
  With spawnflags & 1 it then calls ActivateForce 0x102ee570. So OnActivate runs once, at the thruster's Activate.
- **OnActivate 0x102ee940** (edi = the attached entity, esi = the thruster):
  1. If a frame is dirty (+0xd4 bit 0x800), it is rebuilt by CalcAbsolutePosition 0x101fd3d0: AngleMatrix of the
     entity's angles (+0x2e8) into +0x194, then the origin as the translation column.
  2. MatrixInvert(body +0x194, inv), then ConcatTransforms(inv, thruster +0x194, m).
  3. The local origin (+0x3e0..+0x3e8) = m's translation column.
  4. With spawnflags & 8: MatrixAngles(m), then SetLocalAngles 0x101fe600, so the angles become body-relative.
  5. With spawnflags & 0x20: the local origin is set to 0.
- **AngleMatrix 0x1069bf80**:
  - Each angle x 0x3c8efa35 (mulss), then `fld dword; fsincos; fstp dword` (cos, sin). Order: yaw, pitch, roll.
  - m00 cp cy, m01 (sr sp) cy - cr sy, m02 (cr sp) cy + sr sy;
  - m10 cp sy, m11 (sr sp) sy + cr cy, m12 (cr sp) sy - sr cy;
  - m20 -sp, m21 sr cp, m22 cr cp; the translation is 0.
- **MatrixInvert 0x1069b0d0**:
  - The rotation is transposed (the input itself if in place).
  - t[i] = -((r[i][1] ty + r[i][0] tx) + r[i][2] tz), where r is the transposed rows.
- **ConcatTransforms 0x1069b500** (SSE, by rows):
  - out[i] = ((a[i][2] b[2] + a[i][1] b[1]) + a[i][0] b[0]) + (a[i] & {0, 0, 0, ~0}), with the mask at 0x109732a0.
  - The rotation lanes add +0.0, so a -0.0 comes out as +0.0.
  - The output pointer is a stack argument; plain `ret`.
- **MatrixAngles 0x1069af90**:
  - xy = sqrtss(m10^2 + m00^2).
  - If xy > 0x3a83126f: yaw fpatan(m10, m00), pitch fpatan(-m20, xy), roll fpatan(m21, m22).
  - Else: yaw fpatan(-m01, m11), pitch the same as above, roll 0.
  - Each arctangent is stored to f32, then x 0x42652ee1 (mulss).
- **ScriptSetForward 0x10206080** (SetForwardVector; its descriptor is filled at 0x101f5bb0, binding thunk
  0x10203990): VectorAngles, then Teleport (vtable +0x1c8) with (null, &angles, null, true). On an unparented
  thruster these are its local angles, body-relative under 0x8.
- **VectorAngles 0x1069bb10**:
  - When y and x are both 0 (ucomiss; a NaN takes the general path): (z > 0 ? 270 : 90, 0, 0).
  - Else yaw = f32((f64)(fpatan(y, x) x 180f) x 1/pi), where 1/pi is the f64 at 0x10989be0 and fpatan is the leaf
    0x101cb0c0. Add 360 (0x1098a314) when it is below 0.
  - Pitch is computed the same way from fpatan(-z, sqrtss(x^2 + y^2)); roll is 0.

**Checked**: rubikon/tests/KartOracle `--frame` maps server.dll with DONT_RESOLVE_DLL_REFERENCES (Frame.cs) and calls
each leaf through a register thunk. It also composes OnActivate's frame from the leaves in OnActivate's order.
sim/src/bin/csgo_frame_check.rs replays every case through the port. Results, all bit-identical (the arctangents
come from the DLL's own x87, so this checks math/x87.rs fpatan_dword too):

| Function | Cases |
|---|---|
| AngleMatrix | 22163 |
| MatrixInvert | 20000 |
| ConcatTransforms | 20000 |
| MatrixAngles | 40000 (gimbal cases included) |
| VectorAngles | 40009 |
| Thruster frame | 20000 (flags 58 / 28 / 50 / 59 / 8 / 0 / 0x28) |

**In the game**: csgo/physics/ivp-body.js's bindThruster (the parts bind in the tick they spawn) takes both entities' poses.
ze_csgo_thruster_frame gives the local origin and, under 0x8, the body-relative angles. thrusterForward uses
ze_csgo_vector_angles. csgo/physics/standin-body.js's stand-in keeps its doubles (it runs only without IVP).

## 8. A template's placement: CPointTemplate (2026-11-18, checked natively)

ze_crazykart_v4 is a CS:GO BSP, so its templates place their entities as CS:GO's CPointTemplate does. That uses
VMatrix (4x4) code, not the matrix3x4 code of section 7. Ported in sim/src/math/csgo_mathlib.rs.

### AddTemplate 0x10347270 (this = the point_template, edi = the member, at the map's load)

1. Templates_Add 0x103a8e60 (its "failed to add template" Msg on -1).
2. T = VMatrix::SetupMatrixOrgAngles 0x1069f9d0(the template's abs origin +0x1dc, abs angles +0x1e8).
3. Inline InverseTR (0x10347307..0x10347443):
   - The rotation is transposed.
   - The translation (tx, ty, tz) is negated first, then i[r][3] = ((t[1][r] (-ty) + t[0][r] (-tx)) + t[2][r] (-tz)).
     A zero sum comes out +0.0, where MatrixInvert's -(sum) gives -0.0.
   - The last row is 0 0 0 1.
4. E = SetupMatrixOrgAngles(the member's abs origin and angles).
5. matEntityToTemplate = MatrixMultiply 0x1069fbe0(inverse, E). It is stored with the index in a template_t (68 bytes:
   index, then the VMatrix) and added to m_hTemplates (+0x3e4) by 0x103482a0.

### The VMatrix helpers

- **SetupMatrixOrgAngles 0x1069f9d0**: thiscall (this, origin, angles), `ret 8`. Its rotation is AngleMatrix's code
  exactly (the x87 fsincos order yaw, pitch, roll; the same products), the origin is the fourth column, and the last
  row is 0 0 0 1. The function after it, 0x1069fb70, is VMatrix::Identity.
- **MatrixMultiply 0x1069fbe0** (ecx a, edx b, the out pointer on the stack, plain `ret`):
  - Copies an input that aliases the out pointer.
  - Every element of all four rows is out[i][j] = ((a[i][0] b[0][j] + a[i][1] b[1][j]) + a[i][2] b[2][j]) + a[i][3]
    b[3][j]. (tools/re/game/symss.py, a symbolic run of a listing, printed every element.)

### CreateInstance 0x10347630 (origin*, angles*, the entity list)

- "CreateInstance called on a point_template that has no templates" when m_hTemplates is empty.
- For each template entity, after it is created from its map data (0x102da170):
  1. N = SetupMatrixOrgAngles(the spawn's origin and angles).
  2. W = MatrixMultiply(N, matEntityToTemplate).
  3. Origin = W's translation; angles = MatrixAngles 0x1069af90 of W's first three rows (a VMatrix's rows have the
     matrix3x4 stride).
  4. SetAbsOrigin 0x101fd960, then SetAbsAngles 0x101fdcd0.

### env_entity_maker

- **SpawnEntity 0x10267350**:
  - Finds the template with 0x10267270 ("failed to find template").
  - The spawn pose is the maker's abs origin (+0x1dc) and abs angles (+0x1e8). When the passed origin isn't
    vec3_invalid (0x10a669b8), the passed origin and angles are used instead.
  - Then CreateInstance.
  - What follows CreateInstance (the m_vecEntityMins / maxs bookkeeping, the spawnflag-1 think, the post-spawn speed
    and direction, which only set a velocity) doesn't move the spawned entities.
- **The callers**:
  - ForceSpawn 0x102671e0 passes vec3_invalid.
  - ForceSpawnAtEntityOrigin 0x10267a20 passes the named entity's abs origin and abs angles (+0x1dc, +0x1e8).
  - 0x10267ac0 and 0x10268100 are the other named-entity forms.
  - 0x10267bc0 is the script's SpawnEntityAtLocation(origin, angles).

### The port, the bake and the check

- **In the game**:
  - The baker keeps each member's own place as the BSP wrote it, as `csgo_origin` / `csgo_angles`
    (bake/Source1/Entities.cs). The relative `origin` / `angles` stay for CS2's path.
  - On a CS:GO map, csgo/entities/template-place.js is engine.placeTemplate. engine.spawnTemplate asks it for each
    unparented member, and it calls ze_csgo_template_place (entity_to_template + template_place). The template's own
    keyvalues give its pose.
  - The IVP bodies take the entity's own angles at CreateVPhysics (csgo/physics/ivp-body.js spawnAngles), not a quaternion
    round trip.
- **Checked natively**: KartOracle `--frame` sections 7-10.
  - SetupMatrixOrgAngles and MatrixMultiply are called in the mapped server.dll.
  - The InverseTR block is copied out of the mapped DLL into a thunk that runs it on its own stack layout.
  - The whole placement is AddTemplate then CreateInstance, composed from those native pieces.
  - csgo_frame_check: SetupMatrixOrgAngles 20000, MatrixMultiply 20000, InverseTR 20000 and placement 20000 cases,
    all bit-identical. Sections 1-6 are unchanged.
  - csgo/entities/template-place-test.mjs: the map's 2048 member placements at four spawn poses agree with the bake's doubles to
    0.004 u and 1e-7 of rotation, which shows the inputs are the right ones.
