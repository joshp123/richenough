import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "BB", "BBD",
  "Barbados does not impose capital gains tax.",
  ["tax-bb-gains"],
  () => 0,
);
