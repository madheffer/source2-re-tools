# Touches (triggers, weapons)

server.dll, vphysics2.dll. CS2Fixes' touch-list hook (`cs2f_shuffle_player_physics_sim`).

## Functions

| Address | Module | What |
|---|---|---|
| 180059170 | vphysics2 | world vfn 0x3d0: collects the touch events for the game |
| 18057ad70 | server | OnSimulate: dispatches the touch events right after the physics step |
| 1809fb3c0 | server | CCSWeaponBase::DefaultTouch -> BumpWeapon (a ground weapon's pickup, [pickups.md](pickups.md)) |

## Vtable slots

| Slot | What |
|---|---|
| entity vfn 0x4b0 | StartTouch |
| entity vfn 0x4b8 (index 151) | CBaseEntity::Touch: runs m_pfnTouch (+0x2b0) |
| CVPhys2World vfn 122 | GetTouchingList (CUtlVector<TouchLinked_t>) |

## Fields

| Offset | Field |
|---|---|
| entity +0x2b0 | m_pfnTouch |
| TouchLinked_t (256 bytes) +0 | flags: 4 / 8 touching, 0x10 untouching |
| TouchLinked_t +0x18 / +0x1c | source handle / target handle |

## Touch events

- A shape pair counts when its contact flags keep bit 2 (the pair filter: both function masks with 4), per body pair.
- Bit 4: StartTouch (vfn 0x4b0), then Touch (vfn 0x4b8), both ways. Bit 8: touch persist (Touch both ways). Bit 0x10: EndTouch.
- The pair list order decides which trigger fires first in a tick.

## CS2Fixes shuffle

`cs2f_shuffle_player_physics_sim` (default off) hooks GetTouchingList: shuffles the touching links each tick
(std::srand(tickcount), MSVC rand, Fisher-Yates) and puts the untouching ones after.

## Unread

- The player pawn's physics: its collision property's bounding box shape on the player layer (interacts-as 0x40000, per
  movement's filter); how the server creates and moves it (solid type, shape, function mask with the touch bit):
  server.dll's CCollisionProperty / the pawn's physics creation, then where its body follows the movement each tick.
