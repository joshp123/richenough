import { progressiveTax, registerStandardTax, type TaxBand } from './calculation.ts';

// 2026. Each spouse applies Finland’s 40% deemed cost to fund units held at least ten years.
const bands: TaxBand[] = [[0, 0.30], [30_000, 0.34]];

registerStandardTax(
  'FI', 'EUR',
  'Finland taxes fund sale gains at 30% up to €30,000 of gain per spouse and 34% above that. For mature units held at least ten years, each spouse can subtract a deemed acquisition cost of 40% of proceeds.',
  ['tax-fi-accumulating'],
  ({ withdrawalLocal }) => 2 * progressiveTax(0.60 * withdrawalLocal / 2, bands),
);
