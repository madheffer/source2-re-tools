# Rubikon: joints in a graph-coloured island

How vphysics2 solves the joints of an island that has a graph colouring (an island with 100 or more contacts in a
contact group: a pile of death ragdolls). Ported in rubikon/src/Simulation/WorldSolver.cs (`ColouredJointOrder`, and
`SolveIsland` taking the joint order), checked by rubikon/tests/ColourJointOracle against Valve's own functions.

Addresses are **vphysics2_20260924.dll** (sha256 0f896375...; image base 0x180000000; source2-compiler
tools/re/binaries, Ghidra `/vphysics2_20260924.dll`). source2-compiler's docs/ADDRESSES.md names some of them
(RnSolver_BuildColoured, RnSolver_ChainColouredJobs, RnSolver_PrepareJoints, ...).

## The plan (FUN_180338710, RnSolver_BuildColoured)

The coloured island's plan, built in the solve's arena (param_3 is the bump cursor). Plan fields (8-byte slots):

| Plan | What |
|---|---|
| +0x00 / +0x08 | copied from param_6 (the island's body range) |
| +0x10 | the solver bodies (0xc0 each), allocated here: count x 0xc0 |
| +0x18 (byte) | world +0x44 (sleeping on) |
| +0x20 | the island context (param_2) |
| +0x28 / +0x2c | velocity / position iterations (param_4 / param_5) |
| +0x30 + 0x10 k | job lists {pointer, count}, k = phase + 3 .. phase + 9 (phase 0): 3 joints in parallel (0x40 jobs), 4 joints whole (0x28 jobs), 5 / 6 the type-1 constraints (FUN_180338030, not ported), 7 + g contacts of group g in parallel (0x40 jobs), 9 + g contacts whole (0x28 jobs) |
| +0xb0 | the chain's total chunk count |
| +0xb4 | the widest job (chunks), raised by each builder |
| +0xb8 / +0xc0 | the job chain: count and array (0x28 a job), allocated last: ((position + 1 + velocity) x jobs + 3) x 0x28 |

Called in order: FUN_180337c00 (joints), FUN_180338030 (type-1 constraints), FUN_1803377d0 for group 0 then 1
(contacts). param_5 ends as the number of jobs per pass (each builder adds its job count).

### The joint jobs (FUN_180337c00)

The island's colouring is 17 buckets of 0x50 (0..15 colours, 16 the overflow at bucket +0x500). Bucket +0x00 is the
joints' vector (count +0, capacity +4 with bit 31 a flag, pointer +8: a capacity of 0 reads as no pointer), +0x10 the
type-1 constraints', +0x20 / +0x30 the contacts' per group, +0x40 the joints' size sum, +0x44 the type-1 sum, +0x48 /
+0x4c the contacts' per group. Joints take only colours 0..9 (FUN_1802ca6c0, bits 0..9 of a body's mask), so buckets
10..15 hold no joint.

Two walks over the 17 buckets, in bucket order:

1. Buckets with more than **8** joints, the overflow excepted: a parallel job each (list 3, 0x40 bytes): +0 the
   joints' pointer, +8 the count, +0x10 the plan, +0x18 the bucket's stream (size +0x40 rounded up to 16, from the
   arena), +0x20 that size, +0x28 the chunk table ((count + 7) / 8 entries of 0x10, from the arena), +0x30 its
   length, +0x38 the stream cursor (an atomic store of +0x18). Plan +0xb4 = max(itself, chunks).
2. Buckets with 1..8 joints, and the overflow bucket at any count: a whole job each (list 4, 0x28 bytes): +0 pointer,
   +8 count, +0x10 the plan, +0x18 the stream, +0x20 its size. Plan +0xb4 = max(itself, count).

The contacts' builder FUN_1803377d0 is the same with 4 for 8 (chunks of four), lists 7 + g / 9 + g, sizes +0x48.

## The chain (FUN_1803109c0, RnSolver_ChainColouredJobs)

The jobs in the order one thread runs them; jobs run one after another (+0x10 links each to the next), a parallel
job's chunks on any thread. A job is {function, argument, next, kind (2 chunked / 1 whole), chunks, ...}.

1. FUN_180310970: the bodies' build and integrate, chunks of 8 bodies.
2. Prepare: FUN_18030dca0 (the joint jobs: FUN_180310010 for list 3, FUN_180310230 for list 4), FUN_18030e2c0 (type-1:
   FUN_180310070 / FUN_180310290), FUN_18030d680 for group 0 then 1 (contacts: FUN_18030ffb0 / RnSolver_PrepareContacts).
3. Per velocity iteration i (plan +0x28 of them; the last flagged): FUN_18030de80 (joints: FUN_180312470 / FUN_180312650,
   on the last FUN_180312a00 / FUN_180312cc0), FUN_18030e490 (type-1), FUN_18030d860 per group (contacts).
4. FUN_1803103c0 (positions) or FUN_1803105a0 (positions and the sleep test) when plan +0x18 (sleeping) is set.
5. Per position iteration (plan +0x2c): FUN_18030e0e0 (joints: FUN_180311e60 / FUN_1803120f0), FUN_18030e6e0 (type-1),
   FUN_18030dac0 per group (contacts).
6. FUN_180310850: the writeback.

So in every pass the joints come first, list 3 then list 4, then the type-1 constraints, then the contacts: the serial
island's order (RnSolver_SolveSerial FUN_180310dc0: island +0x38's joints first), with the joints in bucket order.

## The joint workers

Each runs the serial island's code per joint; the parallel ones claim chunks of eight with an atomic counter
(param_2[0], the chunks done added to *param_2[1]) and keep one stream per chunk.

| Job | Calls | What |
|---|---|---|
| FUN_180310010 | FUN_18030eb50 | prepare, chunked: per chunk the joints' sizes (+0xa8) summed (pairs, then the odd one: `(a0 + a2 + ..) + (a1 + a3 + ..) + last`, integers), that much taken from the job's cursor +0x38 (atomic add), the chunk table entry +0x28 + 0x10 chunk = {stream, length}; per joint the record of FUN_18030f0b0 (inlined, byte for byte the same: the 0x12 skip when both bodies are infinite in a tested axis, the header with the priority scales, the type's vtable +0x28 with warm 1) |
| FUN_180310230 | FUN_18030f0b0 | prepare, whole (RnSolver_PrepareJoints): the job's stream +0x18, its length written to +0x20 |
| FUN_180312470 | FUN_18030fb00 | velocity, chunked: each chunk's stream from the chunk table |
| FUN_180312650 | (itself) | velocity, whole (RnSolver_VelocityIterationJoints) |
| FUN_180312a00 | FUN_18030f500 | the last velocity, chunked: per joint the type's solve and store (the same calls as FUN_18030f860: types 2..14), the break test (vtable +0x38), a broken joint to world +0x88 +0x30 (FUN_1801f0ef0), so its order there follows the threads |
| FUN_180312cc0 | FUN_18030f860 | the last velocity, whole (RnSolver_LastVelocityIterationJoints) |
| FUN_180311e60 | FUN_18030f250 | position, chunked: the same type switch as FUN_1803120f0 (record 9 skips 0x8c bytes) |
| FUN_1803120f0 | (itself) | position, whole (RnSolver_PositionIterationJoints) |

A worker's context (param_3): [0] the address of {the joints' pointer, count}, [1] the address of the solver bodies'
pointer, [2] the address of dt (prepare) or of the world (the last velocity's break list).

Joints of one colour share no dynamic body (a static or keyframed one may be shared; its solver body never moves), so
the chunks' order changes no float: the port runs a bucket's joints in bucket order. Only the broken-joint list's order
follows the threads, and the port still refuses a broken joint (RnWorld.Step: breaking is not ported).

## Checked

rubikon/tests/ColourJointOracle (`dotnet run -c Release -- <source2-compiler>/tools/re/binaries 6000`):
- FUN_180337c00 on 6000 random bucket sets (24211 wide buckets, 48049 small, 4518 overflow): the joints its lists 3
  and 4 name, in order, equal ColouredJointOrder, and its job count equals the lists' lengths.
- FUN_18030eb50 / FUN_18030fb00 / FUN_18030f500 / FUN_18030f250 on random joint buckets (up to 40 conical and revolute
  joints, 4012 trials of more than one chunk), one thread claiming every chunk: every byte of the bodies and the
  joints equals JointSolver's after the prepare, each velocity iteration and each position iteration (2987 trials;
  the rest went NaN on a zero effective mass and stop uncompared).
- The port alone: a colour (joints with no dynamic body in common) solved forwards and backwards gives the same bytes
  (3943 trials).

On ze_dark_souls, 20 death ragdolls dropped on one spawn (RagdollSim's world): master's rubikon threw at tick 78 with
10 ragdolls ("joints in a coloured island ... are not ported"); with the port all 640 ticks run, the poses equal on two
runs, and the first 77 ticks' poses equal master's.

## Not read

- FUN_180338030 / the type-1 constraint workers (FUN_180310070, FUN_180310290, FUN_18030e490, FUN_18030e6e0): a
  ragdoll has none; the port keeps no type-1 list.
- FUN_1801f0ef0 (the broken-joint list's add) beyond its call: breaking is not ported.
