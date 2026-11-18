import { progressiveTax, registerStandardTax, type TaxBand } from './calculation.ts';

// 2026. Ordinary wealth schedule, excluding the invalidated emergency surcharge.
const uvt = 52_374;
const wealthBands: TaxBand[] = [[72_000 * uvt, 0.005], [122_000 * uvt, 0.01], [239_000 * uvt, 0.015]];

registerStandardTax(
  'CO', 'COP',
  'Colombia charges 15% on gains from investment assets held at least two years. The estimate treats private sales of the long-held ETF as occasional gains outside the health and pension contribution base. Wealth tax is calculated separately on each spouse’s half of the portfolio.',
  ['tax-co-wealth', 'tax-co-uvt', 'tax-co-emergency-wealth', 'tax-co-ugpp-capital', 'tax-co-ugpp-fixed-assets'],
  ({ withdrawalLocal, capitalAtStartOfYearLocal }) =>
    withdrawalLocal * 0.15 + 2 * progressiveTax(capitalAtStartOfYearLocal / 2, wealthBands),
);
