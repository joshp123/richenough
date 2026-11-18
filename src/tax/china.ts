import { registerTaxRules } from './tax-rules.ts';

// Law and published rates checked November 2026.
registerTaxRules("CN", {
  currency: "CNY",
  hasSpecialRegime: true,
  taxOwed: ({ withdrawalLocal }, regime) => regime === 'special' ? {
    taxLocal: 0,
    regimeName: "Six-year foreign income rule",
    explanation: "Both spouses must remain non-domiciled and receive the foreign income from an overseas payer. They can keep the exemption by taking a trip outside mainland China of more than 30 consecutive days before each six-year period ends, while maintaining tax residence in China.",
    sourceIds: ["tax-cn-iit","tax-cn-six","tax-cn-six-reset"],
  } : {
    taxLocal: 0.20 * withdrawalLocal,
    regimeName: 'Standard',
    explanation: "China taxes gains from disposing of foreign securities at 20% once worldwide taxation applies.",
    sourceIds: ["tax-cn-iit","tax-cn-six"],
  },
});
