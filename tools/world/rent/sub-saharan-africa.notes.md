# Rent, two-bedroom flat: Sub-Saharan Africa, Mauritius, Seychelles, Cabo Verde, Comoros, São Tomé

Written by AI on 2026.11.17 by model claude sonnet 5.5 (research helper for the world-data owner). Figures were read on 17 Nov 2026.

## Where things are

- Rows: `sub-saharan-africa.table.csv` (built by `python3 -I sub-saharan-africa.py`; not in `data/tables/`, as asked). Hand-read rows with `url` and exact `quote`: `sub-saharan-africa.curated.csv`. Sources: each script's `SOURCES` plus `sub-saharan-africa.sources.csv`; `python3 -I sub-saharan-africa.py --sources` prints the merged list.
- Scripts: `sub-saharan-africa-property24.py` (South African cities), `-property24-network.py` (Kenya, Zambia, Botswana, Mozambique), `-propertycloud.py` (Mauritius, Zimbabwe), `-expat-com.py` (Abidjan, Cotonou, Antananarivo), `-africanvestor.py` (modelled estimates).
- Pages saved in `cache/`: `property24-za`, `property24-network`, `propertycloud`, `expat-com`, `africanvestor`, `payprop-rental-index`, `wayback-portals`, `ssa-rent-articles`, `za-cross-checks`, `cross-check-aggregators`, `hassconsult`, `tpn-rental`.
- A row whose note starts "THIN" is a weak figure. 19 of the 49 countries have a country row; 30 have none (list at the end).
- Where the best figure is for the main city, the table has the city row and the same figure under the country code, with `measured_for` saying "main city only".

## Cape Town

Row `CITY-3369157`: **R24,000 a month**. Median asking rent of 242 two-bedroom apartment ads of 65 to 95 m² on Property24 (all 76 results pages, 1,514 two-bedroom ads, 715 of them flats). Median of all 715 flats regardless of size: R24,000 as well.

By district (Property24 suburbs I grouped myself; 65 to 95 m² ads, with all-size median in brackets):

| District | Ads | Median |
|---|---|---|
| City Bowl (centre, Gardens, Vredehoek, Tamboerskloof and so on) | 87 | R25,000 (R26,000) |
| Atlantic Seaboard (Sea Point, Green Point, Camps Bay and so on) | 48 | R30,000 (R36,950) |
| Southern Suburbs (Claremont, Rondebosch, Newlands, Observatory and so on) | 72 | R18,750 (R17,800) |
| Everything else (Muizenberg, Wynberg Upper, Pinelands and so on), all sizes | 149 | R15,500 |

Cross-checks (none are in the table):

| Source | Figure | What it is |
|---|---|---|
| Knoq SA Rental Report, 23 Oct 2026 | R21,000 | median asking, two-bedroom, Cape Town, several portals (method not published) |
| Livingcost, updated 21 Jun 2026 | $942 for a 40 m² one-bed centre, $1,671 for an 80 m² three-bed centre | at R16.63 to the dollar: R15.7k and R27.8k, so a two-bed sits near R21.7k (my interpolation) |
| Africanvestor | R18,500 | modelled estimate, not observed |
| capetowndata.com, Feb to Oct 2026, Property24 and partners | City Bowl R19,000 to 28,000; Atlantic R32,000 to 85,000; Southern Suburbs R18,000 to 28,000 | ranges of suburb medians |
| Indlu Software blog, Mar 2026 | City Bowl R14,000; Atlantic R18,000; Southern Suburbs R11,000 | older, unclear method, lowest of all |
| Fortren & Company (via Nairametrics), 2026 | $27,138 a year, about R37.6k a month | high-end two-bed in Camps Bay, Clifton, Bantry Bay, Constantia |
| PayProp, Western Cape, Q2 2026 | R12,561 | rent actually paid, all sizes, whole province |

The asking figures (R21k to R24k) agree within 15 percent. The gap to PayProp's R12,561 is real and has four causes: PayProp averages all dwelling sizes, including bachelor flats, one-beds and houses; it covers the whole province (Cape Flats, Winelands, Garden Route); it is rent paid on existing leases, which lag new lets (Western Cape rents rose 9.7 percent in the year to Q2 2026); and it covers agent-managed stock only. For "going rate for a new let" the Property24 figure is the right one. Property24 asks more than the market pays, and I have no data on the haggle; I would not cut it by a guess.

South Africa elsewhere (65 to 95 m² ads, Property24): Johannesburg R17,000 (217 ads, but 82 of them in Rosebank, so it reads like a Rosebank figure; the median of all 788 flats is R9,952), Pretoria R10,800 (364 ads), Durban R9,500 (84 ads). Knoq has R9,500, R9,150 and R9,475 for the same cities, which match the all-size medians, not the 65 to 95 m² ones. Property24's Johannesburg area excludes Sandton, which is a separate area there.

## South African provinces

PayProp's Rental Index is the only honest provincial source. It gives the average rent paid, all dwelling sizes, from rent-payment transactions in PayProp-managed rentals. It is not a two-bed figure. The full index PDF needs an email form, so I did not use it; the provincial values come from PayProp's own blog posts (Western Cape, Northern Cape) and press coverage of the same index (checked against each other: The Citizen, The South African, Property Professional, Rand Desk, capetown.cool and Seeff reproduce identical Q1 numbers). Periods are mixed and flagged per row: Q2 2026 for Western Cape, Gauteng, KwaZulu-Natal, North West, Free State; Q1 2026 for Northern Cape, Limpopo, Mpumalanga, Eastern Cape (no free Q2 value found). The `ZA` country row is PayProp's national average (R9,715, Q2 2026), written so provinces and country share one measure; it is not a two-bedroom figure.

Not used: TPN. Its free pages give no provincial table; its reports are paid per suburb (a sample PDF exists). Seeff's "TPN Rental Index" provincial numbers are identical to PayProp's, so they are not independent. Stats SA publishes a rent index only (actual rentals for housing, September 2026: up 3.9 percent on a year earlier; flats up 4.6 percent in August), no rent levels. I did not find a SARB rent level.

## What each other figure measures

- **Kenya, Nairobi (KES 110,000):** Property24 Kenya, 313 distinct two-bedroom ads (first 40 of 3,614 results pages; the order is not random, and the site repeats ads, which I removed by ad number). Cross-checks: Expat.com, 11 ads, median KES 100,000; Fortren high-end two-bed $10,700 a year. HassConsult (read in full, Q1 to Q3 2026): its only rent level is the average asking rent for all property types in 18 Nairobi suburbs, KES 210,205 (Sep 2026), which is mostly houses, so it does not measure a two-bed flat; its apartment series are indices only. KNBS: not checked beyond noting its CPI is an index.
- **Zambia, Lusaka (ZMW 20,000), Botswana, Gaborone (BWP 8,000), Mozambique, Maputo (MZN 130,000):** Property24 country sites, 237, 106 and 243 distinct two-bedroom ads. One portal each; asking rents.
- **Mauritius (MUR 50,000):** Propertycloud.mu, 602 prices on 28 pages (featured ads repeat, so fewer distinct ads), quartiles 35,000 to 65,000. Expat.com sample of 7 gives MUR 28,000, lower because it includes inland towns.
- **Zimbabwe (USD 850):** Property.co.zw, 78 prices on 4 pages, quartiles 650 to 1,200, mostly Harare. Property24 Zimbabwe has 3 two-bed ads (850, 1,300, 1,400).
- **Nigeria, Lagos (NGN 1,250,000 a month):** Nigeria Property Centre's report, Dec 2025, median asking rent of 1,137 two-bed flats in Victoria Island, N15m a year, divided by 12. Lagos Realty's 2026 report (via Nairametrics and Legit.ng) also puts Victoria Island at N15m, Ikoyi N17.25m, Lekki Phase 1 N10m, Ikate N8.5m. All of Lagos is N6.89m a year (N574k a month); the table figure is for the district a foreign couple would use. Lekki, Lagos: N9m a year (May 2026). The live Property Centre pages return 403, so the copy is from the Internet Archive. Abuja: Property24 has 3 two-bed ads, too few; Africanvestor models N500,000 a month.
- **Senegal, Dakar (XOF 712,500, THIN):** au-senegal.com gives 6,000 to 13,000 F CFA per m² per month for Fann Résidence and Fann Mermoz; I took the middle times 75 m². Cross-checks: Africanvestor 650,000; Expat-Dakar's page text says current Dakar apartment ads average about 870,000 (average 180 m², three bedrooms).
- **Côte d'Ivoire, Abidjan (XOF 450,000, THIN):** median of 7 two-bedroom Expat.com ads (350,000 to 900,000). Matches the midpoint of a blog's range for a three-room flat in Cocody Riviera Golf (300,000 to 600,000). Fortren's high-end figure is $41,671 a year (about XOF 1.9m a month), so the top of the market is far higher.
- **Benin, Cotonou (XOF 700,000, THIN):** 7 Expat.com ads. **Madagascar, Antananarivo (MGA 1,300,000, THIN):** 7 Expat.com ads in ariary (5 more are in euros, €699 to €2,600).
- **Ghana, Accra (USD 2,192, THIN, high-end):** Fortren high-end two-bed, $26,299 a year. It is the only dated figure for the expatriate districts. Mid-market is far lower (Africanvestor GH₵4,000; Ghana-wide GH₵3,800). Meqasa renders its listings with JavaScript, so I could not sample it.
- **Rwanda, Kigali (USD 1,303, THIN, high-end):** Fortren, $15,633 a year. The source says it is not a market average.
- **Uganda, Kampala (UGX 1,600,000), Tanzania, Dar es Salaam (TZS 1,550,000), Ethiopia, Addis Ababa (ETB 150,000), DR Congo, Kinshasa (CDF 5,000,000), Cameroon, Douala (XAF 320,000):** all Africanvestor estimates, **modelled** (a seller of data packs compares portal asking rents, then adjusts with its own model). Treat as placeholders. Conflicts: Ethiopia Property Centre's Bole report (Feb 2026) says Br 50,000 for a two-bed, but from only 4 ads; Expat.com Addis ads are $1,200 to $3,000 and Br 170,000. Dar es Salaam: Fortren high-end is $15,110 a year, and Masaki and Mikocheni listings I saw run $700 to $2,600, so TZS 1.55m (about $595) is a citywide mid-market figure and understates where a foreign couple lives. Kinshasa is priced in US dollars in practice (Expat.com ads $1,600 and $2,600; Africanvestor says about $2,200).

## Things you may have wrong, or should decide

1. Province rows are paid rent for all sizes. Two-bed asking rents in the cities run well above them (Cape Town about 1.9 times, Johannesburg 1.8, Durban 1.0). Do not use a province row as a two-bed figure without saying so.
2. Rows from asking-rent portals are asking rents, not signed rents.
3. The modelled and high-end rows (Uganda, Tanzania, Ethiopia, DR Congo, Cameroon, Ghana, Rwanda) disagree with each other in kind. You may prefer to drop every row whose note starts "THIN" and show those countries as "no good data".
4. Nigeria quotes rent a year ahead; I divided by 12. Kinshasa, Harare and Accra rents are really quoted in US dollars; the CDF row is in francs as published.
5. Search-tool snippets, not saved pages (so not table-grade): Windhoek asking rents N$10,000 to 35,000 (13 MyProperty ads, central ones N$16,500 to 23,000); Luanda T2 Kz 400,000 to 2,500,000; Mahé one-bed about 13,670 SCR in central Mahé (2025); Kigali, Dar es Salaam and Accra single ads.

## Countries with no row, and why

I tried and could not get an honest figure for these. Many portals (Nigeria Property Centre network, BuyRentKenya, Jiji, Expat-Dakar, MyProperty Namibia, casa.sapo.ao, Tonaton, HouseInRwanda) return 403, 429 or a bot check to plain fetches; I did not work round that. Meqasa (Ghana) and Expat.com index pages load too little to sample.

- Namibia, Angola, Seychelles, Cabo Verde: only individual ads or an old one-bed article (see item 5 above). Nothing saved.
- Togo, Burkina Faso, Malawi, Lesotho, Eswatini, Comoros, São Tomé and Príncipe, Burundi, Eritrea, Djibouti, Somalia, South Sudan, Sudan, Chad, Central African Republic, Congo (Brazzaville), Gabon, Equatorial Guinea: no free portal or report found; Expat.com had no sample (Togo 0 two-bed ads, Burkina Faso 0, Senegal 0).
- Mali, Niger, Guinea, Guinea-Bissau, Sierra Leone, Liberia, Gambia, Mauritania: nothing found.
- Zimbabwe outside Harare, and every country's second city: not covered.
