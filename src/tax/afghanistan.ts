import { registerStandardTax, progressiveTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "AF", "AFN",
  "Afghanistan’s published Income Tax Law taxes residents on worldwide income and expressly includes gains on shares. Each spouse uses the annual individual bands. This estimate assumes continued application of the published scale and the ability to access a lawful offshore account.",
  ["tax-af-income","tax-af-manual"],
  ({ withdrawalLocal }) => 2 * progressiveTax(withdrawalLocal / 2, [[0, 0], [60_000, 0.02], [150_000, 0.10], [1_200_000, 0.20]]),
);
