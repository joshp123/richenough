import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "LK", "LKR",
  "Sri Lanka taxes gains on offshore investment assets at 15% from 3 June 2026. The small-gain exemption does not apply to a disposal with gains above LKR 50,000.",
  ["tax-lk-cgt"],
  ({ withdrawalLocal }) => withdrawalLocal > 100_000 ? 0.15 * withdrawalLocal : 0,
);
