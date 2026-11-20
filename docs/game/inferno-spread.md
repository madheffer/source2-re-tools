# Inferno spread (server CInferno: think, CreateFire)

server_20261105. CInferno vtable 0x1817be778. The client's drawing: [inferno-client.md](inferno-client.md).

## Functions

| Address | Module | What |
|---|---|---|
| 180345dc0 | server | CreateFire(inferno, pos, normal, parent, depth) -> 0 made / 1 full / 2 / 3 / 5 |
| 18034cf40 | server | (inferno, pos) -> CreateFire 2 (taken as "a fire already there") |
| 18034cc30 | server | in a smoke -> CreateFire 3, +0x11a1 = 1 (smoke rule, grenades.md) |
| 18034cd60 | server | -> CreateFire 5 (unread) |
| 180349010 | server | life left: clamp((end - now) / duration, 0, 1) |
| 180348690 | server | timer remaining |
| 1802ca490 | server | the inferno's own elapsed time (timer +0x1420) |
| 180338b80 | server | restart a timer |
| 180350120 | server | after CreateFire (unread: the extent) |
| 180352350 | server | the think (inferno, velocity*) |
| 1803536c0 | server | the start: CreateFire for the first fire |
| 180349150 | server | vfn 0x8a8: velocity factor by type |
| 180348ba0 | server | vfn 0x898: flame lifetime by type |
| 180348bd0 | server | vfn 0x8b8 (unread) |
| 1814722c0 | server | VectorAngles |
| 181470980 | server | AngleVectors |
| 180341300 | server | ground trace (filter vtable 0x1817bfb38) |

## Fields

| Offset | Field |
|---|---|
| fire +0x00 | position |
| fire +0x0c | position + (0, 0, 40) (+0x14 = z + 40) |
| fire +0x18 | burn normal |
| fire +0x24 | burning (1) |
| fire +0x28 | depth |
| fire +0x2c | spawns owed (0) |
| fire +0x30 | parent fire (null for the first) |
| fire +0x38 | spawn-duration timer |
| fire +0x50 | spawn-interval timer |
| fire +0x68 | life timer |
| fire +0x80 | 0 |
| timer +0 / +8 / +0xc | start / duration / end |
| inferno +0x11a8 / +0x1190 | fire pointers / count (max min(+0x1434, 0x40)) |
| inferno +0x1434 | max flames |
| inferno +0x1194 | type (0 molotov) |
| inferno +0x11a1 | set when a fire fell in a smoke |
| inferno +0x1420 | inferno timer |
| inferno +0x1458 / +0x1464 | think timer |
| inferno +0x1438 | think count |
| inferno +0x1430 | round-robin flame index |
| inferno +0x1408 / +0x140c / +0x1410 | origin |
| inferno +0x1414 / +0x1418 / +0x141c | the seed's second point (unread which field) |
| inferno +0x13fc / +0x1400 / +0x1404 | seed inputs (unread which field) |
| inferno +0x850 + 12 i | m_firePositions |
| inferno +0xb50 | m_fireParentPositions (the parent's, else its own) |
| inferno +0xe50 | m_bFireIsBurning (bits) |
| inferno +0xe90 | m_BurnNormal |

## Constants

| Value ptr | Cvar | Default |
|---|---|---|
| 0x181fa8c10 | inferno_spawn_angle ("Angular change from parent") | 45 |
| 0x181fa8d40 | inferno_max_trace_per_tick | 16 (int) |
| 0x181fa8d10 | inferno_child_spawn_max_depth | 4 |
| 0x181fa8ca0 | inferno_max_range | 150 |
| 0x181fa8cb0 | inferno_max_range_ct ("... for an incendiary") | unread |
| 0x181fa8df0 | inferno_ct_experiment ("enable ct incendiary experiment") | unread (0 taken) |
| 0x181fa8d50 | inferno_forward_reduction_factor | 0.9 |
| 0x181fa8ce0 | inferno_velocity_decay_factor | 0.2 |
| 0x181fa8cb8 / 0x181fa8cc8 | vfn 0x8a8: type 0 / else; one is inferno_velocity_factor (0.003), which and the other's name unread | |
| 0x181fa8c48 / 0x181fa8c38 | vfn 0x898: type 0 / else: inferno_flame_lifetime 7 / _incendiary 5.5 (names taken) | |
| 0x181fa8bd0 | inferno_per_flame_spawn_duration | 3 |
| 0x181fa8be0 | inferno_initial_spawn_interval | 0.02 |
| 0x181fa8bf0 | inferno_child_spawn_interval_multiplier | 0.1 |
| 0x181fa8c00 | inferno_max_child_spawn_interval | 0.5 |
| 0x181fa8c70 | inferno_debug (overlays only) | 0 |

| Value | What |
|---|---|
| 0x88 | fire record size |
| 64 (0x40) | fires per inferno cap |
| PTR_DAT_181e328d8 | global uniform random stream (seeded by the think) |

## CreateFire (180345dc0)

1. count >= min(max flames, 64) -> 1. 18034cf40 -> 2; 18034cc30 -> 3; 18034cd60 -> 5.
2. Life timer: vfn 0x898 less the inferno's elapsed time (1802ca490) when that timer runs, else the whole lifetime: every flame dies at the inferno's start + the lifetime.
3. No parent: spawn duration = inferno_per_flame_spawn_duration, interval = inferno_initial_spawn_interval. Child: duration = 180348690(parent +0x38), interval = min(remaining(parent +0x50) x inferno_child_spawn_interval_multiplier, inferno_max_child_spawn_interval).
4. Networked fields set, the count; 180350120; `Inferno.Fire.Ignite` at the position (only while +0x1194 is 0 or 1).

## The think (180352350)

1. Skip until +0x1458 / +0x1464 is due; +0x1438 + 1; vfn 0x8b8; restart the timer.
2. Every burning fire whose life and spawn-duration timers run and whose interval timer is due: interval restarted (180338b80), +0x2c + 1.
3. Seed: `d = (+0x1408 / 10 - +0x1414 / 10, +0x140c / 10 - +0x1418 / 10, +0x1410 / 10 - +0x141c / 10)`, `n = normalize(d)` (zero when |d| == 0), `a = (int)(think count x |d|)`; MurmurHash3-style mix (`k x 0xcc9e2d51`, rotl 15, `x 0x1b873593`, `h = rotl(h ^ k, 13) x 5 + 0xe6546b64`; h starts 0x417) of a, `(int)(n.x x 9737333)`, `(int)(n.y x 9737333)`, `(int)(n.z x 9737333)`, `(int)(+0x13fc x 0.1)`, `(int)(+0x1400 x 0.1)`, `(int)(+0x1404 x 0.1)`; finaliser (`^ 0x1c`, `x 0x85ebca6b`, `>> 13`, `x 0xc2b2ae35`, `>> 16`) -> SetSeed of the global stream. Constants as the decompiler wrote them; take them from the disassembly (180352680..).
4. Budget = inferno_max_trace_per_tick; from flame index +0x1430 + 1, round robin while the budget lasts and not full: a fire owing a spawn, burning, life timer running and `depth + 1 < inferno_child_spawn_max_depth`: owed - 1, `start = RandomInt(0, 3)` (its use unread: the loop runs i = 0..3), then up to 4 tries:
   - Direction: no parent: `RandomFloat(0, pi/2)`, dir = (cos, sin, 0) (V_sinf / V_cosf; the angle's use unread). Parent: VectorAngles(normalize(fire - parent)); yaw - spawn angle on try 2, + spawn angle on try 3, + `RandomFloat(-spawn angle, +spawn angle)`; AngleVectors -> dir.
   - Push: `v = dir + velocity x lifeLeft(fire) x powf(inferno_velocity_decay_factor, depth) x vfn 0x8a8`; projected into the fire's ground plane: `n x ((v x n))`, n = fire +0x18 (the cross products at 180352ab9..).
   - Step: `r = (max range x 0.5) - RandomFloat(0, 20)` (max range: inferno_max_range_ct with the experiment on and an incendiary, else inferno_max_range): 55..75 u at 150; `p = fire + normalize(projected) x r` (zero case (1, 0, 0)).
   - Farther than the max range from the origin (+0x1408): pulled back onto that sphere.
   - Ground: line p + (0, 0, 50) to (p.x, p.y, fire.z - 200) (180341300: interacts-with 0x1001, exclude 0x40000, group 3, flags `(x & 0xc9) | 0x49`; exact fields unread), budget - 1. No hit: push velocity x inferno_forward_reduction_factor, next try.
   - Hit h (normal kept): line fire + (0, 0, 30) to h + (0, 0, 30), budget - 2 in all; blocked (fraction < 1): the reduction, next try. Clear and not in smoke: `CreateFire(h, normal, fire, depth + 1)`; 0 or 1 -> done (break); 3 or 5 -> the reduction; 2 -> next try.
5. +0x1430 = last index + 1.

## Unread

- The think's schedule (who calls it, how often: 18035xxxx).
- 18034cf40 / 18034cd60; 180350120.
- The seed's second point and velocity fields; vfn 0x8b8 (180348bd0).
- The flames' death (+0x24 cleared: where).
- The burn volume (the damage's touch test).
- The ground trace filter's fields; RandomInt's use.
- inferno_max_range_ct / inferno_ct_experiment defaults; which of 0x181fa8cb8 / 0x181fa8cc8 is inferno_velocity_factor.
