// cvarreg.mjs <program> <name> ...: each cvar's registration function (the string's referencing function) decompiled
// by ReVa, printed from the name's line: the register call with its object, default and flags, and the setup before.
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
const [prog, ...names] = process.argv.slice(2);
const here = fileURLToPath(new URL('./reva.mjs', import.meta.url)); // (a URL's pathname keeps %20: a repo path with a space broke)
const call = (tool, args) => execFileSync(process.execPath, [here, tool, JSON.stringify(args)], { encoding: 'utf8', env: { ...process.env, MSYS_NO_PATHCONV: '1' }, maxBuffer: 1 << 26 });
for (const name of names) {
  const s = JSON.parse(call('get-strings', { programPath: prog, searchString: name, includeReferencingFunctions: true, maxCount: 5 }));
  const hit = s.find((x) => x.content === name);
  const fn = hit?.referencingFunctions?.[0]?.address;
  if (!fn) { console.log(`${name}: no registration found`); continue; }
  const d = call('get-decompilation', { programPath: prog, functionNameOrAddress: fn, limit: 80 });
  const lines = d.split('\n').filter((l) => /FUN_|local_(84|83|82|81|28)\b|= 0x|uStack/.test(l) && !/undefined/.test(l.trim().split(' ')[0]));
  console.log(`== ${name} (${fn})`);
  for (const l of lines) if (/FUN_18|local_84|local_83|local_82|local_81 =|local_28/.test(l)) console.log('  ' + l.trim());
}
