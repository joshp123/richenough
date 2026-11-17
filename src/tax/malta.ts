import { registerStandardTax } from './calculation.ts';

// Income Tax Act art. 4 and MTCA remittance-basis guidelines. A foreign couple
// whose existing domicile remains abroad need not obtain a special residence programme.
registerStandardTax(
  'MT', 'EUR',
  'A resident who remains domiciled abroad is exempt on foreign capital gains even when remitted. The €5,000 minimum tax tests foreign income such as dividends, distinct from foreign sale gains. This estimate uses an accumulating foreign ETF.',
  ['tax-mt-remittance', 'tax-mt-income'], () => 0,
);
