# Music volume: the csgo_music stack, snd_musicvolume, snd_music_mode, `volume`

Read 2026-11-16. Ported in web/src/audio/music-stack.js (the stack's convar part) and audio.js (the buses).

## The stack (pak01 `soundstacks/soundstacks_csgo_music.vsndstck_c`)

Decompiled with Source2Viewer-CLI 19.2 (`-d`). (`soundstacks_csgo_mega.vsndstck_c` fails in VRF's ResourceEditInfo2
reader in both CLIs; tools/kv3dump with vpkstuff's VRF build reads its DATA block: `LASERS_VRF_DIR=<vpkstuff
dotnet/VpkStuff.Backend/bin/Release/net10.0> dotnet run -c Release -- <raw dir> <out dir>` in tools/kv3dump.)

`public` defaults: `mixgroup` "Music", `volume` 1.0, `volume_convar` "snd_musicvolume", `use_mode_music_volume` true,
`skip_if_muted` false, `volume_fade_*` 0 / 1 (no fade), `stop_music` false.

The volume chain, in operator order:

| operator | what |
|---|---|
| `system_globals` get_system_globals | `output_snd_musicvolume_convar`, `output_snd_gain_convar` |
| `mixer` soundmixer_get_mixgroup @public.mixgroup | `output_volume` (Default_Mix level with layers: audio/mix.js) |
| `music_mode` convar_get snd_music_mode | |
| `music_mode_index` | clamp(snd_music_mode - 1, 0, 4) x public.use_mode_music_volume |
| `volume_convar_casual` ... `_rush` math_string add | volume_convar + "_casual" / "_armsrace" / "_deathmatch" / "_rush" |
| `volume_competitive`, `volume_casual` ... convar_get | each of those convars |
| `volume_by_mode` ctrl_switch12_float | input0..4 = competitive, casual, armsrace, deathmatch, rush, by the index |
| `use_omitted_fallback` | (volume_convar == "snd_musicvolume") x (index > 0) |
| `snd_volume_convar` ctrl_switch_float | fallback ? **0.16** : volume_by_mode |
| `skip_stack_execution` sos_goto end | when public.skip_if_muted and snd_volume_convar == 0 |
| `music_total` | output_snd_musicvolume_convar x snd_volume_convar |
| `convar_total` | music_total x output_snd_gain_convar |
| `volume_apply_fade_in / _initial / _out` | x the fades |
| `speaker_volume` | mixer.output_volume x that |
| `volume_accumulate` | x public.volume -> the voice's speakers |
| `should_keep_playing` | max(volume, unstopped) > 0: a voice at volume 0 keeps playing until stopped |

So with the default convar: index 0 (competitive, Wingman, out of a game) plays at snd_musicvolume squared; any other
mode at snd_musicvolume x 0.16. At snd_musicvolume 0 the song is silent and keeps its place.

The csgo_mega stack has no musicvolume / gain term: its `mult_mixer_volume` (math_accumulate12_float) is the mixer level
x the impact speed curve x `get_volume_convar` (convar_get @public.volume_convar when public.use_volume_convar, default
false / "") x the velocity curve x the surf ambient volume x the suppression multiplier.

## client.dll (client_20261015.dll)

- `snd_music_mode` registered at **1800f16b0**: float, default 1.0, flags 0x80000, "Selects which per-game-mode set of
  music volume convars is live" (DAT_182579280).
- Written every frame by **180d0c420**: 1.0, unless the client is in a game (vtable +0x138 / +0x1f0 on DAT_182560ed0)
  with gamerules (DAT_1825651d0): **180769e20** (game_type 0, game_mode 6) -> 5, **180769d90** (1, 0: arms race) -> 3,
  **180769d50** (1, 2: deathmatch) -> 4, **180769cf0** (0, 0: casual) -> 2, tested in that order. game_type is
  DAT_1824c47b8 vfn +0x98, game_mode vfn +0xa0. The same function goes on to the snd_vol_per_game_mode mix layers
  (ArmsRaceVol, DeathmatchVol, CompetitiveVol, CasualVol, SpectatorVol, WarmupVol): unread.

## soundsystem.dll

- `volume` registered at **18000d4a0** (DAT_180656098; value via DAT_1806560a0 + 0x58): float [0, 1], default 1,
  "Sound volume". Read in **180030a10** (the output mix): passed linear to each output's mix (FUN_180016d10) as
  volume x (0 when the window flag 0x10 is set, else 1). FUN_180016d10's use of it not read (taken as a gain).
- `snd_musicvolume` at **18000d620** (DAT_1806560b8): float [0, 1], default 1, flags 0x40000080, "Music volume".
- `snd_gain` at **1800039f0** (DAT_180649db8): float, default 1, flags 0x40000080, no help text.

## Still unread

- What convar_get gives for a convar that doesn't exist (an event naming snd_x without its _casual etc. variants).
  (The round end's snd_roundend_volume / snd_mvp_volume and their four mode variants do exist: 0.16 each, console/
  music-cvars.js, winpanel.md "Round end sounds".)
- The snd_vol_per_game_mode layers, and the window-focus flag behind `volume`'s x 0.
- GFL's own game_type / game_mode (a ZE server is taken as casual 0/0: src/cs2web/gamemodes.js cs2GameMode).
