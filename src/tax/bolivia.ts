import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "BO", "BOB",
  "Bolivia does not tax passive gains from foreign ETF sales. Its tax on individuals’ investment income applies to certain Bolivian-source income.",
  ["tax-bo-gains"],
  () => 0,
);
