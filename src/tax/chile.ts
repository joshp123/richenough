import { progressiveTax, type TaxBand } from './calculation.ts';

// Calendar 2026, assessed in 2027. Each threshold is expressed in December 2026 UTA.
const uta = 873_624;
const bands: TaxBand[] = [
  [13.5 * uta, 0.04], [30 * uta, 0.08], [50 * uta, 0.135], [70 * uta, 0.23],
  [90 * uta, 0.304], [120 * uta, 0.35], [310 * uta, 0.40],
];
import { registerTaxRules } from './tax-rules.ts';

registerTaxRules('CL', {
  currency: 'CLP',
  hasSpecialRegime: true,
  taxOwed: ({ withdrawalLocal }, regime) => regime === 'special' ? {
    taxLocal: 0,
    regimeName: 'New resident territorial period',
    explanation: 'New foreign residents generally pay tax only on Chilean-source income for their first three years from entry. This leaves offshore ETF gains outside Chilean tax during that period.',
    sourceIds: ['tax-cl-new-residents'],
  } : {
    taxLocal: 2 * progressiveTax(withdrawalLocal / 2, bands),
    regimeName: 'Standard',
    explanation: 'Chile taxes non-exempt foreign ETF gains at progressive global income tax rates. Each spouse uses their own bands.',
    sourceIds: ['tax-cl-rates', 'tax-cl-uta'],
  },
});
