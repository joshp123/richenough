// The Sites Worker: serves the page and its files, says roughly where a visitor is, and draws each link's share pictures.
import { Resvg, initWasm } from '@resvg/resvg-wasm';
// @ts-expect-error The WebAssembly module is uploaded beside the Worker by hosting/build.mjs.
import resvgModule from './resvg.wasm';
import 'every-tax-rule';
import { aboutPage } from '../src/about-page.ts';
import { linkQuery, linkStateOf, type LinkState } from '../src/link.ts';
import { readMapGeometry, type MapGeometry } from '../src/map-geometry.ts';
import { formatCapital } from '../src/money.ts';
import { createPlaces, flagCodesOf, nameOf, type CityRow, type PlaceRows, type Places } from '../src/places.ts';
import { pictureHeight, pictureSvg, pictureWidth, previewHeight, previewSvg, previewWidth, type PictureInput } from '../src/share-pictures.ts';
import type { Snapshot } from '../src/snapshot.ts';
import { siteAddress, siteSubtitle, siteTitle } from '../src/words.ts';
import { worldFigures } from '../src/world-figures.ts';

type WebAsset = { contentType: string; base64: string; isGzipped: boolean; cacheControl: string };
// Filled in by hosting/build.mjs.
declare const WEB_ASSETS: Record<string, WebAsset>;
declare const PAGE_HTML: string;
declare const PAGE_STYLES_PATH: string;
declare const DATA_PATHS: { coarseShapes: string; fineShapes: string; places: string; cities: string; snapshot: string };
declare const FLAG_PATHS: Record<string, string>;
declare const SHARE_FONTS_BASE64: string[];
const webAssets = WEB_ASSETS, flagPaths = FLAG_PATHS;
const titleGap = '<!-- title and share preview tags -->', answerGap = '<!-- answer from server -->';

const bytesFromBase64 = (base64: string) => Uint8Array.from(atob(base64), character => character.charCodeAt(0));
function base64FromBytes(bytes: Uint8Array): string {
  let binary = '';
  for (let index = 0; index < bytes.length; index += 0x8000) binary += String.fromCharCode(...bytes.subarray(index, index + 0x8000));
  return btoa(binary);
}
async function assetBytes(path: string): Promise<Uint8Array> {
  const asset = webAssets[path], stored = bytesFromBase64(asset.base64);
  if (!asset.isGzipped) return stored;
  return new Uint8Array(await new Response(new Blob([stored]).stream().pipeThrough(new DecompressionStream('gzip'))).arrayBuffer());
}
const assetJson = async <T>(path: string) => JSON.parse(new TextDecoder().decode(await assetBytes(path))) as T;

let worldOnceRead: Promise<{ places: Places; geometry: MapGeometry }>;
const world = () => (worldOnceRead ??= (async () => {
  const [rows, cities, snapshot, shapes] = await Promise.all([assetJson<PlaceRows>(DATA_PATHS.places), assetJson<CityRow[]>(DATA_PATHS.cities), assetJson<Snapshot>(DATA_PATHS.snapshot), assetBytes(DATA_PATHS.coarseShapes)]);
  return { places: createPlaces(rows, cities, snapshot), geometry: readMapGeometry(shapes) };
})());

const flagDataUrls = new Map<string, string>();
async function flagDataUrl(code: string): Promise<string | null> {
  const path = flagPaths[code];
  if (!path) return null;
  if (!flagDataUrls.has(code)) flagDataUrls.set(code, `data:${webAssets[path].contentType};base64,${base64FromBytes(await assetBytes(path))}`);
  return flagDataUrls.get(code)!;
}

const shareFonts = SHARE_FONTS_BASE64.map(bytesFromBase64);
let resvgOnceReady: Promise<void>;
async function renderPng(svg: string): Promise<Uint8Array> {
  await (resvgOnceReady ??= initWasm(resvgModule));
  // Both objects hold WebAssembly memory that only free() gives back.
  const drawing = new Resvg(svg, { font: { fontBuffers: shareFonts, defaultFontFamily: 'Archivo', loadSystemFonts: false } });
  try {
    const picture = drawing.render();
    try { return picture.asPng().slice(); } finally { picture.free(); }
  } finally { drawing.free(); }
}

// The link names the currency in brackets ("also"), so a picture looks the same whoever's server asks for it.
async function pictureInput(state: LinkState, url: URL): Promise<PictureInput> {
  const { places, geometry } = await world(), figures = worldFigures(places, geometry.shapeCodes, state.settings);
  // Flags for every city that could be labelled: the named places and each city with a figure.
  const flags = new Map<string, string | null>();
  const codes = [state.visitor, state.compared, figures.least, ...figures.cityCapital.keys()].filter((code): code is string => !!code);
  for (const code of codes) {
    const { country, state: stateFlag } = flagCodesOf(places, code);
    for (const flagCode of [country, stateFlag]) if (flagCode && !flags.has(flagCode)) flags.set(flagCode, await flagDataUrl(flagCode));
  }
  const currency = state.currency ?? 'USD', also = url.searchParams.get('also')?.toUpperCase() ?? null;
  return {
    places, geometry, figures, mode: state.mode, visitor: state.visitor, compared: state.compared, currency, have: state.have,
    secondCurrency: also && also !== currency && (also === 'USD' || places.snapshot.exchangeRates[also]) ? also : null,
    flagDataUrl: code => flags.get(code) ?? null, address: siteAddress,
  };
}

const escapeHtml = (text: string) => text.replace(/[<>&"]/g, character => ({ '<': '&lt;', '>': '&gt;', '&': '&amp;', '"': '&quot;' })[character]!);
const htmlResponse = (html: string, status = 200) => new Response(html, { status, headers: { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'public, max-age=300' } });

// The page for one link: its own title, the tags that make Twitter show this link's picture, and the answer in words for a
// browser without JavaScript.
async function pageFor(url: URL): Promise<Response> {
  const { places, geometry } = await world(), state = linkStateOf(places, url), figures = worldFigures(places, geometry.shapeCodes, state.settings);
  const describe = (code: string | null) => {
    if (!code) return null;
    const figure = figures.figureOf(code);
    return figure.kind === 'figure' ? `${nameOf(places, code)}: ${formatCapital(figure.capitalUsDollars, 'USD')}` : null;
  };
  const sentence = [state.visitor, state.compared, figures.least].map(describe).filter(Boolean).join(' · ') || `${siteSubtitle}, everywhere in the world.`;
  const title = `${siteTitle} ${siteSubtitle}`, query = linkQuery(places, state, { withOpened: false });
  const tags = Object.entries({
    'og:type': 'website', 'og:site_name': siteTitle, 'og:title': title, 'og:description': sentence, 'og:url': `${url.origin}/${query}`,
    'og:image': `${url.origin}/preview.png${query}`, 'og:image:width': String(previewWidth), 'og:image:height': String(previewHeight),
    'twitter:card': 'summary_large_image', 'twitter:creator': '@jjpcodes', 'twitter:title': siteTitle, 'twitter:description': sentence, 'twitter:image': `${url.origin}/preview.png${query}`,
  }).map(([name, content]) => `<meta ${name.startsWith('og:') ? 'property' : 'name'}="${name}" content="${escapeHtml(content)}">`);
  const head = [`<title>${escapeHtml(title)}</title>`, `<meta name="description" content="${escapeHtml(sentence)}">`, ...tags].join('\n');
  const answer = `<noscript><p class="no-script">${escapeHtml(sentence)}. The map needs JavaScript.</p></noscript>`;
  return htmlResponse(PAGE_HTML.replace(titleGap, head).replace(answerGap, answer));
}

// The About page is the same for every visitor, so it is written once.
let aboutOnceWritten: Promise<string>;

function serveAsset(asset: WebAsset): Response {
  const headers: Record<string, string> = { 'Content-Type': asset.contentType, 'Cache-Control': asset.cacheControl };
  if (asset.isGzipped) headers['Content-Encoding'] = 'gzip';
  return new Response(bytesFromBase64(asset.base64), { headers, encodeBody: 'manual' } as ResponseInit);
}

export default {
  async fetch(request: Request): Promise<Response> {
    const url = new URL(request.url);
    if (url.pathname === '/api/whereami') {
      const cf = (request as Request & { cf?: Record<string, unknown> }).cf ?? {};
      const country = (cf.country as string | undefined) ?? request.headers.get('CF-IPCountry');
      const latitude = Number(cf.latitude), longitude = Number(cf.longitude);
      return Response.json({ country: country && country !== 'XX' ? country : null, ...(Number.isFinite(latitude) && Number.isFinite(longitude) && cf.latitude ? { latitude, longitude } : {}) }, { headers: { 'Cache-Control': 'no-store' } });
    }
    const asset = webAssets[url.pathname];
    if (asset) return serveAsset(asset);
    if (url.pathname === '/picture.png' || url.pathname === '/preview.png') {
      const started = Date.now(), { places } = await world(), state = linkStateOf(places, url), input = await pictureInput(state, url);
      const png = await renderPng(url.pathname === '/picture.png' ? pictureSvg(input) : previewSvg(input));
      return new Response(png as BodyInit, { headers: { 'Content-Type': 'image/png', 'Cache-Control': 'public, max-age=3600', 'Server-Timing': `render;dur=${Date.now() - started}`, 'X-Picture-Size': url.pathname === '/picture.png' ? `${pictureWidth}x${pictureHeight}` : `${previewWidth}x${previewHeight}` } });
    }
    if (url.pathname === '/') return pageFor(url);
    if (url.pathname === '/about') return htmlResponse(await (aboutOnceWritten ??= world().then(({ places }) => aboutPage(places, PAGE_STYLES_PATH))));
    return htmlResponse('<!doctype html><html lang="en-GB"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Page not found</title><body style="font: 17px/1.4 system-ui, sans-serif; margin: 15vh auto; max-width: 30em; padding: 0 1.5em"><h1>There is no page at this address.</h1><p><a href="/">See what a couple needs to live well, everywhere</a></p>', 404);
  },
};
