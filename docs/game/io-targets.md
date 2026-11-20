# CS2's I/O targets and connections (RUST_PORT phase 4c, server.dll 2026-11-05)

Who an output's event goes to, and in what order an output's connections fire. Addresses are server_20261105.dll
(archived in tools/re/binaries); the glob is tier0's. Code: web/src/world/entities/targets.js (the search), entity.js /
keyvalues.js (the connection order). The queue itself: [io-queue.md](io-queue.md).

## An output's connections

- A connection is 0x50 bytes: +0x00 target name, +0x08 input name, +0x10 override value (string), +0x18 target
  handle, +0x1c target type, +0x20 times to fire, +0x24 delay (f32), +0x28 its variant value, +0x40 a "being removed"
  byte, +0x48 next. The output holds the list head at +0x08.
- **AddEventAction** (180ebf120) links a new connection at the **head**. Spawn (1813762d0) walks the entity's lump
  connections in order and adds each one (FUN_1813aca70 finds the outputs by name), so the list ends up in reverse:
  **an output fires its last-listed connection first.** AddOutput (1813aa560: `output>target>input>param>delay>times`,
  V_StringToFloat32 / V_StringToInt32, type 7) adds the same way, ahead of what the output had. A script's
  connection (181391990) does too, with target type 6 (an entity handle).
- **FireOutputInternal** (181392440), per connection in list order: the value (the connection's override string, type
  0x1e, else the output's own); the delay f32(connection delay + the fire's delay); a type 6 connection queues an
  event at its handle (18137b850), any other a name event with that type (18137bd40). Then the fire count: -1 keeps it,
  else it's decremented and removed when it reaches 0 (as the JS did). The entity system's I/O listeners
  (+0xc20, count +0xc18) see each connection before (vfn 0x18) and after (vfn 0) it fires, and its removal (vfn 0x10).

## The target search (181384290, from ServiceEvents)

Target type 2 searches names only, 7 names then classes; anything else logs "Encountered unknown entity i/o target
type!" and finds nothing. The caller is passed as the searching entity too.

1. **A name** (181383f30):
   - starting with `!`: one entity from CGameEntitySystem vfn 0x68 (180bfdea0): `!player` = player slot 0's pawn
     (180cbce60(0): controller index 1 → its pawn), `!pvsplayer` = a player in the caller's PVS (else the activator's,
     else slot 0's: thunk 180fe9da0, not traced), `!picker` = what slot 0 aims at (gamerules vfn 200), `!parent` =
     the caller's parent (1803d9790), `!owner` = its owner (1809299d0); then a game system's vfn 0xa0 (DAT_18218bff8,
     not traced); then CEntitySystem's (181384580): `!activator`, `!caller`, `!self` (= the caller), else the caller's
     adopted name `__procedural_adopted_targetname_<name>` (a script feature). Nothing: "Invalid entity search name".
   - with a `*` in it: every entity in the entity list (+0x210, next +0x58) that isn't being deleted (+0x30 bit 9), has
     a name and matches **V_CompareNameWithWildcards(pattern, name, 0)** (tier0 18000d4d0: `*` any run, `?` one
     character, ASCII case-insensitive), in list order.
   - else: the name table (entity system +0xaf0, a map keyed by the interned name; names are interned through
     +0x1f50, hashed lower-cased: murmur2 seed 0x31415926 over the lower-cased string, 18054ba10), its handles in order.
     A name's handles are a CUtlVector: an entity taking the name is **appended** (18137bf80, AddToTail 18137c860,
     not if already there); one dropping it is **swap-removed** (18138b030: the last handle moves into its slot). A
     rename (1813ad490) removes then adds, so the renamed entity goes last; deletion (1813ab380, the entity's
     destruction) removes; 1813aa910 removes / re-adds on a state change (its param 1, not identified).
2. **None found and type 7, the class** (181384290 after the name): a pattern with `*` walks the entity list for the
   first entity whose class (identity +0x20) matches and continues through the list with the same test (181389270);
   else the class table (+0xab0, with an alias table DAT_182331e70 tried when the name isn't a class) and that class's
   own list (class entry +0x110, next +0x68). A class list is **prepended** (181373e40), so it runs newest first;
   181376080 unlinks.
3. Each target that isn't being deleted gets the input (1813ac4d0: the class's input table 181373b60, then the
   entity's vfn 0x88, then a script's `Input<name>`); "unhandled input ... target entity not found / target input not
   found" otherwise.

## What the port does, and its stand-ins

- **The sim's entity list** (sim/src/game/entity_list.rs, inside entity_system.rs's EntitySystem, `ze_es_*`;
  web/src/world/entities/entity-system.js): every entity and player by handle (an entity's id; a player's
  0x40000000 | id) with its interned name and class, the list order, the name table (append / swap-remove) and the
  class lists (newest first). engine.js tells it each spawn, kill, rename and player join / leave. ServiceEvents
  resolves each event there: a handle target, the `!` names (`!activator`, `!caller`, `!self`, `!player` /
  `!pvsplayer`), the name / glob / class search; `!parent` / `!owner` come back unresolved for targets.js (they
  need the hierarchy). `wildcard_match` is tier0's glob, checked against the DLL (rubikon/tests/WildcardOracle +
  the wildcard_check bin: 0 of 1,000,000 differ).
- **When a killed entity leaves the name table**: at the kill (CS2: when it's deleted, after the frame's events;
  the order differs only if a name gains an entity in between). TODO: trace the deletion's place in the frame.
- **Every connection is type 7**: entities.json doesn't carry the lump's target type (bake/Program.cs writes the
  connections without it). TODO: bake it, and search names only for type 2.
- **Players' place in the list**: where they join the round (after the map's entities at a round start); a pawn's
  place in CS2's list isn't traced. The map's entities are in creation order, which looks like CS2's list order:
  18137cd30 links a new identity at the tail of a list with head / tail / count (read in the decompiler only; which
  of the entity system's lists that is, relative to +0x210, isn't confirmed).
- `!player` / `!pvsplayer`: the first player in the round (CS2: player slot 0's pawn; the PVS search isn't traced).
  `!picker`, the vfn 0xa0 system and adopted names find nobody.
- engine.find (parentname, SetParent, scripts, KeyValues targets) is still the trainer's search: those are CS2's other
  lookups (FindEntityByName and friends), to trace with their callers.
