import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "KH", "KHR",
  "Cambodia’s 20% capital gains tax extends to foreign securities held by a resident. The separate relief for qualifying Cambodian securities does not apply to a global fund abroad.",
  ["tax-kh-prakas","tax-kh-guidance"],
  ({ withdrawalLocal }) => 0.20 * withdrawalLocal,
);
