// Prints what a couple needs in some places, with every cost and the tax, and Palombo's figure beside his cities.
// Usage: node tools/snapshot/print-figures.ts [place code or name ...] [--rate 0.04] [--special]
import { readFile, readdir } from 'node:fs/promises';
import { defaultSettings, placeFigure, type Settings, type WithdrawalRate } from '../../src/capital.ts';
import { createPlaces, nameOf, plainLetters, type CityRow, type PlaceRows } from '../../src/places.ts';
import type { Snapshot } from '../../src/snapshot.ts';

for (const file of await readdir('src/tax')) if (file.endsWith('.ts') && !['tax-rules.ts', 'calculation.ts'].includes(file)) await import(`../../src/tax/${file}`);
const places = createPlaces(
  JSON.parse(await readFile('assets/map/places.json', 'utf8')) as PlaceRows,
  JSON.parse(await readFile('assets/map/cities.json', 'utf8')) as CityRow[],
  JSON.parse(await readFile('data/snapshot.json', 'utf8')) as Snapshot,
);
const argv = process.argv.slice(2), rateIndex = argv.indexOf('--rate');
const settings: Settings = { withdrawalRate: (rateIndex >= 0 ? Number(argv[rateIndex + 1]) : defaultSettings.withdrawalRate) as WithdrawalRate, regime: argv.includes('--special') ? 'special' : 'standard' };
const asked = argv.filter((word, index) => !word.startsWith('--') && argv[index - 1] !== '--rate');

const palombo = (await readFile('data/reference/palombo-2026-11-17.csv', 'utf8')).split('\n').slice(1).filter(Boolean).map(line => line.split(','));
const codes = asked.length
  ? asked.map(word => (places.rows[word] || places.cityByCode.has(word) ? word : places.cities.find(city => plainLetters(city.name) === plainLetters(word))?.code ?? word))
  : palombo.map(row => `CITY-${row[1]}`);
const millions = (usDollars: number) => `$${(usDollars / 1e6).toFixed(2)}M`;
for (const code of codes) {
  const figure = placeFigure(places, code, settings), his = palombo.find(row => `CITY-${row[1]}` === code)?.[3];
  const label = `${nameOf(places, code).padEnd(16)} ${his ? `Palombo $${(Number(his) / 1e6).toFixed(1)}M` : ''.padEnd(14)}`;
  if (figure.kind !== 'figure') { console.log(`${label}  ${figure.kind === 'occupied' ? 'not known (occupied Palestine)' : `missing ${figure.missing.join(', ')}`}`); continue; }
  const costs = figure.costs.map(cost => `${cost.part} ${Math.round(cost.usDollarsPerMonth)}${cost.isStandIn ? '*' : ''}`).join(' ');
  console.log(`${label}  ${millions(figure.capitalUsDollars)}  spend $${Math.round(figure.spendingUsDollarsPerYear / 12)}/mo (${costs})  tax $${Math.round(figure.tax.usDollarsPerYear)}/yr ${(figure.tax.usDollarsPerYear / figure.withdrawalUsDollarsPerYear * 100).toFixed(1)}%${figure.tax.isStandIn ? '*' : ''} ${figure.tax.regimeName}`);
}
console.log('* stand-in');
