import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "YE", "YER",
  "This estimate assumes the ETF is issued abroad and the sales take place entirely through a foreign broker. The source rules specifically tax resident individuals’ profits earned in Yemen and foreign funding for activities carried out there. Income earned through a Yemeni business, broker or contract can differ.",
  ["tax-ye-income-tax"],
  () => 0,
);
