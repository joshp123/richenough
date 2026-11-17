import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "JO", "JOD",
  "Jordan taxes foreign gains from investments originating in Jordan at 10%. The estimate assumes the couple accumulated and funded the portfolio abroad before moving.",
  ["tax-jo-source","tax-jo-current"],
  () => 0,
);
