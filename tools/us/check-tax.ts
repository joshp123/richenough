// Worked examples from the federal and state instructions listed in data/sources.csv.
// Allow $1 for the whole-dollar base amounts in New York's printed rate schedule.
import assert from 'node:assert/strict';
import '../../src/tax/united-states.ts';
import { taxRulesFor, type TaxRegime } from '../../src/tax/tax-rules.ts';

const withdrawals = [60_000, 120_000, 250_000];
const federal = [0, 0, .15 * (250_000 - 32_200 - 98_900)];

function check(label: string, codes: string[], expected: number[], regime: TaxRegime = 'standard'): void {
  const rules = taxRulesFor(codes);
  assert.ok(rules, label);
  if (regime === 'special') assert.equal(rules.hasSpecialRegime, true, label);
  withdrawals.forEach((withdrawalLocal, i) => {
    const result = rules.taxOwed({ withdrawalLocal, capitalAtStartOfYearLocal: 20 * withdrawalLocal }, regime);
    assert.ok(Math.abs(result.taxLocal - expected[i]) <= 1,
      `${label}, ${withdrawalLocal}: expected ${expected[i]}, got ${result.taxLocal}`);
  });
}

// IRS Rev. Proc. 2025-32 and Form 8960; WA DOR published deduction.
check('Austin', ['US-48453', 'US-TX', 'US'], federal);
check('Seattle', ['US-53033', 'US-WA', 'US'], federal);

// California 2026 Schedule Y. In the first case, use the midpoint of the $50 tax-table band.
check('Los Angeles', ['US-06037', 'US-CA'], [
  229.12 + .02 * (48_225 - 22_912) - 316 - 120,
  2_113.48 + .06 * (108_200 - 85_722) - 316,
  federal[2] + 6_621.76 + .093 * (238_200 - 150_394) - 316,
]);

// New York IT-2105-I state rates, recapture worksheets 1 and 2, NYC rates and credits.
check('New York City', ['US-36061', 'US-NY'], [
  1_174 + .054 * (43_950 - 27_900) + 665 + .03762 * (43_950 - 21_600) - 125 - 37 - .00228 * (43_950 - 21_600),
  5_280.70 + (.054 * 103_950 - 5_280.70) * .247
    + 3_264 + .03876 * (103_950 - 90_000) - 125 - 37 - .00228 * (103_950 - 21_600),
  federal[2] + 8_391 + .059 * (233_950 - 161_550) + 333 + 807
    + 3_264 + .03876 * (233_950 - 90_000) - 125 - 37 - .00228 * (233_950 - 21_600),
]);

// Maryland joint tables and Montgomery's 3.2% using Form 502's taxable income.
check('Montgomery County', ['US-24031', 'US-MD'], [
  90 + .0475 * (46_800 - 3_000) + .032 * 46_800,
  90 + .0475 * (106_800 - 3_000) + .032 * 106_800,
  federal[2] + 10_947.50 + .055 * (243_200 - 225_000) + .032 * 243_200,
]);

// OR-ESTIMATE Chart J and Portland Revenue's Metro, PFA and Arts income taxes.
check('Portland, Multnomah', ['CITY-5746545', 'US-41051', 'US-OR'], [
  1_357 + .0875 * (54_200 - 22_800) - 520 + 70,
  1_357 + .0875 * (114_200 - 22_800) - 520 + 70,
  federal[2] + 1_357 + .0875 * (237_200 - 22_800) + 322 + 558 + 70,
]);

// San Juan Form 482 Schedule A2. Use the lesser of the 15% and ordinary computations.
check('San Juan', ['US-72127', 'US-PR'], [
  .92 * (3_430 + .25 * (53_000 - 41_500)), .15 * 113_000, .15 * 243_000,
]);
check('San Juan, Act 60 2026 decree', ['US-72127', 'US-PR'], [0, 0, 0], 'special');

const seattle = taxRulesFor(['US-53033', 'US-WA'])!;
const gain = 1_400_000;
assert.equal(seattle.taxOwed({ withdrawalLocal: gain, capitalAtStartOfYearLocal: 20 * gain }, 'standard').taxLocal,
  77_220 + 150_820 + 43_700 + 70_000 + 10_890);
console.log('25 tax checks passed across seven places, including the Washington surcharge and Puerto Rico special regime.');
