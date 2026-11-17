import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "ML", "XOF",
  "Mali charges 7% on private share gains. The fund exemption requires approval by the West African regional markets authority. This estimate assumes shares of a foreign corporate ETF without that approval.",
  ["tax-ml-capital","tax-ml-budget-2025"],
  ({ withdrawalLocal }) => withdrawalLocal * 0.07,
);
