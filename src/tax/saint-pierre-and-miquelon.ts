import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "PM", "EUR",
  "Saint-Pierre and Miquelon charges 19% on gains from foreign shares. Its 11% rate is for shares or interests in businesses headquartered in the archipelago.",
  ["tax-pm-cli-2026","tax-pm-return-guidance"],
  ({ withdrawalLocal }) => withdrawalLocal * 0.19,
);
