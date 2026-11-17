import { registerTaxRules } from './tax-rules.ts';

// Law and published rates checked November 2026.
registerTaxRules("RS", {
  currency: "RSD",
  hasSpecialRegime: true,
  taxOwed: ({ withdrawalLocal }, regime) => regime === 'special' ? {
    taxLocal: 0,
    regimeName: "Securities held over ten years",
    explanation: "A resident can exempt gains on qualifying securities held for more than ten consecutive years. The scenario assumes the couple has held the units long enough or sells units in acquisition order.",
    sourceIds: ["tax-rs-gains"],
  } : {
    taxLocal: 0.15 * withdrawalLocal,
    regimeName: 'Standard',
    explanation: "Serbia taxes gains on listed securities at 15%. The estimate uses an exchange-listed foreign fund treated as a security under the ten-year exemption.",
    sourceIds: ["tax-rs-gains"],
  },
});
