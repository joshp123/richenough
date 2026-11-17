import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "DZ", "DZD",
  "Algeria charges 15% on gains from sale of securities. This assumes an ETF structured as company shares, which qualify for the wealth tax exclusion. The 5% reinvestment rate requires reinvesting the gain, so it does not apply to sales used for spending.",
  ["tax-dz-gains","tax-dz-2026","tax-dz-wealth"],
  ({ withdrawalLocal }) => withdrawalLocal * 0.15,
);
