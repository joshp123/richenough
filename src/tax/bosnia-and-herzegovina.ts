import { registerStandardTax } from './calculation.ts';

// 2026. Sarajevo uses the Federation of Bosnia and Herzegovina's tax rules.
registerStandardTax(
  ['BA', 'BA-BIH'],
  'BAM',
  'In the Federation of Bosnia and Herzegovina, including Sarajevo, gains from selling listed securities are exempt. Republika Srpska taxes these gains separately.',
  ['tax-ba-oecd', 'tax-ba-entity'],
  () => 0,
);

registerStandardTax(
  'BA-SRP',
  'BAM',
  'Republika Srpska taxes capital gains on listed securities at 13%.',
  ['tax-ba-oecd', 'tax-ba-entity'],
  ({ withdrawalLocal }) => withdrawalLocal * 0.13,
);
