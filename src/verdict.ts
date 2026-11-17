// "Am I gonna make it?": what the visitor has against what a place needs. WAGMI (we're all going to make it) where it is
// enough, Close where it is at most a quarter short, NGMI (not going to make it) otherwise.
export type Mode = 'need' | 'have';
export type VerdictWord = 'WAGMI' | 'Close' | 'NGMI';
export const closeShare = 1.25;

export function verdictOf(needed: number, have: number): VerdictWord {
  if (needed <= have) return 'WAGMI';
  return needed <= closeShare * have ? 'Close' : 'NGMI';
}

// The map's fill for each verdict, and the colour of words and amounts that carry it. Close is amber: those places are still short.
export const verdictFill: Record<VerdictWord, string> = { WAGMI: '#1B7F4C', Close: '#F2CF7A', NGMI: '#E6BDB7' };
export const verdictInk: Record<VerdictWord, string> = { WAGMI: '#1B7F4C', Close: '#A05A00', NGMI: '#B4263B' };

// What the visitor has: $1,000,000 unless they say otherwise, typed between $50,000 and $20,000,000. The slider runs from
// $100,000 to $10,000,000 in even steps of size, so a million sits in its middle, and snaps to two significant figures.
export const defaultHave = 1e6, smallestHave = 5e4, largestHave = 2e7;
export const clampHave = (amount: number) => Math.min(largestHave, Math.max(smallestHave, amount));
export const twoFigures = (amount: number) => { const magnitude = 10 ** (Math.floor(Math.log10(amount)) - 1); return Math.round(amount / magnitude) * magnitude; };
export const haveAtSliderPosition = (position: number) => twoFigures(1e5 * 100 ** position);
export const sliderPositionOfHave = (amount: number) => Math.min(1, Math.max(0, Math.log(amount / 1e5) / Math.log(100)));
