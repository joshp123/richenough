// Every shape's and city's figure for one choice of settings: what colours the map, labels the cities and names the extremes.
import { placeFigure, type PlaceFigure, type Settings } from './capital.ts';
import type { Places } from './places.ts';

export type WorldFigures = {
  settings: Settings;
  // Each shape's capital in dollars, or NaN where there is no figure, in the map file's shape order.
  shapeCapital: Float64Array;
  cityCapital: Map<string, number>;
  // The cities that need the least and the most; among equals, the biggest.
  least: string | null;
  most: string | null;
  figureOf(code: string): PlaceFigure;
};

export function worldFigures(places: Places, shapeCodes: string[], settings: Settings): WorldFigures {
  const cache = new Map<string, PlaceFigure>();
  const figureOf = (code: string) => {
    let figure = cache.get(code);
    if (!figure) { figure = placeFigure(places, code, settings); cache.set(code, figure); }
    return figure;
  };
  const capitalOf = (code: string) => { const figure = figureOf(code); return figure.kind === 'figure' ? figure.capitalUsDollars : NaN; };
  const shapeCapital = Float64Array.from(shapeCodes, capitalOf);
  const cityCapital = new Map<string, number>();
  let least: string | null = null, most: string | null = null;
  for (const city of places.cities) {
    const capital = capitalOf(city.code);
    if (Number.isNaN(capital)) continue;
    cityCapital.set(city.code, capital);
    // Cities come biggest first, so a later city takes an extreme only by beating it.
    if (least === null || capital < cityCapital.get(least)! - 0.5) least = city.code;
    if (most === null || capital > cityCapital.get(most)! + 0.5) most = city.code;
  }
  return { settings, shapeCapital, cityCapital, least, most, figureOf };
}
