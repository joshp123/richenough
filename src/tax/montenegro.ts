import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "ME", "EUR",
  "Montenegro taxes securities gains at 15%. Its municipal surtax applies to specified income categories, such as dividends and other capital income.",
  ["tax-me-gains","tax-me-local"],
  ({ withdrawalLocal }) => 0.15 * withdrawalLocal,
);
