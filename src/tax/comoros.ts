import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "KM", "KMF",
  "The capital gains provision covers shares of companies under Comorian law, including gains received abroad. This estimate uses shares of a foreign corporate accumulation fund held abroad and assumes any required exchange-control permissions. Foreign dividends have separate rules.",
  ["tax-km-code","tax-km-exchange"],
  () => 0,
);
