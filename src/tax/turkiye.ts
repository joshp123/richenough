import { progressiveTax, type TaxBand } from './calculation.ts';

// 2026 non-wage income tax bands, TRY per person.
const bands: TaxBand[] = [[0, 0.15], [190_000, 0.20], [400_000, 0.27], [1_000_000, 0.35], [5_300_000, 0.40]];
import { registerTaxRules } from './tax-rules.ts';

registerTaxRules('TR', {
  currency: 'TRY',
  hasSpecialRegime: true,
  taxOwed: ({ withdrawalLocal }, regime) => regime === 'special' ? {
    taxLocal: 0,
    regimeName: 'New resident foreign income exemption',
    explanation: 'New residents with no Turkish tax residence or full tax liability in the previous three tax years can qualify for a 20-year exemption on foreign income, including foreign ETF gains.',
    sourceIds: ['tax-tr-new-residents'],
  } : {
    taxLocal: 2 * progressiveTax(withdrawalLocal / 2, bands),
    regimeName: 'Standard',
    explanation: 'Türkiye taxes foreign ETF gains at ordinary rates per spouse after the new-resident exemption ends. This assumes mature units with negligible remaining acquisition cost.',
    sourceIds: ['tax-tr-rates', 'tax-tr-gains'],
  },
});
