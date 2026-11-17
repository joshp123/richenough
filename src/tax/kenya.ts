import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "KE", "KES",
  "Kenya’s capital gains tax applies to Kenyan property and specified interests deriving value from Kenya. A broad foreign equity ETF falls outside that scope.",
  ["tax-ke-kra"],
  () => 0,
);
