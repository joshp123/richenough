import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "BY", "BYN",
  "Belarus taxes gains on securities held through a foreign broker at 13%.",
  ["tax-by-gains","tax-by-2026"],
  ({ withdrawalLocal }) => 0.13 * withdrawalLocal,
);
