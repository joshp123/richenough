import { fundDividendYield, progressiveTax } from './calculation.ts';
import { registerTaxRules } from './tax-rules.ts';

// 2026/27. Half the portfolio per spouse in a foreign fund with HMRC reporting status.
registerTaxRules('GB', {
  currency: 'GBP',
  hasSpecialRegime: true,
  taxOwed: ({ withdrawalLocal, capitalAtStartOfYearLocal }, regime) => {
    if (regime === 'special') {
      return {
        taxLocal: 0,
        regimeName: 'Foreign income and gains (first four tax years)',
        explanation: 'Both spouses claim relief on their foreign ETF gains and income. Each needs ten prior consecutive non-resident tax years. Relief ends after four UK tax years.',
        sourceIds: ['tax-gb-fig'],
      };
    }

    const dividends = fundDividendYield * capitalAtStartOfYearLocal / 2;
    const personalAllowance = Math.max(0, 12_570 - Math.max(0, dividends - 100_000) / 2);
    const taxableIncome = Math.max(0, dividends - personalAllowance);
    // The nil-rate dividend band still occupies basic-rate band space.
    const dividendTax = progressiveTax(taxableIncome, [[500, 0.1075], [37_700, 0.3575], [125_140, 0.3935]]);
    // Allocate part of the spending withdrawal to reportable income already taxed as
    // dividends, to approximate the basis uplift over a mature portfolio's life.
    const gain = Math.max(0, withdrawalLocal / 2 - dividends - 3_000);
    const basicGain = Math.min(gain, Math.max(0, 37_700 - taxableIncome));
    return {
      taxLocal: 2 * (dividendTax + 0.18 * basicGain + 0.24 * (gain - basicGain)),
      regimeName: 'Standard',
      explanation: 'HMRC taxes ETF sale gains at 18% or 24% after each spouse’s £3,000 gains allowance. The estimate also taxes reportable fund income as dividends using an illustrative 1.5% yield and adjusts sale gains for income already taxed.',
      sourceIds: ['tax-gb-gains', 'tax-gb-income', 'tax-gb-fund', 'tax-fund-vanguard'],
    };
  },
});
