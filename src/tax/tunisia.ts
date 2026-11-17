import { registerStandardTax } from './calculation.ts';

// Income Tax Code articles 33 and 44, and Article 88 of the 2026 Finance Act.
registerStandardTax(
  'TN', 'TND',
  'The estimate applies the 10% private securities gains rate to an offshore ETF company held through the end of the calendar year after purchase. The 2026 wealth tax charges each spouse 0.5% of their whole taxable fortune from TND 3 million, or 1% above TND 5 million.',
  ['tax-tn-income-code', 'tax-tn-securities-note', 'tax-tn-wealth-act', 'tax-tn-css-note', 'tax-tn-foreign-ruling'],
  ({ withdrawalLocal, capitalAtStartOfYearLocal }) => {
    const wealthPerSpouse = capitalAtStartOfYearLocal / 2;
    const wealthRate = wealthPerSpouse > 5_000_000 ? 0.01 : wealthPerSpouse >= 3_000_000 ? 0.005 : 0;
    return 0.1 * withdrawalLocal + wealthRate * capitalAtStartOfYearLocal;
  },
);
