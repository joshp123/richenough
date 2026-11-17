import { registerStandardTax } from './calculation.ts';

// 2026. Private investment in a global equity ETF.
registerStandardTax(
  'MY', 'MYR',
  'Malaysia generally exempts individuals’ private ETF sale gains. Foreign investment income received in Malaysia can also qualify for a conditional exemption through 2036.',
  ['tax-my-gains'],
  () => 0,
);
