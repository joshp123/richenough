import { registerStandardTax, progressiveTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "LR", "LRD",
  "Residents include worldwide gains from disposing of investment assets in ordinary taxable income. The model splits gains equally and applies each spouse’s 2026 personal income tax bands.",
  ["tax-lr-code","tax-lr-rates"],
  ({ withdrawalLocal }) => 2 * progressiveTax(withdrawalLocal / 2, [[70_000, 0.05], [200_000, 0.15], [800_000, 0.25]]),
);
