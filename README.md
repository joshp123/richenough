# Rich enough to FIRE?

A world map of the capital a couple needs to live well for life off a global equity ETF portfolio, after each place's tax, at the finest level the data supports: US counties, Europe's NUTS 3 and the UK's ITL 3 regions, first-level regions elsewhere where the data is regional, whole countries otherwise, and the big cities as dots. Working address: richenough.jjpcodes.com (not deployed).

It has two modes. "How much you need" colours each place by what it needs, in eight fixed steps in dollars, the same for every visitor. "Am I gonna make it?" takes what the visitor has and colours each place WAGMI (enough), Close (up to a quarter short) or NGMI.

## How a place's figure is worked out

Spending S a year = 12 × (rent of a two-bed flat + everyday spending + one car + a housekeeper 8 hours a week + private health cover) + trips. Everyday spending is $3,500 a month at US prices times the place's price level; the lifestyle is `data/tables/lifestyle.csv`. The couple sells 5% of their capital C each year. C is the smallest capital at which that withdrawal, less the place's tax on it (`src/tax/`), pays for S; `src/capital.ts` solves for it. Each component comes from the place itself, else the nearest place above it (county, state, country), else a stand-in from Alessandro Palombo's post, marked "stand-in" on the page.

## Data

- `data/tables/*.csv`: one table per component and area, written by the data tools in `tools/us`, `tools/europe`, `tools/world`; columns and place codes are in `.agent/plan.md` (private).
- `data/sources.csv`: every source behind a figure.
- `src/tax/`: each place's tax rules, registered by place code.
- `assets/map/`: the shapes, places and cities, written by `tools/map/`. Shapes are drawn only as finely as the data: a county or region appears where a table or a tax rule names it, and otherwise merges into the place above it, so the map files are rebuilt when the tables change.
- `data/snapshot.json`: the tables, sources, stand-ins and exchange rates in the form the page loads.

Rebuild everything the page loads, in this order (Node 24; `devenv shell` provides it):

```sh
node tools/map/build-map-geometry.ts   # shapes-coarse.bin, shapes-fine.bin, places.json (downloads go to cache/map)
node tools/map/build-cities.ts         # cities.json
node tools/snapshot/build-snapshot.ts  # data/snapshot.json
node tools/snapshot/print-figures.ts Lisbon US-06037   # a place's figure, every cost and the tax, for checking
```

`node tools/build-fonts.ts` rebuilds the Archivo fonts in `assets/fonts`. The flags in `assets/flags` are Apple Prices' (`assets/flags/LICENCES.md`).

## Site

`web/` is the page. The map is drawn by the graphics card (`web/map-view.ts`): fills from precomputed triangles coloured through a texture, borders as instanced line segments, city labels on a canvas above, placed once per half step of zoom so panning never moves them. The projection is one line in `src/projection.ts` (Gall stereographic, turned 11° east; Miller and Patterson are there too); changing it means rebuilding the map files. The title and the address on the pictures are in `src/words.ts`.

`hosting/worker.ts` is the ChatGPT Sites Worker: it serves the page and its files, answers `/api/whereami` with the visitor's country, and draws `/picture.png` (7:8, for posts, in the visitor's mode) and `/preview.png` (2:1 link preview, always the first mode) as SVG (`src/share-pictures.ts`) rendered with resvg. A link carries the state: `/?mode=have&me=lisbon&vs=los-angeles&have=2500000&in=EUR&also=EUR&tax=break`.

```sh
node hosting/build.mjs                       # writes dist/
node hosting/preview.mjs 8791 NL             # the built Worker in the Sites runtime, on every interface, as a visitor from NL
node tools/check-site-in-browser.ts http://127.0.0.1:8791 .agent/build   # uses the site in WebKit and photographs it
npx tsc -p .                                 # type-checks the page, Worker and shared code
```

## Licences

Map data: Natural Earth (public domain); US Census cartographic boundaries (public domain); Eurostat GISCO NUTS 2024 (© EuroGeographics, free reuse with attribution); ONS ITL 3 2025 (Open Government Licence). Cities: GeoNames (CC BY 4.0); place names in Palestine follow `tools/map/palestine-places.mjs`. Fonts: Archivo (SIL Open Font Licence). Exchange-rate stand-ins: ECB reference rates and US Treasury reporting rates.
