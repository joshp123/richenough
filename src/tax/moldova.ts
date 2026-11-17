import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "MD", "MDL",
  "Moldova taxes incoming foreign nationals on Moldovan-source income and foreign income from work performed in Moldova. Gains on their overseas ETF are outside that base. Different worldwide income rules can apply to Moldovan citizens.",
  ["tax-md-scope"],
  () => 0,
);
