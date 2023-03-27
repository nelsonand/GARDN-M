#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 24 16:23:40 2023

This is just a working script to start building up the GARDN-M calculation

@author: oaknelson
"""

### Ok, so this is a working script to start figuring out how the calculation is going to work

## It has a few steps:
    
    

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
    try:
        data[source] = pd.read_csv(datadir+f'{source}.csv')#, index_col='State') # TODO: THIS DOES NOT WORK WITH CITIES YET
    except FileNotFoundError:
        pass # TODO, this is noisy for now
        #print(f'WARNING: processed data for {source}.csv was not found... skipping!')    



## (2) Normalize and process all availible data

# Assign normalized composite scores 
def assign_CompScore(sdata):
    if 'Score' in sdata.keys():
        sdata['CompScore'] = sdata.Score / 10 # TODO: Assumes score in percents
    elif 'Rank' in sdata.keys():
        nNorm = len(sdata.Rank) # this should be the number of states... (50, 51?)
        if nNorm != 50:
            print(f'WARNING: nNorm = {nNorm}')
        compscore = (nNorm-(sdata.Rank-1)) / (nNorm/10) # normalized ranking (0-10)
        sdata['CompScore'] = compscore
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
    sdata = assign_CompScore(sdata)
    sdata = assign_M(sdata, source)



# (3) Combine data arrats into final rankings

# get all states and initialize rankings
states = np.unique(np.concatenate([sdata.State.values for sdata in data.values()]))
rankings = pd.DataFrame({'State':states}) 
rankings['City'] = np.NaN # TODO: enable cities
rankings['M'] = np.NaN # initialize M column

# combine individual metrics into rankings
for source, sdata in data.items():
    rankings = pd.merge(rankings, sdata[['State', 'City', 'M']], on=['State', 'City'], how='left', suffixes=(None, f'_{source}'))

# Sum and normalize M values
Mi = [x for x in rankings.keys() if 'M_' in x]
rankings['n'] = rankings[Mi].count(axis=1) # number of non null Mi entries
rankings['M'] = rankings[Mi].sum(axis=1) / rankings['n'] # 1/n sum(Mi)

print(rankings[['State','M', 'n']])