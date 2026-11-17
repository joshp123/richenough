import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "AO", "AOA",
  "Angola’s investment income tax charges 10% on realised gains on financial instruments. It applies when the recipient is resident in Angola, including gains from foreign securities.",
  ["tax-ao-capital-code","tax-ao-budget-2026"],
  ({ withdrawalLocal }) => withdrawalLocal * 0.10,
);
