import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "PH", "PHP",
  "The Philippines taxes foreign nationals on Philippine-source income. Gains on the couple’s foreign ETF are outside this base. Philippine citizens living in the Philippines generally pay tax on worldwide income.",
  ["tax-ph-source","tax-ph-2026"],
  () => 0,
);
