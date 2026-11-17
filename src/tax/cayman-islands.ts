import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "KY", "KYD",
  "The Cayman Islands has no personal income tax.",
  ["tax-ky-pit"],
  () => 0,
);
