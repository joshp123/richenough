import { registerStandardTax } from './calculation.ts';

// 2026, private buy-and-hold investor.
registerStandardTax(
  'EE', 'EUR',
  'Estonia taxes net gains from listed ETF sales at 22%. Each spouse can use the €8,400 annual basic exemption in 2026. Investment accounts can defer tax until withdrawals exceed deposits.',
  ['tax-ee-rates', 'tax-ee-securities'],
  ({ withdrawalLocal }) => Math.max(0, withdrawalLocal - 16_800) * 0.22,
);
