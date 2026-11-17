import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "KW", "KWD",
  "Kuwait does not impose a personal income tax on individuals.",
  ["tax-kw-pit"],
  () => 0,
);
