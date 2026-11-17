import { registerStandardTax } from './calculation.ts';

// 2026 income tax table: threshold, tax at threshold, and marginal rate.
const incomeBands = [
  [0, 0, 0.0975], [39_094, 3_812, 0.15], [52_127, 5_767, 0.23],
  [78_190, 11_761, 0.30], [110_769, 21_535, 0.375], [162_894, 41_082, 0.465],
].reverse();

const socialBands = [
  7_124.39, 13_283.13, 18_113.26, 22_943.60, 27_773.85, 32_604.05,
  37_434.29, 41_509.81, 45_585.31, 49_660.84, 53_736.35, 57_832.39,
];

registerStandardTax(
  'CW', 'XCG',
  'Curaçao taxes a deemed return of 10% of opening value on an offshore corporate investment fund. The calculation includes old-age, survivors and long-term care contributions, with the couple’s investment income attributed to one spouse. It assumes an independent-means residence permit and private cover, so the basic BVZ premium is excluded.',
  ['tax-cw-deemed-2025', 'tax-cw-income-2026', 'tax-cw-code-2026', 'tax-cw-svb-2026', 'tax-cw-bvz'],
  ({ capitalAtStartOfYearLocal }) => {
    const deemed = capitalAtStartOfYearLocal * 0.10;
    const bandCount = socialBands.filter(threshold => deemed >= threshold).length;
    const fractionPayable = bandCount === 0 ? 0 : 0.40 + bandCount * 0.05;
    const lowIncomeRelief = 0.065 * Math.min(deemed, Math.max(0, 9_340 - 0.338 * deemed));
    const ageAndSurvivors = fractionPayable * (0.16 * Math.min(deemed, 100_000) - lowIncomeRelief)
      + 0.01 * Math.max(0, deemed - 100_000);
    const personalCredit = 2_915;
    const singleEarnerCredit = 1_779;
    const taxable = deemed - ageAndSurvivors;
    const [threshold, fixed, rate] = incomeBands.find(([start]) => taxable >= start) ?? [0, 0, 0.0975];
    const incomeTax = Math.max(0, Math.min(fixed + rate * (taxable - threshold), 0.195 * taxable)
      - personalCredit - singleEarnerCredit);
    const longTermCareRate = deemed <= personalCredit / 0.0975 ? 0.01 : 0.02;
    return incomeTax + ageAndSurvivors + Math.min(deemed, 606_247.08) * longTermCareRate;
  },
);
