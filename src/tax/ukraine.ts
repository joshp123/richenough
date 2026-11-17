import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "UA", "UAH",
  "Ukraine taxes foreign investment gains at 18% with a 5% military levy in the current tax year.",
  ["tax-ua-gains","tax-ua-rates"],
  ({ withdrawalLocal }) => 0.23 * withdrawalLocal,
);
