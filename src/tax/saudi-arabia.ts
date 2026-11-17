import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "SA", "SAR",
  "Saudi Arabia has no individual income tax scheme on these gains. This estimate assumes passive holdings outside a Saudi business or other taxable entity.",
  ["tax-sa-pit"],
  () => 0,
);
