import { registerTaxRules, type TaxOwed, type TaxRules, type YearLivingOffInvestments } from './tax-rules.ts';

// Each band starts at its threshold. Rates are fractions, including zero.
export type TaxBand = readonly [threshold: number, rate: number];

export function progressiveTax(base: number, bands: readonly TaxBand[]): number {
  let tax = 0;
  for (const [index, [threshold, rate]] of bands.entries()) {
    const nextThreshold = bands[index + 1]?.[0] ?? Infinity;
    tax += Math.max(0, Math.min(base, nextThreshold) - threshold) * rate;
  }
  return tax;
}

export function registerStandardTax(
  placeCodes: string | readonly string[],
  currency: string,
  explanation: string,
  sourceIds: string[],
  calculate: (year: YearLivingOffInvestments) => number,
): void {
  const rules: TaxRules = {
    currency,
    hasSpecialRegime: false,
    taxOwed: (year): TaxOwed => ({
      taxLocal: calculate(year),
      regimeName: 'Standard',
      explanation,
      sourceIds,
    }),
  };
  for (const code of typeof placeCodes === 'string' ? [placeCodes] : placeCodes) {
    registerTaxRules(code, rules);
  }
}

// Nominal portfolio assumptions where a country taxes returns before the units are sold.
// 7% is the scenario's nominal total return. Of that, 1.5% approximates fund dividend income.
export const nominalPortfolioReturn = 0.07;
export const fundDividendYield = 0.015;
