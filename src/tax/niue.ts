import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "NU", "NZD",
  "The long-held offshore corporate fund is modeled as a private investment. The sale is assumed not to form part of a dealing business, a purchase made for resale or a profit-making scheme. Section 51 taxes those gains. It also taxes income accumulated on behalf of the investor, which can change the result for a transparent trust.",
  ["tax-nu-income"],
  () => 0,
);
