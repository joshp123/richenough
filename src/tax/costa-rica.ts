import { registerStandardTax } from './calculation.ts';

// 2026. Private investment in a global equity ETF.
registerStandardTax(
  'CR', 'CRC',
  'Costa Rica taxes local-source income. Sale gains on foreign ETF units held as private investments fall outside that tax.',
  ['tax-cr-territorial'],
  () => 0,
);
