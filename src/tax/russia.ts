import { registerStandardTax, progressiveTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "RU", "RUB",
  "Russia taxes ordinary foreign securities gains at 13% up to RUB 2.4 million per spouse and 15% above that. The relief for certain securities held long-term does not generally cover Irish-domiciled ETF units.",
  ["tax-ru-rate","tax-ru-threshold"],
  ({ withdrawalLocal }) => 2 * progressiveTax(withdrawalLocal / 2, [[0, 0.13], [2_400_000, 0.15]]),
);
