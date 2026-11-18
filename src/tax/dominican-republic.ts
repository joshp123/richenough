import { progressiveTax, registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  'DO', 'DOP',
  'The Dominican Republic taxes foreign ETF gains at progressive income tax rates. For new foreign residents, foreign investment income is exempt until the third tax year after they become resident.',
  ['tax-do-rates', 'tax-do-gains', 'tax-do-new-residents'],
  ({ withdrawalLocal }) => 2 * progressiveTax(withdrawalLocal / 2, [[416_220, 0.15], [624_329, 0.20], [867_123, 0.25]]),
);
