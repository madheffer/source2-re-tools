# Music volume: the csgo_music stack, snd_musicvolume, snd_music_mode, `volume`

client_20261015, soundsystem (same date); pak01 `soundstacks/soundstacks_csgo_music.vsndstck_c` (decompiled with
Source2Viewer-CLI 19.2 `-d`; `soundstacks_csgo_mega.vsndstck_c` fails in VRF's ResourceEditInfo2 reader: its DATA
block read with kv3dump).

## Functions

| Address | Module | What |
|---|---|---|
| 1800f16b0 | client | registers snd_music_mode |
| 180d0c420 | client | every frame: writes snd_music_mode (then the snd_vol_per_game_mode layers: unread) |
| 180769e20 | client | game_type 0, game_mode 6 |
| 180769d90 | client | (1, 0): arms race |
| 180769d50 | client | (1, 2): deathmatch |
| 180769cf0 | client | (0, 0): casual |
| 18000d4a0 | soundsystem | registers `volume` |
| 180030a10 | soundsystem | the output mix: reads `volume` |
| FUN_180016d10 | soundsystem | an output's mix (volume taken as a gain: unread) |
| 18000d620 | soundsystem | registers snd_musicvolume |
| 1800039f0 | soundsystem | registers snd_gain |

## Constants

| Cvar | Data | Default / flags |
|---|---|---|
| snd_music_mode | DAT_182579280 | float 1.0, 0x80000, "Selects which per-game-mode set of music volume convars is live" |
| volume | DAT_180656098 (value DAT_1806560a0 + 0x58) | float [0, 1], 1, "Sound volume" |
| snd_musicvolume | DAT_1806560b8 | float [0, 1], 1, 0x40000080, "Music volume" |
| snd_gain | DAT_180649db8 | float 1, 0x40000080, no help |

Client globals: DAT_182560ed0 (in a game: vtable +0x138 / +0x1f0), DAT_1825651d0 (gamerules), DAT_1824c47b8 (game_type
vfn +0x98, game_mode vfn +0xa0). Window flag 0x10: `volume` x 0.

## snd_music_mode (180d0c420)

1.0, unless in a game with gamerules: tested in order 180769e20 -> 5, 180769d90 -> 3, 180769d50 -> 4, 180769cf0 -> 2.
Then the snd_vol_per_game_mode mix layers (ArmsRaceVol, DeathmatchVol, CompetitiveVol, CasualVol, SpectatorVol,
WarmupVol).

## The csgo_music stack

`public` defaults: `mixgroup` "Music", `volume` 1.0, `volume_convar` "snd_musicvolume", `use_mode_music_volume` true,
`skip_if_muted` false, `volume_fade_*` 0 / 1 (no fade), `stop_music` false.

| Operator | What |
|---|---|
| `system_globals` get_system_globals | `output_snd_musicvolume_convar`, `output_snd_gain_convar` |
| `mixer` soundmixer_get_mixgroup @public.mixgroup | `output_volume` (Default_Mix level with layers) |
| `music_mode` convar_get snd_music_mode | |
| `music_mode_index` | clamp(snd_music_mode - 1, 0, 4) x public.use_mode_music_volume |
| `volume_convar_casual` ... `_rush` math_string add | volume_convar + "_casual" / "_armsrace" / "_deathmatch" / "_rush" |
| `volume_competitive`, `volume_casual` ... convar_get | each of those convars |
| `volume_by_mode` ctrl_switch12_float | input0..4 = competitive, casual, armsrace, deathmatch, rush, by the index |
| `use_omitted_fallback` | (volume_convar == "snd_musicvolume") x (index > 0) |
| `snd_volume_convar` ctrl_switch_float | fallback ? 0.16 : volume_by_mode |
| `skip_stack_execution` sos_goto end | public.skip_if_muted and snd_volume_convar == 0 |
| `music_total` | output_snd_musicvolume_convar x snd_volume_convar |
| `convar_total` | music_total x output_snd_gain_convar |
| `volume_apply_fade_in / _initial / _out` | x the fades |
| `speaker_volume` | mixer.output_volume x that |
| `volume_accumulate` | x public.volume -> the voice's speakers |
| `should_keep_playing` | max(volume, unstopped) > 0: a voice at volume 0 keeps playing until stopped |

With the default convar: index 0 (competitive, Wingman, out of a game) plays at snd_musicvolume squared; any other mode
at snd_musicvolume x 0.16. At snd_musicvolume 0 the song is silent and keeps its place.

csgo_mega has no musicvolume / gain term: `mult_mixer_volume` (math_accumulate12_float) = mixer level x impact speed
curve x `get_volume_convar` (convar_get @public.volume_convar when public.use_volume_convar, default false / "") x
velocity curve x surf ambient volume x suppression multiplier.

`volume` (180030a10): passed linear to each output's mix as `volume x (0 when window flag 0x10, else 1)`.

## Unread

- What convar_get gives for a convar that doesn't exist (snd_x without its _casual etc. variants). The round end's
  snd_roundend_volume / snd_mvp_volume and their four mode variants exist: 0.16 each ([winpanel.md](winpanel.md)
  "Round end sounds").
- The snd_vol_per_game_mode layers; the window-focus flag behind `volume`'s x 0; FUN_180016d10's use of `volume`.
- A GFL ZE server's game_type / game_mode (taken as casual 0/0).
