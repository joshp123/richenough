// The line under each cost in a place's details: where the figure was measured and what kind of source it is ("Lisbon · official
// statistics", "Bangkok · rental listings", "Portugal · our model"). Publishers are named on the About page only.
import type { Cost } from './capital.ts';
import { countryOf, nameOf, plainLetters, type Places } from './places.ts';

export type SourceKind = 'official statistics' | 'rental listings' | 'property market reports' | 'press reports' | 'insurers’ prices'
  | 'cleaners’ going rates' | 'our model';

const officialRents = new Set([
  'ade-it-locazioni', 'anil-carte-loyers-2025', 'au-nsw-rent-sales', 'au-qld-rta-median-rents', 'au-sa-private-rent', 'au-tas-bond-data',
  'bbsr-angebotsmieten-de', 'bcrp-pe-inmobiliario', 'bfs-mietpreise', 'ca-cmhc-rms-2025', 'cso-rtb-riq02', 'cy-moi-indicative-rents',
  'cz-mf-cenova-mapa', 'dubai-pulse-ejari', 'es-aeat-irpf-viviendas', 'es-emal', 'es-gva-fianzas', 'es-incasol', 'es-navarra-observatorio',
  'eurostat-colc-rents', 'hk-rvd-avg-rents-by-class', 'hr-eiz-ptn2025', 'hu-ksh-ingatlan-rent', 'idecba-alquileres', 'il-cbs-rent',
  'ine-pt-rendas', 'is-hms-via-reykjavik', 'jp-estat-retail-price-survey-rent', 'kr-molit-rtms-2026', 'li-etab-mietpreise',
  'lu-observatoire-loyers', 'mn-nso-rent-2026-08', 'mo-dsec-rental-2026q3', 'mt-housing-authority-rents', 'nz-mbie-bonds-2026',
  'oime-medellin', 'ons-pipr', 'ru-rosstat-avg-prices', 'scb-se-hyror', 'sg-ura-rentals-nonlanded', 'si-gurs-najemni-trg-2017',
  'ssb-no-leiemarked', 'statfi-fi-vuokrat', 'tcmb-ykke', 'tw-moi-lvr-rentals', 'us-acs-rent',
]);
const rentReports = new Set([
  'ae-engelvoelkers-adrec', 'aguila-cl-arriendos', 'au-vic-reiv', 'au-wa-reiwa', 'ba-globalpropertyguide', 'be-cib-huurbarometer',
  'be-federia-barometre', 'cn-cric-creis-2026-10', 'ge-galt-taggart', 'ge-tbc-capital', 'id-cushman-jakarta', 'jp-reins-rental-2026q3',
  'md-accesimobil', 'sa-kite', 'sk-deloitte-rent-index',
]);
const rentPress = new Set([
  'africanvestor-rents', 'au-senegal-dakar-loyers', 'aruodas-lt-lrt', 'bt-thimphu-rent', 'duashpi-al-balkanweb-2026', 'fortren-african-cities-2026', 'gr-spitogatos-students', 'kg-24kg',
  'my-iqi-kl-rent', 'ua-lun-dengi', 'uz-kvadro',
]);
const officialWages = new Set(['eurostat-minimum-wages', 'eurostat-ses22-hourly-occupation', 'ons-ashe-2026-cleaners', 'urssaf-particuliers-employeurs-2025', 'us-bls-oews', 'ilostat-earnings-isic-t']);

// A figure the data agents estimated rather than found measured says so in its note or in what it was measured for.
const isModelled = (cost: Cost) => /^Inferred\b|\bnot measured\b|publishes no figure/i.test(cost.figure!.note) || /\bestimated\b/i.test(cost.figure!.measuredFor);

export function sourceKind(cost: Cost): SourceKind {
  const sourceId = cost.figure!.sourceId;
  if (cost.part === 'car' || isModelled(cost)) return 'our model';
  if (cost.part === 'health') return 'insurers’ prices';
  if (cost.part === 'housekeeper') return officialWages.has(sourceId) ? 'official statistics' : 'cleaners’ going rates';
  if (cost.part === 'rent') {
    if (officialRents.has(sourceId)) return 'official statistics';
    if (rentReports.has(sourceId)) return 'property market reports';
    if (rentPress.has(sourceId)) return 'press reports';
    return 'rental listings';
  }
  return 'official statistics';
}

const placeCode = /^(CITY-\d+|US-[A-Z0-9]+|NUTS-[A-Z0-9]+|[A-Z]{2}(-[A-Z0-9]{1,3})?)$/;
// Every city's and region's name, by country, so words such as "Mumbai, two-bedroom apartments" can be read as a place.
const namesByCountry = new WeakMap<Places, Map<string, string>>();
function placeNamed(places: Places, words: string, country: string): string | null {
  if (!namesByCountry.has(places)) {
    const names = new Map<string, string>();
    const add = (name: string, code: string) => { const key = `${countryOf(places, code)}|${plainLetters(name).toLowerCase()}`; if (!names.has(key)) names.set(key, nameOf(places, code)); };
    for (const city of places.cities) add(city.name, city.code);
    for (const [code, [name]] of Object.entries(places.rows)) add(name, code);
    for (const city of places.cities) for (const other of city.otherNames) add(other, city.code);
    namesByCountry.set(places, names);
  }
  return namesByCountry.get(places)!.get(`${country}|${plainLetters(words).toLowerCase()}`) ?? null;
}
// Where the figure was measured: the place it names, or the place its words begin with, or else the place it is filed under. Only
// ever a place's name, never a publisher's.
export function sourcePlace(places: Places, cost: Cost): string {
  const { measuredFor } = cost.figure!, rowCode = cost.rowCode!;
  if (placeCode.test(measuredFor)) { const named = nameOf(places, measuredFor); if (named !== measuredFor) return named; }
  return placeNamed(places, measuredFor.split(/[,(:;]/)[0].trim(), countryOf(places, rowCode)) ?? nameOf(places, rowCode);
}
