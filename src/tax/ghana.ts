import { registerStandardTax, progressiveTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "GH", "GHS",
  "Ghana includes foreign investment gains in ordinary income. The couple can elect the separate 25% rate when cheaper.",
  ["tax-gh-rates","tax-gh-election"],
  ({ withdrawalLocal }) => Math.min(0.25 * withdrawalLocal, 2 * progressiveTax(withdrawalLocal / 2, [[7_056, 0.05], [8_016, 0.10], [9_216, 0.175], [44_016, 0.25], [236_016, 0.30], [600_000, 0.35]])),
);
