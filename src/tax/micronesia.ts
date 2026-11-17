import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "FM", "USD",
  "The personal tax is a tax on wages and salaries. Proceeds from selling private offshore ETF shares fall outside the national wage and business taxes.",
  ["tax-fm-tax-booklet"],
  () => 0,
);
