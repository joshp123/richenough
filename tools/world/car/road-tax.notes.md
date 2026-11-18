# Annual road tax for the reference car, outside the US and Europe

Written by AI on 2026.11.18 by model claude sonnet 5.5, for the Rich enough project. Nothing is committed. Files: `road-tax.curated.csv` (25 rows), `road-tax.sources.csv` (56 sources), `road_tax.py` (the arithmetic; it also checks that every `quote` appears on the saved page), pages in `cache/road-tax-*/`.

## What the figure is

`amount` is the yearly tax or fee a private owner of the reference car pays to keep it on the road, averaged over 8 years, in local currency, `per_year`. It adds annual circulation, ownership or registration-renewal taxes, mandatory yearly licence fees, and the fee for a compulsory roadworthiness test (averaged over the years it falls due). It leaves out compulsory third-party insurance, one-off purchase and registration taxes (they are in the car's price), tolls, and dealer service charges. Each row's `note` gives the rule and the arithmetic.

Value-based taxes (Brazil, Chile, Colombia, Costa Rica, Georgia, Indonesia, Peru, Uruguay) use the car module's own price in local currency (`tools/world/car.py`) and its depreciation: a straight line to 50% at year 8, so the base at the start of year k is price x (1 - 0.0625 (k-1)). That is an assumption, not the tax authority's table: it keeps this figure consistent with the depreciation line, but real tax values usually fall faster in years 1 to 3, so these figures are ceilings.

## Results (US dollars use the car module's exchange rate)

| Place | Per year | USD per year | Measured for |
|---|---|---|---|
| TH | 1,964.73 THB | 59 | Thailand, whole country (private car up to 7 seats, taxed on engine cc) |
| MY | 279.20 MYR | 69 | Peninsular Malaysia, private saloon owned by an individual (Sabah and Sarawak pay less) |
| SG | 1,000.91 SGD | 782 | Singapore, whole country (private car, 1,798 cc petrol hybrid) |
| JP | 44,288.00 JPY | 278 | Japan, whole country (private white-plate car, 1.5-2.0 L, 1.0-1.5 t) |
| TW | 11,920.00 TWD | 374 | Taiwan, whole country (private small passenger car, 1,201-1,800 cc petrol) |
| HK | 7,644.25 HKD | 975 | Hong Kong, whole territory (private car, 1,500-2,500 cc petrol) |
| VN | 1,578,750.00 VND | 61 | Vietnam, whole country (private car up to 8 seats; same in Ho Chi Minh City and Da Nang) |
| ID | 7,093,401.00 IDR | 397 | Jakarta (DKI Jakarta provincial rate: first car 2%, no opsen; other provinces about 1.1% + 66% opsen) |
| KR | 406,123.00 KRW | 286 | South Korea, whole country (private passenger car, over 1,600 cc) |
| AE | 476.25 AED | 130 | Dubai (RTA; Abu Dhabi charges 350 + a 150 test) |
| OM | 23.00 OMR | 60 | Oman, whole country (private car under 3 tonnes, 1,500 to below 3,000 cc) |
| GE | 648.66 GEL | 247 | Georgia, Tbilisi rate (0.8% of market value); applies only if the couple's family income is over 100,000 GEL a year |
| MA | 185.00 MAD | 19 | Morocco, whole country (petrol-electric hybrid, 8-10 fiscal hp) |
| ZA | 762.00 ZAR | 47 | Cape Town (Western Cape tariff from 1 July 2026; Gauteng charges R732 + 72 for the same tare band) |
| MX | 760.00 MXN | 44 | Mexico City (Ciudad de México plates) |
| CR | 359,117.00 CRC | 797 | Costa Rica, whole country (property-tax part of the marchamo; the same everywhere) |
| PE | 468.37 PEN | 139 | Lima (SAT Lima; the same national rate applies in every province) |
| CO | 4,240,740.00 COP | 1,275 | Medellín (Antioquia: the national rates apply; the department keeps 80%, the municipality 20%) |
| BR-SP | 6,307.66 BRL | 1,228 | São Paulo state (IPVA 4%; licensing fee 174.08 BRL) |
| BR-SC | 3,066.79 BRL | 597 | Santa Catarina state (IPVA 2%; Florianópolis); licensing fee not included |
| CL | 570,243.00 CLP | 612 | Chile, whole country scale (permiso de circulación paid to Santiago's commune; communes keep it, rate is national) |
| UY | 37,367.00 UYU | 929 | Uruguay, whole country (SUCIVE collects the same patente for every department; Montevideo) |
| PA | 28.00 PAB | 28 | Panama City (Alcaldía de Panamá annual circulation tax) |
| CA-ON | 0.00 CAD | 0 | Ontario (passenger vehicles; the plate sticker fee was abolished in 2022) |
| AU-NSW | 475.00 AUD | 335 | New South Wales (excluding the CTP green slip) |

## Sourced zeros and near zeros

- Ontario: 0. Plate renewal fees for passenger cars ended in 2022 (ontario.ca). Other provinces were not checked.
- Morocco: the vignette is 0 for a hybrid under article 260-15 of the tax code; the 185 MAD is the compulsory inspection. The payment site mavignette.ma still shows hybrids at the petrol rate; if that is enforced, add 650 MAD (8-10 cv) or 350 MAD (under 8 cv).
- Mexico City: the tenencia is 0 for a hybrid; the 760 MXN is the refrendo (news reports; thin).
- Vietnam has no annual vehicle tax on cars; the figure is the road-use fee plus inspection.
- India: not written. Secondary sources say private-car road tax is paid once at registration (15 years or lifetime, by state), which would make the annual figure 0, but they conflict and no official page was read.

## What is thin

- Costa Rica: base is the car module's price, but the law taxes a new car at its customs value (lower), so year 1 is too high; the roadworthiness test (RTV) was left out because the operator changed in 2026 and no tariff was found; small marchamo lines (timbres and the like) are missing.
- Indonesia: the Pergub table that depreciates the tax base was not found; the sedan coefficient 1.025 is from a news report of the Pergub. Jakarta's 2% has no opsen; other provinces are about 1.1% plus a 66% opsen, so the national figure differs.
- Indonesia's Palombo city is Bali (Denpasar), not Jakarta: Bali's provincial PKB rate was not read, so ID carries Jakarta's.
- Brazil: no Brazilian country row, only SP (4%, licensing fee 174.08) and SC (2%, licensing fee not found, about 100 BRL). Florianópolis is in SC.
- Panama: one undated press line (28 PAB); the yearly revisado and sticker fees were not found, so the true figure is higher.
- Georgia: counts only if the couple's family income exceeds 100,000 GEL (about US$38,000, from 30 September 2026); I assumed it does. Without it the figure is 22.50 GEL (inspections only). Whether foreign-source withdrawals count as income was not checked.
- Mexico, Morocco, Hong Kong, Vietnam, UAE, Thailand: the fee behind one part of the figure (inspection or refrendo) is from a secondary page or a search-tool summary, said in the note. Thailand's and Costa Rica's cache folders hold a text file from a search tool in place of a page curl could not fetch.
- Korea: standard rule from a blog; the periodic inspection is not included. Taiwan: the periodic inspection is not included (fee not found).
- Japan: the one-off 75% green cut on the year-2 automobile tax (27,000 yen, which would lower the 8-year average by 3,375 yen) was not applied because eligibility for this trim was not checked.

## Not found (no row)

- Argentina (Buenos Aires city): the CABA patente scale (fixed amount plus a rate per valuation band) could not be read: AGIP's and the law's PDFs were unreachable or returned excerpts without the table. Reports give effective rates of 1.6% up to ARS 7.46m, 2.5% to 17.2m, 3.2% to 26.9m and 3.7% to 36.6m, and nothing for the Corolla's band. The city's VTV is 96,968 ARS (63,454 on the older page), first at 4 years (5 under law 6963 of July 2026), then every 2 years (cache `road-tax-ar-caba-vtv`).
- Philippines: sources disagree on whether the motor vehicle user's charge is by engine (6,000 PHP for 1,601-2,000 cc) or by weight (3,600 PHP for 1,601-2,300 kg); no official table.
- Israel: 2026 licence fee groups by new-car price (group 1: 1,266 ILS for models 2024-2026) came from a search summary only; the Corolla's group and the test fee were not found.
- Saudi Arabia: registration renewal about 100 SAR, plus an inspection (Fahas) of 115 SAR after 3 years, plus a fuel-efficiency fee whose amount was not found. Qatar: 100 to 250 QAR in different guides. No official page for either.
- Kazakhstan: 2026 MRP is 4,325 KZT; the rate for 1,501-2,000 cc was not on the page read. Russia: Moscow's law gives rates per horsepower; the 2026 column could not be read. Egypt, Kenya, Nigeria: not searched.
- China: national range 360-660 CNY a year for 1.6-2.0 L cars, set by each province; Beijing 480 and Shanghai 450 appear only in 2012 and 2016 secondary pages. New Zealand: licensing 172.97-181.45 NZD for 12 months of petrol (NZTA page returned 403; figure from a secondary page) and the WOF fee was not found. Australia: only NSW; Victoria's is about 900 AUD with its TAC levy.

## Things you may want to change

- The brief names Mexico's tenencia, but a hybrid is exempt in Mexico City, so the modelled Corolla Hybrid pays almost nothing there. A non-hybrid Corolla would pay the tenencia above the 638,000 MXN invoice cap.
- Singapore's 1,001 SGD sits on top of a COE-inflated price, so the car there is dominated by depreciation, not tax.
- Where a figure assumes the straight-line base, a visitor who compares it with an authority's own calculator will see a lower number in the first years. The model could take real value tables later.
