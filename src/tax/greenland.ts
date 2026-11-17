import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "GL", "DKK",
  "Greenland exempts private capital gains on fund units. Its tax on gains from certain financial contracts and debentures does not apply to these ETF sales.",
  ["tax-gl-gains"],
  () => 0,
);
