import { registerTaxRules } from './tax-rules.ts';

// 2026. A standard account may elect a 20% deemed cost on listed fund units.
// ISK base is average quarterly value plus contributions. Use opening capital
// as its proxy under the steady-capital scenario.
registerTaxRules('SE', {
  currency: 'SEK',
  hasSpecialRegime: true,
  taxOwed: ({ withdrawalLocal, capitalAtStartOfYearLocal: capital }, regime) => {
    const standard = 0.30 * (withdrawalLocal * 0.8 + 0.004 * capital);
    const savingsAccount = Math.max(0, capital - 600_000) * 0.01065;
    if (regime === 'special' && savingsAccount < standard) {
      return {
        taxLocal: savingsAccount,
        regimeName: 'Investment savings accounts',
        explanation: 'The couple uses Swedish investment savings accounts (ISK). The 2026 tax is 1.065% of asset value above SEK 300,000 per spouse. Transferring an existing holding into an ISK can trigger a one-off taxable disposal.',
        sourceIds: ['tax-se-isk', 'tax-se-deemed'],
      };
    }
    return {
      taxLocal: standard,
      regimeName: 'Standard',
      explanation: 'Sweden taxes 80% of listed fund sale proceeds at 30% under the deemed-cost election. It also charges 0.12% of starting fund value each year on private holdings outside an ISK.',
      sourceIds: ['tax-se-gains', 'tax-se-deemed'],
    };
  },
});
