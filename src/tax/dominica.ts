import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "DM", "XCD",
  "Dominica has no capital gains tax. Arrivals who qualify as retirees also benefit from an exemption of foreign income.",
  ["tax-dm-gains"],
  () => 0,
);
