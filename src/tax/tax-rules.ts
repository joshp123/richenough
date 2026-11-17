// Shared types for the tax a couple pays while living off a global equity ETF portfolio.
// Every amount is in the place's own currency.

export type TaxRegime = 'standard' | 'special';

export type YearLivingOffInvestments = {
  withdrawalLocal: number;
  capitalAtStartOfYearLocal: number;
};

export type TaxOwed = {
  taxLocal: number;
  regimeName: string;
  explanation: string;
  sourceIds: string[];
};

export type TaxRules = {
  currency: string;
  hasSpecialRegime: boolean;
  taxOwed: (year: YearLivingOffInvestments, regime: TaxRegime) => TaxOwed;
};

const taxRulesByPlaceCode = new Map<string, TaxRules>();

export function registerTaxRules(placeCode: string, rules: TaxRules): void {
  taxRulesByPlaceCode.set(placeCode, rules);
}

// Place codes run from the most specific to the country, for example ['US-24031', 'US-MD', 'US'].
export function taxRulesFor(placeCodesMostSpecificFirst: string[]): TaxRules | undefined {
  for (const placeCode of placeCodesMostSpecificFirst) {
    const rules = taxRulesByPlaceCode.get(placeCode);
    if (rules) return rules;
  }
  return undefined;
}
