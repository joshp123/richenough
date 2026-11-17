import { progressiveTax, registerStandardTax } from './calculation.ts';

// Latest territorial Form 390 uses the US December 2000 code and a local 4% floor.
const lowGainThreshold = 43_850;
const gainBands = [[0, 0.10], [lowGainThreshold, 0.20]] as const;

registerStandardTax(
  'AS', 'USD',
  'American Samoa uses the US tax code as of December 2000 and a local minimum tax of 4% of adjusted gross income. This joint-filer estimate assumes gains held over a year in a US-domiciled global ETF and that neither spouse owes a separate US federal resident tax.',
  ['tax-as-adoption', 'tax-as-floor', 'tax-as-form-390', 'tax-as-schedule-d', 'tax-as-amt'],
  ({ withdrawalLocal }) => {
    const exemptionSteps = Math.ceil(Math.max(0, withdrawalLocal - 193_400) / 2_500);
    const personalExemptions = 5_600 * Math.max(0, 1 - 0.02 * exemptionSteps);
    const regularTaxable = Math.max(0, withdrawalLocal - 7_350 - personalExemptions);
    const amtExemption = Math.max(0, 45_000 - 0.25 * Math.max(0, withdrawalLocal - 150_000));
    const amtTaxable = Math.max(0, withdrawalLocal - amtExemption);
    const amtLowGain = Math.min(amtTaxable, regularTaxable, lowGainThreshold);
    const amtTax = 0.10 * amtLowGain + 0.20 * (amtTaxable - amtLowGain);
    return Math.max(0.04 * withdrawalLocal, progressiveTax(regularTaxable, gainBands), amtTax);
  },
);
