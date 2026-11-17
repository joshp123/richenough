import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "KG", "KGS",
  "Gains on securities listed on a Cabinet-approved foreign exchange are exempt. This assumes the accumulating global ETF is listed on one of those exchanges, such as the London Stock Exchange.",
  ["tax-kg-code","tax-kg-exchanges","tax-kg-exchanges-london","tax-kg-london-fund"],
  () => 0,
);
