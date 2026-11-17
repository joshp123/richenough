import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "HN", "HNL",
  "Honduras taxes Honduran-source gains. Gains on the couple’s offshore fund are outside the tax base.",
  ["tax-hn-source"],
  () => 0,
);
