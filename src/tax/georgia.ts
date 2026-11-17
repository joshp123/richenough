import { registerStandardTax } from './calculation.ts';

// Georgian Tax Code arts. 82(1)(u) and 104: foreign-source gains of resident individuals.
registerStandardTax(
  'GE', 'GEL', 'Georgia exempts foreign-source income of resident individuals, including gains from a foreign ETF.',
  ['tax-ge-code'], () => 0,
);
