// The page: the map, the bar over it, the four cells along the bottom, a place's details, the place list and sharing, in two
// modes: "How much you need" (what each place needs, the same for everyone) and "Am I gonna make it?" (the visitor's money
// against each place).
import 'every-tax-rule';
import { withdrawalRates, type PlaceFigure, type Settings } from '../src/capital.ts';
import { fillOf, noFigureColour, stepColours, stepEnds } from '../src/colours.ts';
import { linkQuery, linkStateOf, type LinkState } from '../src/link.ts';
import { readMapGeometry } from '../src/map-geometry.ts';
import { currencyName, formatCapital, formatDifference, formatRounded, formatShort, formatWhole, widelyHeldCurrencies } from '../src/money.ts';
import { chainOf, contextOf, countryInSentence, countryOf, createPlaces, nameOf, plainLetters, type CityRow, type PlaceRows } from '../src/places.ts';
import { sourceKind, sourcePlace } from '../src/source-lines.ts';
import { taxWords } from '../src/tax-words.ts';
import { projectPoint } from '../src/projection.ts';
import type { Snapshot } from '../src/snapshot.ts';
import { clampHave, haveAtSliderPosition, sliderPositionOfHave, twoFigures, verdictFill, verdictInk as verdictInkOnLight, verdictInkOnDark, verdictOf, verdictSide, type Mode, type VerdictWord } from '../src/verdict.ts';
import { siteSubtitle, siteTitle } from '../src/words.ts';
import { worldFigures, type WorldFigures } from '../src/world-figures.ts';
import { flagCanvas, flagHtml } from './flags.ts';
import { createMapView, type MapLabel } from './map-view.ts';

// Filled in by hosting/build.mjs: where each data file is served, at an address that changes when the file does.
declare const DATA_PATHS: { coarseShapes: string; fineShapes: string; places: string; cities: string; snapshot: string };

const escapeHtml = (text: string) => text.replace(/[&<>"]/g, character => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[character]!);
const element = <T extends HTMLElement = HTMLElement>(id: string) => document.getElementById(id) as T;
const isPhone = () => matchMedia('(max-width: 720px)').matches;

const [coarseBytes, placeRows, cityRows, snapshot, whereAmI] = await Promise.all([
  fetch(DATA_PATHS.coarseShapes).then(response => response.arrayBuffer()),
  fetch(DATA_PATHS.places).then(response => response.json() as Promise<PlaceRows>),
  fetch(DATA_PATHS.cities).then(response => response.json() as Promise<CityRow[]>),
  fetch(DATA_PATHS.snapshot).then(response => response.json() as Promise<Snapshot>),
  fetch('/api/whereami').then(response => (response.ok ? response.json() : null)).catch(() => null) as Promise<{ country?: string; latitude?: number; longitude?: number } | null>,
]);
const places = createPlaces(placeRows, cityRows, snapshot);
let geometry = readMapGeometry(new Uint8Array(coarseBytes));
const state: LinkState = linkStateOf(places, new URL(location.href));
document.title = siteTitle;
element('site-title').textContent = siteTitle;
element('site-subtitle').textContent = siteSubtitle;

// ---- Figures, worked out once for each choice of settings.
const figuresBySettings = new Map<string, WorldFigures>();
function figures(settings: Settings = state.settings): WorldFigures {
  const key = `${settings.withdrawalRate}|${settings.regime}`;
  if (!figuresBySettings.has(key)) figuresBySettings.set(key, worldFigures(places, geometry.shapeCodes, settings));
  return figuresBySettings.get(key)!;
}
const needOf = (code: string, settings: Settings = state.settings): number | null => {
  const figure = figures(settings).figureOf(code);
  return figure.kind === 'figure' ? figure.capitalUsDollars : null;
};

// ---- Money: everything in the chosen currency (dollars unless the visitor picks another), the visitor's own in brackets.
const visitorCountry = whereAmI?.country?.toUpperCase() ?? null;
const visitorCurrency = (visitorCountry && snapshot.currencyOfCountry[visitorCountry]) || 'USD';
const mainCurrency = () => state.currency ?? 'USD';
const perUsDollar = (currency: string) => (currency === 'USD' ? 1 : snapshot.exchangeRates[currency]?.perUsDollar ?? NaN);
const secondCurrency = () => (visitorCurrency !== mainCurrency() ? visitorCurrency : mainCurrency() !== 'USD' ? 'USD' : null);
const money = (usDollars: number) => formatCapital(usDollars * perUsDollar(mainCurrency()), mainCurrency());
// What the visitor would have short or to spare in a place, in words: "$2.1M short", "$0.3M to spare".
const differenceWords = (needUsDollars: number) => `${formatDifference((haveUsDollars() - needUsDollars) * perUsDollar(mainCurrency()), mainCurrency())} ${verdictSide(verdict(needUsDollars))}`;
// A sum in the chosen currency to two significant figures: $95,000, $2,300.
const roundedMoney = (usDollars: number) => formatRounded(usDollars * perUsDollar(mainCurrency()), mainCurrency());
function secondMoney(usDollars: number): string | null {
  const currency = secondCurrency();
  return currency && Number.isFinite(perUsDollar(currency)) ? formatCapital(usDollars * perUsDollar(currency), currency) : null;
}
const haveUsDollars = () => state.have / perUsDollar(mainCurrency());
const verdict = (needUsDollars: number): VerdictWord => verdictOf(needUsDollars, haveUsDollars());
// Places with no figure take the page's own grey, darker in dark mode.
const noFigureOnPage = () => getComputedStyle(document.documentElement).getPropertyValue('--no-figure').trim() || noFigureColour;
const fill = (needUsDollars: number | null) => fillOf(state.mode, needUsDollars, haveUsDollars(), noFigureOnPage());
const isDark = () => matchMedia('(prefers-color-scheme: dark)').matches;
const verdictInk = new Proxy({} as Record<VerdictWord, string>, { get: (_, word: VerdictWord) => (isDark() ? verdictInkOnDark : verdictInkOnLight)[word] });
const verdictWord = (word: VerdictWord) => `<b style="color:${verdictInk[word]}">${word}</b>`;

// ---- The visitor's place: from the link, else from where the request came from.
const homeCityOfTimeZone: Record<string, string> = {
  'America/Los_Angeles': 'Los Angeles', 'America/Denver': 'Denver', 'America/Phoenix': 'Phoenix', 'America/Chicago': 'Chicago', 'America/New_York': 'New York City',
  'America/Anchorage': 'Anchorage', 'Pacific/Honolulu': 'Honolulu', 'America/Toronto': 'Toronto', 'America/Vancouver': 'Vancouver', 'America/Edmonton': 'Calgary',
  'Australia/Sydney': 'Sydney', 'Australia/Melbourne': 'Melbourne', 'Australia/Perth': 'Perth', 'Australia/Brisbane': 'Brisbane',
};
function guessVisitorPlace(): string | null {
  if (!whereAmI) return null;
  if (Number.isFinite(whereAmI.latitude) && Number.isFinite(whereAmI.longitude)) {
    const nearest = places.cities.reduce<{ code: string | null; distance: number }>((best, city) => {
      const distance = Math.hypot(city.latitude - whereAmI.latitude!, (city.longitude - whereAmI.longitude!) * Math.cos(city.latitude * Math.PI / 180));
      return distance < best.distance ? { code: city.code, distance } : best;
    }, { code: null, distance: 0.5 });
    if (nearest.code) return nearest.code;
  }
  if (!visitorCountry) return null;
  const inCountry = places.cities.filter(city => countryOf(places, city.code) === visitorCountry);
  const timeZoneCity = homeCityOfTimeZone[Intl.DateTimeFormat().resolvedOptions().timeZone];
  return (inCountry.find(city => city.name === timeZoneCity) ?? inCountry.find(city => city.isCapital) ?? inCountry[0])?.code ?? null;
}
if (!state.visitor) state.visitor = guessVisitorPlace();

// ---- The map.
const tooltip = element('tooltip');
const mapView = createMapView(element('map'), {
  placeAt(_x, _y, shape, labelCode) { openPlace(labelCode ?? (shape >= 0 ? geometry.shapeCodes[shape] : null), false); },
  moved() { tooltip.hidden = true; },
  hovered(shape, labelCode, clientX, clientY) {
    const code = labelCode ? null : shape >= 0 ? geometry.shapeCodes[shape] : null;
    if (!code) { tooltip.hidden = true; return; }
    const need = needOf(code);
    const verdictPart = need !== null && state.mode === 'have' ? ` · ${verdictWord(verdict(need))}, ${differenceWords(need)}` : '';
    tooltip.innerHTML = `${escapeHtml(nameOf(places, code))} <b>${need === null ? figureWords(figures().figureOf(code)) : money(need)}</b>${verdictPart}`;
    tooltip.hidden = false;
    tooltip.style.transform = `translate(${Math.min(clientX + 14, innerWidth - tooltip.offsetWidth - 8)}px, ${clientY + 16}px)`;
  },
});
mapView.setGeometry(geometry, 'coarse');

// The map's sea and lines follow the page's light or dark colours.
function themeTheMap(): void {
  const fractions = (variable: string) => {
    const hex = getComputedStyle(document.documentElement).getPropertyValue(variable).trim().slice(1, 7);
    return [0, 2, 4].map(start => parseInt(hex.slice(start, start + 2), 16) / 255) as [number, number, number];
  };
  const isDark = matchMedia('(prefers-color-scheme: dark)').matches;
  mapView.setTheme({ sea: fractions('--sea'), line: isDark ? fractions('--sea') : [1, 1, 1], ink: fractions('--ink'), isDark });
}
themeTheMap();


function colourTheMap(): void {
  const { shapeCapital } = figures(), bytes = new Uint8Array(shapeCapital.length * 4);
  shapeCapital.forEach((need, shape) => {
    const hex = fill(Number.isNaN(need) ? null : need);
    bytes.set([parseInt(hex.slice(1, 3), 16), parseInt(hex.slice(3, 5), 16), parseInt(hex.slice(5, 7), 16), 255], shape * 4);
  });
  mapView.setShapeColours(bytes);
}

// City labels: every city with a figure, the biggest first; capitals count as twice their size.
let labels: MapLabel[] = [];
function labelTheCities(): void {
  const { cityCapital } = figures(), previous = new Map(labels.map(label => [label.code, label]));
  // Every city with a figure, and the visitor's and compared city even without one, so home always has its pin.
  const named = new Set([state.visitor, state.compared].filter(Boolean) as string[]);
  labels = places.cities.filter(city => cityCapital.has(city.code) || named.has(city.code)).map(city => {
    const [x, y] = projectPoint(city.longitude, city.latitude), need = cityCapital.get(city.code) ?? null;
    return {
      code: city.code, x, y, name: city.name, amount: need === null ? '' : money(need),
      amountColours: state.mode === 'need' || need === null ? null : { onLight: verdictInkOnLight[verdict(need)], onDark: verdictInkOnDark[verdict(need)] },
      colour: fill(need), flag: previous.get(city.code)?.flag ?? null, fame: named.has(city.code) ? 0 : city.fame, population: city.population,
    };
  });
  mapView.setLabels(labels);
  for (const label of labels) {
    if (label.flag) continue;
    flagCanvas(places, label.code).then(canvas => { label.flag = canvas; mapView.redraw(); });
  }
}

// ---- The bar: the mode, the tax switch, and in the second mode what the visitor has.
const haveField = element<HTMLInputElement>('have-field'), haveSlider = element<HTMLInputElement>('have-slider');
function renderBar(): void {
  for (const button of document.querySelectorAll<HTMLButtonElement>('[data-mode]')) button.setAttribute('aria-pressed', String(button.dataset.mode === state.mode));
  for (const button of document.querySelectorAll<HTMLButtonElement>('[data-regime]')) button.setAttribute('aria-pressed', String(button.dataset.regime === state.settings.regime));
  element('rate').hidden = withdrawalRates.length < 2;
  element('rate').innerHTML = withdrawalRates.map(rate => `<button type="button" data-rate="${rate}" aria-pressed="${rate === state.settings.withdrawalRate}">${Math.round(rate * 100)}%</button>`).join('');
  element('currency-button').querySelector('span')!.textContent = mainCurrency();
  document.body.dataset.mode = state.mode;
  element('have').hidden = state.mode !== 'have';
  if (document.activeElement !== haveField) haveField.value = formatWhole(state.have, mainCurrency());
  const position = sliderPositionOfHave(state.have);
  haveSlider.value = String(position);
  haveSlider.style.setProperty('--filled', `${position * 100}%`);
  haveSlider.setAttribute('aria-valuetext', formatWhole(state.have, mainCurrency()));
}
haveSlider.addEventListener('input', () => { state.have = haveAtSliderPosition(Number(haveSlider.value)); update(); });
function commitHaveField(): void {
  const digits = Number(haveField.value.replace(/[^\d]/g, ''));
  if (digits > 0) state.have = clampHave(digits);
  haveField.value = formatWhole(state.have, mainCurrency());
  update();
}
haveField.addEventListener('keydown', event => { if (event.key === 'Enter') { commitHaveField(); haveField.blur(); } });
haveField.addEventListener('blur', commitHaveField);
document.addEventListener('click', event => {
  const target = (event.target as HTMLElement).closest<HTMLElement>('[data-regime],[data-rate],[data-mode]');
  if (!target) return;
  if (target.dataset.mode) state.mode = target.dataset.mode as Mode;
  if (target.dataset.regime) state.settings = { ...state.settings, regime: target.dataset.regime as Settings['regime'] };
  if (target.dataset.rate) state.settings = { ...state.settings, withdrawalRate: Number(target.dataset.rate) as Settings['withdrawalRate'] };
  update();
});

// ---- The currency menu: the visitor's own currency and the most widely held.
function closeMenus(): void { for (const menu of document.querySelectorAll<HTMLElement>('.menu')) menu.hidden = true; }
element('currency-button').addEventListener('click', event => {
  const menu = element('currency-menu'), wasHidden = menu.hidden;
  closeMenus();
  if (!wasHidden) return;
  const currencies = [...new Set(['USD', visitorCurrency, ...widelyHeldCurrencies])].filter(currency => Number.isFinite(perUsDollar(currency)));
  // A phone's bar has no room for the tax switch, so on a phone it is the last row of this menu.
  menu.innerHTML = currencies.map(currency => `<button type="button" role="menuitemradio" aria-checked="${currency === mainCurrency()}" data-currency="${currency}"><span>${escapeHtml(currencyName(currency))}</span><small>${currency}</small></button>`).join('')
    + `<div class="menu-tax segmented" role="group" aria-label="Tax">${(['standard', 'special'] as const).map(regime => `<button type="button" data-regime="${regime}" aria-pressed="${state.settings.regime === regime}">${regime === 'standard' ? 'Normal tax' : 'Newcomer tax break'}</button>`).join('')}</div>`;
  const box = (event.currentTarget as HTMLElement).getBoundingClientRect();
  menu.style.top = `${box.bottom + 6}px`;
  menu.style.left = `${Math.max(8, Math.min(innerWidth - 8 - 260, box.right - 260))}px`;
  menu.hidden = false;
});
element('currency-menu').addEventListener('click', event => {
  const button = (event.target as HTMLElement).closest<HTMLElement>('[data-currency]');
  if (!button) return;
  // What the visitor has stays the same sum of money in the new currency, to two figures: $1,000,000 becomes €860,000.
  const haveInDollars = haveUsDollars();
  state.currency = button.dataset.currency === 'USD' ? null : button.dataset.currency!;
  state.have = clampHave(twoFigures(haveInDollars * perUsDollar(mainCurrency())));
  closeMenus();
  update();
});
document.addEventListener('pointerdown', event => { if (!(event.target as HTMLElement).closest('.menu, #currency-button')) closeMenus(); });

// ---- The key: the dollar scale, or the three verdicts.
function renderKey(): void {
  // On a phone, whose bar has no tax switch, the key says when the tax break is on.
  const taxBreak = state.settings.regime === 'special' ? '<div class="key-tax">With the newcomer tax break</div>' : '';
  const about = '<a class="key-about" href="/about">About these figures</a>';
  if (state.mode === 'need') {
    element('key').innerHTML = `${taxBreak}<div class="key-title">$1M is enough</div>
      <div class="key-row"><div class="key-steps">${stepColours.map(colour => `<i style="background:${colour}"></i>`).join('')}</div>
      <span class="key-none"><i style="background:var(--no-figure)"></i>No figure</span></div>
      <div class="key-ticks">${stepEnds.map(end => `<span class="${end === 1e6 ? 'key-turn' : ''} ${[0.75e6, 1.25e6, 1.5e6, 2.5e6].includes(end) ? 'key-minor' : ''}">$${end / 1e6}M</span>`).join('')}</div>${about}`;
    return;
  }
  element('key').innerHTML = `${taxBreak}<div class="key-verdicts"><b class="key-have">With ${formatShort(state.have, mainCurrency())}</b>
    <span><i style="background:${verdictFill.WAGMI}"></i>${verdictWord('WAGMI')}<span class="key-words"> enough</span></span>
    <span><i style="background:${verdictFill.NGMI}"></i>${verdictWord('NGMI')}<span class="key-words"> not enough</span></span>
    <span class="key-none"><i style="background:var(--no-figure)"></i>No figure</span></div>${about}`;
}

// ---- The strip along the bottom.
function figureWords(figure: PlaceFigure): string {
  if (figure.kind === 'occupied') return 'Not known';
  if (figure.kind === 'missing') return 'No figure yet';
  return money(figure.capitalUsDollars);
}
type Cell = { role: string; shortRole: string; code: string | null; picker?: 'visitor' | 'compared'; emptyWords?: string };
// A cell of the strip: the role on top, the place's name on a line of its own across the whole cell (smaller, then on two lines,
// when it is long; never cut short), and what it needs on the line below, with the other currency beside it. In the second mode
// that line says what the visitor would have short or to spare, beside what the place needs.
function placeCell({ role, shortRole, code, picker, emptyWords = '' }: Cell): string {
  const need = code ? needOf(code) : null;
  const name = code ? escapeHtml(nameOf(places, code)) : emptyWords;
  const flag = code ? flagHtml(places, code) : '<span class="flag flag-empty"><svg viewBox="0 0 10 10"><path d="M5 1v8M1 5h8"/></svg></span>';
  const chevron = picker ? '<svg class="chevron" viewBox="0 0 10 6"><path d="M1 1l4 4 4-4"/></svg>' : '';
  const nameButton = `<button type="button" class="cell-name" ${picker ? `data-pick="${picker}"` : `data-open="${code}"`}>${flag}<span class="cell-name-words">${name}</span>${chevron}</button>`;
  let figure = '', roleWords = `<span class="long">${role}</span><span class="short">${shortRole}</span>`;
  if (code && need === null) figure = `<span class="cell-unknown">${figureWords(figures().figureOf(code))}</span>`;
  else if (code && need !== null && state.mode === 'need') {
    const second = secondMoney(need);
    figure = `<i style="background:${fill(need)}"></i><span class="cell-verb">needs</span><b>${money(need)}</b>${second ? `<small>(${second})</small>` : ''}`;
  } else if (code && need !== null) {
    // The verdict word stands before the amount, as on the share picture: "NGMI $2.4M short".
    const word = verdict(need), colour = verdictInk[word];
    const amount = formatDifference((haveUsDollars() - need) * perUsDollar(mainCurrency()), mainCurrency());
    figure = `<i style="background:${colour}"></i><b class="cell-word" style="color:${colour}">${word}</b><b style="color:${colour}">${amount}<span class="cell-side"> ${verdictSide(word)}</span></b><small>needs ${money(need)}</small>`;
  }
  return `<div class="cell"><div class="cell-role">${roleWords}</div>${nameButton}<div class="cell-figure">${figure}</div></div>`;
}
// How many countries have at least one place the visitor's money is enough for, out of the countries with a figure.
function wagmiCountries(): { wagmi: number; withFigure: number } {
  const { shapeCapital, cityCapital } = figures(), have = haveUsDollars(), withFigure = new Set<string>(), wagmi = new Set<string>();
  const count = (code: string, need: number) => { const country = countryOf(places, code); withFigure.add(country); if (need <= have) wagmi.add(country); };
  shapeCapital.forEach((need, shape) => { if (!Number.isNaN(need)) count(geometry.shapeCodes[shape], need); });
  for (const [code, need] of cityCapital) count(code, need);
  return { wagmi: wagmi.size, withFigure: withFigure.size };
}
function renderStrip(): void {
  const { least, most, cityCapital } = figures();
  const cells = [placeCell({ role: 'You', shortRole: 'You', code: state.visitor, picker: 'visitor', emptyWords: 'Choose a place' }),
    placeCell({ role: 'Compared with', shortRole: 'Compared with', code: state.compared, picker: 'compared', emptyWords: 'Add a place' })];
  if (state.mode === 'need') cells.push(placeCell({ role: 'Cheapest', shortRole: 'Cheapest', code: least }), placeCell({ role: 'Most expensive', shortRole: 'Most expensive', code: most }));
  else {
    // The most to spare is the city that needs least; its lead over the others is the same whatever the visitor has.
    const { wagmi, withFigure } = wagmiCountries();
    cells.push(placeCell({ role: 'Most to spare', shortRole: 'Most to spare', code: least ?? [...cityCapital.keys()][0] ?? null }),
      `<div class="cell cell-count"><div class="cell-role">${verdictWord('WAGMI')} in</div><b class="cell-count-words">${wagmi} of ${withFigure} countries</b></div>`);
  }
  element('strip').innerHTML = cells.join('');
  fitStripNames();
}
// A name too long for its line steps down a size, then wraps onto two lines. It is never cut short.
function fitStripNames(): void {
  for (const words of element('strip').querySelectorAll<HTMLElement>('.cell-name-words')) {
    words.classList.remove('is-smaller', 'is-wrapped');
    if (words.scrollWidth <= words.clientWidth) continue;
    words.classList.add('is-smaller');
    if (words.scrollWidth > words.clientWidth) words.classList.add('is-wrapped');
  }
  // The key and the zoom buttons stand just above the strip, however tall it is.
  document.documentElement.style.setProperty('--strip-height', `${element('strip').offsetHeight}px`);
}
document.fonts.ready.then(() => { fitStripNames(); coverMap(); });
new ResizeObserver(() => fitStripNames()).observe(element('strip'));
element('strip').addEventListener('click', event => {
  const target = (event.target as HTMLElement).closest<HTMLElement>('[data-pick],[data-open]');
  if (target?.dataset.pick) openPicker(target.dataset.pick as 'visitor' | 'compared');
  else if (target?.dataset.open) openPlace(target.dataset.open, true);
});

// ---- A place's details, the same in both modes but for one line in the second.
const costWords: Record<string, string> = {
  rent: 'Rent, two-bed flat in the main town', everyday: 'Everyday spending', car: 'One car',
  housekeeper: `Housekeeper, ${snapshot.lifestyle.housekeeperHoursPerWeek} hours a week`, health: 'Private health cover', trips: 'A few trips a year',
};
// One short line under each cost: where the figure was measured and what kind of source it is ("Lisbon · official statistics"), or
// that it is a stand-in. Publishers are named on the About page only.
function costLine(cost: Extract<PlaceFigure, { kind: 'figure' }>['costs'][number]): string {
  if (!cost.figure) return 'The same everywhere';
  return `${escapeHtml(sourcePlace(places, cost))} · ${cost.isStandIn ? '<em>stand-in</em>' : sourceKind(cost)}`;
}
const closeIcon = '<svg viewBox="0 0 12 12"><path d="M1 1l10 10M11 1L1 11"/></svg>';
function renderDetails(): void {
  const panel = element('details'), code = state.opened;
  panel.hidden = !code;
  document.body.classList.toggle('has-details', !!code);
  if (!code) return;
  const figure = figures().figureOf(code), context = contextOf(places, code);
  const head = `<div class="details-head">${flagHtml(places, code)}<div class="details-title"><h2>${escapeHtml(nameOf(places, code))}</h2>${context ? `<p>${escapeHtml(context)}</p>` : ''}</div>
    <button type="button" class="round-button" data-close-details aria-label="Close">${closeIcon}</button></div>`;
  if (figure.kind !== 'figure') {
    const words = figure.kind === 'occupied' ? 'Figures for occupied Palestine are not known.'
      : `Not known yet: ${figure.missing.map(part => (part === 'tax' ? 'the tax' : part === 'exchange rate' ? 'the exchange rate' : costWords[part].split(',')[0].toLowerCase())).join(', ')}.`;
    panel.innerHTML = `${head}<div class="details-figure"><b class="details-capital details-unknown">${figure.kind === 'occupied' ? 'Not known' : 'No figure yet'}</b></div><p class="details-sentence">${words}</p>${detailsButtons(code)}`;
    return;
  }
  const need = figure.capitalUsDollars, second = secondMoney(need), rate = state.settings.withdrawalRate;
  const visitorNeed = state.visitor && state.visitor !== code ? needOf(state.visitor) : null;
  const comparison = visitorNeed === null ? '' : `${money(Math.abs(need - visitorNeed))} ${need < visitorNeed ? 'less' : 'more'} than ${escapeHtml(nameOf(places, state.visitor!))}.`;
  const word = verdict(need);
  const verdictLine = state.mode === 'have'
    ? `<p class="details-verdict">${verdictWord(word)} <b style="color:${verdictInk[word]}">${differenceWords(need)}</b> with ${formatWhole(state.have, mainCurrency())}.${comparison ? ` ${comparison}` : ''}</p>`
    : comparison ? `<p class="details-verdict">${comparison}</p>` : '';
  const country = countryOf(places, code), countryWords = countryInSentence(places, country).replace(/^the /, 'The ');
  const tax = taxWords(figure.tax, need, figure.withdrawalUsDollarsPerYear, countryWords, country === 'US', roundedMoney);
  const sentence = `Sell ${Math.round(rate * 100)}% a year and you get ${roundedMoney(figure.withdrawalUsDollarsPerYear)}. ${tax.sentence} That leaves ${roundedMoney(figure.withdrawalUsDollarsPerYear - figure.tax.usDollarsPerYear)} to live on.`;
  const taxMonthly = figure.tax.usDollarsPerYear / 12, shades = ['#10151C', '#10151CCC', '#10151C99', '#10151C73', '#10151C52', '#10151C38'];
  const bar = figure.costs.map((cost, index) => `<i style="flex-grow:${cost.usDollarsPerMonth};background:${shades[index]}"></i>`).join('') + `<i class="bar-tax" style="flex-grow:${taxMonthly}"></i>`;
  const taxSource = figure.tax.isStandIn ? '<em>stand-in</em>' : 'tax rules';
  const rows = figure.costs.map((cost, index) => `<li><i style="background:${shades[index]}"></i><div><b>${costWords[cost.part]}</b><small>${costLine(cost)}</small></div><span>${roundedMoney(cost.usDollarsPerMonth)}</span></li>`).join('')
    + `<li class="tax-row"><i></i><div><b>${tax.row}</b><small>${escapeHtml(nameOf(places, country))} · ${taxSource}</small></div><span>${roundedMoney(taxMonthly)}</span></li>`;
  const otherRegime: Settings = { ...state.settings, regime: state.settings.regime === 'standard' ? 'special' : 'standard' };
  const otherNeed = figure.tax.hasSpecialRegime ? needOf(code, otherRegime) : null;
  const otherRow = otherNeed === null || Math.abs(otherNeed - need) < 5e3 ? '' : `<button type="button" class="details-other" data-regime="${otherRegime.regime}"><span>${otherRegime.regime === 'special' ? 'With the newcomer tax break' : 'With normal tax'}</span>
    <span><b>${money(otherNeed)}</b><small>${money(Math.abs(otherNeed - need))} ${otherNeed < need ? 'less' : 'more'}</small></span></button>`;
  panel.innerHTML = `${head}
    <div class="details-figure"><b class="details-capital">${money(need)}</b>${second ? `<span class="details-local">(${second})</span>` : ''}</div>${verdictLine}
    <p class="details-sentence">${sentence}</p>
    <div class="details-costs"><div class="details-costs-head"><b>What it pays for</b><span>a month</span></div><div class="cost-bar">${bar}</div><ul>${rows}</ul>
    <div class="details-total"><b>${Math.round(rate * 100)}% of ${money(need)}, a month</b><b>${formatWhole(figure.withdrawalUsDollarsPerYear / 12 * perUsDollar(mainCurrency()), mainCurrency())}</b></div></div>
    ${otherRow}${detailsButtons(code)}`;
}
function detailsButtons(code: string): string {
  const compare = state.visitor && state.visitor !== code && state.compared !== code ? `<button type="button" class="button button-dark" data-compare="${code}">Compare with ${escapeHtml(nameOf(places, state.visitor))}</button>` : '';
  const here = state.visitor !== code ? `<button type="button" class="button" data-here="${code}">I’m here</button>` : '';
  return `<div class="details-buttons">${compare}${here}<span class="grow"></span><a class="link-button" href="/about#sources">All sources</a></div>`;
}
element('details').addEventListener('click', event => {
  const target = event.target as HTMLElement;
  if (target.closest('[data-close-details]')) openPlace(null, false);
  else if (target.closest('[data-compare]')) compareWith(target.closest<HTMLElement>('[data-compare]')!.dataset.compare!);
  else if (target.closest('[data-here]')) { state.visitor = target.closest<HTMLElement>('[data-here]')!.dataset.here!; if (state.compared === state.visitor) state.compared = null; update(); }
});

// Where a place is on the map, as a box in map units: a city's point, or the box round a region's shapes.
// A place's shapes: its own, or for a country or state drawn by region, every shape inside it.
const shapesByPlace = new Map<string, number[]>();
function shapesOf(code: string): number[] {
  if (!shapesByPlace.has(code)) shapesByPlace.set(code, geometry.shapeCodes.flatMap((shapeCode, shape) => (chainOf(places, shapeCode).includes(code) ? [shape] : [])));
  return shapesByPlace.get(code)!;
}
function boxOf(code: string): [number, number, number, number] | null {
  const city = places.cityByCode.get(code);
  if (city) { const [x, y] = projectPoint(city.longitude, city.latitude); return [x, y, x, y]; }
  let west = Infinity, north = Infinity, east = -Infinity, south = -Infinity;
  shapesOf(code).forEach(shape => {
    west = Math.min(west, geometry.shapeBoxes[shape * 4]); north = Math.min(north, geometry.shapeBoxes[shape * 4 + 1]);
    east = Math.max(east, geometry.shapeBoxes[shape * 4 + 2]); south = Math.max(south, geometry.shapeBoxes[shape * 4 + 3]);
  });
  return Number.isFinite(west) ? [west, north, east, south] : null;
}
// Bring places into the part of the map the cards leave uncovered, as large as fits.
function showPlaces(codes: string[]): void {
  const boxes = codes.map(boxOf).filter((box): box is [number, number, number, number] => !!box);
  if (!boxes.length) return;
  const box: [number, number, number, number] = [Math.min(...boxes.map(b => b[0])), Math.min(...boxes.map(b => b[1])), Math.max(...boxes.map(b => b[2])), Math.max(...boxes.map(b => b[3]))];
  const isPoint = box[2] - box[0] < 1e-4 && box[3] - box[1] < 1e-4;
  if (isPoint) mapView.show(box[0], box[1], Math.max(mapView.zoomLevel(), 4.5));
  else mapView.showBox(...box);
}

// Open a place's details. On a phone the sheet covers most of the map, so the place moves into the strip of map above it; on a
// laptop the map moves only when the place was chosen from a list.
function openPlace(code: string | null, move: boolean): void {
  state.opened = code;
  update();
  if (code && (move || isPhone())) showPlaces([code]);
}

// Compare with a place: back to the map with both places in view and the comparison along the bottom.
function compareWith(code: string): void {
  state.compared = code;
  state.opened = null;
  update();
  showPlaces([state.visitor, code].filter(Boolean) as string[]);
}

// ---- The place list: search every city, region and country the map draws.
type Pick = 'visitor' | 'compared';
let picking: Pick = 'visitor';
const searchEntries = [
  ...places.cities.map(city => ({ code: city.code, names: [city.name, ...city.otherNames].map(plainLetters), rank: city.population })),
  ...Object.entries(places.rows).map(([code, [name, , kind]]) => ({ code, names: [plainLetters(name ?? code)], rank: kind === 'country' ? 5e7 : kind === 'state' ? 2e6 : 1e5 })),
].sort((a, b) => b.rank - a.rank);
function openPicker(pick: Pick): void {
  picking = pick;
  element('picker-title').textContent = pick === 'visitor' ? 'Where are you?' : 'Compare with';
  const input = element<HTMLInputElement>('picker-input');
  input.value = '';
  renderPickerResults();
  element('picker').hidden = false;
  input.focus();
}
function renderPickerResults(): void {
  const query = plainLetters(element<HTMLInputElement>('picker-input').value.trim()), drawn = new Set(geometry.shapeCodes);
  // A region is offered only where the map draws it; otherwise its country or its cities stand for it.
  const offered = searchEntries.filter(entry => places.cityByCode.has(entry.code) || drawn.has(entry.code) || places.rows[entry.code]?.[2] === 'country');
  const matches = query ? offered.filter(entry => entry.names.some(name => name.startsWith(query) || name.includes(` ${query}`))).slice(0, 8)
    : places.cities.slice(0, 8).map(city => ({ code: city.code }));
  element('picker-results').innerHTML = matches.length ? matches.map(({ code }) => {
    const need = needOf(code), context = contextOf(places, code);
    return `<li><button type="button" data-picked="${code}">${flagHtml(places, code)}<span><b>${escapeHtml(nameOf(places, code))}</b>${context ? `<small>${escapeHtml(context)}</small>` : ''}</span><span class="picker-amount">${need === null ? figureWords(figures().figureOf(code)) : money(need)}</span></button></li>`;
  }).join('') : '<li class="picker-none">No place has that name.</li>';
}
element('picker-input').addEventListener('input', renderPickerResults);
element('picker-input').addEventListener('keydown', event => { if (event.key === 'Enter') element('picker-results').querySelector<HTMLElement>('[data-picked]')?.click(); });
element('picker').addEventListener('click', event => {
  const target = event.target as HTMLElement, picked = target.closest<HTMLElement>('[data-picked]');
  if (picked) {
    element('picker').hidden = true;
    if (picking === 'compared') { compareWith(picked.dataset.picked!); return; }
    state.visitor = picked.dataset.picked!;
    if (state.compared === state.visitor) state.compared = null;
    update();
    showPlaces([state.visitor, state.compared].filter(Boolean) as string[]);
  } else if (target === element('picker') || target.closest('[data-close-picker]')) element('picker').hidden = true;
});

// ---- Sharing: one picture of the mode the visitor is in, a link, and a post on Twitter.
// A shared link names the currency in brackets, so its pictures look the same whoever opens it.
const sharedQuery = () => { const query = linkQuery(places, state, { withOpened: false }), second = secondCurrency(); return second ? `${query}${query ? '&' : '?'}also=${second}` : query; };
const shareLink = () => `${location.origin}/${sharedQuery()}`;
const pictureAddress = () => `/picture.png${sharedQuery()}`;
element('share-button').addEventListener('click', () => {
  element<HTMLImageElement>('share-picture').src = pictureAddress();
  element('share-status').textContent = '';
  element('share').hidden = false;
});
element('share').addEventListener('click', async event => {
  const target = event.target as HTMLElement, status = element('share-status');
  if (target === element('share') || target.closest('[data-close-share]')) element('share').hidden = true;
  else if (target.closest('[data-post]')) open(`https://twitter.com/intent/tweet?url=${encodeURIComponent(shareLink())}`, '_blank', 'noopener');
  else if (target.closest('[data-copy-link]')) { await navigator.clipboard.writeText(shareLink()); status.textContent = 'Link copied.'; }
  else if (target.closest('[data-copy-picture]')) {
    try {
      await navigator.clipboard.write([new ClipboardItem({ 'image/png': fetch(pictureAddress()).then(response => response.blob()) })]);
      status.textContent = 'Picture copied. Paste it into your post.';
    } catch {
      const link = document.createElement('a');
      link.href = pictureAddress(); link.download = 'rich-enough-to-fire.png'; link.click();
      status.textContent = 'Picture saved.';
    }
  }
});
document.addEventListener('keydown', event => {
  if (event.key !== 'Escape') return;
  closeMenus();
  for (const id of ['share', 'picker']) element(id).hidden = true;
});

// ---- Zoom buttons.
element('zoom-in').addEventListener('click', () => mapView.zoomBy(2));
element('zoom-out').addEventListener('click', () => mapView.zoomBy(0.5));
element('go-home').addEventListener('click', () => { if (state.visitor) openPlace(state.visitor, true); else mapView.showWorld(); });

// ---- Everything that follows from the state, and the link that holds it.
let figuresDrawnFor = '';
function update(): void {
  const drawnFor = `${state.mode}|${state.settings.withdrawalRate}|${state.settings.regime}|${haveUsDollars()}|${mainCurrency()}|${state.visitor}|${state.compared}|${isDark()}`;
  if (drawnFor !== figuresDrawnFor) { figuresDrawnFor = drawnFor; colourTheMap(); labelTheCities(); }
  renderBar(); renderKey(); renderStrip(); renderDetails();
  const opened = state.opened, isCity = !!opened && places.cityByCode.has(opened);
  mapView.setHighlightedShapes(opened && !isCity ? shapesOf(opened) : []);
  mapView.setEmphasis({ dark: state.visitor, ringed: isCity ? opened : null, named: [state.visitor, state.compared].filter(Boolean) as string[] });
  history.replaceState(null, '', `/${linkQuery(places, state)}`);
  coverMap();
}
matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => { themeTheMap(); figuresDrawnFor = ''; update(); });

// The cards over the map: places are brought into the part they leave uncovered, and no label goes under them. An open place's
// details cover the right of the map on a laptop and most of it on a phone.
function coverMap(): void {
  const cards = ['bar', 'have', 'bar-right', 'strip', 'key', 'zoom', 'details'].map(id => element(id)).filter(card => !card.hidden);
  const top = Math.max(...['bar', 'have'].map(id => element(id)).filter(card => !card.hidden).map(card => card.getBoundingClientRect().bottom));
  const strip = element('strip').getBoundingClientRect(), details = element('details');
  const detailsBox = details.hidden ? null : details.getBoundingClientRect();
  const bottom = detailsBox && isPhone() ? innerHeight - detailsBox.top : innerHeight - strip.top + (isPhone() ? 0 : element('key').offsetHeight + 12);
  const right = detailsBox && !isPhone() ? innerWidth - detailsBox.left : 0;
  mapView.setCovers({ top, bottom, left: 0, right, boxes: cards.map(card => card.getBoundingClientRect()) });
}
addEventListener('resize', coverMap);

update();
// The first view: the whole world on a laptop; on a phone, the visitor's part of it.
const visitorCity = state.visitor && places.cityByCode.get(state.visitor);
if (state.opened) openPlace(state.opened, true);
else if (isPhone() && visitorCity) mapView.show(...projectPoint(visitorCity.longitude, visitorCity.latitude), 3.7, false);
else mapView.showWorld(false);
document.body.classList.add('is-ready');

// The detailed shapes, once the page is up.
fetch(DATA_PATHS.fineShapes).then(response => response.arrayBuffer()).then(bytes => {
  const fine = readMapGeometry(new Uint8Array(bytes));
  if (fine.shapeCodes.join() !== geometry.shapeCodes.join()) throw new Error('The detailed map has different places');
  geometry = fine;
  mapView.setGeometry(fine, 'fine');
  update();
});

// For checking from a browser's console or a test.
Object.assign(window, { enough: { state, places, figures, mapView, openPlace, update } });
