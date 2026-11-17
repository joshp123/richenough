// Runs the built Worker on this machine in the runtime Sites uses, on every network interface, so another machine on the
// tailnet can open it: node hosting/preview.mjs [port] [country the visitor seems to be in]
import { Miniflare } from 'miniflare';

const port = Number(process.argv[2] ?? 8791), country = process.argv[3] ?? 'NL';
const worker = new Miniflare({
  host: '0.0.0.0',
  port,
  modulesRoot: 'dist/server',
  modules: [{ type: 'ESModule', path: 'dist/server/index.js' }, { type: 'CompiledWasm', path: 'dist/server/resvg.wasm' }],
  compatibilityDate: '2026-07-01',
  // Here the request has no location; this stands in for the one Sites gives it.
  cf: { country },
});
await worker.ready;
console.log(`Enough on http://0.0.0.0:${port}, visitors seeming to be in ${country}`);
