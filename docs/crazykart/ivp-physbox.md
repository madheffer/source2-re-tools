# ze_crazykart's item physboxes, thruster frames, template placement

CS:GO legacy server.dll md5 8048019154549052cb6dc057b76f6a85 (`/csgo_server_legacy.dll`) and vphysics.dll md5
d97cf2194594d7545427cdabc7376db4 (`/csgo_vphysics_legacy.dll`). Map: ze_crazykart_v4's greenshell.nut.

The items (green and red shell, banana, star, mushroom, bomb, bombz, repair: one func_physbox each, made by their
templates when a kart uses one) run on the round's IVP world as the karts do. The boss's 16 boss_hurter and the two vote
buttons are parented physboxes that follow their parent: no body.

## Functions

| Address | Module | What |
|---|---|---|
| 0x10320ed0 | server | CEntityFactory<CPhysBox> slot 0 (vtable 0x108ae3bc): allocates 0x52c, runs the ctor |
| 0x10321160 | server | CPhysBox ctor (vtable 0x108acf58; no `.?AVCPhysBox@@` RTTI name) |
| 0x1031ca00 | server | CPhysBox::Spawn (slot 25) |
| 0x1028b440 | server | (Spawn: after the cvar-scaled health fields) |
| 0x1020a440 | server | SetCollisionGroup |
| 0x10234040 | server | SetSolid |
| 0x1031ce60 | server | CPhysBox::CreateVPhysics (slot 154 = 0x268 / 4) |
| 0x1031a000 | server | PhysModelParseSolid (model index, solid -1) |
| 0x100338c0 | vphysics | ParseSolid |
| 0x102f8000 | server | lookup of the entity's model (+0xdc) in a 32-byte-entry table (0x10a4c5fc, count 0x10a4c608) |
| 0x102f7de0 | server | PhysSolidOverride (overridescript) |
| 0x101d38d0 / 0x10059d70 | server | override handler vtable 0x108a817c slot 0 / slot 1 SetDefaults (a bare `ret 4`) |
| 0x1031cd80 | server | thin-model damping fix (modelinfo slot 0x5c bounds) |
| 0x102082c0 | server | VPhysicsInitNormal (GetSolid, GetSolidFlags, createAsleep 1, &solid) -> PhysModelCreate |
| 0x102ee570 | server | CPhysForce ActivateForce |
| 0x102ee940 | server | CPhysThruster::OnActivate (vtable 0x108a4d40 slot 201 = +0x324; edi attached entity, esi thruster) |
| 0x101fd3d0 | server | CalcAbsolutePosition |
| 0x101fe600 | server | SetLocalAngles |
| 0x1069bf80 | server | AngleMatrix |
| 0x1069b0d0 | server | MatrixInvert |
| 0x1069b500 | server | ConcatTransforms (SSE, out pointer a stack argument, plain `ret`) |
| 0x1069af90 | server | MatrixAngles |
| 0x10206080 | server | ScriptSetForward (SetForwardVector; descriptor filled at 0x101f5bb0, binding thunk 0x10203990) |
| 0x1069bb10 | server | VectorAngles |
| 0x101cb0c0 | server | fpatan leaf |
| 0x10347270 | server | CPointTemplate::AddTemplate (this template, edi member, at map load) |
| 0x103a8e60 | server | Templates_Add ("failed to add template" Msg on -1) |
| 0x1069f9d0 | server | VMatrix::SetupMatrixOrgAngles (thiscall this, origin, angles; `ret 8`) |
| 0x1069fb70 | server | VMatrix::Identity |
| 0x1069fbe0 | server | MatrixMultiply (ecx a, edx b, out on the stack, plain `ret`) |
| 0x103482a0 | server | add to m_hTemplates |
| 0x10347630 | server | CreateInstance (origin*, angles*, entity list) |
| 0x102da170 | server | create an entity from its map data |
| 0x101fd960 / 0x101fdcd0 | server | SetAbsOrigin / SetAbsAngles |
| 0x10267350 | server | env_entity_maker SpawnEntity |
| 0x10267270 | server | find the template ("failed to find template") |
| 0x102671e0 | server | ForceSpawn (vec3_invalid) |
| 0x10267a20 | server | ForceSpawnAtEntityOrigin (named entity's +0x1dc, +0x1e8) |
| 0x10267ac0 / 0x10268100 | server | other named-entity forms |
| 0x10267bc0 | server | script SpawnEntityAtLocation(origin, angles) |

## Fields

| Offset | Field |
|---|---|
| CPhysBox +0x22c | from +0x230 |
| CPhysBox +0x31c | spawnflags |
| CPhysBox +0x440 | damagetype |
| CPhysBox +0x444 | massscale |
| CPhysBox +0x448 | overridescript |
| CPhysBox +0x460 | notsolid |
| entity +0xd4 | flags (0x40000 spawnflag sets \| 0x200000; 0x800 frame dirty) |
| entity +0xdc | model |
| entity +0x194 | frame (matrix3x4) |
| entity +0x1dc / +0x1e8 | abs origin / abs angles |
| entity +0x2e8 | angles (AngleMatrix input) |
| thruster +0x3e0..+0x3e8 | local origin |
| point_template +0x3e4 | m_hTemplates |
| template_t (68 bytes) | index, then the VMatrix matEntityToTemplate |
| solid_t +0x400 | surfaceprop |
| solid_t +0x60c | index (atoi) |
| solid_t +0x618 / +0x61c / +0x620 / +0x624 | mass / inertia / damping / rotdamping |
| solid_t +0x634 / +0x638 / +0x63c | volume / drag / enableCollisions |

## Constants

| Value | What |
|---|---|
| 0x4000 | spawnflag: SetCollisionGroup(1) (DEBRIS) |
| 0x1000 | spawnflag clear: Wake (slot 24) |
| 0x8000 | spawnflag: EnableMotion(false) (slot 15) (also a damage / force to enable motion > 0) |
| 8416257 = 0x806c01 | every item's spawnflags; the shells' 8449025 = 0x80ec01 (adds 0x8000) |
| 6 | SOLID_VPHYSICS |
| 9 | thin ratio: longest extent / length of the other two (longest zeroed) above it -> damping below 1 becomes 1 |
| 0x3c8efa35 | deg -> rad (mulss) |
| 0x42652ee1 | rad -> deg (mulss) |
| 0x3a83126f | MatrixAngles' xy threshold |
| 0x109732a0 | mask {0, 0, 0, ~0} |
| 0x10989be0 | 1/pi (f64) |
| 0x1098a314 | 360 |
| 0x10a669b8 | vec3_invalid |
| brush 310 mass 115.057861 / brush 308 mass 201.670349 | green shell / banana (`surfaceprop "default"`, a volume); massscale 0 on every item |
| `damping,10,rotdamping,10` / `rotdamping,10` | overridescript: shells / star |

## CPhysBox::Spawn 0x1031ca00

1. Cvar-scaled health fields, 0x1028b440, the model (slot 0x68), +0x22c from +0x230.
2. Spawnflags 0x4000 -> SetCollisionGroup(1); 0x40000 -> +0xd4 |= 0x200000. SetSolid(6). `notsolid` -> FSOLID_NOT_SOLID. CreateVPhysics (slot 154).
3. Every item is group 1: the game rules never let it collide with a kart (group 2) or another item (ivp-pileup.md 8).

## CPhysBox::CreateVPhysics 0x1031ce60

1. PhysModelParseSolid 0x1031a000: the model's vcollide key text, its "solid" block over g_PhysDefaultObjectParams (mass 1, inertia 1, damping 0.1, rotdamping 0.1, rotInertiaLimit 0.05, drag 1). ParseSolid 0x100338c0 keys: index, name, parent, surfaceprop, mass, massCenterOverride ("%f %f %f"), inertia, damping, rotdamping, volume, drag; anything else to the handler.
2. massscale > 0: mass x massscale, unclamped.
3. 0x102f8000(&solid).
4. PhysSolidOverride 0x102f7de0: `solid { ` + each comma-separated token quoted + `}`, parsed by the text key parser (collision slot 39), ParseSolid with a handler whose SetDefaults does nothing: only the given keys change; enableCollisions (+0x63c) saved and put back.
5. 0x1031cd80: the thin-model damping rule (no item is that thin).
6. VPhysicsInitNormal 0x102082c0 -> PhysModelCreate: CreatePolyObject (env slot 7) with the surfaceprop's index, created asleep.
7. damagetype 1: gameflags | 1.
8. Spawnflag 0x1000 clear: Wake. 0x8000: EnableMotion(false).

## A shell's drive (greenshell.nut)

A shell carries a forward phys_thruster (spawnflags 50: 0x2 linear, 0x10 force x mass, 0x20 no local origin; force
2500), a down one (50, force 1000, angles 90 0 0) and a phys_keepupright (limit 1000), attached to its physbox. Start:
1. Down thruster: its force, Activate, 0.01 s on.
2. EnableMotion on the physbox (spawned pinned by 0x8000).
3. Forward thruster aimed (SetForwardVector), its force, Activate 0.01 s on.

Its 0.05 s Tick toggles the down thruster (pressDown's trace); a bounce re-aims the forward one: Deactivate, a new
forward, Activate 0.01 s on.

## Thruster frame

- CPhysForce::Activate finds attach1, calls OnActivate (slot 201); with spawnflags & 1 then ActivateForce 0x102ee570. OnActivate runs once, at Activate.
- OnActivate 0x102ee940:
  1. Frame dirty (+0xd4 bit 0x800): CalcAbsolutePosition 0x101fd3d0 (AngleMatrix of +0x2e8 into +0x194, origin as the translation column).
  2. MatrixInvert(body +0x194, inv), ConcatTransforms(inv, thruster +0x194, m).
  3. Local origin (+0x3e0..+0x3e8) = m's translation column.
  4. Spawnflags & 8: MatrixAngles(m), SetLocalAngles 0x101fe600 (body-relative angles).
  5. Spawnflags & 0x20: local origin = 0.
- AngleMatrix 0x1069bf80: each angle x 0x3c8efa35 (mulss), then `fld dword; fsincos; fstp dword` (cos, sin), order yaw, pitch, roll.
  - `m00 cp cy`, `m01 (sr sp) cy - cr sy`, `m02 (cr sp) cy + sr sy`
  - `m10 cp sy`, `m11 (sr sp) sy + cr cy`, `m12 (cr sp) sy - sr cy`
  - `m20 -sp`, `m21 sr cp`, `m22 cr cp`; translation 0.
- MatrixInvert 0x1069b0d0: rotation transposed (in place if the same); `t[i] = -((r[i][1] ty + r[i][0] tx) + r[i][2] tz)`, r the transposed rows.
- ConcatTransforms 0x1069b500, by rows: `out[i] = ((a[i][2] b[2] + a[i][1] b[1]) + a[i][0] b[0]) + (a[i] & {0, 0, 0, ~0})` (mask 0x109732a0). The rotation lanes add +0.0, so -0.0 comes out +0.0.
- MatrixAngles 0x1069af90: `xy = sqrtss(m10^2 + m00^2)`; xy > 0x3a83126f: yaw `fpatan(m10, m00)`, pitch `fpatan(-m20, xy)`, roll `fpatan(m21, m22)`; else yaw `fpatan(-m01, m11)`, pitch the same, roll 0. Each arctangent stored to f32, then x 0x42652ee1 (mulss).
- ScriptSetForward 0x10206080: VectorAngles, then Teleport (vtable +0x1c8) with (null, &angles, null, true). On an unparented thruster these are its local angles (body-relative under 0x8).
- VectorAngles 0x1069bb10: y and x both 0 (ucomiss; NaN takes the general path): (z > 0 ? 270 : 90, 0, 0). Else `yaw = f32((f64)(fpatan(y, x) x 180f) x 1/pi)` (1/pi f64 0x10989be0, fpatan leaf 0x101cb0c0); + 360 (0x1098a314) below 0. Pitch the same from `fpatan(-z, sqrtss(x^2 + y^2))`; roll 0.

## Template placement (CPointTemplate)

VMatrix (4x4) code, not section "Thruster frame"'s matrix3x4.

AddTemplate 0x10347270:
1. Templates_Add 0x103a8e60.
2. `T = SetupMatrixOrgAngles(template +0x1dc, +0x1e8)`.
3. Inline InverseTR (0x10347307..0x10347443): rotation transposed; translation negated first, then `i[r][3] = ((t[1][r] (-ty) + t[0][r] (-tx)) + t[2][r] (-tz))` (a zero sum is +0.0, where MatrixInvert's -(sum) gives -0.0); last row 0 0 0 1.
4. `E = SetupMatrixOrgAngles(member's abs origin, angles)`.
5. `matEntityToTemplate = MatrixMultiply(inverse, E)`, stored with the index in a template_t, added to +0x3e4 by 0x103482a0.

- SetupMatrixOrgAngles 0x1069f9d0: rotation exactly AngleMatrix's code (x87 fsincos order yaw, pitch, roll; same products), origin the fourth column, last row 0 0 0 1.
- MatrixMultiply 0x1069fbe0: copies an input that aliases the out pointer; every element of all four rows `out[i][j] = ((a[i][0] b[0][j] + a[i][1] b[1][j]) + a[i][2] b[2][j]) + a[i][3] b[3][j]`.

CreateInstance 0x10347630:
- Empty m_hTemplates: "CreateInstance called on a point_template that has no templates".
- Per template entity, after 0x102da170: `N = SetupMatrixOrgAngles(spawn origin, angles)`; `W = MatrixMultiply(N, matEntityToTemplate)`; origin = W's translation; angles = MatrixAngles 0x1069af90 of W's first three rows (a VMatrix's rows have the matrix3x4 stride); SetAbsOrigin 0x101fd960, then SetAbsAngles 0x101fdcd0.

env_entity_maker SpawnEntity 0x10267350:
- Template by 0x10267270; spawn pose the maker's +0x1dc / +0x1e8, or the passed origin and angles when the origin isn't vec3_invalid; then CreateInstance.
- What follows (m_vecEntityMins / maxs bookkeeping, the spawnflag-1 think, the post-spawn speed and direction: velocity only) doesn't move the spawned entities.

## Unread

- CreateVPhysics steps 3 (0x102f8000's table: what it holds, who fills it), 5 and 7; a surfaceprop other than "default".
- A parented template member's placement (AddTemplate reads its abs origin through the parent): 58 of the map's members, none a body or a part.
- UTIL_StringToFloatArray's own parse (the SDK's atof of each token here).
