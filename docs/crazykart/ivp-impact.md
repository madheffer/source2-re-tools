# IVP: the impact system and a kart on the ground

vphysics.dll (CS:GO legacy, 32-bit, md5 d97cf2194594d7545427cdabc7376db4, Ghidra `/csgo_vphysics_legacy.dll`, capstone). Between collision detection ([ivp-mindist.md](ivp-mindist.md): the mindist's time event up to do_impact) and the contacts ([ivp-contacts.md](ivp-contacts.md): the friction system, its solves, the impact solver 0x1008b0e0): what a mindist's impact does, the friction system on the world, its controllers inside the PSI, sleeping and waking on the ground. SSE scalar single unless said.

## Functions

| Address | Module | What |
|---|---|---|
| 0x1008b020 | vphysics | do_impact (the mindist's vtable slot 8; thiscall mindist) |
| 0x10095dd0 | vphysics | simulate_time_event (calls do_impact) |
| 0x10071ef0 | vphysics | revive a unit (unit, env) |
| 0x10086b70 | vphysics | a revived core's collision side |
| 0x100778d0 | vphysics | the object's recheck |
| 0x10082ce0 | vphysics | revive_friction: the object's exact mindists to contacts |
| 0x1006dd90 | vphysics | frees the temporary memory when its count drops to 0 |
| 0x1006dc70 | vphysics | allocates from the temporary memory (env+0xa0) |
| 0x100779f0 | vphysics | a core synchronised to the event's time (thiscall core) |
| 0x1006ca90 | vphysics | the slerp: q at a time (core, &q_next, t) |
| 0x100723b0 | vphysics | the rows' formulas (+0x60..+0x88 from q) |
| 0x1008ac60 | vphysics | the impact proper (ecx mindist, edx synapse 0's object, stack synapse 1's object) |
| 0x10088450 | vphysics | the contact and the friction system from a mindist (thiscall; &fs out, &new out, unit; ret 0x10) |
| 0x10084d60 / 0x10084da0 | vphysics | env collision listeners: start (flags +4 & 8, slot 0) / end (flags & 1, slot 1) |
| 0x10086690 / 0x100866f0 | vphysics | object listeners start / end (object +0x44 & 0x2000) |
| 0x10084df0 / 0x100867c0 | vphysics | new-contact listeners (env / object) |
| 0x10084e90 | vphysics | new-pair listener (env, pair) |
| 0x1008ba70 | vphysics | the rotation's rescue (thiscall cp) |
| 0x1008b0e0 | vphysics | the impact solver (lt, &cores out, cp), rescue in xmm2 |
| 0x1008b380 | vphysics | the impact system (this, mindist, fs, pair, cp; ret 0x10) |
| 0x1008aed0 | vphysics | frees the impact system block's vectors |
| 0x1008b4c0 | vphysics | a core into the impact system (this, core, pair; ret 8) |
| 0x10081fe0 | vphysics | a pair's contacts refreshed; returns the count left |
| 0x1008b2c0 | vphysics | the same, skipping the impacting contact (pair, cp) |
| 0x1008b590 | vphysics | one impact round |
| 0x1008bb40 | vphysics | the impact system's end |
| 0x1007e990 | vphysics | a contact's normal speed |
| 0x1008df50 | vphysics | find the mindist's contact (ecx mindist, edx &found) |
| 0x1008def0 | vphysics | walk object syn0's friction synapses |
| 0x100831f0 | vphysics | contact matches mindist (contact, mindist) |
| 0x10083110 | vphysics | synapse matches (cp synapse, md synapse); jump table 0x100831dc |
| 0x1007ec20 | vphysics | contact ctor (new 0xa0) from a mindist |
| 0x1008d230 | vphysics | a contact's geometry |
| 0x1008afc0 | vphysics | a contact's materials |
| 0x1008af60 | vphysics | the two materials |
| 0x1006e4b0 | vphysics | a static core's info for a system (list, system) |
| 0x1006e520 | vphysics | the info hash |
| 0x10078860 | vphysics | an info onto a core (core, info) |
| 0x10076330 | vphysics | a static core's info hash, made on first use |
| 0x100870c0 | vphysics | a contact into its pair (system, cp) |
| 0x10081280 | vphysics | two friction systems merge ([ivp-touch.md](ivp-touch.md) 2) |
| 0x100871f0 | vphysics | a core into a system (system, core) |
| 0x100871c0 | vphysics | a contact into a system (system, cp) |
| 0x10086de0 | vphysics | friction system ctor (new 0x4c; env) |
| 0x1008877b | vphysics | 0x10088450's tail |
| 0x10082a60 | vphysics | the spring's mass |
| 0x10071800 / 0x100718e0 / 0x100713b0 / 0x10071aa0 | vphysics | two units merge ([ivp-touch.md](ivp-touch.md) 4); 0x10071800 clears and 0x100713b0 rebuilds a unit's controller list |
| 0x10071d40 | vphysics | a controller onto a core and its unit (core, controller) |
| 0x10071550 / 0x100714f0 | vphysics | a unit controller entry made / a core added to it |
| 0x10071e40 | vphysics | the unit's controller sort |
| 0x100810a0 | vphysics | a contact removed (features left) |
| 0x100970f0 | vphysics | the next PSI from now for a core (core, {dt, 1/dt, env}, list) |
| 0x100974e3 | vphysics | its hull part (collects the due objects) |
| 0x10097db0 | vphysics | stage 4's synapse events (env, list) |
| 0x100730d0 | vphysics | an object's exact synapses rechecked |
| 0x100982d0 | vphysics | recalc_mindist |
| 0x10095310 | vphysics | update_exact_mindist_events(0, 2) |
| 0x10082e70 | vphysics | friction controller, priority 2000 (caches at the PSI's time code, geometry, energy) |
| 0x10082ff0 | vphysics | friction controller 600 (tangential) |
| 0x10082f60 | vphysics | friction controller 0 (the pressure solve) |
| 0x100788c0 | vphysics | the info off the core |
| 0x10087270 | vphysics | a core leaves a system (system, core) |
| 0x10018430 | vphysics | a controller off a core's list |
| 0x10071dc0 | vphysics | a controller off the unit's list |
| 0x10071890 | vphysics | frees an entry without cores |
| 0x10081211 | vphysics | (in 0x100810a0) the unit flags `& ~0x200 | 0x100` |
| 0x10086e30 -> 0x10086e60 | vphysics | the system's end (slot 7): its vectors freed |
| 0x10082fce | vphysics | (in 0x10082f60) the event's unit (es+0xc) flags `& ~0x200 | 0x100` |
| 0x100815a0 / 0x100816a0 | vphysics | the system's split ([ivp-touch.md](ivp-touch.md) 3) |
| 0x10072540 | vphysics | the unit's step; its rebuild at 0x100727ee |
| 0x10071710 | vphysics | the unit's split test |
| 0x10011eb0 | vphysics | vphysics' friction listener |
| 0x10014320 | vphysics | IPhysicsEnvironment::Simulate (calls 0x10011eb0 at 0x100144fe) |
| 0x10096940 | vphysics | the step's rotation (called by 0x100970f0 at 0x10097246) |
| 0x10096d56 / 0x10096fe9 | vphysics | its stage-5 path / the no-wheel rot step |
| 0x10084fb0 | vphysics | the PSI (sets env+0x114) |
| 0x100952d0 | vphysics | stage 5 |
| 0x10077820 | vphysics | a freeze |
| 0x100722d0 | vphysics | the unit's sleep check (stage 2) |
| 0x10077750 | vphysics | the speeds zero |
| 0x100775f0 | vphysics | the rest rates (also at a revival) |
| 0x10094de0 | vphysics | recheck_ov_element |
| 0x10093bb0 | vphysics | hull manager reset |
| 0x100d7fc5 | vphysics | cosf (CRT) |
| 0x100d7a68 | vphysics | asinf (CRT) |
| 0x100d9542 | vphysics | sinf (CRT) |
| 0x10001950 | vphysics | sqrtss |

## Fields

| Offset | Field |
|---|---|
| env+8 +0x1a8 / +0x18 | the sleeping / active unit lists |
| env+0x58 | impact rounds statistic |
| env+0x68 | contacts refreshed counter |
| env+0x98 (object env) | the material manager (slot 2 mu, slot 3 elasticity) |
| env+0xa0 | the temporary memory (+0x10 its use count) |
| env+0xa8 | dt |
| env+0xac | the rescue scale |
| env+0xc0 | 0x41a28f5c (the pressure solve) |
| env+0xca / +0xcc | env collision listeners: count / list |
| env+0xf0 | the event's time (f64) |
| env+0xf8 | the next PSI's time |
| env+0x100 | the time (f64) |
| env+0x108 | time events counted |
| env+0x10c | the impact count (cores' +0x1a0 stamps) |
| env+0x114 | the PSI's stage |
| env+0x118 | 0x3f7f9433 (the friction energy) |
| unit +0 | state (8 sleeping, 1 active) |
| unit +0xe / +0x10 | cores: count / list |
| unit +0x1c / +0x1e / +0x20 | controller entries {controller, its cores} |
| core +1 | movement byte (>= 8 at rest) |
| core flags | & 2 static, & 8, & 0x10 pinned, & 0x12 not dynamic, 0x40 / 0x80 in this PSI's impact lists, & 0xc0 |
| core +4 | radius |
| core +8 | (rot step: 0 skips the wheel path) |
| core +0xc | env |
| core +0x3c | (friction listener factor) |
| core +0x48 | car wheel |
| core +0x4c | friction info (dynamic core) |
| core +0x5c | spin rate |
| core +0x60..+0x88 | the rows |
| core +0x90 | pos_now |
| core +0xc0 | rot speed |
| core +0x100 / +0x110 | q_last / q_next |
| core +0x120 | (1, 0, 0) at rest |
| core +0x138 | 1/dt |
| core +0x13c | 0 at rest |
| core +0x140 / +0x142 / +0x144 | controller lists |
| core +0x14c | the unit |
| core +0x1a0 | impact stamp (env+0x10c) |
| core +0x1a4 | 0 at rest |
| core +0x1ac | the impact block (0x30): +0..+8 rot, +0x10..+0x1c q_next, +0x20 took part |
| object +0x20 | exact synapses (next at +8; mindist = synapse + (i16) +0x18) |
| object +0x28 | friction synapses (next at +0) |
| object +0x40 | the cache (its +0x68) |
| object +0x44 | movement state (8 at rest), & 0x2000 listeners |
| object +0x48 | hull manager: +0 time, +8, +0xc, +0x10, +0x14 |
| object +0x52 / +0x54 | (core's objects: count / list) |
| object +0x94 / +0x98 | core / original core |
| mindist +0x14 | bits 8-9: synapse order; status bits & 0x3c0000 (0xc0000 exact); & 0xc000 |
| mindist +0x28 / +0x44 | synapse 0 / 1 objects |
| mindist +0x1a | synapse status |
| cp +0xe | synapse status |
| cp +0x10 / +0x24 | the two objects |
| cp +0x16 / +0x2a | the synapses' features (3 ball) |
| cp +0x40 | long-term info (lt) |
| cp +0x44 | mu |
| cp +0x48 | friction energy accumulator |
| cp +0x58 | gap |
| cp +0x90 | the friction system |
| cp +0x150 / +0x158 | reference times |
| lt +0x20..+0x28 | relative speed (written by the impact) |
| lt +0x30 / +0x34 | objects |
| lt +0x38 / +0x3c | edges |
| lt +0x40 | materials |
| lt +0x52 | impacts counted |
| lt +0x54 | refreshed flag |
| lt +0x56 | features left (1: removed) |
| lt +0x58 | rescue |
| lt +0x5c | the impact's urgency |
| lt +0x60 | elasticity (x87 fstp) |
| lt +0x70 / +0x74 | long-term cores |
| friction info (0xc) | +0 / +4 a contact vector, +8 the system |
| system (0x4c) +0 / +8 / +0x10 | controllers 600 / 0 / 2000 |
| system +0x20 | contacts (+0 next, +4 prev) |
| system +0x24..+0x28 | cores |
| system +0x2c..+0x30 | dynamic cores |
| system +0x34..+0x38 | pairs (also +0x36 count, +0x38 array) |
| system +0x3c | core count |
| system +0x3e | contact count |
| system +0x40 / +0x44 | (+0x44 set: split) |
| pair (0x40) +0 / +4 | contact vector |
| pair +0x20 | countdown (1) |
| pair +0x28 | last impact time (f64, -1000.0) |
| pair +0x30 | energy (0) |
| pair +0x34 / +0x38 | syn0's / syn1's core |
| impact block (0x68) +0 / +4 | the environment / the rounds |
| impact block +8 / +0x10 / +0x18 / +0x20 | cores moved / cores synchronised / pairs to look at / the friction system |
| friction listener +4 / +0x10 / +0x18 | tracked objects / count / last time |
| CPhysicsObject +0x1c | & 2 CALLBACK_GLOBAL_FRICTION |

## Constants

| Value | What |
|---|---|
| 0x1010d134 | coll_dists[0] |
| 0x1010d238 | coll_dists[63] |
| 0x1010d250 | the gap limit for an impact candidate |
| 0x1010d24c | the revival's contact length |
| 0x100f3bbc | 2.5e-5 |
| 0x100f4310 | sign mask (xor) |
| 0x100f40e0 | -1000.0 |
| 0x60ad78ec | 1e20 |
| 0x501502f9 | 1e10 (1 / dt at or below 1e-10) |
| 0x3f7f3b64 | 0.997 |
| 0x100f3c34 | 0.05 (friction event threshold) |
| 1550.0032 | friction energy to the game's units |
| 0x10116078 | the surface props (slot 0x38) |
| 0x1388 | 5000 impact rounds (the mindist deleted) |
| 0x100f2080 | CRC-32 table (the info hash) |
| 0xa0 / 0x4c / 0x40 / 0xc | sizes: contact / system / pair / info |
| 0x90a | IVP Failed line in 0x10083110 |
| perf +0x18 | 10 (the pressure solve) |
| controller priorities | 0, 600, 2000 (friction); drag and motion 500; gravity 1000 |

## 1. do_impact 0x1008b020

From simulate_time_event when the recalculated length is below `coll_dists[selector] + mindist_change_force_dist`, inside the time event:

1. Per synapse in the mindist's order: an object with +0x44 == 8 has its original core's unit revived (0x10071ef0: each of the unit's cores, last to first, with movement byte >= 8 through 0x10086b70; then a unit in state 8 moved from the sleeping list to the active one, state 1). A static object's unit isn't in state 8: nothing. 0x10086b70 runs each revived core's collision side as at a PSI's revival: 0x100778d0, then 0x10082ce0. That can make a contact with a dynamic partner outside any friction system, whose reference times (+0x150 / +0x158) become the event's time (a sleeping kart hit by a climbing lift: [ivp-pileup.md](ivp-pileup.md) 7). It runs before the impact, on the contacts the impact then reads.
2. env+0xa0 +0x10 += 1 (freed by 0x1006dd90 when it drops back to 0 at the end).
3. Per object (+0x94): movement byte < 8 and not pinned: 0x100779f0 (section 3).
4. env+0x10c += 1.
5. 0x1008ac60.

## 2. 0x1008ac60

1. The unit for 0x10088450: core 1's (+0x14c) when object 0's +0x44 < 8, else core 0's (read only when two units merge).
2. 0x10088450 -> the contact (section 4); [ebp-4] its lt (+0x40).
3. The pair: the system's pairs last to first, the one with (core 0, core 1) in either order (+0x34 / +0x38). Its +0x28 = env+0xf0; `dt = f32(now - old)` into the event block {dt, env, lt}; the start listeners 0x10084d60 (each env listener last to first) and, object +0x44 & 0x2000, 0x10086690; at the end 0x10084da0 and 0x100866f0. vphysics' listeners hold no physics state.
4. The rescue: `r = (coll_dists[0] - gap) x env+0xac` when coll_dists[0] > the gap (+0x58), else 0 and lt+0x58 = 0; `rescue = 0x1008ba70(cp) + r`, then `rescue + rescue` (`addss xmm0, xmm0`) into xmm2.
5. 0x1008b0e0(lt, &cores out, cp), xmm2 the rescue. lt+0x20..+0x28 read, negated (xor 0x100f4310) when core 1 ([ebp-8]) is static (flags & 2).
6. 0x1008b380 on a 0x68-byte block at ebp-0x68 (+0x10..+0x1c, +0x8..+0xc vectors zeroed first); 0x1008aed0; lt+0x20.. = the relative speed again; the end listeners.

0x1008ba70: sum = 0; per lt core (lt+0x70 then +0x74) present with its synapse's feature (cp+0x16, then +0x2a) not 3 (a ball): `a = ((w0^2 + w1^2) + w2^2) x 2.5e-5`, minss 0.25, sqrtss, cosf 0x100d7fc5, then `sum = sum + ((1 - c) x core+4) x env+0xac`.

## 3. 0x100779f0: a core synchronised to the event's time

1. core+0x1ac = 0x30 bytes from env+0xa0 (0x1006dc70): +0x20 = 0, +0..+8 = rot (core+0xc0), +0x10..+0x1c = q_next (core+0x110).
2. The last step's rotation, q_last conjugated times q_next (n = q_next, l = q_last):
   - `d0 = ((nw (-lx) + nx lw) + nz (-ly)) - ny (-lz)`
   - `d1 = ((ny lw + nw (-ly)) + nx (-lz)) - nz (-lx)`
   - `d2 = ((nz lw + nw (-lz)) + ny (-lx)) - nx (-ly)`
3. q_next = 0x1006ca90(core, &q_next, env+0xf0); the rows +0x60..+0x88 from it (0x100723b0's formulas); `pos_now (+0x90) = delta f32(t - t_psi) + pos`.
4. Unless flags & 8: `rot = asinf(d_i) x (inv_dt_psi + inv_dt_psi)` per axis (asinf 0x100d7a68).

The block is the impact's: 0x1008b4c0 sets its +0x20 (the core took part); 0x1008bb40 puts back a core that didn't (rot, q_next) and frees every block.

## 4. 0x10088450: the contact and the friction system from a mindist

1. The sorted synapses (+0x14 bits 8-9: synapse [flag], [flag ^ 1]; objects a, b); their original cores (+0x98); a static a swaps them ([ebp-0xc] dynamic, [ebp-4] the other). esi = the dynamic core's info (+0x4c), env = core+0xc.
2. 0x1008df50: status (bits & 0x3c0000) not 0xc0000 (exact): none. 0x1008def0: object syn0 (+0x28)'s friction synapses: contact = synapse + (i16) +0xc; its objects (+0x10 / +0x24) against the mindist's syn1 object (+0x44); 0x100831f0: (cp syn0 obj == md syn0 obj and cp syn1 obj == md syn1 obj and 0x10083110 on both) or crossed.
3. 0x10083110: same status (cp +0xe vs md +0x1a), then by the jump table:

   | Status | Match |
   |---|---|
   | 0 point | the same ledge (`(edge & ~0xf) - (tri index + 1) x 16`) and the same start point (the edge words' low 16 bits) |
   | 1 edge | the same edge or the cp edge's opposite (`edge + ((int)(word x 2) >> 17) x 4`) |
   | 2 face | the same triangle (`edge & ~0xf`) |
   | 3 ball | yes |
   | else | IVP Failed line 0x90a |

   Found: *new = 0. Else new 0xa0 + 0x1007ec20, *new = 1.
4. A found contact: *fs = the dynamic core's info's system (+8); 0x1008d230 and 0x1008afc0 (0x1008af60, manager slot 3 elasticity into lt+0x60 (x87 fstp), slot 2 mu into cp+0x44); done.
5. A new contact: geometry, materials; listeners 0x10084df0 / 0x100867c0; then:
   - The dynamic core has an info: the other's info for this system (a static core keeps several, found by 0x1006e4b0: a CRC-32 (table 0x100f2080) of the system's address into the hash 0x1006e520; a dynamic one its own +0x4c when its +8 is the system). Found: cp+0x90 = the system, the contact at the head of +0x20, +0x3e += 1, 0x100870c0. Not found and the other dynamic with an info: 0x10081280 (two systems merge). Else a new info for the other, 0x10078860 (a static core: its hash, made by 0x10076330 on first use; a dynamic one: +0x4c), 0x100871f0(system, other), the contact linked as above, 0x100870c0.
   - No info: a new one for it; the other dynamic with an info: join that system (0x10078860, 0x100871f0, 0x100871c0, 0x100870c0: [ivp-touch.md](ivp-touch.md) 1). Else a new system (new 0x4c + 0x10086de0(env)) and an info for the other; both infos' +8 = it; 0x10078860 (other, then dynamic); cp+0x90, the contact at the head, +0x3e += 1, 0x100870c0, 0x100871f0(dynamic), 0x100871f0(other).
   - The tail (0x1008877b): both infos' contact vectors take the contact; *fs = the system; 0x10082a60; two dynamic cores on different units merge them (0x10071800 / 0x100718e0 / 0x100713b0 / 0x10071aa0).
6. 0x100870c0(system, cp): the pair of cores (cp+0x10's, cp+0x24's) in either order (last to first); else a new 0x40 pair: +0x28 = -1000.0, +0x30 = 0, +0x20 = 1, +0x34 syn0's core, +0x38 syn1's, appended to +0x34..+0x38, listener 0x10084e90; the pair's vector takes the contact.
7. 0x100871f0(system, core): +0x24..+0x28 takes it; a dynamic one also +0x2c..+0x30 and 0x10071d40 for +8 (priority 0), +0 (600), +0x10 (2000): appended to the core's list (+0x140 / +0x142 / +0x144) and the unit's (+0x1c / +0x1e / +0x20: an entry made by 0x10071550 if new, the core added by 0x100714f0), then 0x10071e40; +0x3c += 1.
8. 0x100871c0(system, cp): cp+0x90, at the head of +0x20, +0x3e += 1.

## 5. The impact system 0x1008b380 / 0x1008b590

0x1008b380:

1. +4 = 0, +0x20 = fs, +0 = the pair's core a's env.
2. Core 0 (cp+0x10's object's core) dynamic (flags & 0x12 clear): 0x1008b4c0(core, pair); the pair's core a dynamic: into +0x10. Core 1 (cp+0x24's) dynamic: 0x1008b4c0; the pair's core b dynamic: into +0x10. The pair into +0x18; 0x1008b2c0(pair, cp).
3. Rounds: r = 0x1008b590; while r == 1: +4 += 1, count += 1; +4 > 5000: the mindist's slot 4 with 1 (deleted: reported) and stop; r = 0x1008b590. env+0x58 += count + 1. 0x1008bb40.

0x1008b4c0: +8 takes the core; core+0x1ac's +0x20 = 1; per pair of the system (+0x36 / +0x38, last to first) with the core, not the given pair, not in +0x18 yet: 0x10081fe0(pair, fs) > 0 -> +0x18 takes it.

0x10081fe0 / 0x1008b2c0 (the pair's contacts last to first; 0x1008b2c0 skips the impacting one): 0x1008d230 with the env, 0x1008af60 into lt+0x40, lt+0x34 / +0x30 the objects, +0x38 / +0x3c the edges, manager slot 3 into lt+0x60, slot 2 into cp+0x44; lt+0x56 == 1: 0x100810a0 removes it (0x10081fe0: count - 1).

0x1008b590, one round:

1. xmm2 = coll_dists[63], best = none.
2. Per pair of +0x18 last to first: skipped when `((f_a & 2) | (f_a >> 5)) & ((f_b & 2) | (f_b >> 5)) & 6` (the cores' flag bytes: both static or in this PSI's impact lists, 0x40 / 0x80). Per contact last to first: lt+0x54 != 1: env+0x68 += 1, lt+0x54 = 1. gap > 0x1010d250: lt+0x5c = 1e20; else r as in 0x1008ac60 (lt+0x58 = 0 in the else), `rescue = (0x1008ba70 + r)` doubled into lt+0x58, `lt+0x5c = gap - ((normal speed 0x1007e990 + rescue x 0.5) x env+0xa8)`. lt+0x5c below xmm2: the best (xmm2 = it).
3. None: return 0.
4. Per lt core (+0x74 first, then +0x70) without a +0x1ac block: +0x10 takes it and, movement byte < 8 and not pinned, 0x100779f0.
5. lt+0x52 += 1; 0x1008b0e0(lt, &out, cp) with xmm2 = lt+0x58.
6. Per out core (out[1] first) dynamic: its block's +0x20 == 0: 0x1008b4c0(core, the best's pair); else every contact of the core's info for this system gets lt+0x54 = 0 (a static core's info by 0x1006e4b0). Return 1.

0x1008bb40, the end:

1. Per core of +0x10 (last to first) whose block's +0x20 is 0: rot (+0xc0..) and q_next (+0x110..) back from it; every +0x1ac = 0.
2. `dt = f32(env+0xf8 - env+0xf0)`; 1 / dt, or 1e10 at or below 1e-10.
3. Per core of +8 (last to first) not static: 0x100970f0(core, {dt, 1/dt, env}, a 256-entry stack list) (the stage-5 rot step, section 7; 0x100974e3 collects the due objects), +0x1ac = 0, its contacts' lt+0x54 = 0.
4. 0x10097db0(env, the list).
5. Per core of +8 (last to first) not static: +0x1a0 = env+0x10c and per object (+0x52 / +0x54, last to first) 0x100730d0: its exact synapses whose two cores' +0x1a0 differ: 0x100982d0 (the stamp already the event's: no new walk) and, bits & 0xc000 clear, 0x10095310.

## 6. The friction system on the world

- The controllers inside the PSI, in the unit's order (a resting kart: [0, drag 500, motion 500..., 600, gravity 1000, 2000], run from the last). 2000 0x10082e70: the caches refreshed at the PSI's time code, the geometry (0x1008d230 per contact), the energy (the unit's flags word: state byte 1, flags & ~0xff; env+0x118). 600 0x10082ff0 (tangential). 0 0x10082f60 (the pressure solve: the mindist settings, env+0xc0, perf +0x18 10).
- A core leaving the system: 0x100810a0, its info's contact vector empty -> 0x100788c0, 0x10087270(system, core): out of +0x2c, the three controllers off the core's list (0x10018430) and the unit's (0x10071dc0: the entry's core removed, an entry without cores freed (0x10071890) and the rest shifted down; from +0x10 (2000), +0 (600), +8 (0)), out of +0x24, +0x3c -= 1; then the core's unit flags `& ~0x200 | 0x100` (0x10081211). Applied after the controller or impact that caused it.
- The system's end: 0x10082f60 with +0x3e == 0: slot 7 0x10086e30 -> 0x10086e60 (vectors freed; the cores left already), then the event's unit (es+0xc) flags `& ~0x200 | 0x100` (0x10082fce). +0x44 set: 0x100815a0 / 0x100816a0 (one dynamic core never reaches it: an emptied pair empties the system).
- The unit's rebuild (0x10072540 at 0x100727ee, after the controllers and the sleep check): flags & 0x300: the controller list cleared (0x10071800), rebuilt (0x100713b0: per core last to first, its own list (+0x140) from its last controller, each appended when new) and sorted (0x10071e40); 0x10071710 (a one-core unit gives no split); flags &= ~0x300. The rebuild reverses the order of equal priorities (motion controllers and drag at 500).
- vphysics' friction listener 0x10011eb0 (Simulate 0x10014320 at 0x100144fe, after IVP's step): skipped while dt (env+0xa8) > `f32(env+0x100) - +0x18`; else +0x18 = f32(env+0x100); per tracked object with CPhysicsObject +0x1c & 2, each friction synapse (object +0x28) whose other object has the flag: cp+0x48 != 0: `energy = cp+0x48 x (1 / elapsed) x core+0x3c`; past 0.05 the game's IPhysicsCollisionEvent::Friction (`energy x 1550.0032`, the surface props through 0x10116078 slot 0x38); cp+0x48 = 0. Only the clear touches state (nothing in IVP reads +0x48).

## 7. The next PSI from an event's time: 0x10096940's stage-5 path

0x10096940 takes 0x10096d56 when core flags & 8 or env+0x114 == 5; from there, without a car wheel (core+0x48 == 0) or with core+8 == 0, 0x10096fe9:

1. `h = dt x 0.5`; `s_i = sinf(h w_i)` (0x100d9542); `n = (s0^2 + s1^2) + s2^2`.
2. n > 1: `s x (0.997 / sqrt(n))` and n again.
3. `q = (s, sqrt(1 - n))`; the rot speed is not touched (no gyroscopic step).

env+0x114 (set in 0x10084fb0): 0 at 0x10084fcf, 2 at 0x100850a5 before stage 4's 0x10097db0, 3 at 0x100850c3 before stage 5's 0x100952d0, 4 at 0x100850df before stage 6, 5 at 0x1008512b after it. Between PSIs, where the mindist events run, it is 5.

## 8. Sleeping and waking on the ground

- A freeze (0x10077820, from 0x100722d0 in stage 2): 0x10077750 -> 0x100775f0 (q_next = q_last, +0x138 = the event's 1/dt, +0x5c 0, speed and delta zero, +0x13c 0, +0x1a4 0, +0x120 = (1, 0, 0); also at a revival). Then per object (+0x52 / +0x54, last to first): +0x44 = 8; 0x10094de0 (two objects at rest no longer pair: the OO watcher and its mindist deleted); the hull manager (+0x48): `d = f32(env+0xf0 - +0)`, `+0x14 += +0xc x d`, `+0x10 += +8 x d`, +0xc = +8 = 0 (its time +0 kept), reset 0x10093bb0; the cache (+0x40) released (its +0x68 = 0, +0x40 = 0). The core still takes this PSI's stage 3 (hull manager time = now, gradients 0).
- A revival (stage 1, 0x10071ef0 -> 0x100778d0): the creation path every time (recheck_ov_element with movement bytes 0x21: a new OO watcher and mindist, [ivp-mindist.md](ivp-mindist.md) 4); 0x10082ce0 (the object's exact mindists not phantom: the other core static -> skipped for a dynamic core (a static pair is deleted, slot 4); the other dynamic without an info: recalc, len below 0x1010d24c -> 0x10088450 and its geometry; [ivp-pileup.md](ivp-pileup.md) 6).
- The friction system survives the sleep (its unit isn't simulated, its controllers don't run); its contacts carry on at the revival.

## Unread

- The sliding friction 0x1007fd70 and the sliding impacts 0x1008b820 / 0x10088cc0 never run on these paths ([ivp-contacts.md](ivp-contacts.md) 7).
- The impact's speed-limit hooks; a core past perf +0xc impacts; a core already in this PSI's impact list (flags & 0xc0, 0x1008a0b2).
- The pressure solve's undo 0x100a0d10; FF minimize 0x100984c0 and the rescue push 0x100980a0 ([ivp-mindist.md](ivp-mindist.md) 10).
- asinf above sqrt(3)/2 (0x100d7b4b, 0x100d7ca5) and cosf's large-argument path 0x100d80e0.
- The listeners (0x10084d60 / 0x10084da0 / 0x10084df0 / 0x10084e90, 0x10086690 / 0x100866f0 / 0x100867c0): vphysics' collision callbacks, no physics state.
- env+0xc0 and env+0x118's formulas (their values taken from the running environment).
