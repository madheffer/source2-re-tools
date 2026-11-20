# A gun's muzzle flash and shell (traced 2026-11-17)

client_20261015.dll (Ghidra `/client_20261015.dll`), schema names from client_20261105.dll (tools/re/game/schema.py); the
game's content from pak01 (`lasers-bake --decompile`). Port: bake/MuzzleBake.cs (`lasers-bake --impacts`),
web/src/world/anim-graph/clip-particles.js, web/src/cs2web/client/fx/muzzle-fx.js.

## 1. Not in weapons.vdata

CBasePlayerWeaponVData has the fields (client schema entries 0x182231660..): m_sMuzzleAttachment +0x2d0,
m_szMuzzleFlashParticle +0x2f0, m_szMuzzleFlashParticleConfig +0x3d0 ("Effect Config for Muzzle Flash - if set, will
use this config specified in the particle effect..."), m_szBarrelSmokeParticle +0x3d8, m_nMuzzleSmokeShotThreshold
+0x4b8, m_flMuzzleSmokeTimeout +0x4bc, m_flMuzzleSmokeDecrementRate +0x4c0, m_bGenerateMuzzleLight +0x4c4,
m_iRumbleEffect +0x4e4 (a controller rumble id: 1 / 2 / 4 / 9 / -1 per gun; nothing to port in a browser). **No gun in
scripts/weapons.vdata sets m_szMuzzleFlashParticle, its config or the barrel smoke**: the flash and the shell come
from the animation clips.

## 2. The clips' CNmParticleEvents

Every shoot clip carries them (compiled: CNmParticleEvent, fields m_flStartTime / m_flDuration (Percentage_t
{ m_flValue }: a fraction of the clip), m_relevance, m_type (Create / Create_CFG), m_target (Self / Weapon),
m_hParticleSystem, m_tags, m_bStopImmediately, m_bDetachFromOwner, m_bPlayEndCap, m_attachmentPoint0 / Type0,
m_attachmentPoint1 / Type1, m_config, m_effectForConfig). 136 clips under animation/anims/{viewmodel,world} have them
(muzzle.json). Examples:

- viewmodel/rifle/rifle_ak/shoot1_ak: at 0, Create_CFG Self `weapon_shell_casing_rifle` config `shell_eject`;
  at 0, Create_CFG Self `uweapon_muzflsh_ak47_fps` config `game`, tags `muzzleflash`.
- world/rifle/rifle_ak/shoot_ak: the same with target Weapon, `uweapon_muzflsh_ak47` (the world flash).
- the shotguns' and snipers' shells start later (the pump / bolt: nova 10 frames, xm1014 3, awp 21, ssg08 24,
  scar20 2, g3sg1 1); the Dual Berettas alternate configs (`primary(_fps)` / `alternate(_fps)`, `shell_eject` /
  `shell_eject2`); the default pistol / rifle clips (USP-S, M4A1-S) carry a `silenced` and an `unsilenced` flash.
- a *_fps flash system sets **m_nViewModelEffect INHERITABLE_BOOL_TRUE** (drawn in the viewmodel's pass), and names
  the world system as its child; the shell systems are world systems (C_OP_RenderModels of
  weapons/models/shared/shells/*, C_OP_WorldTraceConstraint: they bounce on the world).

A config is the system's own m_controlPointConfigurations entry of that m_name: its m_drivers
(ParticleControlPointDriver_t, defaults m_iControlPoint 0, m_iAttachType PATTACH_ABSORIGIN_FOLLOW): CP0
PATTACH_POINT_FOLLOW on `muzzle_flash` / `shell_eject`, the others PATTACH_WORLDORIGIN with m_vecOffset as constants
(the AK's `game`: CP5 = (0.35, 1, 1) first person, (1, 1, 1) third).

## 3. Which events play

- **0x18080a520** (the tag filter; called by both handlers below): when the weapon's vdata +0x728 is 1 (the silencer
  type: detachable) and the event's +0x2e flag is clear, the event's tags string (+0x30 -> +0x30) is searched
  (V_stristr) for "silenced": found, the event plays iff the weapon's vfn 0xd20 (its silencer state) equals
  "unsilenced" not found. Every other event plays.
- **0x1808ebfd0** (the pawn's anim event handler): an event whose type (vfn 0x38) is 1, the particle one; returns 0
  (not played) when the pawn is FUN_180c7bdb0's (the local player's: your own body plays none); else the active
  weapon (pawn +0x12f0 through 0x1808538e0 when the pawn's own +0x25e8 is null) to 0x18080a520.
- **0x1810d7270** (the viewmodel's): the viewmodel's weapon handle (+0x520) resolved through the entity list, its
  vfns 0x4f0 / 0xab8 checked, 0x1808cc9c0's weapon to 0x18080a520.

## 4. Random children (particles.dll 2026-11-12, md5 b10c5654…)

The world flashes pick their parts with **C_OP_ChooseRandomChildrenInGroup** (vtable 0x18051f3a8, pre-emission
Operate slot 0x110 = **0x180289490**; m_nChildGroupID at op +0x1e8, class default 1; m_flNumberOfChildren at +0x1f0,
default 1): returns at once when the collection's +0x8c1 bit 1 is set or its context byte is (set at the end: it runs
once); every child whose definition's m_nGroupID (+0x260) matches is switched off (flag 0x40, time -FLT_MAX) and
listed; while (float)i < N, the child at trunc((float)count x T[(c914 + c910++) & 0xfff]) (the random table
0x180598f60) is restarted (time 0, 0x18003ff50) and removed from the list; the rest are stopped with their particles
removed (0x18004c500 (k, 0, 1, 1, 0)). The AK's world flash: 2 of group 2 (empty / compensator / spark), 1 of group 1
(primaryflash, primaryflash_alt twice, gen_empty_gp1); group 0 (smoke, fakelight) always.

## 5. The first-person CPs

The *_fps configs give constants the shared children read: CP3 = (1, 0, 0) first person (0 in `thirdperson`): the
fire / beam sprites' C_INIT_InitFloat remap CP3.x 0..1 -> 1..0.5 on their radius and alpha (half size, half alpha in
first person); CP5 (the AK's 0.35, 1, 1), CP6 (the fakelight's input).

## What the port does

The bake keeps every clip's particle events by clip path (muzzle.json `clips`), every viewmodel chassis's gun model
attachments with their rotations (`attachments`), the systems (fx/systems) and the shells' models (models/*.glb).
Both graphs report the events their clips cross in an update ([from, to), `to` at the clip's end; the body graph's
rule for a sound's start): the body's clip node (nodes-pose.js) on the main thread or a pool worker (ids back), the
viewmodel's (weapons/fp/ag2/eval.js `played` ranges, read by weapons/viewmodel.js). muzzle-fx.js filters by
0x18080a520, skips your own body (0x1808ebfd0), builds the CPs from the config's drivers each frame (follow), and
draws a viewmodel-pass system at your eye with the viewmodel camera's projection in Source units, into the HDR frame
after the world, depth-tested against the viewmodel's own depth; the rest under the world's effects. The flashes'
lights (their fakelight children's C_OP_RenderStandardLight) light the world as the map's particle lights do.

The viewmodel's graph (weapons/fp/ag2/eval.js) needed two fixes for one event per shot: a transition out of a
machine's target taken during its fade in the same update (Esoterica's; waiting a frame lost the shoot twins'
one-update action_reset pulse, so a full-auto shot inside the fade never restarted its clip), and a state left by an
instant transition in the same update drops its clip ranges (the first shot entered both twins at 0: two flashes).
Clips under a transition's source are Esoterica's inactive branch: their events don't play (the body graph's
e.active). A third (2026-11-17): a state left by an instant transition clears the active flag of every node it
activated that update, so re-entered the next update it starts over (Esoterica shuts it down). Without it, with a shot
every update (a frame longer than the gun's cycle: a P90 under ~15 fps) the twins flipped back into a clip that went
on from where it was, and a burst played one flash.

A graph steps once a frame (a body's once a step, a worker's held while busy), so shots between two steps restart the
clip once. Each such step's events play again per extra shot, aged: the viewmodel's ages are each shot's time inside
the frame (weapons/viewmodel.js `_shotAges`, from the fire gate's grid), a body's the gun's cycle per shot back
(world/body.js `_extraShots`; their own times aren't sent). A replay's flash takes its age as one longer first step, a
shell's as time already flown. Ours: CS2 runs its prediction per tick and presumably the graph per frame too (not read).

Ours, not CS2's, for frame time (2026-11-17, docs/CLIENT_PERF.md "Muzzle flashes and shells"):
- the shells aren't the particle system: client/fx/shells.js reads each casing vpcf's own numbers (emission delay,
  lifetime, C_INIT_CreateWithinSphereTransform's local speeds along CP0's forward / left / up, C_OP_BasicMovement's
  gravity and drag factor (1 - drag)^(30 dt), C_OP_RotateVector's rates, the stop speed, radius x m_flRadiusScale,
  m_flMaxDrawDistance, the model) and flies them itself: one InstancedMesh a casing model, one world ray a frame while
  airborne. Simplified: the bounce (a random 0.15..0.5 of the normal speed, 0.1..0.3 off the tangent, halved each hit),
  an end-over-end tumble that lies flat when still, the fade as a shrink over the last 0.3 s, none spawned past the
  draw distance, at most 192;
- a flash is stopped once every emitter's state is done (fx/particles/system.js emittersDone; the 4 s cap stays for
  one that never is) and pooled with its light renderer (reset on reuse); at most 48 flashes live;
- the viewmodel pass's camera is rebuilt from the world camera's position and rotation each frame.

## Left (unread)

- the dispatch past the filters: where Create_CFG resolves its config, what it does with a config the system lacks
  (the AWP / SSG's ground smoke names none: the system's first non-preview configuration here), m_bDetachFromOwner,
  m_bStopImmediately, m_bPlayEndCap (no gun event sets them), m_effectForConfig (empty in every clip);
- the attachment a world effect on the viewmodel (the shell) starts at: taken as FormatViewModelAttachment's
  (0x180c770c0, the tracers'); the viewmodel layer's own pass (its order against the viewmodel's translucents, its
  bloom-only renderers: not drawn here, the depth of field after it);
- PATTACH_ABSORIGIN drivers: taken at the target's muzzle_flash (no gun config uses one);
- the event handlers' other checks (0x1808ebfd0's +0x25e8 path, 0x1810d7270's vfns 0x4f0 / 0xab8), the +0x2e flag.
