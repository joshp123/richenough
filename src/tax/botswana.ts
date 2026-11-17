import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "BW", "BWP",
  "Botswana taxes an incoming foreign national on Botswana-source income. The estimate uses gains from a foreign investment.",
  ["tax-bw-source","tax-bw-gains"],
  () => 0,
);
