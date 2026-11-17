import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "JE", "GBP",
  "Jersey has no capital gains tax. The estimate uses an accumulating ETF and excludes separate paid or deemed distributions.",
  ["tax-je-gains"],
  () => 0,
);
