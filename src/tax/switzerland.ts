import { fundDividendYield, registerStandardTax } from './calculation.ts';
import { capitalCommuneTaxes, wealthSamples, zurichIncomeTaxes } from './swiss-capitals.ts';

// Eurostat NUTS 2024, Swiss cantons. The ESTV table uses each cantonal capital.
const cantons: Record<string, string> = {
  VD: '011', VS: '012', GE: '013',
  BE: '021', FR: '022', SO: '023', NE: '024', JU: '025',
  BS: '031', BL: '032', AG: '033',
  ZH: '040',
  GL: '051', SH: '052', AR: '053', AI: '054', SG: '055', GR: '056', TG: '057',
  LU: '061', UR: '062', SZ: '063', OW: '064', NW: '065', ZG: '066',
  TI: '070',
};

function interpolateTax(capital: number, taxes: number[]): number {
  if (capital <= wealthSamples[0]) return taxes[0];
  const index = wealthSamples.findIndex((sample) => sample > capital);
  const upper = index < 0 ? wealthSamples.length - 1 : index;
  const step = wealthSamples[upper] - wealthSamples[upper - 1];
  const share = (capital - wealthSamples[upper - 1]) / step;
  return taxes[upper - 1] + share * (taxes[upper] - taxes[upper - 1]);
}

// 2026 AHV/IV/EO rules for people without employment or pensions. Each spouse's
// base is half the couple's wealth, rounded down to CHF 50,000. Fund income is
// ordinary investment income and does not enter the pension-income multiplier.
function socialInsurance(capital: number): number {
  const steps = Math.max(0, Math.floor((capital / 2 - 300_000) / 50_000));
  const contribution = 530 + 106 * Math.min(29, steps) + 159 * Math.max(0, steps - 29);
  return 2 * Math.min(26_500, contribution);
}

for (const [canton, nuts] of Object.entries(cantons)) {
  const codes = [`CH-${canton}`, `NUTS-CH${nuts}`];
  if (canton === 'ZH') codes.push('CH', 'CITY-2657896');
  if (canton === 'GE') codes.push('CITY-2660646');
  registerStandardTax(
    codes, 'CHF',
    'Private ETF sale gains are exempt. The estimate uses the cantonal capital’s federal, cantonal and municipal tax on net wealth and 1.5% illustrative taxable fund income. It also includes compulsory AHV/IV/EO contributions for a couple without employment.'
      + (canton === 'ZH' ? ' Zürich also charges a 5% administration fee on these contributions and allows the contributions against income.' : ''),
    ['tax-ch-estv', 'tax-ch-funds', 'tax-ch-ahv', 'tax-fund-vanguard', ...(canton === 'ZH' ? ['tax-ch-zh-fee', 'tax-ch-zh-income'] : [])],
    ({ capitalAtStartOfYearLocal: capital }) => {
      const taxes = interpolateTax(capital, capitalCommuneTaxes[canton]);
      const contributions = socialInsurance(capital);
      if (canton !== 'ZH') return taxes + contributions;
      // ESTV sampled income at 1.5% of capital. Look up the income tax alone
      // at the reduced income, keeping wealth tax at the full portfolio value.
      const before = interpolateTax(capital, zurichIncomeTaxes);
      const after = interpolateTax(capital - contributions / fundDividendYield, zurichIncomeTaxes);
      return taxes - before + after + contributions * 1.05;
    },
  );
}
