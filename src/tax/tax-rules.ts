// Shared types for the tax a couple pays while living off a global equity ETF portfolio.
// Every amount is in the place's own currency.

export type TaxRegime = 'standard' | 'special';

export type YearLivingOffInvestments = {
  withdrawalLocal: number;
  capitalAtStartOfYearLocal: number;
};

export type TaxOwed = {
  // Include any mandatory recurring cash costs of the chosen regime.
  taxLocal: number;
  regimeName: string;
  explanation: string;
  sourceIds: string[];
};

export type TaxRules = {
  currency: string;
  // A special regime must last at least ten years from arrival or be open-ended.
  // Describe shorter breaks in the standard result and return it in both modes.
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
