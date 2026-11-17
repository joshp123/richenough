import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "MC", "EUR",
  "Monaco has no individual income or wealth tax. French nationals who move to Monaco are generally still subject to French income tax under the bilateral convention.",
  ["tax-mc-individual"],
  () => 0,
);
