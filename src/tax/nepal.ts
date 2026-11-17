import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "NP", "NPR",
  "For 2026–27, private gains from foreign ETF units enter the non-business gains schedule. This models 10% above NPR 1 million per spouse, with separate returns and a lawfully held pre-move portfolio. Nepal restricts new outbound investments by residents.",
  ["tax-np-income-act","tax-np-foreign-exchange"],
  ({ withdrawalLocal }) => Math.max(0, withdrawalLocal - 2_000_000) * 0.10,
);
