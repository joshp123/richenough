import { registerStandardTax } from './calculation.ts';

// 2026. Private investment in a global equity ETF.
registerStandardTax(
  'SG', 'SGD',
  'Singapore generally exempts gains on the sale of securities held as private investments.',
  ['tax-sg-gains'],
  () => 0,
);
