import { progressiveTax, registerStandardTax, type TaxBand } from './calculation.ts';

// Law 23,966 arts. 24–25. Apply the October CPI published on 12 November
// 2026 to ARCA’s 2025 exemption and first band.
const indexFactor = 12_785.9321 / 9_603.8623;
const exemption = 384_728_044.57 * indexFactor;
const wealthBands: TaxBand[] = [[exemption, 0.005], [exemption + 52_664_283.73 * indexFactor, 0.0075]];
const personalAllowance = 6_019_671.36;

registerStandardTax(
  'AR', 'ARS',
  'Argentina taxes offshore ETF sale gains at 15% after each spouse’s unused personal allowance. Each spouse also pays wealth tax on their share of the offshore portfolio above the indexed 2026 exemption.',
  ['tax-ar-gains-law', 'tax-ar-personal', 'tax-ar-wealth-rates', 'tax-ar-wealth-thresholds', 'tax-ar-cpi'],
  ({ withdrawalLocal, capitalAtStartOfYearLocal }) =>
    0.15 * Math.max(0, withdrawalLocal - 2 * personalAllowance)
    + 2 * progressiveTax(capitalAtStartOfYearLocal / 2, wealthBands),
);
