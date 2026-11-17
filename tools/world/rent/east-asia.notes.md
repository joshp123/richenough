# East Asia rent notes (two-bed flat, 70 to 85 m², going rate for a new let)

Written by AI on 2026.11.17 by model claude sonnet 5.5. Korea, mainland China, Macao and Mongolia were researched by two Sonnet 5.5 sub-agents; their own notes are `east-asia-korea.notes.md` and `east-asia-china-mo-mn.notes.md` and carry the detail. I ran their scripts, spot-checked the China table (Shenzhen, Shanghai, Beijing 60-90 m² cells match the PDF) and did not re-check Korea beyond the output shape.

Rebuild everything: `uv run tools/world/rent/east-asia-build.py`. It writes `east-asia.table.csv` (236 rows, one per place code), `east-asia.crosschecks.csv` (54 rows that lost a place code or are alternates), `east-asia.sources.all.csv` (12 sources) and `east-asia-japan.districts.csv` (every Tokyo, Yokohama and Kawasaki ward). When two sources give one place code, the later in `ORDER` wins and the loser goes to crosschecks.

## What each figure measures

| Source | Measures | Rows |
|---|---|---|
| Japan, e-Stat Retail Price Survey, item 3001 (`jp_estat_rps.py`) | Rent paid by **all sitting private tenants**, all sizes, per 3.3 m², mean of 12 months to Sep 2026, ÷3.3 × 75 | 47 prefectures (prefectural capital stands for the prefecture), 22 cities, `JP` |
| Japan, REINS (`jp_reins.py`) | **Concluded new lets** through member brokers, Jul to Sep 2026, condominium-type flats of every size (average 28 to 50 m²), ¥/m² × 75 | JP-11, JP-12, JP-13, JP-14, Tokyo (five central wards), Yokohama, Kawasaki; these replace the e-Stat rows for the same codes |
| Hong Kong, RVD (`hk_rvd.py`) | Average rent on tenancy agreements received for stamping (new lets and renewals), class C = 70 to 99.9 m², mean of Jul to Sep 2026, provisional | Hong Kong Island (city row), Kowloon (country row) |
| Singapore, URA (`sg_ura_hdb.py`) | Median rent per sq ft of registered condominium rental contracts, 2026-Q3, × 807 sq ft | `SG` (all), Singapore city row (central districts 1, 2, 4, 6, 9, 10, 11) |
| Singapore, HDB (alternates) | Owner-declared rents of approved HDB flat rentals, Aug to Oct 2026, median 3-room (S$2,900) and 4-room (S$3,400) | crosschecks only |
| Taiwan, MOI (`tw_moi_lvr.py`) | Median of registered leases of whole two-room flats of 70 to 85 m² building area (includes shared parts), market leases only, Aug 2025 to Jul 2026 | 9 counties and cities, their main cities, Taipei central five districts, `TW` |
| Korea, MOLIT register (`kr_molit_rtms.py`) | New monthly-rent (wolse) leases of 60 to 85 m² apartments, Apr to Sep 2026; amount = rent + deposit × conversion rate ÷ 12 | 60 rows |
| Korea, KREB R-ONE (`kr_reb_rone.py`) | Appraised average rent of the housing stock, not new contracts | crosschecks only |
| China, China Index Academy (`cn_cric_creis.py`) | **Asking** rent of listed 60 to 90 m² flats, urban districts of 50 cities, Oct 2026 | 81 rows |
| Macao, DSEC | Average rent of every unit with a lease in force, MOP 140/m² × 75 | `MO` |
| Mongolia, NSO via a news report | Experimental asking-rent estimate for Ulaanbaatar's six central districts, Aug 2026 | `MN`, `MN-1`, Ulaanbaatar |

## Things you should know

- **Japan has two different measures under one country.** Tokyo's new-let figure (five central wards ¥387,400; the whole prefecture ¥285,800) comes from REINS, while the other 43 prefectures use sitting-tenant averages (for Tokyo's 23 wards the sitting-tenant figure is ¥226,000). Sitting tenants pay less than new tenants, so the rest of Japan is probably understated against Tokyo. No free new-let figure exists outside the Tokyo region that I could find (the SUUMO and HOME'S pages are asking rents and not machine-readable). The Retail Price Survey figure is per 3.3 m² across every dwelling size, so it is only a proxy for a 75 m² flat. `JP` is the median of the 47 capitals, not a national average.
- **Japan, 2023 Housing and Land Survey (not done).** It would give whole-prefecture rents per tatami, all tenants, which still is not a new-let figure and would need e-Stat file hunting. The 47 capital rows already cover every prefecture, so I left it. It would be the better "whole prefecture" figure if you want one.
- **REINS** serves an incomplete certificate chain, so the script skips certificate checks (sha256 of the PDF in the cache folder: `08be0ea962a92c423bfcbc1eaf8b7fe1e83308bef4dd8715321ac975c1786d70`). The PDF lives at `/pdf/trend/sc/`; the short path in search results returns 403.
- **Hong Kong:** the RVD publishes class C averages only for Hong Kong Island, Kowloon and the New Territories, with no district split and no territory-wide class C figure. The `HK` country row is therefore Kowloon (HK$34,125); Hong Kong Island is HK$36,500; the New Territories (HK$22,750) is not written. `HK` has no ISO first-level regions, so a three-way split has no place code. If the site wants a single Hong Kong number, Kowloon is the middle region.
- **Singapore:** URA's file lists only projects with 10+ contracts in the quarter and carries no unit label (S$ per sq ft per month is inferred; the values only make sense as that). The central row approximates the Core Central Region by postal district. Condominium rents are the right comparator for a foreign couple; HDB is shown as an alternate because it is much cheaper and subject to minimum-stay rules.
- **Taiwan:** thin because only registered market leases count (about 60% of registered leases are social-housing schemes and are excluded) and the filter is strict (two rooms, 70 to 85 m², whole unit). Eleven counties had fewer than 20 qualifying leases and have no row: Nantou (1), Chiayi City (14), Chiayi County (6), Yilan (15), Pingtung (5), Changhua (4), Hsinchu City (13), Hsinchu County (6), Miaoli (1), Kinmen (1), Yunlin (8). They fall back to `TW` (NT$20,000), which is dominated by Kaohsiung, New Taipei and Taipei. Taoyuan, Taichung and Tainan have 99 to 148 leases each; Taipei 180 (107 in the central five districts). Lienchiang, Penghu and Taitung have none. The city rows for places other than Taipei repeat the county figure. The download page says bulk files need a private licence with the Ministry; I downloaded without signing anything, and the licence text referred to was not on the page.
- **Korea:** a monthly figure is only meaningful with its deposit. See the Korea notes; the KREB cross-check differs by 0.96 to 1.64 times. The Korean register page says the data should not be republished as official statistics, which matters for a public site.
- **China:** every city figure is an asking rent for 60 to 90 m² listed flats in the whole urban area, so central flats cost more; there is no free central-zone data. Provincial rows are the provincial capital only. `CN` is the median city, not a national figure. Chengdu has an official bureau figure (CNY 2,512) too; it sits in crosschecks because the bureau's site could not be fetched.
- **Mongolia** rests on one news report of a National Statistics Office release, and on reading Mongolian "3 rooms" as a two-bedroom (the 2-room figure is 1,930,000 MNT, 57% lower). Unconfirmed.
- **Macao** is lease-in-force rent, so it lags the going rate.

## Plan points to settle

- City states (`HK`, `MO`, `SG`) have a country row and a city row that are different measures (HK) or the same (MO). Say which wins.
- Rows for places where a source is an all-tenants measure (Japan) are mixed with new-let measures (Tokyo, Hong Kong, Singapore, Taiwan, Korea). The page may want to show `note` text, not just the number.
- `amount` for Korea includes the capital cost of the deposit, which no other country's rent does.
- Per-m² sources × 75 m² overstate small-unit-heavy markets (Japan REINS, Macao) and the per-m² method for China overstates big cities; the agents used the 60 to 90 m² band for China for that reason.

## Not covered

Every country in the brief has a row (JP, KR, TW, HK, MO, SG, CN, MN). Mongolia outside Ulaanbaatar, Chinese provinces other than the capitals, Korean cities without a GeoNames id (Yongin), Japanese prefectures beyond their capital, and Taiwan's 11 thin counties have no figure of their own.
