import { registerStandardTax } from './calculation.ts';

// 2026. Private investment in a global equity ETF.
registerStandardTax(
  'MA', 'MAD',
  'Morocco charges 20% on gains from foreign securities under its foreign-source movable capital rules.',
  ['tax-ma-cgi'],
  ({ withdrawalLocal }) => withdrawalLocal * 0.20,
);
