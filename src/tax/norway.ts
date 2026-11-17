import { progressiveTax, registerStandardTax } from './calculation.ts';

// 2026. Listed equity fund qualifies for 20% valuation discount. A near-zero
// historic cost basis means negligible cost-based shielding relief in this scenario.
function norway(codes: string[], municipalRate: number, ordinaryIncomeRate: number) {
  registerStandardTax(
    codes, 'NOK',
    'Norway raises equity fund gains by 1.72 before applying income tax and personal allowances. Municipal and national wealth tax use 80% of equity value and double the single thresholds for spouses.',
    ['tax-no-shares', 'tax-no-wealth', 'tax-no-person', 'tax-no-municipal'],
    ({ withdrawalLocal, capitalAtStartOfYearLocal }) => {
      const income = Math.max(0, withdrawalLocal * 1.72 - 2 * 114_540);
      const taxableWealth = 0.8 * capitalAtStartOfYearLocal;
      const wealthTax = progressiveTax(taxableWealth, [
        [3_800_000, 0.0065 + municipalRate], [43_000_000, 0.0075 + municipalRate],
      ]);
      return income * ordinaryIncomeRate + wealthTax;
    },
  );
}
norway(['NO'], 0.0035, 0.22);
