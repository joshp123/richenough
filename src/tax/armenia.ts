import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "AM", "AMD",
  "Armenia excludes proceeds from sales of securities representing participation in qualifying investment funds from the personal tax base.",
  ["tax-am-gains"],
  () => 0,
);
