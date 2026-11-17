# Australia outside NSW, Victoria and Queensland: two-bedroom flat rent

Written by AI on 2026.11.17 by model claude sonnet 5.5 (sub-agent).

Wanted: median weekly rent of a two-bedroom flat/unit at the new-let rate, latest quarter, from bond lodgement data. Monthly figure = weekly x 52 / 12, in AUD.

Short result: South Australia and Tasmania have official bond data and give a true two-bedroom flat figure. Western Australia has only an industry-body figure for Perth. The ACT and the Northern Territory have no free two-bedroom figure that Josh can publish.

Files:
- `canada-australia-nz-au-sa.py` (South Australia, bonds)
- `canada-australia-nz-au-tas.py` (Tasmania, bonds)
- `canada-australia-nz-au-other.curated.csv` and `.sources.csv` (Perth, REIWA)

## South Australia (script, official bond data)

Source: Private Rent Report, South Australian Housing Trust, built from the Consumer and Business Services rental bond data set. Licence CC BY 3.0 Australia. Quarter April to June 2026, published 11 August 2026.

What it measures: median weekly rent of bonds lodged in the quarter, so new tenancies only. Split by dwelling type (flats/units or houses) and bedrooms. Two-bedroom flats/units is the column we use.

| Place | Weekly | Monthly | Bonds | Measures |
|---|---|---|---|---|
| AU-SA | $507.50 | A$2,199 | about 2,200 | whole state |
| Adelaide | $650.00 | A$2,817 | about 265 | City of Adelaide council area (CBD and North Adelaide) |
| Mount Gambier | $330.00 | A$1,430 | about 55 | City of Mount Gambier council area |

Choice to review: the Adelaide row is the central council area, as the CMHC script does for Canadian cities. Greater Adelaide (the four metro regions) is $522.50 a week (A$2,264 a month) from about 1,945 bonds. The two differ by $127 a week. The metro figure is the better answer if the site means "a flat anywhere in Adelaide". It is in the row's note. The central figure is high partly because the City of Adelaide has new and student-style blocks.

Counts are rounded to 5. Cells of 1 to 5 bonds are suppressed. Other councils have too few two-bedroom flat bonds for a figure (Whyalla about 20, Port Augusta 15, Port Lincoln 15 in the March quarter).

Trap: the data.gov.au copy of this dataset stops at the March 2026 quarter. The data.sa.gov.au portal has the June 2026 quarter. The script uses the portal file.

## Tasmania (script, official bond data)

Source: "Rental Bond and Rental Data", Department of Justice Tasmania, on data.gov.au. Licence CC BY 4.0. One Excel file a month. The publisher gives no median, so the script computes it.

The "Active Bonds" sheet lists one row per bond lodged in that month (suburb, postcode, weekly rent, bedrooms, dwelling type, housing type). The "Closed Bonds" sheet lists ended tenancies and is ignored. The script uses April, May and June 2026 (4,038 rows, about 1,345 a month).

Filter: private housing only (community housing dropped), 2 bedrooms, dwelling type Unit, Apartment or Flat. Houses, townhouses, semi-detached and terraces are out. In Tasmania "Unit" is the common word for a flat, and includes small villa units.

| Place | Weekly | Monthly | Bonds | Measures |
|---|---|---|---|---|
| AU-TAS | $480.00 | A$2,080 | 665 | whole state |
| Hobart | $550.00 | A$2,383 | 143 | City of Hobart council area, by postcodes 7000, 7004, 7005, 7007, 7008 |
| Launceston | $460.00 | A$1,993 | 140 | postcodes 7248, 7249, 7250 |

Choice to review: Greater Hobart (Hobart, Glenorchy, Clarence, Kingborough and Brighton councils, by postcode) is $520 a week (A$2,253 a month) from 325 bonds. It is in Hobart's note. Council areas are approximated by postcode, so a few bonds near a boundary may sit on the wrong side.

Thin: Burnie has 13 bonds and Devonport 31 (postcode 7310, including East Devonport), too few to publish. Other towns are smaller still.

The search engine listed this same dataset as if it were New South Wales. It is Tasmanian (every row says State = Tasmania).

## Western Australia (curated, industry body)

The WA Bond Administrator (Consumer Protection) holds the bonds but publishes no rent data. The state open data catalogue has none. A 2017 freedom of information reply says the office does not regularly report on bond data and holds no history. So there is no official figure.

Best free figure: REIWA, the Real Estate Institute of Western Australia. REIWA is an industry body, not a regulator. Its Perth Metro page (Unit panel) shows two-bedroom unit rent $720 a week (A$3,120 a month). One-bedroom is $600, three-bedroom $790, all units $700, and two-bedroom houses $650. The data is a rolling three months to October 2026, updated 8 November 2026. REIWA does not say how the rent median is built or how many leases it uses. Its FAQ counts leasing days from the advert on reiwa.com to the lease contract date, so it is probably new leases. That is an inference, not a published fact.

Measures: Perth Metro region (Greater Perth), not the city centre. A quarterly REIWA release (June 2026 quarter) reportedly gives "two-bedroom other dwellings" by sub-region: Perth Inner $750, Middle $700, Outer $610, whole Perth $700. I only saw this in a search summary, not on the page, because reiwa.com.au blocks plain fetches. Treat it as unconfirmed. The page copy in the cache comes from the Internet Archive snapshot of 8 November 2026.

No AU-WA row: Perth is the only WA figure and is not the state. Mandurah and Bunbury have no free two-bedroom figure that I could reach.

## Australian Capital Territory (none)

The ACT Revenue Office holds the bonds. It publishes no rent statistics. The ACT open data portal (785 datasets listed, checked by title) has no rent or bond dataset. The ACT Treasury cost of living statement for 2026-27 gives no dollar rent. Allhomes (the standard Canberra source) blocks plain fetches. The Domain rent report, which Allhomes republishes, gives Canberra units at $580 a week in the September 2026 quarter, but for units of all sizes, as asking rent. I saw that in a search summary only. Not two-bedroom, so not used.

## Northern Territory (none)

The NT has no public bond or rent data set. The NT Government economy site (Department of Treasury and Finance, copy in cache) gives REINT medians for the June quarter 2026:
- Greater Darwin (Darwin and Palmerston) unit rent $601 a week, house rent $799.
- Alice Springs unit rent $450, house $650.
- Katherine unit rent $450.

The page does not give bedrooms. So these are "all units" and are not two-bedroom. I did not put them in the table. If you want a fallback, $601 a week is A$2,604 a month for all units in Greater Darwin, but it should not be labelled two-bedroom. REINT sells its detailed quarterly report (RELM). REIA publishes two-bedroom "other dwellings" rents by capital (including Darwin and Canberra) in its Real Estate Market Facts report, but sells each data set for A$280 and the full report for A$450. No paid data, so not used.

## Cross-check, not used as a source

SQM Research publishes a weekly asking-rent index with a "2 Beds Units" row for each capital city. Week ending 12 November 2026:

| City | Asking rent, 2-bed units |
|---|---|
| Perth | $697.75 |
| Adelaide | $545.22 |
| Hobart | $541.39 |
| Canberra | $624.51 |
| Darwin | $635.85 |

The bond figures agree with it: Adelaide metro bonds $522.50 against $545 asking, Hobart $520 to $550 against $541, Perth REIWA $720 against $698.

SQM's terms of service (https://sqmresearch.com.au/terms-of-service) allow personal, non-commercial or internal use only and forbid republishing or aggregating content. So the SQM figures cannot go on a public map without written permission from SQM. This is the same position as Numbeo. If Josh wants ACT and NT numbers, SQM is the only free two-bedroom source I found, and it needs a permission request. I did not write to anyone. Pages are cached in `cache/au-sqm-weekly-rents/` for reference only. The index is asking rent (the median of advertised rents, stratified by postcode), not signed leases.

## What each figure is

| Place | Kind | New let? |
|---|---|---|
| South Australia, Adelaide, Mount Gambier | bond lodgements in the quarter | yes, new bonds only |
| Tasmania, Hobart, Launceston | bond lodgements in April-June 2026 | yes, new bonds only |
| Perth | REIWA, method not published | probably new leases |
| ACT, NT | no usable figure | not applicable |

## Cache folders made

`au-sa-private-rent`, `au-tas-bond-data`, `au-wa-reiwa`, `au-reia-remf` (REIA pages showing the paid data sets), `au-nt-economy-housing`, `au-sqm-weekly-rents`. All are inside the ignored `cache/` directory.
