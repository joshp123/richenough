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
  // ESTV calculator at each exact wealth input. Zürich deducts AHV and bills its 5% fee.
  ['CH-ZH', 0.81, [1703 + 1780.8, 5459 + 4006.8, 19109 + 9237.9], 20],
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
  // Kōtō Ward: declared gains at 95% of proceeds, less allowances and premiums.
  // Include pension and the portion of health premiums outside the health budget.
  ['JP', 150, [2_446_674, 4_323_973, 8_087_530], 1],
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
  ['TG', 560, [0, 0, 0], 0],
  ['DJ', 177.72, [0, 0, 0], 0],
  // Afghanistan: AFN 106,800 through 1.2m per spouse, then 20%.
  ['AF', 67, [537_600, 1_341_600, 3_083_600], 1],
  ['MG', 4_600, [55_200_000, 110_400_000, 230_000_000], 1],
  ['GW', 560, [0, 0, 0], 0],
  ['YE', 250, [0, 0, 0], 0],
  ['SD', 1_200, [0, 0, 0], 0],
  // South Sudan: SSP 91,800 through 1.08m per spouse, then 20%.
  ['SS', 5_700, [68_151_600, 136_551_600, 284_751_600], 1],
  ['TM', 3.5, [20_880, 41_880, 87_380], 1],
  ['KI', 1.5, [0, 0, 0], 0],
  ['ER', 15, [0, 0, 0], 0],
  ['CITY-293397', 3.7, [55_500, 111_000, 231_250], 1],
  ['CITY-282615', 3.7, [0, 0, 0], 0],
  // Equatorial Guinea: XAF 2.11m through XAF 15m per spouse, then 25%.
  ['GQ', 560, [5_120_000, 13_520_000, 31_720_000], 1],
  // Cuba, Law 113 art. 26: CUP 14,500 through 50,000 taxable per spouse, then 50%.
  ['CU', 24, [659_880, 1_379_880, 2_939_880], 1],
  ['SY', 110, [0, 0, 0], 0],
  ['NE', 560, [2_352_000, 4_704_000, 9_800_000], 1],
  // The BES return lists gains from selling substantial interests, which this couple does not hold.
  ['BQ', 1, [0, 0, 0], 0],
  // Svalbard's annual resolution: 16% of uplifted gains after two allowances, plus wealth tax.
  ['SJ', 10, [158_720 + 58_000, 323_840 + 154_000, 681_600 + 362_000], 1],
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

// Actual city inputs from the 18 November 2026 review, kept fixed so the
// capital solver cannot conceal a change in the underlying bill.
for (const [code, capital, expected, tolerance] of [
  ['CITY-2618425', 33_694_664, 928_500, 1],  // §§ 8a and 9, Copenhagen municipal rate.
  ['CITY-2267057', 1_464_953, 9_061, 1],    // 95% of the joint IRS assessment.
  ['CH-ZH', 2_618_600, 9_026 + 5_565, 20], // Exact ESTV assessment and SVA invoice.
  ['AR', 2_684_510_791, 30_428_179, 1],    // Income tax and indexed personal assets tax.
  ['ID', 23_283_230_252, 259_498_300, 1],  // Round the combined base down to Rp1,000.
] as const) {
  const rule = taxRulesFor([code]);
  assert(rule, code);
  const year = { withdrawalLocal: capital * 0.05, capitalAtStartOfYearLocal: capital };
  assert(Math.abs(rule.taxOwed(year, 'standard').taxLocal - expected) <= tolerance, code);
}

// Short newcomer breaks must give the same bill even when the map's special setting is selected.
const shortBreaks = [
  ['CL', /three years/],
  ['DO', /third tax year/],
  ['GB', /four UK tax years/],
  ['IN', /two to four tax years/],
  ['KR', /five years/],
  ['NZ', /four years/],
  ['PK', /following tax year/],
  ['SJ', /five years/],
  ['TZ', /two years/],
] as const;
const year = { withdrawalLocal: 100_000_000, capitalAtStartOfYearLocal: 2_000_000_000 };

for (const [code, duration] of shortBreaks) {
  const rules = taxRulesFor([code]);
  assert(rules, code);
  assert.equal(rules.hasSpecialRegime, false, code);
  const ordinary = rules.taxOwed(year, 'standard');
  assert.deepEqual(rules.taxOwed(year, 'special'), ordinary, code);
  assert.match(ordinary.explanation, duration, code);
}

// The special bill includes mandatory recurring costs for both spouses.
for (const [code, withdrawalLocal, expectedTax] of [
  ['IT', 2_000_000, 350_000],
  ['SM', 250_000, 20_000],
  ['UY', 2_400_000, 747.12638],
] as const) {
  const rules = taxRulesFor([code]);
  assert(rules?.hasSpecialRegime, code);
  const result = rules.taxOwed({ withdrawalLocal, capitalAtStartOfYearLocal: withdrawalLocal * 20 }, 'special');
  assert(Math.abs(result.taxLocal - expectedTax) < 0.01, code);
}

console.log(`Passed ${shortBreaks.length} short-break checks and 3 recurring-cost checks`);
