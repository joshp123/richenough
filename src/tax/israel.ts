import { registerTaxRules, type TaxRules } from './tax-rules.ts';

// Law and published rates checked November 2026.
const israelTax: TaxRules = {
  currency: "ILS",
  hasSpecialRegime: true,
  taxOwed: ({ withdrawalLocal }, regime) => regime === 'special' ? {
    taxLocal: 0,
    regimeName: "New immigrants and veteran returning residents",
    explanation: "Qualifying new olim and veteran returning residents can exempt foreign gains for ten years. For arrivals from 2026, reporting is required.",
    sourceIds: ["tax-il-immigrant"],
  } : {
    taxLocal: 0.25 * withdrawalLocal + 0.05 * Math.max(0, withdrawalLocal - 1_443_120),
    regimeName: 'Standard',
    explanation: "Israeli tax on real gains is 25%, plus a combined 5% surtax on investment gains above ILS 721,560 per spouse.",
    sourceIds: ["tax-il-gains","tax-il-immigrant"],
  },
};

// The map embeds these cities in its combined Palestine and Israel geography.
for (const code of ['IL', 'CITY-293397', 'CITY-294801', 'CITY-295530']) {
  registerTaxRules(code, israelTax);
}
