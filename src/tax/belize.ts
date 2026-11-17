import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "BZ", "BZD",
  "Belize has no individual capital gains tax on the sale of a privately held foreign equity fund. The Qualified Retirement Program also exempts foreign income. At 45, an applicant with qualifying investment income can meet its age and income conditions.",
  ["tax-bz-capital","tax-bz-qrp","tax-bz-qrp-exemption"],
  () => 0,
);
