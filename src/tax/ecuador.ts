import { registerStandardTax, progressiveTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "EC", "USD",
  "Ecuador taxes gains on a foreign ETF as foreign income at the individual scale, before deductions for personal expenditure. The couple splits the proceeds equally.",
  ["tax-ec-scope","tax-ec-gains"],
  ({ withdrawalLocal }) => 2 * progressiveTax(withdrawalLocal / 2, [[12_208, 0.05], [15_549, 0.10], [20_188, 0.12], [26_700, 0.15], [35_136, 0.20], [46_575, 0.25], [62_005, 0.30], [82_679, 0.35], [109_956, 0.37]]),
);
