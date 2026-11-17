import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "BJ", "XOF",
  "The tax on realized securities gains is 5% for individuals selling shares. This assumes shares of a foreign corporate ETF. The recipient self-assesses gains received from abroad.",
  ["tax-bj-code"],
  ({ withdrawalLocal }) => withdrawalLocal * 0.05,
);
