import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "MS", "XCD",
  "Montserrat taxes specified income and has no general capital gains tax. This assumes private sales of an accumulating ETF, with no separately paid dividends or share-dealing business.",
  ["tax-ms-income-law","tax-ms-investmontserrat"],
  () => 0,
);
