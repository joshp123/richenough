import { progressiveTax, registerStandardTax, type TaxBand } from './calculation.ts';

// 2026. Each spouse applies Finland’s 40% deemed cost to fund units held at least ten years.
const bands: TaxBand[] = [[0, 0.30], [30_000, 0.34]];
const sources = ['tax-fi-accumulating', 'tax-fi-media'];
const capitalIncome = (withdrawalLocal: number) => 0.60 * withdrawalLocal / 2;

registerStandardTax(
  'FI', 'EUR',
  'Finland taxes fund sale gains at 30% up to €30,000 of gain per spouse and 34% above that. For mature units held at least ten years, each spouse can subtract a deemed acquisition cost of 40% of proceeds. The calculation includes the public broadcasting tax.',
  sources,
  ({ withdrawalLocal }) => {
    const gain = capitalIncome(withdrawalLocal);
    const broadcastingTax = Math.min(160, 0.025 * Math.max(0, gain - 15_150));
    return 2 * (progressiveTax(gain, bands) + broadcastingTax);
  },
);

registerStandardTax(
  ['AX', 'FI-01', 'NUTS-FI20', 'NUTS-FI200'], 'EUR',
  'Åland applies Finland’s capital gains rates and deemed acquisition cost. Each adult with more than €14,000 of net income pays Åland’s €128 media fee.',
  sources,
  ({ withdrawalLocal }) => {
    const gain = capitalIncome(withdrawalLocal);
    const mediaFee = gain > 14_000 ? 128 : 0;
    return 2 * (progressiveTax(gain, bands) + mediaFee);
  },
);
