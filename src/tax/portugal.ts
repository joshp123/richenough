import { progressiveTax, registerStandardTax, type TaxBand } from './calculation.ts';

// CIRS arts. 43(5), 68, 68-A, 69 and 72, 2026. A mature ETF held at least eight years
// has a 30% exclusion. The household can elect aggregation and use the joint quotient.
const mainlandBands: TaxBand[] = [
  [0, 0.122], [8342, 0.152], [12587, 0.207], [17838, 0.236], [23089, 0.306],
  [29397, 0.346], [43090, 0.431], [46566, 0.446], [86634, 0.48],
];
const solidarityBands: TaxBand[] = [[80000, 0.025], [250000, 0.05]];

function portugal(codes: string[], regionalFactor: number) {
  registerStandardTax(
    codes, 'EUR',
    'Portugal taxes 70% of the gain on qualifying ETF units held at least eight years. The couple pays the lower of the separate capital gains rate and the joint income tax scale. IFICI requires qualifying work or professional income.',
    ['tax-pt-gains', 'tax-pt-rates', 'tax-pt-income', 'tax-pt-2026', 'tax-pt-guide', 'tax-pt-islands', 'tax-pt-ifici'],
    ({ withdrawalLocal }) => {
      const taxableGain = withdrawalLocal * 0.7;
      return Math.min(
        taxableGain * 0.28 * regionalFactor,
        2 * (progressiveTax(taxableGain / 2, mainlandBands) * regionalFactor
          + progressiveTax(taxableGain / 2, solidarityBands)),
      );
    },
  );
}

portugal(['PT'], 1);
portugal(['NUTS-PT2', 'NUTS-PT3', 'PT-20', 'PT-30'], 0.7);
