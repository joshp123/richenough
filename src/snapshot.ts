// What tools/snapshot/build-snapshot.ts writes to data/snapshot.json, and the page and Worker read.

export const components = ['rent', 'everyday', 'car', 'housekeeper', 'health'] as const;
export type Component = typeof components[number];

// One figure from a table: an amount in its currency, for the place it was measured for.
export type Figure = {
  amount: number; currency: string; unit: string; period: string;
  // A place code ("CITY-2267057", "US-AL") or words ("Montgomery, AL").
  measuredFor: string;
  sourceId: string; note: string; isStandIn?: boolean;
};

export type Source = { publisher: string; title: string; url: string; licence: string; period: string };

export type Snapshot = {
  builtOn: string;
  lifestyle: { everydayUsDollarsPerMonth: number; housekeeperHoursPerWeek: number; tripsUsDollarsPerYear: number; sourceIds: { everyday: string; trips: string } };
  // By component, then by place code.
  figures: Record<Component, Record<string, Figure>>;
  // By component, then by country: what stands in until a table has a figure.
  standIns: Record<Component, Record<string, Figure>>;
  // A flat share of the withdrawal, by country, until the tax rules cover it.
  taxStandIns: Record<string, { rate: number; measuredFor: string; sourceId: string }>;
  exchangeRates: Record<string, { perUsDollar: number; period: string; sourceId: string; isStandIn: boolean }>;
  currencyOfCountry: Record<string, string>;
  sources: Record<string, Source>;
  cityNames: Record<string, string>;
};
