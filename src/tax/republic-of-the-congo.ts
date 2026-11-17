import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "CG", "XAF",
  "The 2026 Finance Law taxes resident individuals’ worldwide securities gains at 15% under the investment income schedule. The gain is sale proceeds less acquisition cost.",
  ["tax-cg-finance-2026"],
  ({ withdrawalLocal }) => withdrawalLocal * 0.15,
);
