import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "SV", "USD",
  "El Salvador taxes local-source income. Gains on the couple’s offshore fund are outside the tax base.",
  ["tax-sv-source"],
  () => 0,
);
