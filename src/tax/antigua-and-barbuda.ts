import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "AG", "XCD",
  "Antigua and Barbuda abolished personal income tax in 2016. The modeled private fund gains are outside local income and capital gains taxes.",
  ["tax-ag-abolition","tax-ag-capital"],
  () => 0,
);
