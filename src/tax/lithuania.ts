import { registerStandardTax } from './calculation.ts';

// 2026, private buy-and-hold investor.
registerStandardTax(
  'LT', 'EUR',
  'Lithuania taxes qualifying fund units held more than five years at 15%, after the €500 annual gains allowance per spouse. Eligible investment accounts defer tax on withdrawals up to contributions.',
  ['tax-lt-financial-instruments', 'tax-lt-investment-account'],
  ({ withdrawalLocal }) => Math.max(0, withdrawalLocal - 1_000) * 0.15,
);
