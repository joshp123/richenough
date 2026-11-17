import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "GT", "GTQ",
  "Guatemala taxes locally sourced capital gains. Foreign investment gains are outside the tax base.",
  ["tax-gt-gains"],
  () => 0,
);
