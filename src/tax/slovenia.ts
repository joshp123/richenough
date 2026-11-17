import { registerStandardTax } from './calculation.ts';

// 2026, private buy-and-hold investor.
registerStandardTax(
  'SI', 'EUR',
  'Slovenia exempts gains on ETF units held at least 15 years. The mature-portfolio estimate assumes the couple sells units past that threshold.',
  ['tax-si-securities'],
  () => 0,
);
