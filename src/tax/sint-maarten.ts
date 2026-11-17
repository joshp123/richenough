import { registerStandardTax } from './calculation.ts';

// 2026 income tax table: threshold, tax at threshold, and marginal rate.
const incomeBands = [
  [0, 0, 0.125], [36_576, 4_571.95, 0.20], [54_864, 8_229.49, 0.2625],
  [76_200, 13_830.02, 0.3375], [114_297, 26_688.11, 0.40], [161_540, 45_585.20, 0.475],
].reverse();

const socialThresholds = [
  10_928.01,
  ...[11_895.01, 16_220.37, 20_545.93, 24_871.39, 29_196.83, 33_522.29,
    37_171.91, 40_821.51, 44_471.13, 48_120.74].map(threshold => threshold * 88_708.37 / 51_788.74),
  88_708.37,
];

registerStandardTax(
  'SX', 'XCG',
  'Sint Maarten taxes a deemed return of 4% of the opening value of an offshore corporate investment fund. The couple’s investment income is attributed to one spouse. This estimate adds old-age, survivors and long-term care contributions. The newcomer pensioner regime requires arrival from age 50 and an owned home.',
  ['tax-sx-income', 'tax-sx-income-2026', 'tax-sx-szv-2026', 'tax-sx-szv-scale', 'tax-sx-avbz-rate', 'tax-sx-avbz-cap'],
  ({ capitalAtStartOfYearLocal }) => {
    const deemed = capitalAtStartOfYearLocal * 0.04;
    const bandCount = socialThresholds.filter(threshold => deemed >= threshold).length;
    const fractionPayable = bandCount === 0 ? 0 : 0.40 + bandCount * 0.05;
    const ageAndSurvivors = fractionPayable * 0.14 * Math.min(deemed, 132_824.35);
    const taxable = deemed - ageAndSurvivors;
    const [threshold, fixed, rate] = incomeBands.find(([start]) => taxable >= start) ?? [0, 0, 0];
    const incomeTax = taxable <= 27_281.28 ? 0 : Math.max(0, fixed + rate * (taxable - threshold) - 2_381 - 1_590);
    const longTermCareRate = deemed < 36_576 ? 0.01 : 0.02;
    return incomeTax + ageAndSurvivors + longTermCareRate * Math.min(deemed, 382_214);
  },
);
