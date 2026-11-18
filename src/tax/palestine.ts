import { registerStandardTax } from './calculation.ts';

// Palestinian Authority Income Tax Decree 8/2011 as amended, checked November 2026.
// The combined map area also contains places outside this tax administration.
for (const code of ['CITY-285066', 'CITY-282615']) {
  registerStandardTax(
    code, 'ILS',
    'For a resident subject to Palestinian Authority income tax, income earned outside Palestine is exempt unless it originates from local funds or deposits. The estimate assumes the ETF and its funding were held abroad before the move.',
    ['tax-ps-income-decree', 'tax-ps-income-consolidated'],
    () => 0,
  );
}
