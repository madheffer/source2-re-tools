# The weapon list's flash on a new weapon (hudweaponselection)

client_20261015.dll. Ported in web/src/ui/hud.js itemAdded + hud.css.

- **180eb8970** fills the panel's class-token table at 0x1822452b8: +2 WEAPON-ICON, +4 weapon-selection--hidden,
  +6 --fade, +8 weapon-selection--animation-enable, +0xa --bomb-zone, +0xc weapon-row--active, +0xe --deleted,
  +0x10 --selected, +0x12 --anim, ... +0x2a weapon-selection-item--active, +0x2c --active-pop, +0x2e --deleted,
  +0x30 --selected, +0x32 --has-multiple, +0x34 --show-owner, +0x36 --fade-ok, +0x38 hud-colorize-wash--hsv.
- **180ea7660** (an item added to the list: a weapon bought, picked up or given): the new item gets
  weapon-selection-item--active when the panel's animation-disable count (+0x70) is 0, else --active-pop; its row
  weapon-row--active.
- **180eabe10** (the count): only the debug panel's Debug_EnableAnimation calls it (180ec8100), so in play the count is
  0 and weapon-selection--animation-enable stays on: every new item flashes.
- **180ec6b10** (an item's count, e.g. a second flashbang): a count above 1 that went up re-triggers
  weapon-selection-item--active (vfn 0x510); weapon-selection-item--has-multiple and WeaponIcon--itemcount.
- **180eac3d0** (removed): weapon-selection-item--active off, deleted on, a 0.2 s delete.
- hudweaponselection.vcss: `.weapon-selection--animation-enable .weapon-selection-item--active` name and icon:
  on-active (opacity 1 / brightness 1 to 49 %, 0.5 / 4 at 50 %, 0.5 / 2 at 99 %, 1 / 1) and the icon on-active-scale
  (1.1 at 50 %), the icon's main image on-active-icon (brightness 1, 0.2 at 49 %, 4 at 50 %, 0.2 at 99 %, 1), each
  0.4 s linear x 8; the row background weapon-row--on-active the same way.
- Ours: a row per slot (not CS2's item per weapon), so a row shown again, a new gun / pistol in its row, another
  grenade kind or a grenade count going up flash the row. Not ported: the row background's blink, --active-pop.
