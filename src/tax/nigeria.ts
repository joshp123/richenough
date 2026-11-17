import { registerStandardTax, progressiveTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "NG", "NGN",
  "Nigeria’s 2026 law includes gains from foreign fund shares in the 0–25% personal income tax scale. The estimate gives each spouse separate bands, before any deduction for local rent.",
  ["tax-ng-act","tax-ng-scope"],
  ({ withdrawalLocal }) => 2 * progressiveTax(withdrawalLocal / 2, [[800_000, 0.15], [3_000_000, 0.18], [12_000_000, 0.21], [25_000_000, 0.23], [50_000_000, 0.25]]),
);
