import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "BM", "BMD",
  "Bermuda has no personal income tax on passive investors.",
  ["tax-bm-pit"],
  () => 0,
);
