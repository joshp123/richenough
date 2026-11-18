// The About page: how a figure is worked out, and every source with what it covers, its licence and a link. It is the only page
// that names publishers; a place's details say only where each figure was measured and what kind of source it is.
import { taxRegimes } from './capital.ts';
import { formatWhole } from './money.ts';
import { chainOf, countryInSentence, countryOf, nameOf, type Places } from './places.ts';
import { components, type Component, type Source } from './snapshot.ts';
import { taxRulesFor, type TaxRules } from './tax/tax-rules.ts';
import { madeBy, siteTitle } from './words.ts';

type Topic = Component | 'tax' | 'exchange' | 'map';
const topics: [Topic, string][] = [
  ['rent', 'Rent'], ['everyday', 'Everyday spending'], ['car', 'The car'], ['housekeeper', 'The housekeeper'], ['health', 'Health cover'],
  ['tax', 'Tax'], ['exchange', 'Exchange rates'], ['map', 'The map, its places and its font'],
];

// The sources no figure names directly were read to build or check the figures; their identifiers say what for.
function topicOfBackground(sourceId: string): Topic {
  if (/^(hh|dw)-|^hk-(fr|it)-|wage|^ilostat|^boe-smi/.test(sourceId)) return 'housekeeper';
  if (/^(health|care|img|hk-vhis|my-aia|sg-aia|th-chubb|za-bonitas|au-medicare|ca-provincial|cl-fonasa|co-salud|cr-ccss|ir-health|nz-health|pe-essalud|tw-nhi|us-aca)-|^care-|-(nhis|nfz|ssn|ccss)-/.test(sourceId)) return 'health';
  if (/^(road-tax|us-car|car|adac|acea)-|^autokostencheck$|fuel|petrol|oil-bulletin|vehicle/.test(sourceId)) return 'car';
  if (/^tax-/.test(sourceId)) return 'tax';
  if (/exchange|^imf-er$|treasury|^ecb-|^currency-pegs$|^bcc-/.test(sourceId)) return 'exchange';
  if (/^(us-geography|us-cbsa|us-census-places|us-zcta-county|insee-cog-2025|istat-it-comuni|nomis-la-population|nz-statsnz-geographies-2018|geo-api-gouv)$/.test(sourceId)) return 'map';
  if (/cpi$|hicp|colc-ext/.test(sourceId)) return 'everyday';
  return 'rent';
}

// The map's shapes, places, flags and typeface come from files the tools in tools/map and tools/build-*.ts download, not from tables.
const mapSources: (Source & { covers: string })[] = [
  { publisher: 'Natural Earth', title: 'Admin 0 countries and admin 1 states and provinces, 1:10 million', url: 'https://www.naturalearthdata.com/', licence: 'Public domain', period: '', covers: 'Borders outside the US and Europe' },
  { publisher: 'US Census Bureau', title: 'Cartographic boundary files 2024: counties, 1:5 million', url: 'https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.html', licence: 'Public domain', period: '2024', covers: 'US counties' },
  { publisher: 'Eurostat, GISCO', title: 'NUTS 2024 regions, level 3, 1:3 million', url: 'https://ec.europa.eu/eurostat/web/gisco/geodata/statistical-units/territorial-units-statistics', licence: '© EuroGeographics for the administrative boundaries; free reuse with attribution', period: '2024', covers: 'Regions of Europe' },
  { publisher: 'Office for National Statistics', title: 'International Territorial Level 3 (January 2025) boundaries, generalised', url: 'https://geoportal.statistics.gov.uk/', licence: 'Open Government Licence v3.0', period: '2025', covers: 'Regions of the UK' },
  { publisher: 'GeoNames', title: 'Cities of 15,000 people or more (cities15000)', url: 'https://www.geonames.org/', licence: 'CC BY 4.0', period: '2026', covers: 'Cities and their names' },
  { publisher: 'PalQuest, Institute for Palestine Studies', title: 'Places in Palestine', url: 'https://www.palquest.org/en/placesabout', licence: 'Free to read, no licence stated', period: '', covers: 'Arabic names of places in Palestine' },
  { publisher: 'flag-icons', title: 'Country flags as SVG files', url: 'https://github.com/lipis/flag-icons', licence: 'MIT', period: '', covers: 'Country flags' },
  { publisher: 'Wikimedia Commons', title: 'Flags of US states and Canadian provinces and territories', url: 'https://commons.wikimedia.org/', licence: 'Public domain or free use, as each file’s page states', period: '', covers: 'State and province flags' },
  { publisher: 'Omnibus-Type', title: 'Archivo', url: 'https://github.com/Omnibus-Type/Archivo', licence: 'SIL Open Font License 1.1', period: '', covers: 'The font' },
];

const escapeHtml = (text: string) => text.replace(/[<>&"]/g, character => ({ '<': '&lt;', '>': '&gt;', '&': '&amp;', '"': '&quot;' })[character]!);
const sentenceStart = (text: string) => (text ? text[0].toUpperCase() + text.slice(1) : 'No licence stated');
const listWords = (words: string[]) => (words.length < 2 ? words.join('') : `${words.slice(0, -1).join(', ')} and ${words.at(-1)}`);

// Which places each source gives a figure for, by topic: source → topic → country → the places.
type Uses = Map<string, Map<Topic, Map<string, Set<string>>>>;
function usesOf(places: Places): Uses {
  const uses: Uses = new Map();
  const note = (sourceId: string, topic: Topic, country: string, code: string) => {
    // Rows for cities the map does not show give no place a figure.
    if (topic !== 'exchange' && places.rows[country]?.[2] !== 'country') return;
    if (!uses.has(sourceId)) uses.set(sourceId, new Map());
    const byTopic = uses.get(sourceId)!;
    if (!byTopic.has(topic)) byTopic.set(topic, new Map());
    const byCountry = byTopic.get(topic)!;
    if (!byCountry.has(country)) byCountry.set(country, new Set());
    byCountry.get(country)!.add(code);
  };
  const { snapshot } = places;
  for (const component of components) {
    for (const [code, figure] of Object.entries(snapshot.figures[component])) note(figure.sourceId, component, countryOf(places, code), code);
    for (const [country, figure] of Object.entries(snapshot.standIns[component])) note(figure.sourceId, component, country, country);
  }
  note(snapshot.lifestyle.sourceIds.everyday, 'everyday', 'US', 'US');
  for (const [currency, rate] of Object.entries(snapshot.exchangeRates)) note(rate.sourceId, 'exchange', currency, currency);
  // Each set of tax rules names its sources; a year at any amounts brings them out.
  const countriesOfRules = new Map<TaxRules, Set<string>>();
  for (const code of Object.keys(places.rows)) {
    const rules = taxRulesFor(chainOf(places, code));
    if (!rules) continue;
    if (!countriesOfRules.has(rules)) countriesOfRules.set(rules, new Set());
    countriesOfRules.get(rules)!.add(countryOf(places, code));
  }
  for (const [rules, countries] of countriesOfRules) for (const regime of taxRegimes) {
    for (const sourceId of rules.taxOwed({ withdrawalLocal: 50_000, capitalAtStartOfYearLocal: 1_000_000 }, regime).sourceIds) {
      for (const country of countries) note(sourceId, 'tax', country, country);
    }
  }
  return uses;
}

// What a source gives figures for, in a few words: "26 places in Portugal", "Lisbon", "Spain, Italy and 30 more countries".
function coversWords(places: Places, topic: Topic, byCountry: Map<string, Set<string>>): string {
  const countries = [...byCountry.keys()];
  if (topic === 'exchange') return countries.length === 1 ? `The ${countries[0]} rate` : `Rates for ${countries.length} currencies`;
  const countryNames = countries.map(country => countryInSentence(places, country)).sort((a, b) => a.replace(/^the /, '').localeCompare(b.replace(/^the /, ''), 'en'));
  const some = countryNames.length > 3 ? `${countryNames.slice(0, 2).join(', ')} and ${countryNames.length - 2} more countries` : listWords(countryNames);
  if (topic === 'tax') return some;
  const codes = [...byCountry.values()].flatMap(set => [...set]);
  if (codes.length === 1) return nameOf(places, codes[0]);
  return `${codes.length.toLocaleString('en-GB')} places in ${some}`;
}

// A licence as its publisher states it, to the end of its first sentence; the data agents' further notes stay in data/sources.csv.
const licenceWords = (licence: string) => sentenceStart(licence.split(/(?<=[a-z)]\.)\s/)[0]);
function sourceItem(source: Source, covers: string): string {
  const title = source.url ? `<a href="${escapeHtml(source.url)}">${escapeHtml(source.title)}</a>` : escapeHtml(source.title);
  const facts = [source.publisher, covers, licenceWords(source.licence), source.period].filter(Boolean).map(escapeHtml).join(' · ');
  return `<li>${title}<small>${facts}</small></li>`;
}

export function aboutPage(places: Places, stylesPath: string): string {
  const { snapshot } = places, { lifestyle } = snapshot, uses = usesOf(places);
  const usd = (amount: number) => formatWhole(amount, 'USD');
  const severalCountries = 'Several countries';
  const groups = topics.map(([topic, heading]) => {
    // Each topic's sources by the country they cover, those covering several first, so a visitor can find a country's sources.
    const byGroup = new Map<string, Source[]>(), coversOf = new Map<Source, string>();
    for (const [sourceId, byTopic] of uses) {
      const byCountry = byTopic.get(topic), source = snapshot.sources[sourceId];
      if (!byCountry || !source) continue;
      const group = topic === 'exchange' || byCountry.size > 1 ? severalCountries : nameOf(places, [...byCountry.keys()][0]);
      if (!byGroup.has(group)) byGroup.set(group, []);
      byGroup.get(group)!.push(source);
      coversOf.set(source, coversWords(places, topic, byCountry));
    }
    const groupNames = [...byGroup.keys()].sort((a, b) => (a === severalCountries ? -1 : b === severalCountries ? 1 : a.localeCompare(b, 'en')));
    const sections = groupNames.map(group => `${topic === 'exchange' ? '' : `<h4>${escapeHtml(group)}</h4>`}<ul>${byGroup.get(group)!.sort((a, b) => a.title.localeCompare(b.title, 'en')).map(source => sourceItem(source, coversOf.get(source)!)).join('')}</ul>`);
    if (topic === 'map') sections.push(`<ul>${mapSources.map(source => sourceItem(source, source.covers)).join('')}</ul>`);
    const background = Object.keys(snapshot.sources).filter(sourceId => !uses.has(sourceId) && topicOfBackground(sourceId) === topic)
      .sort((a, b) => snapshot.sources[a].title.localeCompare(snapshot.sources[b].title, 'en'));
    if (background.length) sections.push(`<h4>Also read to build or check these figures</h4><ul>${background.map(sourceId => sourceItem(snapshot.sources[sourceId], '')).join('')}</ul>`);
    const count = [...byGroup.values()].reduce((sum, sources) => sum + sources.length, 0) + (topic === 'map' ? mapSources.length : 0) + background.length;
    if (!count) return '';
    return `<details id="sources-${topic}"><summary><span>${heading}</span><small>${count.toLocaleString('en-GB')} ${count === 1 ? 'source' : 'sources'}</small></summary>${sections.join('')}</details>`;
  }).join('');
  const palombo = snapshot.sources['palombo-2026-11-17'];

  return `<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="color-scheme" content="light dark">
<title>About these figures · ${escapeHtml(siteTitle)}</title>
<meta name="description" content="How ${escapeHtml(siteTitle)} works out what a couple needs invested to live well for life, after tax, and every source behind it.">
<link rel="stylesheet" href="${stylesPath}">
</head>
<body class="about">
<main class="about-page">
<p class="about-home"><a href="/">${escapeHtml(siteTitle)}</a></p>
<h1>About these figures</h1>
<p class="about-lead">Each place on the map is coloured by the money a couple needs invested to live well there for the rest of their lives. Each year they sell a little of their investments, pay the place’s tax on what they sell, and live on the rest.</p>

<h2>The lifestyle</h2>
<p>Every place gets the same life for two people:</p>
<ul class="about-list">
<li>a rented two-bedroom flat in the main town of the region;</li>
<li>everyday spending of ${usd(lifestyle.everydayUsDollarsPerMonth)} a month at US prices, raised or lowered by each place’s price level. That is what American households in the top fifth by income spend on food, eating out, bills, clothes, furniture, outings and personal care, scaled to two people;</li>
<li>one car, a Toyota Corolla hybrid bought new for cash, kept for 8 years and driven 12,000 km a year: what it loses in value, its insurance, fuel, servicing and road tax;</li>
<li>a housekeeper ${lifestyle.housekeeperHoursPerWeek} hours a week, at the local hourly rate;</li>
<li>health cover for two people aged 45;</li>
<li>three week-long trips a year, ${usd(lifestyle.tripsUsDollarsPerYear)} in all, the same everywhere, because flights and hotels abroad do not follow local prices.</li>
</ul>
<p>The housekeeper’s hours and the trips are our own choice. Everything else is priced in each place.</p>

<h2>Selling 5% a year</h2>
<p>The couple’s money is in a fund that holds shares from all over the world. Each year they sell 5% of it. The figure for a place is the smallest sum at which that 5%, less the place’s tax, pays for the year. We use 5% because Alessandro Palombo did, so his figures and ours can be compared. The 4% often quoted for a 30-year retirement would make every figure about a quarter larger.</p>

<h2>Tax</h2>
<p>Each country’s tax is worked out from its own rules, and a state’s or region’s where it has its own, for a couple who live off their investments and have no other income. Most countries tax what the couple sell, often only the gain in it. Some tax the money they hold each year instead, or as well, whatever they sell: the Netherlands taxes a return it assumes the money makes, Denmark taxes each year’s rise in the fund, and Switzerland, Spain and Norway tax wealth. A place’s details say which: a share of what you sell, or a share of your money each year. Some countries give newcomers a tax break for ten years or more; the newcomer tax break switch shows the figures with it.</p>

<h2>How local each number is</h2>
<p>Each cost comes from the most local source we found: the place itself, or else the region, state or country it is in. Under each cost, a place’s details say where the figure was measured and what kind of source it is: official statistics, rental listings, property market reports, press reports, insurers’ prices, cleaners’ going rates, or our model. Our model means no one publishes the figure, so we worked it out from figures that are published, such as a country’s price level or income. The car is always our model: we add up its costs from published prices.</p>
<p>The map is as fine as the figures: counties in the US, regions in Europe and in 10 other countries, and whole countries elsewhere. A few places still use Palombo’s own figure for a cost until we find a better one; their details mark it as a stand-in.</p>

<h2>Where the idea comes from</h2>
<p>${palombo ? `<a href="${escapeHtml(palombo.url)}">Alessandro Palombo’s post “Where a million still makes you rich”</a>` : 'Alessandro Palombo’s post “Where a million still makes you rich”'} mapped what a couple needs in 32 cities. His map cites Livingcost, whose prices come partly from its visitors. Working back from his figures, he used a three-bedroom flat in the city centre for the rent, one amount of about $2,000 a month for the car, help, health cover and trips in every city, and one tax rate for each country. We price a two-bedroom flat in the main town from official statistics and listings, price the car, the housekeeper and the health cover in each place, and use each country’s tax rules.</p>

<h2 id="sources">Sources</h2>
<p>These are all the sources behind the figures, by what they price. Each licence is as its publisher states it.</p>
<div class="about-sources">${groups}</div>

<p class="about-credit">${escapeHtml(madeBy[0].toUpperCase() + madeBy.slice(1))}. Figures as of ${new Date(`${snapshot.builtOn}T12:00:00Z`).toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC' })}. <a href="https://github.com/joshp123/richenough">The site’s code</a> is free to reuse under the MIT licence.</p>
</main>
</body>
</html>`;
}
