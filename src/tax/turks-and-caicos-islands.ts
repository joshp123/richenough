import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "TC", "USD",
  "The Turks and Caicos Islands have no personal income or capital gains tax on the private investment gains in this scenario.",
  ["tax-tc-income","tax-tc-budget"],
  () => 0,
);
