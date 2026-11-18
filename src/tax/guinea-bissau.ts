import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "GW", "XOF",
  "The capital income code includes securities gains, but applies only to capital invested in Guinea-Bissau and payable by a person with a local home, seat or relevant permanent establishment. Selling a foreign ETF through a foreign broker produces no Guinea-Bissau tax in this model.",
  ["tax-gw-capital-code"],
  () => 0,
);
