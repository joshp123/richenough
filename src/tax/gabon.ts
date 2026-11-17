import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "GA", "XAF",
  "The personal capital-gains charge is 20% after the annual 15% allowance, giving 17% of the net gain. This uses the general rules for private portfolio assets. A substantial management holding has a separate calculation.",
  ["tax-ga-code","tax-ga-dgi"],
  ({ withdrawalLocal }) => withdrawalLocal * 0.85 * 0.20,
);
