import { registerStandardTax } from './calculation.ts';

// 2026. Private investment in a global equity ETF.
registerStandardTax(
  'TW', 'TWD',
  'Taiwan’s basic income tax includes the full amount of overseas gains once overseas income reaches NT$1 million. The couple files together and pays 20% above the NT$7.5 million basic-income deduction.',
  ['tax-tw-amt', 'tax-tw-foreign-funds'],
  ({ withdrawalLocal }) => Math.max(0, withdrawalLocal - 7_500_000) * 0.20,
);
