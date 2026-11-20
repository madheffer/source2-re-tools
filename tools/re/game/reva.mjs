// reva.mjs <tool> <json args> [out file]: one ReVa MCP tool call over HTTP (http://localhost:8080/mcp/message):
// initialize, notifications/initialized, tools/call. Prints the result's text (or writes it to the out file); a
// get-decompilation result prints as plain decompiled code. `--list` lists the tools and their arguments. For when the
// session's ReVa MCP tools failed to connect (the server started after the session): start it headless from
// this repo (`<S2C_GHIDRA_ROOT>/reva-venv/Scripts/python -u tools/re/reva_serve.py`, ready line "ReVa ready on
// port 8080"), check no other session runs one first, stop it when done. From Git Bash prefix MSYS_NO_PATHCONV=1
// (a programPath like /server_20261105.dll is otherwise rewritten). E.g.
//   MSYS_NO_PATHCONV=1 node tools/re/reva.mjs get-decompilation '{"programPath":"/server_20261105.dll","functionNameOrAddress":"0x180ed4ea0","limit":600}'
import { writeFileSync } from 'node:fs';
const URL_ = 'http://localhost:8080/mcp/message';
const [tool, argJson = '{}', out] = process.argv.slice(2);
let sid = null, id = 0;
async function rpc(method, params, notify = false) {
  const body = notify ? { jsonrpc: '2.0', method, params } : { jsonrpc: '2.0', id: ++id, method, params };
  const h = { 'content-type': 'application/json', accept: 'application/json, text/event-stream' };
  if (sid) h['mcp-session-id'] = sid;
  const r = await fetch(URL_, { method: 'POST', headers: h, body: JSON.stringify(body) });
  sid = r.headers.get('mcp-session-id') || sid;
  if (notify) return null;
  const t = await r.text();
  // SSE or JSON
  const m = t.match(/^data: (.*)$/m);
  return JSON.parse(m ? m[1] : t);
}
const init = await rpc('initialize', { protocolVersion: '2025-03-26', capabilities: {}, clientInfo: { name: 'cli', version: '1' } });
if (init.error) throw new Error(JSON.stringify(init.error));
await rpc('notifications/initialized', {}, true);
if (tool === '--list') {
  const r = await rpc('tools/list', {});
  console.log(r.result.tools.map((t) => `${t.name}: ${JSON.stringify(t.inputSchema?.properties ? Object.keys(t.inputSchema.properties) : [])}`).join('\n'));
  process.exit(0);
}
const r = await rpc('tools/call', { name: tool, arguments: JSON.parse(argJson) });
let text = r.error ? JSON.stringify(r.error) : (r.result?.content || []).map((c) => c.text ?? JSON.stringify(c)).join('\n');
try { const o = JSON.parse(text); if (o.decompilation) text = o.decompilation.replace(/\r/g, '').replace(/^ *\d+\t/gm, ''); } catch { /* plain */ }
if (out) writeFileSync(out, text); else console.log(text);
