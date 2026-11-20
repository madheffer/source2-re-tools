# Entity I/O event queue

server_20261105.

## Functions

| Address | Module | What |
|---|---|---|
| 180ff2430 | server | g_pMemAlloc alloc (the 0xf8-byte event) |
| 180ff2490 | server | free (MemAlloc vfn 0x18) |
| 18137b560 | server | AddEvent, target entity form (also sets +0x08 = 6) |
| 18137b850 / 18137ba80 / 18137bd40 | server | AddEvent, name / variant forms |
| 180c02860 | server | entity system vfn 0x58: the clock -> 180927cb0 |
| 180927cb0 | server | clock for a time domain |
| 180de6a50 | server | gamerules vfn 0x380: paused-adjusted curtime |
| 18017dc70 | server | fire time: `addss xmm2, [rdx]` = f32(delay + now) |
| 18137b240 | server | AddEventInternal: time-ordered insert |
| 18017e2d0 | server | f32 compare: -1 / 0 / 1, -128 unordered |
| 180535520 | server | pooled input name (entity system +0x1f50 table) |
| 18138e480 | server | ServiceEvents (called from 180dd8a60, GameFrame, after the think pass) |
| 18137edf0 | server | clear the whole queue (every event freed, head 0) |
| 181384290 | server | target name search (kind, name, activator, caller) |
| 1813ac4d0 | server | dispatch the input (target, input, activator, caller, value, output id) |
| 18137eb30 | server | CancelEvents (entity) |
| 180c40120 | server | logic_relay CancelPending (also clears m_bWaitForRefire +0x4d9) |
| 180ce4c60 | server | ent_cancelpendingentfires |
| 180d3dca0, 18057f41a | server | other CancelEvents callers (unread) |

## Fields

| Offset | Field |
|---|---|
| event +0x00 | time domain: the caller's entity identity +0x38 (0 for a map entity) |
| event +0x04 | fire time, f32 |
| event +0x08 | 6 from 18137b560 (read by 181384290; untraced) |
| event +0x10 | target name (char*) |
| event +0x18 | input name (pooled string) |
| event +0x20 | activator handle |
| event +0x24 | caller handle (what CancelEvents matches) |
| event +0x28 | target entity handle, else -1 |
| event +0x30 | value variant: type byte +0x38, flags +0x3a bit 0 = owns its string |
| event +0x40, +0xd0 | also passed to the input (untraced: likely outputID and the value's copy) |
| event +0xe8 / +0xf0 | next / prev |
| entity system +0xb20 | list head node (its next is +0xc08) |
| entity system +0xb10 | queue lock: recursive CAtomicMutex (owner thread +0xb18, depth +0xb14) |
| entity system +0xc20 / +0xc18 | input listeners / count |
| entity +0x30 bit 9 | dead (skipped as a target) |
| gamerules +0xc0 | paused ticks |
| gpGlobals +0x30 | curtime |

## Constants

| Value | What |
|---|---|
| 0xf8 | event size |
| 10001 | events per ServiceEvents pass before the whole queue is cleared |

## AddEvent

1. Allocate, read the clock, fire time = **f32(delay + now)** (delay an f32 argument).
2. Clock (180927cb0), domain 0 with gamerules: 180de6a50 = `curtime - pausedTicks (+0xc0) x interval` (paused with a start tick: `(start - paused) x interval`). Unpaused: curtime (n/64 exactly at 64 ticks). Other domain or no gamerules: gpGlobals->curtime (+0x30).
3. AddEventInternal: from the head, walk while the event's time compares `<=` the new one's (18017e2d0; stops only on 1), link after the last passed. Time order, equal times in the order added. String-type values deep-copied (switch on +0x38).

## ServiceEvents (18138e480)

1. From the head: an event whose time compares greater than its domain's clock is skipped; the first one that isn't is serviced (sorted list: skip = stop, except NaN times).
2. Per-pass counter +1; at 10001 the queue is cleared (18137edf0) and the pass returns.
3. Targets: the handle at +0x28, else 181384290. Each live target gets 1813ac4d0; a handled one goes to the input listeners. None found / none handled: "unhandled input: (%s) -> (%s), from (%s,%s); target entity not found / target input not found" on the caller's names.
4. **Then** the event is unlinked and freed, and the walk restarts at the head: an event added by the dispatch with no delay is serviced in the same pass, after already-queued events of that time.

## CancelEvents (18137eb30)

- Every event whose caller handle (+0x24) resolves to the entity is unlinked and freed.
- Undefined: a dispatch that cancels its own event (a relay's output sending the relay CancelPending): CancelEvents frees the in-flight event, and ServiceEvents then unlinks it through its stale links and frees it again.

## Unread

- Event +0x08 (6), +0x40, +0xd0.
- CancelEvents callers 180d3dca0, 18057f41a.
- Where in the frame a killed entity's deferred delete lands.
- The delay's text parse (CS2 parses the text to a float).
- Target resolution: [io-targets.md](io-targets.md).
