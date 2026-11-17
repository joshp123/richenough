import { progressiveTax, type TaxBand } from './calculation.ts';
import { registerTaxRules } from './tax-rules.ts';

// Tax year 2026. Married filing jointly, no dependants, no other income, ordinary
// long-term gains on sales of a US-domiciled global equity ETF. Full-year resident.
const federalSources = ['tax-us-irs-2026', 'tax-us-niit'];
const excess = (amount: number, threshold: number) => Math.max(0, amount - threshold);

function federalTax(gain: number): number {
  const taxable = excess(gain, 32_200);
  return progressiveTax(taxable, [[98_900, 0.15], [613_700, 0.20]])
    + 0.038 * excess(gain, 250_000);
}

interface StateTax {
  calculate(gain: number): number;
  sources?: string[];
  explanation?: string;
}

const flat = (rate: number, deduction = 0, credit = 0): StateTax => ({
  calculate: gain => excess(rate * excess(gain, deduction), credit),
});

const graduated = (deduction: number, bands: TaxBand[], credit = 0): StateTax => ({
  calculate: gain => excess(progressiveTax(excess(gain, deduction), bands), credit),
});

const states: Record<string, StateTax> = {
  AK: flat(0), FL: flat(0), MO: flat(0), NH: flat(0), NV: flat(0),
  SD: flat(0), TN: flat(0), TX: flat(0), WY: flat(0),
  AL: {
    calculate: gain => progressiveTax(
      excess(gain, 7_000 + federalTax(gain)), [[0, .02], [1_000, .04], [6_000, .05]],
    ),
  },
  AZ: { calculate: gain => .025 * excess(.75 * gain, 32_200) },
  AR: { calculate: gain => excess(progressiveTax(
    excess(Math.min(gain, 10_000_000) * .50, 4_940), [[0, .02], [4_600, .039]],
  ), 58) },
  CA: {
    calculate(gain) {
      const taxable = excess(gain, 11_800);
      const credit = excess(316, 12 * Math.ceil(excess(gain, 521_561) / 2_500));
      const renterCredit = gain <= 111_660 ? 120 : 0;
      return excess(progressiveTax(taxable, [[0, .01], [22_912, .02], [54_314, .04],
        [85_722, .06], [118_996, .08], [150_394, .093], [768_218, .103],
        [921_854, .113], [1_536_426, .123]]), credit + renterCredit) + .01 * excess(taxable, 1_000_000);
    },
    sources: ['tax-us-ca'],
  },
  CO: {
    // Colorado caps the federal deduction addback for sufficiently high AGI.
    calculate: gain => .044 * excess(gain, gain >= 300_000 ? 4_000 : 32_200),
  },
  CT: {
    calculate(gain) {
      const exemption = excess(24_000, 1_000 * Math.ceil(excess(gain, 48_000) / 1_000));
      const taxable = excess(gain, exemption);
      const lowerBand = excess(20_000, 2_000 * Math.ceil(excess(gain, 113_000) / 5_000));
      return progressiveTax(taxable, [[0, .045], [100_000, .055], [200_000, .06],
        [400_000, .065], [500_000, .069], [1_000_000, .0699]])
        - .025 * Math.min(taxable, lowerBand)
        + Math.min(500, 50 * Math.ceil(excess(gain, 210_000) / 5_000))
        + Math.min(6_300, 180 * Math.ceil(excess(Math.min(gain, 1_000_000), 400_000) / 5_000)
          + 100 * Math.ceil(excess(gain, 1_000_000) / 5_000));
    },
  },
  DC: graduated(32_200, [[0, .04], [10_000, .06], [40_000, .065], [60_000, .085],
    [250_000, .0925], [500_000, .0975], [1_000_000, .1075]]),
  DE: graduated(6_500, [[2_000, .022], [5_000, .039], [10_000, .048], [20_000, .052],
    [25_000, .0555], [60_000, .066]], 220),
  GA: flat(.0499, 30_000),
  HI: {
    calculate(gain) {
      const taxable = excess(gain, 11_088);
      return Math.min(.0725 * taxable, progressiveTax(taxable, [[0, .014], [19_200, .032],
        [28_800, .055], [38_400, .064], [48_000, .068], [72_000, .072], [96_000, .076],
        [250_000, .079], [350_000, .0825], [450_000, .09], [550_000, .1], [650_000, .11]]));
    },
  },
  IA: { ...flat(.038, 32_200, 80), sources: ['tax-us-ia'] },
  ID: flat(.053, 41_822),
  IL: { calculate: gain => .0495 * excess(gain, gain > 500_000 ? 0 : 5_850) },
  IN: { ...flat(.0295, 2_000), sources: ['tax-us-in'] },
  KS: graduated(26_560, [[0, .052], [46_000, .0558]]),
  KY: flat(.035, 3_360),
  LA: flat(.03, 25_750),
  MA: {
    calculate: gain => .05 * excess(gain, 8_800) + .04 * excess(gain, 8_800 + 1_107_750),
    sources: ['tax-us-ma'],
  },
  MD: {
    calculate: gain => progressiveTax(marylandTaxable(gain), [[0, .02], [1_000, .03],
      [2_000, .04], [3_000, .0475], [150_000, .05], [175_000, .0525],
      [225_000, .055], [300_000, .0575], [600_000, .0625], [1_200_000, .065]])
      + (gain > 350_000 ? .02 * gain : 0),
    sources: ['tax-us-md', 'tax-us-md-deduction', 'tax-us-md-gains'],
  },
  ME: {
    calculate: gain => progressiveTax(
      excess(gain, 10_600 + phasedDeduction(gain, 32_200, 200_000, 75_000)),
      [[0, .058], [54_850, .0675], [129_750, .0715]],
    ),
  },
  MI: { ...flat(.0425, 11_800), sources: ['tax-us-mi'] },
  MN: {
    calculate: gain => progressiveTax(
      excess(gain, 30_600), [[0, .0535], [48_700, .068], [193_480, .0785], [337_930, .0985]],
    ) + .01 * excess(gain, 1_000_000),
  },
  MS: flat(.04, 26_600),
  MT: graduated(32_200, [[0, .03], [95_000, .041]]),
  NC: flat(.0399, 25_500),
  ND: { calculate: gain => progressiveTax(excess(.6 * gain, 32_200), [[80_975, .0195], [298_075, .025]]) },
  NE: graduated(17_700, [[0, .0246], [8_250, .0351], [49_530, .0455]], 352),
  NJ: {
    calculate: gain => gain <= 20_000 ? 0 : progressiveTax(excess(gain, 2_000),
      [[0, .014], [20_000, .0175], [50_000, .0245], [70_000, .035],
        [80_000, .05525], [150_000, .0637], [500_000, .0897], [1_000_000, .1075]]),
  },
  NM: graduated(34_700, [[0, .015], [8_000, .032], [25_000, .043],
    [50_000, .047], [100_000, .049], [315_000, .059]]),
  NY: { calculate: newYorkTax, sources: ['tax-us-ny'] },
  OH: {
    calculate(gain) {
      const base = ohioTaxable(gain);
      return base > 26_050 ? 332 + .0275 * (base - 26_050) : 0;
    },
    sources: ['tax-us-oh'],
  },
  OK: graduated(14_700, [[7_500, .025], [9_800, .035], [14_400, .045]]),
  OR: {
    calculate: gain => excess(progressiveTax(oregonTaxable(gain), [[0, .0475], [9_100, .0675],
      [22_800, .0875], [250_000, .099]]), gain <= 200_000 ? 520 : 0),
    sources: ['tax-us-or', 'tax-us-or-subtraction'],
  },
  PA: flat(.0307),
  RI: {
    calculate: gain => progressiveTax(
      excess(gain, phasedDeduction(gain, 32_900, 261_850, 32_950)),
      [[0, .0375], [82_050, .0475], [186_450, .0599]],
    ),
  },
  SC: { calculate: gain => progressiveTax(excess(.56 * gain, 32_200), [[3_640, .03], [18_230, .06]]) },
  UT: {
    calculate: gain => excess(.045 * gain, excess(.06 * 32_200, .013 * excess(gain, 35_202))),
  },
  VA: graduated(19_360, [[0, .02], [3_000, .03], [5_000, .05], [17_000, .0575]]),
  VT: {
    calculate: gain => Math.max(
      progressiveTax(excess(gain, 33_400), [[0, .0335], [82_500, .066], [199_450, .076], [304_000, .0875]]),
      gain > 150_000 ? .03 * gain : 0,
    ),
  },
  WA: {
    calculate: gain => progressiveTax(excess(gain, 290_000), [[0, .07], [1_000_000, .099]]),
    sources: ['tax-us-wa', 'tax-us-wa-law'],
    explanation: 'Washington taxes gains above its $290,000 joint deduction at 7%, rising to 9.9% above $1 million of taxable gains.',
  },
  WI: {
    calculate(gain) {
      const income = gain * .70;
      const deduction = phasedDeduction(income, 25_840, 29_039, 130_651);
      return progressiveTax(excess(income, deduction + 1_400), [[0, .035], [20_150, .044],
        [69_260, .053], [443_630, .0765]]);
    },
  },
  WV: graduated(4_000, [[0, .0222], [10_000, .0296], [25_000, .0333],
    [40_000, .0444], [60_000, .0482]]),
};

function phasedDeduction(income: number, deduction: number, start: number, width: number): number {
  return deduction * (1 - Math.min(1, excess(income, start) / width));
}

function marylandTaxable(gain: number): number {
  const exemptionPerPerson = gain > 200_000 ? 0 : gain > 175_000 ? 800 : gain > 150_000 ? 1_600 : 3_200;
  return excess(gain, 6_800 + 2 * exemptionPerPerson);
}

function ohioTaxable(gain: number): number {
  const perPerson = gain > 500_000 ? 0 : gain > 80_000 ? 1_850 : gain > 40_000 ? 2_150 : 2_400;
  return excess(gain, 2 * perPerson);
}

function oregonTaxable(gain: number): number {
  const maximum = gain >= 290_000 ? 0 : gain >= 280_000 ? 1_750 : gain >= 270_000 ? 3_500
    : gain >= 260_000 ? 5_250 : gain >= 250_000 ? 7_000 : 8_750;
  return excess(gain, 5_800 + Math.min(federalTax(gain), maximum));
}

const newYorkBands: TaxBand[] = [[0, .039], [17_150, .044], [23_600, .0515],
  [27_900, .054], [161_550, .059], [323_200, .0685], [2_155_350, .0965],
  [5_000_000, .103], [25_000_000, .109]];

function newYorkTax(gain: number): number {
  const taxable = excess(gain, 16_050);
  const regular = progressiveTax(taxable, newYorkBands);
  if (gain <= 107_650) return regular;
  if (gain > 25_000_000) return .109 * taxable;
  const recapture = (threshold: number) => Math.min(1, excess(gain, threshold) / 50_000);
  if (taxable <= 161_550) return regular + (.054 * taxable - regular) * recapture(107_650);
  if (taxable <= 323_200) return regular + 333 + 807 * recapture(161_550);
  if (taxable <= 2_155_350) return regular + 1_140 + 3_071 * recapture(323_200);
  if (taxable <= 5_000_000) return regular + 4_211 + 60_350 * recapture(2_155_350);
  return regular + 64_561 + 32_500 * recapture(5_000_000);
}

function newYorkCityTax(gain: number): number {
  const taxable = excess(gain, 16_050);
  const tax = progressiveTax(taxable, [[0, .03078], [21_600, .03762], [45_000, .03819], [90_000, .03876]]);
  // IT-201 NYC school tax credit, fixed amount and rate reduction.
  const reduction = taxable > 500_000 ? 0
    : taxable > 21_600 ? 37 + .00228 * (taxable - 21_600) : .00171 * taxable;
  const credit = reduction + (gain <= 250_000 ? 125 : 0);
  return excess(tax, credit);
}

type LocalTax = (gain: number) => number;

function register(place: string, state: string, local?: LocalTax, localSource?: string, label?: string): void {
  const rule = states[state] ?? flat(0);
  registerTaxRules(place, {
    currency: 'USD',
    hasSpecialRegime: false,
    taxOwed: ({ withdrawalLocal }) => {
      const gain = Math.max(0, withdrawalLocal);
      return {
        taxLocal: federalTax(gain) + rule.calculate(gain) + (local?.(gain) ?? 0),
        regimeName: 'Standard',
        explanation: '2026. Joint return. The withdrawal is entirely long-term ETF gain. '
          + (rule.explanation ?? 'Includes federal tax and applicable state tax.')
          + (label ? ' ' + label : ''),
        sourceIds: [...new Set([...federalSources,
          ...(state ? rule.sources ?? ['tax-us-states', 'tax-us-state-gains'] : []),
          ...(localSource ? [localSource] : [])])],
      };
    },
  });
}

register('US', '');
for (const state of Object.keys(states)) register('US-' + state, state);

for (const borough of ['36005', '36047', '36061', '36081', '36085']) {
  register('US-' + borough, 'NY', newYorkCityTax, 'tax-us-ny', 'Includes New York City resident income tax.');
}
// Yonkers is a city inside Westchester County. Its rate cannot be assigned to the whole county.
register('CITY-5145215', 'NY', gain => .1675 * newYorkTax(gain), 'tax-us-ny', 'Includes the Yonkers resident surcharge.');

// October 2026 DOR notice, county numbers 01–92. Census county codes
// use the same order expressed as successive odd numbers from 001 to 183.
const indianaCountyRates = [
  0.016, 0.0159, 0.0175, 0.0179, 0.025, 0.0171, 0.025234, 0.024733,
  0.0295, 0.02, 0.0235, 0.0265, 0.0165, 0.015, 0.014, 0.0245,
  0.0213, 0.015, 0.012, 0.02, 0.0282, 0.0189, 0.021, 0.017,
  0.0288, 0.013, 0.0275, 0.0235, 0.011, 0.0194, 0.01, 0.017,
  0.0202, 0.0235, 0.0195, 0.021, 0.02864, 0.025, 0.0103, 0.025,
  0.014, 0.017, 0.01, 0.0165, 0.015, 0.0145, 0.0175, 0.0225,
  0.0202, 0.0125, 0.025, 0.0254, 0.0214, 0.0265, 0.0272, 0.01,
  0.0175, 0.02, 0.0175, 0.025, 0.0265, 0.014, 0.012, 0.005,
  0.0145, 0.0285, 0.023, 0.03, 0.0238, 0.0215, 0.0175, 0.0216,
  0.017, 0.008, 0.0171, 0.0199, 0.017, 0.0145, 0.0128, 0.026,
  0.0275, 0.0125, 0.015, 0.02, 0.029, 0.0212, 0.01, 0.02,
  0.0125, 0.021, 0.0232, 0.016829,
];
for (const [index, rate] of indianaCountyRates.entries()) {
  const fips = String(2 * index + 1).padStart(3, '0');
  register('US-18' + fips, 'IN', gain => rate * excess(gain, 2_000),
    'tax-us-in', 'Includes resident county income tax.');
}

const marylandCountyRates: Record<string, number | TaxBand[]> = {
  '001': .032, '003': [[0, .027], [75_000, .0294], [480_000, .032]],
  '005': .032, '009': .032, '011': .032, '013': .0303, '015': .0274,
  '017': .0303, '019': .033, '021': [[0, .0225], [25_000, .0275], [100_000, .0296], [250_000, .032]],
  '023': .0265, '025': .0306, '027': .032, '029': .033, '031': .032, '033': .032,
  '035': .032, '037': .032, '039': .032, '041': .024, '043': .0295, '045': .032,
  '047': .0225, '510': .032,
};
for (const [county, rate] of Object.entries(marylandCountyRates)) {
  register('US-24' + county, 'MD', gain => {
    const taxable = marylandTaxable(gain);
    return typeof rate === 'number' ? taxable * rate : progressiveTax(taxable, rate);
  }, 'tax-us-md', 'Includes county income tax.');
}

const metroTax: LocalTax = gain => .01 * excess(oregonTaxable(gain), 205_000);
const multnomahTax: LocalTax = gain => .015 * (
  excess(oregonTaxable(gain), 200_000) + excess(oregonTaxable(gain), 400_000)
);
register('US-41051', 'OR', multnomahTax, 'tax-us-portland',
  'Includes the Multnomah County tax. Metro and Portland city taxes depend on the address.');
register('CITY-5746545', 'OR', gain => metroTax(gain) + multnomahTax(gain) + (gain > 21_640 ? 70 : 0),
  'tax-us-portland', 'Models a Portland address inside Multnomah County, including Metro and Arts taxes.');

// Michigan city rates and individual exemptions. The state household exemption is separate.
const michiganCities: [geonames: number, name: string, rate: number, exemption: number][] = [
  [4983905, 'Albion', .01, 600], [4985153, 'Battle Creek', .01, 750],
  [4985711, 'Benton Harbor', .01, 750], [4986020, 'Big Rapids', .01, 600],
  [4990729, 'Detroit', .024, 600], [4991640, 'East Lansing', .01, 600],
  [4992982, 'Flint', .01, 600], [4994358, 'Grand Rapids', .015, 600],
  [4994578, 'Grayling', .01, 3_000], [4995197, 'Hamtramck', .01, 600],
  [4996017, 'Highland Park', .02, 600], [4996718, 'Hudson', .01, 1_000],
  [4997191, 'Ionia', .01, 700], [4997384, 'Jackson', .01, 600],
  [4998830, 'Lansing', .01, 600], [4998842, 'Lapeer', .01, 600],
  [5003132, 'Muskegon', .01, 600], [5003140, 'Muskegon Heights', .01, 600],
  [5006166, 'Pontiac', .01, 600], [5006233, 'Port Huron', .01, 600],
  [5006314, 'Portland', .01, 1_000], [5007989, 'Saginaw', .015, 750],
  [5010917, 'Springfield', .01, 750], [5013924, 'Walker', .01, 600],
];
for (const [geonames, name, rate, exemption] of michiganCities) {
  register('CITY-' + geonames, 'MI', gain => rate * excess(gain, 2 * exemption),
    name === 'Saginaw' ? 'tax-us-mi-saginaw' : 'tax-us-mi-city', 'Includes ' + name + ' resident income tax.');
}

// These jurisdictions can be selected by a verified tax address. Counties and
// city names do not identify a school district or a Metro tax address.
const ohioTraditionalSchoolRates: Record<string, number> = {
  '0203': .0050, '0204': .0050, '0209': .0100, '0303': .0125, '0601': .0100, '0602': .0100,
  '0603': .0125, '0605': .0075, '0606': .0100, '0905': .0050, '0907': .0100, '0909': .0100,
  '1102': .0150, '1103': .0150, '1105': .0175, '1205': .0100, '1303': .0100, '1305': .0100,
  '1502': .0100, '1503': .0100, '1510': .0050, '1701': .0150, '1703': .0125, '1901': .0175,
  '1902': .0150, '1903': .0075, '1904': .0050, '1905': .0175, '1906': .0150, '1907': .0100,
  '2001': .0100, '2002': .0125, '2003': .0050, '2004': .0150, '2101': .0075, '2102': .0100,
  '2303': .0125, '2304': .0200, '2306': .0175, '2307': .0100, '2501': .0075, '2502': .0075,
  '2509': .0050, '2602': .0150, '2603': .0100, '2604': .0100, '2605': .0100, '2606': .0075,
  '2902': .0125, '2903': .0050, '2904': .0100, '2906': .0050, '2907': .0200, '3122': .0125,
  '3201': .0100, '3202': .0175, '3203': .0175, '3205': .0075, '3206': .0150, '3207': .0100,
  '3208': .0100, '3301': .0150, '3302': .0175, '3303': .0100, '3304': .0175, '3305': .0100,
  '3306': .0050, '3501': .0150, '3502': .0175, '3504': .0175, '3604': .0100, '3901': .0050,
  '3903': .0100, '3904': .0050, '3905': .0125, '3906': .0125, '4201': .0075, '4202': .0175,
  '4501': .0075, '4503': .0100, '4506': .0100, '4507': .0100, '4510': .0075, '4712': .0200,
  '4715': .0100, '4903': .0100, '5010': .0100, '5402': .0100, '5405': .0100, '5406': .0150,
  '5502': .0175, '5503': .0200, '5506': .0175, '5507': .0125, '5708': .0125, '5713': .0175,
  '5902': .0050, '5903': .0075, '5904': .0100, '6301': .0150, '6302': .0100, '6303': .0125,
  '6802': .0175, '6803': .0150, '6804': .0175, '6805': .0150, '6901': .0100, '6902': .0100,
  '6903': .0075, '6904': .0100, '6905': .0075, '6906': .0125, '6907': .0150, '6908': .0075,
  '6909': .0175, '7007': .0100, '7008': .0100, '7106': .0050, '7202': .0125, '7204': .0150,
  '7404': .0150, '7405': .0100, '7406': .0100, '7501': .0150, '7503': .0075, '7504': .0150,
  '7505': .0075, '7507': .0075, '8001': .0100, '8003': .0100, '8101': .0100, '8104': .0100,
  '8301': .0100, '8502': .0075, '8505': .0125, '8601': .0100, '8602': .0100, '8604': .0100,
  '8607': .0150, '8701': .0125, '8703': .0125, '8707': .0100, '8708': .0050, '8801': .0100,
  '8802': .0100, '8803': .0125,
};
for (const [district, rate] of Object.entries(ohioTraditionalSchoolRates)) {
  register('US-OH-SD-' + district, 'OH', gain => rate * ohioTaxable(gain),
    'tax-us-oh-school', 'Includes traditional-base school district income tax.');
}
register('US-OR-METRO', 'OR', metroTax, 'tax-us-portland',
  'Includes Metro Supportive Housing Services tax.');
register('US-OR-METRO-MULTNOMAH', 'OR', gain => metroTax(gain) + multnomahTax(gain),
  'tax-us-portland', 'Includes Metro and Multnomah County income taxes.');

for (const fips of ['19007', '19029', '19151', '19161', '19165', '19189']) {
  register('US-' + fips, 'IA', gain => .01 * states.IA.calculate(gain),
    'tax-us-ia-local', 'Includes county emergency medical services surtax. School district surtax depends on the address.');
}

registerTaxRules('US-PR', {
  currency: 'USD',
  hasSpecialRegime: true,
  taxOwed: ({ withdrawalLocal }, regime) => {
    const gain = Math.max(0, withdrawalLocal);
    if (regime === 'special') {
      return {
        taxLocal: 0,
        regimeName: 'Act 60 resident investor, 2026 application',
        explanation: 'Models a qualifying application through 2026 and a 0% decree through 2035. The optional extension through 2055 and new applications from 2027 carry a 4% rate. Primary home ownership, annual donations and fees also apply.',
        sourceIds: ['tax-us-pr-act60', 'tax-us-pr-irs'],
      };
    }

    const taxable = excess(gain, 7_000);
    const regular = progressiveTax(taxable, [[9_000, .07], [25_000, .14], [41_500, .25], [61_500, .33]]);
    return {
      taxLocal: Math.min(regular * (gain <= 100_000 ? .92 : .95), .15 * taxable),
      regimeName: 'Standard',
      explanation: 'Puerto Rico taxes qualifying long-term gains at up to 15%. The estimate assumes bona fide residence and appreciation arising after the move.',
      sourceIds: ['tax-us-pr-treasury', 'tax-us-pr-irs'],
    };
  },
});
