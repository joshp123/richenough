import { registerTaxRules } from './tax-rules.ts';

// Law and published rates checked November 2026.
registerTaxRules("TZ", {
  currency: "TZS",
  hasSpecialRegime: true,
  taxOwed: ({ withdrawalLocal }, regime) => regime === 'special' ? {
    taxLocal: 0,
    regimeName: "Short-term residents (up to two years)",
    explanation: "A resident with at most two years of Tanzanian residence in their lifetime is taxed on Tanzanian income only. Both spouses must qualify.",
    sourceIds: ["tax-tz-foreign","tax-tz-residence"],
  } : {
    taxLocal: 0.30 * withdrawalLocal,
    regimeName: 'Standard',
    explanation: "A long-term resident of Tanzania pays 30% on gains from an overseas investment.",
    sourceIds: ["tax-tz-foreign","tax-tz-residence"],
  },
});
