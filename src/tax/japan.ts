import { registerStandardTax } from './calculation.ts';

// Kōtō Ward, 2026–27. Use the same benchmark as the fixed health-cover entry.
// Each component has an annual household cap and a fixed charge per person.
const insuranceComponents = [
  [0.0751, 670_000, 47_600],
  [0.0280, 260_000, 17_600],
  [0.0243, 170_000, 17_800],
  [0.0027, 30_000, 1_873],
] as const;

// NTA No.1199, 2026 resident basic deductions (per person).
function nationalAllowance(income: number): number {
  if (income <= 4_890_000) return 1_040_000;
  if (income <= 6_550_000) return 670_000;
  if (income <= 23_500_000) return 620_000;
  if (income <= 24_000_000) return 480_000;
  if (income <= 24_500_000) return 320_000;
  if (income <= 25_000_000) return 160_000;
  return 0;
}

function localAllowance(income: number): number {
  if (income <= 24_000_000) return 430_000;
  if (income <= 24_500_000) return 290_000;
  if (income <= 25_000_000) return 150_000;
  return 0;
}

function taxableThousands(income: number): number {
  return Math.max(0, Math.floor(income / 1_000) * 1_000);
}

registerStandardTax(
  'JP', 'JPY',
  'Both spouses declare foreign listed ETF sales. Japan allows a cost of 5% of proceeds on mature units. The estimate deducts personal allowances and statutory premiums, and includes national pension contributions at age 45, resident levies and the income-based health premium. Kōtō Ward supplies the local rates. The fixed health premium is in the health budget.',
  ['tax-jp-foreign-stocks', 'tax-jp-listed-rates', 'tax-jp-koto-nhi', 'tax-jp-basis', 'tax-jp-basic', 'tax-jp-social', 'tax-jp-pension', 'tax-jp-resident'],
  ({ withdrawalLocal }) => {
    const gain = withdrawalLocal * 0.95 / 2;
    const insuranceIncome = 2 * Math.max(0, gain - localAllowance(gain));
    const fixedHealth = insuranceComponents.reduce((sum, component) => sum + 2 * component[2], 0);
    const health = insuranceComponents.reduce((sum, [rate, cap, fixed]) =>
      sum + Math.min(cap, 2 * fixed + rate * insuranceIncome), 0);
    const pension = 12 * 17_920;
    const afterPremiums = gain - health / 2 - pension;
    const national = taxableThousands(afterPremiums - nationalAllowance(gain)) * 0.15315;
    const local = gain <= 450_000 ? 0 : 5_000 + taxableThousands(afterPremiums - localAllowance(gain)) * 0.05;
    return 2 * (national + local + pension) + health - fixedHealth;
  },
);
