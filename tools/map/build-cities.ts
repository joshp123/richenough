// Writes assets/map/cities.json: the cities the map can dot and label, biggest first, each with the shape it stands in.
// GeoNames cities15000 (CC BY 4.0): every city of 100,000 people or more, every capital, and every city a table names.
// In Palestine, cities carry their Arabic names (tools/map/palestine-places.mjs); the Golan Heights' are Syria's.
//
// Usage: node tools/map/build-cities.ts (after build-map-geometry.ts)
import { existsSync } from 'node:fs';
import { mkdir, readFile, readdir, writeFile } from 'node:fs/promises';
import { readMapGeometry, shapeAt, mapXOf, mapYOf } from '../../src/map-geometry.ts';
import { GOLAN_PLACES, PALESTINE_PLACES } from './palestine-places.mjs';

const smallestCity = 100_000;
const citiesUrl = 'https://download.geonames.org/export/dump/cities15000.zip', cache = 'cache/map';

if (!existsSync(`${cache}/cities15000.txt`)) {
  await mkdir(cache, { recursive: true });
  await writeFile(`${cache}/cities15000.zip`, Buffer.from(await (await fetch(citiesUrl)).arrayBuffer()));
  const { execFileSync } = await import('node:child_process');
  execFileSync('unzip', ['-o', '-q', `${cache}/cities15000.zip`, '-d', cache]);
}

// Cities the tables or tax rules name, which are always kept.
const namedCityIds = new Set<string>();
for (const folder of ['data/tables', 'data/reference', 'src/tax']) {
  if (!existsSync(folder)) continue;
  for (const file of await readdir(folder)) {
    for (const [, id] of (await readFile(`${folder}/${file}`, 'utf8')).matchAll(/CITY-(\d+)/g)) namedCityIds.add(id);
  }
}
for (const line of existsSync('data/reference/palombo-2026-11-17.csv') ? (await readFile('data/reference/palombo-2026-11-17.csv', 'utf8')).split('\n').slice(1) : []) {
  const id = line.split(',')[1];
  if (id) namedCityIds.add(id);
}

const geometry = readMapGeometry(new Uint8Array(await readFile('assets/map/shapes-fine.bin')));
// The shape a city stands in; a city on a coast the map has simplified away takes the nearest shape within about 15 km.
function shapeCodeAt(longitude: number, latitude: number): string | null {
  for (let step = 0; step <= 6; step++) {
    const reach = step * 0.025;
    for (const [dx, dy] of step ? [[reach, 0], [-reach, 0], [0, reach], [0, -reach], [reach, reach], [-reach, reach], [reach, -reach], [-reach, -reach]] : [[0, 0]]) {
      const shape = shapeAt(geometry, mapXOf(longitude + dx), mapYOf(latitude + dy));
      if (shape >= 0) return geometry.shapeCodes[shape];
    }
  }
  return null;
}

type City = [id: number, name: string, longitude: number, latitude: number, population: number, shapeCode: string, isCapital: 0 | 1, otherNames: string];
const cities: City[] = [];
let withoutShape = 0;
for (const line of (await readFile(`${cache}/cities15000.txt`, 'utf8')).split('\n')) {
  const cells = line.split('\t');
  if (cells.length < 15) continue;
  const [id, geonamesName, asciiName] = cells, latitude = Number(cells[4]), longitude = Number(cells[5]);
  const featureCode = cells[7], countryCode = cells[8], population = Number(cells[14]);
  const isCapital = featureCode === 'PPLC';
  let name = geonamesName, otherNames = asciiName !== geonamesName ? asciiName : '';
  if (countryCode === 'IL' || countryCode === 'PS') {
    const arabicName = GOLAN_PLACES.get(id) ?? PALESTINE_PLACES.get(id);
    if (!arabicName) continue;
    otherNames = [...new Set([geonamesName, asciiName, ...(id === '293397' ? ['Jaffa', 'Tel Aviv', 'Tel Aviv-Yafo'] : [])])].filter(other => other !== arabicName).join('|');
    name = arabicName;
  }
  if (population < smallestCity && !isCapital && !namedCityIds.has(id)) continue;
  const shapeCode = shapeCodeAt(longitude, latitude);
  if (!shapeCode) { withoutShape++; continue; }
  cities.push([Number(id), name, Number(longitude.toFixed(4)), Number(latitude.toFixed(4)), population, shapeCode, isCapital ? 1 : 0, otherNames]);
}
cities.sort((a, b) => b[4] - a[4]);
await writeFile('assets/map/cities.json', JSON.stringify(cities));
const missing = [...namedCityIds].filter(id => !cities.some(city => String(city[0]) === id));
console.log(`${cities.length} cities, ${withoutShape} off the map; named cities not found: ${missing.join(' ') || 'none'}`);
