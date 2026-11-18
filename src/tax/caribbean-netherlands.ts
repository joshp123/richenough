import { registerStandardTax } from './calculation.ts';

// 2026. Articles 3, 5 and 11 of the BES Income Tax Act.
registerStandardTax(
  'BQ', 'USD',
  'Bonaire, Sint Eustatius and Saba tax dividends and gains on the sale of a substantial shareholding. The couple sells shares in a foreign accumulating ETF on an exchange, owns less than 5% together and receives no distributions. These sale gains fall outside income tax.',
  ['tax-bq-income', 'tax-bq-shares', 'tax-bq-return'],
  () => 0,
);
