import { registerStandardTax } from './calculation.ts';

// Wealth Tax Act, articles 3, 7, 11 and 14, confirmed by the 2025 treaty memorandum.
registerStandardTax(
  'SR', 'SRD',
  'A private sale of an accumulating ETF has no separate gains charge. A married household pays 3% a year on net taxable portfolio wealth above SRD 120,000.',
  ['tax-sr-income', 'tax-sr-wealth', 'tax-sr-treaty'],
  ({ capitalAtStartOfYearLocal }) => 0.03 * Math.max(0, capitalAtStartOfYearLocal - 120_000),
);
