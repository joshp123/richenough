import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "RW", "RWF",
  "Rwanda taxes securities gains at 10%. This estimate assumes the ETF is held outside the locally recognised collective investment scheme exemption.",
  ["tax-rw-scope","tax-rw-gains","tax-rw-funds"],
  ({ withdrawalLocal }) => withdrawalLocal * 0.10,
);
