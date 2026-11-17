import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "AI", "XCD",
  "Anguilla has no personal income tax on private investment gains. The Universal Social Levy applies to remuneration.",
  ["tax-ai-income","tax-ai-levy"],
  () => 0,
);
