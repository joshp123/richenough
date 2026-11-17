import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "TV", "AUD",
  "The income tax excludes amounts of a capital nature other than specified receipts such as disposal of business revenue assets. The model assumes private long-term holdings of offshore ETF shares.",
  ["tax-tv-income-act"],
  () => 0,
);
