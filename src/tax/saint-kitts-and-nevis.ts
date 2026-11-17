import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "KN", "XCD",
  "St Kitts and Nevis does not charge personal income tax on this household’s long-held private investments.",
  ["tax-kn-income","tax-kn-retire"],
  () => 0,
);
