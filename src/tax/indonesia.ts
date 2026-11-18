import { progressiveTax, registerStandardTax, type TaxBand } from './calculation.ts';

// 2026. The joint allowance includes both spouses and the marriage allowance.
const bands: TaxBand[] = [
  [0, 0.05], [60_000_000, 0.15], [250_000_000, 0.25], [500_000_000, 0.30], [5_000_000_000, 0.35],
];

registerStandardTax(
  'ID', 'IDR',
  'Indonesia generally taxes residents’ foreign gains at progressive rates. This assumes joint taxation and two personal allowances. The four-year foreign income exemption requires qualifying professional expertise.',
  ['tax-id-law', 'tax-id-allowance', 'tax-id-income'],
  ({ withdrawalLocal }) => progressiveTax(Math.floor((withdrawalLocal - 112_500_000) / 1_000) * 1_000, bands),
);
