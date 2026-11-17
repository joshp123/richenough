import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "MW", "MWK",
  "Malawi taxes capital gains from Malawi sources. Foreign ETF shares held and sold abroad fall outside the securities deemed to be Malawi-source under section 27. The 2026 Malawi Stock Exchange levy applies to local exchange sales.",
  ["tax-mw-taxation","tax-mw-budget-2026"],
  () => 0,
);
