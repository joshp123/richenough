import { registerStandardTax } from './calculation.ts';

// 2026, private buy-and-hold investor.
registerStandardTax(
  'SK', 'EUR',
  'Slovakia exempts private ETF gains when the securities have been held and admitted to trading on a qualifying regulated market for more than one year.',
  ['tax-sk-securities'],
  () => 0,
);
