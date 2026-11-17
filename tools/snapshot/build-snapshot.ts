// Writes data/snapshot.json, everything the page and the Worker need besides the map: each component's figures by place code,
// the lifestyle, exchange rates, sources, and the names of places figures were measured for that are not on the map.
//
// Stand-ins: until a table has a figure for a country, a component falls back to what Alessandro Palombo's post implies for
// his city in that country (data/reference/palombo-2026-11-17.csv), and exchange rates fall back to the ECB's reference rates
// and fixed pegs. Every stand-in is marked as one, and the page says so beside it.
//
// Usage: node tools/snapshot/build-snapshot.ts
import { existsSync } from 'node:fs';
import { mkdir, readFile, readdir, writeFile } from 'node:fs/promises';
import countryToCurrency from 'country-to-currency';
import { components, type Component, type Figure, type Snapshot, type Source } from '../../src/snapshot.ts';

function parseCsv(text: string): Record<string, string>[] {
  const rows: string[][] = [];
  let row: string[] = [], cell = '', quoted = false;
  for (let index = 0; index < text.length; index++) {
    const character = text[index];
    if (quoted) {
      if (character === '"' && text[index + 1] === '"') { cell += '"'; index++; } else if (character === '"') quoted = false; else cell += character;
    } else if (character === '"') quoted = true;
    else if (character === ',') { row.push(cell); cell = ''; }
    else if (character === '\n' || character === '\r') {
      if (character === '\r' && text[index + 1] === '\n') index++;
      row.push(cell); cell = '';
      if (row.some(value => value !== '')) rows.push(row);
      row = [];
    } else cell += character;
  }
  if (cell !== '' || row.length) { row.push(cell); rows.push(row); }
  const [header, ...body] = rows;
  return body.map(values => Object.fromEntries(header.map((name, index) => [name.trim(), (values[index] ?? '').trim()])));
}
const readCsv = async (path: string) => parseCsv(await readFile(path, 'utf8'));

const tableNameOfComponent: Record<Component, string> = {
  rent: 'rent-two-bedroom', everyday: 'price-level-everyday', car: 'car', housekeeper: 'housekeeper-wage', health: 'health-cover',
};
const figures = Object.fromEntries(components.map(component => [component, {}])) as Snapshot['figures'];
const exchangeRates: Snapshot['exchangeRates'] = {};
const problems: string[] = [];

for (const file of (await readdir('data/tables')).filter(name => name.endsWith('.csv')).sort()) {
  const tableName = file.split('.')[0];
  if (tableName === 'lifestyle') continue;
  const rows = await readCsv(`data/tables/${file}`);
  if (tableName === 'exchange-rates') {
    for (const row of rows) exchangeRates[row.currency] = { perUsDollar: Number(row.amount), period: row.period, sourceId: row.source_id, isStandIn: false };
    continue;
  }
  const component = components.find(candidate => tableNameOfComponent[candidate] === tableName);
  if (!component) { problems.push(`${file}: no component is called ${tableName}`); continue; }
  for (const row of rows) {
    const amount = Number(row.amount);
    if (!row.place_code || !Number.isFinite(amount)) { problems.push(`${file}: unreadable row ${JSON.stringify(row)}`); continue; }
    if (figures[component][row.place_code]) problems.push(`${file}: ${row.place_code} appears twice`);
    figures[component][row.place_code] = { amount, currency: row.currency, unit: row.unit, period: row.period, measuredFor: row.measured_for, sourceId: row.source_id, note: row.note };
  }
}

// A figure measured for a bigger place than the row names (a country's figure copied under each region) also stands for that
// bigger place, so the map can draw the regions as one when nothing else varies between them.
const places: Record<string, [string, string | null, string]> = JSON.parse(await readFile('assets/map/places.json', 'utf8'));
const ancestorsOf = (code: string) => { const chain: string[] = []; for (let current = places[code]?.[1] ?? null; current; current = places[current]?.[1] ?? null) chain.push(current); return chain; };
for (const component of components) {
  for (const [code, figure] of Object.entries(figures[component])) {
    if (ancestorsOf(code).includes(figure.measuredFor)) figures[component][figure.measuredFor] ??= figure;
  }
}

// The lifestyle every place is priced for.
const lifestyleRows = Object.fromEntries((await readCsv('data/tables/lifestyle.csv')).map(row => [row.item, row]));
const lifestyle: Snapshot['lifestyle'] = {
  everydayUsDollarsPerMonth: Number(lifestyleRows.everyday_spending_at_us_average_prices.amount),
  housekeeperHoursPerWeek: Number(lifestyleRows.housekeeper_hours.amount),
  tripsUsDollarsPerYear: Number(lifestyleRows.trips.amount),
  sourceIds: { everyday: lifestyleRows.everyday_spending_at_us_average_prices.source_id, trips: lifestyleRows.trips.source_id },
};

// Stand-ins from Palombo's cities: his rent and everyday spending, and his flat sum for car, help, health and trips less our trips,
// split in fixed shares. One city's figures stand for its whole country.
const palomboSourceId = 'palombo-2026-11-17';
const standIns = Object.fromEntries(components.map(component => [component, {}])) as Snapshot['standIns'];
const taxStandIns: Snapshot['taxStandIns'] = {};
const flatForCarHelpHealthAndTrips = 2010, carShare = 0.45, healthShare = 0.33, housekeeperShare = 0.22;
const hoursPerMonth = lifestyle.housekeeperHoursPerWeek * 52 / 12;
for (const city of await readCsv('data/reference/palombo-2026-11-17.csv')) {
  if (standIns.rent[city.country]) continue;
  const measuredFor = `CITY-${city.geonames_id}`, rest = flatForCarHelpHealthAndTrips - lifestyle.tripsUsDollarsPerYear / 12;
  const standIn = (amount: number, unit: string, note: string): Figure => ({ amount: Math.round(amount * 100) / 100, currency: 'USD', unit, period: '2026', measuredFor, sourceId: palomboSourceId, note, isStandIn: true });
  standIns.rent[city.country] = standIn(Number(city.inferred_rent_usd_month), 'per_month', 'Livingcost’s three-bed flat in the centre, as Palombo used it');
  standIns.everyday[city.country] = standIn(Number(city.inferred_everyday_couple_usd_month) / lifestyle.everydayUsDollarsPerMonth * 100, 'index_us_100', 'Palombo’s everyday spending for a couple against ours at US prices');
  standIns.car[city.country] = standIn(rest * carShare, 'per_month', 'A share of Palombo’s flat sum for car, help and health cover');
  standIns.health[city.country] = standIn(rest * healthShare, 'per_month', 'A share of Palombo’s flat sum for car, help and health cover');
  standIns.housekeeper[city.country] = standIn(rest * housekeeperShare / hoursPerMonth, 'per_hour', 'A share of Palombo’s flat sum for car, help and health cover');
  taxStandIns[city.country] = { rate: Number(city.inferred_tax_rate), measuredFor, sourceId: palomboSourceId };
}

// Exchange rates the tables lack: the ECB's reference rates, then currencies pegged to the dollar or the euro.
const ecbFile = 'cache/map/eurofxref-daily.xml';
if (!existsSync(ecbFile)) {
  await mkdir('cache/map', { recursive: true });
  await writeFile(ecbFile, await (await fetch('https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml')).text());
}
const ecb = await readFile(ecbFile, 'utf8'), ecbDate = ecb.match(/time=['"]([\d-]+)['"]/)![1];
const euroRates = Object.fromEntries([...ecb.matchAll(/currency=['"](\w+)['"] rate=['"]([\d.]+)['"]/g)].map(([, currency, rate]) => [currency, Number(rate)]));
euroRates.EUR = 1;
const perUsDollarFromEuro = (perEuro: number) => perEuro / euroRates.USD;
const peggedToDollar: Record<string, number> = { USD: 1, AED: 3.6725, SAR: 3.75, OMR: 0.3845, QAR: 3.64, BHD: 0.376, JOD: 0.709, PAB: 1, BSD: 1, BMD: 1, XCD: 2.7, BZD: 2, ANG: 1.79, AWG: 1.79, KYD: 0.833, BBD: 2, DJF: 177.721, ERN: 15, LBP: 89500 };
const peggedToEuro: Record<string, number> = { XOF: 655.957, XAF: 655.957, KMF: 491.96775, BAM: 1.95583, BGN: 1.95583, CVE: 110.265, XPF: 119.33174 };
const standInRate = (currency: string, perUsDollar: number, sourceId: string, period: string) => {
  if (!exchangeRates[currency]) exchangeRates[currency] = { perUsDollar, period, sourceId, isStandIn: true };
};
for (const [currency, perEuro] of Object.entries(euroRates)) standInRate(currency, perUsDollarFromEuro(perEuro), 'ecb-reference-rates', ecbDate);
for (const [currency, rate] of Object.entries(peggedToDollar)) standInRate(currency, rate, 'currency-pegs', '2026');
for (const [currency, perEuro] of Object.entries(peggedToEuro)) standInRate(currency, perUsDollarFromEuro(perEuro), 'currency-pegs', ecbDate);

// Then the US Treasury's quarterly reporting rates, for every other currency (public domain).
const treasuryFile = 'cache/map/treasury-rates-of-exchange.json';
if (!existsSync(treasuryFile)) {
  const url = 'https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/od/rates_of_exchange?filter=record_date:gte:2026-01-01&sort=-record_date&page%5Bsize%5D=10000';
  await writeFile(treasuryFile, await (await fetch(url)).text());
}
const englishCountryNames = new Intl.DisplayNames(['en'], { type: 'region' }), countryCodeByName = new Map<string, string>();
for (const code of Object.keys(countryToCurrency as Record<string, string>)) {
  const name = englishCountryNames.of(code);
  if (name) countryCodeByName.set(name.toLowerCase(), code);
}
const treasuryCountryNames: Record<string, string> = { 'korea': 'KR', 'turkey': 'TR', 'russia': 'RU', 'vietnam': 'VN', 'taiwan': 'TW', 'czech republic': 'CZ', 'bosnia': 'BA', 'cote d\'ivoire': 'CI', 'democratic republic of congo': 'CD', 'congo': 'CG', 'burma': 'MM', 'cape verde': 'CV', 'macedonia': 'MK', 'north macedonia': 'MK', 'laos': 'LA', 'brunei': 'BN', 'iran': 'IR', 'syria': 'SY', 'tanzania': 'TZ', 'bolivia': 'BO', 'venezuela': 'VE', 'moldova': 'MD', 'micronesia': 'FM', 'swaziland': 'SZ', 'eswatini': 'SZ', 'east timor': 'TL', 'timor-leste': 'TL', 'hong kong': 'HK', 'macao': 'MO', 'antigua & barbuda': 'AG', 'trinidad & tobago': 'TT', 'sao tome & principe': 'ST', 'st. lucia': 'LC' };
const treasury = JSON.parse(await readFile(treasuryFile, 'utf8')).data as { country: string; exchange_rate: string; record_date: string }[];
for (const row of treasury) {
  const name = row.country.toLowerCase(), countryCode = treasuryCountryNames[name] ?? countryCodeByName.get(name);
  const currency = countryCode && (countryToCurrency as Record<string, string>)[countryCode];
  if (currency && Number(row.exchange_rate) > 0) standInRate(currency, Number(row.exchange_rate), 'us-treasury-rates-of-exchange', row.record_date);
}

// Sources: the shared table, plus the stand-ins' own.
const sources: Record<string, Source> = {};
for (const row of await readCsv('data/sources.csv')) sources[row.source_id] = { publisher: row.publisher, title: row.title, url: row.url, licence: row.licence, period: row.period };
const standInSources: Record<string, Source> = {
  [palomboSourceId]: { publisher: 'Alessandro Palombo', title: 'Where a million still makes you rich (stand-in until our own figure lands)', url: 'https://x.com/thealepalombo/status/2122717540392865934', licence: 'quoted', period: '2026' },
  'ecb-reference-rates': { publisher: 'European Central Bank', title: 'Euro foreign exchange reference rates', url: 'https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html', licence: 'free reuse with attribution', period: ecbDate },
  'us-treasury-rates-of-exchange': { publisher: 'US Treasury, Bureau of the Fiscal Service', title: 'Treasury Reporting Rates of Exchange', url: 'https://fiscaldata.treasury.gov/datasets/treasury-reporting-rates-exchange/', licence: 'public domain', period: '2026' },
  'currency-pegs': { publisher: 'Central banks', title: 'Fixed exchange rates against the dollar or the euro', url: '', licence: '', period: '2026' },
};
for (const [id, source] of Object.entries(standInSources)) sources[id] ??= source;
for (const component of components) for (const figure of Object.values(figures[component])) if (!sources[figure.sourceId]) problems.push(`no source ${figure.sourceId} in data/sources.csv`);

// Each country's currency, for its own money beside the dollars.
const currencyOfCountry: Record<string, string> = {};
for (const [code, [, parent]] of Object.entries(places)) {
  if (parent !== null) continue;
  const currency = (countryToCurrency as Record<string, string>)[code === 'XK' ? 'XK' : code] ?? (code === 'PS' ? 'ILS' : undefined);
  if (currency) currencyOfCountry[code] = currency;
}
currencyOfCountry.HR = 'EUR'; currencyOfCountry.BG = 'EUR';

// Names of the cities figures were measured for, where the map's own city list lacks them.
const mapCities = new Set((JSON.parse(await readFile('assets/map/cities.json', 'utf8')) as [number][]).map(city => city[0]));
const wantedCityIds = new Set<number>();
for (const component of components) for (const figure of [...Object.values(figures[component]), ...Object.values(standIns[component])]) {
  const id = figure.measuredFor.match(/^CITY-(\d+)$/)?.[1];
  if (id && !mapCities.has(Number(id))) wantedCityIds.add(Number(id));
}
const cityNames: Record<string, string> = {};
for (const file of ['cache/geonames/cities1000.txt', 'cache/map/cities15000.txt']) {
  if (!wantedCityIds.size || !existsSync(file)) continue;
  for (const line of (await readFile(file, 'utf8')).split('\n')) {
    const [id, name] = line.split('\t');
    if (wantedCityIds.has(Number(id))) { cityNames[`CITY-${id}`] = name; wantedCityIds.delete(Number(id)); }
  }
}
if (wantedCityIds.size) problems.push(`no name for cities ${[...wantedCityIds].join(' ')}`);

const snapshot: Snapshot = { builtOn: new Date().toISOString().slice(0, 10), lifestyle, figures, standIns, taxStandIns, exchangeRates, currencyOfCountry, sources, cityNames };
await writeFile('data/snapshot.json', JSON.stringify(snapshot));
console.log(components.map(component => `${component}: ${Object.keys(figures[component]).length} places`).join(', '));
console.log(`${Object.keys(exchangeRates).length} exchange rates (${Object.values(exchangeRates).filter(rate => rate.isStandIn).length} stand-ins), ${Object.keys(standIns.rent).length} countries with Palombo stand-ins`);
if (problems.length) console.log(`${problems.length} problems:\n${[...new Set(problems)].slice(0, 40).join('\n')}`);
