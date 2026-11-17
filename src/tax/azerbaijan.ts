import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "AZ", "AZN",
  "Azerbaijan taxes gains from publicly offered shares on regulated local or foreign markets at 14% after acquisition costs and expenses. The estimate treats the listed foreign ETF as an eligible share.",
  ["tax-az-code","tax-az-securities"],
  ({ withdrawalLocal }) => 0.14 * withdrawalLocal,
);
