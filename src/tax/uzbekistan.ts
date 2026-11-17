import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "UZ", "UZS",
  "Uzbekistan applies its 12% individual rate to taxable foreign investment gains.",
  ["tax-uz-gains","tax-uz-rates"],
  ({ withdrawalLocal }) => 0.12 * withdrawalLocal,
);
