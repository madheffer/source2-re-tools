# CS:GO VScript: the script-side helpers the map ports rely on

Binary: `csgo legacy/csgo/bin/server.dll` (md5 8048019154549052cb6dc057b76f6a85, Ghidra `/csgo_server_legacy.dll`).
The server's Squirrel prelude (the SDK's vscript_server.nut) is embedded in the DLL as plain text: no disassembly is
needed for what it defines, the source is the truth. Find a function with a byte search for `function <Name>(`.

## 1. EntFire and EntFireByHandle (2026-11-18)

File offset 0xa36915, verbatim:

```squirrel
function EntFire( target, action, value = null, delay = 0.0, activator = null )
{
	if ( !value )
	{
		value = "";
	}

	local caller = null;
	if ( "self" in this )
	{
		caller = self;
		if ( !activator )
		{
			activator = self;
		}
	}

	DoEntFire( target.tostring(), action.tostring(), value.tostring(), delay, activator, caller );
}
```

What it means for a port:

- **The caller is the script's own entity** (`self`) whenever the script runs in an entity's scope, which every
  entity script and every `RunScriptCode` does. The receiving input sees it as `caller`, and so does a function run
  by `RunScriptCode` on the target.
- **A missing or null activator becomes `self`** too.
- `!value` is Squirrel's falsiness: null, 0, 0.0 and false all become `""`.
- `EntFireByHandle(target, action, value, delay, activator, caller)` is the native one (the block just before it in
  the prelude only fills the defaults): activator and caller go through as given, null stays null.

Ported: `web/src/cs2web/csgo/vscript/ent-fire.js` (`entFire(engine, self, target, action, value, delay, activator)`).
A port's own `fire(target, ...)` helper uses it for a name (the script's `EntFire("name", ...)`) and plain
`engine.fire` for a handle (`EntFireByHandle`).

Why it matters (BUGFIXES 2026-11-18): ze_crazykart's kartcontroller.nut registers a driver with
`EntFire("manager","RunScriptCode"," RegisterKart(true); ",0.00,driver)` (K:507) and manager.nut's `RegisterKart`
keeps `caller` as the player's kart (M:2451-2461: `c.kart = caller`). With a null caller no player ever had a kart.

## Unread

- `DoEntFire` / `DoEntFireByInstanceHandle` (native): how a delay of 0 is queued against the frame's other events
  (the frame order question in docs/CRAZYKART.md "Frame order").
- The rest of the prelude (`__ReplaceClosures`, `UniqueString`, the `Entities` iterator helpers): not needed yet.
