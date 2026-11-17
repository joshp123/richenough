import { nominalPortfolioReturn, registerStandardTax } from './calculation.ts';

// 2026. Irish-domiciled UCITS ETF. Deemed disposal every eight years updates the cost basis.
registerStandardTax(
  'IE', 'EUR',
  'Ireland taxes gains on an Irish-domiciled ETF at 38%, including gains on a deemed sale every eight years. This estimate annualises tax on the whole portfolio at 7% nominal return. Actual years can have sharply different bills.',
  ['tax-ie-fund-rates', 'tax-ie-etf', 'tax-ie-funds-law'],
  ({ capitalAtStartOfYearLocal }) => capitalAtStartOfYearLocal * nominalPortfolioReturn * 0.38,
);
