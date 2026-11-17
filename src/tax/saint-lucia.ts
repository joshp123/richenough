import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "LC", "XCD",
  "Saint Lucia does not tax capital gains. The estimate uses an accumulating fund and excludes separate dividends.",
  ["tax-lc-gains"],
  () => 0,
);
