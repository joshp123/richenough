import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "SZ", "SZL",
  "Eswatini does not impose capital gains tax on private portfolio sales.",
  ["tax-sz-gains"],
  () => 0,
);
