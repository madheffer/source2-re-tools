# A gun's muzzle flash and shell

client_20261015 (schema names from client_20261105), particles.dll 2026-11-12 (md5 b10c5654…). Content: pak01
(scripts/weapons.vdata, animation/anims, the vpcfs).

## Functions

| Address | Module | What |
|---|---|---|
| 0x18080a520 | client | tag filter (both handlers) |
| 0x1808ebfd0 | client | pawn's anim event handler |
| 0x180c7bdb0 | client | the local player |
| 0x1808538e0 | client | active weapon via pawn +0x12f0 (when pawn +0x25e8 is null) |
| 0x1810d7270 | client | viewmodel's anim event handler |
| 0x1808cc9c0 | client | the viewmodel's weapon |
| 0x180c770c0 | client | FormatViewModelAttachment (the tracers') |
| 0x180289490 | particles | C_OP_ChooseRandomChildrenInGroup Operate (pre-emission, slot 0x110; vtable 0x18051f3a8) |
| 0x18003ff50 | particles | restart a child (time 0) |
| 0x18004c500 | particles | stop a child, particles removed (k, 0, 1, 1, 0) |

## Fields

| Offset | Field |
|---|---|
| CBasePlayerWeaponVData (schema entries 0x182231660..) +0x2d0 | m_sMuzzleAttachment |
| +0x2f0 | m_szMuzzleFlashParticle |
| +0x3d0 | m_szMuzzleFlashParticleConfig ("Effect Config for Muzzle Flash - if set, will use this config specified in the particle effect...") |
| +0x3d8 | m_szBarrelSmokeParticle |
| +0x4b8 | m_nMuzzleSmokeShotThreshold |
| +0x4bc | m_flMuzzleSmokeTimeout |
| +0x4c0 | m_flMuzzleSmokeDecrementRate |
| +0x4c4 | m_bGenerateMuzzleLight |
| +0x4e4 | m_iRumbleEffect (controller rumble id: 1 / 2 / 4 / 9 / -1 per gun) |
| weapon vdata +0x728 | silencer type (1: detachable) |
| weapon vfn 0xd20 | silencer state |
| event +0x2e | flag (unread) |
| event +0x30 -> +0x30 | tags string |
| event vfn 0x38 | type (1: particle) |
| viewmodel +0x520 | weapon handle |
| C_OP_ChooseRandomChildrenInGroup +0x1e8 | m_nChildGroupID (default 1) |
| +0x1f0 | m_flNumberOfChildren (default 1) |
| child definition +0x260 | m_nGroupID |
| collection +0x8c1 | bit 1: skip |
| 0x180598f60 | random table (index `(c914 + c910++) & 0xfff`) |

## Weapons.vdata

No gun sets m_szMuzzleFlashParticle, its config or the barrel smoke: the flash and the shell come from the animation
clips.

## The clips' CNmParticleEvents

Fields: m_flStartTime / m_flDuration (Percentage_t { m_flValue }: fraction of the clip), m_relevance, m_type (Create /
Create_CFG), m_target (Self / Weapon), m_hParticleSystem, m_tags, m_bStopImmediately, m_bDetachFromOwner,
m_bPlayEndCap, m_attachmentPoint0 / Type0, m_attachmentPoint1 / Type1, m_config, m_effectForConfig. 136 clips under
animation/anims/{viewmodel,world} have them.

- viewmodel/rifle/rifle_ak/shoot1_ak: at 0, Create_CFG Self `weapon_shell_casing_rifle` config `shell_eject`; at 0,
  Create_CFG Self `uweapon_muzflsh_ak47_fps` config `game`, tags `muzzleflash`.
- world/rifle/rifle_ak/shoot_ak: the same with target Weapon, `uweapon_muzflsh_ak47`.
- Shotgun / sniper shells start later (pump / bolt): nova 10 frames, xm1014 3, awp 21, ssg08 24, scar20 2, g3sg1 1.
- Dual Berettas alternate configs (`primary(_fps)` / `alternate(_fps)`, `shell_eject` / `shell_eject2`); USP-S, M4A1-S
  clips carry a `silenced` and an `unsilenced` flash.
- A *_fps flash sets m_nViewModelEffect INHERITABLE_BOOL_TRUE (drawn in the viewmodel's pass) and names the world system
  as its child. Shells are world systems (C_OP_RenderModels of weapons/models/shared/shells/*, C_OP_WorldTraceConstraint).
- A config is the system's m_controlPointConfigurations entry of that m_name: its m_drivers (ParticleControlPointDriver_t,
  defaults m_iControlPoint 0, m_iAttachType PATTACH_ABSORIGIN_FOLLOW): CP0 PATTACH_POINT_FOLLOW on `muzzle_flash` /
  `shell_eject`, the others PATTACH_WORLDORIGIN with m_vecOffset as constants (AK `game`: CP5 = (0.35, 1, 1) first
  person, (1, 1, 1) third).

## Which events play

- 0x18080a520: weapon vdata +0x728 == 1 and event +0x2e clear: tags searched (V_stristr) for "silenced"; found, it plays
  iff vfn 0xd20 equals "unsilenced" not found. Every other event plays.
- 0x1808ebfd0: event type 1; returns 0 (not played) when the pawn is 0x180c7bdb0's (your own body plays none); else the
  active weapon to 0x18080a520.
- 0x1810d7270: viewmodel +0x520 resolved through the entity list, vfns 0x4f0 / 0xab8 checked, 0x1808cc9c0's weapon to
  0x18080a520.

## Random children (0x180289490)

1. Return when collection +0x8c1 bit 1 or its context byte is set (set at the end: runs once).
2. Every child whose m_nGroupID matches: switched off (flag 0x40, time -FLT_MAX) and listed.
3. While `(float)i < N`: the child at `trunc((float)count * T[(c914 + c910++) & 0xfff])` restarted (0x18003ff50) and
   removed from the list.
4. The rest stopped (0x18004c500).

AK world flash: 2 of group 2 (empty / compensator / spark), 1 of group 1 (primaryflash, primaryflash_alt twice,
gen_empty_gp1); group 0 (smoke, fakelight) always.

## First-person CPs

*_fps configs: CP3 = (1, 0, 0) first person (0 in `thirdperson`): the fire / beam sprites' C_INIT_InitFloat remap CP3.x
0..1 -> 1..0.5 on radius and alpha (half size, half alpha in first person); CP5 (AK's 0.35, 1, 1); CP6 (the fakelight's
input). The flashes' fakelight children use C_OP_RenderStandardLight.

## Unread

- The dispatch past the filters: where Create_CFG resolves its config, a config the system lacks (the AWP / SSG ground
  smoke names none), m_bDetachFromOwner, m_bStopImmediately, m_bPlayEndCap (no gun event sets them), m_effectForConfig
  (empty in every clip).
- The attachment a world effect on the viewmodel (the shell) starts at: taken as 0x180c770c0's; the viewmodel layer's
  own pass (order against the viewmodel's translucents, its bloom-only renderers, the depth of field after it).
- PATTACH_ABSORIGIN drivers: taken at the target's muzzle_flash (no gun config uses one).
- The handlers' other checks (0x1808ebfd0's +0x25e8 path, 0x1810d7270's vfns 0x4f0 / 0xab8), the +0x2e flag.
- Whether the anim graph runs per tick or per frame for shots.
