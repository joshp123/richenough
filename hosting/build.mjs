// Builds the Sites Worker into dist/: the page, its data and pictures, and the code that draws share pictures.
// Usage: node hosting/build.mjs
import { build } from 'esbuild';
import { createHash } from 'node:crypto';
import { copyFile, mkdir, readFile, readdir, writeFile } from 'node:fs/promises';
import { gzipSync } from 'node:zlib';
import { everyTaxRule } from './every-tax-rule.mjs';

const contentHash = bytes => createHash('sha256').update(bytes).digest('hex').slice(0, 16);
const neverChangesAtThisAddress = 'public, max-age=31536000, immutable';

// Every file the page loads is served from an address that holds its content's hash, so browsers keep it for good.
const webAssets = {};
function addWebAsset(name, extension, bytes, contentType) {
  const path = `/${name}-${contentHash(bytes)}.${extension}`, isGzipped = !['png', 'woff2'].includes(extension);
  webAssets[path] = { contentType, base64: (isGzipped ? gzipSync(bytes, { level: 9 }) : bytes).toString('base64'), isGzipped, cacheControl: neverChangesAtThisAddress };
  return path;
}

const dataPaths = {
  coarseShapes: addWebAsset('map/shapes-coarse', 'bin', await readFile('assets/map/shapes-coarse.bin'), 'application/octet-stream'),
  fineShapes: addWebAsset('map/shapes-fine', 'bin', await readFile('assets/map/shapes-fine.bin'), 'application/octet-stream'),
  places: addWebAsset('map/places', 'json', await readFile('assets/map/places.json'), 'application/json'),
  cities: addWebAsset('map/cities', 'json', await readFile('assets/map/cities.json'), 'application/json'),
  snapshot: addWebAsset('data/snapshot', 'json', await readFile('data/snapshot.json'), 'application/json'),
};
const flagPaths = {};
for (const file of (await readdir('assets/flags')).filter(name => /\.(svg|png)$/.test(name))) {
  const [code, extension] = file.split('.');
  flagPaths[code] = addWebAsset(`flags/${code}`, extension, await readFile(`assets/flags/${file}`), extension === 'svg' ? 'image/svg+xml' : 'image/png');
}
const fontNames = ['Archivo-Regular', 'Archivo-Medium', 'Archivo-SemiBold', 'Archivo-Bold', 'Archivo-ExtraBold'];
const fontPaths = {};
for (const name of fontNames) fontPaths[`/fonts/${name}.woff2`] = addWebAsset(`fonts/${name}`, 'woff2', await readFile(`assets/fonts/${name}.woff2`), 'font/woff2');
const shareFontsBase64 = await Promise.all(fontNames.map(async name => (await readFile(`assets/fonts/${name}.ttf`)).toString('base64')));

const withFontPaths = text => Object.entries(fontPaths).reduce((result, [plain, hashed]) => result.replaceAll(plain, hashed), text);
const define = { DATA_PATHS: JSON.stringify(dataPaths), FLAG_PATHS: JSON.stringify(flagPaths) };
const page = await build({ entryPoints: ['web/page.ts'], bundle: true, format: 'esm', target: 'es2022', minify: true, define, write: false, legalComments: 'none', plugins: [everyTaxRule] });
const pageScript = Buffer.from(page.outputFiles[0].contents);
const pageStyles = Buffer.from(withFontPaths(await readFile('web/style.css', 'utf8')));
const pageHtml = withFontPaths(await readFile('web/index.html', 'utf8'))
  .replace('/page.js', addWebAsset('page', 'js', pageScript, 'text/javascript; charset=utf-8'))
  .replace('/page.css', addWebAsset('page', 'css', pageStyles, 'text/css; charset=utf-8'));

await mkdir('dist/server', { recursive: true });
await mkdir('dist/.openai', { recursive: true });
const workerDefine = { ...define, WEB_ASSETS: JSON.stringify(webAssets), PAGE_HTML: JSON.stringify(pageHtml), SHARE_FONTS_BASE64: JSON.stringify(shareFontsBase64) };
const worker = (await build({ entryPoints: ['hosting/worker.ts'], bundle: true, format: 'esm', platform: 'browser', target: 'es2022', external: ['./resvg.wasm'], define: workerDefine, write: false, plugins: [everyTaxRule] })).outputFiles[0].text;
const resvg = await readFile('node_modules/@resvg/resvg-wasm/index_bg.wasm');
await writeFile('dist/server/index.js', worker);
await writeFile('dist/server/resvg.wasm', resvg);
try { await copyFile('.openai/hosting.json', 'dist/.openai/hosting.json'); } catch { /* No Sites project yet: the site has never been deployed. */ }

const mebibytes = bytes => `${(bytes / 1048576).toFixed(2)} MiB`;
console.log(`Page script ${mebibytes(pageScript.length)} (${mebibytes(gzipSync(pageScript).length)} gzipped)`);
console.log(`Worker ${mebibytes(Buffer.byteLength(worker))} (${mebibytes(gzipSync(worker).length)} gzipped) plus resvg.wasm ${mebibytes(gzipSync(resvg).length)} gzipped`);
