// How a place's tax is said in its details. A tax on what the couple sell is a share of what they sell; a tax on the money they
// hold (the Netherlands' box 3, Denmark's yearly tax on unsold gains, a wealth tax) is a share of their money each year, whatever
// they sell; a newcomer regime's flat charge is a fixed sum. A part under a twentieth of the tax is left unsaid.
import type { TaxPart } from './capital.ts';

const percent = (share: number) => `${Number((share * 100).toPrecision(2))}%`;
const and = (words: string[]) => (words.length < 2 ? words.join('') : `${words.slice(0, -1).join(', ')} and ${words.at(-1)}`);

export function taxWords(tax: TaxPart, capitalUsDollars: number, withdrawalUsDollars: number, countryWords: string, isUs: boolean,
  money: (usDollars: number) => string): { row: string; sentence: string } {
  const total = tax.usDollarsPerYear;
  if (total < 1) return { row: 'Tax, none', sentence: `${countryWords} takes none of it in tax.` };
  const counts = (part: number) => part >= 0.05 * total;
  const onHoldings = counts(tax.onHoldingsUsDollarsPerYear), onSales = counts(tax.onSalesUsDollarsPerYear), fixed = counts(tax.fixedUsDollarsPerYear);
  const shares = [
    onHoldings ? `${percent(tax.onHoldingsUsDollarsPerYear / capitalUsDollars)} of your money each year` : '',
    onSales ? `${percent(tax.onSalesUsDollarsPerYear / withdrawalUsDollars)} of what you sell` : '',
    fixed ? 'a fixed sum each year' : '',
  ].filter(Boolean);
  const row = `Tax, ${and(shares)}`;
  if (shares.length > 1) {
    // The parts alone, since rounded parts and a rounded total need not add up: "Each year Norway takes $31,000 in tax on the
    // money you hold and $77,000 on what you sell."
    const parts = ([[onHoldings, tax.onHoldingsUsDollarsPerYear, 'on the money you hold'], [onSales, tax.onSalesUsDollarsPerYear, 'on what you sell'],
      [fixed, tax.fixedUsDollarsPerYear, 'as a fixed sum']] as const).filter(([counted]) => counted)
      .map(([, amount, words], index) => `${money(amount)}${index ? '' : ' in tax'} ${words}`);
    return { row, sentence: `Each year ${countryWords.replace(/^The /, 'the ')} takes ${and(parts)}.` };
  }
  if (onHoldings) return { row, sentence: `${countryWords} taxes the money you hold, whatever you sell: ${money(total)} a year.` };
  if (fixed) return { row, sentence: `${countryWords} takes a fixed ${money(total)} a year in tax.` };
  return { row, sentence: isUs ? `Federal and state tax take ${money(total)} of it.` : `${countryWords} takes ${money(total)} of it in tax.` };
}
