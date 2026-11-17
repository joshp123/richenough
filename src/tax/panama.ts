import { registerStandardTax } from './calculation.ts';

// 2026. Private investment in a global equity ETF.
registerStandardTax(
  'PA', 'PAB',
  'Panama taxes income from Panamanian sources. The couple holds its global ETF outside Panama.',
  ['tax-pa-territorial'],
  () => 0,
);
