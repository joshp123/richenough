# Rent of a two-bed flat: Middle East, North Africa, Caucasus, Central Asia, Russia and nearby

Written by AI on 2026.11.17 by model claude sonnet 5.5, for the agent that owns the world cost data on the Enough site.

Run `uv run tools/world/rent/mena-eurasia-build.py > rent-two-bedroom.mena-eurasia.csv` (add `--sources` for the sources list). It joins `mena-eurasia.curated.csv` (hand-read figures, with `url` and `quote`) and the five scripts here: Rosstat (Russia), Israel's CBS, Mubawab (Morocco), Realt.by (Belarus), OpenSooq (six Arab countries). Where two sources cover one place, the table keeps the first in the order curated, CBS, Rosstat, Mubawab, Realt.by, OpenSooq. The build gives 178 rows in the table's columns and a sources list of 34. Amounts are monthly, in local currency. A figure published per year or per m2 is converted and says so in `note`. Raw pages are in `cache/<source_id>/`.

## Short version

- Strong, official or registry data: Russia (84 regions plus the national figure, Rosstat, Sept 2026), Israel (CBS average of 3-room flats: national, six districts, 17 cities, 2026 Q2) and Dubai (registered Ejari contracts, 70 to 110 m2 flats).
- Good portal or broker data: Riyadh (7,243 listings), Tashkent (5,908), Kazakhstan's 19 cities (Krisha.kz medians), Muscat (Savills), Tbilisi (Galt & Taggart, TBC Capital), Abu Dhabi, Andorra.
- Own listing samples, thin: Morocco (Mubawab), Minsk (Realt.by), and six Arab countries (OpenSooq).
- Very thin, read off one article: Doha, Baku, Bishkek, Chisinau, Sarajevo, Kyiv.
- No row, with reasons: see "Not covered".

## The four Palombo cities

| City | Row | Figure | Cross-checks (not in the table) |
|---|---|---|---|
| Dubai | `CITY-292223` | AED 12,500 a month: mean of Engel & Völkers' two-bed averages for Marina, Business Bay, Downtown and JLT (AED 150,000 a year) | Livingcost 80 m2 centre flat USD 3,820 = AED 14,030. Ejari median for all Dubai AED 6,417 (`AE-DU`). Prop971 Q3 median 2-bed AED 78,000 a year = 6,500. dataHabibi median 2-bed AED 103,000 = 8,583 |
| Muscat | `CITY-287286` | OMR 402: mean of Savills Q2 2026 two-bed averages for Qurum (406) and Al Khuwair (398) | Hamptons H1 2026 asking: Qurum, Madinat Qaboos, Muscat Hills about 450, Al Khuwair and Al Ghubra about 250. Livingcost USD 1,094 = OMR 421. OpenSooq Muscat area median OMR 240 (46 cards) |
| Marrakesh | `CITY-2542997` | MAD 10,000: median of 74 two-bed listings of 60 to 100 m2 in Guéliz, Hivernage, Agdal, Majorelle, Semlalia, Victor Hugo on Mubawab (whole-city median 9,000 from 176) | Mubawab 2-bed median 10,000 (1,418 listings, 9 Oct 2026, StartHijrah's count), Avito 7,500 (829), FeenWay 9,000 all apartments (11,454), Kaynly 8,200 all lettings. Livingcost USD 760 = about MAD 7,560 |
| Tbilisi | `CITY-611717` | USD 954: mean of Galt & Taggart's Aug 2026 rent per m2 for Vake 15.4, Mtatsminda 13.5, Saburtalo 11.7, Chugureti 10.3 (USD 12.725), times 75 m2 | TBC Capital citywide USD 10.3 per m2 (Sep 2026) = USD 772 (`GE`). Livingcost 80 m2 centre flat USD 1,132 |

Gaps worth knowing:

- Dubai. The registry median for all of Dubai (AED 6,417) is half the central figure because most Ejari contracts are in Jumeirah Village Circle, International City, Al Furjan and similar. DLD publishes no bedroom count for flats (the rooms field is filled on about 4% of contracts), so the 70 to 110 m2 band stands in for a two-bed. dataHabibi's AED 103,000 uses that sparse rooms field and so skews to premium flats. The Engel & Völkers averages are broker figures from Property Monitor, not a registry median, and I read them from a copy because Engel & Völkers' own page returned 404. DLD's Dubai Pulse bulk file (4.4 GB, `dld_rent_contracts-open`) times out from this network; with it you could take the 70 to 110 m2 median for Marina, Downtown and Business Bay straight, and that is the one thing I would do to improve Dubai. If you want one Dubai number for a "centre" dot, I would use AED 12,500.
- Muscat. Savills tracks expat-grade buildings. Omani-market flats rent for about half (OpenSooq OMR 240 in Muscat, Hamptons OMR 250 in Al Khuwair). Oman publishes no rent index (NCSI's CPI rent sample is 1,509 units, no levels). The country row `OM` also carries OMR 402, which overstates Oman outside Muscat.
- Marrakesh. Mubawab is asking rents, and 144 of the 176 cards are marked furnished (the unfurnished median is also MAD 9,000, n=32). The local portal Avito runs a quarter lower. Treat MAD 8,000 to 10,000 as the range; the table has 10,000 because the brief asks for the central districts.
- Tbilisi. Galt & Taggart's series is for 50 to 60 m2 new apartments, and rent per m2 falls with flat size, so 75 m2 may overstate by a few percent. Georgian rents are quoted in US dollars, so the amount is USD.

## What each source measures

- Russia, `ru-rosstat-avg-prices`. Rosstat's price survey: average price at the end of September 2026 of renting a two-room flat from a private person, over the towns Rosstat surveys in each region, mostly the regional capital. Not an advertised-rent sample. Includes Crimea (`RU-CR`) and Sevastopol (`RU-SEV`), as the plan wants. Rosstat lists no Donetsk, Luhansk, Zaporizhzhia or Kherson regions and no Yamalo-Nenets (`RU-YAN`); price those from `RU` or a neighbour. `RU-NEN` (Nenets) and `RU-KHM` (Khanty-Mansi) are listed separately. The script downloads the workbook from rosstat.gov.ru (certificate check off: Russian root certificate) if it is not in the cache.
- Israel, `il-cbs-rent`. CBS Table 4.9, Price Statistics Monthly 7/2026, quarter 2026 Q2, size group 2.5 to 3 rooms (an Israeli "3-room" flat is a living room and two bedrooms). The CBS rent average comes from its consumer-price survey of rented dwellings and mixes in estimated changes for dwellings not re-priced in the quarter, so it runs below what a new tenant is asked (CBS table note 2). Covers Israel only: `PS` carries the Israeli national figure, with the West Bank and Gaza not covered. District rows use ISO codes `IL-JM`, `IL-Z`, `IL-HA`, `IL-M`, `IL-TA`, `IL-D`; drop them if the map has no such shapes. CBS's server timed out for curl here; the PDF came through the web-fetch tool and is cached.
- Dubai, `dubai-pulse-ejari`. Median annual rent of registered new Ejari contracts, flats of 70 to 110 m2, 12 months to 16 Nov 2026 (84,161 contracts), processed from DLD open data by dubairealestatedata.com (CC BY 4.0). `AE` uses it too; Abu Dhabi is dearer, the northern emirates cheaper.
- Abu Dhabi, `ae-engelvoelkers-adrec`. Broker page quoting ADREC average annual rents for 2-beds on Al Reem, Yas and Saadiyat. Bayut H1 2026 gives Al Reem AED 128,000 against 104,100 here. ADREC froze annual rent increases in June 2026 (existing leases).
- Riyadh, `sa-kite`. Median of current asking listings, not contracts. No Ejar or REGA average rent could be found. The five-year Riyadh rent freeze (September 2025) covers existing contracts, not new lets.
- Kazakhstan, `kz-krisha`. Krisha.kz median asking rents for 19 cities; a "two-room" flat has two living rooms, so it is a two-bed. The page is undated and speaks of rises since 17 July, so I have written 2026-08. Earlier editions (April, June) are in the cache: Astana 270,000 and 280,000, Almaty 300,000. The Bureau of National Statistics publishes average offer rents per m2 (press reports for July 2026: Astana KZT 5,796, Almaty 5,961, Shymkent 4,326, which times 75 m2 gives KZT 435,000 to 447,000, well above the Krisha medians because small flats let for more per m2). I could not open its tables, so Krisha medians stand in. Regional rows are the oblast's main town.
- Uzbekistan, `uz-kvadro`. Median of 5,908 listings from Telegram channels, October 2026; IMRI's May 2026 median was USD 500 for 2-rooms, so rents rose or the samples differ.
- Morocco, `ma-mubawab-listings`. My own sample: the first 15 result pages of Mubawab's flats to let in each city, listings with exactly 2 bedrooms and 60 to 100 m2, monthly asking rent. Marrakesh n=176 (74 central), Casablanca 84, Rabat 70. `MA` carries Casablanca (the biggest city; Rabat is dearer at MAD 11,500).
- Belarus, `by-realt`. Realt.by's Minsk long-term lets: 630 unique listings reachable, 162 two-room of 50 to 100 m2, of which 69 priced in BYN (median 2,000) and 92 in USD (median USD 750). I publish BYN because contracts are in BYN; the dollar-priced ones run dearer. Not checked against Belstat.
- OpenSooq (Kuwait, Bahrain, Iraq, Jordan, Egypt, Libya). Median of cards with 2 bedrooms and a stated 60 to 100 m2 area, country-wide, not priced per day, outliers beyond a quarter or four times the median dropped. Undated classifieds, mostly local-market flats; expatriate flats let for more. Medians (country, capital area): Kuwait KWD 330 (141 cards; Hawalli/Kuwait City 325), Bahrain BHD 200 (63), Iraq IQD 750,000 (83; Baghdad 825,000), Jordan JOD 400 (68; Amman 362), Egypt EGP 9,000 (115; Cairo and Giza 10,000), Libya LYD 1,500 (49; Tripoli 1,450). Cross-checks: Amman Apts says 2-beds in Abdoun typically list at JOD 650 to 900 and Deir Ghbar 550 to 750 (Feb 2026); House Solution says a decent Cairo area costs EGP 30,000 to 50,000 and Maadi or Zamalek 50,000 to 90,000 (Sep 2026). Those are the sought-after areas; the table has the country-wide classifieds median. For a "living well" couple the broker ranges are the nearer fit, so consider scaling.
- Doha, `qa-qatarliving`. The midpoint of a stated range (QAR 5,500 to 10,000), not a measured median. OpenSooq has only 9 usable Qatar cards (median QAR 4,200).
- Kyiv, `ua-lun-dengi`. LUN's median two-room rent, 1 September 2026.
- Baku, Bishkek, Chisinau. Midpoints of ranges quoted by one article each, 2024 to 2025, no method. Replace if you find better.
- Sarajevo. Global Property Guide's 2026 median asking rent for a two-bed (EUR 410). The page blocks automated fetches, so the figure comes from a search excerpt and no copy is saved.
- Andorra, `ad-pisos-ad`. Pisos.ad Q2 2026 average asking rent per m2 (117 flats) times 75 m2. The Government's contract-based study (Nov 2025) reports about EUR 9.9 per m2 because it includes old leases.

## Not covered, with reasons

- Kosovo (`XK`), San Marino (`SM`), Monaco (`MC`), Vatican City (`VA`). Kosovo: no aggregate found, only Flatio holiday stays. San Marino: three single listings (about EUR 725 to 900 for 50 to 65 m2 flats); too few. Monaco: IMSEE publishes sale prices only; the one rent figure found, EUR 8,500 a month for a central two-bed (early 2025), is uncited. Vatican City: no private rental market (residents live in Church or Holy See housing).
- Armenia (`AM`). Only cost-of-living guides ($650 to $1,200 for central 2-beds, GoWira AMD 420,000) and no portal aggregate; list.am blocks automated fetches. Needs a list.am sample.
- Lebanon (`LB`). Rents are quoted in US dollars but OpenSooq and OLX Lebanon show converted pounds at a rate I could not check; single OLX Achrafieh 2-bed listings ask USD 1,200 to 1,800.
- Iran (`IR`). Al Jazeera (19 May 2026): "No official data has been released for Tehran"; the Statistical Centre gives only a 31% year-on-year rent rise; the only level is one tenant's lease (23 million tomans for 60 m2).
- Algeria (`DZ`) and Tunisia (`TN`). OpenSooq yields 1 and 0 usable cards; the other sources are blog ranges (Sands of Wealth DZD 70,000 to 140,000 in family districts, machine-written; Houni.tn 2-pièces El Menzah DT 700 to 1,200, Ennasr 650 to 1,000, La Marsa 1,200 to 2,000; Century 21 La Marsa median unfurnished S+2 about DT 1,775 from 20 ads). Ouedkniss and Tayara load too little data without a browser.
- Syria (`SY`), Yemen (`YE`). OpenSooq prices are in pounds and riyals at multiple unofficial rates; no credible figure.
- Tajikistan (`TJ`), Turkmenistan (`TM`). Nothing found in free sources.
- Cities other than the above Israeli ones, the Moroccan three and the Kazakh 19: not attempted.

## Sources I could not open, and what I would do next

- DLD Dubai Pulse bulk file (timeout), cbs.gov.il by curl (timeout), stat.gov.kz tables (dynamic site), bina.az, list.am, myhome.ge, Lalafo, Avito, Global Property Guide (403), Property Finder and Bayut (empty or 401). Parallel Search hit its free-tier rate limit partway through.
- Next steps in order of value: the Dubai Pulse CSV for per-area 70 to 110 m2 medians; list.am and bina.az samples through a headless browser (not run here, as the brief bans a GUI browser); the BNS Kazakhstan rent tables; a Tunis and Algiers sample from Tayara and Ouedkniss.

## Things you may have wrong

- `AE` is a Dubai figure. If most of your UAE people live in Dubai that is fine.
- Several "country" rows are the capital, which is dearer than the rest of the country (Oman, Saudi Arabia, Qatar, Kazakhstan, Uzbekistan, Ukraine, Azerbaijan, Kyrgyzstan, Moldova, Georgia, Belarus). The page says how local each figure is through `measured_for`; nothing here is a national average except Russia (Rosstat's own `RU`) and Israel.
- The ISO 3166-2 codes I used outside Russia, Israel and Kazakhstan (`AE-DU`, `AE-AZ`, `OM-MA`, `SA-01`, `UZ-TK`, `UA-30`, `AZ-BA`, `KG-GB`, `MD-CU`) are from memory of the standard; check them against the shapes.
- Mubawab pages came back with up to 34 cards each and, after 15 pages, 630 unique listings on Realt.by out of the 1,707 the site counts; both are the most recent or best-ranked, not random samples.
