import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "PY", "PYG",
  "Paraguay taxes Paraguayan-source capital gains. The estimate uses ETF units issued, held and sold abroad.",
  ["tax-py-source"],
  () => 0,
);
