import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "JM", "JMD",
  "Jamaica has no capital gains tax. The estimate uses ETF units sold abroad, outside Jamaica’s transfer tax.",
  ["tax-jm-gains"],
  () => 0,
);
