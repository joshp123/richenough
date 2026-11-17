import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "TD", "XAF",
  "Chad’s 2026 Finance Act applies a 20% rate to net capital income, including securities gains. Residents are taxed on worldwide income.",
  ["tax-td-finance-2026"],
  ({ withdrawalLocal }) => withdrawalLocal * 0.20,
);
