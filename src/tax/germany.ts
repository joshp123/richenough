import { nominalPortfolioReturn, registerStandardTax } from './calculation.ts';

// 2026: InvStG §§16, 18–20 and EStG §§20, 32d. Equity ETF with at least 51% equities.
// 2026 Vorabpauschale (deemed received in January 2027): 70% of the 3.20% basis rate.
const advanceYield = 0.7 * 0.032;

registerStandardTax(
  'DE', 'EUR',
  'Germany exempts 30% of qualified equity ETF returns, then applies the couple’s €2,000 allowance and 26.375% tax including solidarity surcharge. The annual advance amount is credited against sale gains. This steady-state estimate treats it as prepaid tax and includes at least the annual advance amount.',
  ['tax-de-funds', 'tax-de-advance', 'tax-de-income', 'tax-de-soli'],
  ({ withdrawalLocal, capitalAtStartOfYearLocal }) => {
    const advance = capitalAtStartOfYearLocal * Math.min(advanceYield, nominalPortfolioReturn);
    return Math.max(0, 0.7 * Math.max(withdrawalLocal, advance) - 2_000) * 0.25 * 1.055;
  },
);
