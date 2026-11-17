import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "ZM", "ZMW",
  "Zambia does not levy a general capital gains tax. The estimate sells foreign ETF units outside Zambia’s property transfer tax.",
  ["tax-zm-gains"],
  () => 0,
);
