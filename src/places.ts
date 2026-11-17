// Places: their names, the places they belong to, and the cities on the map. The page and the Worker share this.
import type { Snapshot } from './snapshot.ts';

export type PlaceKind = 'country' | 'state' | 'county' | 'region';
// From assets/map/places.json: name, the code of the place it belongs to (null for a country), and what kind of place it is.
export type PlaceRows = Record<string, [name: string, parent: string | null, kind: PlaceKind]>;
// From assets/map/cities.json, biggest first. fame: 0 for Palombo's cities, 1 for capitals of half a million and cities of 2.5
// million, 2 for other cities of a million and capitals of 100,000, 3 for the rest (tools/map/build-cities.ts).
export type CityRow = [id: number, name: string, longitude: number, latitude: number, population: number, shapeCode: string, isCapital: 0 | 1, otherNames: string, fame: number];
export type City = { code: string; name: string; longitude: number; latitude: number; population: number; shapeCode: string; isCapital: boolean; otherNames: string[]; fame: number };

export type Places = {
  rows: PlaceRows;
  cities: City[];
  cityByCode: Map<string, City>;
  snapshot: Snapshot;
};

export function createPlaces(rows: PlaceRows, cityRows: CityRow[], snapshot: Snapshot): Places {
  const cities = cityRows.map(([id, name, longitude, latitude, population, shapeCode, isCapital, otherNames, fame]) => ({
    code: `CITY-${id}`, name, longitude, latitude, population, shapeCode, isCapital: isCapital === 1, otherNames: otherNames ? otherNames.split('|') : [], fame,
  }));
  return { rows, cities, cityByCode: new Map(cities.map(city => [city.code, city])), snapshot };
}

// The place and every place it belongs to, most specific first: ['CITY-5368361', 'US-06037', 'US-CA', 'US'].
export function chainOf(places: Places, code: string): string[] {
  const city = places.cityByCode.get(code);
  if (city) return [code, ...chainOf(places, city.shapeCode)];
  const chain: string[] = [];
  for (let current: string | null = code; current && !chain.includes(current); current = places.rows[current]?.[1] ?? null) chain.push(current);
  return chain;
}

export const countryOf = (places: Places, code: string) => chainOf(places, code).at(-1)!;

export function nameOf(places: Places, code: string): string {
  return places.cityByCode.get(code)?.name ?? places.rows[code]?.[0] ?? places.snapshot.cityNames[code] ?? code;
}

// The words under a place's name: the country, and for a US county or a region, the state or region above it too.
export function contextOf(places: Places, code: string): string {
  const chain = chainOf(places, code), country = chain.at(-1)!;
  if (chain.length === 1) return '';
  const city = places.cityByCode.get(code);
  if (city) return nameOf(places, country);
  const state = chain.length >= 3 ? chain[chain.length - 2] : null;
  const countryName = nameOf(places, country);
  if (state && places.rows[state]?.[2] === 'state') return `${nameOf(places, state)}, ${countryName}`;
  return countryName;
}

// What a figure's "measured for" means to a visitor: a place's name, or the words as written.
export function measuredForWords(places: Places, measuredFor: string): string {
  if (/^(CITY-\d+|US-[A-Z0-9]+|NUTS-[A-Z0-9]+|[A-Z]{2}(-[A-Z0-9]{1,3})?)$/.test(measuredFor)) return nameOf(places, measuredFor);
  return measuredFor;
}

// The flag codes a place shows: its country's flag, and a US state's own flag over its corner.
export function flagCodesOf(places: Places, code: string): { country: string; state: string | null } {
  const chain = chainOf(places, code), country = chain.at(-1)!;
  if (chain.includes('US-PR')) return { country: 'PR', state: null };
  const state = chain.find(link => /^US-[A-Z]{2}$/.test(link)) ?? null;
  return { country, state };
}

// Plain letters for search: no accents, lower case.
export const plainLetters = (text: string) => text.normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/ø/g, 'o').replace(/æ/g, 'ae').replace(/ß/g, 'ss').replace(/ł/g, 'l').replace(/[’']/g, '').toLowerCase();
