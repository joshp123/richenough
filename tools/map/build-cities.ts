// Writes assets/map/cities.json: the cities the map can dot and label, biggest first, each with the shape it stands in.
// GeoNames cities15000 (CC BY 4.0): every city of 100,000 people or more, every capital, and every city a table names.
// In Palestine, cities carry their Arabic names (tools/map/palestine-places.mjs); the Golan Heights' are Syria's.
//
// Usage: node tools/map/build-cities.ts (after build-map-geometry.ts)
import { existsSync } from 'node:fs';
import { mkdir, readFile, readdir, writeFile } from 'node:fs/promises';
import { readMapGeometry, shapeAt } from '../../src/map-geometry.ts';
import { projectPoint } from '../../src/projection.ts';
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
      const shape = shapeAt(geometry, ...projectPoint(longitude + dx, latitude + dy));
      if (shape >= 0) return geometry.shapeCodes[shape];
    }
  }
  return null;
}

// How well known a city is, which decides how early its label shows: 0 for the cities in Palombo’s post, 1 for capitals of
// half a million and cities of 2.5 million, 2 for other cities of a million and capitals of 100,000, 3 for the rest.
const palomboCityIds = new Set((existsSync('data/reference/palombo-2026-11-17.csv') ? (await readFile('data/reference/palombo-2026-11-17.csv', 'utf8')).split('\n').slice(1) : []).map(line => line.split(',')[1]).filter(Boolean));
const fameOf = (id: string, population: number, isCapital: boolean) => (palomboCityIds.has(id) ? 0 : (isCapital && population >= 5e5) || population >= 2.5e6 ? 1 : population >= 1e6 || (isCapital && population >= 1e5) ? 2 : 3);
// A city within this distance of a bigger one is part of it (Brooklyn of New York, Callao of Lima) and gets no dot of its own.
const sameCityKm = 25;

type City = [id: number, name: string, longitude: number, latitude: number, population: number, shapeCode: string, isCapital: 0 | 1, otherNames: string, fame: number];
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
  cities.push([Number(id), name, Number(longitude.toFixed(4)), Number(latitude.toFixed(4)), population, shapeCode, isCapital ? 1 : 0, otherNames, fameOf(id, population, isCapital)]);
}
cities.sort((a, b) => a[8] - b[8] || b[4] - a[4]);
const kept: City[] = [];
const kilometresBetween = (a: City, b: City) => 111 * Math.hypot(a[3] - b[3], (a[2] - b[2]) * Math.cos(a[3] * Math.PI / 180));
for (const city of cities) {
  const isPartOfBiggerCity = city[8] > 0 && !city[6] && kept.some(other => kilometresBetween(city, other) < sameCityKm);
  if (!isPartOfBiggerCity) kept.push(city);
}
kept.sort((a, b) => b[4] - a[4]);
await writeFile('assets/map/cities.json', JSON.stringify(kept));
const missing = [...palomboCityIds].filter(id => !kept.some(city => String(city[0]) === id));
console.log(`${kept.length} cities (${cities.length - kept.length} merged into a bigger city nearby), ${withoutShape} off the map; Palombo's cities missing: ${missing.join(' ') || 'none'}`);
