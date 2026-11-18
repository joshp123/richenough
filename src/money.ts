// How amounts are written: dollars first, and the chosen currency in brackets where it is not the dollar.

const currencySymbols: Record<string, string> = {
  USD: '$', EUR: '€', GBP: '£', CNY: 'CN¥', JPY: '¥', CAD: 'CA$', AUD: 'A$', CHF: 'CHF ', HKD: 'HK$', SGD: 'S$', NZD: 'NZ$', MXN: 'MX$',
  TWD: 'NT$', TRY: '₺', INR: '₹', KRW: '₩', VND: '₫', BRL: 'R$', THB: '฿', PHP: '₱', MYR: 'RM ', IDR: 'Rp ', ILS: '₪', UAH: '₴',
  RUB: '₽', NGN: '₦', PLN: 'zł ', CZK: 'Kč ', HUF: 'Ft ', SEK: 'kr ', NOK: 'kr ', DKK: 'kr ', ZAR: 'R ',
  AED: 'AED ', SAR: 'SAR ', GEL: '₾', KZT: '₸', AZN: '₼', PEN: 'S/ ', COP: 'COL$', CLP: 'CLP$', ARS: 'AR$', UYU: '$U ',
};
export const currencySymbol = (currency: string) => currencySymbols[currency] ?? `${currency} `;

// The currencies offered after the dollar and the visitor's own, most widely held first.
export const widelyHeldCurrencies = ['EUR', 'GBP', 'CNY', 'JPY', 'CAD', 'AUD', 'CHF', 'HKD', 'SGD'];
const currencyNames = new Intl.DisplayNames(['en-GB'], { type: 'currency' });
export const currencyName = (currency: string) => currencyNames.of(currency) ?? currency;

const withThousandsSeparators = (digits: string) => digits.replace(/\B(?=(\d{3})+(?!\d))/g, ',');

// A capital, to a tenth of a million: $1.9M, €0.6M; in currencies where that is thousands of millions, ₫48.2bn.
export function formatCapital(amount: number, currency: string): string {
  const symbol = currencySymbol(currency);
  if (amount >= 1e9) return `${symbol}${withThousandsSeparators((amount / 1e9).toFixed(1))}bn`;
  return `${symbol}${(amount / 1e6).toFixed(1)}M`;
}

// A yearly or monthly sum, whole: $95,000; $2,300.
export function formatWhole(amount: number, currency: string): string {
  return `${amount < 0 ? '−' : ''}${currencySymbol(currency)}${withThousandsSeparators(String(Math.round(Math.abs(amount))))}`;
}

// A sum rounded to two significant figures, for the details' costs: $2,300, $450, $95,000.
export function formatRounded(amount: number, currency: string): string {
  const magnitude = 10 ** Math.max(0, Math.floor(Math.log10(Math.max(1, Math.abs(amount)))) - 1);
  return formatWhole(Math.round(amount / magnitude) * magnitude, currency);
}

// A sum in few characters, for the key: $750K, $1.25M, ₫24.5bn.
export function formatShort(amount: number, currency: string): string {
  const symbol = currencySymbol(currency);
  if (amount >= 1e9) return `${symbol}${Number((amount / 1e9).toFixed(1))}bn`;
  if (amount >= 1e6) return `${symbol}${Number((amount / 1e6).toFixed(2))}M`;
  return `${symbol}${Math.round(amount / 1e3)}K`;
}

// A difference with its sign, to a tenth of a million: +$0.3M, −$0.9M (with a true minus sign).
export function formatSignedCapital(amount: number, currency: string): string {
  return `${amount < 0 ? '−' : '+'}${formatCapital(Math.abs(amount), currency)}`;
}

// A difference in words-sized money: to a tenth of a million, or in thousands where a tenth of a million would round it away
// ($40K, not $0.0M).
export function formatDifference(amount: number, currency: string): string {
  const size = Math.abs(amount);
  return size >= 95_000 ? formatCapital(size, currency) : formatShort(Math.max(1_000, size), currency);
}
