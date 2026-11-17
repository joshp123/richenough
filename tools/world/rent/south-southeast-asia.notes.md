# Two-bed rent, South and South-East Asia: notes

Written by AI on 2026.11.17 by model claude sonnet 5.5 (research helper for the world-data agent). Table columns as in `.agent/plan.md`.

## What is here

- `south-southeast-asia.py`: downloads and parses four listing portals into rows (George Town, Da Nang, Colombo, Phnom Penh), with country rows for Sri Lanka and Cambodia. Run `python3 -I tools/world/rent/south-southeast-asia.py`. Stdlib only. Its `SOURCES` list holds those four sources.
- `south-southeast-asia.curated.csv`: 26 rows read off reports and portal pages (`url` and `quote` per row).
- `south-southeast-asia.sources.csv`: 12 sources behind the curated rows plus 12 cross-check-only sources.
- `south-southeast-asia.crosschecks.csv`: 42 second figures for the eight Palombo cities, Jakarta, Makati, Mumbai and Phnom Penh. **Not for the table.**
- Saved pages are in `cache/<source_id>/` (ids in the sources file). Hipflat blocks scripts (HTTP 403), so `cache/th-hipflat-rent/` holds text extracts, not HTML.

All figures are **asking rents**, not signed leases. Where a source says how far signed rents sit below asking, it is 5 to 10% (Rummah, Visreal) and, in Bali, 10 to 17% for a year paid up front (Bali Villa Hunter). Nothing here is an official statistic: none exists for this region.

## Rows, and what each measures

| Place | Figure | What it is |
|---|---|---|
| Bangkok (and TH) | THB 53,000 | Vurel median, two-bed condos, Sukhumvit corridor, 87k listings from 11 portals. |
| Phuket | THB 40,000 | Vurel median, island-wide, 3,338 listings. Mixes Phuket Town with Bang Tao, Kata, Patong. |
| Chiang Mai | THB 23,000 | Vurel median, whole condo market, 1,928 listings. Nimman alone is about THB 29,000. |
| Kuala Lumpur (and MY) | MYR 4,750 | **Derived, thin.** Midpoint of IQI's RM4,500 to 5,000 settled range for inner-city KL; all home sizes, signed leases. |
| George Town | MYR 2,700 | Median of 35 two-bed listings on Rummah (script). |
| Ho Chi Minh City (and VN) | USD 1,300 | Visreal median, District 1 furnished two-bed condos, 202 listings. |
| Da Nang | EUR 847 | Median of 51 two-bed apartment listings on FazWaz Vietnam (script). Shown in EUR by the portal. Mostly beach districts. |
| Bali (`ID-BA`, and `CITY-1639002`) | IDR 35,000,000 | All Bali Rentals median, two-bed **villa**, Canggu, 83 listings. See below. |
| Jakarta (and ID) | IDR 20,540,000 | **Derived.** Cushman & Wakefield market-wide rent per m2 (Rp 265,007) times 77.5 m2. |
| Makati (and PH) | PHP 50,000 | BalayHub median, two-bed condos, Makati (Housal's 140 listings agree). |
| Mumbai (and IN) | INR 107,000 | **Derived.** Midpoint of ANAROCK's Q3 2026 quoted-rent range for Lower Parel, 700 sq ft two-bed. |
| Colombo (and LK) | LKR 461,000 | Median of 172 two-bed apartment listings, Colombo district, LankaPropertyWeb (script). |
| Phnom Penh (and KH) | USD 800 | Median of 23 two-bed listings, Chamkarmon khan, realestate.com.kh (script). |
| Dhaka (and BD) | BDT 70,000 | **Inferred, thin.** From agency ranges for Gulshan 1 and Banani two-beds. |
| Kathmandu (and NP) | NPR 85,000 | "Typical" asking rent for a 2 BHK on Thulo Bazaar; leans high (furnished, serviced). |
| Thimphu (and BT) | BTN 12,000 | **Inferred, very thin.** Three press pieces; no dataset. |
| Malé (and MV) | USD 2,000 | **Very thin.** Median of three property.mv listings for Malé island. |
| Vientiane (and LA) | USD 650 | **Very thin, and not flats.** Three house and townhouse listings. |

`TH`, `MY`, `VN`, `ID`, `PH`, `IN`, `BD`, `NP`, `BT`, `MV`, `LA`, `LK` and `KH` rows repeat their main city's figure, labelled in `measured_for`.

## Countries with no row

- **Pakistan.** Zameen, the one portal that matters, shows a bot check to scripts. The three listings a search returned were gone (HTTP 410), a studio at PKR 210,000, or a two-bed marked "no longer available", so I discarded them. Cost-of-living blogs say DHA and Clifton two-beds run roughly PKR 60,000 to 120,000, flagged by their authors as illustrative. Global Property Guide has a Karachi/Islamabad median but is paywalled.
- **Myanmar.** The Global New Light of Myanmar (27 Jul 2026) says Yangon rents in good areas have tripled in two years but gives no figure. Shwe Property two-beds are priced in USD and dated 2024. The kyat has an official and a market rate. No usable 2026 figure.
- **Brunei.** ExpatFocus gives apartments in Gadong, Kiulap and Kiarong as BND 400 to 800+, all sizes. The only two-bed listing I found is in Kuala Belait (BND 1,380), not the capital.
- **Timor-Leste.** Only aggregator estimates with no listings behind them (one-bed in Dili USD 300 to 850, a wide spread).

## The Palombo cities, and the gaps

Each has at least two independent figures in `crosschecks.csv`.

- **Bangkok.** Vurel THB 53,000, Hello Mira median THB 55,000 (Oct 2026), Hipflat province-wide average USD 1,486 (about THB 50,000). They agree within 5%. Livingcost's mean of one-bed and three-bed is USD 862, about 40% lower; it is crowdsourced and has no two-bed.
- **Phuket.** The widest spread: THB 33,684 (C9 Hotelworks long-term average, May 2025) to 40,000 (Vurel) to 45,000 (Thailand-Property, 75 listings) to 55,000 (one agency site, skewed to Bang Tao). Island-wide rents hide a Phuket Town versus northwest-coast gap (Baanlyy guide: Phuket Town two-beds THB 16,000 to 28,000, Bang Tao and Laguna condo median THB 45,000 across all sizes, per Kvartiry-Phuket). The dot is "Phuket", so the island median is the honest one; a site that wants Phuket Town needs another source.
- **Chiang Mai.** Vurel THB 23,000; Hipflat average USD 716 (about THB 25,000); Nimman median THB 29,000. Close.
- **Kuala Lumpur.** The weakest of the eight. No portal publishes a two-bed median; iProperty and PropertyGuru block scripts. IQI's signed-lease data (RM3,500 to 5,300 median, RM4,500 to 5,000 settled) is for all sizes. Three agency or platform guides put KLCC two-beds at RM4,000 to 7,000. Treat RM4,750 as plus or minus RM1,000.
- **Penang.** Rummah 35 two-beds median RM2,700; Rummah all sizes RM2,500; Dourr RM2,600; Propcashflow RM1,500 to 2,200. Consistent, except the investment blog.
- **Ho Chi Minh City.** Visreal District 1 USD 1,300; Visreal city-wide USD 1,345; VietnamRenty District 1 USD 1,600 (H1 2026). The USD 300 gap between Visreal and VietnamRenty is mix (Visreal's 75 m2 older towers against VietnamRenty's foreigner-grade towers). Livingcost USD 708 is again far lower.
- **Da Nang.** The thinnest of the Palombo set: FazWaz sample EUR 847 (Hai Chau only EUR 882, 11 listings); Homii USD 1,038 (agency catalogue, upper half of the market); Lease in Vietnam Hai Chau CBD USD 750 to 1,250. The FazWaz sample is beach-district heavy because that is where the apartment stock is. No Vietnamese consultancy publishes a Da Nang flat rent.
- **Bali.** The villa market, not a flat market. Canggu two-bed villas: Rp 35M (All Bali Rentals, 83 listings), Rp 32M (Bali Villa Hunter, 171, with pool), Rp 40M (Baliestate, 141), Rp 38.8M all types (Livuma). Seminyak Rp 24M (4 listings). A one-bed apartment in Canggu asks Rp 20M. Year leases paid up front cost about Rp 22.9M a month in Canggu (Rp 275M a year). **Decision for the coordinator:** the monthly asking median fits "going rate for a new let" in the other rows, but a couple who stay would normally sign a year, about 17% cheaper.

## Things you may have wrong or should decide

1. **Palombo's two-bed is not a Livingcost figure.** Livingcost publishes one-bed (40 m2) and three-bed (80 m2) city-centre rents only. Whatever he did for a two-bed, our asking-rent figures run well above Livingcost's one-bed and three-bed mean in Bangkok (about 1.7 times at THB 35.5 to the dollar) and Ho Chi Minh City (about 1.8 times), and level with it in Chiang Mai.
2. **Bali's dot has no GeoNames city.** There is no GeoNames city of 15,000+ at Canggu or Seminyak. I wrote the same figure under `ID-BA` and under Kuta (`CITY-1639002`, the nearest), with `measured_for` saying it is not Kuta town. Say if you want it pinned elsewhere, or dropped from Kuta. Denpasar has no row: it is the local administrative city with a different, cheaper market (Balinsky, read in a search excerpt: 10 Denpasar villa listings, two-bed median USD 450).
3. **Licences.** Vurel's terms say "Do not resell, scrape, or bulk-export the dataset"; I cite three headline medians from public pages. ANAROCK's and Cushman & Wakefield's PDFs are copyright with no reuse licence; one figure each. Check you are content before these go on a public map.
4. **Currencies.** Da Nang is in EUR (as the portal shows it). Malé, Phnom Penh, Vientiane and Ho Chi Minh City are in USD, the market currency. Bali, Jakarta, Colombo, Dhaka and Kathmandu are in local currency.
5. **Periods.** Almost all are November 2026 asking rents. KL is 2025 to early 2026 (signed leases); Makati is September 2026; Mumbai and Jakarta are Q3 2026; Thimphu is 2025 to 2026 press.
6. **Better sources found but not used.** bengaluru.rent publishes a tenant-reported (actual rent) two-bed median for Bengaluru, INR 26,000 (Nov 2026, 650 reports), CSV downloadable, reuse allowed with attribution; useful if you add Bengaluru. Global Property Guide publishes two-bed median asking rents for Jakarta, Bali, Karachi, Islamabad and others but is paywalled. Hipflat Thailand gives a bedroom-level average by province but is a USD average, not a median.

## Tool note

Parallel's search tool hit its free-tier rate limit partway through; I finished with the built-in search and fetch tools. Not an error in the data.
