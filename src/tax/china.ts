import { registerTaxRules } from './tax-rules.ts';

// Law and published rates checked November 2026.
registerTaxRules("CN", {
  currency: "CNY",
  hasSpecialRegime: true,
  taxOwed: ({ withdrawalLocal }, regime) => regime === 'special' ? {
    taxLocal: 0,
    regimeName: "Six-year foreign income rule",
    explanation: "Residents without Chinese domicile can exempt foreign income paid by an overseas entity or person before the six-year test is met. A single absence of more than 30 consecutive days restarts the count. Both spouses must qualify.",
    sourceIds: ["tax-cn-iit","tax-cn-six"],
  } : {
    taxLocal: 0.20 * withdrawalLocal,
    regimeName: 'Standard',
    explanation: "China taxes gains from disposing of foreign securities at 20% once worldwide taxation applies.",
    sourceIds: ["tax-cn-iit","tax-cn-six"],
  },
});
