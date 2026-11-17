import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "MN", "MNT",
  "Mongolia taxes net gains from selling securities at 10%.",
  ["tax-mn-gains"],
  ({ withdrawalLocal }) => 0.10 * withdrawalLocal,
);
