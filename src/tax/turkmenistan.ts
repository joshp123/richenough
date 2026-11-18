import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "TM", "TMT",
  "Resident individuals pay 10% on worldwide gains from selling securities after acquisition costs. A monthly TMT 50 deduction per spouse gives an annual household allowance of TMT 1,200. The tax uses the official exchange rate.",
  ["tax-tm-tax-code","tax-tm-standard-deduction"],
  ({ withdrawalLocal }) => 2 * Math.round(0.10 * Math.max(0, withdrawalLocal / 2 - 600)),
);
