import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "BN", "BND",
  "Brunei does not impose a personal income tax on individuals.",
  ["tax-bn-pit"],
  () => 0,
);
