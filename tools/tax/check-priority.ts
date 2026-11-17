import assert from 'node:assert/strict';
import '../../src/tax/international.ts';
import { taxRulesFor } from '../../src/tax/tax-rules.ts';

// US dollar inputs use illustrative FX and a 5% withdrawal rate. Expected bills
// are in local currency. See .agent/research/tax.md for the official guidance.
const cases = [
  ['PT', 0.86, [5604.60, 16491.08, 42140], 1],
  ['ES-VC', 0.86, [8379.45, 19311.45, 48393.98], 1],
  ['IT', 0.86, [15480, 30960, 64500], 1],
  ['DE', 0.86, [1708, 11390, 39166.88], 1],
  ['NL', 0.86, [13496.82, 39450.54, 90316.51], 1],
  ['GB', 0.76, [5369.14, 11949.44, 35093.62], 1],
  // ESTV detailed calculator income and wealth tax, plus the AHV table.
  ['CH-ZH', 0.81, [1703 + 1696, 5621 + 3816, 20190 + 8798], 20],
  ['CH-GE', 0.81, [3850 + 1696, 10770 + 3816, 30678 + 8798], 25],
  ['TH', 32.7, [198400, 681000, 1946500], 1],
  ['AE', 3.6725, [0, 0, 0], 0],
  ['GE', 2.7, [0, 0, 0], 0],
  // Territorial exclusions and standalone gains charges documented by the local authorities.
  ['AW', 1.79, [0, 0, 0], 0],
  ['PF', 103, [0, 0, 0], 0],
  ['ET', 150, [1_350_000, 2_700_000, 5_625_000], 1],
  ['CG', 560, [5_040_000, 10_080_000, 21_000_000], 1],
  ['GA', 560, [5_712_000, 11_424_000, 23_800_000], 1],
  // DRC brackets, 30% cap and reduction on the lower bands (CDF).
  ['CD', 2_000, [32_033_971.20, 71_620_531.20, 149_620_531.20], 1],
  ['BT', 86, [0, 0, 0], 0],
  ['IR', 42_000, [0, 0, 0], 0],
  ['TL', 1, [0, 0, 0], 0],
  ['BJ', 560, [1_680_000, 3_360_000, 7_000_000], 1],
  ['CI', 560, [0, 0, 0], 0],
  ['GM', 73, [657_000, 1_314_000, 2_737_500], 1],
  ['LR', 190, [2_643_000, 5_493_000, 11_668_000], 1],
  ['PM', 0.86, [9804, 19608, 40850], 1],
  ['MF', 0.86, [17853.60, 35707.20, 74390], 1],
  ['NC', 103, [0, 0, 0], 0],
  ['GU', 1, [0, 0, 17835], 1],
  ['MP', 1, [0, 0, 17835], 1],
  ['VI', 1, [0, 0, 17835], 1],
  // Pakistan: PKR 1.61m through 5.6m for each spouse, then 45% and the 10% surcharge above 10m.
  ['PK', 280, [5_740_000, 14_630_000, 32_648_000], 1],
  // Kōtō Ward, household limits less the fixed premium already priced in health cover.
  ['JP', 150, [2_784_328, 4_616_954, 8_578_379], 1],
  // Tunisia: at the three scales, spouse wealth is TND 1.8m, 3.6m and 7.5m.
  ['TN', 3, [18_000, 72_000, 225_000], 1],
  ['TJ', 10, [90_000, 180_000, 375_000], 1],
  // Suriname: 3% of the joint portfolio value above SRD 120,000.
  ['SR', 40, [1_436_400, 2_876_400, 5_996_400], 1],
  ['HT', 130, [1_560_000, 3_120_000, 6_500_000], 1],
  ['SN', 560, [10_758_000, 24_198_000, 54_518_000], 1],
  ['GN', 8_600, [77_400_000, 154_800_000, 322_500_000], 1],
  ['BF', 560, [0, 0, 0], 0],
  ['MR', 40, [0, 0, 0], 0],
  ['KM', 420, [0, 0, 0], 0],
  // Lesotho: each spouse owes LSL 15,552 through 77,760, then 30% less the personal credit.
  ['LS', 18, [283_968, 607_968, 1_309_968], 1],
  ['NU', 1.7, [0, 0, 0], 0],
  // Curaçao uses a 10% deemed return, 19.5% cap less credits, AOV/AWW and AVBZ.
  ['CW', 1.79, [55_292.14, 103_203.28, 201_235.69], 1],
  // Sint Maarten uses a 4% deemed return and the 2026 table on income less AOV/AWW.
  ['SX', 1.79, [22_556.77, 60_328.36, 151_855.29], 1],
  ['ML', 560, [2_352_000, 4_704_000, 9_800_000], 1],
  // Somalia Ministry of Finance manual, section XIV: $1,728 per spouse through $18k, then 15%.
  ['SO', 1, [7_056, 16_056, 35_556], 1],
  ['LA', 22_000, [26_400_000, 52_800_000, 110_000_000], 1],
  // American Samoa Form 390 deductions and two Schedule D rates.
  ['AS', 1, [5_025, 17_025, 43_540.20], 1],
] as const;

for (const [code, exchangeRate, expected, tolerance] of cases) {
  const rules = taxRulesFor([code]);
  assert(rules, `Missing rule for ${code}`);
  for (const [index, withdrawalUsd] of [60_000, 120_000, 250_000].entries()) {
    const withdrawalLocal = withdrawalUsd * exchangeRate;
    const year = { withdrawalLocal, capitalAtStartOfYearLocal: withdrawalLocal / 0.05 };
    const { taxLocal } = rules.taxOwed(year, 'standard');
    assert(
      Math.abs(taxLocal - expected[index]) <= tolerance,
      `${code} at USD ${withdrawalUsd}: expected ${expected[index]}, got ${taxLocal}`,
    );
  }
}

console.log(`Passed ${cases.length * 3} tax comparisons in local currency`);
