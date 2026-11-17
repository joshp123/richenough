import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "EG", "EGP",
  "Egypt taxes residents’ foreign gains where their commercial, industrial or professional activity is centred in Egypt. The estimate assumes a couple holding a foreign fund privately and doing no business in Egypt.",
  ["tax-eg-source","tax-eg-gains"],
  () => 0,
);
