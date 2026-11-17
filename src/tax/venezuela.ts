import { registerStandardTax, progressiveTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "VE", "VES",
  "Foreign ETF sale gains enter the resident household’s joint income tax schedule at rates from 6% to 34%. This uses VES 43 per tax unit and assumes the couple has ordinary taxpayer status. A separate 0.25% net wealth tax can apply to designated taxpayers with at least VES 6.45 billion each.",
  ["tax-ve-income-law","tax-ve-tax-unit","tax-ve-wealth"],
  ({ withdrawalLocal }) => Math.max(0, 43 * (progressiveTax(withdrawalLocal / 43 - 774, [[0, 0.06], [1_000, 0.09], [1_500, 0.12], [2_000, 0.16], [2_500, 0.20], [3_000, 0.24], [4_000, 0.29], [6_000, 0.34]]) - 20)),
);
