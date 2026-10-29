"""
Process files downloaded by hand (sites that block automated access) into GARDN-M datasets.

Usage: python3 -I scripts/gather/oct2026/manual/process_manual_downloads.py [manual_downloads_dir]

The downloads themselves are large and are not committed (see .gitignore); small extracts of the
values used are saved to data/raw_data_2026/<key>/.
"""
import io
import os
import re
import sys
import zipfile

import pandas as pd
import pypdf

REPO = os.path.abspath(f"{__file__}/../../../../..")
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(REPO, 'manual_downloads')
OUT = os.path.join(REPO, 'data', 'processed_data_2026')
RAW = os.path.join(REPO, 'data', 'raw_data_2026')


def save(key, df, raw=None):
    df.to_csv(os.path.join(OUT, f'{key}.csv'), index=False)
    if raw is not None:
        os.makedirs(os.path.join(RAW, key), exist_ok=True)
        raw.to_csv(os.path.join(RAW, key, 'extract.csv'), index=False)
    print(f'{key}: {len(df)} rows')


def national_equity_atlas():
    """National Equity Atlas Racial Equity Index (data download updated 2024-12-04), latest data year 2022.
    States (geo_type 2) and the 100 largest cities (geo_type 7); Score = REI_total (0-100)."""
    d = pd.read_excel(os.path.join(SRC, 'REI_DATA_DOWNLOAD_20241126.xlsx'), sheet_name='Data')
    d = d[d.year == d.year.max()]
    states = d[d.geo_type == 2]
    fips_to_abbr = dict(zip(states.geo_code_long // 1000, states.GEO_NAME_SHORT))
    fips_to_abbr[11] = 'DC'

    cities = d[d.geo_type == 7].copy()
    # place codes are SSPPPPP; Honolulu is stored as a county-style code (15999)
    fips = [c // 1000 if c < 100000 else c // 100000 for c in cities.geo_code_long]
    cities['State'] = [fips_to_abbr[f] for f in fips]
    special = {
        'City and County of Honolulu': 'Honolulu',
        'Lexington-Fayette urban county': 'Lexington',
        'Washington city': 'Washington',
    }
    def clean(name):
        if name in special:
            return special[name]
        name = re.split(r'/| metropolitan government|-Fayette', name)[0]
        name = re.sub(r'-Davidson$', '', name)
        return re.sub(r' (city \(balance\)|city|municipality)$', '', name)
    cities['City'] = [clean(n) for n in cities.GEO_NAME_SHORT]

    out = pd.concat([
        pd.DataFrame({'State': states.GEO_NAME_SHORT, 'City': '', 'Score': states.REI_total.round(2),
                      'Source name': states.GEO_NAME_SHORT}),
        pd.DataFrame({'State': cities.State, 'City': cities.City, 'Score': cities.REI_total.round(2),
                      'Source name': cities.GEO_NAME_SHORT}),
    ])
    out['Data year'] = int(d.year.max())
    assert not out.duplicated(['State', 'City']).any()
    keep = ['year', 'geo_type', 'geo_code_long', 'GEO_NAME_SHORT', 'REI_total', 'IS_total', 'PS_total']
    save('nationalEquityAtlas_2024', out, raw=d[d.geo_type.isin([2, 7])][keep])


def aarp_ltss_scorecard():
    """AARP/Commonwealth Fund/SCAN LTSS State Scorecard 2023, Exhibit 3 (overall rank 1-51, with tiers)."""
    pdf = pypdf.PdfReader(os.path.join(SRC, '2023-ltss-scorecard-innovation-and-opportunity.doi.10.26419-2fppi.00203.001.pdf'))
    text = pdf.pages[31].extract_text()  # page 32
    assert 'EXHIBIT 3' in text
    rows, tier = [], None
    for line in text.splitlines():
        line = line.strip()
        if m := re.match(r'TIER (\d)$', line):
            tier = int(m.group(1))
        elif m := re.match(r'([A-Z][A-Za-z .]+?) (\d{1,2})$', line):
            rows.append((m.group(1), int(m.group(2)), tier))
    out = pd.DataFrame(rows, columns=['State', 'Rank', 'Tier']).sort_values('Rank')
    assert len(out) == 51 and list(out.Rank) == list(range(1, 52)), out
    save('aarp_ltssScorecard_2023', out, raw=out)


def commonwealth_health_system():
    """Commonwealth Fund 2025 Scorecard on State Health System Performance, overall rank from each state profile."""
    rows = []
    with zipfile.ZipFile(os.path.join(SRC, '2025_State_Scorecard_Profiles.zip')) as z:
        for name in z.namelist():
            if name.endswith('.pdf'):
                text = pypdf.PdfReader(io.BytesIO(z.read(name))).pages[0].extract_text()
                m = re.search(r'(.+?) ranks #(\d+) overall', text)
                rows.append((m.group(1).strip(), int(m.group(2))))
    out = pd.DataFrame(rows, columns=['State', 'Rank']).sort_values('Rank')
    assert len(out) == 51 and out.Rank.is_unique
    save('commonwealthFund_healthSystemPerformance_2025', out, raw=out)


if __name__ == '__main__':
    national_equity_atlas()
    aarp_ltss_scorecard()
    commonwealth_health_system()
