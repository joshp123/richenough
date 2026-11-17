// Writes assets/fonts: Archivo (SIL Open Font Licence) in the five weights the design uses, cut down to the characters the site
// prints, as TTF for the share pictures and WOFF2 for the page, and how wide each character is, so the share pictures can fit
// text without a browser.
// Usage: node tools/build-fonts.ts
import { mkdir, writeFile } from 'node:fs/promises';
import opentype from 'opentype.js';
import subsetFont from 'subset-font';

const archivoFolder = 'https://raw.githubusercontent.com/Omnibus-Type/Archivo/master';
export const fontWeights = { 400: 'Archivo-Regular', 500: 'Archivo-Medium', 600: 'Archivo-SemiBold', 700: 'Archivo-Bold', 800: 'Archivo-ExtraBold' };
const charactersBetween = (first: number, last: number) => Array.from({ length: last - first + 1 }, (_, index) => String.fromCodePoint(first + index)).join('');
const latinLettersWithAccents = charactersBetween(0x20, 0x7e) + charactersBetween(0xa0, 0x17f) + charactersBetween(0x1e00, 0x1eff) + 'ȘșȚțəƏ';
const punctuationAndCurrencySymbols = '‘’“”–—…‹›−→×·•฿₫₱₩₪₹₺€₽₴₦₡₲₵₸₮₭₼₾£¥¢';
const printedCharacters = latinLettersWithAccents + punctuationAndCurrencySymbols;

await mkdir('assets/fonts', { recursive: true });
const advanceWidthsByWeight: Record<string, Record<string, number>> = {};
let unitsPerEm = 0;
for (const [weight, fontName] of Object.entries(fontWeights)) {
  const response = await fetch(`${archivoFolder}/fonts/ttf/${fontName}.ttf`);
  if (!response.ok) throw new Error(`${fontName}: ${response.status}`);
  const whole = Buffer.from(await response.arrayBuffer());
  const truetype = await subsetFont(whole, printedCharacters, { targetFormat: 'truetype' });
  await writeFile(`assets/fonts/${fontName}.ttf`, truetype);
  await writeFile(`assets/fonts/${fontName}.woff2`, await subsetFont(whole, printedCharacters, { targetFormat: 'woff2' }));
  const font = opentype.parse(truetype.buffer.slice(truetype.byteOffset, truetype.byteOffset + truetype.byteLength));
  unitsPerEm = font.unitsPerEm;
  advanceWidthsByWeight[weight] = {};
  for (const character of printedCharacters) {
    const glyph = font.charToGlyph(character);
    if (glyph.index !== 0) advanceWidthsByWeight[weight][character] = glyph.advanceWidth!;
  }
  console.log(`${fontName}: ${truetype.length} bytes as TTF`);
}
await writeFile('assets/fonts/archivo-advance-widths.json', JSON.stringify({ unitsPerEm, advanceWidthsByWeight }));
await writeFile('assets/fonts/OFL-Archivo.txt', await (await fetch(`${archivoFolder}/OFL.txt`)).text());
