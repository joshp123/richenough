#!/usr/bin/env python3
"""Rebuild US spending tables. Requires openpyxl, beautifulsoup4 and pdftotext."""
import csv
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
import io
import json
from math import hypot, isfinite
from pathlib import Path
import re
import shutil
import subprocess
from unicodedata import normalize
from urllib.request import Request, urlopen
from zipfile import ZipFile

from bs4 import BeautifulSoup
from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / 'cache'
TABLES = ROOT / 'data/tables'
CENSUS = 'https://www2.census.gov'
CMS = 'https://www.cms.gov'
GRA = CMS + '/cciio/programs-and-initiatives/health-insurance-market-reforms/'
SBE = {
    'CA': 'californiasbpuf2026', 'CO': 'coloradosbepuf2026',
    'CT': 'connecticutsbepuf2026', 'DC': 'districtofcolumbiapuf2026',
    'GA': 'georgiasbepuf2026', 'ID': 'idahosbepuf2026',
    'IL': 'illinois-sbe-qhp-puf', 'KY': 'kentuckysbepuf2026',
    'MA': 'massachusettssbepuf2026', 'MD': 'marylandsbepuf2026',
    'ME': 'mainesbepuf2026', 'MN': 'minnesotasbepuf2026',
    'NJ': 'newjerseysbepuf2026', 'NM': 'newmexicosbepuf2026',
    'NV': 'nevadasbepuf2026', 'NY': 'newyorksbepuf2026',
    'PA': 'pennsylvaniasbepuf2026', 'RI': 'rhodeislandsbepuf2026',
    'VA': 'virginiasbepuf2026', 'WA': 'washingtonsbepuf2026',
}
PR_PLAN = ('https://docs.pr.gov/files/OCS/Seguros_Salud/Planes%20en%20Cumplimiento/'
           '2027/Cubiertas%20Individuales/Triple-S%20Salud%2C%20Inc/Triple-S%20Directo%20Plata/Tarifas.pdf')
AAA = 'https://newsroom.aaa.com/wp-content/uploads/2026/09/8-YDC-Brochure_2026-1.pdf'


def fetch(source, name, url, data=None):
    path = CACHE / source / name
    if not path.is_file() or path.stat().st_size == 0:
        path.parent.mkdir(parents=True, exist_ok=True)
        request = Request(url, data, {'User-Agent': 'Enough data rebuild', 'Content-Type': 'application/json'})
        temporary = path.with_suffix(path.suffix + '.part')
        try:
            with urlopen(request, timeout=60) as response, temporary.open('wb') as output:
                shutil.copyfileobj(response, output)
            temporary.replace(path)
        finally:
            temporary.unlink(missing_ok=True)
    return path


@contextmanager
def zipped_rows(path, member_prefix='', delimiter=','):
    with ZipFile(path) as archive:
        name, = [name for name in archive.namelist()
                 if Path(name).name.lower().startswith(member_prefix.lower())
                 and name.lower().endswith(('.txt', '.csv'))]
        with io.TextIOWrapper(archive.open(name), encoding='utf-8-sig', errors='replace') as contents:
            yield csv.DictReader(contents, delimiter=delimiter)


def pdf_text(path):
    return subprocess.check_output(['pdftotext', '-layout', str(path), '-'], text=True)


def write_table(component, unit, values, counties):
    columns = ['place_code', 'amount', 'currency', 'unit', 'period', 'measured_for', 'source_id', 'note']
    TABLES.mkdir(parents=True, exist_ok=True)
    if values.keys() != counties.keys():
        raise ValueError(f'{component} county coverage mismatch: {values.keys() ^ counties.keys()}')
    with (TABLES / f'{component}.us.csv').open('w', newline='') as file:
        rows = csv.writer(file, lineterminator='\n')
        rows.writerow(columns)
        for fips, (amount, period, area, source, note) in sorted(values.items()):
            if not isfinite(amount) or amount <= 0:
                raise ValueError(f'{component} value for {fips}: {amount}')
            rows.writerow([f'US-{fips}', round(amount, 2), 'USD', unit, period, area, source, note])
    county_count = sum(area == f'US-{fips}' for fips, (_, _, area, _, _) in values.items())
    print(f'{component}: {county_count} county, {len(values) - county_count} other reporting areas')


def geography():
    gazetteer = fetch('us-geography', 'gazetteer.zip',
                      CENSUS + '/geo/docs/maps-data/data/gazetteer/2026_Gazetteer/2026_Gaz_counties_national.zip')
    with zipped_rows(gazetteer, delimiter='|') as rows:
        counties = {r['GEOID']: (r['USPS'], r['NAME']) for r in rows}
    assert len(counties) == 3222
    workbook = fetch('us-geography', 'cbsa.xlsx',
                     CENSUS + '/programs-surveys/metro-micro/geographies/reference-files/2023/delineation-files/list1_2023.xlsx')
    sheet = load_workbook(workbook, read_only=True).active
    metros = {}
    for row in sheet.values:
        cbsa, _, _, name, kind, _, _, _, _, state, county, *_ = row
        if kind == 'Metropolitan Statistical Area':
            fips = f'{int(state):02d}{int(county):03d}'
            metros[fips] = (str(cbsa), name)
    return counties, metros


def market_rent(counties):
    def lookup_name(name):
        return re.sub(r'[^a-z0-9]', '', normalize('NFKD', name).casefold())

    path = fetch('us-census-places', 'sub-est2025.csv', CENSUS +
                 '/programs-surveys/popest/datasets/2020-2025/cities/totals/sub-est2025.csv')
    main_places = {}
    with path.open(encoding='latin-1') as file:
        rows = [row for row in csv.DictReader(file) if row['SUMLEV'] in ('157', '061')]
    name_exceptions = {
        'Boise City': 'Boise', 'Urban Honolulu': 'Honolulu',
        'Indianapolis city (balance)': 'Indianapolis',
        'Louisville/Jefferson County metro government (balance)': 'Louisville',
        'Nashville-Davidson metropolitan government (balance)': 'Nashville',
        'Augusta-Richmond County consolidated government (balance)': 'Augusta',
        'Athens-Clarke County unified government (balance)': 'Athens',
        'Lexington-Fayette urban county': 'Lexington',
        'Macon-Bibb County': 'Macon',
    }
    for row in rows:
        fips = row['STATE'] + row['COUNTY']
        if fips not in counties or row['NAME'].startswith('Balance of '):
            continue
        population = int(row['POPESTIMATE2025'])
        if population <= main_places.get(fips, (0, ''))[0]:
            continue
        name = re.sub(r' (city|town|village|borough|municipality|CDP)( \(pt\.\))?$', '', row['NAME'])
        main_places[fips] = population, name_exceptions.get(row['NAME'], name_exceptions.get(name, name))

    # Easy Rental reports the five New York City boroughs separately. The
    # Census file calls each borough a part of New York city.
    boroughs = {'36005': 'Bronx', '36047': 'Brooklyn', '36061': 'New York',
                '36081': 'Queens', '36085': 'Staten Island'}
    path = fetch('us-easy-rental', 'rents.csv', 'https://easyrental.ai/data/rents.csv')
    market = {}
    with path.open(encoding='utf-8-sig') as file:
        for row in csv.DictReader(file):
            samples = int(row['samples_2br'])
            if not row['median_2br'] or samples < 100:
                continue
            key = row['state'], lookup_name(row['city'])
            # Keep the better-sampled series when the feed splits punctuation variants.
            if samples > int(market.get(key, {}).get('samples_2br', 0)):
                market[key] = row

    result = {}
    for fips, (_, name) in main_places.items():
        state, _ = counties[fips]
        row = market.get((state, lookup_name(boroughs.get(fips, name))))
        if row is None:
            continue
        area = f'{row["city"]}, {state}'
        if fips in boroughs or fips in ('06075', '11001'):
            area = f'US-{fips}'
        note = (f'Median advertised rent for two bedrooms from {row["samples_2br"]} listings. '
                f'Prices before utilities and concessions. Easy Rental rent data, {row["url"]}')
        result[fips] = (float(row['median_2br']), row['as_of'], area, 'us-easy-rental', note)
    return result


def rent(counties):
    # The ratio adjusts for lease turnover without claiming an observed two-bedroom new-lease median.
    inputs = {}
    for year, duration in [(2025, 1), (2024, 5)]:
        for table in ('b25031', 'b25113'):
            name = f'acsdt{duration}y{year}-{table}.dat'
            old_name = f'{table}-2025.dat' if year == 2025 else f'{table}.dat'
            path = fetch('us-acs-rent', old_name, CENSUS + '/programs-surveys/acs/summary_file/'
                         f'{year}/table-based-SF/data/{duration}YRData/{name}')
            with path.open(encoding='utf-8-sig') as file:
                inputs[year, table] = {r['GEO_ID']: r for r in csv.DictReader(file, delimiter='|')
                                       if r['GEO_ID'].startswith(('0400000US', '0500000US'))}

    def estimate(year, area, table, line):
        row = inputs[year, table].get(area, {})
        prefix = table.upper()
        value, margin = (row.get(f'{prefix}_{kind}{line:03d}', '') for kind in ('E', 'M'))
        if value.isdecimal() and margin.isdecimal() and int(value) > 0:
            return int(value), int(margin) / int(value)
        return None, float('inf')

    result = {}
    for fips, (state, _) in counties.items():
        county_area = f'0500000US{fips}'
        state_area = f'0400000US{fips[:2]}'
        for area, year, code in [
            (county_area, 2025, f'US-{fips}'), (county_area, 2024, f'US-{fips}'),
            (state_area, 2025, f'US-{state}'), (state_area, 2024, f'US-{state}'),
        ]:
            base, error = estimate(year, area, 'b25031', 4)
            if base is None or error > .50:
                continue
            detail = 'ACS two-bedroom median gross rent, including utilities'
            for ratio_area, label in [(area, 'local'), (state_area, 'statewide')]:
                recent, recent_error = estimate(year, ratio_area, 'b25113', 2)
                all_leases, all_error = estimate(year, ratio_area, 'b25113', 1)
                if hypot(recent_error, all_error) <= .20:
                    base *= recent / all_leases
                    detail += f', adjusted by the {label} recent-mover rent ratio across all unit sizes'
                    break
            period = '2025' if year == 2025 else '2020-2024'
            result[fips] = (base, period, code, 'us-acs-rent', detail)
            break
    result.update(market_rent(counties))
    return result


def regional_prices(counties, metros):
    index = {}
    for filename, table in [('metro', 'MARPP'), ('portion', 'PARPP'), ('state', 'SARPP')]:
        path = fetch('us-bea-rpp', filename + '.zip', f'https://apps.bea.gov/regional/zip/{table}.zip')
        with zipped_rows(path, table + '_') as rows:
            for row in rows:
                if row['LineCode'] in {'2', '4', '5'}:
                    code = row['GeoFIPS'].strip().strip(chr(34))
                    index.setdefault((table, code), {})[row['LineCode']] = float(row['2024'])
    with zipped_rows(CACHE / 'us-bea-rpp/portion.zip', 'PARPP_') as rows:
        portions = {r['GeoFIPS'].strip().strip(chr(34))[:2]: r['GeoFIPS'].strip().strip(chr(34)) for r in rows
                    if 'nonmetropolitan' in (r['GeoName'] or '').lower()}
    result = {}
    for fips, (state, _) in counties.items():
        if state == 'PR':
            # The regulator's scanned 2026-Q2 release, page 1. The benchmark
            # is its 283 participating cities; Puerto Rico has no BEA RPP.
            amount = .4 * 108.4 + .6 * 92.5
            result[fips] = (amount, '2026-Q2', 'San Juan–Bayamón–Caguas urban area', 'us-pr-coli',
                            '40% groceries and 60% miscellaneous goods and services; US reporting cities = 100')
            continue
        metro, metro_name = metros.get(fips, (None, None))
        for key, area in [
            (('MARPP', metro), metro_name),
            (('PARPP', portions.get(fips[:2]) if not metro else None), f'{state} nonmetropolitan area'),
            (('SARPP', fips[:2] + '000'), f'US-{state}'),
        ]:
            values = index.get(key, {})
            if values.get('2', 0) > 0 and values.get('5', 0) > 0:
                break
        else:
            raise ValueError(f'No usable BEA RPP for {fips}')
        # Fixed national budget shares for goods and non-housing, non-utility services.
        national = index['SARPP', '00000']
        amount = .4 * 100 * values['2'] / national['2'] + .6 * 100 * values['5'] / national['5']
        result[fips] = (amount, '2024', area, 'us-bea-rpp',
                        '40% goods and 60% other services; housing rents and utilities excluded')
    return result


def wages(counties, metros):
    series = {'OEUS' + (fips[:2] + '00000') + '00000037201208' for fips in counties}
    series |= {'OEUM' + code.zfill(7) + '00000037201208' for code, _ in metros.values()}
    series = sorted(series)

    def query(batch):
        payload = json.dumps({'seriesid': batch, 'startyear': '2025', 'endyear': '2025'}).encode()
        path = fetch('us-bls-oews', batch[0] + '.json',
                     'https://api.bls.gov/publicAPI/v2/timeseries/data/', payload)
        document = json.loads(path.read_text())
        if document['status'] != 'REQUEST_SUCCEEDED':
            path.unlink()
            raise RuntimeError(document)
        return {row['seriesID']: float(row['data'][0]['value'])
                for row in document['Results']['series'] if row['data'] and row['data'][0]['value'] != '-'}

    with ThreadPoolExecutor(max_workers=5) as pool:
        rates = {key: value for batch in pool.map(query, [series[i:i+25] for i in range(0, len(series), 25)])
                 for key, value in batch.items()}
    result = {}
    for fips, (state, _) in counties.items():
        metro, name = metros.get(fips, ('', ''))
        key = 'OEUM' + metro.zfill(7) + '00000037201208'
        if key not in rates:
            key = 'OEUS' + (fips[:2] + '00000') + '00000037201208'
            name = f'US-{state}'
        if key in rates:
            result[fips] = (rates[key], '2025-05', name, 'us-bls-oews',
                            'Median employee pay, maids and housekeeping cleaners (SOC 37-2012)')
    return result


def cars(counties):
    guide = pdf_text(fetch('us-car-aaa', '2026.pdf', AAA))
    sedan = guide.split('Medium Sedan')[-1].split('Medium SUV')[0]

    def gas_sedan_cost(label):
        line = next(line for line in sedan.splitlines() if line.lstrip().startswith(label))
        values = re.findall(r'\$([\d,.]+)', line)
        return float(values[1].replace(',', ''))

    annual = gas_sedan_cost('cost per year')
    national_fuel = gas_sedan_cost('fuel')
    national_insurance = gas_sedan_cost('full-coverage insurance')
    assert (annual, national_fuel, national_insurance) == (10582, 2215, 1704)

    naic_url = 'https://content.naic.org/sites/default/files/2024-adb-average-premium-supplement.pdf'
    naic = pdf_text(fetch('us-car-naic', '2024.pdf', naic_url))
    insurance = {}
    for name, cost in re.findall(r'^([A-Za-z ]+?)\s{2,}([\d,]+\.\d{2})\s+[\d,]+\.\d{2}',
                                  naic.split('Combined Average Premium')[-1], re.M):
        insurance[name.strip()] = float(cost.replace(',', ''))
    national_naic = next(value for name, value in insurance.items() if name.lower().startswith('countrywide'))

    gas = fetch('us-car-gas', 'state-prices.html', 'https://gasprices.aaa.com/state-gas-price-averages/')
    soup = BeautifulSoup(gas.read_text(), 'html.parser')
    date = re.search(r'Price as of\s+(\d+/\d+/\d+)', soup.get_text(' ', strip=True))[1]
    period = datetime.strptime(date, '%m/%d/%y').date().isoformat()
    fuel = {}
    for row in soup.select_one('table').find_all('tr'):
        cells = row.find_all('td')
        if cells:
            fuel[cells[0].get_text(strip=True)] = float(cells[1].get_text(strip=True).strip('$'))
    state_names = {}
    states = fetch('us-bea-rpp', 'state.zip', 'https://apps.bea.gov/regional/zip/SARPP.zip')
    with zipped_rows(states, 'SARPP_') as rows:
        for row in rows:
            if row['LineCode'] == '1' and row['GeoFIPS']:
                state_names[row['GeoFIPS'].strip().strip(chr(34))[:2]] = row['GeoName']
    result = {}
    for fips, (state, _) in counties.items():
        if state == 'PR':
            result[fips] = (annual / 12, '2026', 'US', 'us-car-aaa',
                            'US national gasoline sedan cost at 15,000 miles; Puerto Rico adjustment unavailable')
            continue
        name = state_names[fips[:2]]
        # AAA's 2026 study benchmark used $4.152/gal. Keep the model's mileage
        # and effective fuel economy fixed while substituting the local price.
        estimate = annual - national_fuel - national_insurance
        estimate += national_fuel * fuel[name] / 4.152
        estimate += national_insurance * insurance[name] / national_naic
        result[fips] = (estimate / 12, period, f'US-{state}', 'us-car-aaa',
                        'AAA 2026 gasoline sedan at 15,000 miles; fuel adjusted using AAA state prices and insurance using NAIC 2024')
    return result


def main():
    from health import premiums
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('components', nargs='*', choices=None)
    selection = parser.parse_args().components
    counties, metros = geography()
    components = {
        'rent-two-bedroom': ('per_month', lambda: rent(counties)),
        'price-level-everyday': ('index_us_100', lambda: regional_prices(counties, metros)),
        'housekeeper-wage': ('per_hour', lambda: wages(counties, metros)),
        'car': ('per_month', lambda: cars(counties)),
        'health-cover': ('per_month', lambda: premiums(counties)),
    }
    for component in selection or components:
        unit, build = components[component]
        write_table(component, unit, build(), counties)


if __name__ == '__main__':
    main()
