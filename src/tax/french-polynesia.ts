import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "PF", "XPF",
  "French Polynesia’s personal taxes do not assess private gains from selling an offshore accumulating ETF. This assumes the sales are private investments and the couple are taxed as established Polynesian residents.",
  ["tax-pf-income-system","tax-pf-private-income"],
  () => 0,
);
