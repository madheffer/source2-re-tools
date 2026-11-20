# CS2's touches (RUST_PORT phase 4 groundwork, 2026-11-09)

What decides that a player touches a trigger or a weapon, for the move of triggers.js' hull overlaps and items.js'
reach box onto CS2's own touch pipeline.

## Known (rubikon/CS2_RUNTIME.md "Trigger touches" and "Physboxes in hurt, push and teleport triggers")

- Touches are vphysics2's: a shape pair whose contact flags keep bit 2 (the pair filter, both function masks with 4)
  counts per body pair; the events are collected for the game by world vfn 0x3d0 (180059170) and dispatched by the
  server's OnSimulate right after the physics step (18057ad70): bit 4 StartTouch (vfn 0x4b0, then Touch vfn 0x4b8,
  both ways), bit 8 touch persist (Touch both ways), bit 0x10 EndTouch. CBaseEntity::Touch (vfn 0x4b8, index 151)
  runs the entity's m_pfnTouch (+0x2b0). Trigger records and the pair test are ported for physboxes
  (rubikon/src/Game/TriggerPhysics.cs, physics-touch.js).
- CS2Fixes hooks the touch list: CVPhys2World vfn 122 GetTouchingList (CUtlVector<TouchLinked_t>, 256 bytes each:
  flags +0 (4 / 8 touching, 0x10 untouching), source handle +0x18, target handle +0x1c). With
  `cs2f_shuffle_player_physics_sim` on (default off), it shuffles the touching links each tick (std::srand(tickcount),
  MSVC rand, Fisher-Yates) and puts the untouching ones after: a 1:1 port of a server running it needs MSVC's rand
  and the same list order.
- A weapon on the ground is picked up by its own touch (docs/game/pickups.md): CCSWeaponBase::DefaultTouch
  1809fb3c0 → BumpWeapon.

## Open

- **Players have no bodies in the sim's world**, so none of this reaches them today: triggers.js overlaps the player's
  hull with trigger hulls and items.js uses a reach box. CS2's player pawn has physics (its collision property's
  bounding box shape on the player layer, interacts-as 0x40000, as movement's filter says); how the server creates and
  moves it (the solid type, the shape, its function mask with the touch bit) is the next trace: server.dll's
  CCollisionProperty / the pawn's physics creation, then where its body follows the movement each tick.
- The order the touch events reach the game (the pair list order) decides which trigger fires first in a tick.
