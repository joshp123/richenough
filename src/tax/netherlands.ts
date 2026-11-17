import { nominalPortfolioReturn, registerStandardTax } from './calculation.ts';

// 2026. Fiscal partners hold only listed securities, equally, with no debt or other income.
registerStandardTax(
  'NL', 'EUR',
  'Box 3 taxes 6% deemed investment return above the couple’s €118,714 joint allowance at 36%, less general tax credits. An actual return below the deemed taxable return can reduce the bill. Withdrawals do not measure actual return, which includes unsold gains.',
  ['tax-nl-box3', 'tax-nl-credits', 'tax-nl-actual'],
  ({ capitalAtStartOfYearLocal }) => {
    const deemedReturn = 0.06 * Math.max(0, capitalAtStartOfYearLocal - 118_714);
    const actualReturn = capitalAtStartOfYearLocal * nominalPortfolioReturn;
    const incomePerPerson = Math.min(deemedReturn, actualReturn) / 2;
    const credit = Math.max(0, 3115 - 0.06398 * Math.max(0, incomePerPerson - 29_736));
    return 2 * Math.max(0, 0.36 * incomePerPerson - credit);
  },
);
