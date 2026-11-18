import { progressiveTax, registerStandardTax, type TaxBand } from './calculation.ts';

// Calendar 2026, assessed in 2027. Each threshold is expressed in December 2026 UTA.
const uta = 873_624;
const bands: TaxBand[] = [
  [13.5 * uta, 0.04], [30 * uta, 0.08], [50 * uta, 0.135], [70 * uta, 0.23],
  [90 * uta, 0.304], [120 * uta, 0.35], [310 * uta, 0.40],
];

registerStandardTax(
  'CL', 'CLP',
  'Chile taxes non-exempt foreign ETF gains at progressive rates separately for each spouse. The new foreign resident exemption for offshore income lasts three years from entry. The tax authority can extend it in exceptional cases.',
  ['tax-cl-rates', 'tax-cl-uta', 'tax-cl-new-residents'],
  ({ withdrawalLocal }) => 2 * progressiveTax(withdrawalLocal / 2, bands),
);
