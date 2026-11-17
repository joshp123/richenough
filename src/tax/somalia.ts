import { registerStandardTax, progressiveTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "SO", "USD",
  "Under federal Somali law, resident individuals pay on worldwide investment gains. The ordinary bands apply through US$18,000 per spouse and the rate above that is 15% on the gain. This is the federal rule used for Mogadishu. Other administrations, including Somaliland, can apply different laws.",
  ["tax-so-income","tax-so-guidance"],
  ({ withdrawalLocal }) => 2 * progressiveTax(withdrawalLocal / 2, [[0, 0], [1_200, 0.06], [6_000, 0.12], [18_000, 0.15]]),
);
