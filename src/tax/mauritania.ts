import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "MR", "MRU",
  "The tax on investment income, including private sales of securities, applies to securities of entities subject to Mauritanian company tax. The model assumes a small position in a corporate ETF with no Mauritanian establishment or investments held directly by the couple in Mauritania.",
  ["tax-mr-capital","tax-mr-capital-doctrine"],
  () => 0,
);
