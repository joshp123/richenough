import { registerTaxRules } from './tax-rules.ts';

// Law and published rates checked November 2026.
registerTaxRules("KR", {
  currency: "KRW",
  hasSpecialRegime: true,
  taxOwed: ({ withdrawalLocal }, regime) => regime === 'special' ? {
    taxLocal: 0,
    regimeName: "New resident foreign securities",
    explanation: "The tax authority applies capital gains tax on foreign shares after five consecutive years of Korean residence. Both spouses must meet the new resident condition. This uses an accumulating ETF listed outside Korea.",
    sourceIds: ["tax-kr-foreign","tax-kr-returns"],
  } : {
    taxLocal: 0.22 * Math.max(0, withdrawalLocal - 5_000_000),
    regimeName: 'Standard',
    explanation: "Korea taxes gains on foreign-listed fund shares at 22% including local income tax, after a KRW 2.5 million allowance each.",
    sourceIds: ["tax-kr-foreign","tax-kr-returns"],
  },
});
