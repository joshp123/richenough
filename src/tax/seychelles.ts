import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "SC", "SCR",
  "An individual living off a foreign equity fund pays no Seychelles capital gains tax on the sale in this scenario.",
  ["tax-sc-territory","tax-sc-gains"],
  () => 0,
);
