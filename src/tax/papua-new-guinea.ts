import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "PG", "PGK",
  "Papua New Guinea has no general capital gains tax. The estimate assumes passive ETF sales outside a trading business or profit-making scheme.",
  ["tax-pg-gains"],
  () => 0,
);
