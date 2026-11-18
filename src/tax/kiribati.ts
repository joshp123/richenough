import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "KI", "AUD",
  "Kiribati’s resident return asks for worldwide investment income but does not include gains on non-business asset sales in its investment income categories. The estimate treats sales of long-held offshore ETF units as personal capital disposals. Distributions and trading as a business can be taxable.",
  ["tax-ki-resident-return"],
  () => 0,
);
