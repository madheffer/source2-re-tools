# The weapon list's flash on a new weapon (hudweaponselection)

client_20261015. hudweaponselection.vcss.

## Functions

| Address | Module | What |
|---|---|---|
| 180eb8970 | client | fills the panel's class-token table at 0x1822452b8 |
| 180ea7660 | client | item added (bought, picked up, given): item --active (count 0) else --active-pop; row weapon-row--active |
| 180eabe10 | client | the animation-disable count; only Debug_EnableAnimation (180ec8100) calls it |
| 180ec6b10 | client | item count changed: count > 1 that went up re-triggers --active (vfn 0x510); --has-multiple, WeaponIcon--itemcount |
| 180eac3d0 | client | item removed: --active off, --deleted on, 0.2 s delete |

## Fields

| Offset | Field |
|---|---|
| panel +0x70 | animation-disable count (0 in play: weapon-selection--animation-enable stays on, every new item flashes) |

## Class tokens (0x1822452b8)

| +off | Class |
|---|---|
| +2 | WEAPON-ICON |
| +4 | weapon-selection--hidden |
| +6 | weapon-selection--fade |
| +8 | weapon-selection--animation-enable |
| +0xa | weapon-selection--bomb-zone |
| +0xc | weapon-row--active |
| +0xe | weapon-row--deleted |
| +0x10 | weapon-row--selected |
| +0x12 | weapon-row--anim |
| ... | |
| +0x2a | weapon-selection-item--active |
| +0x2c | weapon-selection-item--active-pop |
| +0x2e | weapon-selection-item--deleted |
| +0x30 | weapon-selection-item--selected |
| +0x32 | weapon-selection-item--has-multiple |
| +0x34 | weapon-selection-item--show-owner |
| +0x36 | weapon-selection-item--fade-ok |
| +0x38 | hud-colorize-wash--hsv |

## Styles (hudweaponselection.vcss)

`.weapon-selection--animation-enable .weapon-selection-item--active`, each 0.4 s linear x 8:
- name and icon on-active: opacity / brightness 1 / 1 to 49 %, 0.5 / 4 at 50 %, 0.5 / 2 at 99 %, 1 / 1.
- icon on-active-scale: 1.1 at 50 %.
- icon's main image on-active-icon: brightness 1, 0.2 at 49 %, 4 at 50 %, 0.2 at 99 %, 1.
- row background weapon-row--on-active: the same way.
