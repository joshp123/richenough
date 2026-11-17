import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "MH", "USD",
  "There is no personal tax on gains from selling private ETF shares. The 2026 income-tax amendment applies to wages and salaries.",
  ["tax-mh-income-act","tax-mh-2026-act","tax-mh-imf"],
  () => 0,
);
