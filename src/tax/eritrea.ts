import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "ER", "ERN",
  "The Eritrean income tax schedules do not charge a non-Eritrean resident on a private sale of foreign securities in this model. The estimate assumes the couple does not trade as a business. The 2% levy on Eritreans abroad is a separate rule.",
  ["tax-er-income","tax-er-income-review"],
  () => 0,
);
