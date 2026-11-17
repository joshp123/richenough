import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "HT", "HTG",
  "Haiti’s new Fiscal Code taxes residents on worldwide income. It specifies a 20% final charge on gains from selling shares, including the foreign ETF share sales used here. The code took effect on 1 October 2026.",
  ["tax-ht-fiscal-2026"],
  ({ withdrawalLocal }) => withdrawalLocal * 0.20,
);
