import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "AL", "ALL",
  "Albania taxes gains on sales of securities at 15%.",
  ["tax-al-gains"],
  ({ withdrawalLocal }) => 0.15 * withdrawalLocal,
);
