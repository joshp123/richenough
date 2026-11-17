import { registerStandardTax } from './calculation.ts';

// 2026. Private investment in a global equity ETF.
registerStandardTax(
  'JP', 'JPY',
  'Japan charges 20.315% including local inhabitant tax on qualifying listed ETF gains. This assumes the couple remits the sale proceeds to Japan.',
  ['tax-jp-foreign-stocks', 'tax-jp-listed-rates'],
  ({ withdrawalLocal }) => withdrawalLocal * 0.20315,
);
