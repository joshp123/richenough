import { registerTaxRules } from './tax-rules.ts';

// Law and published rates checked November 2026.
registerTaxRules("MK", {
  currency: "MKD",
  hasSpecialRegime: true,
  taxOwed: ({ withdrawalLocal }, regime) => regime === 'special' ? {
    taxLocal: 0,
    regimeName: "Securities held over two years",
    explanation: "The tax rate on sales of securities and investment fund shares held over two years is 0%.",
    sourceIds: ["tax-mk-base","tax-mk-rates"],
  } : {
    taxLocal: 0.09 * withdrawalLocal,
    regimeName: 'Standard',
    explanation: "North Macedonia taxes 90% of the gain on securities and investment fund shares at 10% when held for up to two years.",
    sourceIds: ["tax-mk-base","tax-mk-rates"],
  },
});
