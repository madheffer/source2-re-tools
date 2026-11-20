# I/O targets and connections

server_20261105; the glob is tier0's. Who an output's event goes to, and in what order an output's connections fire. The queue itself: [io-queue.md](io-queue.md).

## Functions

| Address | Module | What |
|---|---|---|
| 180ebf120 | server | AddEventAction: links a new connection at the head |
| 1813762d0 | server | Spawn: walks the entity's lump connections in order and adds each |
| 1813aca70 | server | finds an output by name |
| 1813aa560 | server | AddOutput: `output>target>input>param>delay>times` (V_StringToFloat32 / V_StringToInt32), type 7, at the head |
| 181391990 | server | a script's connection: type 6, at the head |
| 181392440 | server | FireOutputInternal |
| 18137b850 | server | queue an event at a handle |
| 18137bd40 | server | queue a name event with a target type |
| 181384290 | server | the target search (from ServiceEvents) |
| 181383f30 | server | search a name |
| 180bfdea0 | server | CGameEntitySystem vfn 0x68: the `!` names |
| 180cbce60 | server | (0): controller index 1 -> its pawn (`!player`) |
| 180fe9da0 | server | thunk for `!pvsplayer` (not traced) |
| 1803d9790 | server | parent (`!parent`) |
| 1809299d0 | server | owner (`!owner`) |
| 181384580 | server | CEntitySystem's `!` names: `!activator`, `!caller`, `!self`, adopted names |
| 18000d4d0 | tier0 | V_CompareNameWithWildcards(pattern, name, 0): `*` any run, `?` one character, ASCII case-insensitive |
| 18054ba10 | server | name hash: murmur2 seed 0x31415926 over the lower-cased string |
| 18137bf80 | server | an entity takes a name: append (AddToTail 18137c860), not if already there |
| 18137c860 | server | CUtlVector AddToTail |
| 18138b030 | server | an entity drops a name: swap-remove (the last handle moves into its slot) |
| 1813ad490 | server | rename: remove then add (the renamed entity goes last) |
| 1813ab380 | server | deletion (the entity's destruction): removes the name |
| 1813aa910 | server | removes / re-adds the name on a state change (its param 1, not identified) |
| 181389270 | server | class glob: continue through the entity list with the same test |
| 181373e40 | server | class list prepend (newest first) |
| 181376080 | server | class list unlink |
| 1813ac4d0 | server | deliver an input: the class's input table (181373b60), the entity's vfn 0x88, then a script's `Input<name>` |
| 181373b60 | server | the class's input table |
| 18137cd30 | server | links a new identity at the tail of a list with head / tail / count (decompiler only; which list, relative to +0x210, unconfirmed) |

## Fields

| Offset | Field |
|---|---|
| connection +0x00 | target name |
| connection +0x08 | input name |
| connection +0x10 | override value (string) |
| connection +0x18 | target handle |
| connection +0x1c | target type |
| connection +0x20 | times to fire |
| connection +0x24 | delay (f32) |
| connection +0x28 | its variant value |
| connection +0x40 | "being removed" byte |
| connection +0x48 | next |
| output +0x08 | connection list head |
| entity system +0x210 / entity +0x58 | entity list / next |
| entity +0x30 bit 9 | being deleted |
| identity +0x20 | class |
| entity system +0xaf0 | name table (keyed by the interned name; handles in a CUtlVector) |
| entity system +0x1f50 | name interning |
| entity system +0xab0 | class table |
| class entry +0x110 / +0x68 | class's entity list / next |
| entity system +0xc20 / +0xc18 | I/O listeners / count |

## Constants

| Value | What |
|---|---|
| 0x50 | connection size |
| type 2 | names only |
| type 7 | names, then classes |
| type 6 | an entity handle |
| 0x1e | the override string's variant type |
| DAT_182331e70 | class alias table (tried when the name isn't a class) |
| DAT_18218bff8 | a game system whose vfn 0xa0 resolves `!` names (not traced) |

## Connection order

- Spawn adds the lump's connections in order at the head, so the list ends up reversed: an output fires its last-listed connection first. AddOutput and script connections go ahead of what the output had.

## FireOutputInternal (181392440), per connection in list order

1. Value: the connection's override string (type 0x1e), else the output's own.
2. Delay: `f32(connection delay + the fire's delay)`.
3. Type 6: event at its handle (18137b850); any other: a name event with that type (18137bd40).
4. Fire count: -1 keeps it; else decremented, removed at 0.
5. I/O listeners see each connection before (vfn 0x18) and after (vfn 0) it fires, and its removal (vfn 0x10).

## The target search (181384290)

Type 2 searches names only, 7 names then classes; any other logs "Encountered unknown entity i/o target type!" and finds nothing. The caller is passed as the searching entity too.

1. A name (181383f30):
   - `!` prefix: CGameEntitySystem vfn 0x68 (180bfdea0): `!player` = player slot 0's pawn (180cbce60(0)), `!pvsplayer` = a player in the caller's PVS (else the activator's, else slot 0's; 180fe9da0), `!picker` = what slot 0 aims at (gamerules vfn 200), `!parent` (1803d9790), `!owner` (1809299d0); then DAT_18218bff8's vfn 0xa0; then 181384580: `!activator`, `!caller`, `!self` (= the caller), else the caller's adopted name `__procedural_adopted_targetname_<name>` (a script feature). Nothing: "Invalid entity search name".
   - with a `*`: every entity in the entity list (+0x210, next +0x58) not being deleted, with a name matching `V_CompareNameWithWildcards(pattern, name, 0)`, in list order.
   - else: the name table (+0xaf0), its handles in order (append on take, swap-remove on drop).
2. None found and type 7, the class: a `*` pattern walks the entity list for the first entity whose class (identity +0x20) matches and continues with 181389270; else the class table (+0xab0, alias table DAT_182331e70) and that class's list (newest first).
3. Each target not being deleted gets the input (1813ac4d0); otherwise "unhandled input ... target entity not found / target input not found".

## Unread

- The deletion's place in the frame (a killed entity leaves the name table when deleted, after the frame's events).
- A pawn's place in the entity list; which list 18137cd30 links into.
- The `!pvsplayer` PVS search (180fe9da0); the vfn 0xa0 game system (DAT_18218bff8).
- CS2's other lookups (FindEntityByName and friends: parentname, SetParent, scripts, KeyValues targets), to trace with their callers.
