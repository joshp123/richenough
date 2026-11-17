import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "BI", "BIF",
  "Burundi taxes residents on worldwide income, with a separate 15% rate for capital income and net gains on investments. The 2026–27 Finance Act retains the separate capital income schedule.",
  ["tax-bi-income-2020","tax-bi-budget-2026"],
  ({ withdrawalLocal }) => withdrawalLocal * 0.15,
);
