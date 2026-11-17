import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "CM", "XAF",
  "Cameroon’s securities gains tax applies to direct or indirect disposals of Cameroonian company interests. This estimate uses an offshore accumulating global ETF with no Cameroonian business interest.",
  ["tax-cm-gains","tax-cm-code"],
  () => 0,
);
