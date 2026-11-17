import { progressiveTax, registerStandardTax, type TaxBand } from './calculation.ts';

// The two applicable 2026 rates are enacted. The bands below use the latest
// published 2025 peso thresholds until ARCA publishes the 2026 indexed values.
const exemption = 384_728_044.57;
const wealthBands: TaxBand[] = [[exemption, 0.005], [exemption + 40_107_213.86, 0.0075]];

registerStandardTax(
  'AR', 'ARS',
  'Argentina charges 15% on sales of foreign ETF units held and traded overseas. The individual wealth tax includes offshore holdings. The estimate uses the 2026 rates and the latest published 2025 peso thresholds pending indexation.',
  ['tax-ar-gains', 'tax-ar-wealth-rates', 'tax-ar-wealth-thresholds'],
  ({ withdrawalLocal, capitalAtStartOfYearLocal }) =>
    withdrawalLocal * 0.15 + 2 * progressiveTax(capitalAtStartOfYearLocal / 2, wealthBands),
);
