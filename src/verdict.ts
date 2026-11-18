// "Am I gonna make it?": what the visitor has against what a place needs. WAGMI (we're all going to make it) where it is
// enough, NGMI (not going to make it) where it is not.
export type Mode = 'need' | 'have';
export type VerdictWord = 'WAGMI' | 'NGMI';

export const verdictOf = (needed: number, have: number): VerdictWord => (needed <= have ? 'WAGMI' : 'NGMI');

// The map's fill for each verdict: a green and a deep red that read as a verdict at a glance, the red darker than the green so the
// two differ in lightness too, for eyes that do not tell red from green. Then the colour of words and amounts that carry it.
export const verdictFill: Record<VerdictWord, string> = { WAGMI: '#2E9E62', NGMI: '#A3192F' };
export const verdictInk: Record<VerdictWord, string> = { WAGMI: '#1B7F4C', NGMI: '#B4263B' };
// The same words on dark cards and labels, light enough to read at 4.5:1 or better.
export const verdictInkOnDark: Record<VerdictWord, string> = { WAGMI: '#5FD394', NGMI: '#FF8F8F' };

// What the visitor has: $1,000,000 unless they say otherwise, typed between $50,000 and $20,000,000. The slider runs from
// $100,000 to $10,000,000 in even steps of size, so a million sits in its middle, and snaps to two significant figures.
export const defaultHave = 1e6, smallestHave = 5e4, largestHave = 2e7;
export const clampHave = (amount: number) => Math.min(largestHave, Math.max(smallestHave, amount));
export const twoFigures = (amount: number) => { const magnitude = 10 ** (Math.floor(Math.log10(amount)) - 1); return Math.round(amount / magnitude) * magnitude; };
export const haveAtSliderPosition = (position: number) => twoFigures(1e5 * 100 ** position);
export const sliderPositionOfHave = (amount: number) => Math.min(1, Math.max(0, Math.log(amount / 1e5) / Math.log(100)));

// What a verdict says in words, with the difference already formatted: "$2.1M short", "$0.3M to spare".
export const verdictSide = (word: VerdictWord) => (word === 'WAGMI' ? 'to spare' : 'short');
