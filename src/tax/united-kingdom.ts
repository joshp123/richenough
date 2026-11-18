import { fundDividendYield, nominalPortfolioReturn, progressiveTax } from './calculation.ts';
import { registerTaxRules } from './tax-rules.ts';

// 2026/27. Half the portfolio per spouse in a foreign fund with HMRC reporting status.
registerTaxRules('GB', {
  currency: 'GBP',
  hasSpecialRegime: false,
  taxOwed: ({ withdrawalLocal, capitalAtStartOfYearLocal }) => {
    const dividends = fundDividendYield * capitalAtStartOfYearLocal / 2;
    const personalAllowance = Math.max(0, 12_570 - Math.max(0, dividends - 100_000) / 2);
    const taxableIncome = Math.max(0, dividends - personalAllowance);
    // The nil-rate dividend band still occupies basic-rate band space.
    const dividendTax = progressiveTax(taxableIncome, [[500, 0.1075], [37_700, 0.3575], [125_140, 0.3935]]);
    // Allocate part of the spending withdrawal to reportable income already taxed as
    // dividends, to approximate the basis uplift over a mature portfolio's life.
    const gainShare = 1 - fundDividendYield / nominalPortfolioReturn;
    const gain = Math.max(0, withdrawalLocal * gainShare / 2 - 3_000);
    const basicGain = Math.min(gain, Math.max(0, 37_700 - taxableIncome));
    return {
      taxLocal: 2 * (dividendTax + 0.18 * basicGain + 0.24 * (gain - basicGain)),
      regimeName: 'Standard',
      explanation: 'HMRC taxes ETF sale gains at 18% or 24% after each spouse’s £3,000 gains allowance. The estimate also taxes reportable fund income as dividends using an illustrative 1.5% yield and adjusts sale gains for income already taxed. The Foreign Income and Gains regime can cover the first four UK tax years after ten consecutive years abroad.',
      sourceIds: ['tax-gb-gains', 'tax-gb-examples', 'tax-gb-income', 'tax-gb-fund', 'tax-fund-vanguard', 'tax-gb-fig'],
    };
  },
});
