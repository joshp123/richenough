import { registerStandardTax, progressiveTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "SS", "SSP",
  "The Taxation Act includes a resident’s worldwide capital gains in personal income. This estimate annualizes the individual 2024/25 income bands in the latest signed Finance Act I could verify. Its published table is headed wages and I could not confirm a separate assessment scale for private foreign securities.",
  ["tax-ss-taxation-act","tax-ss-finance-act"],
  ({ withdrawalLocal }) => 2 * progressiveTax(withdrawalLocal / 2, [[0, 0], [240_000, 0.05], [480_000, 0.10], [684_000, 0.15], [1_080_000, 0.20]]),
);
