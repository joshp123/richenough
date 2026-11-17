# Rent of a two-bed flat: Latin America and the Caribbean

Written by AI on 2026.11.17 by model claude sonnet 5.5, as a research helper for the agent that owns the world cost data. Figures were retrieved on 2026-11-17.

## What is here

| File | What it does |
| --- | --- |
| `latin-america-fipezap.py` | Brazil: FipeZAP rent per m2 for 36 cities, 22 state rows and a Brazil row. Reads the free workbook. |
| `latin-america-aguila.py` | Chile: median two-bed asking rent per comuna from Aguila's open CSV (country, Providencia for Santiago, and the main town of nine regions). |
| `latin-america-listings.py` | Median asking rent of two-bed flats sampled from Fincaraiz (Colombia) and InfoCasas (Uruguay, Paraguay, Bolivia). `--crosschecks` prints two rows for the notes only. |
| `latin-america-encuentra24-archive.py` | Costa Rica and Panama, from archived Encuentra24 pages. Very thin. |
| `latin-america.curated.csv` | 19 rows typed from reports: Peru, Argentina, Mexico, Medellin, Montevideo, Ecuador. Each has a URL and the quote. |
| `latin-america.sources.csv` | The sources behind the curated rows. The scripts carry their own `SOURCES`. |

Raw files are in `cache/` under `fipezap`, `bcrp-pe-alquiler`, `caba-alquileres`, `inmuebles24-index`, `navent-index`, `aguila-cl`, `cambio-uruguay`, `ine-uy-alquileres`, `plusvalia-index`, `latin-america-listings`, `encuentra24-archive`, `livingcost-latam` and `latin-america-pages`.

## Rules I used

- Amount is the published figure in the published currency. Rent per m2 is multiplied by 75 m2 and the note says so (Brazil, Peru, Medellin).
- Where a source gives a median two-bed rent, I used that and put the median flat size in the note. Many of these medians describe flats of 55 to 65 m2, smaller than your 70 to 85 m2. Scaling up pro rata overstates, because small flats cost more per m2. I did not rescale.
- Room conventions. Argentina counts the living room, so a 3-ambientes flat (living room plus two bedrooms) is the two-bed. Chile, Colombia, Uruguay, Paraguay, Bolivia, Mexico and Peru count bedrooms (dormitorios, habitaciones, recamaras). Brazil's FipeZAP gives no split by bedrooms for rents, so its figure covers flats of all sizes.
- A city row is the central or most sought-after district where the source has districts (Providencia, Cuauhtemoc, Palermo, Miraflores, El Poblado, Pocitos). The region row beside it is the whole area. The country row is the capital's figure where no national series exists. Every proxy says so in `measured_for`.
- Everything is an asking rent from listings, except Uruguay's INE contracts (a cross-check only). None is a signed lease.

## Coverage by country

Rows with a source I would stand behind, labelled where thin:

- Brazil (BR, 22 states, 36 cities): FipeZAP, October 2026. National index R$ 55.04 per m2, so R$ 4,128 at 75 m2. Sao Paulo R$ 4,962, Rio R$ 4,643, Florianopolis R$ 4,664.
- Peru (PE, PE-LMA, Lima): BCRP, Q2 2026, US dollars.
- Argentina (AR, AR-C, Buenos Aires): IDECBA, Q3 2026, pesos.
- Mexico (MX, MX-CMX, MX-JAL, MX-NLE, Mexico City, Guadalajara, Monterrey): Inmuebles24 index, October 2026.
- Chile (CL, Santiago, nine regional towns): Aguila, October 2026. Small portal (78 two-beds in Providencia), labelled so.
- Colombia (CO, CO-ANT, CO-DC, CO-VAC, CO-ATL, Bogota, Cali, Barranquilla, Medellin): Medellin's El Poblado from the city's property observatory; the rest are listing samples of 120 to 220 flats each. Thin.
- Uruguay (UY, UY-MO, Montevideo): Cambio Uruguay live medians over 9,645 ads. Thin because it is one day of one aggregator.
- Ecuador (EC, Quito): Plusvalia index, but July 2025, so stale.
- Paraguay (PY, PY-ASU, Asuncion): 48-flat sample. Thin.
- Bolivia (BO, BO-L, BO-S, La Paz, Santa Cruz): 79 and 193 flats. Thin.

- Costa Rica (CR, CR-SJ, San Jose) and Panama (PA, PA-8, Panama City): VERY THIN. Pooled asking rents of 15 and 9 two-bed flats, read from Internet Archive copies of Encuentra24's search pages (April and July 2026 for Costa Rica, April 2026 for Panama), because Encuentra24 blocks scripts. US$ 1,300 and US$ 1,100. The Costa Rican ads split into colones (8 flats, median CRC 425,000, about US$ 950) and dollars (7 flats, median US$ 1,900, the expatriate segment), so the pooled median sits between two different markets.

No row, tried and rejected: Guatemala, El Salvador, Honduras, Nicaragua and the Dominican Republic. The same archive method found fewer than 8 two-bed flats (4, 4, 7 and none readable) or, for Managua, 12 flats whose few stated areas had a median of 150 m2. Indicative live Encuentra24 asking rents seen through a search tool in Aug 2026, not saved: Guatemala City zones 10 and 14 US$ 875 to 2,015 (55 to 98 m2); San Salvador, Escalon US$ 1,150 to 2,290, typically 1,300 to 1,500; Tegucigalpa HNL 14,000 to 17,500 or US$ 725 to 1,000; Managua US$ 600 to 1,000 unfurnished; Santo Domingo (Piantini, Naco) US$ 990 to 2,200.

No row, with the reason:

- Venezuela, Cuba, Haiti: no free series, no portal that answers a script. Venezuelan rents are quoted in dollars in a split market (press reports of US$ 300 to 1,000 in Caracas, 2024). Not enough to put a number on a public map.
- Belize, Guyana, Suriname: only single agency listings. Belize City two-bed asking US$ 750 to 1,900 (belizerealestate.bz listings); Georgetown US$ 1,673 to 3,500 (Century 21, 2025 to 2026). Not saved, not a sample.
- Jamaica, Trinidad and Tobago, The Bahamas, Barbados, Saint Lucia, Antigua, Grenada, Saint Kitts, Saint Vincent, Dominica: no free survey and no listing portal that a script can read. Indicative asking ranges from agent listings and expat guides, not verified and not saved: Kingston (New Kingston) US$ 1,500 to 2,200 or J$ 125,000 to 208,000; Port of Spain TT$ 6,000 to 10,000 (ExpatFocus, 2025); Nassau US$ 1,600 to 2,500; Barbados US$ 2,200 to 3,000, south coast; Saint Lucia US$ 1,288 to 1,840 (Terra Caribbean). I found nothing at all for Saint Vincent and Dominica.
- Territories (Puerto Rico, Aruba, Curacao, Cayman and so on) were not covered. Puerto Rico belongs to the US data.

## The nine Palombo cities

"Table" is the figure in the rows. US dollar values use the 17 Nov 2026 open exchange rate. Livingcost is a cross-check only: its figures are for a 40 m2 one-bed in the centre and an 80 m2 three-bed in the centre, so a two-bed should sit between them.

| City | Table figure | Second figure | Livingcost 1-bed / 3-bed (US$) | Why they differ |
| --- | --- | --- | --- | --- |
| Mexico City | Cuauhtemoc MXN 29,722 (US$ 1,602); whole index MXN 22,019 (US$ 1,187) | Propiedades.com colonia ranges via Expat360, Aug 2026: Roma Norte 23,000 to 34,000, Condesa 26,000 to 40,000, Polanco 33,000 to 52,000 | 1,061 / 1,959 | Inmuebles24 is a 65 m2 flat; at 75 m2 add about 15%. The city housing secretariat's MXN 17,267 average (La Jornada, 8 Nov; page not saved) covers all housing and reads low. |
| San Jose (Costa Rica) | US$ 1,300, pooled median of 15 archived Encuentra24 flats (very thin) | Live Encuentra24 ads seen through a search tool, Jul to Aug 2026 (not saved): Escazu US$ 1,100 to 2,700, Rohrmoser US$ 1,250 (85 m2), Barrio Escalante US$ 1,400 (65 m2, furnished) | 821 / 1,456 | The sample mixes colones-priced ads (about US$ 950) with dollar-priced ones (US$ 1,900); neither alone is "the" rent. Livingcost sits between them. |
| Panama City | US$ 1,100, median of 9 archived Encuentra24 flats, April 2026 (very thin) | Live Encuentra24 ads seen through a search tool, Aug 2026 (not saved): El Cangrejo US$ 1,300 (93 m2), El Carmen US$ 1,250 (90 m2), Edison Park US$ 1,100 (80 m2), San Francisco US$ 1,050 (56 m2), Balboa US$ 2,200 (114 m2), Costa del Este US$ 2,400 (96 m2) | 1,068 / 1,913 | The archived page is April and leans to the cheaper inner districts; Costa del Este and Punta Pacifica ask twice as much. Livingcost is higher than the table figure. |
| Medellin | El Poblado COP 4,035,900 (US$ 1,217) | Fincaraiz, El Poblado search: COP 4,800,000 on 200 flats (US$ 1,448); whole city COP 3,500,000 on 206 flats (US$ 1,056) | 689 / 1,244 | The portal's "El Poblado" search also catches neighbouring areas and its median flat is 83 m2, against the observatory's 75 m2 rule. The observatory sample is not an official index. |
| Lima | Miraflores US$ 956 | Ubicasa, 13 Nov 2026: S/ 41 per m2 on 619 Miraflores listings, so S/ 3,075 at 75 m2 (US$ 902) | 660 / 1,102 | Close. The BCRP derives rent from sale prices and a price-to-rent ratio, so it is a modelled asking rent. Urbania's Lima-wide two-bed median is S/ 2,281 (US$ 669). |
| Florianopolis | R$ 4,664 (US$ 816) | FipeZAP's own neighbourhood rents, Oct 2026: Agronomica R$ 69.3, Centro R$ 65.9, Trindade R$ 61.8, Itacorubi R$ 59.2 per m2, so R$ 4,400 to 5,200 at 75 m2. QuintoAndar's page average is R$ 3,200 for all property types and R$ 2,135 for one-beds | 558 / 997 | One source is the real measure here (the FipeZAP index is Brazil's standard). I tried a QuintoAndar listing sample but only 2 flats fitted the filter, so I dropped it. |
| Santiago | Providencia CLP 983,000 (US$ 987) | Propertia, 18 Oct 2026: Providencia CLP 950,000 (9 ads); Las Condes CLP 1,319,000 (12 ads). Aguila: Las Condes 1,350,000 | 612 / 1,129 | Aguila and Propertia agree. Santiago comuna itself (the old centre) is CLP 445,000, which is why the city figure depends so much on which comuna you call "the centre". |
| Buenos Aires | Palermo ARS 1,448,060 (US$ 934); whole city ARS 1,248,298 (US$ 805) | Zonaprop Index, Oct 2026: 3 ambientes of 70 m2, ARS 1,230,282 (US$ 794) | 583 / 1,068 | Two portals, two months, within 1.5% for the whole city. Pesos only: dollar-priced ads are excluded and rents rise about 30% a year, so the quarter matters. |
| Montevideo | Pocitos UYU 39,500 (US$ 973); whole department UYU 33,000 (US$ 813) | InfoCasas sample: UYU 36,000 on 160 flats (US$ 886). Gallito, Aug 2026: UYU 40,065 (via TheLatinvestor) | 674 / 1,100 | The median flat is 60 m2. INE's registered new apartment contracts averaged UYU 24,188 in September 2026, but that mixes all flat sizes and covers about 55% of leases, so it reads lower. |

## What each source really measures

- **FipeZAP (Brazil).** Fipe, the University of Sao Paulo's economic research institute, with the OLX Group portals. It is the average advertised rent per m2 of ready apartments, a three-month moving average, for 36 cities. Not leases, and no split by bedroom for rents in the free file (the workbook has one for sales only). Small flats cost more per m2, so 75 m2 may overstate a little.
- **BCRP (Peru).** The central bank has tracked flat prices since 1998 from Urbania listings. "Rent per m2" is derived: median sale price per district divided by a price-to-annual-rent ratio built from rents asked in nearby areas. Twelve central and middle-income districts only. The BCRP site blocks scripts, so the table in `cache/bcrp-pe-alquiler/` is a transcription from a reader service. The PDF and the "Datos desagregados - Alquiler" workbook are linked from the BCRP page named in the sources file; someone with a normal browser could fetch the workbook and replace my transcription.
- **IDECBA (Buenos Aires).** The city statistics office, Argenprop ads in pesos, used flats, provisional, per barrio and per ambientes. The unit price is price per m2 times 70 m2. The city's open-data portal lists a related monthly series (used and new flats together, from 2010, CC BY), but the portal blocks scripts, so the quarterly PDF is the cached source.
- **Inmuebles24 Index (Mexico).** All the portal's own ads for a 2-bed flat of 65 m2, averaged by borough and colonia, monthly. The Mexico City index includes State of Mexico municipalities next to the city.
- **Aguila (Chile).** A small portal; 7,013 de-duplicated flat ads nationwide. The medians are neat and the CSV is open, but the sample per comuna is small (78 two-beds in Providencia). The leading portals (Portal Inmobiliario, TocToc) publish no free table; the 2024 TocToc figures that the Assetplan blog quotes are old.
- **OIME (Medellin).** The city's property observatory, through a press story. 8,066 rentals in El Poblado since 2014. The article says it is a sample and not an official index.
- **Cambio Uruguay.** An aggregator that de-duplicates ads across portals and shows live medians without building fees. The number moves every day.
- **Listing samples (Colombia, Paraguay, Bolivia).** The first 12 result pages of a search, apartments with 2 bedrooms and 50 to 110 m2, advertised rent without building fees. Default order, so not random. They sit inside the range other sources give (for example Medellin's El Poblado). Paraguay and Uruguay list in two currencies. Paraguay's row is the 48 flats priced in guarani (median PYG 6,250,000, about US$ 1,007); 33 dollar-priced flats had a median of US$ 1,300. InfoCasas Montevideo had 160 flats in pesos (UYU 36,000) and 49 in dollars (median US$ 1,800).

## What is thin or missing

- Costa Rica and Panama have no published series. `latin-america-encuentra24-archive.py` is the only route I found that gives a number, and it reads old copies of Encuentra24's search pages from the Internet Archive because the site blocks scripts. The first ads on each page are paid highlights, so it leans expensive. The Archive holds only one or two 2026 copies of each page.
- Colombia has no free national rent table. DANE does not publish asking rents, and I found no free market report from Fincaraiz or Metrocuadrado.
- Every figure except the Uruguayan INE cross-check is an asking rent. Signed leases are probably lower; none of these sources says by how much.
- Ecuador: no 2026 edition of Plusvalia's index turned up at the portal's usual address; the July 2025 file is the newest I could open. Guayaquil has no file at all.
- Not tried: Brazil's QuintoAndar and Loft rent indices (the portals block scripts), Colombia's Metrocuadrado API, Argentina's Cordoba and Rosario, Mexico's INEGI household survey rent, Peru's Arequipa and Cusco.

## Things you may have wrong, or should decide

1. Country rows for Peru, Argentina, Mexico, Uruguay, Paraguay, Ecuador, Colombia and Bolivia are capital or big-city proxies. They overstate the national picture. If the site falls back from region to country, small towns in these countries will look dearer than they are. You may prefer no country row for them.
2. Median two-bed flats in Chile (55 m2), Uruguay (60 m2) and Colombia (60 to 75 m2) are smaller than your 70 to 85 m2. Brazil's 75 m2 rule is the opposite problem: flats of all sizes at a per-m2 rate. Choose one policy; I left each figure as published.
3. Argentine rents rise about 30% a year (IDECBA: +32.9% for 3 ambientes, Q3 on Q3). The figure is the Q3 2026 average, six weeks old; decide whether the page should say so.
4. Panama City and San Jose rest on a small archived sample, not a measure. If those two matter for the headline, someone with a normal browser should read Encuentra24's current pages. The Livingcost interpolation (about US$ 1,490 for Panama and US$ 1,140 for San Jose) is a sanity check, not a better number.
