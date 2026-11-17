import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "TO", "TOP",
  "Tonga taxes property income such as dividends and gains on business assets. This estimate assumes the couple sells units in an accumulating ETF held as a private investment.",
  ["tax-to-income","tax-to-amendments"],
  () => 0,
);
