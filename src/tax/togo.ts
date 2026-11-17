import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "TG", "XOF",
  "Togo’s private capital gains charge covers share sales in Togolese companies and qualifying local mining interests. Foreign investment distributions fall under separate income rules. The estimate assumes a foreign corporate accumulation fund with no qualifying local interest.",
  ["tax-tg-gazette","tax-tg-gains-2026"],
  () => 0,
);
