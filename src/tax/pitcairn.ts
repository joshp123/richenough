import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "PN", "NZD",
  "Pitcairn has no personal income tax. The couple must qualify for settlement separately.",
  ["tax-pn-economic-report","tax-pn-laws","tax-pn-settlement"],
  () => 0,
);
