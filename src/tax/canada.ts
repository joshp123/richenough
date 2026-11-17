import { progressiveTax, registerStandardTax, type TaxBand } from './calculation.ts';

// 2026. The base is half the capital gain for each separately taxed spouse.
const federalBands: TaxBand[] = [[0, 0.14], [58_523, 0.205], [117_045, 0.26], [181_440, 0.29], [258_482, 0.33]];
const provinces: Record<string, { name: string; basicAmount: number; bands: TaxBand[] }> = {
  AB: { name: 'Alberta', basicAmount: 22_769, bands: [[0, 0.08], [61_200, 0.10], [154_259, 0.12], [185_111, 0.13], [246_813, 0.14], [370_220, 0.15]] },
  BC: { name: 'British Columbia', basicAmount: 13_216, bands: [[0, 0.056], [50_363, 0.077], [100_728, 0.105], [115_648, 0.1229], [140_430, 0.147], [190_405, 0.168], [265_545, 0.205]] },
  MB: { name: 'Manitoba', basicAmount: 15_780, bands: [[0, 0.108], [47_564, 0.1275], [101_200, 0.174]] },
  NB: { name: 'New Brunswick', basicAmount: 13_664, bands: [[0, 0.094], [52_333, 0.14], [104_666, 0.16], [193_861, 0.195]] },
  NL: { name: 'Newfoundland and Labrador', basicAmount: 13_094, bands: [[0, 0.087], [44_678, 0.145], [89_354, 0.158], [159_528, 0.178], [223_340, 0.198], [285_319, 0.208], [570_638, 0.213], [1_141_275, 0.218]] },
  NS: { name: 'Nova Scotia', basicAmount: 11_932, bands: [[0, 0.0879], [30_995, 0.1495], [61_991, 0.1667], [97_417, 0.175], [157_124, 0.21]] },
  NT: { name: 'Northwest Territories', basicAmount: 18_198, bands: [[0, 0.059], [53_003, 0.086], [106_009, 0.122], [172_346, 0.1405]] },
  NU: { name: 'Nunavut', basicAmount: 19_659, bands: [[0, 0.04], [55_801, 0.07], [111_602, 0.09], [181_439, 0.115]] },
  ON: { name: 'Ontario', basicAmount: 12_989, bands: [[0, 0.0505], [53_891, 0.0915], [107_785, 0.1116], [150_000, 0.1216], [220_000, 0.1316]] },
  PE: { name: 'Prince Edward Island', basicAmount: 15_000, bands: [[0, 0.095], [33_928, 0.1347], [65_820, 0.166], [106_890, 0.1762], [142_520, 0.19], [200_000, 0.20]] },
  QC: { name: 'Québec', basicAmount: 18_952, bands: [[0, 0.14], [54_345, 0.19], [108_680, 0.24], [132_245, 0.2575]] },
  SK: { name: 'Saskatchewan', basicAmount: 20_381, bands: [[0, 0.105], [54_532, 0.125], [155_805, 0.145]] },
  YT: { name: 'Yukon', basicAmount: 16_452, bands: [[0, 0.064], [58_523, 0.09], [117_045, 0.109], [181_440, 0.128], [500_000, 0.15]] },
};

const ontarioHealthBands: TaxBand[] = [
  [20_000, 0.06], [25_000, 0], [36_000, 0.06], [38_500, 0],
  [48_000, 0.25], [48_600, 0], [72_000, 0.25], [72_600, 0], [200_000, 0.25], [200_600, 0],
];

for (const [code, { name, basicAmount, bands }] of Object.entries(provinces)) {
  const places = [`CA-${code}`];
  if (code === 'ON') places.push('CA', 'CITY-6167865', 'CITY-6094817');
  if (code === 'QC') places.push('CITY-6077243', 'CITY-6325494');
  if (code === 'BC') places.push('CITY-6173331', 'CITY-6174041');
  if (code === 'AB') places.push('CITY-5913490', 'CITY-5946768');

  const sourceIds = ['tax-ca-gains', 'tax-ca-rates', 'tax-ca-credits'];
  if (code === 'QC') sourceIds.push('tax-ca-qc');
  if (code === 'ON') sourceIds.push('tax-ca-on');
  registerStandardTax(
    places, 'CAD',
    `Canada taxes half of each spouse’s mature ETF gains at the federal and ${name} rates. This allows for the basic personal tax credits${code === 'ON' ? ', Ontario surtax and Ontario Health Premium. The country fallback uses Ontario' : ''}. Each spouse’s units generally receive a new market-value cost basis at immigration.`,
    sourceIds,
    ({ withdrawalLocal }) => {
      const income = withdrawalLocal / 4;
      const federalBasic = 16_452 - 1_623 * Math.min(1, Math.max(0, (income - 181_440) / 77_042));
      const federal = Math.max(0, progressiveTax(income, federalBands) - 0.14 * federalBasic);
      let provincialBasic = code === 'YT' ? federalBasic : basicAmount;
      if (code === 'MB') provincialBasic *= Math.min(1, Math.max(0, (400_000 - income) / 200_000));
      let provincial = Math.max(0, progressiveTax(income, bands) - bands[0][1] * provincialBasic);
      if (code === 'ON') {
        provincial += 0.20 * Math.max(0, provincial - 5_818) + 0.36 * Math.max(0, provincial - 7_446);
        provincial = Math.max(0, provincial - Math.max(0, 600 - provincial));
        provincial += progressiveTax(income, ontarioHealthBands);
      }
      return 2 * (federal * (code === 'QC' ? 0.835 : 1) + provincial);
    },
  );
}
