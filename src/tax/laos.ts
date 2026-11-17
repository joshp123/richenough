import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "LA", "LAK",
  "The estimate applies the 2% share-transfer charge to the full sale price of shares in a global corporate ETF. It assumes the 2026 resident worldwide income rule applies the share-transfer rate to offshore shares. Published guidance on offshore ETF sales is limited.",
  ["tax-la-pwc-gains","tax-la-2026-worldwide"],
  ({ withdrawalLocal }) => withdrawalLocal * 0.02,
);
