// 2026. Private investors hold well below 5% of the fund and sell units on the exchange.
import { registerTaxRules } from './tax-rules.ts';

// Each spouse needs a 55.70 UI movement certificate annually under the physical-presence route.
const householdCertificateFees = 2 * 55.70 * 6.7067; // UYU per UI on 18 November 2026

registerTaxRules('UY', {
  currency: 'UYU',
  hasSpecialRegime: true,
  taxOwed: ({ withdrawalLocal }, regime) => {
    const standardTax = withdrawalLocal * 0.20 * 0.12;
    if (regime === 'special' && householdCertificateFees < standardTax) {
      return {
        taxLocal: householdCertificateFees,
        regimeName: 'New resident tax holiday',
        explanation: 'New residents who qualify and elect IRNR can exempt foreign portfolio gains in the residence year and the following ten tax years. The couple uses the physical-presence route. Each spouse spends more than 183 days a year in Uruguay and certifies residence annually. The estimate includes both annual migration certificate fees.',
        sourceIds: ['tax-uy-holiday', 'tax-uy-holiday-residence', 'tax-uy-residence-certificate', 'tax-uy-migration-certificate', 'tax-uy-index-unit'],
      };
    }
    return {
      taxLocal: standardTax,
      regimeName: 'Standard',
      explanation: 'Uruguay charges 12% on foreign portfolio gains. Using the annual election to treat 20% of open-market sale proceeds as gain gives 2.4% of proceeds in the mature-portfolio scenario.',
      sourceIds: ['tax-uy-foreign-source', 'tax-uy-ficto'],
    };
  },
});
