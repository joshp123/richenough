import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "IQ", "IQD",
  "Article 5 excludes foreign-source income for resident non-Iraqis. This assumes both spouses are foreign citizens and keep their ETF sale proceeds in offshore accounts.",
  ["tax-iq-income-law","tax-iq-pwc"],
  () => 0,
);
