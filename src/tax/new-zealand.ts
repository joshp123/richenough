import { fundDividendYield, nominalPortfolioReturn, progressiveTax, type TaxBand } from './calculation.ts';
import { registerTaxRules } from './tax-rules.ts';

// 2026–27. The mature offshore ETF is passive. Model gain under the FDR or CV rules.
const bands: TaxBand[] = [[0, 0.105], [15_600, 0.175], [53_500, 0.30], [78_100, 0.33], [180_000, 0.39]];

registerTaxRules('NZ', {
  currency: 'NZD',
  hasSpecialRegime: false,
  taxOwed: ({ capitalAtStartOfYearLocal: capital }) => {
    // Purchase cost is unavailable. At or below NZ$50,000 of total market value
    // per spouse, use dividends only as an approximation to the cost exemption.
    const taxableYield = capital <= 100_000 ? fundDividendYield : Math.min(0.05, nominalPortfolioReturn);
    return {
      taxLocal: 2 * progressiveTax(capital * taxableYield / 2, bands),
      regimeName: 'Standard',
      explanation: 'New Zealand’s foreign investment fund rules usually tax eligible offshore portfolios on 5% of opening value every year, even with no sales. The estimate assumes a 7% nominal return. Actual tax can fall in weaker years. It uses market value as a proxy for the small-portfolio purchase-cost exemption. The transitional resident exemption for qualifying newcomers covers foreign investment fund income for about four years.',
      sourceIds: ['tax-nz-fif', 'tax-nz-rates', 'tax-nz-fif-guide', 'tax-nz-transition'],
    };
  },
});
