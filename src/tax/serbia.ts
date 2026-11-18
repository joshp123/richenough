import { registerTaxRules } from './tax-rules.ts';

// Law and published rates checked November 2026.
registerTaxRules("RS", {
  currency: "RSD",
  hasSpecialRegime: true,
  taxOwed: ({ withdrawalLocal }, regime) => regime === 'special' ? {
    taxLocal: 0,
    regimeName: "Shares held for at least ten years",
    explanation: "A resident can exempt gains on qualifying shares held for at least ten consecutive years. The estimate assumes that the couple sells shares in a foreign corporate ETF that qualify as securities and meet the holding period.",
    sourceIds: ["tax-rs-gains","tax-rs-gains-holding"],
  } : {
    taxLocal: 0.15 * withdrawalLocal,
    regimeName: 'Standard',
    explanation: "Serbia taxes gains on listed securities at 15%.",
    sourceIds: ["tax-rs-gains"],
  },
});
