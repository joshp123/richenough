# East Asia rents: mainland China, Macao, Mongolia

Written by AI on 2026.11.17 by model claude sonnet 5.5. Figures read on 2026-11-17.

## Files

- `cn_cric_creis.py`: 50 Chinese cities, 26 provincial capitals under their province codes, the four municipalities, and a `CN` fallback row. Run with `uv run tools/world/rent/cn_cric_creis.py`; 81 rows.
- `east-asia-china-mo-mn.curated.csv`: Macao (1 row), Mongolia (city, `MN-1`, `MN`), and a second, official Chengdu row.
- `east-asia-china-mo-mn.sources.csv`: six sources (the script's `SOURCES` entry is copied in).
- Cached pages and PDF: `cache/cn-cric-creis-2026-10/`, `cn-chengdu-rent-2026q2/`, `mo-dsec-rental-2026q3/`, `mo-dsec-rental-2026q1/`, `mo-dsec-rental-2025q1/`, `mn-nso-rent-2026-08/`.

## Mainland China

**What the figure is.** China Index Academy (中指研究院) takes asking (listing) rents from Fang.com, Lianjia, Beike and Anjuke for a fixed sample of active compounds in each city's urban districts, on the 25th of each month. It is not a signed rent and not all tenants. October 2026, Table 6 of its free monthly PDF, gives the average rent of a whole listed flat by size band. I use the 60-90 m2 band, the nearest to 70-85 m2. It is not filtered to two bedrooms. Examples (yuan a month): Shenzhen 5,893, Shanghai 5,263, Beijing 5,149, Hangzhou 3,747, Guangzhou 3,609, Chengdu 2,365, Wuhan 1,947, Chongqing 1,735, Xi'an 1,856, Tianjin 2,073.

**Use the band, not 75 m2 x the per-m2 figure.** Table 5 gives rent per m2 for all sizes (Beijing 80.78, Shanghai 85.04, Shenzhen 83.21). 75 m2 x that is higher than the 60-90 m2 band in the big cities (Beijing 6,058 against 5,149; Shanghai 6,378 against 5,263). Small flats dominate the listings and cost more per m2, so the all-size per-m2 average overstates a 75 m2 flat. Each row's note carries both.

**No central zone.** CRIC's district split is only in paid reports and chart images (the free articles say "Chaoyang fell", not what it costs). Every city figure is the whole urban area. In Beijing, Shanghai, Guangzhou and Shenzhen a central flat costs more than this.

**Province rows are the capital only.** `CN-GD` is Guangzhou (not Shenzhen), `CN-ZJ` Hangzhou, and so on; `measured_for` says so. Delete them if the page should not show a province colour from one city. Tibet and the other provinces whose capital is not in CRIC's 50 have no row. `CN-BJ`, `CN-SH`, `CN-TJ`, `CN-CQ` are municipalities and equal their city.

**`CN` row (1,825).** Median of the 50 cities. It describes the large-city market, not China; small towns are far cheaper. Treat as a last fallback.

**Chengdu has a second, official row.** Chengdu's housing bureau publishes average rent by subdistrict every quarter (yuan per m2 per month; residential, apartment, dormitory). Q2 2026, 58 residential subdistrict figures in the five central districts, unweighted mean 33.49 yuan per m2, x 75 = 2,512 yuan; Chunxi Road alone 43.76. It agrees with CRIC (2,365 for 60-90 m2, whole city) to within about 6%. The place code is the same as the CRIC Chengdu row, so you must pick one. The bureau's own site refused my fetch (HTTP 412); the table is from the Chengdu Bendibao reprint, and the bureau's method is not stated there.

**Checked, not usable.**
- National Bureau of Statistics: publishes a rent CPI sub-index, not levels. Its census yearbook tables I found (`stats.gov.cn/sj/pcsj/rkpc/5rp` and `6rp`, older censuses) count households by band of monthly rent, with no flat size. I found no rent table for the 2020 census, and no rent per m2 anywhere.
- Shenzhen: the only official rent reference is the 2022 edition (Nanshan 109 yuan per m2, Futian 98, Luohu 80, Bao'an 68) from the Shenzhen housing bureau's research centre. I could read it only through a third-party page (shenzuhui.com); zjj.sz.gov.cn refuses requests from here. Stale and unverified, so not used.
- Beijing, Shanghai, Guangzhou housing bureaus: no free monthly rent level found. Guangzhou has a 租金参考价 for public-housing pricing but I found no table.
- Beike Research (贝壳研究院): no free October 2026 city table found.
- A report summarised on Sina (2026-09-16) gives Beijing 98.83 and Shanghai 94.64 yuan per m2 for August 2026. It is a different, higher basis (probably managed apartments); not opened in full, not used.

## Macao

DSEC Rental Statistics, Q3 2026 (released 2026-11-13): MOP140 per m2 of usable area for residential units; x 75 = MOP10,500 a month. Q1 and Q2 2026 were also MOP140, so it is flat. The statistic covers every unit with an unexpired lease, from property-tax lease declarations, so it lags new lets and likely understates the going rate when rents are rising (they are flat now). Usable area is smaller than gross, so 75 m2 usable is a big flat; DSEC's under-50 m2 band costs MOP168 per m2, the 100-150 m2 band MOP129. The 50-99.9 m2 band for Q3 is not in the press release (Q1: MOP139). DSEC's release PDF and database could not be fetched (JavaScript and POST driven, GUID links), so the row is typed from the Government Information Bureau's copy of the release. No script.

## Mongolia

The National Statistics Office (NSO) has an experimental monthly rent estimate for Ulaanbaatar's six central districts, from unegui.mn asking rents. The 1212.mn PxWeb API (`data.1212.mn/api/v1/en/NSO`) has the housing price index and sale prices per m2 but no rent table; I walked all 1,478 tables. The figures exist only in news reports of NSO releases, so the source is iKon.mn quoting NSO, and the NSO original is unread. August 2026: 1-room 1.40m, 2-room 1.93m, 3-room 3.03m MNT a month.

**The row uses the 3-room figure (3,030,000 MNT).** In Mongolian counting the living room counts, so 3-room is a two-bedroom flat (a 66 m2 example is the only size I found; NSO states none). If you read "2-room" as the two-bedroom, use 1,930,000 instead; the gap is 57%, so this choice matters more than any other in this file. I could not confirm the room-count reading from a source.

The iKon.mn headline for the 11 September article says 2-room 1.85m; its text says 1.93m. 1.85m is February's figure. I trust the text. September and October 2026 figures were not found. `MN` and `MN-1` and the Ulaanbaatar city row carry the same number; the country row is Ulaanbaatar only and overstates the rest of Mongolia.

## What is thin

- China: asking rents, whole urban area, no central zone, not two-bedroom specific; one month (October 2026).
- Macao: stock of leases, not new lets; usable area.
- Mongolia: one portal, six districts, secondary reporting, room-count assumption.

## What the plan gets wrong

- "A two-bed in the centre" is not what China's free data gives: nothing free is central. If the page promises a centre, say "city-wide" for Chinese cities.
- The brief says "multiply per-m2 by 75". For China the per-flat 60-90 m2 band is better and is used (see above).
- Mongolia: "2-room apartments" is a one-bedroom flat in local counting.
- Hong Kong and Taiwan are not in my scope; Macao's DSEC is the only SAR figure.
