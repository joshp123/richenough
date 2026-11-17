import { registerStandardTax } from './calculation.ts';

// Cyprus Income Tax Law securities exemption. Use an accumulating fund and private investor.
registerStandardTax(
  'CY', 'EUR',
  'Cyprus exempts gains on the sale of qualifying securities, including ETF units. Non-dom status exempts qualifying dividends from defence contribution. With an accumulating ETF and sale gains only, there are no dividends to assess for defence or health contributions.',
  ['tax-cy-securities', 'tax-cy-nondom', 'tax-cy-tax-return'], () => 0,
);
