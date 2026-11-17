import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "TL", "USD",
  "The income tax law applies to residents’ worldwide income, but excludes gains from assets held on personal account. This assumes private buy-and-hold ETF shares.",
  ["tax-tl-act"],
  () => 0,
);
