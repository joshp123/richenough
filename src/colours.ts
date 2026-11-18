// The map's colours. "How much you need": eight fixed steps in dollars that turn at a million, the same for every visitor, so
// two people's screenshots always compare. "Am I gonna make it?": the two verdicts (src/verdict.ts).
import { verdictFill, verdictOf, type Mode } from './verdict.ts';

export const stepColours = ['#1B7F4C', '#86CC6E', '#F6E88E', '#F7C352', '#F0913C', '#E0562F', '#B4263B', '#6B1241'];
// Where each step ends, in dollars; the last runs on without end. Greens are under a million.
export const stepEnds = [0.75e6, 1e6, 1.25e6, 1.5e6, 2e6, 2.5e6, 3e6];
export const noFigureColour = '#CDD2D9';

export function colourOfNeed(usDollars: number): string {
  const step = stepEnds.findIndex(end => usDollars < end);
  return stepColours[step === -1 ? stepColours.length - 1 : step];
}

// A place's colour in either mode, or the no-figure grey.
export function fillOf(mode: Mode, neededUsDollars: number | null, haveUsDollars: number, noFigure = noFigureColour): string {
  if (neededUsDollars === null) return noFigure;
  return mode === 'need' ? colourOfNeed(neededUsDollars) : verdictFill[verdictOf(neededUsDollars, haveUsDollars)];
}
