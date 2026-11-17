import { registerStandardTax } from './calculation.ts';

// Law 4099/2012 art. 103(5) and AADE POL.1032/2015: qualifying EU/EEA UCITS.
// Under Code arts. 5A and 5B, neither lump-sum taxation nor the pension-only
// election improves the ordinary exemption for this fund.
registerStandardTax(
  'GR', 'EUR',
  'Qualifying EU/EEA UCITS sale gains are exempt. The foreign-income flat tax requires a qualifying €500,000 investment and charges €100,000 plus €20,000 for an included spouse. The 7% pensioner option requires a foreign pension.',
  ['tax-gr-ucits', 'tax-gr-incentives'], () => 0,
);
