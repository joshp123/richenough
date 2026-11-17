import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "VU", "VUV",
  "Vanuatu has no personal income or capital gains tax on the private investment gains in this scenario.",
  ["tax-vu-income"],
  () => 0,
);
