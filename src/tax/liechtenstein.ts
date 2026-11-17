import { progressiveTax, registerStandardTax, type TaxBand } from './calculation.ts';

const incomeBands: TaxBand[] = [
  [31_710, 0.01], [42_280, 0.03], [84_560, 0.04], [147_980, 0.05],
  [211_400, 0.06], [274_820, 0.065], [338_240, 0.07], [422_800, 0.08],
];

// Non-employed person's 2026 annual AHV/IV/FAK contribution, including administration.
const socialContributions = [
  1411.65, 1840.50, 2269.40, 2698.25, 3127.10, 3555.95, 3984.80, 4413.60, 4842.55,
  5271.35, 5700.25, 6129.10, 6557.95, 6986.85, 7415.70, 7844.55, 8273.35, 8702.25,
  9131.05, 9560, 9988.80, 10417.70, 10846.55, 11275.35, 11704.30, 12133.10, 12285,
];
const lowerContributions = [368.55, 464.55, 607.55, 768.40, 982.80];

const municipalities = [
  ['01', 'Balzers', 1.5], ['02', 'Eschen', 1.6], ['03', 'Gamprin', 1.5],
  ['04', 'Mauren', 1.8], ['05', 'Planken', 1.5], ['06', 'Ruggell', 1.65],
  ['07', 'Schaan', 1.5], ['08', 'Schellenberg', 1.5], ['09', 'Triesen', 1.5],
  ['10', 'Triesenberg', 1.5], ['11', 'Vaduz', 1.5],
] as const;

for (const [code, name, surtax] of municipalities) {
  const codes = [`LI-${code}`];
  if (code === '11') codes.push('LI', 'CITY-3042030');
  registerStandardTax(
    codes, 'CHF',
    `Liechtenstein taxes a deemed return of 4% on the portfolio using national and municipal income tax (${name}). The estimate also includes social contributions on wealth for a couple without employment.`,
    ['tax-li-law', 'tax-li-local', 'tax-li-ahv'],
    ({ capitalAtStartOfYearLocal: capital }) => {
      const spouseWealth = capital / 2;
      const contribution = spouseWealth < 1_000_000
        ? lowerContributions[Math.floor(spouseWealth / 200_000)]
        : socialContributions[Math.min(26, Math.floor((spouseWealth - 1_000_000) / 100_000))];
      const socialTax = 2 * contribution;
      return (1 + surtax) * progressiveTax(0.04 * capital - socialTax, incomeBands) + socialTax;
    },
  );
}
