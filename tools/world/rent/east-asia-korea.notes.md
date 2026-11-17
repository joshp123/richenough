# South Korea rent: notes

Written by AI on 2026.11.17 by model claude sonnet 5.5.

Files: `kr_molit_rtms.py` (the recommended rows, 60 of them), `kr_reb_rone.py` (cross-check rows, 44), `east-asia-korea.sources.csv`, `east-asia-korea.districts.csv` (the same statistic for 205 cities and districts, extra, for the parent's use). No curated CSV: nothing is hand-typed. Both scripts rebuild from `cache/kr-molit-rtms-2026/` and `cache/kr-reb-rone/` and fetch them if missing (`uv run tools/world/rent/kr_molit_rtms.py`; add `--districts` for the district file). The MOLIT download takes about 5 minutes.

## How a Korean flat is rented, and what the number is

A new lease is **jeonse** (one large deposit, no rent; 54% of new 60-85 m2 apartment leases in Seoul) or **wolse** (a deposit plus monthly rent; the deposit runs from KRW 10m to KRW 700m and trades off against the rent). A monthly figure with no deposit beside it is meaningless. So the amount is the monthly rent plus the monthly cost of the deposit, worked out for each contract:

`amount = median over contracts of ( monthly rent + deposit x r / 12 )`

`r` is KREB's market jeonse-to-wolse conversion rate for apartments of 60-85 m2 in the contract's province (R-ONE table A_2024_00159, 2026-09): 4.8% (Seoul) to 5.8% (South Chungcheong). Each row's note gives median rent, median deposit, `r`, the number of contracts, and the amount at the statutory cap. The two medians do not add up to the amount (rent and deposit are medians of different contracts; the amount is the median of the per-contract sum).

Why `r` from KREB and not the statutory rate: KREB measures what landlords and tenants trade at. The statutory cap is the Bank of Korea base rate (3.00% since 2026-08-27, bok.or.kr) plus 2 points, so 5.0%, and it binds only when an existing deposit is converted or a lease is renewed, not the rent of a new contract. The note gives the amount at 5.0% as a sensitivity; it differs from the main amount by 0% to 7% across the 60 rows (Seoul 3.00m vs 3.05m). If the plan wants one national number with no regional input, use the 5.0% variant (`amount_at_5pct` in the districts file).

What the deposit cost means for the couple: the deposit is capital that stays theirs but cannot be invested. `r` stands in for what that capital would earn. It is close to the plan's 5% real withdrawal rate, so the double counting risk is small, but the plan should know the deposit is already inside the monthly figure and not also counted as a capital need.

## Rows

### `kr-molit-rtms-2026` (recommended; the rows in `kr_molit_rtms.py`)

Ministry of Land (MOLIT) real-transaction register, apartment lease reports, contracts dated 2026-04 to 2026-09, area class 60-85 m2 (median flat is 84.8 m2: the standard 84 m2 "34 pyeong" type; the 59 m2 type falls in the 60 m2-or-less class and is out), contract type 신규 (new) and 월세 only. Every row's `measured_for` and `period` say so. Where a place has under 30 such contracts in six months the row uses 2025-10 to 2026-09; under 30 in twelve months, no row (none of the 60 rows needed the 12-month window; 14 of the 205 districts in the districts file did, flagged `12m`).

Rows: `KR` (all provinces pooled, not population weighted), 17 provinces and metropolitan cities (`KR-11` ... `KR-49`), `CITY-` rows for Seoul (central zone only, see below), 7 metropolitan cities (same figure as their province row), and 34 other cities (the pooled 시 including its districts). Yongin has no GeoNames city in `cities15000`, so no `CITY-` row; it is in the districts file.

Seoul city row (`CITY-1835848`): the central zone of Jongno, Jung and Yongsan (KREB's 도심권), 423 contracts. Whole Seoul is `KR-11` (7,970 contracts). Seoul districts, from the districts file (amount, KRW per month, 6 months): Gangnam 4.40m, Seocho 4.20m, Songpa 3.80m, Seongdong 3.60m, Mapo 3.30m, Yongsan 3.30m, Jongno 3.20m (83 contracts), Jung 3.09m, Guro 1.54m.

### `kr-reb-rone` (cross-check; the rows in `kr_reb_rone.py`)

KREB R-ONE, National Housing Price Trends Survey, apartments: average monthly rent and average deposit of the wolse sample apartments, plus the all-apartment conversion rate, same formula, 2026-10. This is **not new contracts**. KREB staff estimate the market price each month of a fixed sample of 37,619 apartments from recent transactions, listings and agents' opinions, so it describes the stock at today's asking levels, all sizes mixed. KREB's own survey notes say the average and median prices are "for reference" because the survey is built for the price index. The MOLIT new-contract amount is 0.96 to 1.64 times the KREB figure across the 42 places both cover (median 1.19; Seoul 3.00m vs 2.46m; national 1.24m vs 1.28m). Higher is what you would expect: rents are rising (KREB's Seoul average rent rose 12% from January to October 2026), and KREB's sample mixes in smaller flats. Do not load both sets under the same place codes. The KREB set is useful for places MOLIT lacks (it has nothing for the 군 and small cities that MOLIT also lacks) and for checking the order of magnitude. Use the district-level tables A_2024_00069/00068 for any 시군구 not covered.

## What each source is, and its licence

- MOLIT register (rt.molit.go.kr): keyless CSV download form, nationwide capped to 1 month and a province to 1 year. The page says the data has no legal force, may change as reports are corrected or cancelled, and that figures derived from it should not be published as official statistics (the official aggregates are by report date). It states no licence. Public data of the Korean state; I treat it as "free to read, no licence stated". If that is not acceptable for a public site, the Seoul file below is explicit.
- Seoul Open Data "서울시 부동산 전월세가 정보" (data.seoul.go.kr OA-21276): the same register for Seoul only, one ZIP per year, free, KOGL type 1 (attribution; commercial use and changes allowed). The 2025 file was last updated 2026-02-04, so it does not reach 2026; the API needs a key. I did not use it for the figures. It is the licensed fallback for Seoul.
- KREB R-ONE: keyless JSON endpoints behind the portal's table viewer. Approved national statistic no. 304004. No licence on the tables.
- KOSIS: not tried. It republishes the same KREB survey.

## Thin or imperfect

- **Apartments only.** Villas (연립/다세대), officetels and detached houses are not in the figures. Many young couples rent villas and officetels, usually cheaper per m2 than apartments in the same district. MOLIT offers them in the same download (`srhThingNo` B, D, C); I did not run them to keep the size of the work down.
- **Wolse only.** In Seoul 54% of new 60-85 m2 leases are jeonse. A jeonse flat costs `deposit x r / 12` a month in opportunity cost (Seoul: median deposit KRW 700m, KRW 2.8m a month) and is shown in each note for comparison. The wolse-only amount is not the whole market; it is what the site asked for ("a new let at monthly rent").
- **Who rents wolse.** Wolse tenants skew to smaller deposits, so the Seoul wolse amount (3.00m) is close to the jeonse-equivalent (2.80m) rather than far above it. The two methods agree in order of magnitude.
- **Jeonnam, Mokpo, Gwangyang, Jeonju:** more than half of new wolse leases there have a tiny rent (KRW 50,000 to 90,000) with a KRW 140m to 200m deposit, i.e. quasi-jeonse. The medians of rent alone are misleading there (South Jeolla median rent KRW 70,000), so the amount (KRW 734,000) rests almost entirely on the deposit term. Read those rows with the note.
- **Small samples:** Jongno 83 contracts; some districts under 100; the districts file lists `n` for each. Every published row has at least 138 contracts (the note gives n); the largest is 54,495 (national).
- **Reporting rules.** From my search of Korean news and the Seoul city site (not the statute): reporting is required for homes with a deposit over KRW 60m or monthly rent over KRW 300,000, in the capital region, metropolitan cities, Sejong and 시 of the provinces (not 군 outside the capital region), within 30 days; the fines began in June 2025. Cheap wolse (below both thresholds) and rural counties are therefore missing, and the latest month is incomplete. The 'contract type' field also has about 10,700 contracts marked '-' (unknown), which I excluded.
- **Time.** Rents moved fast in 2026 (Seoul +12% in ten months on KREB's numbers). A six-month window lags the October level by about three months. A 12-month window would lag more.
- **Provinces include rural areas.** A province row is the median over its contracts, so it is weighted toward its big cities (Gyeonggi: Seongnam, Suwon; Gyeongnam: Changwon). It does not describe a rural county.

## What I could not do

- Area-specific KREB averages: KREB publishes average rent only for all sizes, so the cross-check cannot be restricted to 70-85 m2.
- A hand-typed press or PDF figure: not needed.
- Sub-province conversion rates for a 60-85 m2 apartment: KREB publishes them by size only at province level. A district row uses its province's rate (district rate for all sizes is in A_2024_00156 if wanted).

## What the plan may have wrong

- **Place codes.** The 2026 reforms changed the map: 광주 and 전남 became one 전남광주통합특별시 from July 2026 (the register now files all Gwangju and Jeonnam leases under it, including old ones); Incheon's districts were reorganised (제물포구, 영종구, 서해구, 검단구, ...); 화성시 got four new districts. I split Gwangju (`KR-29`: the five 구) from South Jeolla (`KR-46`: the 시 and 군) on the address. If the map draws the merged province, fold the two rows. ISO 3166-2 still lists KR-29 and KR-46; I did not find a code for the merged unit.
- **Seoul "centre".** Seoul's central business area is Jongno, Jung and Yongsan, but the expensive area to live is Gangnam and Seocho (4.2-4.4m a month against 3.2m). Which one the site means by "a centre" changes the Seoul rent by about a third. The brief said "Jung, Jongno, Yongsan, Mapo, Seocho, Gangnam, Songpa"; I used the three that KREB calls the central zone.
- **"A new let" in Korea.** The sensible new-let figure for Korea includes jeonse, which is most of the market in Seoul. Dropping it understates what a tenant who cannot or does not want to pay a deposit would face; keeping it requires an assumption about the cost of tying up a large deposit (the plan's 5% real withdrawal rate would do). I used wolse as asked and gave the jeonse equivalent in each note.
- **Rent is not the monthly bill.** Korean tenants also pay a building management fee (관리비, typically KRW 150,000 to 400,000 for an 84 m2 flat, not measured here) on top. I found no official source for it in this task.
