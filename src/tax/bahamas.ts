import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "BS", "BSD",
  "The Bahamas has no personal income tax.",
  ["tax-bs-pit"],
  () => 0,
);
