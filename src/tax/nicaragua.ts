import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "NI", "NIO",
  "Nicaragua taxes Nicaraguan-source income. Gains on the couple’s offshore fund are outside the tax base.",
  ["tax-ni-source"],
  () => 0,
);
