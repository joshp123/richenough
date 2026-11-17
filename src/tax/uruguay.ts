// 2026. Private investors hold well below 5% of the fund and sell units on the exchange.
import { registerTaxRules } from './tax-rules.ts';

registerTaxRules('UY', {
  currency: 'UYU',
  hasSpecialRegime: true,
  taxOwed: ({ withdrawalLocal }, regime) => regime === 'special' ? {
    taxLocal: 0,
    regimeName: 'New resident tax holiday',
    explanation: 'New residents who qualify and elect IRNR can exempt foreign portfolio gains in the residence year and the following ten tax years. This assumes both spouses independently meet the residence and election conditions.',
    sourceIds: ['tax-uy-holiday'],
  } : {
    taxLocal: withdrawalLocal * 0.20 * 0.12,
    regimeName: 'Standard',
    explanation: 'Uruguay charges 12% on foreign portfolio gains. Using the annual election to treat 20% of open-market sale proceeds as gain gives 2.4% of proceeds in the mature-portfolio scenario.',
    sourceIds: ['tax-uy-foreign-source', 'tax-uy-ficto'],
  },
});
