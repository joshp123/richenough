import { fundDividendYield, nominalPortfolioReturn, progressiveTax, registerStandardTax, type TaxBand } from './calculation.ts';

// 2026. EStG sections 27a and 33 and InvFG section 186.
const ordinaryBands: TaxBand[] = [
  [13_539, 0.20], [21_992, 0.30], [36_458, 0.40], [70_365, 0.48], [104_859, 0.50], [1_000_000, 0.55],
];

registerStandardTax(
  'AT', 'EUR',
  'Austria taxes the gains and deemed income of a reporting ETF at 27.5%, or at ordinary rates if they are lower. The estimate spreads 1.5% annual deemed fund income over the portfolio and adjusts the sale gain for deemed income already taxed. Actual fund reports can also include realised gains inside the fund.',
  ['tax-at-funds', 'tax-at-cap-rate', 'tax-at-income'],
  ({ withdrawalLocal, capitalAtStartOfYearLocal }) => {
    const deemedIncome = capitalAtStartOfYearLocal * fundDividendYield;
    const saleGain = withdrawalLocal * (1 - fundDividendYield / nominalPortfolioReturn);
    const taxableIncome = deemedIncome + saleGain;
    return Math.min(0.275 * taxableIncome, 2 * progressiveTax(taxableIncome / 2, ordinaryBands));
  },
);
