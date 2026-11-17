import { registerTaxRules } from './tax-rules.ts';

// 2026. Fixed CASS bases use the minimum salary in force on January 1.
const minimumSalary = 4_050;

registerTaxRules('RO', {
  currency: 'RON',
  hasSpecialRegime: true,
  taxOwed: ({ withdrawalLocal }, regime) => {
    const gainPerSpouse = withdrawalLocal / 2;
    const salaryMultiple = gainPerSpouse / minimumSalary;
    const healthBase = salaryMultiple >= 24 ? 24 : salaryMultiple >= 12 ? 12 : salaryMultiple >= 6 ? 6 : 0;
    const rate = regime === 'special' ? 0.03 : 0.16;
    return {
      taxLocal: rate * withdrawalLocal + 2 * 0.10 * minimumSalary * healthBase,
      regimeName: regime === 'special' ? 'Qualifying broker withholding' : 'Standard',
      explanation: regime === 'special'
        ? 'A Romanian-resident broker or qualifying Romanian branch withholds 3% on gains from ETF units held at least 365 days. This estimate adds each spouse’s statutory health contribution.'
        : 'Romania taxes foreign ETF sale gains at 16% on self-assessment. This estimate adds each spouse’s 10% health contribution on fixed bands of six, twelve or twenty-four minimum monthly salaries.',
      sourceIds: ['tax-ro-capital', 'tax-ro-cass'],
    };
  },
});
