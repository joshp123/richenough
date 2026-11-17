import { registerStandardTax } from './calculation.ts';

// 2026, private buy-and-hold investor.
registerStandardTax(
  'IS', 'ISK',
  'Iceland charges 22% on extraordinary gains from listed fund shares after the couple’s combined ISK 600,000 annual capital income allowance.',
  ['tax-is-capital'],
  ({ withdrawalLocal }) => Math.max(0, withdrawalLocal - 600_000) * 0.22,
);
