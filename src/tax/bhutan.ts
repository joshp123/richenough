import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "BT", "BTN",
  "Schedule 3 of the 2025 Income Tax Act exempts a resident individual’s gains from selling private assets, including ETF shares held outside a business. Applies from the 2026 income year.",
  ["tax-bt-act"],
  () => 0,
);
