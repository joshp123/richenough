import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "WF", "XPF",
  "Wallis and Futuna has no personal income tax or tax on securities income or wealth. Local taxes instead include customs, consumption and business levies.",
  ["tax-wf-invest"],
  () => 0,
);
