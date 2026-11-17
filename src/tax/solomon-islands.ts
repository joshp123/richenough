import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "SB", "SBD",
  "Residents report income worldwide. The income tax covers trading profits, dividends, interest and certain mining-rights disposals. The model treats gains from selling privately held offshore ETF shares as capital receipts.",
  ["tax-sb-income-act"],
  () => 0,
);
