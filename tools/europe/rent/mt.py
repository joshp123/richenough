"""Malta: Housing Authority's Rent Calculator, median rent of new two-bed flat contracts, H1 2026.

The Housing Authority's register holds every private residential lease in Malta (registration is compulsory). Its
Rent Calculator (a public Shiny web app) gives, from contracts that started in a half year, the lower quartile, median,
mean and upper quartile of the monthly rent by locality or by the Authority's six regions, per property type and bedroom
count; cells with fewer than 15 registrations are suppressed ("Scarce Data").

The app has no download. We read it the way the page does, over the Shiny websocket, once, and keep the answers in
cache/mt-ha-rent-calculator/two-bed-flat-2026H1.json (refresh with fetch(), which needs `websocket-client`).

Malta (MT001): Valletta has too few contracts, so we use the Authority's Southern Harbour region, which contains
Valletta. Gozo (MT002): Victoria (Rabat, Ghawdex) locality.
"""

import json
import re
import time

import common as c

SOURCE_ID = "mt-housing-authority-rents"
URL = "https://housingauthority.shinyapps.io/MaltaRentCalculator/"
CACHE_NAME = "two-bed-flat-2026H1.json"
PERIOD = "2026-H1"

SOURCES = [c.source(
    SOURCE_ID, "Malta Housing Authority",
    "Rent Calculator: rents registered with the Housing Authority, H1 2026 (apartment/flat, 2 bedrooms)",
    URL, "Free to read; no licence stated (public body)", PERIOD,
    "Median monthly rent of private residential leases that started in H1 2026 and were registered with the Housing "
    "Authority, by locality or region. Agreed rents of new contracts, no dwelling size in m2.")]


def fetch() -> dict:
    """Query the Rent Calculator for every region and locality (2-bed flat). Needs websocket-client and requests."""
    import html
    import requests
    import websocket

    page = requests.get(URL, headers={"User-Agent": c.USER_AGENT}, timeout=60)
    worker = re.search(r"_w_[0-9a-f]+", page.text).group(0)
    cookies = "; ".join(f"{k}={v}" for k, v in page.cookies.items())

    def options(select_id):
        block = page.text.split(f'id="{select_id}"')[1].split("</select>")[0]
        return [html.unescape(x) for x in re.findall(r'<option value="([^"]*)"', block)]

    ws = websocket.create_connection(
        f"wss://housingauthority.shinyapps.io/MaltaRentCalculator/{worker}/websocket/",
        header=[f"Cookie: {cookies}", f"User-Agent: {c.USER_AGENT}"], origin="https://housingauthority.shinyapps.io", timeout=30)
    init = {f".clientdata_output_{o}_hidden": False for o in ("q1_rent", "median_rent", "average_rent", "q3_rent")}
    init.update({".clientdata_pixelratio": 1, ".clientdata_url_protocol": "https:",
                 ".clientdata_url_hostname": "housingauthority.shinyapps.io", ".clientdata_url_port": "",
                 ".clientdata_url_pathname": "/MaltaRentCalculator/", ".clientdata_url_search": "",
                 ".clientdata_url_hash_initial": "", ".clientdata_singletons": "", ".clientdata_allowDataUriScheme": True})
    state = {"basis": "Locality", "Region": "Northern Harbour", "Locality": options("Locality")[0],
             "property_type": "Apartment (Flat)", "bedrooms_two": "2", "bedrooms_three": "2"}
    ws.send(json.dumps({"method": "init", "data": {**init, **state}}))

    def read(seconds):
        values, end = {}, time.time() + seconds
        ws.settimeout(1.5)
        while time.time() < end:
            try:
                message = json.loads(ws.recv())
            except Exception:
                if values:
                    break
                continue
            for name, v in message.get("values", {}).items():
                if isinstance(v, dict) and v.get("html"):
                    text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", v["html"])).strip()
                    m = re.match(r"€\s*([\d,]+)", text)
                    values[name] = int(m.group(1).replace(",", "")) if m else None
        return values

    def ask(update):
        ws.send(json.dumps({"method": "update", "data": update}))
        return read(5)

    out = {"retrieved": c.today(), "period": PERIOD, "query": "Apartment (Flat), 2 bedrooms", "regions": {}, "localities": {}}
    read(8)
    for region in options("Region"):
        out["regions"][region] = ask({"basis": "Region", "Region": region, "bedrooms_three": "2"})
    for locality in options("Locality"):
        out["localities"][locality] = ask({"basis": "Locality", "Locality": locality, "bedrooms_three": "2"})
    return out


def rows():
    path = c.CACHE / SOURCE_ID / CACHE_NAME
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(fetch(), indent=1))
    data = json.loads(path.read_text())
    out = []
    south = data["regions"]["Southern Harbour"]
    out.append(c.row(
        c.place("MT001"), south["median_rent"], "EUR", "per_month", PERIOD, c.place("MT001"), SOURCE_ID,
        f"Median rent of two-bed flats whose lease started in H1 2026, Housing Authority 'Southern Harbour' region "
        f"(contains Valletta); Valletta alone has under 15 contracts. Quartiles "
        f"{south['q1_rent']} to {south['q3_rent']}. Island-wide it is not published; Northern Harbour (Sliema, St Julian's) "
        f"is {data['regions']['Northern Harbour']['median_rent']}. Registered contract rents, no size in m2."))
    victoria = data["localities"]["IR-RABAT, GHAWDEX"]
    out.append(c.row(
        c.place("MT002"), victoria["median_rent"], "EUR", "per_month", PERIOD, c.city_code("MT", "Victoria"), SOURCE_ID,
        f"Median rent of two-bed flats whose lease started in H1 2026 in Victoria (Rabat, Gozo); quartiles "
        f"{victoria['q1_rent']} to {victoria['q3_rent']}. Gozo and Comino as a whole: {data['regions']['Gozo and Comino']['median_rent']}."))
    return out
