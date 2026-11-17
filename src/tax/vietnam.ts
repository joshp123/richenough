import { registerStandardTax } from './calculation.ts';

// 2026. Private investment in a global equity ETF.
registerStandardTax(
  'VN', 'VND',
  'Vietnam levies 0.1% of outright securities sale proceeds. The estimate treats the foreign listed ETF as a security and excludes Vietnam’s new relief for qualifying domestic funds.',
  ['tax-vn-pit'],
  ({ withdrawalLocal }) => withdrawalLocal * 0.001,
);
