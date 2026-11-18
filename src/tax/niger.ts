import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "NE", "XOF",
  "Niger’s 2026 securities income tax charges 7% on a resident’s share sale gains, including foreign gains paid by a nonresident. This assumes shares in an offshore corporate ETF; the exemption for qualifying regional funds does not apply.",
  ["tax-ne-cgi2026"],
  ({ withdrawalLocal }) => 0.07 * withdrawalLocal,
);
