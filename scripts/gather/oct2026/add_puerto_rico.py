"""
Add Puerto Rico rows to 2026 datasets whose committed raw files include it but whose processing scripts
dropped it. Each value is recomputed from the raw file with the same method used for the states, and the
method is checked by recomputing an existing row and comparing it to the processed file. Safe to re-run.

Usage: python3 -I scripts/gather/oct2026/add_puerto_rico.py
"""
import csv
import collections
import json
import os
import re

import pandas as pd

REPO = os.path.abspath(f"{__file__}/../../../..")
RAW = os.path.join(REPO, 'data', 'raw_data_2026')
OUT = os.path.join(REPO, 'data', 'processed_data_2026')


def acs_rows(path):
    """Rows of a data.census.gov API response as {NAME: {column: value}}"""
    data = json.load(open(path))['response']['data']
    return {r[data[0].index('NAME')]: dict(zip(data[0], r)) for r in data[1:]}


def add_row(key, new, check_state, check):
    """Check the method against an existing row, then add (or replace) the Puerto Rico row"""
    path = os.path.join(OUT, f'{key}.csv')
    d = pd.read_csv(path)
    existing = d[d.State == check_state].iloc[0]
    for col, value in check.items():
        assert abs(float(existing[col]) - value) < 0.011, (key, col, existing[col], value)
    d = d[d.State != 'Puerto Rico']
    d = pd.concat([d, pd.DataFrame([new])], ignore_index=True).sort_values('Score', ascending=False)
    d.to_csv(path, index=False)
    print(f'{key}: added {new}')


def gini():
    rows = acs_rows(os.path.join(RAW, 'census_acsGiniIndex_2025', 'ACSDT1Y2025_B19083_states.json'))
    calc = lambda name: round(100 * (1 - float(rows[name]['B19083_001E'])), 2)
    pr = rows['Puerto Rico']
    add_row('census_acsGiniIndex_2025',
            {'State': 'Puerto Rico', 'Score': calc('Puerto Rico'), 'gini_index': pr['B19083_001E'],
             'gini_moe90': pr['B19083_001M'], 'year': 2025},
            'Alabama', {'Score': calc('Alabama')})


def disability_parity():
    rows = acs_rows(os.path.join(RAW, 'census_acsDisabilityEmploymentParity_2025', 'acs1_2025_C18120_state.json'))
    def calc(name):
        v = {k: float(x) for k, x in rows[name].items() if k.endswith('E') and k.startswith('C18120') and x}
        with_dis = v['C18120_004E'] + v['C18120_007E'] + v['C18120_010E']
        without = v['C18120_005E'] + v['C18120_008E'] + v['C18120_011E']
        r_dis, r_no = 100 * v['C18120_004E'] / with_dis, 100 * v['C18120_005E'] / without
        return {'Score': round(100 * r_dis / r_no, 2), 'Employment rate with disability (%)': round(r_dis, 2),
                'Employment rate without disability (%)': round(r_no, 2),
                'Employment gap (pct points)': round(r_no - r_dis, 2),
                'Civilian noninstitutionalized pop. 18-64 with disability': int(with_dis)}
    add_row('census_acsDisabilityEmploymentParity_2025', {'State': 'Puerto Rico', **calc('Puerto Rico')},
            'Alabama', calc('Alabama'))


def diversity():
    df = pd.read_csv(os.path.join(RAW, 'census_diversityIndex_2025', 'acsdt1y2025-b03002.dat'), sep='|', dtype=str)
    groups = {'NHWhite': 'E003', 'NHBlack': 'E004', 'NHAIAN': 'E005', 'NHAsian': 'E006', 'NHNHPI': 'E007',
              'NHOther': 'E008', 'NHTwoPlus': 'E009', 'Hispanic': 'E012'}
    def calc(geo):
        r = df[df.GEO_ID == geo].iloc[0]
        tot = float(r['B03002_E001'])
        p = {g: float(r['B03002_' + c]) / tot for g, c in groups.items()}
        return {'Score': round(100 * (1 - sum(x ** 2 for x in p.values())), 2),
                **{f'pct_{g}': round(100 * x, 2) for g, x in p.items()}, 'total_pop': int(tot)}
    pr = calc('0400000US72')
    add_row('census_diversityIndex_2025', {'State': 'Puerto Rico', **pr, 'DI_rank': None},
            'Alabama', {'Score': calc('0400000US01')['Score']})


def oxfam():
    text = open(os.path.join(RAW, 'oxfam_bestStatesToWork_2025', 'table1_extracted_text.txt')).read()
    pattern = r'{} (\d+) ([\d.]+) ([\d.]+) ([\d.]+) ([\d.]+)'
    rank, score, wages, prot, org = re.search(pattern.format('Puerto Rico'), text).groups()
    check = float(re.search(pattern.format('Nevada'), text).group(2))
    add_row('oxfam_bestStatesToWork_2025',
            {'State': 'Puerto Rico', 'Score': float(score), 'oxfam_rank_of52': int(rank), 'wages_dim': float(wages),
             'protections_dim': float(prot), 'organize_dim': float(org), 'year': 2025},
            'Nevada', {'Score': check})


def fta_stations():
    """Same aggregation as disabilities/ntd.py, which skipped urbanized areas ending in ', PR'"""
    raw = os.path.join(RAW, 'fta_ntdAdaAccessibleStations_2025')
    agencies = {r['NTD ID']: r for r in csv.DictReader(open(os.path.join(raw, 'ntd_2025_reporter_agency_info_jm7a-9hsy.csv'), encoding='utf-8-sig'))}
    agg = collections.defaultdict(lambda: [0, 0, set()])
    for r in csv.DictReader(open(os.path.join(raw, 'ntd_2025_transit_stations_k9se-yvyg.csv'), encoding='utf-8-sig')):
        a = agencies.get(r['NTD ID'])
        if a:
            u = a['UZA Name']
            agg[u][0] += int(float(r['Primary Mode ADA Accessible Stations'] or 0))
            agg[u][1] += int(float(r['Primary Mode Total Stations'] or 0))
            agg[u][2].add(a['Agency Name'])
    path = os.path.join(OUT, 'fta_ntdAdaAccessibleStations_2025.csv')
    d = pd.read_csv(path)
    seattle = d[d.City == 'Seattle'].iloc[0]
    ada, tot, _ = agg[seattle['Urbanized area (UZA)']]
    assert round(100 * ada / tot, 2) == seattle.Score
    pr_areas = [u for u, (_, tot, _) in agg.items() if u.endswith(', PR') and tot >= 10]
    d = d[d.State != 'PR']
    for u in pr_areas:
        ada, tot, names = agg[u]
        city = u.rsplit(', ', 1)[0].split('--')[0].split('/')[0].strip()
        d.loc[len(d)] = {'State': 'PR', 'City': city, 'Score': round(100 * ada / tot, 2), 'ADA accessible stations': ada,
                         'Total stations': tot, 'Urbanized area (UZA)': u, 'Number of reporting agencies': len(names),
                         'City_source': city}
        print(f'fta_ntdAdaAccessibleStations_2025: added {u} ({ada}/{tot})')
    d.sort_values('Score', ascending=False).to_csv(path, index=False)


if __name__ == '__main__':
    gini()
    disability_parity()
    diversity()
    oxfam()
    fta_stations()
