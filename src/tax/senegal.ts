import { progressiveTax, registerStandardTax } from './calculation.ts';

const bands = [
  [630_000, 0.20], [1_500_000, 0.30], [4_000_000, 0.35], [8_000_000, 0.37],
  [13_500_000, 0.40], [50_000_000, 0.43],
] as const;

// Applies the personal annual assessment for stock sold through a foreign broker.
registerStandardTax(
  'SN', 'XOF',
  'Residents report overseas portfolio sale gains as non-commercial income. The model applies ordinary income bands, the married reduction for two earners and the 40% overall ceiling. The 25% withholding rule applies to transactions through Senegalese portfolio intermediaries.',
  ['tax-sn-cgi', 'tax-sn-2022-gains'],
  ({ withdrawalLocal }) => {
    const gain = Math.floor(withdrawalLocal / 2_000) * 1_000;
    const tax = progressiveTax(gain, bands);
    const familyReduction = Math.min(300_000, Math.max(100_000, tax * 0.10));
    return 2 * Math.max(0, Math.min(gain * 0.40, tax - familyReduction));
  },
);
