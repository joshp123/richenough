// The share pictures, as SVG the Worker turns into PNG with resvg: the 7:8 picture for posts (the only one people copy) and the
// 2:1 picture Twitter shows under a bare link. A phone shows either at a fifth or a sixth of its size, so type here is large.
import advanceWidths from '../assets/fonts/archivo-advance-widths.json' with { type: 'json' };
import { fillOf, noFigureColour, stepColours, stepEnds } from './colours.ts';
import type { MapGeometry } from './map-geometry.ts';
import { svgMap } from './map-svg.ts';
import { formatCapital, formatShort, formatSignedCapital, formatWhole } from './money.ts';
import { countryOf, flagCodesOf, nameOf, type Places } from './places.ts';
import { projection, projectPoint } from './projection.ts';
import { verdictFill, verdictInk, verdictOf, type Mode } from './verdict.ts';
import { madeBy, siteSubtitle, siteTitle } from './words.ts';
import type { WorldFigures } from './world-figures.ts';

export type PictureInput = {
  places: Places; geometry: MapGeometry; figures: WorldFigures; mode: Mode;
  visitor: string | null; compared: string | null;
  // The currency amounts are written in, and the visitor's own, shown in brackets where different.
  currency: string; secondCurrency: string | null;
  // What the visitor has, in that currency.
  have: number;
  // A flag file as a data URL, by flag code ("NL", "US-CA"), or null where there is none.
  flagDataUrl(flagCode: string): string | null;
  address: string;
};

const ink = '#10151C', grey = '#4A5360', sea = '#E9EEF3', paper = '#FFFFFF';
type Weight = 400 | 500 | 600 | 700 | 800;
const widths = advanceWidths as { unitsPerEm: number; advanceWidthsByWeight: Record<string, Record<string, number>> };

const escapeXml = (text: string) => text.replace(/[<>&"]/g, character => ({ '<': '&lt;', '>': '&gt;', '&': '&amp;', '"': '&quot;' })[character]!);
const plainSpaces = (text: string) => text.replaceAll(' ', ' ');
export function textWidth(text: string, size: number, weight: Weight, letterSpacingEm = 0): number {
  const table = widths.advanceWidthsByWeight[weight];
  let units = 0;
  for (const character of plainSpaces(text)) units += table[character] ?? table.M;
  return units / widths.unitsPerEm * size + letterSpacingEm * size * Math.max(0, [...text].length - 1);
}
const fittedSize = (text: string, size: number, weight: Weight, widthLimit: number, letterSpacingEm = 0) => Math.min(size, Math.floor(size * widthLimit / textWidth(text, size, weight, letterSpacingEm)));
type Run = { words: string; weight: Weight; colour: string };
// One line of text in runs of different weight and colour, from a left edge or to a right edge.
function runs(parts: Run[], x: number, baseline: number, size: number, anchor: 'start' | 'end' = 'start', letterSpacingEm = 0): string {
  const total = parts.reduce((sum, part) => sum + textWidth(part.words, size, part.weight, letterSpacingEm), 0);
  let left = anchor === 'start' ? x : x - total, svg = '';
  // SVG text drops a run's leading and trailing spaces, so each run is drawn without them, moved along by their width.
  for (const part of parts) {
    const spacing = letterSpacingEm ? ` letter-spacing="${(letterSpacingEm * size).toFixed(2)}"` : '';
    const leading = part.words.length - part.words.trimStart().length, trimmed = part.words.trim();
    const start = left + textWidth(' '.repeat(leading), size, part.weight, letterSpacingEm);
    if (trimmed) svg += `<text x="${start.toFixed(1)}" y="${baseline.toFixed(1)}" font-family="Archivo" font-size="${size}" font-weight="${part.weight}" fill="${part.colour}"${spacing}>${escapeXml(plainSpaces(trimmed))}</text>`;
    left += textWidth(part.words, size, part.weight, letterSpacingEm);
  }
  return svg;
}
const text = (words: string, x: number, baseline: number, size: number, weight: Weight, colour = ink, anchor: 'start' | 'end' = 'start', letterSpacingEm = 0) => runs([{ words, weight, colour }], x, baseline, size, anchor, letterSpacingEm);

let clipCount = 0;
function roundedPicture(url: string, x: number, y: number, width: number, height: number, radius: number): string {
  const id = `clip-${++clipCount}`;
  return `<clipPath id="${id}"><rect x="${x}" y="${y}" width="${width}" height="${height}" rx="${radius}"/></clipPath><image href="${url}" x="${x}" y="${y}" width="${width}" height="${height}" preserveAspectRatio="xMidYMid slice" clip-path="url(#${id})"/>`;
}
function flag(input: PictureInput, code: string, left: number, top: number, height: number, radius: number): string {
  const { country, state } = flagCodesOf(input.places, code), width = height * 1.5, countryUrl = input.flagDataUrl(country);
  if (!countryUrl) return '';
  let svg = roundedPicture(countryUrl, left, top, width, height, radius) + `<rect x="${left}" y="${top}" width="${width}" height="${height}" rx="${radius}" fill="none" stroke="${ink}" stroke-opacity="0.14" stroke-width="${Math.max(1, height / 40)}"/>`;
  const stateUrl = state && input.flagDataUrl(state);
  if (stateUrl) {
    const cornerWidth = width * 0.6, cornerHeight = height * 0.6, outline = height * 0.05;
    svg += `<rect x="${left + width - cornerWidth - outline}" y="${top + height - cornerHeight - outline}" width="${cornerWidth + outline}" height="${cornerHeight + outline}" fill="${paper}"/>`
      + roundedPicture(stateUrl, left + width - cornerWidth, top + height - cornerHeight, cornerWidth, cornerHeight, radius / 2);
  }
  return svg;
}

const perUnit = (input: PictureInput, currency: string) => (currency === 'USD' ? 1 : input.places.snapshot.exchangeRates[currency]?.perUsDollar ?? NaN);
const money = (input: PictureInput, usDollars: number) => formatCapital(usDollars * perUnit(input, input.currency), input.currency);
const haveUsDollars = (input: PictureInput) => input.have / perUnit(input, input.currency);
const capitalOf = (input: PictureInput, code: string) => { const figure = input.figures.figureOf(code); return figure.kind === 'figure' ? figure.capitalUsDollars : null; };
const colourOf = (input: PictureInput, usDollars: number | null) => fillOf(input.mode, usDollars, haveUsDollars(input));
// What a place's label says: what it needs, or what the visitor would have spare or be short.
const placeAmount = (input: PictureInput, need: number) => {
  if (input.mode === 'need') return money(input, need);
  const difference = (haveUsDollars(input) - need) * perUnit(input, input.currency);
  return Math.abs(difference) >= 95_000 * perUnit(input, input.currency) ? formatSignedCapital(difference, input.currency)
    : `${difference < 0 ? '−' : '+'}${formatShort(Math.max(1_000, Math.abs(difference)), input.currency)}`;
};

// A frame on the world map: the world as wide as the frame, the given latitude in the middle of its height.
type Frame = { width: number; height: number; left: number; top: number; scale: number };
function worldFrame(width: number, height: number, top: number, middleLatitude: number): Frame {
  const scale = width, middle = projection.project(0, middleLatitude)[1] * scale;
  return { width, height: top + height, left: 0, top: top + height / 2 - middle, scale };
}
function worldMap(input: PictureInput, frame: Frame, clip: { y: number; height: number }): string {
  const colours = Array.from(input.figures.shapeCapital, capital => colourOf(input, Number.isNaN(capital) ? null : capital));
  const body = svgMap(input.geometry, frame, shape => colours[shape] ?? noFigureColour, { colour: paper, width: 1.2, kinds: ['country'] });
  const id = `clip-${++clipCount}`;
  return `<rect x="0" y="${clip.y}" width="${frame.width}" height="${clip.height}" fill="${sea}"/><clipPath id="${id}"><rect x="0" y="${clip.y}" width="${frame.width}" height="${clip.height}"/></clipPath><g clip-path="url(#${id})">${body}</g>`;
}

// A city's label on a picture's map: a dot in its own colour, then a pill with its flag, name and figure.
type LabelBox = [left: number, top: number, right: number, bottom: number];
function labelParts(input: PictureInput, code: string, frame: Frame, scale: number) {
  const city = input.places.cityByCode.get(code), capital = capitalOf(input, code);
  if (!city || capital === null) return null;
  const [mapX, mapY] = projectPoint(city.longitude, city.latitude), x = mapX * frame.scale + frame.left, y = mapY * frame.scale + frame.top;
  const name = nameOf(input.places, code), amount = placeAmount(input, capital), size = 12 * scale;
  const width = (4 + 17 + 5 + 5 + 7) * scale + textWidth(name, size, 500) + textWidth(amount, size, 700), height = 22 * scale;
  return { code, x, y, name, amount, capital, size, width, height, scale };
}
function labelBox(parts: NonNullable<ReturnType<typeof labelParts>>, side: 'right' | 'left'): LabelBox {
  const left = side === 'right' ? parts.x + 9 * parts.scale : parts.x - 9 * parts.scale - parts.width;
  return [left, parts.y - parts.height / 2, left + parts.width, parts.y + parts.height / 2];
}
// A colour lightened for the dark label, so a verdict's colour still reads on ink.
const towardsWhite = (hex: string, share: number) => `#${[1, 3, 5].map(start => Math.round(parseInt(hex.slice(start, start + 2), 16) * (1 - share) + 255 * share).toString(16).padStart(2, '0')).join('')}`;
function drawLabel(input: PictureInput, parts: NonNullable<ReturnType<typeof labelParts>>, box: LabelBox, dark: boolean): string {
  const { scale, size } = parts, [left, top] = box, flagHeight = 12 * scale, baseline = parts.y + size * 0.36;
  const verdictColour = input.mode === 'have' ? verdictInk[verdictOf(parts.capital, haveUsDollars(input))] : null;
  const amountColour = verdictColour ? (dark ? towardsWhite(verdictColour, 0.55) : verdictColour) : dark ? paper : ink;
  return `<circle cx="${parts.x}" cy="${parts.y}" r="${5.5 * scale}" fill="${ink}"/><circle cx="${parts.x}" cy="${parts.y}" r="${5 * scale}" fill="${paper}"/><circle cx="${parts.x}" cy="${parts.y}" r="${3.5 * scale}" fill="${colourOf(input, parts.capital)}"/>`
    + `<rect x="${left}" y="${top}" width="${parts.width}" height="${parts.height}" rx="${5 * scale}" fill="${dark ? ink : paper}" stroke="${ink}" stroke-opacity="${dark ? 0 : 0.14}" stroke-width="${scale}"/>`
    + flag(input, parts.code, left + 4 * scale, parts.y - flagHeight / 2, flagHeight, 2 * scale)
    + text(parts.name, left + 26 * scale, baseline, size, 500, dark ? paper : ink)
    + text(parts.amount, left + 26 * scale + textWidth(parts.name, size, 500) + 5 * scale, baseline, size, 700, amountColour);
}
const overlaps = (a: LabelBox, b: LabelBox, margin: number) => a[0] - margin < b[2] && a[2] + margin > b[0] && a[1] - margin < b[3] && a[3] + margin > b[1];
// Labels for the named places first, then for each country's biggest city, then the next, until the map is full or has enough.
function mapLabels(input: PictureInput, frame: Frame, mapTop: number, scale: number, clear: LabelBox[], named: string[], most: number): string {
  const byCountry = new Map<string, number>(), ranked: { code: string; rank: number; population: number }[] = [];
  for (const city of input.places.cities) {
    if (!input.figures.cityCapital.has(city.code)) continue;
    const country = countryOf(input.places, city.code), rank = byCountry.get(country) ?? 0;
    byCountry.set(country, rank + 1);
    ranked.push({ code: city.code, rank, population: city.population });
  }
  ranked.sort((a, b) => a.rank - b.rank || b.population - a.population);
  const order = [...named, ...ranked.map(city => city.code).filter(code => !named.includes(code))];
  const placed: { parts: NonNullable<ReturnType<typeof labelParts>>; box: LabelBox }[] = [], taken = [...clear];
  for (const code of order) {
    if (placed.length >= most) break;
    const parts = labelParts(input, code, frame, scale);
    if (!parts) continue;
    const box = (['right', 'left'] as const).map(side => labelBox(parts, side))
      .find(candidate => candidate[0] > 8 && candidate[2] < frame.width - 8 && candidate[1] > mapTop + 8 && candidate[3] < frame.height - 8 && !taken.some(other => overlaps(candidate, other, 6 * scale)));
    if (!box) continue;
    placed.push({ parts, box });
    taken.push(box, [parts.x - 8 * scale, parts.y - 8 * scale, parts.x + 8 * scale, parts.y + 8 * scale]);
  }
  return placed.reverse().map(({ parts, box }) => drawLabel(input, parts, box, parts.code === input.visitor)).join('');
}

// The key: the dollar scale in the first mode, the three verdicts in the second. Returns its drawing and its box.
function keyCard(input: PictureInput, x: number, y: number, scale: number): { svg: string; box: LabelBox } {
  if (input.mode === 'have') {
    const size = 26 * scale, swatch = 26 * scale, gap = 14 * scale, between = 34 * scale;
    const items = (['WAGMI', 'Close', 'NGMI'] as const).map(word => ({ word, width: swatch + gap + textWidth(word, size, word === 'Close' ? 500 : 800) }));
    const width = items.reduce((sum, item) => sum + item.width, 0) + between * 2 + 48 * scale, height = 66 * scale;
    let svg = `<rect x="${x}" y="${y}" width="${width}" height="${height}" rx="${20 * scale}" fill="${paper}" fill-opacity="0.95"/>`, left = x + 24 * scale;
    for (const item of items) {
      svg += `<rect x="${left}" y="${y + (height - swatch) / 2}" width="${swatch}" height="${swatch}" rx="${6 * scale}" fill="${verdictFill[item.word]}"/>`
        + text(item.word, left + swatch + gap, y + height / 2 + size * 0.36, size, item.word === 'Close' ? 500 : 800, item.word === 'Close' ? ink : verdictInk[item.word]);
      left += item.width + between;
    }
    return { svg, box: [x, y, x + width, y + height] };
  }
  const step = 76 * scale, height = 14 * scale, width = step * stepColours.length, id = `clip-${++clipCount}`;
  let svg = `<rect x="${x}" y="${y}" width="${width + 48 * scale}" height="${118 * scale}" rx="${20 * scale}" fill="${paper}" fill-opacity="0.95"/>`;
  svg += text('$1M is enough', x + 24 * scale, y + 40 * scale, 24 * scale, 600, '#1B7F4C');
  svg += `<clipPath id="${id}"><rect x="${x + 24 * scale}" y="${y + 56 * scale}" width="${width}" height="${height}" rx="${4 * scale}"/></clipPath><g clip-path="url(#${id})">`
    + stepColours.map((colour, index) => `<rect x="${x + 24 * scale + index * step}" y="${y + 56 * scale}" width="${step + 1}" height="${height}" fill="${colour}"/>`).join('') + '</g>';
  for (const [index, end] of stepEnds.entries()) {
    if (![1e6, 2e6, 3e6].includes(end)) continue;
    const words = `$${end / 1e6}M`, centre = x + 24 * scale + (index + 1) * step, weight = end === 1e6 ? 700 : 500;
    svg += text(words, centre - textWidth(words, 22 * scale, weight) / 2, y + 100 * scale, 22 * scale, weight, end === 1e6 ? ink : grey);
  }
  return { svg, box: [x, y, x + width + 48 * scale, y + 118 * scale] };
}

const verdictRuns = (input: PictureInput, capital: number): Run[] => {
  const word = verdictOf(capital, haveUsDollars(input));
  return [{ words: ' · ', weight: 400, colour: grey }, { words: word, weight: 700, colour: verdictInk[word] }];
};

export const pictureWidth = 1400, pictureHeight = 1600;
export function pictureSvg(input: PictureInput): string {
  const margin = 64, right = pictureWidth - margin;
  let svg = `<rect width="${pictureWidth}" height="${pictureHeight}" fill="${paper}"/>`;
  svg += text(siteTitle, margin, 132, fittedSize(siteTitle, 104, 800, pictureWidth - 2 * margin, -0.035), 800, ink, 'start', -0.035);
  svg += input.mode === 'have' ? text(`I have ${formatWhole(input.have, input.currency)}. Am I gonna make it?`, margin, 186, 32, 400, grey) : text(siteSubtitle, margin, 186, 32, 400, grey);
  const mapTop = 216, mapHeight = 760, frame = worldFrame(pictureWidth, mapHeight, mapTop, 16);
  svg += worldMap(input, frame, { y: mapTop, height: mapHeight });
  const key = keyCard(input, 40, mapTop + mapHeight - (input.mode === 'have' ? 106 : 150), 1);
  svg += mapLabels(input, frame, mapTop, 2, [[key.box[0], key.box[1] - 8, key.box[2], mapTop + mapHeight]], [input.visitor, input.compared].filter((code): code is string => !!code), 2) + key.svg;

  const third = input.mode === 'have' ? 'Most to spare' : 'Needs least';
  // A place that fills two roles (I live where it costs least) gets one row naming both.
  const list: { code: string; role: string }[] = [];
  for (const [code, role] of [[input.visitor, 'Me'], [input.compared, 'Compared with'], [input.figures.least, third]] as const) {
    if (!code) continue;
    const same = list.find(row => row.code === code);
    if (same) same.role += ` · ${role.toLowerCase()}`; else list.push({ code, role });
  }
  const rowsTop = mapTop + mapHeight + 8, rowsBottom = pictureHeight - 112, rowHeight = (rowsBottom - rowsTop) / 3;
  list.forEach((row, index) => {
    const top = rowsTop + (3 - list.length) * rowHeight / 2 + index * rowHeight, middle = top + rowHeight / 2, capital = capitalOf(input, row.code);
    if (index) svg += `<rect x="${margin}" y="${top}" width="${right - margin}" height="2" fill="${ink}" fill-opacity="0.08"/>`;
    svg += flag(input, row.code, margin, middle - 44, 88, 8);
    const name = nameOf(input.places, row.code), nameSize = fittedSize(name, 58, 700, 520, -0.01);
    svg += runs([{ words: row.role, weight: 400, colour: grey }, ...(capital === null || input.mode === 'need' ? [] : verdictRuns(input, capital))], margin + 160, middle - 22, 30);
    svg += text(name, margin + 160, middle + 40, nameSize, 700, ink, 'start', -0.01);
    if (capital === null) { svg += text('Not known', right, middle + 24, 54, 700, grey, 'end'); return; }
    const second = input.mode === 'have' ? `needs ${money(input, capital)}`
      : input.secondCurrency && Number.isFinite(perUnit(input, input.secondCurrency)) ? `(${formatCapital(capital * perUnit(input, input.secondCurrency), input.secondCurrency)})` : '';
    const amount = placeAmount(input, capital), amountColour = input.mode === 'have' ? verdictInk[verdictOf(capital, haveUsDollars(input))] : ink;
    const secondWidth = second ? textWidth(second, 32, 400) + 26 : 0, amountWidth = textWidth(amount, 84, 800, -0.035);
    if (second) svg += text(second, right, middle + 22, 32, 400, grey, 'end');
    svg += text(amount, right - secondWidth, middle + 30, 84, 800, amountColour, 'end', -0.035);
    svg += `<circle cx="${right - secondWidth - amountWidth - 34}" cy="${middle}" r="15" fill="${input.mode === 'have' ? amountColour : colourOf(input, capital)}"/>`;
  });
  svg += text(input.address, margin, pictureHeight - 52, 42, 700, ink, 'start', -0.01) + text(madeBy, right, pictureHeight - 52, 32, 400, grey, 'end');
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${pictureWidth}" height="${pictureHeight}" viewBox="0 0 ${pictureWidth} ${pictureHeight}">${svg}</svg>`;
}

// The link preview is always the first mode, so it is the same for everyone: the map edge to edge, the title on a card at the top
// left and the key at the bottom left. Twitter may trim the sides to 1.91:1 and lays the page's title over the lower left on a
// phone, so the cards keep away from the edges.
export const previewWidth = 1800, previewHeight = 900;
export function previewSvg(given: PictureInput): string {
  const input: PictureInput = { ...given, mode: 'need' };
  const frame = worldFrame(previewWidth, previewHeight, 0, 24);
  let svg = worldMap(input, frame, { y: 0, height: previewHeight });
  const titleSize = fittedSize(siteTitle, 76, 800, 620, -0.035), cardWidth = Math.max(textWidth(siteTitle, titleSize, 800, -0.035), textWidth('What a couple needs invested to live well for life', 30, 400)) + 72;
  const titleCard: LabelBox = [110, 48, 110 + cardWidth, 48 + 212], key = keyCard(input, 110, previewHeight - 176, 1.1);
  svg += mapLabels(input, frame, 0, 1.55, [titleCard, key.box], [input.visitor].filter((code): code is string => !!code), 30);
  svg += `<rect x="${titleCard[0]}" y="${titleCard[1]}" width="${cardWidth}" height="212" rx="28" fill="${paper}"/>`
    + text(siteTitle, titleCard[0] + 36, titleCard[1] + 92, titleSize, 800, ink, 'start', -0.035)
    + text('What a couple needs invested to live well for life', titleCard[0] + 36, titleCard[1] + 142, 30, 400, grey)
    + text(input.address, titleCard[0] + 36, titleCard[1] + 186, 30, 700, ink);
  svg += key.svg;
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${previewWidth}" height="${previewHeight}" viewBox="0 0 ${previewWidth} ${previewHeight}">${svg}</svg>`;
}
