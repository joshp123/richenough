// The capital a couple needs in a place: the smallest sum whose yearly withdrawal, less that place's tax on it, pays for the
// lifestyle for good. The page and the Worker share this; the tax rules come from src/tax/.
import { chainOf, countryOf, type Places } from './places.ts';
import { components, type Component, type Figure } from './snapshot.ts';
import { taxRulesFor, type TaxRegime } from './tax/tax-rules.ts';

// The two choices that recolour the whole map. Josh may change either, so each is one list here.
export const withdrawalRates = [0.03, 0.04, 0.05] as const;
export type WithdrawalRate = typeof withdrawalRates[number];
export const defaultWithdrawalRate: WithdrawalRate = 0.05;
export const taxRegimes: TaxRegime[] = ['standard', 'special'];
export type Settings = { withdrawalRate: WithdrawalRate; regime: TaxRegime };
export const defaultSettings: Settings = { withdrawalRate: defaultWithdrawalRate, regime: 'standard' };

export type Cost = { part: Component | 'trips'; usDollarsPerMonth: number; figure: Figure | null; isStandIn: boolean };
export type TaxPart = {
  usDollarsPerYear: number; localPerYear: number; currency: string; regimeName: string; explanation: string; sourceIds: string[]; isStandIn: boolean;
  // The place has rules for a special regime, so the other setting would give a different figure.
  hasSpecialRegime: boolean;
};
export type PlaceFigure =
  | { kind: 'figure'; capitalUsDollars: number; withdrawalUsDollarsPerYear: number; spendingUsDollarsPerYear: number; costs: Cost[]; tax: TaxPart }
  | { kind: 'occupied' }
  | { kind: 'missing'; missing: (Component | 'tax' | 'exchange rate')[] };

const unitsPerMonth: Record<string, number> = { per_month: 1, per_year: 1 / 12, per_week: 52 / 12 };

function usDollarsPerUnit(places: Places, currency: string): number | null {
  if (currency === 'USD') return 1;
  const rate = places.snapshot.exchangeRates[currency];
  return rate ? 1 / rate.perUsDollar : null;
}

// The figure for a component: the first one along the place's chain, else the country's stand-in.
export function figureFor(places: Places, chain: string[], component: Component): Figure | null {
  for (const code of chain) {
    const figure = places.snapshot.figures[component][code];
    if (figure) return figure;
  }
  return places.snapshot.standIns[component][chain.at(-1)!] ?? null;
}

function monthlyCost(places: Places, component: Component, figure: Figure): number | null {
  const { lifestyle } = places.snapshot;
  if (component === 'everyday') return figure.unit === 'index_us_100' ? lifestyle.everydayUsDollarsPerMonth * figure.amount / 100 : null;
  const perUnit = usDollarsPerUnit(places, figure.currency);
  if (perUnit === null) return null;
  if (component === 'housekeeper') return figure.unit === 'per_hour' ? figure.amount * perUnit * lifestyle.housekeeperHoursPerWeek * 52 / 12 : null;
  const perMonth = unitsPerMonth[figure.unit];
  return perMonth === undefined ? null : figure.amount * perUnit * perMonth;
}

// The smallest capital C at which rate × C less tax(rate × C, C) covers the spending, all in the tax's currency.
function solveCapital(spending: number, rate: number, taxOf: (withdrawal: number, capital: number) => number): number | null {
  const shortfall = (capital: number) => spending - (rate * capital - taxOf(rate * capital, capital));
  let low = spending / rate;
  if (shortfall(low) <= 0) return low;
  let high = low * 2;
  while (shortfall(high) > 0) { low = high; high *= 2; if (high > spending / rate * 1e3) return null; }
  for (let step = 0; step < 60 && (high - low) / high > 1e-9; step++) {
    const middle = (low + high) / 2;
    if (shortfall(middle) > 0) low = middle; else high = middle;
  }
  return high;
}

export function placeFigure(places: Places, code: string, settings: Settings): PlaceFigure {
  const chain = chainOf(places, code), country = chain.at(-1)!;
  if (country === 'PS') return { kind: 'occupied' };
  const missing: (Component | 'tax' | 'exchange rate')[] = [], costs: Cost[] = [];
  for (const component of components) {
    const figure = figureFor(places, chain, component), cost = figure && monthlyCost(places, component, figure);
    if (cost === null || cost === undefined) { missing.push(component); continue; }
    costs.push({ part: component, usDollarsPerMonth: cost, figure, isStandIn: !!figure!.isStandIn });
  }
  const { lifestyle } = places.snapshot;
  costs.push({ part: 'trips', usDollarsPerMonth: lifestyle.tripsUsDollarsPerYear / 12, figure: null, isStandIn: false });
  const spendingUsDollarsPerYear = costs.reduce((sum, cost) => sum + cost.usDollarsPerMonth * 12, 0);

  const rules = taxRulesFor(chain), standIn = places.snapshot.taxStandIns[country];
  const currency = rules?.currency ?? 'USD', perUnit = usDollarsPerUnit(places, currency);
  if (!rules && !standIn) missing.push('tax');
  if (perUnit === null) missing.push('exchange rate');
  if (missing.length) return { kind: 'missing', missing };

  const rate = settings.withdrawalRate;
  const taxOf = (withdrawal: number, capital: number) => (rules
    ? rules.taxOwed({ withdrawalLocal: withdrawal, capitalAtStartOfYearLocal: capital }, settings.regime).taxLocal
    : withdrawal * standIn.rate);
  const capitalLocal = solveCapital(spendingUsDollarsPerYear / perUnit!, rate, taxOf);
  if (capitalLocal === null) return { kind: 'missing', missing: ['tax'] };
  const withdrawalLocal = rate * capitalLocal;
  const owed = rules?.taxOwed({ withdrawalLocal, capitalAtStartOfYearLocal: capitalLocal }, settings.regime);
  const taxLocal = owed ? owed.taxLocal : withdrawalLocal * standIn.rate;
  return {
    kind: 'figure',
    capitalUsDollars: capitalLocal * perUnit!,
    withdrawalUsDollarsPerYear: withdrawalLocal * perUnit!,
    spendingUsDollarsPerYear,
    costs,
    tax: {
      usDollarsPerYear: taxLocal * perUnit!, localPerYear: taxLocal, currency,
      regimeName: owed?.regimeName ?? 'Standard', explanation: owed?.explanation ?? '', sourceIds: owed?.sourceIds ?? [standIn.sourceId],
      isStandIn: !rules, hasSpecialRegime: !!rules?.hasSpecialRegime,
    },
  };
}

// Whether the figure leans on a stand-in anywhere.
export const hasStandIn = (figure: PlaceFigure) => figure.kind === 'figure' && (figure.tax.isStandIn || figure.costs.some(cost => cost.isStandIn));
