import { progressiveTax, registerStandardTax, type TaxBand } from './calculation.ts';

// 2026. Income tax law articles 51 and 53. No employment deduction on wholly foreign income.
const bands: TaxBand[] = [[0, 0.08], [27_500, 0.14], [110_000, 0.17], [192_500, 0.20], [247_500, 0.30]];

registerStandardTax(
  'PE', 'PEN',
  'Peru taxes foreign ETF sale gains outside its qualifying exchange and integration arrangements at progressive income tax rates. Each spouse uses their own bands.',
  ['tax-pe-foreign-income', 'tax-pe-2026-uit'],
  ({ withdrawalLocal }) => 2 * progressiveTax(withdrawalLocal / 2, bands),
);
