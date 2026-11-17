import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "LY", "LYD",
  "Libya exempts income earned abroad under Income Tax Law No. 7 of 2010, article 33(10). The model assumes a foreign ETF held and sold abroad.",
  ["tax-ly-income-law","tax-ly-pwc-individual"],
  () => 0,
);
