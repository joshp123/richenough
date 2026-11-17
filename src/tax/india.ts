import { registerTaxRules } from './tax-rules.ts';

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

registerTaxRules('IN', {
  currency: 'INR',
  hasSpecialRegime: true,
  taxOwed: ({ withdrawalLocal }, regime) => regime === 'special' ? {
    taxLocal: 0,
    regimeName: 'Resident but not ordinarily resident',
    explanation: 'Qualifying newcomers can exclude foreign passive gains when the proceeds are first received abroad. Both spouses need to meet the residence history test. The relief ends after they become ordinarily resident.',
    sourceIds: ['tax-in-act'],
  } : {
    taxLocal: 2 * capitalGainsTax(withdrawalLocal / 2),
    regimeName: 'Standard',
    explanation: 'India taxes the gain on an equity fund held overseas for more than 24 months at 12.5%, plus surcharge where applicable and a 4% cess. Each resident spouse uses a ₹400,000 basic exemption.',
    sourceIds: ['tax-in-act', 'tax-in-gains'],
  },
});
