import { registerTaxRules } from './tax-rules.ts';

// 2026 residents. The fund is a qualifying EU UCITS held via a non-blacklisted foreign broker.
// End-year portfolio value approximates opening capital in the constant real-capital scenario.
registerTaxRules('IT', {
  currency: 'EUR',
  hasSpecialRegime: true,
  taxOwed: ({ withdrawalLocal, capitalAtStartOfYearLocal }, regime) => {
    const standard = withdrawalLocal * 0.26 + capitalAtStartOfYearLocal * 0.002;
    // Art. 24-bis, as amended by Law 199/2025 art. 1(25)–(26).
    const lumpSum = 300_000 + 50_000;
    if (regime === 'special' && lumpSum < standard) {
      return {
        taxLocal: lumpSum,
        regimeName: 'New resident flat tax',
        explanation: 'The main applicant pays €300,000 and the spouse €50,000 on eligible foreign income, with relief from IVAFE. Each must have lived outside Italy for at least nine of the preceding ten tax years. The election lasts up to 15 years.',
        sourceIds: ['tax-it-flat', 'tax-it-flat-guide', 'tax-it-ivafe'],
      };
    }
    return {
      taxLocal: standard,
      regimeName: 'Standard',
      explanation: 'Italy taxes gains on qualifying EU equity ETFs at 26% and charges 0.2% IVAFE on their value in an ordinary foreign account.',
      sourceIds: ['tax-it-gains', 'tax-it-ivafe', 'tax-it-flat'],
    };
  },
});
