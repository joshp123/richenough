import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "SH", "SHP",
  "Saint Helena taxes locally sourced income. This assumes private sales of a foreign ETF, with no income from Saint Helena assets or businesses.",
  ["tax-sh-income","tax-sh-guide"],
  () => 0,
);
