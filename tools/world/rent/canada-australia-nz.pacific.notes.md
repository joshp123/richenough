# Pacific rent: notes

Written by AI on 2026.11.17 by model claude sonnet 5.5 (sub-agent).

Target: monthly rent of a two-bedroom flat (70-85 m2) at a new-let asking rate, for 12 Pacific countries. Result: 5 countries have a usable (if thin) figure, 7 have none. Every figure is an asking rent from one agency or portal. None is an official statistic. No official statistics office in these countries publishes a rent level for new lets that I could reach.

Method limits. The Parallel search tool was rate-limited all session, so I used web search, curl and Python. Raine & Horne Fiji, Harcourts Fiji, Pacific Property Group, Colliers and Expatistan returned 403 or "request blocked" to plain fetches; I did not work round that. I never used Numbeo. Aggregator and expat-guide numbers (Livingcost-style, GlobalCostData, Abrova, Jarnias Cyril, 360nations, Expat Exchange) turn up in every search but are modelled or anecdotal; I did not use them for any row. No Expatistan or Livingcost cross-check was possible (Expatistan blocked).

## Fiji (Suva)

Row: Suva FJD 4,250 per month, median of 14 distinct two-bedroom ads on Opal Real Estate (licensed Suva agent). Range FJD 1,900 to 7,950. Mostly furnished "executive" flats in Toorak, Laucala Bay, Domain, Raiwai, Namadi Heights. Some ads say "$x/Monthly"; the rest show a bare "$" figure, read here as FJD per month (inference, supported by the stated-monthly ads and by the same range). Ads are dated by "x months ago" on the site: 1 month to 2 years old. Of the 13 Suva ads on the apartment pages, 10 are 12 months old or less; their median is also FJD 4,250 (the flat and townhouse pages show no age). This is the expat/executive end of the market. Cheaper local flats exist (Opal lists a Nasese flat at 1,900 and a new two-bed flat at 2,000) but few are advertised on agent sites; Facebook Marketplace shows more but is not allowed. Thin: one agent. Not found: Nadi and Lautoka rents; any Fiji Bureau of Statistics rent level (FBoS publishes a CPI with a rent component and a real-estate output report, not rent levels; a new HIES is under way). Unverified leads seen only in search snippets (pages blocked or gone, not cached, not used): Raine & Horne Capital Hill three-bed FJD 8,500 per month; Bayleys Burerua Rd FJD 2,500 per month per apartment.

Opal Suva two-bed ads used (FJD per month, location): 1,900 Nasese; 2,800 Namadi Heights; 3,500 Samabula North; 3,500 Bayview Heights; 3,500 Toorak (Waimanu Rd); 4,000 Samabula South; 4,000 Toorak (Waimanu Rd); 4,500 The Domain (Allardyce Rd); 5,000 The Domain (Ratu Cakobau Rd); 5,500 Laucala Bay; 5,500 Toorak (Suva St); 6,250 Toorak (Amy St); 6,500 Laucala Bay; 7,950 Raiwai. Pages: https://opalfiji.com/rental-apartment/ (3 pages) and https://opalfiji.com/homes-for-rent/ (5 pages). Ads in Tamavua, Nasinu, Naitasiri and Lami were left out of the Suva median.

## Papua New Guinea (Port Moresby)

Two rows, both weekly asking rents converted x52/12.
1. Hausples (the main PNG property portal, price filter "per week"): median K1,850 per week = PGK 8,017 per month, n=38 two-bedroom ads in Port Moresby aged 12 months or less (K650 to K7,150). For the 32 ads aged 6 months or less the median is K2,500 per week (PGK 10,833 per month); the series is lumpy because new executive compounds in Town, Ela Beach and Konedobu sit at K3,500 to K7,000. Most ads give no floor area (2 of the 38 state one in the 70-85 m2 band), so I did not filter on size. Portal-wide figure (all bedroom counts, apartments): median K2,500 per week, 302 ads.
2. Century 21 Siule (shown on c21responsive.immobel.com): 129 ads, median K1,500, range K500 to K4,500; per-ad pages are https://c21responsive.immobel.com/propertyDetails.action?id=<id> (ids in cache/pacific-rent/pg/c21-rows.json). Only 3 ads state "per week" in words; the rest are bare numbers, read as weekly (inference). Undated ads, so possibly stale.
Both describe expat-grade, secured, often furnished compounds with backup power and water. This is what an employer pays in Port Moresby; local housing is far cheaper and not advertised on portals. Lae: Hausples has only 2 two-bedroom ads (K963 and K1,100 per week), too few to use. Not found: any PNG National Statistics Office rent level.

Hausples two-bedroom ads used (weekly rent, age):
- K650/wk, 2 months ago, Aniani Street, Gerehu, Port Moresby, NCD: https://www.hausples.com.pg/rent/gerehu/aniani-street-32186/
- K700/wk, 1 month, 2 weeks ago, place 1 Litsea, Hohola, Port Moresby, NCD: https://www.hausples.com.pg/rent/hohola/place-1-litsea-27672/
- K800/wk, 11 months ago, Lot 18 Penda Place Section 22,, Hohola, Port Moresby, NCD: https://www.hausples.com.pg/rent/hohola/lot-18-penda-place-section-22-30273/
- K800/wk, 11 months ago, Korobosea, Port Moresby, NCD: https://www.hausples.com.pg/rent/korobosea/lot-13-unit-6-geboso-street-hgk-6sec-87-17873/
- K850/wk, 6 months, 1 week ago, 8 mile, Port Moresby, NCD: https://www.hausples.com.pg/rent/8-mile/2-bed-1-bath-apartment-32005/
- K875/wk, 9 months ago, Kaugere, Port Moresby, NCD: https://www.hausples.com.pg/rent/kaugere/2-bed-1-bath-apartment-31883/
- K900/wk, 2 months, 2 weeks ago, Kennedy Estate Amode Compound, 7 mile, Port Moresby, NCD: https://www.hausples.com.pg/rent/7-mile/kennedy-estate-amode-compound-31418/
- K1200/wk, 1 month, 1 week ago, Pruth Street , Korobosea, Port Moresby, NCD: https://www.hausples.com.pg/rent/korobosea/pruth-street-32232/
- K1300/wk, 2 months, 1 week ago, Korobosea, Port Moresby, NCD: https://www.hausples.com.pg/rent/korobosea/place-geboso-30140/
- K1300/wk, 1 month, 1 week ago, Igua   , Boroko, Port Moresby, NCD: https://www.hausples.com.pg/rent/boroko/igua-32214/
- K1300/wk, 1 month ago, Igua        , Boroko East, Port Moresby, NCD: https://www.hausples.com.pg/rent/boroko-east/igua-31938/
- K1375/wk, 2 weeks, 6 days ago, Korobosea, Port Moresby, NCD: https://www.hausples.com.pg/rent/korobosea/2-bed-1-bath-apartment-32253/
- K1400/wk, 4 months, 3 weeks ago, Laurabada       , Boroko, Port Moresby, NCD: https://www.hausples.com.pg/rent/boroko/laurabada-30799/
- K1400/wk, 4 months, 3 weeks ago, Avenue Lahara, Boroko, Port Moresby, NCD: https://www.hausples.com.pg/rent/boroko/avenue-lahara-29609/
- K1500/wk, 6 months, 3 weeks ago, Boroko East, Port Moresby, NCD: https://www.hausples.com.pg/rent/boroko-east/drive-boroko-12251/
- K1600/wk, 4 months ago, 5 mile, Port Moresby, NCD: https://www.hausples.com.pg/rent/5-mile/2-bed-1-bath-apartment-31455/
- K1700/wk, 1 month, 1 week ago, Sec25 Lot9, Brampton street, , Town, Port Moresby, NCD: https://www.hausples.com.pg/rent/town/sec25-lot9-brampton-street-32228/
- K1700/wk, 1 week, 1 day ago, Koki Street, Koki, Port Moresby, NCD: https://www.hausples.com.pg/rent/koki/koki-street-32121/
- K1700/wk, 1 year ago, Koki, Port Moresby, NCD: https://www.hausples.com.pg/rent/koki/lehunt-road-31133/
- K2000/wk, 5 months, 3 weeks ago, Section18 Lot11, Chesterfield Street Idibana/2 bedder , Town: https://www.hausples.com.pg/rent/town/section18-lot11-chesterfield-street-idibana2-bedder-16798/
- K2200/wk, 1 month, 2 weeks ago, Bligh Street, Granville Sec 9, Lot 7, Town, Port Moresby, NC: https://www.hausples.com.pg/rent/town/bligh-street-granville-sec-9-lot-7-30348/
- K2500/wk, 1 month, 3 weeks ago, Armit street, Paga Hill, Port Moresby, NCD: https://www.hausples.com.pg/rent/paga-hill/armit-street-32155/
- K2500/wk, 2 months, 1 week ago, Kitty Hawk, 6 Mile, Port Moresby, NCD: https://www.hausples.com.pg/rent/6-mile/kitty-hawk-32147/
- K2500/wk, 1 month, 2 weeks ago, Ela Beach, Port Moresby, NCD: https://www.hausples.com.pg/rent/ela-beach/2-bed-2-bath-apartment-29472/
- K2800/wk, 1 month ago, Koki, Port Moresby, NCD: https://www.hausples.com.pg/rent/koki/2-bed-1-bath-apartment-32237/
- K3000/wk, 1 month, 1 week ago, Ela Beach, Port Moresby, NCD: https://www.hausples.com.pg/rent/ela-beach/street-winter-31404/
- K3500/wk, 2 months ago, Chesterfield Street , Town, Port Moresby, NCD: https://www.hausples.com.pg/rent/town/chesterfield-street-32182/
- K3500/wk, 2 months, 2 weeks ago, Konedobu, Port Moresby, NCD: https://www.hausples.com.pg/rent/konedobu/2-bed-2-bath-apartment-32157/
- K3500/wk, 1 week, 1 day ago, Place Bevan, Town, Port Moresby, NCD: https://www.hausples.com.pg/rent/town/place-bevan-32070/
- K3600/wk, 1 week, 1 day ago, Road Ela Beach, Ela Beach, Port Moresby, NCD: https://www.hausples.com.pg/rent/ela-beach/road-ela-beach-16033/
- K3600/wk, 2 months, 3 weeks ago, Ela Beach, Port Moresby, NCD: https://www.hausples.com.pg/rent/ela-beach/2-bed-2-bath-apartment-32101/
- K4250/wk, 2 months, 2 weeks ago, Sec 39 Lot 13 Ela-Makana Street Makana Apt/2 bedder , Town, : https://www.hausples.com.pg/rent/town/sec-39-lot-13-ela-makana-street-makana-apt2-bedder-32041/
- K5000/wk, 2 months, 2 weeks ago, Champions Parade , Konedobu, Port Moresby, NCD: https://www.hausples.com.pg/rent/konedobu/champions-parade-32158/
- K5000/wk, 4 months, 3 weeks ago, Champions Parade , Konedobu, Port Moresby, NCD: https://www.hausples.com.pg/rent/konedobu/champions-parade-32080/
- K5000/wk, 3 months, 2 weeks ago, 37 Chesterfield Street Section 24 Lot, Town, Port Moresby, N: https://www.hausples.com.pg/rent/town/37-chesterfield-street-section-24-lot-16885/
- K5500/wk, 1 week, 1 day ago, Ela Beach, Port Moresby, NCD: https://www.hausples.com.pg/rent/ela-beach/beach-rd-ela-32164/
- K6600/wk, 6 months ago, Town, Port Moresby, NCD: https://www.hausples.com.pg/rent/town/tougaba-hills-tougaba-hills-32017/
- K7150/wk, 1 week, 1 day ago, Street McGregor, Town, Port Moresby, NCD: https://www.hausples.com.pg/rent/town/street-mcgregor-32143/

## Samoa (Apia)

Only a stale figure: WST 1,850 per month, median of two 2-bedroom furnished houses (Matautu 1,700, Moamoa 2,000) on the Samoa Realty rentals page, from the Internet Archive snapshot of 2019-11-14. The live site is offline (the domain no longer serves it). Treat as 2019 data, not a 2026 rent. Samoa Housing Corporation runs 73 government rental houses but publishes no rates. The Samoa HIES 2018 reports only imputed and actual household spending totals (no rent per unit). The agency "Navigator Real Estate" has no site I could find; Facebook group leads are not allowed. Search results with WST 8,000 to 14,000 on Rentberry have no stated period and look scraped; not used.

## Tonga (Nuku'alofa)

One ad: a semi-furnished two-bedroom stand-alone house in Sopu, "under TOP1,800 per month" on Property Tonga (licensed agent). n=1, a ceiling, not a median. Other two-bedroom ads on the page carry no price. No official source found.

## Vanuatu (Port Vila)

VUV 150,000 per month, median of 25 two-bedroom ads from one agency (Alliance Real Estate): 24 on its "Rented" page (what was asked for properties that have since let, so closer to a going new-let rate than stale ads) and 1 current ad (Nambatu 2B, VT 272,000). Range VT 60,000 to 272,000. Ads are undated. A mix of lagoon cottages, townhouses and apartments, partly expat-grade. Prices: 60,000; 70,000; 85,000; 95,000; 100,000; 125,000; 130,000; 135,000; 150,000 (x5); 155,000; 160,000 (x2); 165,000 (x2); 175,000; 185,000; 220,000; 250,000 (x2); 300,000; 272,000 (current). The agency page shows "$" before some numbers; I read all as vatu. Two ads lack "per month"; read as monthly. Not found: First National Vanuatu and LJ Hooker Vanuatu list rentals only through scripts that do not load without a browser (First National shows no listings at all); the Vanuatu National Statistics Office publishes no rent level (2010 and 2019-20 HIES, quarterly CPI only; a 2026-27 HIES is in the field). Search snippets (not verified, not used): LJ Hooker city listing VUV 395,000 per month.

## Solomon Islands (Honiara)

None found. No agency site with rental ads that I could reach; only holiday lets, expat-guide estimates, one Facebook ad and an undated Solomon Times article. Nothing usable and traceable.

## Kiribati (South Tarawa)

None found. Only expat-guide estimates (modelled or anecdotal; one says western-standard housing runs AUD 1,000 to 2,500 per month). No listings, no official rent data.

## Micronesia / FSM (Palikir, Pohnpei)

None found. The FSM 2010 census key indicators give tenure, not rent amounts (I searched the FSM 2010 key indicators and the RMI 2021 table report for "rent"; neither has rent levels). Pohnpei has no agency site; Airbnb monthly pages are holiday pricing. Pohnpei rents quoted in expat guides (USD 800 to 1,500 for two bedrooms) are anecdotal and not traceable.

## Marshall Islands (Majuro)

None found. The 2021 census table report gives tenure by island (public rental, owned, occupied free) but no rent amounts. The weekly Marshall Islands Journal has a "space for rent" notice without prices. The 2019 HIES asks for an expected monthly rent; I could not reach its results.

## Palau (Koror)

No listing figure found. Koror is not in GeoNames cities15000, so any row would go under PW. Official data: the 2020 census counts 1,228 cash-rent households and 668 renting without payment (Statistical Yearbook 2021, Table 3.21); the 2023/24 HIES shows actual rentals paid by tenants of 8,435,548 (urban 7,955,508, rural 480,040; assumed annual USD). Inference only, not a row: 8,435,548 / 1,228 is about USD 6,870 per year or USD 570 per month, mean across all rented homes of every size, two different survey years. The census microdata (monthly rent variable) is behind a Cloudflare check; not fetched.

## Nauru

None found. No agency, no official rent. Aggregator figures exist and were not used.

## Tuvalu (Funafuti)

None found. The 2017 census report should hold tenure but I could not download it (the host refused the connection), and it would not hold new-let rents. Aggregator and one 2026 blog figures (USD 275 to 350 for a one-bedroom) are untraceable; not used.

## Things the coordinator may want to know

- The only "official" angle in this region is census tenure and HIES spending tables. None gives rent per two-bedroom flat.
- Fiji and Port Moresby figures are expat/executive-grade by construction (agency portals). The median local household does not live there. Say so on the map.
- PNG rents are weekly everywhere, which makes them look huge per month. K8,017 is about USD 1,900 at roughly USD 0.24 per kina (not checked against a dated rate).
- Port Vila and Suva are the only two cities where the agency set is large enough (n of 25 and 14) to be called a sample.
- Raw files are in cache/pacific-rent/<iso2>/. The Hausples JSON endpoint is /api/portal/pages/results/?pathname=/rent/apartment/ (public, keyless, 100 per page).
