import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "BF", "XOF",
  "The securities gains levy covers shares with a Burkinabè connection. The tax also exempts small disposals by shareholders who hold less than 25% under the statutory ownership tests. An ordinary sale on a foreign exchange of a small stake in a foreign corporate ETF incurs no modeled tax.",
  ["tax-bf-securities"],
  () => 0,
);
