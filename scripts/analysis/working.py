#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 24 16:23:40 2023

This is just a working script to start building up the GARDN-M calculation

@author: oaknelson
"""

### Ok, so this is a working script to start figuring out how the calculation is going to work

## It has a few steps:
    
    
    
### THIS SHOULD BE SAVED SOMEWHERE ELSE ###    
statename_to_abbr = {
# States
'Alabama': 'AL',
'Montana': 'MT',
'Alaska': 'AK',
'Nebraska': 'NE',
'Arizona': 'AZ',
'Nevada': 'NV',
'Arkansas': 'AR',
'New Hampshire': 'NH',
'California': 'CA',
'New Jersey': 'NJ',
'Colorado': 'CO',
'New Mexico': 'NM',
'Connecticut': 'CT',
'New York': 'NY',
'Delaware': 'DE',
'North Carolina': 'NC',
'Florida': 'FL',
'North Dakota': 'ND',
'Georgia': 'GA',
'Ohio': 'OH',
'Hawaii': 'HI',
'Oklahoma': 'OK',
'Idaho': 'ID',
'Oregon': 'OR',
'Illinois': 'IL',
'Pennsylvania': 'PA',
'Indiana': 'IN',
'Rhode Island': 'RI',
'Iowa': 'IA',
'South Carolina': 'SC',
'Kansas': 'KS',
'South Dakota': 'SD',
'Kentucky': 'KY',
'Tennessee': 'TN',
'Louisiana': 'LA',
'Texas': 'TX',
'Maine': 'ME',
'Utah': 'UT',
'Maryland': 'MD',
'Vermont': 'VT',
'Massachusetts': 'MA',
'Virginia': 'VA',
'Michigan': 'MI',
'Washington': 'WA',
'Minnesota': 'MN',
'West Virginia': 'WV',
'Mississippi': 'MS',
'Wisconsin': 'WI',
'Missouri': 'MO',
'Wyoming': 'WY',

# Other
'District of Columbia': 'DC',
'D.C.':'DC',
'Puerto Rico': 'PR',
'Washington, D.C.': 'DC',
'American Samoa': 'AS',
'Northern Mariana Islands': 'NMI',
'U.S. Virgin Islands': 'USVI',
'Guam': 'GU'
}



verbose = False


## (1) Load all the data from GARDN-M/data/processed_data

import git # requires gitpython module
import pandas as pd
import os
import json
import numpy as np

# establish relative directories
repo = git.Repo('.', search_parent_directories=True)
os.chdir(repo.working_tree_dir)

# get source data
with open('./data/sources/source_ratings.json', 'r') as f:
    source_ratings = json.load(f)
sources = source_ratings.keys()

# get processed data
data = {}
datadir = './data/processed_data/'
for source in sources:
    if verbose: 
        print(f'Reading data from {source}...')
    try:
        data[source] = pd.read_csv(datadir+f'{source}.csv')
        data[source]['State'] = data[source]['State'].replace(statename_to_abbr) # change to abbeviations
    except FileNotFoundError:
        #pass # TODO, this is noisy for now
        print(f'   ---   WARNING: processed data for {source}.csv was not found... skipping!')    




## (2) Normalize and process all availible data

# Assign normalized composite scores 
def assign_CompScore(sdata, source):
    if 'Score' in sdata.keys():
        sdata['CompScore'] = sdata.Score / 10 # TODO: Assumes score in percents
        # or should this be normalized to max/min score?  = sdata.Score / max(sdata.Score) * 10
    elif 'Rank' in sdata.keys():
        nNorm = len(sdata.Rank) # this should be the number of states... (50, 51?)
        if source == 'statusWomen_bestWorstStates':
            nNorm = 50 # we know this dataset is incomplete, and expect it to be, but nNorm is still 50
        if nNorm != 50:
            print(f'WARNING: nNorm for {source} was {nNorm}...')
        compscore = (nNorm-(sdata.Rank-1)) / (nNorm/10) # normalized ranking (0-10)
        sdata['CompScore'] = compscore
    elif 'Processed' in sdata.keys():
        sdata['CompScore'] = sdata.Processed
    else:
        print(f' ---   WARNING: unclear interpretation of CompScore for {source}... this will break!') 
    return sdata

# Assign individual measures, requires CompScore entry
def assign_M(sdata, source): 
    PSW = np.prod(source_ratings[source]) # P * S * W
    sdata['M'] = sdata['CompScore'] * PSW / 10 # out of 10
    return sdata

# Run stanard analysis on each source
for source, sdata in data.items():
    if 'City' not in sdata.keys():
        sdata['City'] = np.NaN
    sdata.City = sdata.City.fillna('')
    sdata = assign_CompScore(sdata, source)
    sdata = assign_M(sdata, source)

# (3) Combine data arrats into final rankings

# get all states and initialize rankings
states = np.unique(np.concatenate([sdata.State.values for sdata in data.values()]))
rankings = pd.DataFrame({'State':states}) 
rankings['City'] = ''
for sdata in data.values():
    rankings = pd.concat([rankings, sdata])
rankings = rankings.drop_duplicates(['State', 'City'])[['State', 'City']]
rankings['M'] = np.NaN # initialize M column

# combine individual metrics into rankings
for source, sdata in data.items():
    rankings = pd.merge(rankings, sdata[['State', 'City', 'M']], on=['State', 'City'], how='left', suffixes=(None, f'_{source}'))

# fill data from sets missing cities
rankings.sort_values(by=['State', 'City'], inplace=True) # sort so that fillna(method='ffil')  is appropriate
rankings = rankings.where(rankings['City']!='', rankings.fillna('tmp')) # fill no-city entries with placeholders
rankings.fillna(method='ffill', inplace=True) # fill city-specific rows with no-city entries
rankings.replace('tmp', np.nan, inplace=True) # replace no-city placeholders

# sum and normalize M values
Mi = [x for x in rankings.keys() if 'M_' in x]
rankings['n'] = rankings[Mi].count(axis=1) # number of non null Mi entries
rankings['M'] = rankings[Mi].sum(axis=1) / rankings['n'] # 1/n sum(Mi)

print(rankings[['State', 'City', 'M', 'n']].sort_values('M', ascending=False))