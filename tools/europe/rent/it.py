"""Italy: Agenzia delle Entrate (OMI) statistics on new residential lets registered in 2025, by comune.

Every new lease must be registered with the tax office, so these are agreed rents of new contracts (not asking
rents, not the stock). The Agenzia publishes, per comune with at least 5 lets, the number of whole dwellings let,
their cadastral floor area and the annual rent. We take the free-market long-let segment (ORD_L: contracts of 3+
years not on the tax-advantaged "canone concordato" scheme in high-tension municipalities), divide total rent by
total area for EUR/m2/month, price a 75 m2 two-bed, and scale by MARKET for under-declaration. Main town = the province's capoluogo (the most populous
where a NUTS 3 region holds several); where it has fewer than MIN_LETS lets, the whole province's ORD_L lets.
"""

import common as c
import pandas as pd

SOURCE_ID = "ade-it-locazioni"
ISTAT_ID = "istat-it-comuni"
URL = ("https://www.agenziaentrate.gov.it/portale/documents/20143/1144826/Locazioni_Abitazioni_2018_2025.csv/"
       "9cdb4279-6e19-77b2-f598-153c65f9085e?t=1779375828")
ISTAT_URL = "https://www.istat.it/storage/codici-unita-amministrative/Elenco-comuni-italiani.csv"
PERIOD = "2025"
MIN_LETS = 50  # below this the town's mean is too noisy; use the province
# Registered rents are under-declared to the tax office. Against portals' asking rents per m2 they run at 0.64 in the
# median of 31 capoluoghi (Immobiliare.it) and 0.70 to 0.78 in Milano, Roma and Bologna (Idealista, October 2026).
# Agreed rents elsewhere in Europe run about 10% below asking (Spain's registers, Ireland's RTB), so 1.25 brings the
# big cities to about 0.9 of asking and leaves the median town at about 0.8: a deliberately cautious correction.
MARKET = 1.25

SOURCES = [
    c.source(SOURCE_ID, "Agenzia delle Entrate, Osservatorio del Mercato Immobiliare (OMI)",
             "Locazioni immobiliari: abitazioni oggetto di nuova locazione con contratto registrato, per comune, "
             "2018-2025 (Locazioni_Abitazioni_2018_2025.csv) and Nota metodologica locazioni (3 June 2026)",
             "https://www.agenziaentrate.gov.it/portale/locazioni-immobiliari",
             "CC BY 4.0 (OMI services; cite 'Agenzia delle Entrate - OMI')", PERIOD,
             "Agreed annual rent and cadastral floor area of whole dwellings newly let on registered contracts; "
             "segment ORD_L (free-market lets of 3+ years)."),
    c.source(ISTAT_ID, "ISTAT", "Elenco dei comuni italiani (cadastral code, ISTAT code, NUTS 2024, capoluogo flag)",
             ISTAT_URL, "CC BY 4.0", "2026", "Maps the Agenzia's cadastral comune codes to NUTS 3 2024."),
]


def _load():
    d = pd.read_csv(c.fetch(SOURCE_ID, URL, "comuni.csv"), sep=";", decimal=",", encoding="latin1",
                    dtype={"COD_NAZ": str}, keep_default_na=False, na_values=["nd"])
    d.columns = ["anno", "seg", "prov", "cod", "comune", "cap", "lets", "portions", "m2", "rent", "iml"]
    d = d[(d["anno"] == int(PERIOD)) & (d["seg"] == "ORD_L")]
    e = pd.read_csv(c.fetch(ISTAT_ID, ISTAT_URL, "elenco.csv"), sep=";", encoding="latin1", dtype=str,
                    keep_default_na=False)
    e = e.rename(columns={"Codice Catastale del comune": "cod", "Codice NUTS3 2024": "nuts3",
                          "Codice Comune formato alfanumerico": "istat", "Denominazione in italiano": "name",
                          "Flag Comune capoluogo di provincia/città metropolitana/libero consorzio": "capo",
                          "Sigla automobilistica": "sigla"})
    return d, e[["cod", "nuts3", "istat", "name", "capo", "sigla"]]


def rows():
    d, e = _load()
    lau = c.lau()
    pop = dict(zip(lau[lau["country"] == "IT"]["lau_code"], lau[lau["country"] == "IT"]["population"]))
    e["pop"] = e["istat"].map(pop).fillna(0)
    sigla_nuts = e.groupby("sigla")["nuts3"].agg(lambda s: s.mode()[0])

    # Comuni below the Agenzia's 5-let threshold are published as one "other comuni" row per province.
    other = d["comune"].astype(str).str.startswith("_TOT")
    d_other = d[other].assign(nuts3=lambda t: t["prov"].map(sigla_nuts))
    d_comuni = d[~other].merge(e, on="cod", how="left")
    d_comuni = d_comuni[d_comuni["nuts3"].notna()]
    allrows = pd.concat([d_comuni, d_other], ignore_index=True)
    by_region = allrows.groupby("nuts3")[["lets", "m2", "rent"]].sum()

    out = []
    for nuts3 in c.regions_in("IT"):
        town = None
        cands = e[(e["nuts3"] == nuts3) & (e["capo"] == "1")].sort_values("pop", ascending=False)
        if len(cands):
            town = cands.iloc[0]
        else:
            ranked = c.main_towns(nuts3)
            hit = e[(e["nuts3"] == nuts3) & (e["name"] == ranked.iloc[0]["name"])]
            town = hit.iloc[0] if len(hit) else None
        t = d_comuni[d_comuni["cod"] == town["cod"]] if town is not None else d_comuni.iloc[0:0]
        if len(t) and t.iloc[0]["lets"] >= MIN_LETS:
            r = t.iloc[0]
            per_m2 = r["rent"] / r["m2"] / 12
            measured = c.city_code("IT", town["name"]) or c.place(nuts3)
            note = (f"Mean agreed rent of {int(r['lets'])} new free-market long lets (ORD_L) registered in 2025 in "
                    f"{town['name']}: {per_m2:.2f} EUR/m2/month x 75 m2. Average let {r['m2'] / r['lets']:.0f} m2 "
                    f"cadastral. Registered rents, not asking rents.")
        else:
            g = by_region.loc[nuts3]
            per_m2 = g["rent"] / g["m2"] / 12
            measured = c.place(nuts3)
            note = (f"Too few lets in the main town ({town['name'] if town is not None else 'n/a'}); mean agreed rent "
                    f"of {int(g['lets'])} new free-market long lets (ORD_L) registered in 2025 across the whole "
                    f"province: {per_m2:.2f} EUR/m2/month x 75 m2. Registered rents, not asking rents.")
        note += (f" Scaled by {MARKET} for under-declaration of registered rents (registered rents run at about 0.64 "
                 f"of asking rents in the median capoluogo and 0.70 to 0.78 in Milano, Roma and Bologna).")
        out.append(c.row(c.place(nuts3), round(per_m2 * c.TWO_BED_M2 * MARKET, 2), "EUR", "per_month", PERIOD, measured,
                         SOURCE_ID, note))
    return out
