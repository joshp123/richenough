import { registerStandardTax } from './calculation.ts';

// Article 150-0 A threshold for the 2025 return, the latest published local amount.
const proceedsThreshold = 30_597;

registerStandardTax(
  'MF', 'EUR',
  'Saint-Martin taxes securities gains at 16% once annual sale proceeds exceed €30,597. French social levies of 18.6% also apply to residents in the French social system. The local rate assumes the couple was outside mainland France and its overseas departments for the previous five years.',
  ['tax-mf-income', 'tax-mf-residency', 'tax-mf-fr-social', 'tax-fr-gains'],
  ({ withdrawalLocal }) => withdrawalLocal * (0.186 + (withdrawalLocal > proceedsThreshold ? 0.16 : 0)),
);
