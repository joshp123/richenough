import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "TV", "AUD",
  "Tuvalu’s Income Tax Act excludes private capital gains from gross income. This estimate assumes a personal holding and sales of an accumulating ETF.",
  ["tax-tv-income","tax-tv-amendments"],
  () => 0,
);
