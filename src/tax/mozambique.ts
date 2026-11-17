import { registerStandardTax, progressiveTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "MZ", "MZN",
  "Mozambique includes 55% of securities gains on shares held more than five years in tax, at progressive rates of 10% to 32%. The estimate uses that holding period for the mature fund.",
  ["tax-mz-gains","tax-mz-rates"],
  ({ withdrawalLocal }) => 2 * progressiveTax(0.55 * withdrawalLocal / 2, [[0, 0.10], [42_000, 0.15], [168_000, 0.20], [504_000, 0.25], [1_512_000, 0.32]]),
);
