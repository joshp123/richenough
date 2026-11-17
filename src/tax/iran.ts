import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "IR", "IRR",
  "The exemption in Article 143 bis, note 3, applies to shares of a listed foreign company sold on a foreign exchange. The model assumes an accumulating equity ETF structured as a listed foreign company. It assumes the couple can lawfully hold and transact through its broker.",
  ["tax-ir-listed-shares"],
  () => 0,
);
