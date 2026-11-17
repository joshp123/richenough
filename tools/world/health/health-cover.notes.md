# Private health cover for a new-resident couple aged 45: notes

Written by AI on 2026.11.17 by model claude sonnet 5.5, as research helper for the agent that owns the world data. Nothing here is committed.

## Result

Three insurers publish a full rate table with a country-to-zone list, so every country maps to a zone in each. Two more publish tables with no country dimension and serve as flat cross-checks.

| Insurer and product | Zones | Currency | Table date | Covers |
|---|---|---|---|---|
| AXA GlobalReach (AXA Hong Kong) | 6 (zones 2 to 7) | HKD and USD, both printed | Effective 2025-09-09 | 231 country entries; no US, Russia, Belarus, Iran, Cuba, Syria and a few more |
| Generali InternationalExclusive (Malaysia) | 6 (zones 1 to 6) | MYR | Edition 02/2025 | 248 entries, includes the US (zone 1) |
| Globality YouGenio World (Luxembourg) | 5 | EUR | Edition 01/2025 | 243 entries, includes the US (zone 1) |
| IMG Global Medical Insurance | none | USD | New business from 2026-02-01 | flat |
| Care Expat World (Barmenia, Germany) | 3 areas of cover, not residence | EUR | 2026 | flat |

AXA and Generali use the same country-to-zone list except China (AXA zone 7, Generali zone 2) and the countries AXA leaves out. So they are two price lists on one zoning, not two independent zonings. Globality's zoning is its own.

Each country therefore has up to three independent zone-based figures plus IMG. For a typical middle-cost country (Thailand, Turkey, Vietnam, Malaysia, Portugal, Germany) the figures for the couple are:

| Place | AXA (nil deductible) | AXA (USD 3,125 deductible) | Generali Plan 2 | Globality Plus | IMG Gold |
|---|---|---|---|---|---|
| Thailand | 2,063 | 1,238 | 703 | 1,062 | 662 |
| Malaysia | 2,017 | 1,210 | 678 | 681 | 662 |
| Portugal, Germany | 2,508 | 1,505 | 728 | 681 | 662 |
| Mexico | 2,697 | 1,618 | 827 | 1,062 | 662 |
| United Kingdom | 2,562 | 1,537 | 769 | 1,987 | 662 |
| United States | n/a | n/a | 1,618 | 2,538 | n/a |

US dollars per month for two people aged 45, at ECB rates of 2026-11-17 (USD per EUR 1.0989, MYR per EUR 4.4983). The ECB rate is only for putting the insurers side by side; the real conversion belongs to the exchange-rate table.

For the US, Generali's figure (USD 1,618) lands inside the US agent's ACA Silver medians for two 45-year-olds (USD 1,600 to 1,744 in `data/tables/health-cover.us.csv`). That is a useful independent check that the Generali table is read correctly. Globality's US zone is about 50% higher.

The spread between insurers is large (AXA about three times Generali for the same age and zone). That is normal in this market: IPMIcompare's July 2026 rate-engine survey found five to nine times between cheapest and dearest for identical cover. The page should show one number with an honest label, not pretend the insurers agree.

### Suggested figure and how to read it

`health-cover.compare.csv` has one row per place (252, every ISO code in GeoNames' country list), with each insurer's figure in USD and two medians:

- `median_zoned`: the median of AXA (nil deductible), Generali Plan 2 and Globality Plus. It keeps the zone structure. Range USD 581 to 2,508, median 703. Needs at least two of the three.
- `median_with_img`: adds IMG. Flat across countries, so it pulls everything toward USD 660 to 700 and hides the zones. I would not use it as the figure.

The median of three is robust to AXA being three times dearer, and it is one method for every country. If you want a lower, "typical expat" figure use Generali alone; for a premium figure use AXA alone. I would use `median_zoned` and show the three underlying figures on the country card.

`health-cover.candidate.csv` is the same data in the `data/tables` contract (`place_code,amount,currency,unit,period,measured_for,source_id,note`), one row per insurer per country, in each insurer's own currency. IMG and Care rows are included for every country, so choose rows by `source_id` rather than taking them all. I did not write to `data/tables/`.

## What was captured

All in `tools/world/health/`. `ipmi_tables.py` reads the cached PDFs (it downloads any that are missing; IMG refuses requests without a browser User-Agent) and writes the typed tables; `couple_cost.py` builds the per-country figures. Run both with `uv run`.

- `axa-globalreach.rates.csv`: 28,518 rows. Zone x benefit level (Prestige, Comprehensive, Standard, Essential) x area (Asia, Worldwide excl. USA, Worldwide) x annual deductible (nil, USD 3,125, 6,250, 12,500) x single age 0 to 99, in HKD and USD. Single ages, so any age can be priced, not only 45 to 49.
- `generali-intl-exclusive.rates.csv`: 4,157 rows. Zone x plan 1 to 4 x area x single age 16 to 80, in MYR. Children's bands are in merged PDF cells and were not typed.
- `globality-yougenio.rates.csv`: 1,125 rows. Zone x plan (Essential, Classic, Plus, Top) x outpatient deductible (0, 250, 500, 1,000, 2,500) x 15 age bands (0-19 ... 85-99), monthly and annual EUR.
- `img-gmi.rates.csv`: 648 rows. Plan (Bronze, Silver, Gold, Platinum) x two areas x deductible x age band, USD. No age 70 and over (IMG says "contact us").
- `care-expat-world.rates.csv`: 297 rows. Area x plan (Basic, Comfort, Premium) x deductible (0, 1,200, 3,600) x age band.
- `*.zones.csv` for AXA, Generali and Globality: the insurer's own country name, our ISO 3166 code, zone.
- `health-cover.sources.csv`: every source, in the `data/sources.csv` columns. PDFs are in `cache/axa-globalreach/`, `cache/generali-intl-exclusive/`, `cache/globality-yougenio/`, `cache/img-gmi/`, `cache/care-expat-world/`.

### Checks run

- AXA: 288 series (6 zones x 4 levels x 4 deductibles x 3 areas) of 99 ages each; premium rises with age from 19 in every series; Prestige > Comprehensive > Standard > Essential at age 45 in every zone, deductible and area.
- Generali: my parse matches the insurer's own illustrative premium table (Product Disclosure Sheet, Malaysia residents, zone 6) in all 24 cells checked (plans 1 to 4, Asia, worldwide ex USA, worldwide, ages 40 and 50).
- Globality: for every row, monthly x 12 equals the yearly table.
- Source typos found and corrected: Globality zone 3 yearly "6.000.00" (monthly table gives 500 x 12 = 6,000); Generali zone 5 plan 3 Asia age 28 "6.448" (neighbours bracket 6,448).
- Source gaps left as gaps: Generali zone 3 plan 3 Asia ages 76 to 78 are blank in the PDF; AXA age 0 rows are garbled in the PDF text and equal age 1, so not typed.

## Reference plan and why

The brief asked for comprehensive inpatient and outpatient, worldwide excluding the USA, no maternity or dental, deductible near USD 1,000.

- AXA GlobalReach: **Comprehensive**, worldwide excl. USA. GP and specialist consultations are paid in full only on Prestige and Comprehensive (brochure, benefit schedule item III(j)); Standard and Essential cover GP and specialist consultations only around a hospital stay (90 days before and after), plus cancer, dialysis and outpatient surgery. Prestige adds dental, optical and maternity, so Comprehensive is the match. Deductibles are nil, USD 3,125, 6,250 or 12,500. USD 1,000 is not offered; nil is nearest (USD 1,000 away) and USD 3,125 is the other bracket. I show both.
- Generali InternationalExclusive: **Plan 2** (RM 7,000,000 yearly limit), worldwide excl. USA. Plans 1 to 3 include GP and specialist consultations; Plan 1 adds screening, maternity, dental and optical; Plan 4 is inpatient only. No deductible exists (the PDS says "less any deductible or co-insurance" but lists none). In zone 1 (the US) only worldwide cover is sold, so the US figure is worldwide including the USA.
- Globality YouGenio World: **Plus**, EUR 1,000 outpatient deductible. Essential is inpatient only; Classic has outpatient capped at EUR 7,500 a year; Plus caps outpatient at EUR 15,000 and adds dental; Top is uncapped. The deductible applies to outpatient and dental only. **The table does not say whether it prices worldwide including or excluding the USA** (the general conditions offer both and double the limits for "including"). If it prices "including", the figures overstate the ex-USA price.
- IMG GMI: **Gold**, USD 1,000 deductible, the "excluding USA, Canada, China, Hong Kong, Japan, Macau, Singapore and Taiwan" sheet. IMG's brochure says Silver, Gold and Platinum cover outpatient care; Bronze covers it only after inpatient treatment or outpatient surgery.
- Care Expat World: **Basic**, EUR 1,200 deductible, area "excluding China, Singapore and the US".

None of these is the same product, so a figure for one country from two insurers still differs by benefit level, deductible, network and claims limits.

## What is thin or wrong

- All three zoned tables are from 2025 (AXA Sept 2025, Generali Feb 2025, Globality Jan 2025). Medical inflation in this market has run high; a 2026 refresh would likely be higher. Globality's product was replaced by Global Health Journey in February 2026 and no public Journey table exists.
- AXA's table is for policies issued in Hong Kong. Its applicability to someone buying through AXA elsewhere is not stated. Premiums exclude the Hong Kong levy.
- Generali states it generally cannot cover a person who is a national of their country of residence (other than Malaysia). That suits a new foreign resident.
- Gaps in the zone lists: Kosovo and South Sudan are in none. Palestine is only in Globality (zone 4). AXA also omits Afghanistan, Belarus, Cuba, Iran, North Korea, Russia, Sudan, Somalia, Syria, Venezuela, Yemen, Zimbabwe, Myanmar, Congo (both), the US and a few islands. The sanctioned ones are listed by Generali and Globality, but cover there is subject to the insurers' compliance checks. I would not publish a number for them without a flag.
- Alderney, Herm, Sark, Madeira, the Azores and the Canary Islands appear as separate entries in the AXA and Generali lists with their own zones (for example Canary Islands zone 4 against Spain zone 3). I left them out of the country mapping; `*.zones.csv` keeps them. The dissolved Netherlands Antilles entry is applied to Curacao, Sint Maarten and Bonaire.
- IMG's table has no country dimension and I could not confirm eligibility rules (it does not sell to people in some countries). I dropped IMG for the US and for the other zone-1 places on the assumption that it is not sold to US residents; I did not verify that.
- A median of three is a method, not a market price. The headline number will depend on which insurer's benefit level you think "private health cover" means.
- Scope: Palombo's "private health cover" may be local cover, not IPMI. For rich-country cities with a universal system (most of Europe, Japan, Korea, Taiwan) many residents would use the public scheme or a top-up. The IPMI figure is the cost if the couple insure privately and fully; it is not what a typical local pays.

## Local options (for you to decide on, not in the main table)

Official source where I found one; otherwise labelled. Nothing here is a quote.

- **UAE, Dubai.** Cover is compulsory for residents. The DHA Essential Benefits Plan is in force from 2025-01-01 with an Index Rate band of AED 550 to 750 per member per year plus VAT (DHA circular GC 03/2024, cached). That is the regulator's figure for the minimum plan; for two members about AED 1,100 to 1,500 a year before VAT. Broker blogs say the EBP is for residents earning AED 4,000 or less a month and their dependants, and give AED 1,600 to 1,771 for a non-working married woman aged 18 to 45; I did not find these in an official document. An investor, retiree or golden-visa couple would normally buy a normal plan, for which the zone tables above (UAE is zone 4 at AXA and Generali, zone 3 at Globality) are the proxy. Abu Dhabi runs its own scheme; not researched.
- **Qatar.** Mandatory cover for residents and visitors under Law 22 of 2021, with employers paying for employees (secondary sources, not read in the law itself). No official premium table found. A 2026 blog gives QAR 1,200 to 2,500 a year per resident for the mandatory package; unverified.
- **Saudi Arabia.** The Council of Health Insurance (formerly CCHI) sets a unified minimum policy; the employer pays for employees. No official price found. A blog says SAR 4,000 to 8,000 a year for an adult comprehensive plan; unverified.
- **Australia, Overseas Visitors Health Cover.** Required by condition 8501 on most working visas. Insurers (Medibank, nib, Bupa, HCF, Allianz) show prices only through quote forms; I found no public table. A blog estimates AUD 160 to 240 a month for a couple on basic cover; unverified. Medicare applies once the couple are permanent residents (not researched).
- **Thailand.** Visa rules (official): the Non-Immigrant O-A needs health insurance or social welfare of at least USD 100,000 (THB 3 million) since 2021-10-01, replacing THB 400,000 inpatient and THB 40,000 outpatient (Ministry of Foreign Affairs document, cached). Many sites still quote the old figures, and some attach them to the O-X visa. LTR visa: hospitalisation and medical cover of at least USD 50,000 with at least 10 months left, or Thai social security, or a USD 100,000 deposit held for 12 months (BOI list as of 2025-11-06, Wealthy Global Citizen category; other categories not read). Local insurers: Pacific Cross and Luma publish no premium table; Luma's brochures say rates are "indicative" and available on request; the only age-band tables I found are on a broker's blog. Not captured. For Thailand the zone tables give USD 703 (Generali) to 2,063 (AXA) a month for the couple.
- **Japan, National Health Insurance.** Premium is set by each municipality and charged per household. Koto ward, Tokyo, FY2026 (official page, cached): per person a flat amount of JPY 47,600 (medical) + 17,600 (elderly support) + 17,800 (care, ages 40 to 64) + 1,873 (child support) = JPY 84,873, plus 7.51% + 2.80% + 2.43% + 0.27% = 13.01% of the previous year's income after a JPY 430,000 deduction, with annual caps (JPY 670,000 + 260,000 + 170,000 + 30,000). Two 45-year-olds with no taxable income: JPY 169,746 a year (about JPY 14,100 a month) before low-income reductions. Investment income held in a Japanese withholding account and not declared is, per Koto, excluded from the premium base; if declared it counts. Enrolment rules for foreign residents not checked here.
- **South Korea, NHIS.** Income-based: 7.19% of income in 2026 plus long-term care at 13.14% of that (secondary sources quoting the NHIS notice). Foreign residents who stay six months or more are enrolled; secondary sources give a floor of about KRW 150,000 a month for foreigners and KRW 20,160 for locals. No official NHIS figure was reachable; the foreigner floor is unverified.
- **Taiwan, NHI.** General rate 5.17% (Taipei Times, Nov 2025); non-employed foreign residents join after six months. The monthly amount for the non-employed category was not verified. NT$ 826 appears in news as the premium for an unemployed person aged 65 or over; do not apply it to this couple.
- **Singapore.** Not researched. The zone tables give Singapore as zone 3 at AXA and Generali and zone 2 at Globality (USD 2,562, 769 and 1,987 a month for the couple).
- **Costa Rica, CAJA (CCSS).** Contribution is a percentage of declared income. The only scale I found is a lawyer's page dated 2017: 5.18% to 10.69% of monthly income in four USD bands for foreign residents, health only; the example of a base of CRC 604,260 at 6.24% gives CRC 37,706 a month. Out of date; the current CCSS table was not found. Uncertain enough that I would not use it.
- **Mexico, IMSS voluntary scheme (Seguro de Salud para la Familia).** Annual fee per person, by age group, in a table published December 2025: age 40 to 49 MXN 13,800, 50 to 59 MXN 14,250 (cached press copy; the IMSS page needs JavaScript). Two 45-year-olds: MXN 27,600 a year (about MXN 2,300 a month). Press reports of 2026 figures (0 to 19: MXN 9,300 against 8,900; age 35: MXN 12,350 against 11,850) imply about +4% for 2026. Press notes pre-existing conditions are excluded.
- **Uruguay, mutualistas.** FONASA capita (the state's monthly payment per member), July 2026 (official, cached): ages 45 to 64, men UYU 3,727.95 and women UYU 4,559.55. A man and a woman: UYU 8,287.50 a month. This is the best official proxy; individual affiliation fees are set by each mutualista, capped to rise by at most 2.13% in July 2026, and I did not find a retail fee list.

## What I think the brief has slightly wrong

- "Worldwide excluding USA" is not sold to US residents in the Generali and Globality tables (zone 1 gets worldwide cover only), so the US needs a different row. That is how the US figures are built here.
- "A rate table plus the insurer's zone list gives a figure for every country by one consistent method" holds, but the tables are 2025 and one insurer's whole table sits about three times above the other two. The label on the page matters more than the number.

## Not found or not done

- No public rate table from Cigna Global, Allianz Care, Bupa Global, William Russell, Now Health, April International, GeoBlue or Aetna. IPMIcompare, expatriates-health-insurance.com and others report the same: those insurers show prices only through quote tools.
- No Europe cross-check: `data/tables/` had only the US health table when I looked.
- Local-option premiums for Qatar, Saudi Arabia, Australia, Korea, Taiwan, Costa Rica and Singapore are unverified or missing, as flagged above.
