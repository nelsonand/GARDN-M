"""
Harmonize city names across the city-level 2026 datasets so they merge on (State, City).
The original source spelling is kept in a 'City_source' column. Safe to re-run.
"""
import os
import pandas as pd

DATADIR = os.path.abspath(f"{__file__}/../../../../data/processed_data_2026")

RENAMES = {
    'berkeleyOBI_citySegregation_2023': {
        ('ID', 'Boise City'): 'Boise',
        ('KY', 'Lexington-Fayette urban c'): 'Lexington',
        ('AK', 'Anchorage municip'): 'Anchorage',
        ('GA', 'Augusta-Richmond County consolidated government (bal'): 'Augusta',
        ('TN', 'Nashville-Davidson metropolitan government (bal'): 'Nashville',
        ('IN', 'Indianapolis city (bal'): 'Indianapolis',
        # OBI lists two Louisville rows; the consolidated city-county government is the jurisdiction other
        # sources call Louisville. The other row (pop. 246,161) appears to be the pre-merger city limits.
        ('KY', 'Louisville/Jefferson County metro government (bal'): 'Louisville',
        ('KY', 'Louisville'): 'Louisville (pre-merger city limits)',
    },
    'hrc_municipalEqualityIndex_2025': {
        ('FL', 'Port Saint Lucie'): 'Port St. Lucie',
        ('MN', 'Saint Paul'): 'St. Paul',
        ('MN', 'Saint Cloud'): 'St. Cloud',
        ('GA', 'Augusta-Richmond County'): 'Augusta',
        ('HI', 'Honolulu County'): 'Honolulu',
        ('UT', 'Ogden City'): 'Ogden',
        ('VA', 'Arlington County'): 'Arlington',  # Arlington, VA is a county with no incorporated city
    },
    'infogram_socialEquityCitiesRanking': {
        ('CA', 'San Benandino'): 'San Bernardino',  # typo in the source
    },
    'wallethub_citiesDisabilities_2026': {
        ('KY', 'Lexington-Fayette'): 'Lexington',
    },
    'fta_ntdAdaAccessibleStations_2025': {
        ('TN', 'Nashville-Davidson'): 'Nashville',
    },
}

for key, renames in RENAMES.items():
    path = os.path.join(DATADIR, f'{key}.csv')
    d = pd.read_csv(path)
    if 'City_source' not in d.columns:
        d['City_source'] = d['City']
    d['City'] = [renames.get((s, c), c) for s, c in zip(d['State'], d['City_source'])]
    assert not d.duplicated(['State', 'City']).any(), key
    d.to_csv(path, index=False)
    print(f'{key}: renamed {sum(d.City != d.City_source)} cities')
