import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "DJ", "DJF",
  "Djibouti’s financial income charge covers gains on direct interests in companies under Djiboutian law. The estimate assumes sale of shares in an offshore corporate accumulation fund. Cash dividends and other types of financial income have separate rules.",
  ["tax-dj-gains","tax-dj-budget-2026"],
  () => 0,
);
