import { registerStandardTax } from './calculation.ts';

// Kōtō Ward, 2026–27. Use the same benchmark as the fixed health-cover entry.
// Each component has an annual household cap and a fixed charge per person.
const insuranceComponents = [
  [0.0751, 670_000, 47_600],
  [0.0280, 260_000, 17_600],
  [0.0243, 170_000, 17_800],
  [0.0027, 30_000, 1_873],
] as const;

registerStandardTax(
  'JP', 'JPY',
  'Japan charges 20.315% on qualifying listed ETF gains. The estimate assumes declared gains remitted from abroad. It also includes the income-based part of National Health Insurance using Kōtō Ward’s rates. Premiums use the previous year’s income and vary by municipality.',
  ['tax-jp-foreign-stocks', 'tax-jp-listed-rates', 'tax-jp-koto-nhi'],
  ({ withdrawalLocal }) => {
    const insuranceIncome = 2 * Math.max(0, withdrawalLocal / 2 - 430_000);
    // At income levels where the basic deduction shrinks, all components are already capped.
    const healthContribution = insuranceComponents.reduce((total, [rate, cap, fixedPerSpouse]) =>
      total + Math.min(rate * insuranceIncome, cap - 2 * fixedPerSpouse), 0);
    return withdrawalLocal * 0.20315 + healthContribution;
  },
);
