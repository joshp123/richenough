import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "GN", "GNF",
  "Guinea’s income tax code taxes residents’ worldwide income. Shares are financial capital and gains on their sale paid from abroad are included at 15%. This assumes an ordinary stake in a corporate offshore fund.",
  ["tax-gn-income-code"],
  ({ withdrawalLocal }) => withdrawalLocal * 0.15,
);
