import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "VG", "USD",
  "The British Virgin Islands imposes no personal income tax on private ETF sale gains. The payroll tax applies to employment and business earnings.",
  ["tax-vg-oecd","tax-vg-private"],
  () => 0,
);
