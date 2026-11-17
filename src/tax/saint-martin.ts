import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "MF", "EUR",
  "Saint-Martin taxes securities gains at 16%, with French social levies of 18.6% for residents in the French social system. The local rate assumes the couple was outside mainland France and its overseas departments for the previous five years.",
  ["tax-mf-income","tax-mf-residency","tax-mf-fr-social", "tax-fr-gains"],
  ({ withdrawalLocal }) => withdrawalLocal * (0.16 + 0.186),
);
