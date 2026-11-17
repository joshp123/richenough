import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "GD", "XCD",
  "Grenada does not tax private capital gains. This estimate uses gains on disposing of a foreign accumulating ETF.",
  ["tax-gd-income","tax-gd-pkf"],
  () => 0,
);
