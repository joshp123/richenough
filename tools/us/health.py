"""Join CMS plan, premium and geographic files for unsubsidised age-45 coverage."""
from collections import defaultdict
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import csv
import io
import re
from statistics import median
import unicodedata
from zipfile import ZipFile

from bs4 import BeautifulSoup
from openpyxl import load_workbook

from build import CENSUS, CMS, GRA, PR_PLAN, SBE, fetch, pdf_text


def normalise(value):
    text = unicodedata.normalize('NFKD', value.lower())
    return re.sub('[^a-z0-9]+', '', text)


@contextmanager
def records(path, kind):
    with ZipFile(path) as archive:
        # State names begin with a two-letter abbreviation. Federal files use
        # descriptive names with an underscore before PUF.
        pattern = {
            'rate': r'(^Rate_PUF|^[A-Z]{2}Rates\d)',
            'plan': r'(^Plan_Attributes_PUF|^[A-Z]{2}Plans\d)',
            'service-area': r'(^Service_Area_PUF|^[A-Z]{2}ServiceAreas\d)',
        }[kind]
        name, = [name for name in archive.namelist()
                 if name.lower().endswith('.csv') and re.match(pattern, Path(name).name, re.I)]
        with io.TextIOWrapper(archive.open(name), encoding='utf-8-sig', errors='replace') as contents:
            yield ({normalise(k): (v or '').strip() for k, v in row.items() if k}
                   for row in csv.DictReader(contents))


def county_rating_areas(counties):
    by_name = {}
    states = set()
    for fips, (state, name) in counties.items():
        states.add(state)
        name = re.sub(r' (County|Parish|Municipio|Borough|Census Area|Planning Region)$', '', name)
        by_name[(state, normalise(name))] = fips
        by_name[(state, normalise(name + ' City'))] = fips

    zcta_path = fetch('us-geography', 'zcta-county.txt',
                      CENSUS + '/geo/docs/maps-data/data/rel2020/zcta520/tab20_zcta520_county20_natl.txt')
    prefixes = defaultdict(set)
    with zcta_path.open() as file:
        for row in csv.DictReader(file, delimiter='|'):
            fips = row['GEOID_COUNTY_20']
            if int(row['AREALAND_PART']) > 0:
                prefixes[(fips[:2], row['GEOID_ZCTA5_20'][:3])].add(fips)
    state_codes = {state: fips[:2] for fips, (state, _) in counties.items()}

    def get(state):
        path = fetch('us-aca-areas', state + '.html', GRA + state.lower() + '-gra')
        return state, BeautifulSoup(path.read_text(), 'html.parser')

    areas = defaultdict(set)
    with ThreadPoolExecutor(max_workers=8) as pool:
        for state, page in pool.map(get, sorted(states - {'PR', 'DC'})):
            for row in page.select('table tr'):
                cells = [cell.get_text(' ', strip=True) for cell in row.find_all('td')]
                if len(cells) < 2:
                    continue
                match = re.fullmatch(r'Rating Area\s*(\d+)', cells[0], re.I)
                if not match:
                    continue
                rating = int(match[1])
                county_name = re.sub(r'\s*\(.*', '', cells[1])
                county_name = re.sub(r' (County|Parish)$', '', county_name)
                county = by_name.get((state, normalise(county_name)))
                if county:
                    areas[county].add(rating)
                elif len(cells) >= 3:
                    for prefix in re.findall(r'\b\d{3}\b', cells[2]):
                        for fips in prefixes[(state_codes[state], prefix)]:
                            if fips in counties:
                                areas[fips].add(rating)
    areas['11001'].add(1)
    return areas


def load_market(files, counties, rating_areas):
    by_state = defaultdict(set)
    for fips, (state, _) in counties.items():
        by_state[state].add(fips)

    services = defaultdict(dict)
    with records(files['service-area'], 'service-area') as rows:
        for row in rows:
            if (row.get('marketcoverage') != 'Individual'
                    or 'Yes' in (row.get('dentalonlyplan'), row.get('dentalplanonly'))):
                continue
            state = row['statecode']
            areas = by_state[state] if row['coverentirestate'].lower() in ('true', 'yes') else set()
            if not areas:
                match = re.search(r'\b\d{5}\b', row['county'])
                if match and match[0] in counties:
                    areas = {match[0]}
            key = (state, row['issuerid'], normalise(row['serviceareaid']))
            for fips in areas:
                services[key][fips] = row['partialcounty'].lower() in ('true', 'yes')

    eligible = {}
    with records(files['plan'], 'plan') as rows:
        for row in rows:
            kind = row.get('qhpnonqhptypeid', '').lower()
            if (row['marketcoverage'] != 'Individual' or 'silver' not in row['metallevel'].lower()
                    or kind not in {'both', 'on the exchange', 'on-exchange', 'qhp'}):
                continue
            plan = row['standardcomponentid']
            key = (row['statecode'], row['issuerid'], normalise(row['serviceareaid']))
            eligible[plan] = services[key]

    plan_rates = defaultdict(dict)
    with records(files['rate'], 'rate') as rows:
        for row in rows:
            plan = row['planid']
            if plan not in eligible:
                continue
            date = row['rateeffectivedate']
            try:
                year = row['businessyear']
                january = date in {f'{year}-01-01', f'1/1/{year}', f'01/01/{year}', f'01-01-{year}'}
                if date and not january:
                    continue
                rating = int(re.search(r'\d+', row['ratingareaid'])[0])
                age = row['age'].lower()
                if age == '45':
                    if row['tobacco'].lower() not in {'no preference', 'tobacco user/non-tobacco user',
                                                         'non-tobacco user', ''}:
                        continue
                    amount = 2 * float(row['individualrate'])
                elif age in {'', 'family option'} and row.get('couple'):
                    amount = float(row['couple'])
                else:
                    continue
            except (TypeError, ValueError):
                continue
            if 0 < amount < 50_000:
                plan_rates[plan][rating] = amount

    local = defaultdict(dict)
    state_rates = defaultdict(list)
    for plan, rated in plan_rates.items():
        state = plan[5:7]
        state_rates[state].extend(rated.values())
        for fips, partial in eligible[plan].items():
            areas = rating_areas[fips] & rated.keys()
            if areas:
                local[fips][plan] = (median(rated[area] for area in areas), partial)
            elif len(set(rated.values())) == 1 and not rating_areas[fips]:
                local[fips][plan] = (next(iter(rated.values())), partial)
    return local, state_rates


def oregon_premiums(counties):
    url = 'https://dfr.oregon.gov/healthrates/Documents/2027-plan-comparison-table.xlsx'
    path = fetch('us-or-health', '2027.xlsx', url)
    with path.open('rb') as file:
        workbook = load_workbook(file, read_only=True, data_only=True)
        sheet = workbook['Plan Information']
        header, *plans = sheet.iter_rows(min_row=4, values_only=True)
        county_amounts = {}
        for column, name in enumerate(header[104:], start=104):
            ages_40 = [row[column] for row in plans if row[4] in {'Both', 'On Exchange'}
                       and row[5] == 'Silver' and isinstance(row[column], (float, int))]
            # Oregon uses the federal age curve. The regulator quotes age 40.
            county_amounts[name] = median(ages_40) * 2 * 1.444 / 1.278
        workbook.close()
    return {fips: county_amounts[name.removesuffix(' County')]
            for fips, (state, name) in counties.items() if state == 'OR'}


def premiums(counties):
    areas = county_rating_areas(counties)
    federal = {}
    for kind in ('rate', 'plan', 'service-area'):
        filename = 'plan-attributes' if kind == 'plan' else kind
        federal[kind] = fetch('us-cms-ffm', filename + '.zip',
                              f'https://download.cms.gov/marketplace-puf/2027/{filename}-puf.zip')
    federal_counties, federal_rates = load_market(federal, counties, areas)
    state_counties, state_rates = {}, {}

    def load_state(state):
        filename = SBE[state] + '.zip'
        archive = fetch('us-cms-sbe', filename, CMS + '/files/zip/' + filename)
        return load_market(dict.fromkeys(federal, archive), counties, areas)

    with ThreadPoolExecutor(max_workers=6) as pool:
        for local, statewide in pool.map(load_state, SBE):
            state_counties.update(local)
            state_rates.update(statewide)

    document = pdf_text(fetch('us-pr-health', 'triples.pdf', PR_PLAN))
    match = re.search(r'^.*?Tobacco User/Non-Tobacco User\s+45\s+([\d,.]+)', document, re.MULTILINE)
    if not match:
        raise ValueError('Missing Puerto Rico age-45 rate')
    pr_amount = 2 * float(match[1].replace(',', ''))

    oregon = oregon_premiums(counties)
    # State exchange's 2027 Silver 70 comparison PDF, COUPLE rows.
    vermont = median([3076.66, 3192.90, 3037.10, 2986.14, 2598.26, 2652.82, 2626.66, 2752.74])
    result = {}
    for fips, (state, _) in counties.items():
        if state == 'PR':
            result[fips] = (pr_amount, '2027', 'US-PR', 'us-pr-health',
                            'Triple-S Directo Plata, two individual age-45 non-tobacco rates')
            continue
        if state == 'OR':
            result[fips] = (oregon[fips], '2027', f'US-{fips}', 'us-or-health',
                            'Median of on-exchange Silver plans, state age-40 rates adjusted to two age-45 adults')
            continue
        if state == 'VT':
            result[fips] = (vermont, '2027', 'US-VT', 'us-vt-health',
                            'Median of statewide unsubsidised Silver couple rates; Vermont uses community rating')
            continue
        markets = [
            (federal_counties, federal_rates, 'us-cms-ffm', '2027'),
            (state_counties, state_rates, 'us-cms-sbe', '2026'),
        ]
        for local, _, source, year in markets:
            if fips in local:
                plans = local[fips].values()
                all_county = [amount for amount, partial in plans if not partial]
                selected = all_county or [amount for amount, _ in plans]
                note = 'Median of individual on-exchange Silver plans, full premium for two age-45 non-smokers'
                if not all_county:
                    note += '; available in part of the county'
                result[fips] = (median(selected), year, f'US-{fips}', source, note)
                break
        else:
            for _, rates, source, year in markets:
                if rates.get(state):
                    result[fips] = (median(rates[state]), year, f'US-{state}', source,
                                    'State median across Silver plan rating areas; county match unresolved')
                    break
    return result
