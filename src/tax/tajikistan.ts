import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "TJ", "TJS",
  "Resident private gains on the sale of shares in a foreign ETF company are taxed at 15%. The exemption for selling ordinary movable property excludes shares.",
  ["tax-tj-code","tax-tj-code-current"],
  ({ withdrawalLocal }) => withdrawalLocal * 0.15,
);
