import { registerTaxRules } from './tax-rules.ts';
import { progressiveTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerTaxRules("DO", {
  currency: "DOP",
  hasSpecialRegime: true,
  taxOwed: ({ withdrawalLocal }, regime) => regime === 'special' ? {
    taxLocal: 0,
    regimeName: "New residents (first three years)",
    explanation: "The Dominican Republic exempts foreign investment gains from its tax base for the first three years of residence.",
    sourceIds: ["tax-do-rates","tax-do-gains"],
  } : {
    taxLocal: 2 * progressiveTax(withdrawalLocal / 2, [[416_220, 0.15], [624_329, 0.20], [867_123, 0.25]]),
    regimeName: 'Standard',
    explanation: "Dominican residents pay progressive income tax on gains from foreign investments after the third year.",
    sourceIds: ["tax-do-rates","tax-do-gains"],
  },
});
