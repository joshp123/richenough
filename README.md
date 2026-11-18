# Rich enough to FIRE?

A world map of the capital a couple needs to live well for life off a global equity ETF portfolio, after each place's tax, at the finest level the data supports: US counties, Europe's NUTS 3 and the UK's ITL 3 regions, first-level regions elsewhere where the data is regional, whole countries otherwise, and the big cities as dots. Address: richenough.jjpcodes.com.

It has two modes. "How much you need" colours each place by what it needs, in eight fixed steps in dollars, the same for every visitor. "Am I gonna make it?" takes what the visitor has and colours each place WAGMI (enough), Close (up to a quarter short) or NGMI.

## How a place's figure is worked out

Spending S a year = 12 × (rent of a two-bed flat in the region's main town + everyday spending + one car + a housekeeper 8 hours a week + private health cover) + trips. Everyday spending is $3,500 a month at US prices times the place's price level; the lifestyle is `data/tables/lifestyle.csv`. The couple sells 5% of their capital C each year. C is the smallest capital at which that withdrawal, less the place's tax on it (`src/tax/`), pays for S; `src/capital.ts` solves for it. Each component comes from the place itself, else the nearest place above it (county, state, country), else a stand-in from Alessandro Palombo's post, marked "stand-in" on the page.

## Data

- `data/tables/*.csv`: one table per component and area, written by the data tools in `tools/us`, `tools/europe`, `tools/world`; columns and place codes are in `.agent/plan.md` (private).
- `data/sources.csv`: every source behind a figure.
- `src/tax/`: each place's tax rules, registered by place code.
- `assets/map/`: the shapes, places and cities, written by `tools/map/`. Shapes are drawn only as finely as the data: a county or region appears where a table or a tax rule gives a figure measured for it (a country's figure copied under each region counts for the country), and otherwise merges into the place above it. Countries outside the US and Europe are split into first-level regions when a table's `place_code` column names one (today Canada, Australia, New Zealand, Japan, Korea, China, Taiwan, Kazakhstan, Brazil and Russia). Rebuild the map files when the tables change.
- Cities: GeoNames places of 100,000 people, capitals and Palombo's cities. A city within 25 km of a bigger one is part of it (Brooklyn of New York). Each has a fame (Palombo's cities, then capitals of half a million and cities of 2.5 million, then cities of a million) that decides the zoom at which its label may show.
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

`web/` is the page. The map is drawn by the graphics card (`web/map-view.ts`): fills from precomputed triangles coloured through a texture, borders as instanced line segments, city labels on a canvas above, placed once per half step of zoom so panning never moves them. It has the shapes at two levels of detail (`shapes-coarse.bin` below zoom 4, `shapes-fine.bin` from zoom 4) and sorts their triangles and lines into a 32 × 32 grid, so each frame draws only what is on screen. A pointer arriving on the idle map, or a finger landing, draws it once, because Safari lets an idle page's canvases go cold and the first frame after that was slow. The projection is one line in `src/projection.ts` (Gall stereographic, turned 11° east; Miller and Patterson are there too); changing it means rebuilding the map files. The title and the address on the pictures are in `src/words.ts`.

`hosting/worker.ts` is the ChatGPT Sites Worker: it serves the page and its files, answers `/api/whereami` with the visitor's country, and draws `/picture.png` (7:8, for posts, in the visitor's mode) and `/preview.png` (2:1 link preview, always the first mode) as SVG (`src/share-pictures.ts`) rendered with resvg. A link carries the state: `/?mode=have&me=lisbon&vs=los-angeles&have=2500000&in=EUR&also=EUR&tax=break`.

`/about` (`src/about-page.ts`, written by the Worker once) explains the method in plain words and lists every source in `data/sources.csv`, and the map's, places', flags' and font's sources, with what each covers, its licence and a link. It is the only page that names publishers: under each cost, a place's details say only where the figure was measured and what kind of source it is ("Lisbon · official statistics", `src/source-lines.ts`). The key links to it, and so does "All sources" in a place's details.

```sh
node hosting/build.mjs                       # writes dist/
node hosting/preview.mjs 8791 NL             # the built Worker in the Sites runtime, on every interface, as a visitor from NL
node tools/check-site-in-browser.ts http://127.0.0.1:8791 .agent/build   # uses the site in WebKit and photographs it
npx tsc -p .                                 # type-checks the page, Worker and shared code
```

## Licences

The code is under the MIT licence (`LICENSE`). The data keeps each source's own licence; the About page lists them all, as does `data/sources.csv`. Map data: Natural Earth (public domain); US Census cartographic boundaries (public domain); Eurostat GISCO NUTS 2024 (© EuroGeographics, free reuse with attribution); ONS ITL 3 2025 (Open Government Licence). Cities: GeoNames (CC BY 4.0); place names in Palestine follow `tools/map/palestine-places.mjs`. Flags: flag-icons (MIT) and Wikimedia Commons (`assets/flags/LICENCES.md`). Font: Archivo (SIL Open Font Licence).
