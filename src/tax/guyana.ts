import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "GY", "GYD",
  "The estimate assumes the new residents keep their foreign domicile and sell foreign ETF units held for more than one year and up to 25 years. Guyana charges each spouse 20% if their net gain exceeds G$500,000. Foreign holdings of residents who remain domiciled abroad are excluded from the annual property tax.",
  ["tax-gy-gains","tax-gy-guide","tax-gy-wealth"],
  ({ withdrawalLocal }) => withdrawalLocal / 2 > 500_000 ? withdrawalLocal * 0.20 : 0,
);
