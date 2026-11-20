# CS2's entity I/O event queue (RUST_PORT phase 4b, server.dll 2026-11-05)

Addresses are server_20261105.dll (archived in tools/re/binaries, the Ghidra project's /server_20261105.dll). Code:
sim/src/game/io_queue.rs (the queue), web/src/world/entities/io-queue.js (the payloads and the exports' wrapper),
entities/engine.js (fireOutput / fire / after / cancelPending / tick).

## The event

0xf8 bytes from g_pMemAlloc (180ff2430), freed with 180ff2490 (MemAlloc vfn 0x18).

| Offset | What |
|---|---|
| +0x00 | the time domain: the caller's entity identity +0x38 (0 for a map entity), read by the clock below |
| +0x04 | fire time, f32 |
| +0x08 | 6 from 18137b560 (not traced: read by the name search 181384290) |
| +0x10 | target name (char*) |
| +0x18 | input name (pooled string from the entity system's +0x1f50 table, 180535520) |
| +0x20 | activator handle |
| +0x24 | caller handle (what CancelEvents matches) |
| +0x28 | target entity handle (an event at one entity, not a name), else -1 |
| +0x30 | the value (a variant: type byte +0x38, flags +0x3a bit 0 = owns its string); +0x40 and +0xd0 are passed to the input as well (not traced: Source's outputID and the value's copy are the likely fits) |
| +0xe8 / +0xf0 | next / prev. The list head is the node at entity system +0xb20 (its next is +0xc08) |

The queue's lock is entity system +0xb10 (a recursive CAtomicMutex, owner thread +0xb18, depth +0xb14).

## AddEvent

- The entry points (18137b560 for a target entity, 18137b850 / 18137ba80 / 18137bd40 the name / variant forms)
  allocate the event, read the clock (entity system vfn 0x58 = 180c02860 → 180927cb0) and set the fire time with
  18017dc70: `addss xmm2, [rdx]`, i.e. **f32(delay + now)**, the delay an f32 argument.
- The clock (180927cb0) for domain 0, with gamerules: vfn 0x380 = 180de6a50 → `curtime - pausedTicks (+0xc0) x
  interval` (while paused with a start tick: `(start - paused) x interval`). No pause in ZE: **curtime**, which at 64
  ticks is n/64 exactly. Another domain, or no gamerules: gpGlobals->curtime (+0x30).
- **AddEventInternal** (18137b240): from the head, walk while the event's time compares `<= ` the new one's
  (18017e2d0: -1 / 0 / 1, -128 unordered; the walk stops only on 1), then link after the last one passed. Time order,
  equal times in the order added. The value is deep-copied for string types (switch on +0x38).

## ServiceEvents (18138e480)

GameFrame's I/O step (called from 180dd8a60), after the think pass:

1. From the head: an event whose time compares greater than the clock for its domain is skipped; the first one that
   isn't is serviced. (The list is time-sorted, so skipping is the same as stopping, except for NaN times.)
2. A per-pass counter goes up; at **10001** the whole queue is cleared (18137edf0: every event freed, the head 0)
   and the pass returns.
3. The targets: the handle at +0x28, else the name search (181384290 with the kind, name, activator, caller). Each
   live target (entity flag +0x30 bit 9 clear) gets the input (1813ac4d0: target, input, activator, caller, value,
   output id); a handled one goes to the entity system's input listeners (+0xc20, count +0xc18). None found, or none
   handled: "unhandled input: (%s) -> (%s), from (%s,%s); target entity not found / target input not found" on the
   caller's names.
4. **Then** the event is unlinked and freed, and the walk starts again at the head. So an event added by the dispatch
   with no delay (time = now) is serviced in this same pass, after any already-queued event of that time.

## CancelEvents (18137eb30)

Every event whose caller handle (+0x24) resolves to the entity is unlinked and freed. Callers: logic_relay's
CancelPending (180c40120, which also clears m_bWaitForRefire at +0x4d9), ent_cancelpendingentfires (180ce4c60), and
two others not looked at (180d3dca0, 18057f41a).

**Undefined in CS2**: a dispatch that cancels its own event (a relay's output sending the relay CancelPending, the
event's caller being the relay). CancelEvents frees the in-flight event, and ServiceEvents then unlinks it through its
stale links and frees it again. The port takes it out at the cancel and leaves it alone at the end of the dispatch.

## What the port leaves in JS (phase 4, later steps)

- The dispatch (1813ac4d0, the classes' inputs): engine.input. Since 4e the events themselves live in the sim
  (sim/src/game/entity_system.rs): handles for the caller, activator and a handle target, interned strings for the
  target name, input and value; ServiceEvents resolves the targets there ([io-targets.md](io-targets.md)) and hands
  web/src/world/entities/entity-system.js one job per event.
- A killed entity's handle answers until the next frame starts (engine.dying: a stand-in for CS2's deferred
  delete, whose place in the frame isn't traced); after that a queued event's caller or activator that was it is
  null, as a dead handle is in CS2.
- The value's type: the JS passes the parameter string; CS2 keeps a variant (+0x30) with its type.
- The delay's parse: entities.json carries it as a JSON number, which the sim rounds to f32 (`f32(f64(text))`; CS2
  parses the text to a float: the same except for a double-rounding case at a halfway f32).
- engine.after (the engine's own timed callbacks: env_spark, ambient_generic's OnSoundFinished, items.js): stand-ins
  for CS2's thinks, queued as events with no caller so they keep their order with the map's.
