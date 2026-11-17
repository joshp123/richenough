import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "FO", "DKK",
  "The Faroe Islands tax residents’ securities gains at 35%, including sales in foreign accounts.",
  ["tax-fo-gains","tax-fo-rate"],
  ({ withdrawalLocal }) => 0.35 * withdrawalLocal,
);
