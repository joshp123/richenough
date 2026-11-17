import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "HK", "HKD",
  "Hong Kong exempts capital gains on long-held ETF shares in a private portfolio. Investment dealing as a business has different rules.",
  ["tax-hk-ird"],
  () => 0,
);
