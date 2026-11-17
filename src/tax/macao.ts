import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "MO", "MOP",
  "Macao exempts individual capital gains and foreign investment income.",
  ["tax-mo-gains"],
  () => 0,
);
