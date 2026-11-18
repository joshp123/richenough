import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  'TZ', 'TZS',
  'A long-term resident of Tanzania pays 30% on gains from an overseas investment. The short-term resident exemption for foreign income applies for up to two years of Tanzanian residence in a lifetime.',
  ['tax-tz-foreign', 'tax-tz-residence', 'tax-tz-income-act'],
  ({ withdrawalLocal }) => 0.30 * withdrawalLocal,
);
