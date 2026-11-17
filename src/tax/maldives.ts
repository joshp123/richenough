import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "MV", "MVR",
  "Foreign nationals with legal stay who satisfy the 183-day residence test and are not married to Maldivians are classed as temporary residents. The Maldives tax these taxpayers on local income only, so the foreign equity fund is outside the tax.",
  ["tax-mv-income","tax-mv-residence"],
  () => 0,
);
