import { registerStandardTax, progressiveTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "CU", "CUP",
  "For permanent residents Cuba taxes income from worldwide sales of property and rights. The estimate treats regular foreign ETF sales as taxable gains and applies the annual CUP 39,120 allowance and the ordinary 15% to 50% scale to each spouse. Temporary residence has a different source rule. Cuba has several exchange rates, and the estimated bill depends on the rate used to value the gains.",
  ["tax-cu-tax-system-2026","tax-cu-currency-resolution"],
  ({ withdrawalLocal }) => 2 * progressiveTax(Math.max(0, withdrawalLocal / 2 - 39_120), [[0, 0.15], [10_000, 0.20], [20_000, 0.30], [30_000, 0.40], [50_000, 0.50]]),
);
