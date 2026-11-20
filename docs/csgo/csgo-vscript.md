# CS:GO VScript: the prelude's EntFire

server.dll (CS:GO legacy, md5 8048019154549052cb6dc057b76f6a85, Ghidra `/csgo_server_legacy.dll`). The Squirrel prelude (the SDK's vscript_server.nut) is embedded as plain text: find a function with a byte search for `function <Name>(`.

## Constants

| Value | What |
|---|---|
| file offset 0xa36915 | `function EntFire(` in server.dll |

## 1. EntFire (verbatim)

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

- The caller is `self` whenever the script runs in an entity's scope (every entity script and every `RunScriptCode`); the input sees it as `caller`, as does a function run by `RunScriptCode` on the target.
- A missing or null activator becomes `self` too.
- `!value` is Squirrel falsiness: null, 0, 0.0 and false all become `""`.
- `EntFireByHandle(target, action, value, delay, activator, caller)` is native (the prelude block before it only fills defaults): activator and caller pass as given, null stays null.
- ze_crazykart depends on it: kartcontroller.nut registers a driver with `EntFire("manager","RunScriptCode"," RegisterKart(true); ",0.00,driver)` (K:507); manager.nut's `RegisterKart` keeps `caller` as the player's kart (M:2451-2461: `c.kart = caller`).

## Unread

- `DoEntFire` / `DoEntFireByInstanceHandle` (native): how a delay of 0 is queued against the frame's other events (the frame order question in cs2web's docs/CRAZYKART.md "Frame order").
- The rest of the prelude (`__ReplaceClosures`, `UniqueString`, the `Entities` iterator helpers).
