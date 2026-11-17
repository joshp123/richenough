import { registerStandardTax } from './calculation.ts';

// FY 2026/27. The modeled fund is foreign listed and has been held for over five years.
registerStandardTax(
  'BD', 'BDT',
  'Bangladesh taxes the modeled foreign fund’s long-held gains at 15%. A surcharge on the tax starts when individual net wealth exceeds Tk 40 million. The listed-share exemption for gains up to Tk 5 million is assumed to apply to domestic listings.',
  ['tax-bd-budget', 'tax-bd-gains', 'tax-bd-surcharge'],
  ({ withdrawalLocal, capitalAtStartOfYearLocal }) => {
    const wealth = capitalAtStartOfYearLocal / 2;
    const surcharge = wealth > 500_000_000 ? 0.35
      : wealth > 200_000_000 ? 0.30
      : wealth > 100_000_000 ? 0.20
      : wealth > 40_000_000 ? 0.10 : 0;
    return withdrawalLocal * 0.15 * (1 + surcharge);
  },
);
