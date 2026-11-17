# Housekeeper pay outside the US and Europe: notes

Written by AI on 2026.11.17 by model claude sonnet 5.5 (research owner for this part), with seven sonnet 5.5 sub-agents, one per slice. The per-slice notes follow the summary, unedited. Every row in `housekeeper.curated.csv` has a saved page in `cache/<source_id>/`; I re-checked the quotes against those pages by script (all but a few are verbatim matches; the rest are Thai, Chinese and scanned-PDF cases I checked by hand or that the slice notes flag).

## What is here

- `housekeeper.curated.csv`: 305 rows, 232 sources (`housekeeper.sources.csv`). Every `note` starts with `type=statutory-domestic-min`, `type=agency-price`, `type=direct-hire` or `type=survey`.
- Statutory domestic-worker minimums: 71 rows. Philippines (17 regions, monthly, kasambahay), Hong Kong, Taiwan, Thailand (provincial daily rates applied to domestic workers since Ministerial Regulation 15), Vietnam, Australia (two awards, neither a clean fit), Argentina, Uruguay, Costa Rica, Panama (two regions), Dominican Republic, Mexico (including the border zone), Brazil (São Paulo, Rio Grande do Sul, Paraná, Santa Catarina), South Africa, Morocco (60% of SMIG, derived), Kenya (Nairobi, Mombasa, Kisumu), Namibia, Zambia, Tanzania, Qatar, Kuwait, Tunisia, Malawi, Zimbabwe, Botswana, Liberia.
- Going rates: every one of the 25 cities has at least one agency or platform price and at least one other figure, except where the slice notes say otherwise. Montevideo, Da Nang, Muscat, Chiang Mai, Ubud, Tbilisi and Panama City are the thinnest.

## Read before using a figure

- `type=agency-price` is what the household pays a company. It includes the company's margin and platform fee, and is usually higher than what a freelance cleaner charges. The worker's pay is often 50 to 70% of it. `type=direct-hire` is a freelance or marketplace rate. Do not average across types.
- Short visits cost more per hour than long ones (Medellín: COP 26,000 an hour for a 4-hour visit, 17,060 for an 8-hour one). Our housekeeper works about 4 hours a time, so use the 4-hour rows, not an 8-hour price divided by 8.
- Several statutory figures are full-time monthly floors (Philippines, Costa Rica, Panama, Mexico daily). They are not an hourly rate for 4 hours a week and should not be divided into one without saying so.
- Legal minimums mostly sit well below the going rate in the same city (agencies and expat households pay more). Treat them as floors.
- Some countries have no domestic-specific floor (Singapore, Malaysia, Japan, Korea, Chile, Peru, Colombia, Saudi Arabia, UAE, Oman, Bahrain, Egypt, Lebanon, Jordan and others); the slice notes give the source that says so. ILOSTAT's general minimum wage covers those.
- Some rows are flagged `unverified` or "stale" in their note (for example Brazil's Santa Catarina floor, Taiwan's NT$20,000 foreign caregiver floor, Zimbabwe and Malawi from press only, Chiang Mai 2019, Montevideo's Expatistan copy). The least trustworthy are listed at the end of each slice.

## Things in the brief or the site you may have wrong

- Dubai: MoHRE suspended hourly and daily Tadbeer service on 16 March 2021 and I found no later notice. There is no current official hourly tariff; the only official figure is the 2018 AED 120 for 4 hours, recorded as stale. The hourly market is run by licensed and unlicensed platforms.
- Tokyo: `taskaru.com` is a parked domain; the company is Taskaji. Bears' price table is script-built and did not save; only its headline line is first-hand.
- Taiwan: no confirmed Domestic Service Act hourly guidance; the Labour Standards Act minimum wage does not cover directly hired domestic workers, and I could not save the ministry page that says so.
- Morocco: Law 19.12 sets the floor at 60% of the SMIG (not 50%); the row is my arithmetic, so it is derived.
- Paraguay: the old 60% rule is obsolete (Ley 6338/2019); the general minimum applies.
- Argentina: Res 7/2026 replaced the Annex 4 figure of Res 6/2026 (4,170.52 against 4,174.62 an hour). "Con retiro" means live-out and is the lower rate; press often swaps the labels.
- Panama has two regional rates under one code `PA`; pick by city (Panama City is Region 1, USD 350).
- Thailand: Ministerial Regulation 14 (2012) excluded domestic workers; Regulation 15 (2024) extended minimum wage to them. The Thai rows rest on ILO summaries of Regulation 15 plus Royal Gazette wage rates.
- Hong Kong: the Statutory Minimum Wage (HK$43.1 an hour) already covers local live-out helpers, so it is a general rate and needs no domestic row; the row recorded is the Minimum Allowable Wage for foreign live-in helpers.
- India: no figure recorded; no state gazette could be read.
- Not covered by my slices: Georgia, Mauritius, Azerbaijan, Uzbekistan, Kazakhstan, Israel, Algeria, Ghana, Uganda (no domestic-specific source found; general minimums are ILOSTAT's).

---


# Slice notes: c-eastasia

Written by AI on 2026.11.17 by model claude sonnet 5.5

# c-eastasia: housekeeper hourly rates, Tokyo, Taipei, Singapore, Bangkok, Phuket, Chiang Mai

Files: `c-eastasia.curated.csv` (52 rows), `c-eastasia.sources.csv` (34 sources). Every cited page is in `cache/<source_id>/` (`page.html` or `page.pdf`). Every quote was checked by script against the saved page, so each quoted cell exists in the saved copy. Searches ran in English, Japanese, Chinese (traditional) and Thai.

## Rows per city

| City | Rows | Agency/platform | Direct-hire | Survey/guide |
|---|---|---|---|---|
| Tokyo | 11 | CaSy x3, Bears x2, Kajitaku | Taskaji x2, Setagaya Silver Centre | Curama x2 |
| Taipei | 11 | OK Housekeeper, Jacker x2, Bounbang x2 | Jacker private cleaners x2 | PRO360 x2, Tasker x2 |
| Singapore | 12 | Helpling x2, StringsSG x2, Sureclean, Urban Company, HelperGo, Luce | Homejourney x2, Urban Company guide x2 | none |
| Bangkok | 9 | Kiidu x2, Q-CHANG, HomePro x2, ThaiHelper agency band x2 | ThaiHelper direct x2 | none |
| Phuket | 5 | Phuket Maids | Phuket Expat Guide x4 | none |
| Chiang Mai | 4 | HomePro, Perfect Homes | Chiang Mai Clean, 2019 post report | none |

A range on a page is two rows (low end, high end), marked in `note`. Per-visit prices (HomePro, Q-CHANG, Phuket Maids, Kajitaku, Setagaya) are `per_visit` with the hours in the note, because those pages state the visit price, not an hourly one.

## What the figures really measure

- **Tokyo.** CaSy is a platform that vets its cleaners: 2,790 JPY/h weekly, 3,490 one-off, tax included, plus 880 travel per visit. It rises to 2,950 on 2026-12-01 (both are rows). Bears 4,840 JPY/h (2 to under 3 h) is from its own page; its 4,180 (3 h or more) comes from a review site, because Bears' price table is built by JavaScript and did not save. Kajitaku publishes per visit only (9,900 for 2 h weekday weekly, travel 1,100 included, so 4,400 JPY/h before travel). Taskaji is the direct-contract marketplace: lowest tier 1,500, top tier 4,190 (PULMO). Curama's 3,000 to 4,500 is a national editorial range, not Tokyo-specific. Setagaya Silver Human Resources Center (members aged 60+): 2,712 JPY for 2 h, as at 1 April 2024.
- **Taipei.** Company or platform prices run 450 to 650 TWD/h (OK Housekeeper 600 on a 3-month contract; Jacker 450 to 650 by cleaner level; Bounbang 450 to 600), all with a 3 to 4 hour minimum. Private cleaners are quoted at 400 to 550 TWD/h (Jacker), 350 to 600 (Tasker), and PRO360's statistic of marketplace quotes is 400 to 600. Platform pages price Taiwan-wide, not Taipei only.
- **Singapore.** Platform "from" prices are 19 to 24 SGD/h for regular cleaning (Urban Company 19, Luce 18 before GST, Helpling 21, Sureclean 22, HelperGo 22, StringsSG 22.75 to 23.58). Helpling adds a 3.90 SGD fee per booking and 10 SGD on Fri-Sun, and does not bring equipment; Urban Company brings its kit. Direct-hire figures (18 to 25 SGD/h) come only from vendor guides.
- **Bangkok.** Kiidu publishes 250 to 350 THB/h (4 h minimum, +10% fee, +7% VAT). HomePro sells a 3 h visit for 950 THB (about 317 THB/h) and a 6 h visit for 1,650 (about 275 THB/h). Q-CHANG starts at 590 THB per 2 h. ThaiHelper's guide puts agencies at 400 to 700 THB/h and direct hire at 200 to 350.
- **Phuket.** Phuket Maids prices a one-maid, 2 h visit of a small condo at 550 THB (275 THB/h). The independent figure is Phuket Expat Guide: 150 to 300 THB/h.
- **Chiang Mai.** HomePro's 950 THB per 3 h visit (Chiang Mai is in its service area). Perfect Homes (a local property agency): companies "start at 250 THB/h", and a direct hire may save "a hundred baht or so an hour". A small advert gives 500 THB for 3 h. The 120 THB/h figure is from a 2019 post report.

## Statutory domestic minimums: none added

No row of `type=statutory-domestic-min` for any of these countries. I found only general minimum wages, which the ILOSTAT agent covers; I record them for context.

- Japan: Tokyo's general minimum wage is 1,280 JPY/h from 2026-10-01 (Tokyo Labour Bureau, per search results; I did not save the page). Household workers employed by a family are outside the Labour Standards Act; I did not find a domestic scale.
- Taiwan: general 196 TWD/h and 29,500 TWD/month from 2026-01-01, official page saved at `cache/tw-mol-minwage-2026/`. A search result reporting a Ministry of Labour statement says domestic workers are outside the Labour Standards Act minimum; I did not save that page, so treat it as unverified. The Domestic Service Act (家事服務法) is about providers and training. I found no rate guidance in it, and I could not open its text on law.moj.gov.tw. The brief expected rate guidance there; I could not confirm it exists.
- Singapore: no general minimum wage. The Progressive Wage Model covers cleaners employed by cleaning firms, not households (unverified, from a search result). MOM says foreign domestic workers may not take part-time work for another household (saved: `cache/hh-singapore-mom-fdw-parttime/`), so the households' part-time cleaners are citizens, PRs or work-permit holders (Household Services Scheme). The "foreign domestic worker salary" is a different thing and is not recorded.
- Thailand: general daily minimum wage only (400 THB in Bangkok and Phuket from July 2025 per search results; Chiang Mai lower; 2026 rates unconfirmed; not saved). One expat guide claims domestic workers have been covered by it since 2024 rules. I could not confirm that.

## What is thin

- Chiang Mai is the weakest city. One agency-style price (HomePro, shared with Bangkok), one 2024 snapshot ("start at 250"), one advert, and a 2019 post report. No 2026 independent figure.
- Phuket has one agency price page and one independent source (Phuket Expat Guide, affiliate-funded, no named author). Its salary guide gives a daily rate of 300 to 500 THB without hours.
- Singapore direct-hire is vendor guides only (Homejourney, Urban Company). No survey, no worker-organisation figure; no government rate exists.
- Tokyo has no government hourly guide. The Setagaya Silver Centre quote is from April 2024 and the page does not say whether tax is included. Silver centres in other wards charge different amounts (a Sumida figure of 1,214 JPY/h for continuing work appeared in search results; I could not save the page, so it is not a row).
- Taipei: no agency price page found for 愛媽咪 (Aimami), 好幫手 or DoDo after searches; the sites did not load or showed no price. Rows use other Taipei and Taiwan-wide platforms instead.
- Bangkok: Maidtobe, Sorbet, Smile Clean and BeNeat have no price I could save (BeNeat's page is script-built and saved nothing). Not recorded.
- Platform pages quote Taiwan-wide or Japan-wide prices; `measured_for` says so on each row.

## Things the owner may have wrong

- Casy/Bears "publish yen per hour": CaSy does, and its price changes on 2026-12-01 (both are rows). Bears' table is script-built and I could only save the 4,840 line from it; Kajitaku publishes per visit only.
- `taskaru.com` is a parked domain; the company is Taskaji (`taskaji.jp`).
- The same HomePro page covers Bangkok and Chiang Mai at one national price. I wrote one row for each city from the same source (`hh-bangkok-homepro-3h`); the source id carries the Bangkok prefix.
- Hourly "agency price" is not like for like: some include supplies and travel (Urban Company, Phuket Maids), some do not (Helpling, CaSy travel, Bears travel), some are before tax (Luce, Sureclean per a listing site). Read the row note before comparing.
- Several rows are marketplace price lists written by the marketplace, not independent surveys. Rows say so.

## Figures I trust least

1. Chiang Mai 120 THB/h (Talesmag, March 2019): over 7 years old and before minimum-wage rises.
2. Phuket 150 to 300 THB/h and 300 to 500 THB/day (Phuket Expat Guide): affiliate-funded, no author, no method.
3. Singapore direct-hire 18 to 25 SGD/h (Urban Company guide, Homejourney guide): each is written by a business that sells cleaning, and neither shows its data.

## Not used, deliberately

Livingcost and Expatistan were seen in search results (Bangkok about 259 THB/h, Phuket about 204, Chiang Mai about 183 per search summaries). I did not save or use them. Numbeo not used.

---

# Slice notes: c-sea-gulf

Written by AI on 2026.11.17 by model claude sonnet 5.5

# c-sea-gulf: part-time cleaner and housekeeper hourly prices, 9 city codes

Files: `c-sea-gulf.curated.csv` (75 rows), `c-sea-gulf.sources.csv` (43 sources). Every source page is saved under `cache/<source_id>/` (`page.html`). Two exceptions are listed below.

## Rows per place

| Place | Rows | Agency | Direct hire | Survey |
|---|---|---|---|---|
| Kuala Lumpur CITY-1735161 | 9 | 7 | 2 | 0 |
| Penang (George Town) CITY-1735106 | 8 | 5 | 2 | 1 |
| Ho Chi Minh City CITY-1566083 | 12 | 4 | 6 | 2 |
| Da Nang CITY-1583992 | 9 | 5 | 2 | 2 |
| Denpasar / south Bali CITY-1645528 | 12 | 2 | 6 | 4 |
| Ubud CITY-1622846 | 1 | 1 | 0 | 0 |
| Dubai CITY-292223 | 13 | 5 | 1 | 7 |
| Muscat CITY-287286 | 5 | 3 | 2 | 0 |
| Tbilisi CITY-611717 | 6 | 2 | 0 | 4 |

Where a source gives a range with no central figure, I wrote two rows (low end, high end) with the same quote. I did not take a midpoint. Where a source gives a price for a session of N hours, the row is `per_visit` and the note starts `type=...;` then `hours=N`.

## What the figures mean (order of trust, per place)

### Kuala Lumpur and Penang (MYR)
- Agencies and apps publish a session price, not an hourly rate. Maideasy: RM120 per 4 man-hours weekly, RM135 on demand, both before 8% SST, tools +RM35. bTaskee: RM79 for 2 h, RM99 for 3 h, RM125 for 4 h (about RM31 to RM40 per hour). Hauzmaid: RM35 per maid-hour from 3 maid-hours. Recommend.my and PT Clean always send 2 cleaners.
- Agency price per cleaner-hour in KL is RM30 to RM40. That includes the agency margin and (for some) tools.
- Direct hire is thin and contradictory. Helperex (a maid-recruitment site) says RM12 to RM20 per hour nationally with no source. Penangrenovations (a contractor directory) says RM20 to RM35 for Penang. Neither shows method. I found no KL-specific direct-hire figure. Treat direct hire as RM15 to RM30 with low confidence.
- Penang: bTaskee only launched there on 1 November 2026 and says it uses KL prices. That is a stated plan, not a booking history. Local agencies are cheaper (Asian Cleaning from RM19.90 per hour, PN Cleaning RM85 for 4 hours, Lye Intl RM25 per hour).
- Hauzmaid changed its rate between my search snippet (RM40 per hour for 2 hours) and my fetch (RM35 per hour, min 3 hours) on the same day. Small agencies edit prices often.
- Malaysia has a general minimum wage only. I did not research domestic-worker rules in Malaysia. I record no `statutory-domestic-min` row.

### Ho Chi Minh City and Da Nang (VND)
- bTaskee shows two different price sets. Its hourly housekeeping page: VND 192,000 for 2 h, 240,000 for 3 h, 304,000 for 4 h. Its price blog (reference prices for the An Khanh area of HCMC, September 2026): from VND 216,000, 270,000, 360,000. The gap is probably an area adjustment. Both rows are in the file. Neither page is labelled by city.
- JupViec says only "from VND 70,000 per hour"; its real prices sit inside the app. I could not get its Da Nang price. A job ad on Viec Lam Tot says JupViec opened in Da Nang in late 2026.
- Phuong Nam publishes the wage paid to the helper (VND 55,000 to 60,000 per hour for 2 to 4 hours a day), without the agency fee. It is a floor under what the household pays, so I marked it `direct-hire`.
- Direct hire in HCMC: VND 60,000 to 90,000 (Visreal, attributes to a muaban.net guide I could not open) and 60,000 to 120,000 (Lease in Vietnam, one range for HCMC, Hanoi and Da Nang). Both are expat-agency guides without method. They agree with each other, which is weak evidence because they may share a source.
- Da Nang agencies: Novoking (undated page) VND 125,000 to 150,000 one-off, 80,000 for one session a week, 50,000 for six. Giup Viec Da Nang VND 35,000 to 50,000 per hour is from 2023 and is for a full-day helper, so it is stale and not comparable. Da Nang direct-hire evidence is only the shared three-city range from Lease in Vietnam. The monthly USD ranges from Vietnam Knowledge (weekly part-time cleaner HCMC USD 80 to 150, Da Nang/Hoi An USD 50 to 100) state no hours.
- Not used: Viec Lam Tot (a job board) summaries for Da Nang were unstable. On 2 November the search snippet said VND 70,000 to 100,000 per hour for hourly housekeepers; the saved snapshot of 16 November said VND 30,000 to 40,000 per hour for part-time work. The site blocks plain fetches (403), so I used the Wayback copy. A bTaskee job ad at "from VND 80,000 per hour" is the worker's pay, not the household price. I removed these caches.
- Vietnam has regional general minimum wages only; someone else covers them. No `statutory-domestic-min` row.

### Bali (IDR)
- Agency prices on pages I could read: Bali Villa Cleaning IDR 150,000 per hour (2-hour minimum, one island-wide rate; aimed at villa owners, so the top of the market). Clean Hub Bali IDR 350,000 per 2 to 3 hour visit with two cleaners. Pinhome (Gojek) says from IDR 55,000 per hour in Denpasar, but that page is a 2022 launch article (modified June 2026), so I did not use it as a row and did not save it.
- Direct hire evidence is weak and mostly second-hand: Lokalfinds quotes the Knowmads Bali guide (IDR 50,000 to 75,000 per hour ad hoc) and a Bali Villa Hub scale (IDR 100,000 to 250,000 per day for a one-off day). I could not open Knowmads or Bali Villa Hub (the latter returned 429 errors). Last Call Bali: IDR 100,000 to 200,000 per 2 to 4 hour visit.
- The monthly figures (Bali Estate Manager: IDR 3.0 to 4.0 million net for a full-time housekeeper without English, 6 days a week) are a full-time job. They are in the file to anchor the part-time rate: 3.0 million divided by 173 hours is about IDR 17,300 per hour. That implies a part-time direct hire is probably IDR 25,000 to 50,000 per hour, below the Knowmads range. The expat "ad hoc" price and the villa-agency price are well above the local wage floor.
- Ubud has one row only (Bali Villa Cleaning lists Ubud and has one island-wide rate). Bali Estate Manager says Ubud may be 10 to 20% lower for staff, and Canggu and Seminyak sit at the top.
- Minimum wage reference (no row, because it is a general minimum, not a domestic one). Governor's Decree No. 1021/03-M/HK/2025 of 23 December 2025, in force from 1 January 2026: Badung (Canggu, Seminyak, Uluwatu, Jimbaran, Kuta) IDR 3,791,002.57 per month; Denpasar IDR 3,499,878.78; Gianyar (Ubud) IDR 3,316,798.48; Tabanan IDR 3,287,678.87; provincial minimum for the other regencies IDR 3,207,459. Source: Disnaker ESDM Bali announcement, saved as `cache/bali-umk-2026/umk.pdf` (official PDF). The announcement says it is the floor for workers with under one year of service. 173 hours a month gives about IDR 21,900 per hour in Badung.
- Indonesia passed a domestic-worker law in 2026 (Law No. 2 of 2026). Lokalfinds (`cache/hh-bali-lokalfinds-staff/`) says pay in a private household is left to the parties pending an implementing regulation. I could not open the law. No `statutory-domestic-min` row.

### Dubai (AED)
- The market is agency and platform only. Hourly maids must come from a licensed company; GCC Domestic says a freelance hourly maid is illegal for both sides. So there is no real "direct hire" going rate; the single `direct-hire` row is an old official MoHRE rate (below).
- Platform rates (2026-11): Helpling UAE from AED 35 per hour (maids page) and AED 37 (cleaning page); Justlife AED 35 per hour; Urban Company AED 52 for a 1-hour booking, AED 139 for 4 hours without materials (AED 34.75 per hour). inDubai.city compared 12 provider pages on 26 September 2026: AED 23.99 per hour (cheapest), ServiceMarket AED 34 per hour for 4 to 8 hours ex VAT, Maid Corner AED 120 for 4 hours VAT included. That is an independent comparison, though a convenience sample.
- Plan on AED 30 to 40 per hour for a 3 to 4 hour booking, AED 45 to 55 for a 1 hour slot. VAT (5%), materials (AED 10 per hour) and area can add to it.
- Tadbeer: MoHRE's June 2018 package priced hourly work at AED 120 for 4 hours (Gulf News report, saved). MoHRE announced on 16 March 2021 that hourly and daily provision was suspended at Tadbeer centres, in the Covid context (`cache/dw-ae-mohre-suspension-2021/`, Wayback copy as the live site would not connect). I found no later MoHRE notice. The private directory tadbeer.center says AED 35 to 60 per hour "(2-year package)" for Tadbeer part-time maids; I flagged it unverified. So the Tadbeer hourly route may not exist in 2026. The brief's assumption that a "MoHRE-licensed hourly part-time maid service price" exists as an official tariff is not supported: no official hourly tariff is published.
- No domestic minimum wage found for the UAE; not searched in depth.

### Muscat (OMR)
- Agency evidence is thin. CleanWave Muscat: OMR 5 per hour residential, 2 hours recommended. Justclean (a GCC app): studio OMR 7 to 10 for 2 to 2.5 hours (about OMR 3 to 4 per hour), 1 bedroom OMR 8 to 11 for 2.5 to 3 hours. The Justclean page is JavaScript-rendered, so `cache/hh-muscat-justclean/page.html` is an empty shell; the prices are in `rendered-text.md`, which holds the page text as a fetch tool returned it on 2026-11-17 (I transcribed it).
- Direct-hire evidence: GCC Domestic (an agency directory guide) says OMR 3 to 5 per hour. No method.
- Legal context (OmanHousemaids guide, `cache/ref-muscat-omanhousemaids/`): there is no legal minimum pay for domestic workers in Oman (Ministerial Decision 574/2025, in force 13 October 2025, requires a stated wage but sets no amount). Part-time work rules (MD 13/2025) are limited to Omanis, and a sponsored domestic worker may not work for others (Art. 9). So a legal part-time maid for expats probably comes through a company, as in Dubai. I did not read the decisions themselves.
- Not used: Expatistan says OMR 3.72 per hour (a search snippet said 7 price points, "only a guess"); I could not fetch the page (403) so I have no saved copy. The 2009 blog "Maids in Oman" quotes OMR 2 per hour; too old to use. Dubizzle and OpenSooq classifieds show "OMR 3" for part-time maids with no unit stated, so I did not use them.
- Oman has no domestic minimum wage; the OMR 325 minimum covers Omani private-sector staff only (OmanHousemaids). No `statutory-domestic-min` row.

### Tbilisi (GEL)
- Real hourly agency price: Vardo, GEL 30 per hour, 1 staff member, "Hourly Cleaning" package. Most other companies price by area or by visit (DMPROCLEAN from GEL 89 for a standard 1-room clean with no hours stated; Vardo standard cleaning GEL 3 per m2).
- Independent: the US State Department post report (via Tales Magazine) records the average housekeeper at GEL 18.75 per hour in 2024 (range GEL 16 to 25), up from 14.8 in 2022 and 17.1 in 2023. It is an expat-reported figure. A reviewer says a "nanny mafia" overcharges foreigners and locals pay less. ExpatHub (2023) budgets USD 80 a month for a weekly cleaner; it is old and not a price list.
- Searches: I ran 9 queries, in English, Georgian and Russian, for Georgian hourly prices. Other agency pages (Sparkle from GEL 157, FixFox GEL 175 to 235 per clean, Helpers City from GEL 80) showed prices only in a search snippet, not in the saved HTML, so I did not record them. The ss.ge services marketplace (which a snippet says lists cleaners from GEL 50 to 90 per day, and says a standard apartment clean costs GEL 60 to 130 and takes 3 to 5 hours) returns 403 to plain fetches. The Facebook group "Expats in Tbilisi" had a post saying USD 5 to 7 per hour; I could not open it. The agency price gap (Vardo GEL 30 vs expat-reported GEL 18.75) probably shows the agency margin plus a foreigner premium.
- Georgia has a general minimum wage only. No domestic row.

## Doubts, and what the owner may have wrong

1. Hourly versus per session. Most agencies publish a session price (2 to 4 hours, sometimes 2 cleaners). I turned none of these into hourly rows. Dividing is easy, but the minimum booking and per-hour discount for longer sessions make the 1-hour price much higher than the 4-hour price (Dubai: AED 52 for 1 hour against AED 34.75 per hour for 4 hours).
2. "Agency vs direct hire" is not clean in the Gulf. In Dubai and Muscat the legal route is always a company, so a direct-hire hourly price does not exist as a market.
3. Penang bTaskee prices are a launch announcement for 1 November 2026.
4. The Bali agency figure (IDR 150,000 per hour) is a villa-owner price; the direct rate for an expat renting a flat is likely much lower.
5. Da Nang has no current hourly agency price I could confirm from a saved page apart from one undated agency page and one stale one.
6. Currency note: the vietnamkb and expathub rows are in USD as published.
7. Livingcost, Expatistan and Numbeo were not used as sources. Expatistan (Muscat OMR 3.72, Tbilisi GEL 18, Denpasar IDR 58,254) agrees roughly with my rows but I did not save the pages. Numbeo appeared in a search snippet only.
8. Tools: Parallel search hit its free-tier rate limit mid-session, so later searches used WebSearch. Several pages (Helpling UAE) needed `curl -k` because the site certificate had expired. Some Wayback copies were used (MoHRE notice). Nothing was contacted or signed up for.

## Cleanup
Temporary scripts in `/tmp/c-sea-gulf/` are removed at the end. Nothing else was written outside `tools/world/housekeeper/parts/c-sea-gulf.*` and `cache/`.

---

# Slice notes: c-mea-ca

# Housekeeper rates: Marrakesh, Cape Town, Mexico City, San José (Costa Rica), Panama City (part c-mea-ca)

Written by AI on 2026.11.17 by model claude sonnet 5.5

## What I covered

Going hourly rates for a part-time live-out cleaner in five cities, agency price and direct hire, from 34 saved pages (`cache/<source_id>/`). 38 rows in `c-mea-ca.curated.csv`:

| Place | Rows | Agency price | Direct hire | Survey |
|---|---|---|---|---|
| Marrakesh `CITY-2542997` | 6 | 2 | 4 | 0 |
| Cape Town `CITY-3369157` | 4 (+3 under `ZA`) | 2 (+1) | 2 (+1) | 0 (+1) |
| Mexico City `CITY-3530597` | 6 (+1 under `MX`) | 4 | 1 (+1) | 1 |
| San José `CITY-3621849` | 7 | 3 | 4 | 0 |
| Panama City `CITY-3703443` | 11 | 4 | 5 | 2 |

Every quote was checked by machine against the saved page text. Where a source gives a range the amount is the midpoint and the note says so.

## Read this first: what the owner needs to know

- **The sources disagree by a factor of two to four inside each city.** The gap is mostly agency price against what the worker is paid. Do not average rows across `type`. For a household's cost, use agency or platform price; for what a worker earns, use direct hire.
- **No city has a government or union hourly rate for going market pay.** Government sources only give legal floors (Mexico's domestic-worker professional minimum, Costa Rica's MTSS, Panama's MITRADEL, Morocco's law 19-12, South Africa's NMW). Those are someone else's, but I noted the figures below. The "independent" figures in every city are expat guides, price guides of quote marketplaces, or news reports. None is a rigorous survey. Be careful how much weight the map puts on them.
- **Several figures are marketplace estimates, not prices anyone quoted.** I flagged each in `note`.

## Per city

### Marrakesh
- Agency price: Hany (a home-services platform) publishes hourly prices for Marrakech: 70-80 MAD/h weekly, 80-90 one-off, 60-70 for a monthly commitment, 3 hour minimum.
- Direct hire: Allo Maison/Hanæ (a marketplace; `allo-maison.ma` now redirects to `hanae.ma`) gives 130-200 MAD for a 6-7 hour day (about 19-33 MAD/h). Stoniz (relocation blog) and Allozain (agency blog) both say 25-40 MAD/h. The two ranges are identical, so they may share an origin.
- Agency price is about double the direct figure: 75 against 25-35 MAD/h.
- No government or worker-organisation rate found. Searches (French, Arabic, English, more than 8 queries including "Mjob femme de ménage tarif", HCP and NGO surveys, expat forums) found only classified ads, Expatistan and legal texts. Mjob has no readable price page. The legal floor is 60% of the SMIG for a full-time domestic worker under law 19-12 (stated on the saved Allo Maison page); no row, per the brief.
- Expatistan says 129 MAD/h for "cleaning help" in Marrakech. It rests on 6 price points, calls itself "only a guess", and is 4-5 times the other sources. I did not record it (aggregator, cross-check only) and I would not trust it.

### Cape Town
- SweepSouth no longer publishes a plain hourly rate. Its help page says the price is an estimate from duration, day of week, frequency and local demand. What it publishes: R250-R350 for a weekly clean of a 3-bed 2-bath house (hours not stated); Express (1-3 hours, specific tasks only) R199 Mon-Thu, R299 Fri-Sun. An old SweepSouth page on `api.sweepsouth.com` says "from R29 per hour"; that is below the R30.23 national minimum, so I treated it as stale and did not record it.
- What SweepSouth pays the cleaner: about R210 for an average 7.1 hour booking (about R29.6/h). Worker keeps 80-96% of the fee. The article is undated (I inferred 2024 from the pre-2022 minimum bands it cites), so the real current figure will be higher.
- Marketplaces: JobZapp R36-R90/h (plus about 20% booking fee); Care4SA R70/h typical (R40-R120). ProCompare gives R63-R100/h (average R94) for cleaning companies, nationally. Kandua, Motelo and Shalean repeat that same band, so I treated them as one source.
- Expat guide (Relocating to South Africa): R150-R250 a day for a once- or twice-weekly cleaner; the same guide says R6,000-R9,000 a month for a full-time live-out worker.
- SweepSouth's own 2025 survey: average hourly earnings of South African domestic workers R33.71 (39% below the minimum). Whole-country, skewed to its platform.
- Domestly and Bark: I found no published Cape Town price for either (Domestly only as a third-party directory listing; Bark's Cape Town pages did not show an hourly price in search results; I did not open them).
- Expatistan (R60/h, 5 data points) and Payscale ignored, cross-check only.
- The SweepSouth rows sit under the Cape Town code because it is the home city and flagship market, but the pages are national. The 2020 Expat Info Desk figures for agencies (R180-R205 a day) are too old, so I left them out.

### Mexico City
- Agency price: Aquilimpio 200 MXN/h, 4 hour minimum; Limpieza Help 150 MXN/h reference. Cronoshare says 350-400 MXN/h for CDMX. That is double the next highest, so treat it as an outlier.
- Survey/price guide: Habitissimo 100-200 MXN/h per professional, built from user quote requests.
- Direct hire: Infobae (Nov 2025) quotes Indeed and Aliada.mx at 60-100 MXN/h in big cities and 70-90 for platforms. I could not open those two sources, so both rows are flagged unverified. They look low next to the agency prices above; they are probably what the worker receives.
- Worker organisation: CACEH's 2026 scale, as reported by Infobae: 500 MXN per day for deep cleaning, 450 for washing and ironing. CACEH's own site did not show the scale, so unverified. Placed under `MX`.
- Statutory floor, for the owner who covers it: Conasami's 2026 professional minimum for domestic workers is 342.47 MXN per day (440.87 on the northern border), about 43 MXN/h on an 8-hour day. It is sourced in the Infobae June 2026 page I saved (`hh-mexicocity-infobae2026`). No row, per the brief.
- Hogaru and Aliada.mx have no readable price on their pages (Aliada says workers set their own rates). The CDMX labour ministry bulletin 6/2025 on domestic workers (IMSS average daily base wage 339.7 MXN for women) would have been a government source, but the site timed out and the Wayback Machine has no copy, so no row. The COPRED CDMX report has 2020-21 survey data (average 3,121.65 MXN a month), too old to use.

### San José, Costa Rica
- Agency price: DomestiHogar "from 2,500 CRC/h". It is a placement agency in Cartago, not San José, and the figure is a floor. Mabbi estimates 5,500 CRC/h or more for a formal service with social charges, and 3,500-5,000 for a company. These are Mabbi's own estimates, not a named company's price list.
- Direct hire: Mabbi 2,500-3,500 CRC/h (4,000-5,000 in Escazú, Santa Ana, San Pedro, Heredia); Q Costa Rica 2,500 CRC/h in the Greater Metropolitan Area (unnamed sources); Wellfred expat guide USD 3-5/h.
- No agency in San José itself publishes an hourly price that I could read. Mucamas.cr and similar sites say "get a quote". Zubi says each pro publishes a rate after sign-up. Search queries in Spanish and English (7) found only the above.
- MTSS (the Ministry of Labour): hourly or daily domestic pay is contractual, not set by the decree. Its reference is monthly minimum / 30 / 8, which with the 2026 minimum of 268,731.31 CRC comes to about 1,120 CRC/h. The saved MTSS page still shows the older 258,376.22. That is a floor and not a market rate.
- Mabbi notes that formal pay carries about 25.33% employer social charges, so the 2,500 informal rate is not the cost of a regular formal hire.

### Panama City
- Agency price: Maid in Panama "from USD 60 per visit" and Lavanda "from USD 30" (one cleaner). Neither states hours, so there is no hourly figure. Inside Panama says agency hourly cleaning is USD 4-8; Yoklean says USD 10-15 for Panama (weak source, no method). Helping Clean's USD 32.10 promo (4-5 hours) was blocked and is not recorded.
- Quote data: Camarounds (a quote marketplace) published offers in Sept 2026. One offer is USD 30 for about 6 hours (about USD 5/h), another USD 47 for 7 hours (about USD 6.7/h). Its 2022 analysis gave USD 7-12/h for 90% of cases, four years old.
- Expat guides: Inside Panama USD 5-10/h for occasional help and USD 25-40 a day; MoveIn Panama USD 15-25 per session; "Tales From a Small Planet" USD 20-30 a day (2021).
- No government or worker-organisation figure found. MITRADEL's domestic minimum belongs to another agent: Inside Panama puts it at USD 275-380 a month depending on zone; check the decree.
- Camarounds' 2026 article has a single USD 32/h offer. It includes products and is an outlier, so I did not record it.

## What I trust least

1. **Cronoshare, Mexico City, 375 MXN/h.** Double any other Mexican source, no method.
2. **Stoniz and Allozain, Marrakesh, 32.5 MAD/h.** Identical ranges, unsourced, from a property blog and an agency blog. They may not be independent.
3. **Mabbi's formal-service 5,500 CRC/h.** An estimate of what a company must charge. No company in Costa Rica published that figure.

Also soft: the SweepSouth worker-pay article is undated, and the Infobae rows are second-hand.

## For the owner

- The measures differ: agency/platform price to the household; what a worker is paid; a day rate with unstated hours. The map should say which it shows. A defensible choice for a couple that employs someone is the direct-hire figure plus social charges (Costa Rica about 25%, Panama about 30%, Mexico requires IMSS, Morocco CNSS about 18-20% per two guides).
- Rows with `per_day` or `per_visit` do not give an hourly rate without a stated number of hours; I recorded the hours where the source gave them.
- Parallel's search tool hit its free-tier rate limit partway through (shared with other agents), so some searches used WebSearch. Wayback copies stood in for two pages blocked by Cloudflare (SweepSouth help pages).

---

# Slice notes: c-sam

Written by AI on 2026.11.17 by model claude sonnet 5.5

# c-sam: going rates for a part-time live-out cleaner, six South American cities

Files: `c-sam.curated.csv` (66 rows), `c-sam.sources.csv` (28 sources). Every cited page is saved in `cache/<source_id>/` (`page.html` or `page.pdf`, plus a `page.txt` text copy I made). I checked every quote in the CSV against the saved text copy (0 mismatches). Retrieved 2026-11-17.

## Rows per place

| Place | Rows | Real agency or platform price pages | Other figures |
|---|---|---|---|
| Medellín `CITY-3674962` | 14 | Holper, Clean Solutions LIM, Limpiarte, Anitas (agency's market range) | Solverio marketplace blog (direct hire ranges) |
| Lima `CITY-3936456` | 17 | LimpioTuDepaPeru, Toplim, Hadas (via ILO study), Reludcir (agency blog summary) | ILO study (Loop, 2 interviews), La Celestina (direct hire), Reludcir (direct hire day rate) |
| Florianópolis `CITY-3463237` | 13 | Donamaid, Mais Capricho (firm's range) | Workfly, GetNinjas, Odete, Famyle, Cronoshare (all direct-hire or marketplace figures) |
| Santiago `CITY-3871336` | 11 | Appseo (2 pages) | Jobbing, Cronoshare x2, 2x3 (marketplace quote summaries) |
| Buenos Aires `CITY-3435910` | 6 | Zolvers (2 rows), Servidos, Solvit | none independent; legal scale below |
| Montevideo `CITY-3441575` | 5 | ArreglaTodo | Expatistan 2024 copy, cross-check only |

## How to read the rows

- Most platforms quote a **visit** price, not an hourly one. These are `per_visit` with the hours in the note and the per-hour figure worked out in the note. Where the source states an hourly price (Zolvers, Appseo, Jobbing, ArreglaTodo, La Celestina) it is `per_hour`.
- Ranges are stored as two rows (low and high end), named as such in `measured_for`. I did not take midpoints.
- A visit price falls per hour as the visit gets longer. Medellín example: Holper COP 26,000 per hour for 4 hours, 17,060 for 8 hours. The owner's 4-hours-a-week housekeeper is one visit of about 4 hours, so use the 4-hour rows, not the 8-hour rows.
- Agency and platform prices include the platform margin and, for Colombian and Chilean firms that employ the cleaner, the employer's labour cost. Direct-hire figures do not include the employer's legal contributions, which are due for regular domestic help in all six countries (see below). So agency vs direct is not the same thing even before margin.
- Almost every price page is undated and live on the retrieval date. `period` is then `2026-11` and the note says "page undated". The search index showed older copies for Limpiarte (2025-05) and Toplim (higher prices than the live page), so these pages change.

## What each source really measures

- **Holper, Clean Solutions LIM, Limpiarte (Medellín):** rate cards of real firms. Holper: one national tariff for Bogotá, Medellín, Cali and Barranquilla, not a Medellín price. Clean Solutions: identical price for Bogotá, Medellín and the Caribbean coast, IVA included, employs staff itself. Limpiarte: plan (weekly, same cleaner) vs one-off prices; shifts are 3 h 40 min, 6 h, 7 h 35 min (includes a lunch hour).
- **Anitas (Medellín):** the agency's blog of what the market charges. Not a rate card.
- **Solverio (Medellín):** a marketplace blog, no method. It is the only Medellín figure for freelancers. Treat as indicative.
- **LimpioTuDepaPeru, Toplim (Lima):** real rate cards of Lima platforms, cleaner independent, client supplies products. Toplim "desde" prices.
- **ILO study (Lima):** CC BY 4.0, 2025. Gives Hadas package prices (5 h S/ 89, 6 h S/ 99, 7 h S/ 114) and what two Loop users said they paid (S/ 70-150 a day). The pages do not give the fieldwork date. Only 2 Loop interviews.
- **Donamaid (Florianópolis):** R$ 104.10 plus R$ 20 for each hour, quoted for a 1-bedroom 1-bathroom booking.
- **Workfly (Florianópolis):** its city range is its own national table (R$ 150-250) with a +15% Florianópolis uplift, shown in its blog. It is a rule of thumb, not local bookings.
- **Diária hours (Florianópolis):** a "diária" is not reliably 8 hours. Mais Capricho says 3-5 hours of work on average; Workfly says 8 hours. Per-day rows are marked with that doubt.
- **Appseo (Santiago):** a company that employs its cleaners; price list 2 h CLP 29,900, 4 h 39,900, 6 h 49,900, 8 h 59,900. Its "from CLP 7,500 an hour" is its 8-hour price divided by 8.
- **Jobbing, Cronoshare, 2x3 (Santiago):** quote marketplaces summarising what freelance cleaners and nanas ask. Method not stated. The 2x3 and Cronoshare asesoras rows are per day with hours unstated.
- **Zolvers (Buenos Aires):** a domestic-staff platform. Its quote form shows "Hora promedio" ARS 8,000 for a recurring cleaner and ARS 13,500 one-off. It does not say whether the price includes employer contributions. It is the only real agency price in the city.
- **Servidos, Solvit (Buenos Aires):** marketplace blogs giving ranges for invoiced one-off cleaning, not for registered domestic employees. Servidos (Nov 2026) says its values are reference estimates. Solvit was last updated 2 June 2026, five months of ARS inflation ago, and contradicts itself (headline ARS 5,200-8,300 an hour; detail table ARS 6,000-11,000).
- **ArreglaTodo (Montevideo):** estimator prices per hour, platform fee included, 3 Oct 2026.

## Statutory domestic wage items (no rows from me; another agent covers them)

- **Argentina (national, not Buenos Aires-specific):** no row, per the task. Another part has `dw-ar-cntcp-2026`. For the owner's cross-check: the Comisión Nacional de Trabajo en Casas Particulares scale (Res. 6/2026, corrected by Res. 7/2026), "personal para tareas generales", November 2026: ARS 4,170.52 per hour **con retiro** (live-out, the relevant one) and ARS 4,447.11 sin retiro; monthly ARS 511,639.37 and 562,284.09. The UPACP union page (`cache/hh-ba-upacp`) shows the same numbers. Careful: Los Andes (11 Nov 2026) prints with/without retiro the wrong way round, and La Nación (22 Oct 2026) prints the uncorrected Res. 6 figures (4,174.62 and 4,451.49). The registered legal floor is about half of the invoiced one-off prices (Servidos, Solvit, Zolvers).
- **Uruguay (national):** another part has `dw-uy-bps`. BPS: from 1 July 2026 the Grupo 21 "General" minimum is UYU 32,051 a month for 44 hours, UYU 169 an hour (cleaning and tidying category). ArreglaTodo's UYU 530-680 an hour is about 3 to 4 times the floor.
- **Chile:** no separate domestic scale. The saved `cache/dw-cl-dt` folder was empty when I looked. I did not verify the national minimum myself; one aggregator (cuantopaga.cl) quotes CLP 553,553 a month from 1 May 2026 under Ley 21.830, unverified here. Not recorded.
- **Colombia:** no separate domestic scale; the general minimum applies pro rata. Press (Infobae, 19 Mar 2026, saved in `cache/hh-medellin-infobae-pordias`, no Mintrabajo page found) says the floor for a domestic worker paid by the day is COP 76,394 for up to 8 hours (base 58,364 + transport 8,303 + Sunday-rest share 9,727, on a monthly minimum of COP 1,750,905). Other outlets found by search give COP 66,667 (no Sunday-rest share). I could not find the primary Mintrabajo text, so no row. Whoever covers CO should check the law (Ley 2466 de 2025).
- **Peru:** no separate scale; the general minimum (RMV) applies pro rata for hours. SUNAT's page, Wayback copy of June 2026, says S/ 1,130 for 48 hours a week "from 1 January 2025"; a search snippet of the live page shows S/ 1,230 from 1 October 2026, which I could not save (live SUNAT page returns 403). Saved at `cache/dw-pe-sunat-rmv`. No row.
- **Brazil (Santa Catarina):** not covered here, as instructed. For the diarista market, note the law (Lei Complementar 150/2015): a domestic worker on 3 or more days a week in the same home is an employee with contributions; a diarista is up to 2 days a week. A 4-hours-a-week cleaner is a diarista.

## What is thin or missing

- **Montevideo is the weakest city.** After nine different searches (Spanish, with BPS, MTSS, union, press and price-page angles) I found one real published price page (ArreglaTodo, a marketplace). No agency rate card, no government or union going rate, no survey. The only other figures are aggregators: Expatistan (UYU 322 per hour on 15 price points, Wayback copy of Feb 2024, saved as cross-check row; a search snippet shows a newer UYU 350 on 8 points that I could not save) and cuantomecuesta.com (UYU 250-450 per hour, no stated source, and it misstates the 2026 categories, so I did not use it). The floor UYU 169 is the BPS figure.
- **Buenos Aires:** one real agency-type price (Zolvers). Hogarth (www.hogarth.com.ar and hogarth.com.ar) did not load, so no Hogarth price. Solvit and Servidos are marketplace blogs.
- **Florianópolis:** no union or government going rate. I searched for the Santa Catarina domestic workers' union and Fenatrad rates (several queries including the local-language union and "tabela" angles) and found none published. The diarista figures are marketplace figures. Of the apps you named, only Donamaid and Workfly had a readable price; Parafuso, Triider, Zeladoria, Cleanwork, Donna Limpeza did not turn up with prices.
- **Santiago:** no Cleanmas/Yapo/Bark price page found. Maidon (placement agency) charges a one-off placement fee, for example CLP 125,000 for "nana por días y part time", which is not a wage, so no row. Dirección del Trabajo guidance not re-checked (empty cache folder from another part).
- **Medellín:** no Mintrabajo or union going rate beyond the legal floor above. The three real rate cards agree on about COP 104,000-110,000 for 4 hours. Helpling-like apps beyond Holper were not found.
- **Lima:** no MTPE going rate; the ILO study is the independent figure. Limpiazen, Loop and Manitas Limpiadoras were named only second-hand in LimpioTuDepaPeru's blog (Limpiazen 5 h S/ 76, 6 h S/ 88, 7 h S/ 99; Loop minimum S/ 70). I did not record these as rows because I did not save their own pages.

## What the owner may have wrong

- The 4-hours-a-week housekeeper is not paid the 8-hour-day rate divided by 8. Short visits cost more per hour (Appseo 4 h is CLP 9,975 an hour vs 7,488 for 8 h; Holper 4 h is COP 26,000 vs 17,060). Pick the 4-hour visit rows.
- In Argentina, Chile, Uruguay and Colombia a regular direct hire is a registered employee, and platforms that sell "no contract" service carry that cost in the price. Direct-hire rows here are asking prices, many from informal markets, and exclude that cost.
- Brazilian "diária" prices are not hourly: the stated hours range from 3-5 to 8.

## Three figures I trust least

1. `hh-flori-cronoshare`, BRL 98 per diária: about half of every other 2026 source for the city, and the same site gives R$ 70-120 for the whole country.
2. `hh-ba-solvit`, ARS 5,200-8,300 per hour: page last updated 2 June 2026 and its own detail table says ARS 6,000-11,000.
3. `hh-mvd-expatistan`, UYU 322 per hour: crowd-sourced, two years old, and Montevideo has only one other source (ArreglaTodo).

Close behind: `hh-flori-workfly` (derived from a national table with a +15% uplift) and the two `hh-lima-ilo-agencias` Loop rows (two interviews).

## Housekeeping

I removed cached pages that I fetched but did not use (Holper price page copy, LimpioTuDepaPeru home, 2x3 aseo, Servidos service index, cuantomecuesta, todoresuelto, MTSS). Kept in cache but not in the CSVs: `hh-ba-upacp`, `hh-sant-maidon`, `hh-medellin-infobae-pordias`, `dw-pe-sunat-rmv`, referenced above. Two Wayback copies are marked: `hh-mvd-expatistan` and `dw-pe-sunat-rmv`.

---

# Slice notes: w-asia

Written by AI on 2026.11.17 by model claude sonnet 5.5

# w-asia: statutory minimum wages for domestic workers, Asia-Pacific and Canada

Scope: minimum wages that apply to domestic workers specifically, in force on 2026-11-17. No going rates (agency or direct-hire prices) were in my slice. Files: `w-asia.curated.csv` (31 rows), `w-asia.sources.csv` (39 sources), saved pages in `cache/<source_id>/`.

## Rows written (count per place)

| Place | Rows | What |
|---|---|---|
| PH-00 NCR | 1 | PHP 7,800 per month from 2026-02-07 |
| PH-15, PH-01, PH-02, PH-03, PH-41, PH-05, PH-10, PH-13, PH-14 | 1 each | Kasambahay monthly minimum, from the NWPC tables |
| PH-40 CALABARZON | 1 | PHP 7,500 from 2026-10-26 |
| PH-07 Central Visayas | 1 | PHP 7,500 from 2026-10-14 |
| PH-11 Davao | 1 | PHP 6,500 from 2026-03-13 (one rate for cities and other municipalities) |
| PH-06 Western Visayas | 2 | PHP 6,500 now; PHP 7,000 from 2026-11-20 (not yet in force) |
| PH-12 SOCCSKSARGEN | 2 | PHP 6,000 now; PHP 6,450 from 2026-11-22 (not yet in force) |
| PH-08 Eastern Visayas | 2 | PHP 6,400 cities and first-class municipalities; PHP 5,800 other municipalities |
| PH-09 Zamboanga Peninsula | 2 | PHP 6,000 and PHP 5,500, same split |
| HK | 1 | HKD 5,220 per month MAW for foreign live-in helpers, contracts signed from 2026-10-03 |
| TW | 1 | TWD 20,000 per month for foreign household caregivers |
| CITY-1609350 Bangkok, TH-83 Phuket | 1 each | THB 400 per day |
| TH-50 Chiang Mai | 2 | THB 380 per day (Mueang district), THB 357 (rest of province) |
| VN | 2 | VND 25,500 per hour and VND 5,310,000 per month, Region I |
| AU-WA | 1 | AUD 26.27 per hour, WA state award that covers household employers |
| AU | 1 | AUD 27.08 per hour, Cleaning Services Award Level 1 (cleaning businesses) |

The PH-NIR (Negros Island Region) has no kasambahay order of its own yet. Negros Occidental including Bacolod is still under the Western Visayas order, and Negros Oriental under Central Visayas, per those two orders. I did not add a separate row.

## What each figure really measures

Philippines. Every figure is a monthly minimum for a kasambahay under RA 10361, one wage order per region. The orders cover live-in and live-out workers who regularly do domestic work in one household on an occupational basis. They exclude service providers, family drivers and anyone who works only occasionally or sporadically. No order states weekly hours. So these are full-time monthly floors. A cleaner who comes four to six hours a week is probably outside the order as an occasional worker; I could not find the implementing rules' treatment of part-time kasambahay, so there is no per-hour figure. Eastern Visayas and Zamboanga Peninsula have two rates inside the region (cities and first-class municipalities versus the rest). Davao's order had two rates last time and now has one. Sulu is inside the Zamboanga order. I checked the order PDFs themselves for NCR, CALABARZON, Western Visayas, Central Visayas, Eastern Visayas (scanned, read from the rendered page), Zamboanga, Davao and SOCCSKSARGEN. Other regions come from the official NWPC tables only. The Western Visayas and SOCCSKSARGEN "in force today" rows use the "current rate" column of the new orders, which say when the previous orders began (19 Nov 2025 and 2 Nov 2025).

Hong Kong. The Minimum Allowable Wage is the floor for foreign domestic helpers under the Standard Employment Contract, not under the Minimum Wage Ordinance. It is for live-in, full-time work: foreign helpers may not take part-time work or work at other addresses. Free food or at least HK$1,236 a month food allowance comes on top. The Statutory Minimum Wage (HK$43.1 per hour from 1 May 2026) excludes only live-in domestic workers (Labour Department Concise Guide 2026, page 2). So a local live-out part-time helper is covered by the general HK$43.1 rate. That is a general rate, so there is no row; the general-minimum-wage agent should have it.

Taiwan. NT$20,000 is a Ministry of Labor floor for foreign household caregivers (live-in), in place since August 2022. Household caregivers are outside the Labor Standards Act, so the general minimum (NT$29,500 per month, NT$196 per hour, 2026) does not apply to them. The 2027 rise (NT$30,900 and NT$205, approved 24 Sep 2026 per CNA) will not apply to them either. Average hours reported by the MOL survey are 10.1 a day. No floor exists for local part-time cleaners other than whatever the general law gives.

Thailand. Provincial daily minimum from Wage Committee announcement No. 14, in force since 1 July 2025. It applies to domestic workers because Ministerial Regulation 15 on Domestic Work (30 April 2024) brought them under minimum wage. I read the wage list as reproduced by Thairath from the Royal Gazette, and the domestic coverage from two ILO pages. Hours: an 8-hour day. The sources give no hourly figure and do not say how the daily rate applies to a few hours a week. The Wage Committee decided on 17 March 2026 not to raise rates and I found no later change.

Vietnam. No separate scale. Decree 145/2020 Art. 89(2) says a domestic worker's job-based wage must not be lower than the regional minimum wage. Decree 293/2025 gives the Region I (highest) rates from 1 January 2026: 5,310,000 per month, 25,500 per hour for hourly-paid employees. Region depends on where the employer operates; I did not map cities to regions. Regions II to IV are in the row notes.

Australia. Two floors, neither a pure household rule. The WA state Cleaners and Caretakers Award explicitly covers household employers who directly employ a cleaner in a private home, but only for state-system employers (WA households, sole traders and partnerships). The national Cleaning Services Award covers cleaning businesses, and its Level 1 tasks include cleaning private residences. So its AUD 27.08 is the floor for an agency or platform cleaner, not for a cleaner a household hires directly. Casual loading is 25% in both awards (AUD 32.84 and AUD 33.85 per hour).

## Countries with no domestic-specific floor (no row), and the source

- Singapore: MOM "does not prescribe minimum wages for all workers in Singapore, whether local or foreign" (MOM FAQ). The employer must pay the salary declared to MOM. Foreign domestic worker pay floors come from the source country. The Philippines raised its floor for Filipino domestic workers abroad from US$400 to US$500 (DMW advisory, August 2025, press reports only; one report quotes an official saying employers who pay less will not be penalised). I did not save or verify the DMW text and did not find an Indonesian official figure. This is source-country policy, not Singapore law, so no row.
- Malaysia: Minimum Wages Order 2024 (P.U.(A) 376), paragraph 2: "Perintah ini tidak terpakai bagi pekhidmat domestik" (the order does not apply to domestic servants as defined in the Employment Act 1955 and the Sabah and Sarawak ordinances). The Malaysia-Indonesia 2022 MoU: press reports conflict on whether it fixes RM1,500; the Human Resources Minister first said RM1,200 and later RM1,500. I found no primary document, so no row.
- Japan: Minimum Wage Act Art. 2(1) defines "worker" excluding "同居の親族のみを使用する事業又は事務所に使用される者及び家事使用人". The MHLW defines a domestic worker as someone who contracts directly with a private household. So a directly hired household cleaner has no statutory minimum. A cleaner employed by a housekeeping business is generally treated as a normal worker (1988 notice, in a search summary only; not saved), so the prefectural minimum applies; Tokyo is ¥1,280 from 1 October 2026 (up ¥54). MHLW's January 2025 study group asked for the exclusion to be reviewed.
- South Korea: Minimum Wage Act Art. 3(1) proviso: the Act does not apply to businesses employing only cohabiting relatives and to housekeeping employees (the 가사 사용인). The English text I saved is an older translation; the Korean text is quoted by korea.legal. The 2022 Domestic Workers Act covers staff of certified service providers; I could not establish from sources whether the minimum wage reaches them (a 2023 report said a pilot was planned; a June 2026 article says the exclusion is still abused by platforms). General minimum is KRW 10,320 per hour for 2026 and KRW 10,700 from 1 January 2027 (search results, not saved).
- Indonesia: Law 2 of 2026 on the Protection of Domestic Workers was passed on 21 April 2026. A law-firm summary says wages are set in the agreement; I found no statutory amount, and implementing regulations are due within a year. I did not find the statute text. UMP figures for Jakarta and Bali were not looked up because the general minimum is the other agent's slice and I found nothing saying UMP applies to domestic workers.
- New Zealand: adult minimum wage NZ$23.95 per hour from 1 April 2026 (Employment New Zealand); no domestic-specific rate found.
- Canada: provincial general minimums are the floor (for example Quebec's general rate of CAD 16.60 per hour from 1 May 2026, from a search result quoting CNESST; not saved). I could not confirm any domestic-specific minimum rule in Ontario, BC or Quebec, so I record none.
- Sri Lanka, Nepal, Bangladesh: nothing found. A search summary says Sri Lankan domestic workers are outside the national minimum wage law; for Nepal a 2021 report says the minimum wage applies in the formal sector only. Not verified, no row.

## India (not recorded)

Domestic work is a scheduled employment in several states, but I could not get a current figure from a gazette or labour department page. What I found and did not record: Karnataka's notification KAI 411 LWA 2023 of 22 May 2026 (a unified scale; domestic/household work is scheduled employment 14), only available as a payroll firm's unofficial translation of a degraded scan, with pending litigation; Tamil Nadu's reported 2018 hourly rates (Rs 37, 38, 39 for an 8-hour day, press); Kerala figures of Rs 195 to 219 per day dated 2016 (WageIndicator) and an undated Rs 37.50 per hour press report. Delhi and Maharashtra: nothing official found. A proper India row needs the Karnataka Kannada gazette or the other state gazettes.

## What is thin or may be wrong

- Wage orders drift. Several Philippine regions revised in the last 6 weeks (Western Visayas, SOCCSKSARGEN, CALABARZON, Central Visayas) and two take effect after the reference date.
- Thailand's domestic coverage rests on ILO summaries, not the gazette text of Regulation 15. The Thai wage list is a newspaper reproduction of the gazette.
- Taiwan's NT$20,000 rests on press (Taipei Times January 2026, Taiwan News August 2022). I did not find the MOL notice.
- Australia: the National Minimum Wage (AUD 26.44 per hour from 1 July 2026) was not verified; the Fair Work pages blocked plain fetches and the Wayback copy was not usable.
- The ILO page gives the Thai regulation date as "31 April 2024", which does not exist; other sources say 30 April.
- The owner may have two things wrong. Thailand's Ministerial Regulation No. 14 (2012) is the old regulation that excluded domestic workers from minimum wage; the 2024 one is No. 15. The Wage Committee's "No. 14" is an unrelated announcement with the same number. And in Taiwan, Japan, Korea and Malaysia the general minimum does not apply to directly hired household help, so using the general minimum for those countries overstates the legal floor.
- Vietnam and Thailand rows are the general regional or provincial rate that the law expressly extends to domestic workers. Merge with the general-minimum figures with care to avoid double counting.

## Not covered

Going rates (agency or direct-hire) were not in my slice. Singapore and Hong Kong foreign helper source-country wages beyond what is stated above were not researched.

---

# Slice notes: w-latam

Written by AI on 2026.11.17 by model claude sonnet 5.5

# w-latam: statutory domestic-worker minimums, Latin America and the Caribbean

Date of values: in force on 2026-11-17. 13 rows in `w-latam.curated.csv`, 16 sources in `w-latam.sources.csv`, saved pages in `cache/<source_id>/`.

## Rows written (type=statutory-domestic-min)

| Place | Figure | What it is |
|---|---|---|
| AR | 4,170.52 ARS per hour | Live-out ("con retiro") general household tasks, Nov 2026 scale. Hourly scale applies under 24 h a week for one employer, so it fits a 4 h/week cleaner. Monthly (24+ h) is 511,639.37. |
| UY | 169 UYU per hour; 32,051 per month | Grupo 21, category General, from 1 Jul 2026. Monthly assumes 44 h a week. |
| CR | 268,731.31 CRC per month | Decree 45303-MTSS, "Trabajo doméstico", full-time. No hourly rate in the decree. |
| PA | 350.00 USD (Region 1) and 320.00 USD (Region 2) per month | Decreto Ejecutivo 13/2025, from 16 Jan 2026. Fixed monthly, no hourly rate. Two rows share place code PA. |
| DO | 13,000 DOP per month | Resolución CNS-02-2025, from 1 May 2025. |
| MX | 342.47 MXN per day; MX-BCN 440.87 per day | CONASAMI professional minimum "Trabajador(a) del hogar" (row 56 of 61). Border zone rate used for MX-BCN. |
| BR-SP | 1,874.36 BRL per month | Lei 18.471/2026 names "trabalhadores domésticos". |
| BR-RS | 1,884.75 BRL per month | Lei RS 16.514/2026, Faixa 1 lists "empregados domésticos". |
| BR-PR | 2,181.63 BRL per month (9.92 per hour) | Resolução CETER 632/2026, Grupo II. Domestic workers are placed there only by CBO group. Doubt flagged in the row. |
| BR-SC | 1,842.00 BRL per month | **Unverified against the law**; newspaper report of the approved bill. |

## Trust and doubts, by row

- **BR-SC is the weakest.** The ALESC portal refused the connection and COAD returned 403. The only saved page is NSC Total's report written before the governor signed. Secondary sources say Lei Complementar 895 of 26 Mar 2026. NSC lists Faixa 2 as R$1,980 while others say R$1,908, so the report may be imperfect. Check LC 895/2026 before use.
- **BR-PR:** the resolution does not name domestic workers. It groups by CBO major group; domestic workers (CBO 5121) sit in group 5, which is Grupo II. Payroll sites say domestic workers get Grupo II. I found no Paraná government page that says so. Text read on third-party copies of the DOE (legisweb, diariofiscal, normaslegais).
- **BR-RS:** law text read on normaslegais.com.br (a copy of the DOE of 2026-05-21), not the Assembly's page. The state government's bill page (blocked to scripts, read through WebFetch) and Brasil de Fato agree on amount and on domestic workers in Faixa 1. Article 2 of the law says new values apply from publication; data-base 1 May. I used 2026-05-21 as the start; Brasil de Fato says retroactive to 1 May.
- **PA:** the MITRADEL PDF gives 403 to scripts, and the PDF is scanned images. The saved copy is the Wayback capture of the same URL. I read page 4 by eye (it matches the figures reported by Prensa, Softland and WageIndicator). EY's alert confirms Gaceta Oficial 30438 and the start date of 16 Jan 2026; it does not list the domestic rate.
- **DO:** scanned PDF, read by eye. I found no 2026 revision. Press reports a constitutionality action against the resolution; I did not check its status.
- **MX:** a real domestic-specific minimum exists. The professional minimum for "Trabajador(a) del hogar" is above the general minimum outside the border zone (342.47 against 315.04). CONASAMI says the minimum cannot be split by hour. Practical reading for a few hours a week: the daily figure per visit. The owner needs to decide how to turn a daily floor into an hourly figure. I did not.
- **AR:** two scales exist for Nov 2026. Annex 4 attached to Res 6/2026 had general-tasks con retiro 4,174.62; Res 7/2026 replaced Annex 4 and the figure is 4,170.52 (the replaced annex is in the cache as `res6-4.pdf`). El Litoral quotes the old one. Infobae and Los Andes swap the con/sin retiro labels; the ARCA Oct 2026 table settles the column order (Caseros, live-in only, sits in the "sin retiro" column). The official ARCA PDF for Nov 2026 was not yet online. December 2026 adds 1.6% (Los Andes reports 4,237.24 for general tasks con retiro; not recorded, not from an official page I saved). Provinces from La Pampa south and Patagones get +31%.
- **UY:** the MTSS page still shows the 30 Jun 2026 reference values for Cocina and Cuidados. The BPS July 2026 values are used. BPS rounds the hourly value to whole pesos.
- **CR:** MTSS's own "trabajo doméstico" page still shows 258,376.22, the 2025 figure. The 2026 figure comes from the decree list. A 2027 rise of about 1.70% is announced and is not in force. The hour figure 1,119.71 CRC (monthly / 30 / 8) is MTSS's reference rule and is not a published rate, so I did not record it.

## Countries with no domestic-specific floor (no row, by the brief)

- **Chile (puertas afuera and adentro):** casa particular pay is the general ingreso mínimo. Since 2011 (Ley 20.279) it equals 100% of the general minimum. DT: from 1 May 2026 the monthly minimum is $553.553 for ages 18-65 (Ley 21.830, Diario Oficial 22 Jun 2026; dictamen on the DT site), and it rises with CPI on 1 Jan 2027. Food and lodging cannot be deducted (art. 151 Código del Trabajo). The DT page that says casa particular pay "no puede ser inferior al ingreso mínimo legal" is saved. Part-time pay is proportional; DT's dictamen says "sin perjuicio de la proporcionalidad ... en jornadas parciales". Maximum full week for puertas afuera is 42 h from 26 Apr 2026 under Ley 21.561 (the DT casa-particular page still shows 44 and 2024 values: stale; the 42 h comes from the law's schedule as reported by secondary sites). If the owner wants Chile in the table, 553,553 CLP per month for a full week is the figure; hourly is derived, not published.
- **Peru:** Ley 31047 art. 6: pay "no podrá ser inferior a la remuneración mínima vital (RMV) por jornada completa de ocho (8) horas diarias o cuarenta y ocho (48) horas semanales"; by the hour it is proportional. The RMV itself is another agent's slice (there is a `dw-pe-sunat-rmv` cache folder from someone else). Press says the RMV rose from S/1,130 to S/1,230 on 1 Oct 2026 (DS 015-2026-TR); I did not verify that and did not use it.
- **Paraguay:** Ley 6338/2019 art. 10 puts domestic workers on the general minimum ("salario mínimo legal para actividades diversas no especificadas") and bars pro rata pay below it for shorter days. **The 60% rule raised in the task is out of date:** it came from Ley 5407/15 and Ley 6338 replaced it in 2019. (Press still repeats 60%.) Current general minimum: Última Hora and a blog report Gs 3,044,000 from 1 Jul 2026 (Decreto 6225/2026, Res. MTESS 670/2026). I did not verify it from the decree, and it is the other agent's slice.
- **Bolivia:** Ley 2450 art. 14: full-time pay "no inferior al mínimo nacional"; half-time is half the national minimum; for specific hours "el salario mínimo nacional, dividido por las horas trabajadas". Press says Bs 3,300 from Jan 2026 (DS 5516); not verified.
- **Ecuador:** the Acuerdo Ministerial MDT-2025-195 sets the SBU at USD 482 for 2026 and names "trabajadores remunerados del hogar" among the covered groups (saved copy, ~line 216). No separate domestic rate.
- **Brazil, outside the state floors above:** no federal domestic-specific minimum. Domestic workers get the national minimum (R$1,621 in 2026, Decreto 12.797/2025; saved Agência Gov report). Rio de Janeiro: press says the state floors (Lei 8.315/2019) are frozen below the national minimum, so the national minimum applies. I found no official RJ page and did not record it. Other states' floors (for example Minas Gerais) were not searched; only RS, SP, PR, SC and RJ were.
- **Colombia:** no separate floor; domestic work is paid at least the SMMLV, or pro rata by days. I saved no official source for this and found no MinTrabajo page. 2026 SMMLV was set at $1,750,905 by Decreto 1469 of 2025. The Consejo de Estado suspended that decree on 12 Feb 2026, confirmed the suspension in April, then reversed it in July 2026 (press; no later news found). The final ruling on the decree is still open. This is the other agent's slice and is unverified here.
- **Guatemala, Honduras:** I did not find whether domestic workers are inside the general minimum decree or outside it. A Guatemalan law blog says there is no lower domestic minimum (secondary, not recorded). Honduras's 2026-27 tripartite agreement (April 2026) was found only in press. No row.
- **Other countries not searched:** Venezuela, Cuba, Jamaica, Trinidad, Barbados, Bahamas, El Salvador, Nicaragua, Haiti and the smaller Caribbean states.

## Things the owner may have wrong

1. (Answer to the task's question) Mexico does have a domestic-specific professional minimum ("Trabajador(a) del hogar"), higher than the general minimum outside the border zone.
2. Paraguay's 60% rule is obsolete; domestic workers are at 100% of the general minimum since 2019.
3. Uruguay's Grupo 21 now has three categories from 1 Jul 2026 (General, Cocina, Cuidados). Use General for a cleaner.
4. In Argentina, "con retiro" means the worker goes home (live-out) and is the lower rate. "Sin retiro" (live-in) is higher.
5. Costa Rica and Panama publish monthly rates only; hourly figures there are contractual or derived.
6. Brazil's state floors depend on the state; the national minimum applies where no state floor names domestic work.
7. In Brazil, a state floor does not apply where federal law or a union agreement already sets a floor for the category (Lei RS 16.514 art. 4 says so).

## What I did not cover

City-level going rates. This was a minimum-wage slice only.

---

# Slice notes: w-mea

Written by AI on 2026.11.17 by model claude sonnet 5.5

# w-mea: statutory domestic-worker minimum wages, Middle East, Africa, Caucasus and Central Asia

Figures are in force on 2026-11-17 unless the row says otherwise. Raw pages are in `cache/<source_id>/`.

## What is in the CSV (30 rows)

Reliability: **read** = I read the legal text or a government page. **secondary** = a reputable report that quotes the text, not read myself. **unverified** = news only, the instrument not found.

| Place | Figure | Basis |
|---|---|---|
| South Africa (ZA) | R30.23/hour from 2026-03-01; R28.79 from 2025-03-01 | read (2026 gazette); 2025 from the Department's 2026 statement |
| Morocco (MA) | 60% of SMIG = 10.752 MAD/h (2026), 10.26 (2025) | derived; secondary (official law and decree not reachable) |
| Kenya (Nairobi, Mombasa, Kisumu) | KES 18,047.40/month, 161.34/hour from 2026-05-01 | read (Gazette text via Grant Thornton PDF) |
| Namibia (NA) | N$15/h in 2026, N$12 in 2025, N$18 from 2027 | read (gazette 8409) |
| Zambia (ZM) | K5.29/h or K1,100/month from 2024-01-01 | read (SI 49 of 2023) |
| Tanzania (TZ) | live-out TZS 821/h, 160,000/month; other 410/h, 80,000/month, from 2026-01-01 | read (GN 605A) + Clyde & Co |
| Qatar (QA) | QAR 1,000/month basic; 1,800 if no food or housing, since 2021-03-20 | secondary (ILO page; Ministry PDFs unreachable) |
| Kuwait (KW) | KWD 75/month | secondary (ILO factsheet) |
| Tunisia (TN) | 2.667 TND/h, 554.736/month (48-hour week) | law read; SMIG from secondary |
| Malawi (MW) | K83,720/month from 2026-06-01 | unverified (two news reports) |
| Zimbabwe (ZW) | US$90/month gardeners; US$99 cooks and housekeepers, from 2026-06-16 | unverified (Cabinet announcement in news) |
| Botswana (BW) | P1,500/month from 2024-02-01 | unverified against the S.I.; Botswana government news item |
| Liberia (LR) | US$3.50/day | old (2015 Act, via ILO), unverified |
| Armenia (AM) | survey: 1,000 AMD/h most common, 1,200 average (workers), 1,500 average (employers) | CRRC-Armenia interviews, not representative |

## Doubts the owner should know about

1. **Most of these floors are not a part-time cleaner's rate.** Qatar, Kuwait, Zimbabwe, Malawi, Botswana, Zambia (monthly) and the Tanzania low band are monthly full-time floors, mostly for live-in staff. Only the `per_hour` rows (ZA, NA, ZM, TZ live-out, KE, MA, TN) can be used as an hourly price for a 4 hour a week job. Monthly figures divided by a month's hours give a different, usually lower, price.
2. **South Africa:** "Sectoral Determination 7 abolished" is not quite right. SD7 (2002) still governs domestic workers' conditions (for example the 10% cap on deducting for accommodation, per Fasken); only its wage schedule was replaced. The NMW is the same R30.23 for domestic workers since 2022-03-01. A worker must be paid at least 4 hours on any day worked (DEL flyer), so a 3 hour visit still costs R120.92 at minimum. Morocco is **60%** of the SMIG, not 50%.
3. **Morocco:** I could not open adala.justice.gov.ma, sgg.gov.ma or the decree. Article 19's wording (60% of the legal minimum for industry, commerce and the liberal professions; food and lodging do not count) is in a search excerpt of the official PDF and in two secondary sites. The SMIG itself (17.92 MAD/h from 2026-01-01, decree 2.25.983, BO 7469 of 2025-12-29) comes from Upsilon, AvocatLib and Le360. The 10.752 figure is my arithmetic.
4. **Kenya:** the Gazette hourly rate (161.34) is higher than the monthly rate divided by working hours, so it behaves as a casual rate. A live-out monthly worker also gets a 15% housing allowance on top (Nairobi about KES 20,754.51), per secondary sources. Legal Notice 95 (29 May 2026) is the text I read. A secondary source says Legal Notice 108 (26 June 2026) replaced it and moved the "all other areas" monthly rate from 9,268.07 to 9,628.07, leaving the five-city rates unchanged. Kenya Law returns an empty bot-check page to curl, so I could not read LN 108. Cities rows are the first zone (Nairobi, Mombasa, Kisumu, Nakuru, Eldoret); former municipalities (Mavoko, Ruiru, Limuru) get 16,650.95/month, 147.45/h, and all other areas the lower rate.
5. **Kuwait:** KD 75 (ILO factsheet and the PAM-hosted law text). Some guides still print KD 60 (the 2015 original). The PAM PDF is a scanned image, so I did not read article 27 myself.
6. **Qatar:** the QAR 1,000 applies to household workers by law (Law 17/2020), but a live-out cleaner without food or housing is owed at least 1,800 in total. QatarSteps says no revision as of Oct 2026.
7. **Tunisia:** the 2021 domestic work law (art. 11) ties the domestic wage to the SMIG; there is no separate domestic scale. SMIG steps up to 582.400 DT (2.800/h) in 2027.
8. **Zimbabwe, Malawi, Botswana:** news-sourced only. Zimbabwe's rate is quoted in USD but one report says payment is in ZiG at the interbank rate. Treat these as unverified until the S.I. or Government Notice is found.
9. **Armenia survey rows:** qualitative, snowball sample (60 worker and 40 employer interviews). Fieldwork year is inferred as 2024. The report says the Labour Code does not cover domestic workers.

## Countries with no domestic-specific floor (no row)

- **Saudi Arabia:** "Not specified by law" for domestic workers (ILO FAIRWAY factsheet, `dw-sa-ilo-fairway`). Pay is the contract wage (Musaned); Musaned wage tables by nationality I saw are recruitment or embassy practice, not law. Salary must be paid through official channels from 2026-01-01.
- **UAE:** Federal Decree-Law 9 of 2022 sets no minimum wage (Migrant-Rights.org, `dw-ae-migrantrights`; I could not open MOHRE or uaelegislation.gov.ae). Wage is the contract wage.
- **Bahrain:** "There is no minimum wage for domestic workers in Bahrain" (LMRA Workers' Handbook, Feb 2026, `dw-bh-lmra-handbook`). A BHD 120 ceiling on domestic salaries was proposed in 2023; I found no sign it became law.
- **Oman:** no minimum wage for expatriate domestic workers; the OMR 325 national minimum is for Omani citizens. Ministerial Decision 574/2025 (October 2025) sets hours and leave but no wage. Source is a private guide (`dw-om-sanad-guide`); I could not read the decision from an official host, so this is flagged secondary.
- **Jordan:** the JOD 290 minimum (2025 to 2027) excludes non-Jordanian domestic workers and their cooks and gardeners (Social Security Corporation statement, via Asiaref; `dw-jo-asiaref`). Jordanian domestic workers are covered by the JOD 290. An older tripartite figure of JOD 110 a month for domestic workers is reported (Tamkeen, `dw-jo-tamkeen`); no current domestic figure found. Not a row because it applies to live-in migrants and is out of date.
- **Lebanon:** the Labour Code (art. 7) excludes domestic workers; the LBP 28,000,000 minimum (decree 699, from 2025-08-01) does not apply. Only the standard contract regime for migrants applies.
- **Egypt:** the new Labour Law 14 of 2025 does not cover domestic workers (Ops360; ILO Africa report says the same for Egypt and Libya). A separate bill was proposed in 2021.
- **Algeria:** single national SNMG, DZD 24,000/month (138.46/h) from 2026-01-01 (decree 26-01), no occupational variants. No domestic-specific floor found.
- **Israel:** general minimum wage only, NIS 6,443.85/month, NIS 35.4/h (182-hour base) from April 2026 (Histadrut). I found no domestic cleaning scale for private households; the Histadrut note's "cleaning" sector premium relates to contract cleaning firms, not households. Not a row.
- **Nigeria:** the National Minimum Wage Act excludes part-time workers and firms under 25 employees, so domestic workers are most likely excluded (ILO Africa report, box 4).
- **Ghana, Uganda, Ethiopia:** no domestic-specific rate found. Ghana has a daily NMW (reported GHS 21.77 for 2026, one news report, not saved). The ILO report says Uganda has never adjusted its minimum wage and Ethiopia has no minimum wage system.
- **Mauritius:** one search says domestic workers fall under the general National Minimum Wage (Rs 17,745 a month from 2026-01-01), another claims domestic-specific regulations exist; I could not settle it. No row.
- **Georgia, Azerbaijan, Uzbekistan, Kazakhstan:** I found no source that states the position either way. Armenia and Georgia studies say domestic work is poorly regulated and the Labour Code is not designed for it. No rows. These are not statements that no floor exists, only that I could not find one.

## Leads I could not record (WageIndicator hides figures behind a sign-up)

WageIndicator has domestic pages for **Eswatini** (Regulation of Wages (Domestic Employees) Order 2022; reportedly from 2024-12-06 SZL 1,453.21/month house attendant or laundress, 1,488.37 cook, 1,717.35 caregiver or driver), **Lesotho** (reportedly LSL 962/month from 2025-03-28; another site says LSL 800 from 2026-04-01, unclear) and **Senegal** (domestic workers and housekeepers). The figures in brackets are from search-result snippets only. I did not sign up, so there is no saved page to quote and they are not in the CSV. A later pass could find the gazettes.

## Not covered or thin

- No Mozambique, Rwanda, Seychelles, Cameroon, Angola, Ethiopia, Sudan or Libya checks beyond the ILO lines.
- The ILO Africa report (Dec 2024) says 23 African countries give domestic workers a minimum wage at the same or a lower rate; I recorded only those where I could read a figure.
- Hosts that time out from this network (Moroccan, Qatari and UAE government sites) were tried directly and through the Wayback Machine (404). The Parallel search tool hit its free-tier rate limit partway through, so some pages came from WebSearch snippets.
- No city going-rate rows (agency or direct-hire) for Dubai, Muscat, Tbilisi, Marrakesh or Cape Town: the task was statutory minimums, and I did not search for them.

## Sources quality

ILO, government gazettes (South Africa, Namibia, Zambia, Tanzania, Kenya via a reproduction), the LMRA Bahrain handbook and the JORT law text are the strongest. Upsilon, SmartPaie, Afriref, AvocatLib, Asiaref, Ops360, Sanad, Migrant-Rights.org, QatarSteps and the news items are secondary and flagged where used.

---
