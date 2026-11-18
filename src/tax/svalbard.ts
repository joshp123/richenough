import { progressiveTax, registerStandardTax } from './calculation.ts';

// 2026. The combined map code uses Svalbard's resident rules.
registerStandardTax(
  'SJ', 'NOK',
  'Svalbard taxes equity ETF gains at 16% after multiplying them by 1.72 and deducting NOK 20,000 per spouse. Net wealth tax uses 80% of the equity fund value. Newcomers without Norwegian tax residence in the previous ten years can have limited tax liability for the first five years. Jan Mayen has no tax residence regime.',
  ['tax-sj-rates', 'tax-sj-residents', 'tax-no-shares', 'tax-no-wealth', 'tax-sj-jan-mayen'],
  ({ withdrawalLocal, capitalAtStartOfYearLocal }) => {
    const incomeTax = 0.16 * Math.max(0, withdrawalLocal * 1.72 - 40_000);
    const wealthTax = progressiveTax(0.8 * capitalAtStartOfYearLocal, [[3_800_000, 0.01], [43_000_000, 0.011]]);
    return incomeTax + wealthTax;
  },
);
