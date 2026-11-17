import { registerStandardTax } from './calculation.ts';

// 2026. Private investment in a global equity ETF.
registerStandardTax(
  'BR', 'BRL',
  'Brazil charges 15% on realised gains from foreign investment funds under the annual offshore investment rules.',
  ['tax-br-offshore'],
  ({ withdrawalLocal }) => withdrawalLocal * 0.15,
);
