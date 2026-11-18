import { progressiveTax, type TaxBand } from './calculation.ts';
import { registerTaxRules } from './tax-rules.ts';

// Income Tax Ordinance consolidated on 30 June 2026, First Schedule, Part I.
const bands: TaxBand[] = [
  [600_000, 0.15], [1_200_000, 0.2], [1_600_000, 0.3],
  [3_200_000, 0.4], [5_600_000, 0.45],
];
const superTaxRates: TaxBand[] = [
  [150_000_000, 0.01], [200_000_000, 0.015], [250_000_000, 0.025],
  [300_000_000, 0.035], [350_000_000, 0.055], [400_000_000, 0.075], [500_000_000, 0.08],
];

registerTaxRules('PK', {
  currency: 'PKR',
  hasSpecialRegime: false,
  taxOwed: ({ withdrawalLocal }) => {
    const gainPerSpouse = withdrawalLocal / 2;
    const incomeTax = progressiveTax(gainPerSpouse, bands);
    const surcharge = gainPerSpouse > 10_000_000 ? incomeTax * 0.1 : 0;
    const superTaxRate = superTaxRates.reduce((rate, [threshold, bandRate]) => gainPerSpouse > threshold ? bandRate : rate, 0);
    return {
      taxLocal: 2 * (incomeTax + surcharge + gainPerSpouse * superTaxRate),
      regimeName: 'Standard',
      explanation: 'The couple sells shares in an offshore ETF company on a foreign exchange outside Pakistan’s clearing system. Section 37 applies the ordinary bands to each spouse’s gains. Surcharges apply above PKR 10 million and PKR 150 million per spouse. Section 51 exempts foreign gains for qualifying returning Pakistani citizens in the year of return and the following tax year.',
      sourceIds: ['tax-pk-ito'],
    };
  },
});
