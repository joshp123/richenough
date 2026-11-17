// A link carries everything a view and its share picture show: /?me=amsterdam&vs=lisbon&in=EUR&have=2000000&tax=break
// Cities go by name (with their GeoNames id where two share a name), other places by their code in lower case (us-06037).
import { defaultSettings, withdrawalRates, type Settings, type WithdrawalRate } from './capital.ts';
import { plainLetters, type Places } from './places.ts';
import { clampHave, defaultHave, type Mode } from './verdict.ts';

// mode: "How much you need" or "Am I gonna make it?". have: what the visitor says they have, in the currency they chose
// (US dollars unless they chose another).
export type LinkState = { mode: Mode; visitor: string | null; compared: string | null; opened: string | null; currency: string | null; have: number; settings: Settings };

const slugOfName = (name: string) => plainLetters(name).replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');

let citySlugs: { slugOfCode: Map<string, string>; codeOfSlug: Map<string, string> } | null = null;
function slugsOf(places: Places) {
  if (citySlugs) return citySlugs;
  const slugOfCode = new Map<string, string>(), codeOfSlug = new Map<string, string>();
  // Cities are biggest first, so the biggest of several with one name keeps the plain name.
  for (const city of places.cities) {
    const plain = slugOfName(city.name), slug = codeOfSlug.has(plain) ? `${plain}-${city.code.slice(5)}` : plain;
    slugOfCode.set(city.code, slug); codeOfSlug.set(slug, city.code);
  }
  return (citySlugs = { slugOfCode, codeOfSlug });
}

export function slugOf(places: Places, code: string): string {
  return slugsOf(places).slugOfCode.get(code) ?? code.toLowerCase();
}

export function codeOfSlug(places: Places, slug: string | null): string | null {
  if (!slug) return null;
  const lower = slug.toLowerCase(), city = slugsOf(places).codeOfSlug.get(lower);
  if (city) return city;
  const asCode = lower.toUpperCase();
  if (places.rows[asCode] || places.cityByCode.has(asCode)) return asCode;
  const cityById = lower.match(/-(\d+)$/)?.[1];
  return cityById && places.cityByCode.has(`CITY-${cityById}`) ? `CITY-${cityById}` : null;
}

export function linkQuery(places: Places, state: LinkState, { withOpened = true } = {}): string {
  const parameters = new URLSearchParams();
  if (state.mode === 'have') parameters.set('mode', 'have');
  if (state.visitor) parameters.set('me', slugOf(places, state.visitor));
  if (state.compared) parameters.set('vs', slugOf(places, state.compared));
  if (withOpened && state.opened) parameters.set('place', slugOf(places, state.opened));
  if (state.currency) parameters.set('in', state.currency);
  if (state.mode === 'have' && state.have !== defaultHave) parameters.set('have', String(Math.round(state.have)));
  if (state.settings.withdrawalRate !== defaultSettings.withdrawalRate) parameters.set('spend', String(Math.round(state.settings.withdrawalRate * 100)));
  if (state.settings.regime === 'special') parameters.set('tax', 'break');
  return parameters.size ? `?${parameters}` : '';
}

export function linkStateOf(places: Places, url: URL): LinkState {
  const parameters = url.searchParams, spend = Number(parameters.get('spend')) / 100;
  const currency = (parameters.get('in') ?? '').toUpperCase();
  return {
    mode: parameters.get('mode') === 'have' ? 'have' : 'need',
    visitor: codeOfSlug(places, parameters.get('me')),
    compared: codeOfSlug(places, parameters.get('vs')),
    opened: codeOfSlug(places, parameters.get('place')),
    currency: currency === 'USD' || places.snapshot.exchangeRates[currency] ? currency : null,
    have: Number(parameters.get('have')) > 0 ? clampHave(Number(parameters.get('have'))) : defaultHave,
    settings: {
      withdrawalRate: (withdrawalRates as readonly number[]).includes(spend) ? spend as WithdrawalRate : defaultSettings.withdrawalRate,
      regime: parameters.get('tax') === 'break' ? 'special' : 'standard',
    },
  };
}
