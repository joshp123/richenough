import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "VC", "XCD",
  "Saint Vincent and the Grenadines taxes investment income such as interest and dividends. It has no separate levy on private ETF sale gains. This estimate uses an accumulating foreign ETF.",
  ["tax-vc-income","tax-vc-overview","tax-vc-capital"],
  () => 0,
);
