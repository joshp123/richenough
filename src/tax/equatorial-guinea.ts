import { registerStandardTax, progressiveTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "GQ", "XAF",
  "Residents are taxed on worldwide income. This estimate applies the individual capital gains brackets, up to 25% per spouse, to the sale of a foreign ETF. The 10% resident withholding on movable capital income is a separate charge on payments.",
  ["tax-gq-tax-law-2024","tax-gq-pit","tax-gq-cgt"],
  ({ withdrawalLocal }) => 2 * progressiveTax(withdrawalLocal / 2, [[0, 0], [1_400_000, 0.10], [5_000_000, 0.15], [10_000_000, 0.20], [15_000_000, 0.25]]),
);
