import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "SL", "SLE",
  "Sierra Leone’s capital gains rules cover locally issued shares and foreign companies deriving at least 20% of sales in or from Sierra Leone. An offshore global ETF with no such exposure falls outside that definition. This treatment concerns sale gains.",
  ["tax-sl-income-act","tax-sl-finance-2021","tax-sl-finance-2026"],
  () => 0,
);
