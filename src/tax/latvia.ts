import { registerStandardTax } from './calculation.ts';

// 2026, private buy-and-hold investor.
registerStandardTax(
  'LV', 'EUR',
  'Latvia charges 25.5% on fund sale gains plus 3% on total income above €200,000 per spouse. Eligible accounts can defer tax until withdrawals exceed deposits.',
  ['tax-lv-gains', 'tax-lv-account'],
  ({ withdrawalLocal }) => withdrawalLocal * 0.255 + Math.max(0, withdrawalLocal - 400_000) * 0.03,
);
