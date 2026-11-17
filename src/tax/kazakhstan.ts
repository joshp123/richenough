import { registerStandardTax, progressiveTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "KZ", "KZT",
  "Kazakhstan taxes taxable foreign securities gains at 10% up to KZT 36,762,500 per spouse and 15% above that.",
  ["tax-kz-gains"],
  ({ withdrawalLocal }) => 2 * progressiveTax(withdrawalLocal / 2, [[0, 0.10], [36_762_500, 0.15]]),
);
