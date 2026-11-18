import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  'KR', 'KRW',
  'South Korea taxes foreign-listed ETF gains at 22%, including local tax, after a KRW 2.5 million allowance per spouse. The newcomer foreign-securities exemption applies during the first five years of continuous residence. Foreign-listed ETF gains are outside the National Health Insurance income base.',
  ['tax-kr-foreign', 'tax-kr-returns', 'tax-kr-nhis-income'],
  ({ withdrawalLocal }) => 0.22 * Math.max(0, withdrawalLocal - 5_000_000),
);
