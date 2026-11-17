// Writes assets/map/shapes-coarse.bin and shapes-fine.bin (see src/map-geometry.ts) and assets/map/places.json: every place on
// the map at the finest level the data supports, in the projection named in src/projection.ts, with its name and the place it
// belongs to.
//
//   US counties and county-equivalents: Census cartographic boundaries 2024, 1:5,000,000 (public domain).
//   Europe: Eurostat GISCO NUTS 2024 level 3 at 1:3,000,000 (EuroGeographics licence: free reuse with attribution);
//   the UK: ONS ITL 3 (January 2025), generalised (Open Government Licence).
//   Everywhere else: Natural Earth 10m countries, and its first-level regions for countries whose tables or tax rules
//   name such regions (public domain).
//
// Palestine is one shape over Israel and Palestine, without the Golan Heights, which are Syria's. Russia and Ukraine follow the
// borders in Russia's constitution: Crimea, Sevastopol and the Donetsk, Luhansk, Zaporizhzhia and Kherson regions are Russia.
//
// Usage: node tools/map/build-map-geometry.ts (downloads go to cache/map)
import earcut from 'earcut';
import { existsSync } from 'node:fs';
import { mkdir, readFile, readdir, writeFile } from 'node:fs/promises';
import * as polyclip from 'polyclip-ts';
import * as shapefile from 'shapefile';
import * as topojsonClient from 'topojson-client';
import * as topojsonServer from 'topojson-server';
import { assembleRing, gridSize, lineKinds, VarintWriter, type GeometryHeader, type LineKind } from '../../src/map-geometry.ts';
import { onTheMap, projection } from '../../src/projection.ts';

const cache = 'cache/map';
const downloads: Record<string, string> = {
  'ne_10m_admin_0_countries.geojson': 'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/v5.1.2/geojson/ne_10m_admin_0_countries.geojson',
  'ne_10m_admin_1_states_provinces.geojson': 'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/v5.1.2/geojson/ne_10m_admin_1_states_provinces.geojson',
  'cb_2024_us_county_5m.zip': 'https://www2.census.gov/geo/tiger/GENZ2024/shp/cb_2024_us_county_5m.zip',
  'NUTS_RG_03M_2024_4326_LEVL_3.geojson': 'https://gisco-services.ec.europa.eu/distribution/v2/nuts/geojson/NUTS_RG_03M_2024_4326_LEVL_3.geojson',
  'NUTS_AT_2024.csv': 'https://gisco-services.ec.europa.eu/distribution/v2/nuts/csv/NUTS_AT_2024.csv',
  'itl3_2025_bgc.geojson': 'https://services1.arcgis.com/ESMARspQHYMw9BZ9/arcgis/rest/services/ITL3_JAN_2025_UK_BGC_V2/FeatureServer/1/query?where=1%3D1&outFields=ITL325CD%2CITL325NM&outSR=4326&f=geojson',
  'lad25_itl.json': 'https://services1.arcgis.com/ESMARspQHYMw9BZ9/ArcGIS/rest/services/ITL125_ITL225_ITL325_LAU125_LAD25_UK_LU/FeatureServer/0/query?where=1%3D1&outFields=*&returnGeometry=false&f=json&resultRecordCount=2000',
};

// Natural Earth parts of countries drawn from finer sources are kept only where those sources leave a sizeable gap (Svalbard).
const smallestUncoveredPartKm2 = 150;

type Ring = [number, number][];
type Polygon = Ring[];
type Place = { code: string; name: string; parent: string | null; kind: 'country' | 'state' | 'county' | 'region' };
type Shape = { code: string; country: string; state: string; polygons: Polygon[] };

async function download(fileName: string): Promise<string> {
  const path = `${cache}/${fileName}`;
  if (!existsSync(path)) {
    await mkdir(cache, { recursive: true });
    const response = await fetch(downloads[fileName]);
    if (!response.ok) throw new Error(`${downloads[fileName]}: ${response.status}`);
    await writeFile(path, Buffer.from(await response.arrayBuffer()));
  }
  return path;
}
const readJson = async (fileName: string) => JSON.parse(await readFile(await download(fileName), 'utf8'));

function polygonsOf(geometry: { type: string; coordinates: unknown } | null): Polygon[] {
  if (!geometry) return [];
  if (geometry.type === 'Polygon') return [geometry.coordinates as Polygon];
  if (geometry.type === 'MultiPolygon') return geometry.coordinates as Polygon[];
  throw new Error(`Unexpected geometry ${geometry.type}`);
}

// Area in km² on the sphere, near enough to sort out islands.
function areaKm2(polygon: Polygon): number {
  const ringArea = (ring: Ring) => {
    let sum = 0;
    for (let index = 0; index < ring.length; index++) {
      const [x1, y1] = ring[index], [x2, y2] = ring[(index + 1) % ring.length];
      sum += (x2 - x1) * Math.PI / 180 * (2 + Math.sin(y1 * Math.PI / 180) + Math.sin(y2 * Math.PI / 180));
    }
    return Math.abs(sum * 6371 ** 2 / 2);
  };
  return ringArea(polygon[0]) - polygon.slice(1).reduce((sum, hole) => sum + ringArea(hole), 0);
}

function isInside([x, y]: [number, number], polygons: Polygon[]): boolean {
  let inside = false;
  for (const polygon of polygons) for (const ring of polygon) {
    for (let index = 0, previous = ring.length - 1; index < ring.length; previous = index++) {
      const [x1, y1] = ring[index], [x0, y0] = ring[previous];
      if ((y1 > y) !== (y0 > y) && x < (x0 - x1) * (y - y1) / (y0 - y1) + x1) inside = !inside;
    }
  }
  return inside;
}
// A point inside the polygon: the middle of the widest gap along the line through its outer ring's middle height.
function pointInside(polygon: Polygon): [number, number] {
  let low = Infinity, high = -Infinity;
  for (const [, latitude] of polygon[0]) { low = Math.min(low, latitude); high = Math.max(high, latitude); }
  const y = (low + high) / 2 + 1e-7;
  const crossings: number[] = [];
  for (const ring of polygon) for (let index = 0, previous = ring.length - 1; index < ring.length; previous = index++) {
    const [x1, y1] = ring[index], [x0, y0] = ring[previous];
    if ((y1 > y) !== (y0 > y)) crossings.push((x0 - x1) * (y - y1) / (y0 - y1) + x1);
  }
  crossings.sort((a, b) => a - b);
  let best: [number, number] = polygon[0][0], widest = -1;
  for (let index = 0; index + 1 < crossings.length; index += 2) {
    if (crossings[index + 1] - crossings[index] > widest) { widest = crossings[index + 1] - crossings[index]; best = [(crossings[index] + crossings[index + 1]) / 2, y]; }
  }
  return best;
}

const countryNames = new Intl.DisplayNames(['en-GB'], { type: 'region' });
const countryNameOverrides: Record<string, string> = {
  PS: 'Palestine', TR: 'Turkey', HK: 'Hong Kong', MO: 'Macau', US: 'United States', GB: 'United Kingdom', CZ: 'Czechia', KR: 'South Korea',
  KP: 'North Korea', CD: 'DR Congo', CG: 'Congo', MM: 'Myanmar', CI: 'Côte d’Ivoire', VA: 'Vatican City', XK: 'Kosovo', TW: 'Taiwan',
  RU: 'Russia', SY: 'Syria', FM: 'Micronesia', BN: 'Brunei', LA: 'Laos', VN: 'Vietnam', IR: 'Iran', BO: 'Bolivia', VE: 'Venezuela', TZ: 'Tanzania',
};
const countryName = (code: string) => countryNameOverrides[code] ?? countryNames.of(code) ?? code;

// Natural Earth gives no ISO code to some pieces of land; each goes to the country that holds or claims it.
const unnamedNaturalEarthUnits: Record<string, string | null> = {
  ESB: 'CY', WSB: 'CY', CYN: 'CY', CNM: 'CY', SOL: 'SO', USG: 'CU', KAS: 'IN', SPI: 'CL', BJN: 'CO', SER: 'CO',
  BRT: null, PGA: null, SCR: null,
};
const nutsCountryToIso = (code: string) => ({ EL: 'GR', UK: 'GB', TL: 'GB' } as Record<string, string>)[code] ?? code;
// The parts of Ukraine that Russia's constitution names, as Natural Earth codes its regions. Crimea and Sevastopol are already
// Russia's in Natural Earth's regions.
const ukrainianRegionsInRussiasConstitution = new Set(['UA-14', 'UA-09', 'UA-23', 'UA-65']);
// Natural Earth 5.1.2 gives Moscow city the code of Moscow region and the other way round.
const regionCodeFixes: Record<string, string> = { 'RU-MOW': 'RU-MOS', 'RU-MOS': 'RU-MOW' };
const regionNamesInRussiasConstitution: Record<string, string> = { 'UA-43': 'Crimea', 'UA-40': 'Sevastopol', 'UA-14': 'Donetsk', 'UA-09': 'Luhansk', 'UA-23': 'Zaporizhzhia', 'UA-65': 'Kherson' };
const usTerritoriesKeptAsCountries = new Set(['60', '66', '69', '78']); // American Samoa, Guam, Northern Mariana Islands, US Virgin Islands
// The Golan Heights: everything of Natural Earth's Israel east of the line the Syrian border followed before 1967.
const golanCut: Ring = [[35.62, 33.6], [35.652, 33.276], [35.626, 33.222], [35.64, 33.13], [35.616, 33.02], [35.632, 32.913], [35.651, 32.87],
  [35.642, 32.81], [35.636, 32.765], [35.663, 32.705], [35.594, 32.703], [35.594, 32.6], [36.3, 32.6], [36.3, 33.6], [35.62, 33.6]];

// Countries drawn by their first-level regions: those whose tables give figures under one of Natural Earth's regions' codes
// (ISO 3166-2), read from the tables' place codes alone.
async function countriesWithRegionData(regionCodes: Set<string>): Promise<Set<string>> {
  const countries = new Set<string>();
  for (const file of (await readdir('data/tables')).filter(name => name.endsWith('.csv'))) {
    for (const line of (await readFile(`data/tables/${file}`, 'utf8')).split('\n').slice(1)) {
      const code = line.slice(0, line.indexOf(','));
      if (regionCodes.has(code)) countries.add(code.slice(0, 2));
    }
  }
  for (const drawnOtherwise of ['US', 'UA', 'PS', 'IL', 'GB', 'XK', 'PR']) countries.delete(drawnOtherwise);
  return countries;
}

const places = new Map<string, Place>();
const addPlace = (place: Place) => { if (!places.has(place.code)) places.set(place.code, place); };
const shapes: Shape[] = [];
const addShape = (code: string, country: string, state: string, polygons: Polygon[]) => { if (polygons.length) shapes.push({ code, country, state, polygons }); };

// ---- Europe: NUTS 3 and ITL 3
const nuts = await readJson('NUTS_RG_03M_2024_4326_LEVL_3.geojson');
const nutsNames = new Map<string, string>();
for (const line of (await readFile(await download('NUTS_AT_2024.csv'), 'utf8')).split('\n').slice(1)) {
  const cells = line.match(/("([^"]|"")*"|[^,]*)(,|$)/g)!.map(cell => cell.replace(/,$/, '').replace(/^"|"$/g, '').replaceAll('""', '"'));
  if (cells[1]) nutsNames.set(cells[1], cells[2]);
}
const nutsCountries = new Set<string>();
const nutsParent = (code: string, country: string) => (code.length > 3 ? `NUTS-${code.slice(0, -1)}` : country);
for (const feature of nuts.features) {
  const id: string = feature.properties.NUTS_ID, country = nutsCountryToIso(feature.properties.CNTR_CODE);
  nutsCountries.add(country);
  for (let length = 3; length <= id.length; length++) {
    const code = id.slice(0, length);
    addPlace({ code: `NUTS-${code}`, name: nutsNames.get(code) ?? feature.properties.NAME_LATN, parent: nutsParent(code, country), kind: length === id.length ? 'county' : 'region' });
  }
  addShape(`NUTS-${id}`, country, country, polygonsOf(feature.geometry));
}
const itl = await readJson('itl3_2025_bgc.geojson');
const itlNames = new Map<string, string>();
for (const { attributes } of (await readJson('lad25_itl.json')).features) {
  itlNames.set(attributes.ITL325CD, attributes.ITL325NM); itlNames.set(attributes.ITL225CD, attributes.ITL225NM); itlNames.set(attributes.ITL125CD, attributes.ITL125NM);
}
for (const feature of itl.features) {
  const id: string = feature.properties.ITL325CD;
  for (let length = 3; length <= id.length; length++) {
    const code = id.slice(0, length);
    addPlace({ code: `NUTS-${code}`, name: itlNames.get(code) ?? feature.properties.ITL325NM, parent: nutsParent(code, 'GB'), kind: length === id.length ? 'county' : 'region' });
  }
  addShape(`NUTS-${id}`, 'GB', 'GB', polygonsOf(feature.geometry));
}
nutsCountries.add('GB');

// ---- The United States: counties and county-equivalents, Puerto Rico's municipalities
const countyFolder = `${cache}/cb_2024_us_county_5m`;
if (!existsSync(`${countyFolder}/cb_2024_us_county_5m.shp`)) {
  const { execFileSync } = await import('node:child_process');
  execFileSync('unzip', ['-o', '-q', await download('cb_2024_us_county_5m.zip'), '-d', countyFolder]);
}
const counties = await shapefile.read(`${countyFolder}/cb_2024_us_county_5m.shp`, `${countyFolder}/cb_2024_us_county_5m.dbf`, { encoding: 'utf-8' });
for (const feature of counties.features as { properties: Record<string, string>; geometry: { type: string; coordinates: unknown } }[]) {
  const { STATEFP, GEOID, NAMELSAD, STUSPS, STATE_NAME } = feature.properties;
  if (usTerritoriesKeptAsCountries.has(STATEFP)) continue;
  addPlace({ code: `US-${STUSPS}`, name: STATE_NAME, parent: 'US', kind: 'state' });
  addPlace({ code: `US-${GEOID}`, name: NAMELSAD, parent: `US-${STUSPS}`, kind: 'county' });
  addShape(`US-${GEOID}`, 'US', `US-${STUSPS}`, polygonsOf(feature.geometry));
}

// ---- Everywhere else: Natural Earth
const admin0 = await readJson('ne_10m_admin_0_countries.geojson');
const admin1 = await readJson('ne_10m_admin_1_states_provinces.geojson');
const regionCountries = await countriesWithRegionData(new Set(admin1.features.map((feature: { properties: { iso_3166_2: string } }) => feature.properties.iso_3166_2)));
const countryPolygons = new Map<string, Polygon[]>();
for (const feature of admin0.features) {
  const { ISO_A2_EH, ADM0_A3 } = feature.properties;
  const code = ADM0_A3 in unnamedNaturalEarthUnits ? unnamedNaturalEarthUnits[ADM0_A3] : ISO_A2_EH === '-99' ? null : ISO_A2_EH;
  if (!code || code === 'AQ') continue;
  countryPolygons.set(code, [...(countryPolygons.get(code) ?? []), ...polygonsOf(feature.geometry)]);
}

// Palestine over Israel and Palestine, the Golan Heights to Syria.
const israel = countryPolygons.get('IL')!, palestine = countryPolygons.get('PS')!;
const golan = polyclip.intersection(israel as never, [golanCut] as never) as Polygon[];
countryPolygons.set('PS', polyclip.union(polyclip.difference(israel as never, [golanCut] as never) as never, palestine as never) as Polygon[]);
countryPolygons.set('SY', polyclip.union(countryPolygons.get('SY')! as never, golan as never) as Polygon[]);
countryPolygons.delete('IL');

// Russia and Ukraine from Natural Earth's regions, which share their borders exactly.
const russianRegions: Polygon[] = [], ukrainianRegions: Polygon[] = [];
for (const feature of admin1.features) {
  const { adm0_a3, iso_3166_2 } = feature.properties;
  if (adm0_a3 === 'RUS' || ukrainianRegionsInRussiasConstitution.has(iso_3166_2)) russianRegions.push(...polygonsOf(feature.geometry));
  else if (adm0_a3 === 'UKR') ukrainianRegions.push(...polygonsOf(feature.geometry));
}
countryPolygons.set('RU', polyclip.union(...(russianRegions as never[])) as Polygon[]);
countryPolygons.set('UA', polyclip.union(...(ukrainianRegions as never[])) as Polygon[]);

const shapesOfCountry = (country: string) => shapes.filter(shape => shape.country === country).flatMap(shape => shape.polygons);
for (const [code, polygons] of countryPolygons) {
  addPlace({ code, name: countryName(code), parent: null, kind: 'country' });
  if (code === 'US' || nutsCountries.has(code)) {
    // Keep only sizeable parts the finer source leaves out, such as Svalbard and Jan Mayen.
    const finer = shapesOfCountry(code);
    addShape(code, code, code, polygons.filter(polygon => areaKm2(polygon) >= smallestUncoveredPartKm2 && !isInside(pointInside(polygon), finer)));
  } else if (code === 'PR') {
    // Puerto Rico is drawn by its municipalities, as part of the United States' county file.
  } else if (regionCountries.has(code)) {
    // Russia's regions include the six in its constitution, under Natural Earth's codes for them.
    const isRegionOf = ({ iso_a2, adm0_a3, iso_3166_2 }: { iso_a2: string; adm0_a3: string; iso_3166_2: string }) =>
      (code === 'RU' ? adm0_a3 === 'RUS' || ukrainianRegionsInRussiasConstitution.has(iso_3166_2) : iso_a2 === code);
    for (const region of admin1.features.filter((feature: { properties: Parameters<typeof isRegionOf>[0] }) => isRegionOf(feature.properties))) {
      const { name } = region.properties, iso_3166_2 = regionCodeFixes[region.properties.iso_3166_2] ?? region.properties.iso_3166_2;
      addPlace({ code: iso_3166_2, name: regionNamesInRussiasConstitution[iso_3166_2] ?? name ?? countryName(code), parent: code, kind: 'state' });
      addShape(iso_3166_2, code, code, polygonsOf(region.geometry));
    }
  } else {
    addShape(code, code, code, polygons);
  }
}
for (const code of ['US', ...nutsCountries]) addPlace({ code, name: countryName(code), parent: null, kind: 'country' });
places.get('US-PR')!.parent = 'US';

// ---- Only as fine as the data: a county or region is drawn as itself where a table or a tax rule names it or a place inside
// it, and otherwise as part of the nearest place above it that has data of its own. Shapes drawn as one place share a code, and
// no line is drawn between them.
// A row counts for the place it was measured for: a country's figure copied under each of its regions counts for the country.
const chainOfPlace = (code: string) => { const chain: string[] = []; for (let current: string | null = code; current; current = places.get(current)?.parent ?? null) chain.push(current); return chain; };
const csvCells = (line: string) => [...line.matchAll(/("([^"]|"")*"|[^,]*)(,|$)/g)].map(match => match[1].replace(/^"|"$/g, '').replaceAll('""', '"'));
const codesWithData = new Set<string>();
for (const file of (await readdir('data/tables')).filter(name => name.endsWith('.csv') && !name.startsWith('lifestyle'))) {
  for (const line of (await readFile(`data/tables/${file}`, 'utf8')).split('\n').slice(1)) {
    const [code, , , , , measuredFor] = csvCells(line);
    if (!code) continue;
    codesWithData.add(chainOfPlace(code).slice(1).includes(measuredFor) ? measuredFor : code);
  }
}
const { taxRulesFor } = await import('../../src/tax/tax-rules.ts');
for (const file of await readdir('src/tax')) if (file.endsWith('.ts') && !['tax-rules.ts', 'calculation.ts'].includes(file)) await import(`../../src/tax/${file}`);
const hasData = (code: string) => codesWithData.has(code) || !!taxRulesFor([code]);
for (const shape of shapes) {
  const chain = chainOfPlace(shape.code);
  shape.code = chain.find(hasData) ?? chain.at(-1)!;
}

// ---- To map units, into one topology, so neighbours share their borders and each border is simplified once. Each polygon goes
// whole to whichever side of the map's edge its middle is on.
const projectPolygon = (polygon: Polygon): Polygon => {
  const middle = polygon[0].reduce((sum, [longitude]) => sum + longitude, 0) / polygon[0].length, turn = onTheMap(middle) - middle;
  return polygon.map(ring => ring.map(([longitude, latitude]) => projection.project(longitude + turn, latitude)));
};
const features = shapes.map((shape, index) => ({
  type: 'Feature' as const, id: index, properties: {},
  geometry: { type: 'MultiPolygon' as const, coordinates: shape.polygons.filter(polygon => polygon[0].some(point => point[1] > -60)).map(projectPolygon) },
}));
const topology = topojsonServer.topology({ shapes: { type: 'FeatureCollection', features } } as never, 2 ** 22) as never as {
  arcs: [number, number][][]; transform: { scale: [number, number]; translate: [number, number] }; objects: { shapes: { geometries: { arcs: number[][][]; type: string }[] } };
};

// Visvalingam's weights on each arc, in map units squared. An arc's ends always stay; a closed arc keeps at least four points.
const { scale, translate } = topology.transform;
const absoluteArcs = topology.arcs.map(arc => {
  let x = 0, y = 0;
  return arc.map(([dx, dy]) => { x += dx; y += dy; return [x * scale[0] + translate[0], y * scale[1] + translate[1]] as [number, number]; });
});
function simplifyArc(arc: [number, number][], smallestTriangle: number): [number, number][] {
  if (arc.length <= 2) return arc;
  const weight = new Float64Array(arc.length).fill(Infinity), removed = new Uint8Array(arc.length);
  // A projection that blows up the far north has its coasts there simplified as if they were no further north than 50 degrees.
  const highLatitudeDamping = arc.map(([mapX, mapY]) => (projection.enlargesHighLatitudes ? Math.min(1, (Math.cos(projection.invert(mapX, mapY)[1] * Math.PI / 180) / Math.cos(50 * Math.PI / 180)) ** 2) : 1));
  const area = (a: number, b: number, c: number) => highLatitudeDamping[b] * Math.abs((arc[b][0] - arc[a][0]) * (arc[c][1] - arc[a][1]) - (arc[c][0] - arc[a][0]) * (arc[b][1] - arc[a][1])) / 2;
  const previous = arc.map((_, index) => index - 1), next = arc.map((_, index) => index + 1);
  for (let index = 1; index < arc.length - 1; index++) weight[index] = area(index - 1, index, index + 1);
  const isClosed = arc[0][0] === arc[arc.length - 1][0] && arc[0][1] === arc[arc.length - 1][1];
  // Always remove the least important point next, so a binary heap of points by weight.
  const heap: number[] = [], heapWeight = new Float64Array(arc.length);
  const push = (index: number) => { heapWeight[index] = weight[index]; heap.push(index); let child = heap.length - 1; while (child) { const parent = (child - 1) >> 1; if (heapWeight[heap[parent]] <= heapWeight[heap[child]]) break; [heap[parent], heap[child]] = [heap[child], heap[parent]]; child = parent; } };
  const pop = () => { const top = heap[0], last = heap.pop()!; if (heap.length) { heap[0] = last; let parent = 0; for (;;) { const left = parent * 2 + 1, right = left + 1; let smallest = parent; if (left < heap.length && heapWeight[heap[left]] < heapWeight[heap[smallest]]) smallest = left; if (right < heap.length && heapWeight[heap[right]] < heapWeight[heap[smallest]]) smallest = right; if (smallest === parent) break; [heap[parent], heap[smallest]] = [heap[smallest], heap[parent]]; parent = smallest; } } return top; };
  for (let index = 1; index < arc.length - 1; index++) push(index);
  let remaining = arc.length, floor = 0;
  while (heap.length) {
    const index = pop();
    if (removed[index] || heapWeight[index] !== weight[index]) continue;
    const effective = Math.max(weight[index], floor);
    if (effective >= smallestTriangle || (isClosed && remaining <= 4)) break;
    floor = effective;
    removed[index] = 1; remaining--;
    const before = previous[index], after = next[index];
    next[before] = after; previous[after] = before;
    for (const neighbour of [before, after]) {
      if (neighbour <= 0 || neighbour >= arc.length - 1) continue;
      weight[neighbour] = area(previous[neighbour], neighbour, next[neighbour]);
      push(neighbour);
    }
  }
  return arc.filter((_, index) => !removed[index]);
}

const geometries = topology.objects.shapes.geometries;
const polygonsOfGeometry = (geometry: { type: string; arcs: unknown }) => (geometry.type === 'Polygon' ? [geometry.arcs as number[][]] : (geometry.arcs as number[][][]) ?? []);

// Which shapes each arc divides, for the lines: each border once, as prominent as the most important thing it divides.
const arcUsers = new Map<number, number[]>();
geometries.forEach((geometry, shapeIndex) => {
  for (const arc of polygonsOfGeometry(geometry).flat(2)) { const index = arc < 0 ? ~arc : arc; arcUsers.set(index, [...(arcUsers.get(index) ?? []), shapeIndex]); }
});
function lineKindOf(arc: number): LineKind | null {
  const users = arcUsers.get(arc)!, a = shapes[users[0]], b = shapes[users[1] ?? users[0]];
  if (users.length === 1 || a.country !== b.country) return 'country';
  if (a.code === b.code) return null;
  return a.state !== b.state ? 'state' : 'region';
}

const ringArea = (flat: number[]) => { let sum = 0; for (let index = 0, previous = flat.length - 2; index < flat.length; previous = index, index += 2) sum += (flat[previous] - flat[index]) * (flat[previous + 1] + flat[index + 1]); return Math.abs(sum / 2); };
const { gzipSync } = await import('node:zlib');
const mebibytes = (bytes: number) => `${(bytes / 1048576).toFixed(2)} MiB`;

// One file per level of detail: the page draws the coarse one first and swaps in the fine one once it has arrived.
async function writeLevel(fileName: string, detailZoom: number): Promise<void> {
  // A point stays when the triangle it makes with its neighbours covers at least 0.6 of a pixel at the detail zoom; islands smaller
  // than a few pixels there go, unless they are all a place has.
  const pixel = 1 / (256 * 2 ** detailZoom), smallestTriangle = 0.6 * pixel ** 2, smallestIsland = (2.5 * pixel * gridSize) ** 2;
  const arcs = absoluteArcs.map(arc => Int32Array.from(simplifyArc(arc, smallestTriangle).flat(), value => Math.round(value * gridSize)));

  // The shapes' rings as arc lists, keeping only what is drawn; the arcs they use get new numbers in order of first use.
  const usedArcNumber = new Map<number, number>(), usedArcs: number[] = [];
  const renumber = (reference: number) => {
    const arc = reference < 0 ? ~reference : reference;
    if (!usedArcNumber.has(arc)) { usedArcNumber.set(arc, usedArcs.length); usedArcs.push(arc); }
    return reference < 0 ? ~usedArcNumber.get(arc)! : usedArcNumber.get(arc)!;
  };
  const shapeWriter = new VarintWriter(), triangleWriter = new VarintWriter();
  let pointCount = 0, ringCount = 0, triangleIndexCount = 0;
  for (const geometry of geometries) {
    const polygons = polygonsOfGeometry(geometry).map(polygon => polygon.map(references => ({ references, points: assembleRing(arcs, references) })));
    const largest = polygons.reduce((best, polygon) => (polygon[0].points.length && (!best || ringArea(polygon[0].points) > ringArea(best[0].points)) ? polygon : best), null as typeof polygons[number] | null);
    const rings: { references: number[]; isOuter: boolean }[] = [], triangles: number[] = [];
    let base = 0;
    for (const polygon of polygons) {
      if (polygon[0].points.length < 6 || (polygon !== largest && ringArea(polygon[0].points) < smallestIsland)) continue;
      const kept = [polygon[0], ...polygon.slice(1).filter(ring => ring.points.length >= 6)];
      const flat: number[] = [], holeStarts: number[] = [];
      kept.forEach((ring, index) => { if (index) holeStarts.push(flat.length / 2); flat.push(...ring.points); });
      for (const index of earcut(flat, holeStarts)) triangles.push(base + index);
      base += flat.length / 2;
      kept.forEach((ring, index) => rings.push({ references: ring.references, isOuter: index === 0 }));
    }
    shapeWriter.unsigned(rings.length);
    let previousReference = 0;
    for (const ring of rings) {
      shapeWriter.unsigned(ring.isOuter ? 1 : 0);
      shapeWriter.unsigned(ring.references.length);
      for (const reference of ring.references.map(renumber)) { shapeWriter.signed(reference - previousReference); previousReference = reference; }
      ringCount++;
    }
    pointCount += base;
    triangleWriter.unsigned(triangles.length);
    let previousIndex = 0;
    for (const index of triangles) { triangleWriter.signed(index - previousIndex); previousIndex = index; }
    triangleIndexCount += triangles.length;
  }

  const arcWriter = new VarintWriter();
  let x = 0, y = 0, arcPointCount = 0;
  for (const arc of usedArcs.map(index => arcs[index])) {
    arcWriter.unsigned(arc.length / 2);
    for (let index = 0; index < arc.length; index += 2) { arcWriter.signed(arc[index] - x); arcWriter.signed(arc[index + 1] - y); x = arc[index]; y = arc[index + 1]; }
    arcPointCount += arc.length / 2;
  }
  const lineWriter = new VarintWriter(), lineArcCounts = {} as Record<LineKind, number>;
  for (const kind of lineKinds) {
    const numbers = usedArcs.map((arc, number) => (lineKindOf(arc) === kind ? number : -1)).filter(number => number >= 0);
    let previous = 0;
    for (const number of numbers) { lineWriter.unsigned(number - previous); previous = number; }
    lineArcCounts[kind] = numbers.length;
  }

  const header: GeometryHeader = { projection: projection.name, shapeCodes: shapes.map(shape => shape.code), arcCount: usedArcs.length, arcPointCount, ringCount, pointCount, triangleIndexCount, lineArcCounts };
  const headerBytes = Buffer.from(JSON.stringify(header)), lengthBytes = Buffer.alloc(4);
  lengthBytes.writeUInt32LE(headerBytes.length);
  const sections = [arcWriter.result(), shapeWriter.result(), triangleWriter.result(), lineWriter.result()];
  const file = Buffer.concat([lengthBytes, headerBytes, ...sections]);
  await writeFile(`assets/map/${fileName}`, file);
  console.log(`${fileName}: ${arcPointCount} arc points, ${pointCount} ring points, ${triangleIndexCount / 3} triangles; ${mebibytes(gzipSync(file, { level: 9 }).length)} gzipped `
    + `(arcs ${mebibytes(gzipSync(sections[0]).length)}, rings ${mebibytes(gzipSync(sections[1]).length)}, triangles ${mebibytes(gzipSync(sections[2]).length)}, lines ${mebibytes(gzipSync(sections[3]).length)})`);
}

await mkdir('assets/map', { recursive: true });
await writeLevel('shapes-coarse.bin', 3.5);
await writeLevel('shapes-fine.bin', Number(process.env.FINE_ZOOM ?? 6.5));

const placesOut: Record<string, [string, string | null, Place['kind']]> = {};
for (const place of [...places.values()].sort((a, b) => a.code.localeCompare(b.code))) placesOut[place.code] = [place.name, place.parent, place.kind];
await writeFile('assets/map/places.json', JSON.stringify(placesOut));
console.log(`${shapes.length} shapes, ${places.size} places; first-level regions for ${[...regionCountries].sort().join(' ') || 'no country'}`);
