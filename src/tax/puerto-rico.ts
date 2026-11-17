import './united-states.ts';
import { registerTaxRules, taxRulesFor } from './tax-rules.ts';

// The map uses ISO PR while the US data and rule use US-PR.
const rules = taxRulesFor(['US-PR']);
if (rules) registerTaxRules('PR', rules);
