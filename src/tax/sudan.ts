import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "SD", "SDG",
  "Sudan’s capital gains tax covers disposals of taxable assets in Sudan, including shares. The model assumes an ETF issued overseas and sold through a foreign broker. The ordinary income tax separately excludes individuals’ capital gains.",
  ["tax-sd-capital-gains","tax-sd-current-tax-system","tax-sd-ordinary-income"],
  () => 0,
);
