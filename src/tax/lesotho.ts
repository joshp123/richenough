import { registerStandardTax, progressiveTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "LS", "LSL",
  "Lesotho taxes residents on worldwide gains from investment assets. For 2026/27 each spouse gets a credit of LSL 12,240, pays 20% on the first LSL 77,760 of taxable income and 30% above that. The exemption for temporary residents on qualifying employment contracts does not fit this couple.",
  ["tax-ls-income","tax-ls-2026-rates"],
  ({ withdrawalLocal }) => 2 * Math.max(0, progressiveTax(withdrawalLocal / 2, [[0, 0.20], [77_760, 0.30]]) - 12_240),
);
