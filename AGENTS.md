---
written_by: AI (Claude Opus 5.5), 2026-11-17, from Josh's steering
---

# AGENTS.md

Josh owns this project. His own words are the authority; they are kept privately in `.agent/josh-words.md` (ignored by Git), with the plan (`.agent/plan.md`) and the design (`.agent/design/README.md`). Read them before changing anything a visitor sees.

## What it is

"Rich enough to FIRE?", at richenough.jjpcodes.com: a world map of what a couple needs invested to live well for life, after tax, at the finest level the data supports. See `README.md` for how it works and how to rebuild it.

## Where things are

- `tools/us`, `tools/europe`, `tools/world`, `tools/tax` and `data/tables/` belong to the data and tax agents; `src/tax/` holds the tax rules.
- `tools/map`, `tools/snapshot`, `src/` (except `src/tax`), `web/` and `hosting/` are the site.
- `.agent/build/` holds the latest photographs of the site from `tools/check-site-in-browser.ts`.

## Rules

- Never draw a place finer than its data: the map builder merges shapes without data of their own into the place above them. Rebuild the map files after the tables change.
- Every number on the page traces to a row in `data/sources.csv`; stand-ins say so beside them.
- Publishers are named on the About page (`/about`, `src/about-page.ts`) and nowhere else. Under each cost, a place's details say only where the figure was measured and what kind of source it is ("Bangkok · rental listings", `src/source-lines.ts`); a new rent or wage source gets its kind there.
- Palestine is one place over Israel and Palestine, with Arabic place names, and its figure is "not known". Russia and Ukraine follow the borders in Russia's constitution.
- Things Josh is still choosing are one line each: the projection (`src/projection.ts`), the title (`src/words.ts`), the withdrawal rates offered (`src/capital.ts`).
- Nothing a visitor sees is cut short or ends in "…": a long name steps down a size, then wraps. In "Am I gonna make it?" amounts are said in words ("$2.1M short"), never with a plus or minus sign. `tools/check-site-in-browser.ts` checks both in every photograph and tries the longest names.
- The map is the product. At phone size (390 × 844) it keeps at least 560 px between the bar and the strip in both modes, and the check fails below that; so on a phone the tax switch is the last row of the currency menu, and the strip shows no second currency and no "needs $X" (the map's labels and a place's details do).
- The map moves at one frame of a 60 Hz screen (about 17 ms) and never takes more than about 50 ms for a frame, on an iPhone or a MacBook (Josh's rule). The check prints the median and the slowest.
- The extremes ("Cheapest" and "Most expensive", or "Most to spare" and "Most short") are on every first screen and share picture, so they come only from cities whose rent was measured for the city itself, or for its US county or NUTS 3 / ITL 3 region (not a province, state or country, nor another city), and that have no stand-in cost (`src/world-figures.ts`).
- Check work as a visitor: `tools/check-site-in-browser.ts` in WebKit at phone, laptop and wide sizes, light and dark, then look at the photographs and the share pictures at Twitter's sizes.
- No deploy, push or posting without Josh's go-ahead. Opus or Fable build the frontend; GPT Sol never builds frontend or UI.
