import { progressiveTax, type TaxBand } from './calculation.ts';
import { registerTaxRules, type TaxRules } from './tax-rules.ts';

// 2026–27 income year. Held at least a year after deemed acquisition at arrival.
const bands: TaxBand[] = [[18_200, 0.15], [45_000, 0.30], [135_000, 0.37], [190_000, 0.45]];

const rules: TaxRules = {
  currency: 'AUD',
  hasSpecialRegime: true,
  taxOwed: ({ withdrawalLocal }, regime) => {
    if (regime === 'special') {
      return {
        taxLocal: 0,
        regimeName: 'Temporary residents on New Zealand special category visas',
        explanation: 'Qualifying Australian temporary residents generally owe no Australian tax on gains from a foreign ETF. This estimate assumes both spouses are New Zealand citizens with non-protected Special Category visas (subclass 444), which allow an indefinite stay and are available again on each entry if they remain eligible. The exemption ends if either spouse becomes an Australian permanent resident or citizen.',
        sourceIds: ['tax-au-temporary', 'tax-au-444'],
      };
    }
    const taxable = withdrawalLocal / 4;
    const offset = Math.max(0, 700 - 0.05 * Math.max(0, Math.min(45_000, taxable) - 37_500)
      - 0.015 * Math.max(0, taxable - 45_000));
    // Apply the lower levy available under the individual or family threshold.
    const levy = Math.min(0.02 * taxable, 0.10 * Math.max(0, taxable - 28_011),
      0.05 * Math.max(0, 2 * taxable - 47_238));
    return {
      taxLocal: 2 * (Math.max(0, progressiveTax(taxable, bands) - offset) + levy),
      regimeName: 'Standard',
      explanation: 'Australia applies the 50% long-term capital gains discount and each spouse’s own income tax bands and low-income offset. It includes the Medicare levy and assumes private hospital cover avoids the surcharge. This is the 2026–27 estimate. Indexation and a new minimum tax apply to gains accruing from July 2027.',
      sourceIds: ['tax-au-rates', 'tax-au-cgt', 'tax-au-lito', 'tax-au-medicare', 'tax-au-2027'],
    };
  },
};

registerTaxRules('AU', rules);
registerTaxRules('NF', {
  ...rules,
  taxOwed: (year, regime) => {
    const owed = rules.taxOwed(year, regime);
    return { ...owed, sourceIds: [...owed.sourceIds, 'tax-au-norfolk'] };
  },
});
