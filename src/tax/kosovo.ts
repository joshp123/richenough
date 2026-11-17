import { registerStandardTax, progressiveTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "XK", "EUR",
  "Kosovo taxes capital gains from securities at progressive rates of up to 10%. The estimate gives the two spouses separate bands.",
  ["tax-xk-gains","tax-xk-rates"],
  ({ withdrawalLocal }) => 2 * progressiveTax(withdrawalLocal / 2, [[3_000, 0.08], [5_400, 0.10]]),
);
