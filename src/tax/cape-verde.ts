import { registerStandardTax } from './calculation.ts';

registerStandardTax(
  'CV', 'CVE',
  'The household aggregates foreign ETF gains, deducts CVE 220,000 per spouse and applies one rate to the remaining gain. In 2026 the rate is 16.5%, 23.1% or 27.5%, selected by each spouse’s share of taxable income.',
  ['tax-cv-irps', 'tax-cv-budget', 'tax-cv-simulator'],
  ({ withdrawalLocal }) => {
    const taxablePerSpouse = Math.max(0, withdrawalLocal / 2 - 220_000);
    const rate = taxablePerSpouse <= 960_000 ? 0.165 : taxablePerSpouse <= 1_800_000 ? 0.231 : 0.275;
    return 2 * Math.round(taxablePerSpouse * rate);
  },
);
