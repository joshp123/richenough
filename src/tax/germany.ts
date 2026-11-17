import { nominalPortfolioReturn, registerStandardTax } from './calculation.ts';

// 2026: InvStG §§16, 18–20 and EStG §§20, 32d. Equity ETF with at least 51% equities.
// 2026 Vorabpauschale (deemed received in January 2027): 70% of the 3.20% basis rate.
const advanceYield = 0.7 * 0.032;

function ordinaryTaxPerPerson(income: number): number {
  if (income <= 12_348) return 0;
  if (income <= 17_799) {
    const y = (income - 12_348) / 10_000;
    return (914.51 * y + 1_400) * y;
  }
  if (income <= 69_878) {
    const z = (income - 17_799) / 10_000;
    return (173.1 * z + 2_397) * z + 1_034.87;
  }
  if (income <= 277_825) return 0.42 * income - 11_135.63;
  return 0.45 * income - 19_470.38;
}

registerStandardTax(
  'DE', 'EUR',
  'Germany exempts 30% of qualified equity ETF returns and gives the couple a €2,000 allowance. The couple can elect ordinary income tax if cheaper than 26.375% including solidarity surcharge. The annual advance amount is credited against sale gains. This steady-state estimate treats it as prepaid tax and includes at least the annual advance amount.',
  ['tax-de-funds', 'tax-de-advance', 'tax-de-income', 'tax-de-soli', 'tax-de-ordinary-2026'],
  ({ withdrawalLocal, capitalAtStartOfYearLocal }) => {
    const advance = capitalAtStartOfYearLocal * Math.min(advanceYield, nominalPortfolioReturn);
    const taxableGain = Math.max(0, 0.7 * Math.max(withdrawalLocal, advance) - 2_000);
    const flatTax = taxableGain * 0.25 * 1.055;
    const incomeTax = 2 * Math.floor(ordinaryTaxPerPerson(Math.floor((taxableGain - 72) / 2)));
    const solidarity = Math.min(0.055 * incomeTax, 0.119 * Math.max(0, incomeTax - 40_700));
    return Math.min(flatTax, incomeTax + solidarity);
  },
);
