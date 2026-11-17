import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "QA", "QAR",
  "Qatar’s territorial system taxes qualifying Qatar-source income. The couple’s gains on a foreign ETF fall outside this base.",
  ["tax-qa-scope"],
  () => 0,
);
