import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "AD", "EUR",
  "Andorra exempts gains on sale or redemption of qualifying collective investment fund shares. The estimate assumes a qualifying regulated ETF.",
  ["tax-ad-funds"],
  () => 0,
);
