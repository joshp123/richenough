import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "ZW", "USD",
  "The capital gains law taxes Zimbabwe-source gains. Sales of a private offshore ETF produce foreign-source gains. The provision that deems foreign investment income to arise in Zimbabwe covers interest and dividends, so the estimate assumes an accumulating fund.",
  ["tax-zw-capital-gains","tax-zw-income-source"],
  () => 0,
);
