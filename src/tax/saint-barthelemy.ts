import './france.ts';
import { registerTaxRules, taxRulesFor } from './tax-rules.ts';

const france = taxRulesFor(['FR'])!;

// Article LO6214-4, still in force in 2026. Model the household on arrival.
registerTaxRules('BL', {
  ...france,
  taxOwed: (year, regime) => {
    const result = france.taxOwed(year, regime);
    return {
      ...result,
      explanation: 'France taxes new arrivals’ worldwide gains during their first five years on Saint-Barthélemy. The island has no local personal income tax once they qualify for local tax residence. French social contributions are governed separately.',
      sourceIds: [...result.sourceIds, 'tax-bl-residence', 'tax-bl-contributions', 'tax-bl-social'],
    };
  },
});
