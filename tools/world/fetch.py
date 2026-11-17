"""Download the raw files the world tables are built from into cache/<source_id>/.

Run: python3 -I tools/world/fetch.py [--refresh]
Every download needs no account or key. Existing files are kept unless --refresh is given.
"""

import pathlib
import sys
import subprocess

REPO = pathlib.Path(__file__).resolve().parents[2]
CACHE = REPO / "cache"
REFRESH = "--refresh" in sys.argv

IMF = "https://api.imf.org/external/sdmx/2.1/data"
WB = "https://api.worldbank.org/v2"

# ICP 2021 headings used here: household consumption without housing (the everyday price level),
# household consumption as a whole, and the headings the car and housekeeper estimates need.
ICP_SERIES = [
    "9260000",  # individual consumption expenditure by households, without housing
    "9100000",  # households and NPISHs final consumption expenditure
    "9020000",  # actual individual consumption
    "1101000", "1102000", "1103000", "1105000", "1107000", "1107100", "1107300", "1108000", "1111000",
    "9060000", "9080000", "9110000", "9120000", "9140000",
]
ICP_CLASSIFICATIONS = ["PPPGlob", "CN", "PP.CD", "PX.WL", "EXR"]

WDI_INDICATORS = [
    "PA.NUS.PRVT.PP",  # PPP conversion factor, private consumption (LCU per international $), incl. World Bank extrapolations
    "PA.NUS.FCRF",  # official exchange rate, LCU per US$, period average
    "NY.GDP.PCAP.CD",  # GDP per capita, current US$
    "NY.GDP.PCAP.PP.CD",  # GDP per capita, PPP
    "SP.POP.TOTL",
]

ILOSTAT = {
    # mean hourly earnings of employees by sex and economic activity (ISIC section T: households as employers)
    "EAR_EHRA_SEX_ECO_NB_A": "Average hourly earnings of employees by sex and economic activity (local currency)",
    # mean hourly earnings by sex and occupation (ISCO-08 major group 9: elementary occupations)
    "EAR_EHRA_SEX_OCU_NB_A": "Average hourly earnings of employees by sex and occupation (local currency)",
    # mean monthly earnings by economic activity and by occupation, for countries without hourly figures
    "EAR_EMTA_SEX_ECO_NB_A": "Average monthly earnings of employees by sex and economic activity (local currency)",
    "EAR_EMTA_SEX_OCU_NB_A": "Average monthly earnings of employees by sex and occupation (local currency)",
    # weekly hours actually worked per employed person by economic activity
    "HOW_TEMP_SEX_ECO_NB_A": "Average weekly hours actually worked per employed person by sex and economic activity",
    # statutory monthly minimum wage
    "EAR_INEE_NOC_NB_A": "Monthly minimum wage (local currency)",
}


def get(url: str, dest: pathlib.Path, headers: dict | None = None) -> pathlib.Path:
    """Download with curl: Python's urllib stalls on the World Bank API from this machine, curl does not."""
    if dest.exists() and dest.stat().st_size > 0 and not REFRESH:
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    command = ["curl", "--fail", "--silent", "--show-error", "--location", "--retry", "3", "--retry-all-errors", "--retry-delay", "20", "--max-time", "600", "-o", str(tmp), url]
    for name, value in (headers or {}).items():
        command[1:1] = ["-H", f"{name}: {value}"]
    subprocess.run(command, check=True)
    tmp.replace(dest)
    print(f"fetched {dest.relative_to(REPO)} ({dest.stat().st_size:,} bytes)")
    return dest


def fetch_icp() -> None:
    """The World Bank API often answers 502 for minutes at a time; a heading that fails is reported and retried next run."""
    out = CACHE / "wb-icp-2021"
    for series in ICP_SERIES:
        url = (
            f"{WB}/sources/90/country/all/series/{series}/classification/{';'.join(ICP_CLASSIFICATIONS)}"
            f"/time/YR2021/data?format=json&per_page=5000"
        )
        try:
            get(url, out / f"{series}.json")
        except subprocess.CalledProcessError:
            print(f"FAILED ICP heading {series}; run fetch.py again later")


def fetch_wdi() -> None:
    out = CACHE / "wb-wdi"
    for indicator in WDI_INDICATORS:
        try:
            get(f"{WB}/country/all/indicator/{indicator}?format=json&per_page=20000&date=2015:2026", out / f"{indicator}.json")
        except subprocess.CalledProcessError:
            print(f"FAILED WDI {indicator}; run fetch.py again later")


def fetch_eurostat() -> None:
    base = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"
    get(f"{base}/prc_colc_ext?format=JSON&lang=en", CACHE / "eurostat-colc-ext" / "prc_colc_ext.json")


def fetch_imf() -> None:
    get(f"{IMF}/IMF.STA,CPI/*.CPI._T.IX.M?startPeriod=2020-01", CACHE / "imf-cpi" / "cpi-monthly.xml")
    get(f"{IMF}/IMF.STA,CPI/*.CPI._T.IX.Q?startPeriod=2020-Q1", CACHE / "imf-cpi" / "cpi-quarterly.xml")
    get(f"{IMF}/IMF.STA,ER/*.XDC_USD.PA_RT.M?startPeriod=2020-01", CACHE / "imf-er" / "xdc-usd-monthly-average.xml")
    get(f"{IMF}/IMF.STA,ER/*.XDC_USD.EOP_RT.M?startPeriod=2025-01", CACHE / "imf-er" / "xdc-usd-month-end.xml")
    for indicator in ["PCPI", "NGDPDPC", "PPPEX"]:
        get(f"{IMF}/IMF.RES,WEO/*.{indicator}.A?startPeriod=2019", CACHE / "imf-weo" / f"{indicator}.xml")


def fetch_treasury() -> None:
    base = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/od/rates_of_exchange"
    url = f"{base}?filter=record_date:gte:2025-01-01&sort=-record_date&page%5Bsize%5D=10000"
    get(url, CACHE / "us-treasury-rates-of-exchange" / "since-2025.json")


def fetch_ecb() -> None:
    get("https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.zip", CACHE / "ecb-euro-reference-rates" / "eurofxref-hist.zip")


def fetch_ilostat() -> None:
    for indicator in ILOSTAT:
        get(f"https://rplumber.ilo.org/data/indicator/?id={indicator}&format=.csv.gz", CACHE / "ilostat" / f"{indicator}.csv.gz")


def main() -> None:
    for step in [fetch_imf, fetch_treasury, fetch_ecb, fetch_eurostat, fetch_ilostat, fetch_icp, fetch_wdi]:
        step()


if __name__ == "__main__":
    main()
