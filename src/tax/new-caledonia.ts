import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "NC", "XPF",
  "New Caledonia’s personal tax code taxes investment distributions and has a separate tax on private real estate gains. A private investor’s sale of shares in a foreign accumulating ETF is outside those categories and the associated solidarity levy.",
  ["tax-nc-code","tax-nc-solidarity"],
  () => 0,
);
