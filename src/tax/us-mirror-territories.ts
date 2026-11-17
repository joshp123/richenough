import { progressiveTax, registerStandardTax } from './calculation.ts';

// Tax year 2026. The mirror code applies the joint long-term gain schedule locally.
const federalRateSources = ['tax-us-irs-2026', 'tax-us-territories-mirror', 'tax-us-territories-niit'];
const longTermGainTax = ({ withdrawalLocal }: { withdrawalLocal: number }) =>
  progressiveTax(withdrawalLocal - 32_200, [[98_900, 0.15], [613_700, 0.20]]);

registerStandardTax(
  ['GU', 'MP'], 'USD',
  'Guam and the Northern Mariana Islands use the US long-term capital gains brackets for bona fide residents. The model uses a joint return and offshore fund gains, with no local-source rebate or US net investment income tax.',
  federalRateSources,
  longTermGainTax,
);

registerStandardTax(
  'VI', 'USD',
  'The US Virgin Islands uses the US long-term capital gains brackets for bona fide residents. A September 2026 district court ruling held that the net investment income tax does not apply to such residents.',
  [...federalRateSources, 'tax-vi-perkins'],
  longTermGainTax,
);
