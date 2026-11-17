import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "WS", "WST",
  "Samoa excludes gains on foreign assets acquired before becoming resident. This estimate assumes the couple continues to sell the foreign ETF units it already held on arrival.",
  ["tax-ws-gains"],
  () => 0,
);
