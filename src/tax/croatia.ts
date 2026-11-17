import { registerStandardTax } from './calculation.ts';

// 2026, private buy-and-hold investor.
registerStandardTax(
  'HR', 'EUR',
  'Croatia exempts capital gains on private ETF units sold more than two years after purchase.',
  ['tax-hr-income', 'tax-hr-funds'],
  () => 0,
);
