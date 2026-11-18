import { registerTaxRules } from './tax-rules.ts';

// General Income Tax Law, articles 13 and 41. Special residence conditions as amended in 2026.
registerTaxRules('SM', {
  currency: 'EUR',
  hasSpecialRegime: true,
  taxOwed: ({ withdrawalLocal }, regime) => {
    const standardTax = 0.10 * withdrawalLocal;
    const atypicalTax = 2 * Math.min(100_000, Math.max(10_000, 0.07 * withdrawalLocal / 2));
    if (regime === 'special' && atypicalTax < standardTax) {
      return {
        taxLocal: atypicalTax,
        regimeName: 'Atypical residence',
        explanation: 'Approved first-time residents with foreign income can pay 7% on foreign gains for up to 15 years. Each spouse pays between €10,000 and €100,000 a year. Applicants can rent locally and must have their own health cover and sufficient resources. The €1,000 application fee is one-off.',
        sourceIds: ['tax-sm-atypical', 'tax-sm-atypical-2026', 'tax-sm-atypical-application', 'tax-sm-irg'],
      };
    }
    return {
      taxLocal: standardTax,
      regimeName: 'Standard',
      explanation: 'San Marino taxes gains on financial instruments at a separate 10% rate from 2026.',
      sourceIds: ['tax-sm-irg'],
    };
  },
});
