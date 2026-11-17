import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "FK", "FKP",
  "The Falkland Islands do not levy a general capital gains tax or a wealth tax. This assumes sales from a private accumulating ETF, with no separately paid interest or dividends.",
  ["tax-fk-guide"],
  () => 0,
);
