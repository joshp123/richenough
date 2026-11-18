import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "SY", "SYP",
  "The existing Syrian income tax is territorial. The estimate assumes long-held ETF shares issued overseas, sold through an overseas broker, with no Syrian activity or issuer. The government announced a draft replacement tax framework for 2027.",
  ["tax-sy-income-tax","tax-sy-territorial","tax-sy-tax-reform"],
  () => 0,
);
