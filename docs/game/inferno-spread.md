# The inferno's spread on the server: CInferno's think and CreateFire (server_20261105, traced 2026-11-21, session "nade-players")

What our server/cs2web/grenades/inferno.js still stands in for (its header's STAND-INS): where a molotov's /
incendiary's flames go, when, and how long each lives. This is the server's CInferno (vtable 0x1817be778); the
client's drawing is inferno-client.md. Unread parts are marked UNREAD.

## Cvars (value pointers read by the code; defaults from their registrations, cvardump.py)

| value ptr | name | default |
|---|---|---|
| 0x181fa8c10 | inferno_spawn_angle ("Angular change from parent") | 45 (grenades.md) |
| 0x181fa8d40 | inferno_max_trace_per_tick | 16 (int) |
| 0x181fa8d10 | inferno_child_spawn_max_depth | 4 |
| 0x181fa8ca0 | inferno_max_range | 150 |
| 0x181fa8cb0 | inferno_max_range_ct ("... for an incendiary") | UNREAD default |
| 0x181fa8df0 | inferno_ct_experiment ("enable ct incendiary experiment") | UNREAD (0 taken) |
| 0x181fa8d50 | inferno_forward_reduction_factor | 0.9 |
| 0x181fa8ce0 | inferno_velocity_decay_factor | 0.2 |
| 0x181fa8cb8 / 0x181fa8cc8 | vfn 0x8a8 180349150: type 0 (+0x1194, the molotov) / else; one is inferno_velocity_factor (0.003): UNREAD which, and the other's name |
| 0x181fa8c48 / 0x181fa8c38 | vfn 0x898 180348ba0 (the flame lifetime): type 0 / else: inferno_flame_lifetime 7 / _incendiary 5.5 (taken: names UNREAD) |
| 0x181fa8bd0 | inferno_per_flame_spawn_duration | 3 |
| 0x181fa8be0 | inferno_initial_spawn_interval | 0.02 |
| 0x181fa8bf0 | inferno_child_spawn_interval_multiplier | 0.1 |
| 0x181fa8c00 | inferno_max_child_spawn_interval | 0.5 |
| 0x181fa8c70 | inferno_debug (only debug overlays) | 0 |

## A fire's record (0x88 bytes, made by CreateFire)

+0x00 position, +0x0c the position + (0, 0, 40) (+0x14 = z + 40), +0x18 the burn normal, +0x24 burning (1), +0x28
depth (CreateFire's last argument), +0x2c spawns owed (0), +0x30 the parent fire (null for the first), +0x38 the
spawn-duration timer, +0x50 the spawn-interval timer, +0x68 the life timer (each a { start, duration, end }: +0 the
start, +8 the duration, +0xc the end; 180349010 reads the life left as clamp((end - now) / duration, 0, 1)), +0x80 0.
The inferno keeps up to 64 (min(+0x1434 the max flames, 0x40)) in +0x11a8 (pointers, count at +0x1190).

## CreateFire 180345dc0(inferno, pos, normal, parent, depth) -> 0 made / 1 full / 2 / 3 / 5

- Full (count >= min(max flames, 64)) -> 1.
- 18034cf40(inferno, pos) -> 2 (UNREAD: taken as "a fire already there"; the think doesn't slow the push for it);
  18034cc30 (in a smoke: the smoke rule, grenades.md) -> 3 and +0x11a1 = 1; 18034cd60 -> 5 (UNREAD).
- The life timer: vfn 0x898 (the flame lifetime) less the inferno's own elapsed time (its timer +0x1420, 1802ca490)
  when that timer runs, else the whole lifetime: **every flame dies at the inferno's start + the lifetime** (no
  per-flame spread: ours adds +-10 %).
- No parent: the spawn-duration timer = inferno_per_flame_spawn_duration, the interval = inferno_initial_spawn_interval.
  A child: the duration = the parent's duration timer's remaining (180348690(parent +0x38)), the interval =
  min(remaining(parent +0x50) x inferno_child_spawn_interval_multiplier, inferno_max_child_spawn_interval).
- Networked: m_firePositions (+0x850 + 12 i), m_fireParentPositions (+0xb50: the parent's, else its own),
  m_bFireIsBurning (+0xe50 bit), m_BurnNormal (+0xe90), the count; 180350120 (UNREAD: the extent); the
  Inferno.Fire.Ignite sound at the position (only while +0x1194 is 0 or 1).

## The think 180352350(inferno, velocity*)

1. Skips until its timer (+0x1458 / +0x1464) is due; +0x1438 (think count) + 1; vfn 0x8b8; the timer restarted.
2. Every burning fire whose life and spawn-duration timers run and whose interval timer is due: the interval timer
   restarted (180338b80) and +0x2c (spawns owed) + 1.
3. **The seed**: d = (+0x1408 / 10 - +0x1414 / 10, +0x140c / 10 - +0x1418 / 10, +0x1410 / 10 - +0x141c / 10) (the
   origin less a second point, both / 10: UNREAD which fields), n = normalize(d) (zero when |d| == 0), a = (int)(think
   count x |d|); then a MurmurHash3-style mix (k x 0xcc9e2d51, rotl 15, x 0x1b873593, h = rotl(h ^ k, 13) x 5 +
   0xe6546b64; 0x417 first) of a, (int)(n.x x 9737333), (int)(n.y x 9737333), (int)(n.z x 9737333), (int)(+0x13fc x
   0.1), (int)(+0x1400 x 0.1), (int)(+0x1404 x 0.1), then the finaliser (^ 0x1c, x 0x85ebca6b, >> 13, x 0xc2b2ae35,
   >> 16) -> **the global uniform random stream's SetSeed** (PTR_DAT_181e328d8). The constants as the decompiler
   wrote them; the port must take them from the disassembly (180352680..).
4. The budget = inferno_max_trace_per_tick; from flame index +0x1430 + 1, round robin over the fires while the budget
   lasts and the fires aren't full: a fire owing a spawn, burning, its life timer running and depth + 1 <
   inferno_child_spawn_max_depth: owed - 1, **start = RandomInt(0, 3)** (UNREAD: whether `start` is used: the loop
   below runs i = 0..3), then up to 4 tries:
   - **The direction**: no parent: RandomFloat(0, pi/2), dir = (cos, sin, 0) (the V_sinf / V_cosf imports; UNREAD:
     the angle argument's use as the decompiler hid it). A parent: VectorAngles(normalize(fire - parent))
     (1814722c0), the yaw - spawn angle on try 2, + spawn angle on try 3, + RandomFloat(-spawn angle, +spawn angle),
     AngleVectors (181470980) -> dir.
   - **The push**: v = dir + velocity x lifeLeft(fire) x powf(inferno_velocity_decay_factor, depth) x vfn 0x8a8;
     projected into the fire's ground plane: n x ((v x n)) with n the fire's normal (+0x18) (the two cross products
     at 180352ab9..).
   - **The step**: r = (max range x 0.5) - RandomFloat(0, 20) (max range: inferno_max_range_ct with the experiment
     on and an incendiary, else inferno_max_range): **55..75 u at 150**; p = fire + normalize(projected) x r
     (normalize's zero case (1, 0, 0)).
   - Farther than the max range from the origin (+0x1408): pulled back onto that sphere.
   - **The ground**: a line from p + (0, 0, 50) to (p.x, p.y, fire.z - 200) (180341300 with filter vtable
     0x1817bfb38: interacts-with 0x1001, exclude 0x40000, group 3, flags (x & 0xc9) | 0x49; UNREAD: the exact
     fields), budget - 1. No hit: the push velocity x inferno_forward_reduction_factor, next try.
   - Hit at h (its normal kept): a line from the fire + (0, 0, 30) to h + (0, 0, 30), budget - 2 in all; blocked
     (fraction < 1): the reduction, next try. Clear: not in a smoke -> **CreateFire(h, normal, fire, depth + 1)**;
     0 or 1 -> this fire's spawn is done (break); 3 or 5 -> the reduction; 2 -> next try.
5. +0x1430 = the last index + 1.

## Left for the port

UNREAD: the think's schedule (who calls it, how often: 18035xxxx; the start 1803536c0 calls CreateFire for the
first fire), 18034cf40 / 18034cd60, the seed's second point and velocity fields, vfn 0x8b8 (180348bd0), the flames'
death (+0x24 cleared: where), the burn volume (the damage's touch test: ours is a 30 u cylinder stand-in), the trace
filter's fields, the RandomInt's use. The global stream is tier0's (the server's one: core/global-random.js); its
SetSeed must be ported with it.
