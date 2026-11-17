import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "AW", "AWG",
  "Private sale gains are outside the income-tax base for a small stake in a widely held ETF. Aruba taxes gains on a substantial interest, generally 25% or more of a company’s share capital. The model assumes an accumulating ETF with no cash distributions.",
  ["tax-aw-income-ordinance","tax-aw-tax-return","tax-aw-bdo"],
  () => 0,
);
