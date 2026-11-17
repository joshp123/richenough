import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "PW", "USD",
  "Palau charges tax on wages and on business income. A private portfolio sale through an offshore broker creates neither for this household.",
  ["tax-pw-code","tax-pw-brt"],
  () => 0,
);
