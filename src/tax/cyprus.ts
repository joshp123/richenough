import { registerStandardTax } from './calculation.ts';

// 2026. Use secondary-market sales of a qualifying accumulating ETF by a private investor.
registerStandardTax(
  'CY', 'EUR',
  'Cyprus exempts private gains on secondary-market sales of qualifying securities, including ETF units. GeSY applies to dividends, interest and other defined income. The estimate uses an accumulating ETF, with gains from sales and no distribution.',
  ['tax-cy-securities', 'tax-cy-nondom', 'tax-cy-tax-return', 'tax-cy-gesy'], () => 0,
);
