import { registerStandardTax } from './calculation.ts';

// 2026, private buy-and-hold investor.
registerStandardTax(
  'PL', 'PLN',
  'Poland taxes private ETF gains at 19%. A further 4% solidarity levy applies to the portion above PLN 1 million of eligible income per spouse.',
  ['tax-pl-etfs', 'tax-pl-pit'],
  ({ withdrawalLocal }) => withdrawalLocal * 0.19 + Math.max(0, withdrawalLocal - 2_000_000) * 0.04,
);
