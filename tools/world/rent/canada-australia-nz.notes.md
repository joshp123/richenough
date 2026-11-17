# Rent of a two-bedroom flat: Canada, Australia, New Zealand, Pacific

Written by AI on 2026.11.17 by model claude sonnet 5.5 (with two sonnet 5.5 sub-agents for the Pacific and for the smaller Australian states).

Rebuild everything: `uv run tools/world/rent/canada-australia-nz-build.py`. It runs each source script (each downloads into `cache/<source_id>/` when missing), adds the hand-typed rows in `canada-australia-nz.curated.csv`, checks them and writes `canada-australia-nz.table.csv` (the table contract, 132 rows) and `canada-australia-nz.sources.all.csv` (15 sources). I checked a rebuild from an empty cache for the Canada, NSW, Queensland and New Zealand scripts. `canada-australia-nz.crosschecks.csv` holds two rows that are not in the table (a second Port Moresby source and a stale 2019 Samoa figure). Detail notes: `canada-australia-nz.au-other.notes.md` (SA, Tasmania, WA, ACT, NT) and `canada-australia-nz.pacific.notes.md` (the listings behind each Pacific median).

Each row's `amount` is monthly in local currency. Weekly sources are converted x 52 / 12, and the weekly figure is in the row's note.

## What each source measures

| Source | Place codes | Measure | New let? | Quality |
|---|---|---|---|---|
| CMHC Rental Market Survey, Oct 2025 | provinces, CMAs, Yellowknife, Canada | Purpose-built rental apartments in buildings of 3+ units. Provinces and cities without a usable central zone: average rent of two-bedroom units that turned over in the past 12 months (new tenants). Cities with a central zone: average asking rent of two-bedroom units that were vacant on survey day, central zone named in `measured_for` | yes | Official survey, quality code a to c on every row used |
| NSW DCJ Rent and Sales Report, Apr-Jun 2026 | NSW, 11 cities | Median weekly rent of every new private bond, Flat/Unit with 2 bedrooms, by council area | yes | Official bond data, 30+ bonds per row |
| Queensland RTA, Jul-Sep 2026 | Queensland, 13 cities | Median rent of new bonds, "Flat 2", state, council area or central postcode | yes | Official bond data, 30+ bonds per row |
| South Australia, Apr-Jun 2026 | SA, Adelaide, Mount Gambier | Median rent of new bonds, 2-bed flats/units (bond counts rounded to 5) | yes | Official bond data |
| Tasmania, Apr-Jun 2026 | Tasmania, Hobart, Launceston | Median of 665 / 143 / 140 new private bonds, 2-bed unit/apartment/flat, computed by us from the monthly bond rows | yes | Official bond data |
| MBIE Tenancy Services bonds, Oct 2025 to Sep 2026 | NZ, 13 regions, 25 cities | Two-bedroom dwellings of all types (houses, apartments, flats), new private bonds. We pool the SA2 medians into regions and councils (bond-weighted median of medians) | yes | Official bond data, pooled by us; 30+ bonds per row |
| REIWA (industry body), Perth | Perth | 2-bed unit median rent, rolling three months to Oct 2026, Greater Perth | probably | Method not published |
| REIV (industry body), Melbourne | Melbourne | 2-bed unit median weekly rent, Greater Melbourne, "current quarter" | unknown | Page not dated, method not published |
| Agency and portal listings | Suva, Port Moresby, Port Vila, Nuku'alofa | Asking rent of expat-grade two-bed flats or houses; medians of 14, 38, 25 and 1 ads | asking | Thin; see below |

## Coverage: every province, state, region and country

Canada. All 10 provinces and the Northwest Territories have a row, plus a country row and 44 cities (all 43 CMHC centres that have a GeoNames city, plus Yellowknife). No row for Yukon: yukon.ca refuses scripted requests (Cloudflare, HTTP 403) and the Yukon Bureau of Statistics Rent Survey (April and October) is only on that site. A search summary gave a Whitehorse two-bed median of $1,675, but I could not open the table, so I did not use it. No row for Nunavut: nobody publishes a two-bedroom rent. CMHC's 2026 Northern Housing Report (copy in `cache/ca-cmhc-northern-2026/`) gives only an all-bedroom median for Iqaluit, $3,025 a month, and $1,364 for Whitehorse, $1,975 for Yellowknife. The Northwest Territories row is Yellowknife only, all tenants (CMHC publishes no turnover or vacant rent there).

Australia. Rows for New South Wales, Queensland, South Australia and Tasmania, plus 12 NSW, 13 Queensland, 2 SA, 2 Tasmania cities, Perth and Melbourne. Missing:
- Victoria (state and LGAs): the official Rental Report is hosted on dffh.vic.gov.au. That site hangs or errors for every connection I could make: this MacBook, the Mac mini, and the web fetch tool. The Melbourne row is a stand-in from an industry body (REIV), low confidence. To get the official figure someone on an Australian connection should download "Quarterly Tables Jun 2026" and "Quarterly: Median Rents by LGA Jun 2026" (links under https://discover.data.vic.gov.au/dataset/rental-report-quarterly-data-tables and .../rental-report-quarterly-quarterly-median-rents-by-lga, CC BY 4.0) into `cache/au-vic-rental-report/`. I did not write a parser for a file I could not open.
- Western Australia: the Bond Administrator publishes no rent data. Perth is an industry-body figure for Greater Perth, not the centre. No `AU-WA` row, because Perth is not the state.
- ACT (Canberra) and Northern Territory (Darwin): no bond or two-bedroom rent data is published. The NT government quotes REINT medians for all units (Greater Darwin $601 a week, Alice Springs $450); they are not two-bed, so I left them out. SQM Research has a free 2-bed asking-rent index for every capital (Canberra $625, Darwin $636 a week), but its terms forbid republishing; it is a cross-check only, unless Josh asks SQM for written permission.
- Australia country row: none. One needs Victoria. The coordinator's builder will fall back to the state rows.

New Zealand. A country row, 13 of 16 regions and 24 cities. No row for Tasman, Marlborough or West Coast: fewer than 30 unsuppressed two-bedroom bonds in the year after the privacy rules (areas with under 5 bonds are suppressed). Their all-bedroom medians for Jul-Sep 2026 (MBIE monthly region file) are Tasman about $600, Marlborough about $580, West Coast about $450 a week; these are not two-bed, so not in the table. Queenstown is missing from GeoNames' city list.

Pacific. Rows for Fiji (Suva), Papua New Guinea (Port Moresby), Vanuatu (Port Vila) and Tonga (Nuku'alofa, one listing). No usable figure for Samoa (only a 2019 snapshot, in crosschecks), Solomon Islands, Kiribati, Micronesia, Marshall Islands, Palau, Nauru, Tuvalu: no agency listings or official rent levels that I could reach. No Pacific country publishes a rent level for new lets. All Pacific numbers are asking rents from one agency or portal, and describe expat-grade stock, not the local market.

## What is thin or may be wrong

- CMHC counts purpose-built rental apartments only. Toronto and Vancouver renters often live in rented condominiums, and CMHC's two-bedroom condo average is $2,891 in Toronto and $2,900 in Vancouver, against $3,128 and $3,480 for central purpose-built vacant units. The condo figure is in each city's note where CMHC publishes it.
- Canadian city rows mix two measures (central-zone vacant rent, or the whole CMA's turnover rent when the central zone is suppressed or poor). `measured_for` says which. Vacant units are 3% of the stock, so zone figures rest on small samples; I only used zones with quality code a, b or c. Of 28 cities using a central zone, the zone sits far above the CMA's turnover rent in Montréal ($2,625 downtown vs $1,644), Vancouver ($3,480 vs $2,696), Edmonton ($2,274 vs $1,600) and Toronto ($3,128 vs $2,547), and below it in Kelowna, Kingston and Sherbrooke. Central zones with a quality code of c (Edmonton, Ottawa, Gatineau, Québec City, Sherbrooke, Moncton, Nanaimo, Charlottetown) are the least stable.
- Province rows are the whole province's urban areas of 10,000+, not a main town.
- MBIE publishes no two-bedroom figure by region or council, so the New Zealand rows are our pooling of SA2 medians (the smallest published areas). The method reproduces MBIE's own published regional medians for all bedrooms to within about 2% (checks in the script's docstring), but a pooled median of medians is an estimate, not a published statistic. The four-quarter window means "new let over the past year". The 2-bed row for NZ includes houses on purpose: apartments are too few outside Auckland, Wellington and Christchurch to give regional figures. The apartment-only figure is in the note where it has 30+ bonds.
- NSW and Queensland cities use council or central-postcode figures. The City of Sydney council area covers the CBD, Pyrmont and Surry Hills; its median ($1,150 a week) is far above Sydney's. Greater Sydney's number is a different, lower one. Central or whole-city choice is in each row's `measured_for`.
- Tasmania has no published median; our script computes it from every bond row, with houses, townhouses and community housing out.
- Perth: REIWA figure for Greater Perth, not the centre. Melbourne: REIV, undated page.
- Pacific rows are low-confidence asking-rent medians, as described in the Pacific notes. Tonga is one listing.

## Things you may have wrong

- Palombo-style "two-bed flat in the centre" does not exist as a published statistic in most of this region. For Canada, Australia (NSW, Queensland, South Australia, Tasmania) and New Zealand the figures are real new-bond or turnover data; for the Pacific they are not.
- CMHC publishes turnover and vacant-unit rents, which are closer to a new let than the headline average. I used those, not the all-tenant average. The all-tenant average is in each note.
- GeoNames' `cities15000` file lacks several Australian and New Zealand towns (Wagga Wagga, Albury, Gosford, Nowra, Tweed Heads, Queenstown). They are not in the table. Central Coast (NSW) stands in for Gosford.
