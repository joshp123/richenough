import { progressiveTax, registerStandardTax, type TaxBand } from './calculation.ts';

// Ordinary scale under the 2026 Finance Act, income year 2025 (latest enacted scale).
const incomeBands: TaxBand[] = [
  [11_600, 0.11], [29_579, 0.30], [84_577, 0.41], [181_917, 0.45],
];

registerStandardTax(
  'FR', 'EUR',
  'France taxes ETF gains at 31.4%, including 18.6% social levies. The couple can elect the ordinary income scale if cheaper. Above €24,030 of investment income per spouse, a separate PUMa contribution can apply to residents with French public health cover and no earnings or pension.',
  ['tax-fr-gains', 'tax-fr-brackets', 'tax-fr-high-income', 'tax-fr-csm', 'tax-fr-pass'],
  ({ withdrawalLocal: gain }) => {
    const scale = 2 * progressiveTax(gain / 2, incomeBands);
    const scaleAfterDiscount = Math.max(0, scale - Math.max(0, 1483 - 0.4525 * scale));
    const incomeTax = Math.min(gain * 0.128, scaleAfterDiscount);
    const highIncomeTax = progressiveTax(gain, [[500_000, 0.03], [1_000_000, 0.04]]);
    // A stable reference income above EUR 660k has neither the entry taper nor exceptional-income relief.
    const cdhrTarget = Math.min(0.2 * gain, 0.825 * Math.max(0, gain - 500_000));
    const cdhr = gain > 500_000 ? Math.max(0, cdhrTarget - incomeTax - highIncomeTax - 12_500) : 0;
    const healthContribution = 2 * 0.065 * Math.max(0, Math.min(gain / 2, 384_480) - 24_030);
    return incomeTax + 0.186 * gain + highIncomeTax + cdhr + healthContribution;
  },
);
