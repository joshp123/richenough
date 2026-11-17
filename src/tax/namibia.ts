import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "NA", "NAD",
  "Namibia does not charge tax on this private ETF gain. Special rules cover interests in mineral and petroleum rights.",
  ["tax-na-gains"],
  () => 0,
);
