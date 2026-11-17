import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "GG", "GBP",
  "Guernsey has no capital gains tax. The estimate uses an accumulating ETF and excludes separate paid or deemed distributions.",
  ["tax-gg-gains"],
  () => 0,
);
