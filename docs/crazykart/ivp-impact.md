# CS:GO legacy IVP: the impact system and the kart on the ground, end to end (vphysics.dll, 32-bit, 2026-11-17)

**CS:GO legacy, not CS2** (ze_crazykart's karts, cs2web's docs/CRAZYKART.md). vphysics.dll md5 d97cf2194594d7545427cdabc7376db4,
Ghidra `/csgo_vphysics_legacy.dll`, capstone. The joint between collision detection (ivp-mindist.md: the mindist's time
event up to do_impact) and the contacts (ivp-contacts.md: the friction system, its solves, the impact solver
0x1008b0e0): everything a mindist's impact does, the friction system's life on the world, its controllers inside the
PSI, sleeping and waking on the ground. All SSE scalar single unless said; sums as the Rust keeps them. Ported in
sim/src/ivp/impact_sys.rs (the impact), friction_sys.rs (the friction system on the world), collide_events.rs (the
freeze), world.rs (World::psi_with, the unit's rebuild), core.rs (the stage-5 rot step), math/csgo_libm.rs (cosf,
asinf); checked by `ivp_check` in its ground mode (section 9).

## 1. do_impact 0x1008b020 (the mindist's vtable slot 8)

thiscall (mindist), from simulate_time_event 0x10095dd0 (ivp-mindist.md 9) when the recalculated length is below
coll_dists[selector] + mindist_change_force_dist, inside the time event (env+0xf0 the event's time, env+0x108 counted):
1. per synapse in the mindist's own order (objects at +0x28 / +0x44): an object with +0x44 == 8 has its original core's
   (object +0x98) unit revived (0x10071ef0(unit, env): each of the unit's cores (+0xe count, +0x10 list, last to first)
   with movement byte >= 8 through 0x10086b70, then a unit in state 8 (+0) moved from the sleeping list (env+8 +0x1a8)
   to the active list (+0x18), state 1). A static object's unit isn't in state 8 (the oracle's env rows: the box's units
   stay sleeping): nothing. 0x10086b70 runs each revived core's collision side as at a PSI's revival: the object's
   recheck (0x100778d0), then **0x10082ce0** (revive_friction.rs). That can make a contact with a dynamic partner
   outside any friction system, whose reference times (+0x150 / +0x158) become the event's time (lift-pinned: a
   sleeping kart hit by the climbing lift; ported 2026-11-18, ivp-pileup.md 7). It runs before the impact, on the
   contacts side the impact then reads.
2. env+0xa0 (the temporary memory) +0x10 += 1 (freed by 0x1006dd90 when it drops back to 0 at the end).
3. per object (+0x94 the core): movement byte (+1) < 8 and not pinned (flags & 0x10): **0x100779f0** (section 3).
4. env+0x10c += 1 (the environment's impact count; the cores' +0x1a0 stamps, section 6).
5. **0x1008ac60**(ecx mindist, edx synapse 0's object, stack synapse 1's object).

## 2. 0x1008ac60

- The unit argument for 0x10088450: core 1's (+0x14c) when object 0's +0x44 < 8, else core 0's (only read when two
  units merge).
- **0x10088450**(&fs out, &new out, unit, mindist) -> the contact (section 4); [ebp-4] its long-term info (+0x40).
- The pair: the system's pairs (+0x36 count, +0x38 array) last to first, the one with cores (core 0, core 1) in either
  order (+0x34 / +0x38). Its +0x28 (f64, the last impact's time) = env+0xf0, dt = f32(now - old) into the event block
  {dt, env, lt} for the listeners: env 0x10084d60 (each env collision listener (env+0xca count, +0xcc list, last to
  first) with flags +4 & 8, slot 0) and, object +0x44 & 0x2000, 0x10086690; at the end 0x10084da0 (flags & 1, slot 1)
  and 0x100866f0. vphysics' listeners: no physics state.
- The rescue: r = (0x1010d134 coll_dists[0] - gap) x env+0xac when coll_dists[0] > the contact's gap (+0x58), else 0
  and lt+0x58 = 0; rescue = 0x1008ba70(cp) + r, then rescue + rescue (`addss xmm0, xmm0`) into xmm2.
- **0x1008b0e0**(lt, &cores out, cp) with xmm2 the rescue (impact.rs). Then lt+0x20..+0x28 (the relative speed the
  impact wrote) read, negated (xor 0x100f4310) when core 1 ([ebp-8], object 1's core) is static (flags & 2).
- **0x1008b380** the impact system on a 0x68-byte block at ebp-0x68 (+0x10..+0x1c, +0x8..+0xc vectors zeroed first),
  0x1008aed0 frees its vectors; lt+0x20.. = the relative speed again; the end listeners.

**0x1008ba70** (thiscall cp) the rotation's rescue: sum = 0; per long-term core (lt+0x70 then +0x74) present and its
synapse's feature (cp+0x16, then +0x2a) not 3 (a ball): a = ((w0^2 + w1^2) + w2^2) x 2.5e-5 (0x100f3bbc), minss 0.25,
sqrtss (0x10001950), cosf **0x100d7fc5**, then sum = sum + ((1 - c) x core+4 (radius)) x env+0xac.

## 3. 0x100779f0: a core synchronised to the event's time

thiscall (core): core+0x1ac = 0x30 bytes from env+0xa0 (0x1006dc70) with +0x20 = 0, +0..+8 = rot (core+0xc0), +0x10..+0x1c
= q_next (core+0x110); the rotation of the last step, q_last (+0x100) conjugated times q_next (n = q_next, l = q_last):
d0 = ((nw (-lx) + nx lw) + nz (-ly)) - ny (-lz), d1 = ((ny lw + nw (-ly)) + nx (-lz)) - nz (-lx), d2 = ((nz lw + nw (-lz))
+ ny (-lx)) - nx (-ly); q_next = 0x1006ca90(core, &q_next, env+0xf0) (the slerp, object.rs quat_at); the rows +0x60..+0x88
from it (the 0x100723b0 formulas); pos_now (+0x90) = delta f32(t - t_psi) + pos; unless flags & 8: rot = asinf(d_i) x
(inv_dt_psi + inv_dt_psi) per axis (asinf **0x100d7a68**). The block is the impact's: 0x1008b4c0 sets its +0x20 (the core
took part), 0x1008bb40 puts a core that didn't back (rot, q_next) and frees every block.

## 4. 0x10088450: the contact and the friction system from a mindist

thiscall (mindist; [ebp+8] &fs out, +0xc &new out, +0x10 the unit, ret 0x10):
- the sorted synapses (+0x14 bits 8-9: synapse [flag], [flag ^ 1]; objects a, b); their original cores (+0x98); a
  static a swaps them (so [ebp-0xc] is dynamic, [ebp-4] the other). esi = the dynamic core's friction info (+0x4c),
  env = core+0xc.
- **0x1008df50**(ecx mindist, edx &found): status (bits & 0x3c0000) not 0xc0000 (exact): none. **0x1008def0**: object
  syn0 (+0x28)'s friction synapses (+0x28 list, next at +0): the contact = synapse + (i16) +0xc; its objects (+0x10 /
  +0x24) against the mindist's syn1 object (+0x44); **0x100831f0**(contact, mindist): (cp syn0 obj == md syn0 obj and cp
  syn1 obj == md syn1 obj and **0x10083110** on both) or crossed. 0x10083110(cp synapse, md synapse): same status (cp
  +0xe vs md +0x1a), then by the jump table 0x100831dc: 0 point: the same ledge ((edge & ~0xf) - (tri index + 1) x 16)
  and the same start point (the edge words' low 16 bits); 1 edge: the same edge or the cp edge's opposite (edge +
  ((int)(word x 2) >> 17) x 4); 2 face: the same triangle (edge & ~0xf); 3 ball: yes; else IVP Failed line 0x90a.
  Found: *new = 0. Else new 0xa0 + ctor 0x1007ec20 (contact.rs from_mindist), *new = 1.
- A found contact: *fs = the dynamic core's info's system (+8); 0x1008d230 (geometry) and 0x1008afc0 (materials:
  0x1008af60 the two materials, the manager (object env +0x98) slot 3 the elasticity into lt+0x60 (x87 fstp), slot 2
  mu into cp+0x44); done.
- A new contact: geometry, materials; listeners 0x10084df0 / 0x100867c0; then
  - the dynamic core has an info: the other's info for this system (a static core keeps several, found by
    0x1006e4b0(list, system): a CRC-32 (table 0x100f2080) of the system's address into a hash 0x1006e520; a dynamic one
    its own +0x4c when its +8 is the system). Found: cp+0x90 = the system, the contact at the head of +0x20 (+0 next, +4
    prev), +0x3e += 1, **0x100870c0**. Not found, the other dynamic with an info: **0x10081280** (two systems merge:
    ported 2026-11-17: ivp-touch.md 2). Else a new 0xc-byte info (+0 / +4 a vector, +8 the system) for the other, 0x10078860(core, info) (a
    static core: its hash, made by 0x10076330 on first use; a dynamic one: +0x4c), **0x100871f0**(system, other), then
    the contact linked as above and 0x100870c0.
  - no info: a new one for it; the other dynamic with an info: join that system (0x10078860, 0x100871f0, 0x100871c0,
    0x100870c0: ported: ivp-touch.md 1). Else **a new system** (new 0x4c + ctor 0x10086de0(env)) and an info for the
    other; both infos' +8 = it; 0x10078860 (other, then dynamic); cp+0x90, the contact at the head, +0x3e += 1,
    0x100870c0, 0x100871f0(dynamic), 0x100871f0(other).
  - the tail (0x1008877b): both infos' contact vectors take the contact; *fs = the system; **0x10082a60** the spring's
    mass; two dynamic cores on different units merge them (0x10071800 / 0x100718e0 / 0x100713b0 / 0x10071aa0: ported, ivp-touch.md 4).
- **0x100870c0**(system, cp): the pair of cores (cp+0x10's core, cp+0x24's) in either order (last to first); else a new
  0x40 block: +0 / +4 its contact vector, +0x28 = -1000.0 (0x100f40e0), +0x30 = 0 (energy), +0x20 = 1 (countdown), +0x34
  syn0's core, +0x38 syn1's, appended to +0x34..+0x38, listener 0x10084e90(env, pair); the pair's vector takes the contact.
- **0x100871f0**(system, core): +0x24..+0x28 takes it; a dynamic one also +0x2c..+0x30 and **0x10071d40**(core,
  controller) for +8 (priority 0), +0 (600), +0x10 (2000): appended to the core's list (+0x140 / +0x142 / +0x144),
  appended to the unit's (+0x1c / +0x1e / +0x20: an entry {controller, its cores} made by 0x10071550 if new, the core
  added by 0x100714f0), then the unit's sort 0x10071e40; +0x3c += 1.
- **0x100871c0**(system, cp): cp+0x90, at the head of +0x20, +0x3e += 1.

## 5. The impact system 0x1008b380 / 0x1008b590

The block: +0 the environment, +4 the rounds, +8 the cores the impacts moved, +0x10 the cores synchronised, +0x18 the pairs
to look at, +0x20 the friction system.

**0x1008b380**(this, mindist, fs, pair, cp; ret 0x10): +4 = 0, +0x20 = fs, +0 = the pair's core a's env. Core 0 (cp+0x10's
object's core) dynamic (flags & 0x12 clear): **0x1008b4c0**(core, pair); the pair's core a dynamic: into +0x10; core 1
(cp+0x24's) dynamic: 0x1008b4c0; the pair's core b dynamic: into +0x10; the pair into +0x18; **0x1008b2c0**(pair, cp);
then the rounds: r = 0x1008b590; while r == 1: +4 += 1, count += 1, +4 > 5000 (0x1388): the mindist's slot 4 with 1 (it
is deleted: reported) and stop; r = 0x1008b590. env+0x58 += count + 1 (a statistic). **0x1008bb40**.

**0x1008b4c0**(this, core, pair; ret 8): +8 takes the core; core+0x1ac's +0x20 = 1; per pair of the system (+0x36 /
+0x38, last to first) with the core, not the given pair, not in +0x18 yet: **0x10081fe0**(pair, fs) > 0: +0x18 takes it.

**0x10081fe0** / **0x1008b2c0** (the pair's contacts, last to first; 0x1008b2c0 skips the impacting one): 0x1008d230 with
the env, 0x1008af60 into lt+0x40, lt+0x34 / +0x30 the objects, +0x38 / +0x3c the edges, the manager's slot 3 into lt+0x60,
slot 2 into cp+0x44; lt+0x56 == 1 (the features left): **0x100810a0** removes it (0x10081fe0: count - 1). 0x10081fe0
returns the count left.

**0x1008b590** one round: xmm2 = 0x1010d238 (coll_dists[63]), best = none. Per pair of +0x18 last to first: skipped when
((f_a & 2) | (f_a >> 5)) & ((f_b & 2) | (f_b >> 5)) & 6 (bytes of the cores' flags: both static or in this PSI's impact
lists, 0x40 / 0x80); per contact of the pair last to first: lt+0x54 != 1: env+0x68 += 1, lt+0x54 = 1; gap > 0x1010d250:
lt+0x5c = 1e20 (0x60ad78ec); else r as in 0x1008ac60 (lt+0x58 = 0 in the else), rescue = (0x1008ba70 + r) doubled into
lt+0x58, lt+0x5c = gap - ((the normal speed **0x1007e990** + rescue x 0.5) x env+0xa8). Then lt+0x5c below xmm2: the
best (and xmm2 = it). None: return 0. Else per long-term core (+0x74 first, then +0x70) without a +0x1ac block: +0x10
takes it and, movement byte < 8 and not pinned, 0x100779f0. lt+0x52 += 1; 0x1008b0e0(lt, &out, cp) with xmm2 = lt+0x58;
per out core (out[1] first) dynamic: its +0x1ac block there with +0x20 == 0: 0x1008b4c0(core, the best's pair); else every
contact of the core's info for this system gets lt+0x54 = 0 (a static core's info by 0x1006e4b0). Return 1.

**0x1008bb40** the end: per core of +0x10 (last to first) with a block whose +0x20 is 0: rot (+0xc0..) and q_next
(+0x110..) back from it; every +0x1ac = 0. dt = f32(env+0xf8 - env+0xf0) (the next PSI from now), 1 / dt or 1e10
(0x501502f9) at or below 1e-10; per core of +8 (last to first) not static: **0x100970f0**(core, {dt, 1/dt, env}, a
256-entry list on the stack) (the next PSI from now: core.rs next_psi with the stage-5 rot step, section 7; its hull part
0x100974e3 collects the due objects), +0x1ac = 0, its contacts' lt+0x54 = 0; **0x10097db0**(env, the list) (stage 4's
synapse events); per core of +8 (last to first) not static: +0x1a0 = env+0x10c and per object (+0x52 / +0x54, last to
first) **0x100730d0**: its exact synapses (object +0x20, next at +8; the mindist = synapse + (i16) +0x18) whose two cores'
+0x1a0 differ: recalc_mindist 0x100982d0 (the stamp already the event's: no new walk) and, bits & 0xc000 clear,
update_exact_mindist_events(0, 2) 0x10095310.

## 6. The friction system on the world (friction_sys.rs)

- The cores of the world are indexed by object (one object per core here); a contact's `core` pair and a pair's are
  object indices; the static box's core is the collision world's own.
- **The controllers inside the PSI**: World::psi_with hands `Hook::Controller(Kind::Friction(p))` to Collide in the
  unit's order (the kart resting: [0, drag 500, motion 500..., 600, gravity 1000, 2000], run from the last).
  2000 0x10082e70: the caches refreshed at the PSI's time code, the geometry (friction_energy::geometry with
  0x1008d230 per contact), the energy (the unit's flags word: its state byte 1, flags & ~0xff from World::Body
  unit_flags; env+0x118 0x3f7f9433). 600 0x10082ff0 (friction::tangential). 0 0x10082f60 (solver::pressure_controller:
  SolveEnv from the mindist settings, env+0xc0 0x41a28f5c, perf +0x18 10, the World's limits).
- **A core leaving the system** (0x100810a0: its info's contact vector empty -> 0x100788c0 the info off the core,
  **0x10087270**(system, core): out of +0x2c, the three controllers off the core's list (0x10018430) and the unit's
  (**0x10071dc0**: the entry's core removed, an entry without cores freed (0x10071890) and the rest shifted down: from
  +0x10 (2000), +0 (600), +8 (0)), out of +0x24, +0x3c -= 1; then the core's unit flags & ~0x200 | 0x100 (0x10081211)).
  solver.rs records the core in FrictionSystem::left; Collide::drain_left applies it after the controller or impact.
- **The system's end**: 0x10082f60 with +0x3e == 0: slot 7 **0x10086e30** -> 0x10086e60 (its vectors freed; nothing
  else: the cores left already), then the event's unit (es+0xc) flags & ~0x200 | 0x100 (0x10082fce). +0x44 set:
  0x100815a0 / 0x100816a0 (the split: ported, ivp-touch.md 3; one dynamic core never reaches it: an emptied pair empties
  the system).
- **The unit's rebuild** (0x10072540 at 0x100727ee, after the controllers and the sleep check): flags & 0x300: the
  controller list cleared (**0x10071800**), rebuilt (**0x100713b0**: per core last to first, its own list (+0x140) from
  its last controller, each appended when new) and sorted (0x10071e40); 0x10071710 (the split test: a one-core unit
  gives none); flags &= ~0x300. The rebuild reverses the order of equal priorities (the motion controllers and drag at
  500): flat-drive's jump (tick 301) depends on it. controller.rs List keeps both lists (.0 the unit's, .1 the core's).
- **vphysics' friction listener 0x10011eb0** (IPhysicsEnvironment::Simulate 0x10014320 calls it at 0x100144fe after
  IVP's step): skipped while dt (env+0xa8) > f32(env+0x100) - its +0x18; else +0x18 = f32(env+0x100), per tracked object
  (+4 list, +0x10 count) with CPhysicsObject +0x1c & 2 (CALLBACK_GLOBAL_FRICTION) each friction synapse (object +0x28)
  whose other object has the flag: cp+0x48 != 0: energy = cp+0x48 x (1 / elapsed) x core+0x3c, past 0.05 (0x100f3c34)
  the game's IPhysicsCollisionEvent::Friction (energy x 1550.0032, the surface props through 0x10116078 slot 0x38); cp+0x48
  = 0. Only the clear touches the state (nothing in IVP reads +0x48): Collide::friction_listener.

## 7. The next PSI from an event's time: 0x10096940's stage-5 path

0x10096940 (the step's rotation, called by 0x100970f0 at 0x10097246) takes **0x10096d56** when core flags & 8 or env+0x114
== 5, and from there, without a car wheel (core+0x48 == 0) or with core+8 == 0, **0x10096fe9**: h = dt x 0.5; s_i =
sinf(h w_i) (0x100d9542); n = (s0^2 + s1^2) + s2^2; n > 1: s x (0.997 (0x3f7f3b64) / sqrt(n)) and n again; q = (s, sqrt(1 -
n)); the rot speed is not touched (no gyroscopic step). env+0x114 is the PSI's stage (0x10084fb0: 0 at 0x10084fcf, 2 at
0x100850a5 before stage 4's 0x10097db0, 3 at 0x100850c3 before stage 5's 0x100952d0, 4 at 0x100850df before stage 6, 5
at 0x1008512b after it): between PSIs, where the mindist events run, it is 5. core.rs next_psi(.., stage5) / rot_step_sin.

## 8. Sleeping and waking on the ground

- **A freeze** (0x10077820, the unit's sleep check 0x100722d0 in stage 2): 0x10077750 (the speeds zero) -> **0x100775f0**
  (q_next = q_last, +0x138 = the event's 1/dt, +0x5c spin rate 0, speed and delta zero, +0x13c 0, **+0x1a4 0, +0x120 = (1,
  0, 0)**: Core::rest_rates, also at a revival); then per object (+0x52 / +0x54, last to first): +0x44 = 8; recheck_ov_element
  0x10094de0 (two objects at rest no longer pair: the OO watcher and its mindist are deleted); the hull manager (object
  +0x48): d = f32(env+0xf0 - +0), +0x14 += +0xc x d, +0x10 += +8 x d, +0xc = +8 = 0 (its time +0 kept), reset 0x10093bb0;
  the cache (+0x40) released (its +0x68 = 0, +0x40 = 0). The core still takes this PSI's stage 3 (its hull manager's time
  = now, gradients 0). Collide::freeze_objects, run by World::psi_with's Hook::Freeze inside the sleep check (a Sleep
  between ticks: World::frozen, drained at Collide::simulate's start).
- **A revival** (stage 1, 0x10071ef0 -> 0x100778d0): the creation path every time (recheck_ov_element with the movement
  bytes 0x21: a new OO watcher and mindist, ivp-mindist.md 4); **0x10082ce0** (the object's exact mindists not phantom:
  the other core static -> skipped for a dynamic core (a static pair is deleted, slot 4); the other dynamic without an
  info: recalc, len below 0x1010d24c -> 0x10088450 and its geometry: two dynamic cores only: ported since, ivp-pileup.md 6).
- The friction system survives the sleep (its unit isn't simulated, so its controllers don't run); its contacts carry on
  at the revival.

## 9. The check: ivp_check's ground mode

A scenario with one `box` (rubikon/tests/KartOracle/scenarios) runs the kart through Collide::simulate with the contacts
side on (Friction::new(FrictionEnv::csgo())): the box's static core / frame / ledge tree root from the oracle's `.md`
objects line (sim/src/bin/common/ivp_floor.rs, shared with mindist_check), the box then the kart made (add_object) as the
oracle made them. Per tick, beside the free-flight checks (every core field, GetPosition / GetVelocity /
GetPositionMatrix / IsAsleep, the environment's unit lists and LCG): the friction system's dump (`fs` counts, +0x40,
+0x44, every contact's modelled words in list order, every pair's count / countdown / last impact / energy), the live
mindist's bits and +0x50..+0x6c, both hull managers (fields and every listener's value and kind) against the `.md`
(common/ivp_ground.rs), and no untraced path.

**Checked (2026-11-17)**: bit-identical over every tick of every box scenario: flat-drive 400 (the touchdown's 5 impacts
in tick 8, a fourth contact at 45-52, the jump and landing 300-322), wake-drive 1300 (asleep at 359 and 891, woken at 700,
a jump at 900, landing 933, asleep 980), drop-flip, drop-tilt, drop-high, drop-edge, drop-corner (120 each), corner-roll,
corner-roll-left, corner-pierce (90 each); and scratch runs of the drops / corners at 900 ticks and flat-drive at 1200.
IVP_DEBUG=1 prints each impact's inputs (impact_sys.rs dbg_impact) against the oracle's impact_in lines.

Run: `cargo build --release -p ze-sim --bin ivp_check`, then `ivp_check <scenario> <oracle out> <the kart's .phy>` (the
oracle with KART_ORACLE_PROBES=1 for the `fs` / `cp` / `pair` lines; crazykart-physics.md 8).

## 10. Not ported (reported when reached: Collide::untraced, or a panic naming the address)

- Two dynamic cores: a second friction system or two merging (0x10081280, the units' merge 0x10071800 / 0x100718e0 /
  0x100713b0 / 0x10071aa0), the split 0x100815a0 / 0x100816a0 (all ported since: ivp-touch.md); 0x10082ce0's dynamic
  branch and the revival of a unit of several cores: ported since (ivp-pileup.md 6).
- (The sliding friction 0x1007fd70 and the sliding impacts 0x1008b820 / 0x10088cc0 never run: ivp-contacts.md 7.) The impact's speed-limit hooks and
  a core past perf +0xc impacts (impact.rs panics); a core already in this PSI's impact list (flags & 0xc0, 0x1008a0b2).
- 5000 impact rounds (the mindist deleted). (A triangle's own material: ported, ivp-contacts.md 7.)
- The pressure solve's undo 0x100a0d10 (solver.rs); FF minimize 0x100984c0 and the rescue push 0x100980a0 (ivp-mindist.md 10).
- asinf above sqrt(3)/2 (0x100d7b4b, 0x100d7ca5) and cosf's large-argument path 0x100d80e0.
- The listeners (env 0x10084d60 / 0x10084da0 / 0x10084df0 / 0x10084e90, objects 0x10086690 / 0x100866f0 / 0x100867c0):
  vphysics' collision callbacks, no physics state (not read further).
- env+0xc0 and env+0x118's formulas (their values are the oracle environment's: friction_sys.rs FrictionEnv::csgo).
