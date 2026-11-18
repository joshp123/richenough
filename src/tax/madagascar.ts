import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "MG", "MGA",
  "Residents are taxed at 20% on private securities gains under the capital income tax. The estimate treats shares in a foreign corporate ETF as securities and rounds each spouse’s gain down to the nearest MGA 1,000.",
  ["tax-mg-finance-2026","tax-mg-finance-2026-amendment"],
  ({ withdrawalLocal }) => 0.40 * Math.floor(withdrawalLocal / 2_000) * 1_000,
);
