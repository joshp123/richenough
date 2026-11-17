import { registerStandardTax } from './calculation.ts';

// 2026, private buy-and-hold investor.
registerStandardTax(
  'LU', 'EUR',
  'Luxembourg exempts private gains on a minority holding of listed fund shares sold after more than six months.',
  ['tax-lu-gains'],
  () => 0,
);
