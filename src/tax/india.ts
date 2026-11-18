import { registerStandardTax } from './calculation.ts';

// Tax year 2026/27, Income-tax Act 2025 as amended by the Finance Act 2026.
function capitalGainsTax(gain: number): number {
  const tax = (income: number) => 0.125 * Math.max(0, income - 400_000);
  let withSurcharge = tax(gain);
  if (gain > 5_000_000) {
    withSurcharge = Math.min(1.10 * tax(gain), tax(5_000_000) + gain - 5_000_000);
  }
  if (gain > 10_000_000) {
    withSurcharge = Math.min(1.15 * tax(gain), 1.10 * tax(10_000_000) + gain - 10_000_000);
  }
  return 1.04 * withSurcharge;
}

registerStandardTax(
  'IN', 'INR',
  'India taxes gains on offshore fund units held over 24 months at 12.5%, plus surcharge where applicable and a 4% cess. Each spouse uses a ₹400,000 basic exemption. Resident but Not Ordinarily Resident status can exempt gains received abroad, normally for two to four tax years after a full-time move, depending on the days and years already spent in India.',
  ['tax-in-act', 'tax-in-gains', 'tax-in-residential-status'],
  ({ withdrawalLocal }) => 2 * capitalGainsTax(withdrawalLocal / 2),
);
