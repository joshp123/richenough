import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "MM", "MMK",
  "Myanmar taxes residents’ worldwide capital gains at 10%.",
  ["tax-mm-gains","tax-mm-world"],
  ({ withdrawalLocal }) => 0.10 * withdrawalLocal,
);
