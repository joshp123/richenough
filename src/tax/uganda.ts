import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "UG", "UGX",
  "Uganda exempts non-business capital gains other than gains on shares of a private limited company. This estimate uses a publicly traded foreign ETF.",
  ["tax-ug-gains"],
  () => 0,
);
