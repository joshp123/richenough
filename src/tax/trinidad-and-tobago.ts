import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "TT", "TTD",
  "Trinidad and Tobago excludes capital gains on assets held more than a year and foreign gains of a resident foreign national.",
  ["tax-tt-gains"],
  () => 0,
);
