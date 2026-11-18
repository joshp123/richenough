import { nominalPortfolioReturn } from './calculation.ts';
import { registerTaxRules } from './tax-rules.ts';

// 2026. Both spouses own the positive-list equity ETF and have no other income.
const jointShareBand = 2 * 79_400;
const householdSavingsAccountCap = 2 * 174_200;

function denmark(code: string, municipalRate: number) {
  // Personskatteloven §§ 8a, 9–12. Unused allowances can reduce the upper
  // share tax. The lower band and the savings-account tax are final.
  const personalCredit = 2 * 54_100 * (0.1201 + municipalRate);
  registerTaxRules(code, {
    currency: 'DKK',
    hasSpecialRegime: true,
    taxOwed: ({ capitalAtStartOfYearLocal: capital }, regime) => {
      const accountCapital = regime === 'special' ? Math.min(capital, householdSavingsAccountCap) : 0;
      const returnOutsideAccount = (capital - accountCapital) * nominalPortfolioReturn;
      const lowerTax = 0.27 * Math.min(returnOutsideAccount, jointShareBand);
      const upperTax = 0.42 * Math.max(0, returnOutsideAccount - jointShareBand);
      return {
        taxLocal: lowerTax + Math.max(0, upperTax - personalCredit) + accountCapital * nominalPortfolioReturn * 0.17,
        regimeName: regime === 'special' ? 'Share savings accounts' : 'Standard',
        explanation: 'Denmark taxes annual returns on positive-list equity ETFs, including unsold gains. The estimate uses a 7% nominal return, joint share-income bands of 27% and 42%, and both spouses’ unused personal allowances against the upper band.'
          + (regime === 'special' ? ' Each spouse puts up to DKK 174,200 into a share savings account taxed at 17% on its annual return. Existing accounts can grow beyond that limit.' : ''),
        sourceIds: ['tax-dk-share-tax', 'tax-dk-fund-tax', 'tax-dk-ask', 'tax-dk-credit', 'tax-dk-person', 'tax-dk-local'],
      };
    },
  });
}

denmark('DK', 0.2505); // National average municipal rate, no church membership.
denmark('CITY-2618425', 0.2339);
