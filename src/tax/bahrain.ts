import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "BH", "BHD",
  "Bahrain imposes no personal income tax. Foreign investment gains have no local income tax or social insurance charge in this scenario.",
  ["tax-bh-pit"],
  () => 0,
);
