import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "NR", "AUD",
  "Employment, services and active business are taxed. Selling an offshore ETF as a private investor does not give rise to taxable business income.",
  ["tax-nr-tax-office"],
  () => 0,
);
