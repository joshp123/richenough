import { nominalPortfolioReturn, progressiveTax, type TaxBand } from './calculation.ts';
import { registerTaxRules } from './tax-rules.ts';

// 2026. Positive-list equity ETF, joint share-income bands and two share savings accounts.
const bands: TaxBand[] = [[0, 0.27], [158_800, 0.42]];
const householdSavingsAccountCap = 2 * 174_200;

registerTaxRules('DK', {
  currency: 'DKK',
  hasSpecialRegime: true,
  taxOwed: ({ capitalAtStartOfYearLocal: capital }, regime) => {
    const accountCapital = regime === 'special' ? Math.min(capital, householdSavingsAccountCap) : 0;
    return {
      taxLocal: progressiveTax((capital - accountCapital) * nominalPortfolioReturn, bands)
        + accountCapital * nominalPortfolioReturn * 0.17,
      regimeName: regime === 'special' ? 'Share savings accounts' : 'Standard',
      explanation: regime === 'special'
        ? 'Each spouse can use a share savings account with a DKK 174,200 contribution limit in 2026 and 17% annual tax on returns. The rest of the portfolio stays on the normal scale. Capital above the contribution limit may accrue inside an existing account.'
        : 'Denmark taxes the annual change in value of positive-list equity ETFs, including unsold gains. The estimate uses a 7% nominal return and joint share-income bands of 27% and 42%.',
      sourceIds: ['tax-dk-share-tax', 'tax-dk-fund-tax', 'tax-dk-ask'],
    };
  },
});
