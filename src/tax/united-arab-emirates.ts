import { registerStandardTax } from './calculation.ts';

// Cabinet Decision 49 of 2023, art. 1. FTA guide CTGTNP1, example 11.
registerStandardTax(
  'AE', 'AED', 'The UAE excludes passive personal investment gains and income from corporate tax and levies no personal income tax.',
  ['tax-ae-investment', 'tax-ae-guide'], () => 0,
);
