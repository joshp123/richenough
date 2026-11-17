import { registerStandardTax } from './calculation.ts';

// 2026: 6 April 2026 financial assets gains law and 30 May 2026 Programme Law.
// Assume one securities account per spouse, a foreign-domiciled accumulating UCITS
// without Belgian distribution registration, and one sale per spouse per month.
registerStandardTax(
  'BE', 'EUR',
  'Belgium taxes financial gains above €10,000 per person at 10% from 2026 and levies 0.30% on each assumed single-owner securities account over €1 million, subject to the threshold cap. This estimate includes 0.12% stock exchange tax on a foreign ETF without Belgian registration.',
  ['tax-be-gains', 'tax-be-capital', 'tax-be-transactions'],
  ({ withdrawalLocal, capitalAtStartOfYearLocal }) => {
    const account = capitalAtStartOfYearLocal / 2;
    const accountTax = Math.min(account * 0.003, Math.max(0, account - 1_000_000) * 0.10);
    const gainTax = Math.max(0, withdrawalLocal / 2 - 10_000) * 0.10;
    const monthlyTransactionTax = Math.min(1300, withdrawalLocal / 24 * 0.0012);
    return 2 * (accountTax + gainTax + 12 * monthlyTransactionTax);
  },
);
