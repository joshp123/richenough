import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "CK", "NZD",
  "The Cook Islands generally does not tax private capital gains. This assumes the ETF was acquired as a long-term investment. A purchase for resale or a dealing business can bring sale gains into taxable income.",
  ["tax-ck-act","tax-ck-oecd"],
  () => 0,
);
