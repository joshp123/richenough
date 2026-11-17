import { progressiveTax, registerStandardTax, type TaxBand } from './calculation.ts';

// Resident over the full year. Thai Revenue Code §§40–41 and 47–48, Orders P.161 and P.162.
const bands: TaxBand[] = [
  [150_000, 0.05], [300_000, 0.1], [500_000, 0.15], [750_000, 0.2],
  [1_000_000, 0.25], [2_000_000, 0.30], [5_000_000, 0.35],
];

registerStandardTax(
  'TH', 'THB',
  'Thailand taxes foreign ETF gains earned while tax-resident from 2024 onward when remitted. This estimate assumes both spouses remit half and each gets a ฿60,000 allowance. LTR’s Wealthy Global Citizen route requires US$500,000 in qualifying Thai assets outside this ETF portfolio.',
  ['tax-th-remittance', 'tax-th-code', 'tax-th-rates', 'tax-th-ltr', 'tax-th-ltr-decree'],
  ({ withdrawalLocal }) => {
    const gainPerPerson = withdrawalLocal / 2;
    return 2 * Math.max(
      progressiveTax(gainPerPerson - 60_000, bands),
      gainPerPerson > 1_000_000 ? 0.005 * gainPerPerson : 0,
    );
  },
);
