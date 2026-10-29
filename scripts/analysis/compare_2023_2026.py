"""
Compare GARDN-M results from the original (2023) data with the Oct 2026 update, and cross-check the
2026 state results against the Othering & Belonging Institute's Inclusiveness Index (not a model input).
Run main.py for both data versions first.
"""
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd

os.chdir(Path(__file__).resolve().parents[2])

CATEGORIES = ['social', 'race', 'gender', 'sexual_orientation', 'disabilities']
CITIES = [('MA', 'Boston'), ('VA', 'Richmond'), ('KY', 'Louisville'), ('OH', 'Cleveland'), ('MN', 'Minneapolis'),
          ('NM', 'Albuquerque'), ('GA', 'Atlanta'), ('DC', 'Washington'), ('TX', 'Houston'), ('IL', 'Chicago'),
          ('VA', 'Arlington'), ('TN', 'Memphis'), ('CO', 'Denver'), ('WA', 'Seattle'), ('CA', 'San Diego'),
          ('FL', 'Orlando'), ('PA', 'Pittsburgh'), ('NC', 'Charlotte'), ('UT', 'Salt Lake City'), ('NV', 'Las Vegas')]


def gar(m):
    """Green/Amber/Red zone from the composite score (cutoffs from the original GARDN-M write-up)"""
    return np.where(m.isna(), '', np.where(m >= 6.0, 'Green', np.where(m >= 3.6, 'Amber', 'Red')))


def load(name):
    d = pd.read_csv(f'data/outputs/{name}.csv', index_col=0)
    d['City'] = d['City'].fillna('')
    return d.set_index(['State', 'City'])[['M'] + [f'M_{c}' for c in CATEGORIES]]


old = load('gardnm_2023_normalized')
new = load('gardnm_2026_normalized')
ext = load('gardnm_2026_extended_normalized')[['M']].rename(columns={'M': 'M_2026_extended'})

both = old.join(new, how='outer', lsuffix='_2023', rsuffix='_2026').join(ext)
both['GAR_2023'] = gar(both['M_2023'])
both['GAR_2026'] = gar(both['M_2026'])
both['GAR_2026_extended'] = gar(both['M_2026_extended'])
both['dM'] = both['M_2026'] - both['M_2023']

states = both.xs('', level='City').sort_values('M_2026', ascending=False)
states.to_csv('data/outputs/comparison_states_2023_vs_2026.csv')
cities = both.loc[[c for c in CITIES if c in both.index]].sort_values('M_2026', ascending=False)
cities.to_csv('data/outputs/comparison_cities_2023_vs_2026.csv')

cols = ['M_2023', 'M_2026', 'dM', 'GAR_2023', 'GAR_2026', 'M_2026_extended', 'GAR_2026_extended']
print('=== Selected cities ===')
print(cities[cols].round(2).to_string())
print('\n=== GAR zone counts (states, DC and territories with data) ===')
print(pd.DataFrame({k: states[k].value_counts() for k in ['GAR_2023', 'GAR_2026', 'GAR_2026_extended']}).fillna(0).astype(int))
print('\n=== Largest state changes ===')
print(states['dM'].dropna().sort_values().iloc[[0, 1, 2, 3, 4, -5, -4, -3, -2, -1]].round(2).to_string())

# cross-checks
with open('data/utils/statename_to_abbr.json') as f:
    abbr = json.load(f)
obi = pd.read_csv('data/processed_data_2026/berkeleyOBI_inclusivenessIndex_2025.csv')
obi['State'] = obi['State'].replace(abbr)
obi = obi.set_index('State')['Score']
s = states.join(obi.rename('OBI'), how='inner')
print('\n=== Spearman rank correlations across states ===')
print(f"2023 vs 2026 GARDN-M:        {s['M_2023'].corr(s['M_2026'], method='spearman'):.2f}")
print(f"2026 GARDN-M vs OBI 2025:    {s['M_2026'].corr(s['OBI'], method='spearman'):.2f}")
print(f"2023 GARDN-M vs OBI 2025:    {s['M_2023'].corr(s['OBI'], method='spearman'):.2f}")
for c in CATEGORIES:
    print(f"  {c:20s} 2023 vs 2026: {s[f'M_{c}_2023'].corr(s[f'M_{c}_2026'], method='spearman'):.2f}")
