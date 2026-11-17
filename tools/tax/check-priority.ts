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
