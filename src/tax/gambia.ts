import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "GM", "GMD",
  "Resident gains on offshore shares fall within the capital-gains tax. Above GMD 24,000 per disposal, individuals pay the higher of 15% of gain or 5% of sale proceeds. For mature holdings the gain approximates proceeds, so 15% applies. Assumes one annual sale per spouse.",
  ["tax-gm-cgt"],
  ({ withdrawalLocal }) => withdrawalLocal / 2 <= 24_000 ? 0 : withdrawalLocal * 0.15,
);
