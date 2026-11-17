import { progressiveTax, registerStandardTax, type TaxBand } from './calculation.ts';

// Foral income and wealth taxes, 2026. Each spouse owns and sells half.
// Unlike the common regime, the wealth-tax limit in these jurisdictions includes long-held gains.
const basqueSavings: TaxBand[] = [
  [0, 0.19], [7_500, 0.20], [15_000, 0.22], [30_000, 0.24], [50_000, 0.255],
  [90_000, 0.26], [120_000, 0.265], [240_000, 0.27], [300_000, 0.28],
];
const alavaGipuzkoaWealth: TaxBand[] = [
  [0, 0.002], [200_000, 0.003], [400_000, 0.005], [800_000, 0.009],
  [1_600_000, 0.013], [3_200_000, 0.017], [6_400_000, 0.021], [12_800_000, 0.025],
];
const alavaGipuzkoaSolidarity: TaxBand[] = [
  [3_200_000, 0.017], [6_400_000, 0.021], [12_800_000, 0.025], [14_500_000, 0.035],
];
const bizkaiaWealth: TaxBand[] = [
  [0, 0.002], [800_000, 0.006], [1_600_000, 0.01], [3_200_000, 0.015],
  [6_400_000, 0.0175], [12_800_000, 0.02],
];
const bizkaiaSolidarity: TaxBand[] = [
  [3_200_000, 0.015], [6_400_000, 0.0175], [12_800_000, 0.02], [14_500_000, 0.035],
];

function registerBasqueTax(
  codes: string[], name: string, allowance: number,
  wealthBands: TaxBand[], solidarityBands: TaxBand[], sources: string[],
) {
  registerStandardTax(
    codes, 'EUR',
    `${name} applies its own savings-income, wealth and large-fortunes scales. Income-based limits and minimum charges apply to the wealth taxes.`,
    sources,
    ({ withdrawalLocal, capitalAtStartOfYearLocal }) => {
      const gain = withdrawalLocal / 2;
      const taxableWealth = capitalAtStartOfYearLocal / 2 - allowance;
      const incomeTax = progressiveTax(gain, basqueSavings);
      const wealthBeforeLimit = progressiveTax(taxableWealth, wealthBands);
      const wealthTax = Math.min(wealthBeforeLimit, Math.max(0.25 * wealthBeforeLimit, 0.65 * gain - incomeTax));
      const solidarityBeforeLimit = progressiveTax(taxableWealth, solidarityBands);
      const solidarityTax = Math.min(
        solidarityBeforeLimit,
        Math.max(0.20 * solidarityBeforeLimit, 0.60 * gain - incomeTax - wealthTax),
      );
      return 2 * (incomeTax + Math.max(wealthTax, solidarityTax));
    },
  );
}

registerBasqueTax(
  ['NUTS-ES211', 'ES-VI'], 'Álava', 800_000,
  alavaGipuzkoaWealth, alavaGipuzkoaSolidarity,
  ['tax-es-vi-income', 'tax-es-vi-wealth', 'tax-es-vi-solidarity'],
);
registerBasqueTax(
  ['NUTS-ES212', 'ES-SS'], 'Gipuzkoa', 700_000,
  alavaGipuzkoaWealth, alavaGipuzkoaSolidarity,
  ['tax-es-ss-income', 'tax-es-ss-wealth', 'tax-es-ss-solidarity'],
);
registerBasqueTax(
  ['NUTS-ES213', 'ES-BI', 'ES-PV', 'NUTS-ES21'], 'Bizkaia (also the Basque Country reference)', 800_000,
  bizkaiaWealth, bizkaiaSolidarity,
  ['tax-es-bi-income', 'tax-es-bi-wealth', 'tax-es-bi-solidarity'],
);

const navarraSavings: TaxBand[] = [
  [0, 0.20], [6_000, 0.22], [10_000, 0.24], [15_000, 0.26], [200_000, 0.27], [300_000, 0.28],
];
const navarraWealth: TaxBand[] = [
  [0, 0.0016], [155_511.88, 0.0024], [311_023.76, 0.004], [622_047.53, 0.0072],
  [1_244_095.06, 0.0104], [2_488_190.11, 0.0136], [4_976_380.22, 0.0168],
  [9_952_760.45, 0.02], [11_003_784.50, 0.035],
];

registerStandardTax(
  ['ES-NC', 'ES-NA', 'NUTS-ES22', 'NUTS-ES220'], 'EUR',
  'Navarra taxes sale gains on its savings scale. Its wealth scale includes the higher rates for large estates, with a €550,000 allowance per person and an income-based limit.',
  ['tax-es-nc-income', 'tax-es-nc-wealth', 'tax-es-nc-2026', 'tax-es-nc-cap'],
  ({ withdrawalLocal, capitalAtStartOfYearLocal }) => {
    const gain = withdrawalLocal / 2;
    const taxBeforeCredits = progressiveTax(gain, navarraSavings);
    const lowerIncomeCredit = gain <= 30_000
      ? 1_280 - 0.0904 * Math.max(0, gain - 17_500)
      : Math.max(0, 150 - 0.075 * (gain - 30_000));
    const incomeTax = Math.max(0, taxBeforeCredits - 1_084 - lowerIncomeCredit);
    const grossWealthTax = progressiveTax(capitalAtStartOfYearLocal / 2 - 550_000, navarraWealth);
    const wealthTax = Math.min(grossWealthTax, Math.max(0.45 * grossWealthTax, 0.65 * gain - taxBeforeCredits));
    return 2 * (incomeTax + wealthTax);
  },
);
