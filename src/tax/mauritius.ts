import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "MU", "MUR",
  "Mauritius exempts gains from private sales of securities and units, including foreign investments. Dividends from foreign investments received in Mauritius can be subject to tax, so this estimate uses an accumulating ETF.",
  ["tax-mu-gains"],
  () => 0,
);
