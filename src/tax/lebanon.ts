import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "LB", "LBP",
  "Private sales of shares in foreign joint-stock companies are exempt. The estimate uses an accumulating listed corporate fund. Foreign dividends, other legal forms and commercial trading can be taxed.",
  ["tax-lb-gains"],
  () => 0,
);
