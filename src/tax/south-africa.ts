import { progressiveTax, registerStandardTax, type TaxBand } from './calculation.ts';

// Tax year 2027 (March 2026 through February 2027).
const bands: TaxBand[] = [
  [0, 0.18], [245_100, 0.26], [383_100, 0.31], [530_200, 0.36],
  [695_800, 0.39], [887_000, 0.41], [1_878_600, 0.45],
];

registerStandardTax(
  'ZA', 'ZAR',
  'South Africa excludes the first R50,000 of capital gains per spouse and taxes 40% of the rest at ordinary rates, after each spouse’s personal rebate. The estimate reflects a mature portfolio after entry-value adjustments have washed out.',
  ['tax-za-cgt', 'tax-za-income'],
  ({ withdrawalLocal }) => {
    const taxableGain = 0.4 * Math.max(0, withdrawalLocal / 2 - 50_000);
    return 2 * Math.max(0, progressiveTax(taxableGain, bands) - 17_820);
  },
);
