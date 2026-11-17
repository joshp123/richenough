import { registerStandardTax } from './calculation.ts';

// 2026. Private investment in a global equity ETF.
registerStandardTax(
  'OM', 'OMR',
  'Oman has no personal income tax in 2026. The new income tax starts in 2028 at 5% above OMR 42,000 per person, with exemptions and deductions. A lifetime estimate at 2026 rules omits that future tax.',
  ['tax-om-pit'],
  () => 0,
);
