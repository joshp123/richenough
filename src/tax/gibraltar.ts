import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "GI", "GIP",
  "Gibraltar has no capital gains tax on the couple’s ETF sales.",
  ["tax-gi-gains"],
  () => 0,
);
