import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "FJ", "FJD",
  "Fiji charges 10% on capital gains from offshore assets owned by full residents. A disposal with up to FJ$30,000 of gain is exempt. The estimate uses one annual sale by each spouse.",
  ["tax-fj-gains","tax-fj-shares"],
  ({ withdrawalLocal }) => withdrawalLocal / 2 <= 30_000 ? 0 : 0.10 * withdrawalLocal,
);
