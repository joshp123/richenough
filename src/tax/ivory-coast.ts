import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "CI", "XOF",
  "Article 180 charges securities income tax on gains from direct share transfers without an intermediary. This estimate assumes listed accumulating ETF shares are sold on exchange through a broker. Direct share sales and fund distributions have different rules.",
  ["tax-ci-cgi-equity","tax-ci-pwc-gains"],
  () => 0,
);
