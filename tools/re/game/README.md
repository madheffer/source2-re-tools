# tools/re/game: helpers for CS2's game DLLs

Small standalone scripts that read a DLL file directly (pefile, capstone, numpy; Unicorn for the oracles), written
while tracing server.dll and client.dll for cs2web's game ports (the notes they fed are in
[docs/game/](../../../docs/game/README.md)). Every one takes the DLL's path as its first argument, so it works on any
build: the installed one, or an archived copy in `tools/re/binaries/`. None needs Ghidra, except the two ReVa clients.

```
pip install pefile capstone numpy unicorn
python tools/re/game/rtti.py tools/re/binaries/server_20261105.dll CCSPlayerPawn
```

They sit in their own folder because four names overlap the compiler-side tools in `tools/re/` (`callers.py`,
`disasm.py`, `riprefs.py`, `xref.py`) with different arguments: these take `<dll> <args>` and need no `paths.py`
alias. Each script's header comment is its full usage.

## Classes, vtables, RTTI (MSVC x64)

| Script | What |
|---|---|
| `rtti.py <dll> <Class>...` | a class's vtable(s), through its type descriptor and complete-object locators |
| `bases.py <dll> <Class>...` | a class's base classes, nearest first (the hierarchy descriptor) |
| `vtall.py <dll> <Class> [slots]` | every vtable of a class, at every sub-object offset, with its first slots |
| `vtdump.py <dll> <0xvtable> [n]` | a vtable's slots with each function's size (finds small virtuals) |
| `vslot.py <dll> <vt>[,<vt>] <slot>[,<slot>]` | which function each class runs at a slot |
| `vslotall.py <dll> <0xslot> <Class>...` | each class's function at one slot (who overrides a vfn) |
| `vdiff.py <dll> <base vt> <derived vt>` | the slots a derived class overrides |
| `vtfind.py <dll> <0xvtable> <0xfunc>...` | which slots of a vtable point at the functions |
| `vtowner.py <dll> <0xfunc>...` | every class vtable and slot holding a function |
| `vtstart.py <dll> <0xslotVA>` | from a slot back to its vtable's start and class |
| `ptrscan.py <dll> <0xVA>...` | every aligned qword equal to a VA, with the vtable's class when there is one |

## Code: functions, calls, references

| Script | What |
|---|---|
| `fnat.py <dll> <0xVA> [--consts] [--around N]` | the function holding an address (exact .pdata bounds, chained parts), disassembled |
| `disasm.py <dll> <va> [bytes] [--all]` | the instructions from a VA to the first ret / int3 (32-bit PEs too) |
| `disasm_consts.py <dll> <va> [bytes] [--fp]` | the same, with each rip-relative operand's f32 value |
| `symss.py <listing> <out reg> <name=reg>...` | straight-line scalar SSE run symbolically: each store as an expression (sum orders) |
| `callers.py <dll> <0xVA>...` | every `call` / `jmp rel32` to a function |
| `argcalls.py <dll> <0xcallee> <reg>` | each direct call with the last write to an argument register before it |
| `vcalls.py <dll> <0xslot>...` | every `call [reg + slot]`: the virtual calls through a slot |
| `svccall.py <dll> <0xfield> <0xslot>` | a load of `[reg + field]` then `call [reg + slot]`: a services object's virtual |
| `impat.py <dll> <iat va>...` | which import an IAT slot holds |
| `riprefs.py <dll> <0xVA>... [--imm N]` | every rip-relative operand pointing at a VA, by bytes (seconds over server.dll) |
| `xref.py <dll> <string or 0xVA>...` | a string's VA and every rip-relative lea / mov to it |
| `f32refs.py <dll> <value>` | an f32's copies in the image and every read of one |
| `fieldwrites.py <dll> <0xoffset> [--reads]` | every store (or use) of `[reg + offset]`: who writes a field |
| `dispuses.py <dll> <0xstart> <0xend> <0xdisp>...` | the instructions in a range using a displacement, lea included |
| `sibscan.py <dll> <0xdisp> [scale]` | every `[base + index*scale + disp32]` operand: who indexes an array in a struct |
| `imulscan.py <dll> <0ximm>...` | every multiply by an immediate (a record array's stride) |
| `recstores.py <dll> <0xstart> <0xend>` | functions ranked by SSE stores to `[reg + small disp]` (a record filled field by field) |

## Strings, enums, tokens, packs

| Script | What |
|---|---|
| `strings.py <dll> <regex>` | every NUL-terminated ASCII string matching, with its VA |
| `strva.py <dll> <string>...` | the VA of an exact string (then `riprefs.py` for its users) |
| `fnstrings.py <dll> <0xstart> <0xend>` | the strings a function references (names a vfn) |
| `enumtab.py <dll> <string>` | the pointer table around a string (an enum's name / value table) |
| `strtoken.py <want hex>... [-- name...]` | CUtlStringToken (MurmurHash2, seed 0x31415926, lower-cased) for candidates |
| `vpkgrep.py <pak_dir.vpk> <path re> <content re>` | search a VPK's files by path and content |

## Schema, ConVars, entity inputs, protobuf

| Script | What |
|---|---|
| `schema.py <dll> <m_field>...` / `--near <entry>` | a schema field's offset from the binding tables, and its class's neighbours |
| `cvardump.py <dll> <name>...` | a ConVar's registration: object, flags, help, the setup's default stores |
| `cvardefs.py <dll> <names file> <out.json>` | many ConVars at once, decoded to type / default / min / max / flags / help |
| `cvarreg.mjs <program> <name>...` | a ConVar's registration decompiled through ReVa |
| `inputs.py <server.dll> [--json out]` | every entity class's I/O inputs (its entity-API bindings) |
| `protodesc.py <dll> <file.proto> [Message...]` | an embedded protobuf FileDescriptorProto, decoded |
| `protomsg.py <dll> <Message>...` | one message's DescriptorProto, for a .proto protodesc.py can't parse whole |
| `pbsetters.py <dll> <0xhasbits> <0xbit> <0xfield>` | inlined protobuf setters (has-bit `or` beside the field store) |
| `nearstores.py <dll> <0xfield> <0xbit> [range]` | the same by a linear sweep, for setters with the bits in a register (slow) |

## Ghidra over HTTP

| Script | What |
|---|---|
| `reva.mjs <tool> <json args> [out]` | one ReVa MCP tool call over HTTP (localhost:8080), for when an MCP client isn't connected; start the server with `tools/re/reva_serve.py` |

## Oracles: CS2's own code run under Unicorn

The pattern for checking a port of a pure function without the game: map the DLL by hand, stub or trap every import
it reaches, plant the globals it reads, run it on random inputs, dump the results' bits as JSON for a test to compare.
Each writes `<out.json>`; the outputs are not kept here (rerun against your build).

| Script | What |
|---|---|
| `tier0_link.py` | the real tier0.dll linked into an oracle's Unicorn (relocated, named imports pointed at its exports, the CRT's FMA flag cleared) |
| `tier0_trig_oracle.py <tier0.dll> <out.json>` | V_sincosf / V_tanf / V_atanf / V_expf / V_powf / V_roundf: the SSE2 path |
| `tier0_native.py <tier0.dll> <in.json> <out.json>` | the same inputs through tier0 loaded natively (ctypes, Windows x64): the FMA3 path on a CPU with it |
| `xhair_oracle.py <client.dll> <out.json>` | the crosshair-code decode and its rescale |
| `xhair_draw_oracle.py <client.dll> <out.json>` | every crosshair style's shape list |
| `xhair_proj_oracle.py <client.dll> <out.json>` | the crosshair's spread projection through the real world-to-screen |
| `xhair_lineup_oracle.py <client.dll> <out.json>` | the grenade line-up crosshair |
| `deathcam_oracle.py <client.dll> <out.json>` | the death camera's ease, AngleDiff, VectorAngles |
| `friendcode_oracle.py <client.dll> <out.json>` | friend codes: account id to code and back |

The oracles name the addresses of the build they were written against in their headers (client 2026-10-15 /
2026-11-12, tier0 2026-10-15); on another build find each function again first (`tools/re/patch_check.py` style:
by its strings or callers).
