import { progressiveTax, registerStandardTax, type TaxBand } from './calculation.ts';

// AEAT 2025 return manual (updated in 2026) and LIRPF arts. 66 and 76.
const savings: TaxBand[] = [
  [0, 0.19], [6_000, 0.21], [50_000, 0.23], [200_000, 0.27], [300_000, 0.30],
];
const nationalStarts = [0, 167129.45, 334252.88, 668499.75, 1336999.51, 2673999.01, 5347998.03, 10695996.06];
const nationalWealthRates = [0.2, 0.3, 0.5, 0.9, 1.3, 1.7, 2.1, 3.5];
const solidarity: TaxBand[] = [[3_000_000, 0.017], [5_347_998.03, 0.021], [10_695_996.06, 0.035]];

type WealthRules = {
  name: string;
  codes: string[];
  allowance?: number;
  personalMinimum?: number;
  rates?: number[];
  starts?: number[];
  rebate?: number;
  solidarityOnly?: boolean;
};

const regions: WealthRules[] = [
  { name: 'national reference', codes: ['ES'] },
  { name: 'Galicia', codes: ['ES-GA', 'NUTS-ES11'], personalMinimum: 5789, rebate: 0.5 },
  { name: 'Asturias', codes: ['ES-AS', 'NUTS-ES12'], personalMinimum: 6105, rates: [0.22, 0.33, 0.56, 1.02, 1.48, 1.97, 2.48, 3] },
  { name: 'Cantabria', codes: ['ES-CB', 'NUTS-ES13'], solidarityOnly: true },
  { name: 'La Rioja', codes: ['ES-RI', 'NUTS-ES23'], solidarityOnly: true },
  { name: 'Aragón', codes: ['ES-AR', 'NUTS-ES24'] },
  { name: 'Madrid', codes: ['ES-MD', 'NUTS-ES30'], personalMinimum: 5956.65, solidarityOnly: true },
  { name: 'Castilla y León', codes: ['ES-CL', 'NUTS-ES41'] },
  { name: 'Castilla-La Mancha', codes: ['ES-CM', 'NUTS-ES42'] },
  { name: 'Extremadura', codes: ['ES-EX', 'NUTS-ES43'], solidarityOnly: true },
  {
    name: 'Catalonia', codes: ['ES-CT', 'NUTS-ES51'], allowance: 500_000,
    starts: [0, 167129.45, 334252.88, 668499.75, 1336999.75, 2673999.01, 5347998.03, 10695996.06, 20_000_000],
    rates: [0.21, 0.315, 0.525, 0.945, 1.365, 1.785, 2.205, 2.75, 3.48],
  },
  {
    name: 'Valencia', codes: ['ES-VC', 'NUTS-ES52', 'CITY-2509954'], allowance: 1_000_000,
    personalMinimum: 6105, rates: [0.25, 0.37, 0.62, 1.12, 1.62, 2.12, 2.62, 3.5],
  },
  {
    name: 'Balearic Islands', codes: ['ES-IB', 'NUTS-ES53'], allowance: 3_000_000,
    starts: [0, 170472.04, 340937.04, 681869.75, 1336739.51, 2727479, 5454958, 10909915.99],
    rates: [0.28, 0.41, 0.69, 1.24, 1.79, 2.35, 2.9, 3.45],
  },
  { name: 'Andalusia', codes: ['ES-AN', 'NUTS-ES61'], personalMinimum: 5790, solidarityOnly: true },
  { name: 'Murcia', codes: ['ES-MC', 'NUTS-ES62'], solidarityOnly: true },
  { name: 'Ceuta', codes: ['ES-CE', 'NUTS-ES63'] },
  { name: 'Melilla', codes: ['ES-ML', 'NUTS-ES64'] },
  { name: 'Canary Islands', codes: ['ES-CN', 'NUTS-ES70'], personalMinimum: 5606 },
];

for (const region of regions) {
  const bands = (region.starts ?? nationalStarts).map(
    (start, index): TaxBand => [start, (region.rates ?? nationalWealthRates)[index] / 100],
  );
  const personalMinimum = region.personalMinimum ?? 5550;
  registerStandardTax(
    region.codes, 'EUR',
    `Spain applies the savings bands and personal minima to sales, plus the applicable wealth and solidarity taxes (${region.name}). Wealth-tax limits reduce the charge when all income is from units held more than a year. The Beckham regime requires a qualifying reason for moving to Spain, such as employment.`,
    ['tax-es-income', 'tax-es-minima', 'tax-es-wealth', 'tax-es-solidarity', 'tax-es-beckham'],
    ({ withdrawalLocal, capitalAtStartOfYearLocal }) => {
      const gain = withdrawalLocal / 2;
      const capital = capitalAtStartOfYearLocal / 2;
      const incomeTax = progressiveTax(gain, savings) - (
        progressiveTax(Math.min(gain, 5550), savings)
        + progressiveTax(Math.min(gain, personalMinimum), savings)
      ) / 2;

      // LIP art. 31 excludes gains on assets held over a year from both sides
      // of the 60% limit. For investment-only income, the 20% minimum remains.
      const wealthTax = 0.2 * progressiveTax(capital - (region.allowance ?? 700_000), bands);
      const nationalMinimum = 0.2 * progressiveTax(capital - 700_000, solidarity);
      const totalWealthTax = region.solidarityOnly
        ? nationalMinimum
        : Math.max(nationalMinimum, wealthTax * (1 - (region.rebate ?? 0)));
      return 2 * (incomeTax + totalWealthTax);
    },
  );
}
