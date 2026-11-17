import { progressiveTax, registerStandardTax } from './calculation.ts';

const bands = [[0, 0.03], [1_944_000, 0.15], [21_600_000, 0.30], [43_200_000, 0.40]] as const;

// Law 23/053, in force for 2026. The 20% domestic withholding is credited
// against the annual assessment. The portfolio is held with a foreign broker.
registerStandardTax(
  'CD', 'CDF',
  'Resident private capital gains are taxed at 3% to 40%, capped at 30% of taxable income. The model splits the gains equally between spouses and applies each spouse’s 2% reduction to tax on the first three bands.',
  ['tax-cd-irpp', 'tax-cd-act', 'tax-cd-2026-amending'],
  ({ withdrawalLocal }) => {
    const gainPerPerson = Math.floor(withdrawalLocal / 2_000) * 1_000;
    const incomeTax = Math.min(progressiveTax(gainPerPerson, bands), gainPerPerson * 0.30);
    const eligibleTax = Math.min(incomeTax, progressiveTax(Math.min(gainPerPerson, 43_200_000), bands));
    return 2 * (incomeTax - eligibleTax * 0.02);
  },
);
