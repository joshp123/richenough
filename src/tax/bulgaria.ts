import { registerStandardTax } from './calculation.ts';

// 2026. Private investment in a global equity ETF.
registerStandardTax(
  'BG', 'EUR',
  'Gains on a qualifying ETF sold on an EU or EEA regulated market are exempt. The venue must be a regulated market under the securities law. The standard scenario assumes an eligible venue.',
  ['tax-bg-nra'],
  () => 0,
);
