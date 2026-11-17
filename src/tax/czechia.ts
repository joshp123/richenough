import { registerStandardTax } from './calculation.ts';

// 2026, private buy-and-hold investor.
registerStandardTax(
  'CZ', 'CZK',
  'The Czech Republic exempts gains on securities held for more than three years. From 2026 the former CZK 40 million cap no longer applies to qualifying securities.',
  ['tax-cz-time-test', 'tax-cz-gains'],
  () => 0,
);
