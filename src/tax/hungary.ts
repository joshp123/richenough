import { registerTaxRules } from './tax-rules.ts';

// 2026. Personal Income Tax Act 67/A and 67/B. The special result is for a matured ladder.
registerTaxRules('HU', {
  currency: 'HUF',
  hasSpecialRegime: true,
  taxOwed: ({ withdrawalLocal }, regime) => regime === 'special' ? {
    taxLocal: 0,
    regimeName: 'Mature long-term investment accounts',
    explanation: 'Gains from investments in qualifying TBSZ accounts are exempt after five full years. The couple can open successive accounts and keep the exemption as each matures. The couple must fund the intervening years and may owe tax when selling existing holdings to fund the accounts.',
    sourceIds: ['tax-hu-tbsz', 'tax-hu-tbsz-etfs'],
  } : {
    taxLocal: withdrawalLocal * 0.15,
    regimeName: 'Standard',
    explanation: 'Hungary charges 15% on sale gains from controlled capital market transactions through a qualifying broker. The estimate assumes the ETF is sold in a qualifying transaction.',
    sourceIds: ['tax-hu-pit'],
  },
});
