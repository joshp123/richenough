import { registerStandardTax } from './calculation.ts';

// 2026. Private investment in a global equity ETF.
registerStandardTax(
  'MX', 'MXN',
  'Mexico charges 10% on gains from eligible exchange-traded securities. The estimate assumes a global equity ETF listed in Mexico’s international market, such as Vanguard Total World Stock ETF.',
  ['tax-mx-gains', 'tax-mx-vt'],
  ({ withdrawalLocal }) => withdrawalLocal * 0.10,
);
