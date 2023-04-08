#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 24 16:23:40 2023

This is just a working script to start building up the GARDN-M calculation

@author: oaknelson
"""

### Ok, so this is a working script to start figuring out how the calculation is going to work

verbose = False # some extra print statements for debugging
noramlizeAll = True # normalize results from every source to span the full 0-10 scale
filename = 'gardnm_test' # where to save the results of this run
setPbyCity = True # if True, uses P=5 for city data and P=4 for state data, regardless of the entry in source_ratings.json
cities_to_print = ['Atlanta', 'Boston', 'Memphis'] # print the output of a specific city to the console    



## (0) Setup enviornment

import git # requires gitpython module
import pandas as pd
import os
import json
import numpy as np
    
with open('./data/utils/statename_to_abbr.json', 'r') as f:
    statename_to_abbr = json.load(f)

# get source data
with open('./data/sources/source_ratings.json', 'r') as f:
    source_ratings = json.load(f)

with open('./data/sources/source_types.json', 'r') as f:
    source_types = json.load(f)

sources = source_ratings.keys()



## (1) Load all the data from GARDN-M/data/processed_data

# establish relative directories
repo = git.Repo('.', search_parent_directories=True)
os.chdir(repo.working_tree_dir)

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
        print(f' ---   WARNING: processed data for {source}.csv was not found... skipping!')    

# redefine sources array for future use (now excludes missing files)
sources = data.keys()



## (2) Normalize and process all availible data

# Assign composite scores 
def assign_CompScore(sdata, source):

    if 'Score' in sdata.keys():
        sdata['CompScore'] = sdata.Score / 10 # TODO: Assumes score in percents
    elif 'Rank' in sdata.keys():
        nNorm = len(sdata.Rank) # this should be the number of states... (50, 51?)
        if source == 'statusWomen_bestWorstStates':
            nNorm = 50 # we know this dataset is incomplete, and expect it to be, but nNorm is still 50
        if nNorm != 50:
            print(f' ---   WARNING: nNorm for {source} was {nNorm}...')
        compscore = (nNorm-(sdata.Rank-1)) / (nNorm/10) # normalized ranking (0-10)
        sdata['CompScore'] = compscore
    elif 'Processed' in sdata.keys():
        sdata['CompScore'] = sdata.Processed
    else:
        print(f' ---   WARNING: unclear interpretation of CompScore for {source}... this will break!') 

    return sdata

# Normalized composite scores 
def nornalize_CompScore(sdata):

    minScore = min(sdata['CompScore'])
    maxScore = max(sdata['CompScore'])
    sdata['CompScore'] = (sdata['CompScore']-minScore) / (maxScore-minScore) * 10

    return sdata

# Assign individual measures, requires CompScore entry
def assign_M(sdata, source): 

    P = source_ratings[source][0]
    PSW = np.prod(source_ratings[source]) # P * S * W
    sdata['M'] = sdata['CompScore'] * PSW / 10 # out of 10
    if setPbyCity: # adjust the P value to give stronger weighting to city-specific info
        sdata['M'].where(sdata.City != '', sdata['M']/P*4, inplace=True)
        sdata['M'].where(sdata.City == '', sdata['M']/P*5, inplace=True)

    return sdata

# Run stanard analysis on each source
for source, sdata in data.items():

    if 'City' not in sdata.keys():
        sdata['City'] = np.NaN
    sdata.City = sdata.City.fillna('')
    sdata = assign_CompScore(sdata, source)
    if noramlizeAll:
        sdata = nornalize_CompScore(sdata)
    sdata = assign_M(sdata, source)



# (3) Combine data arrays into final rankings

# get all states and initialize rankings
states = np.unique(np.concatenate([sdata.State.values for sdata in data.values()]))
rankings = pd.DataFrame({'State':states}) 
rankings['City'] = ''
for sdata in data.values():
    rankings = pd.concat([rankings, sdata])
rankings = rankings.drop_duplicates(['State', 'City'])[['State', 'City']]

# initialize results columns so that they appear in the beginning of the structure
rankings['M'] = np.NaN 
rankings['n'] = np.NaN 
for stype in source_types.keys(): 
    rankings[f'M_{stype}'] = np.NaN 
    rankings[f'n_{stype}'] = np.NaN 

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

# calculate individual M's for each source type
for stype in source_types.keys():
    tsources = [st for st in source_types[stype] if st in sources]
    trankings = rankings[[f'M_{ts}' for ts in tsources]]
    Mi = [x for x in trankings.keys() if 'M_' in x]
    rankings[f'n_{stype}'] = trankings[Mi].count(axis=1) # number of non null Mi entries
    rankings[f'M_{stype}'] = trankings[Mi].sum(axis=1) / rankings[f'n_{stype}'] # 1/n sum(Mi)

if verbose:
    print(rankings[['State', 'City', 'M', 'n']].sort_values('City', ascending=False))#.to_string())



# (4) Save the output and print results

rankings.to_csv(f'data/outputs/{filename}.csv')
print(f'Data has been saved to data/outputs/{filename}.csv!')

if len(cities_to_print):
    inds_to_print = []
    for city_to_print in cities_to_print:
        if city_to_print in rankings['City'].values:
            inds_to_print += [np.where(rankings['City']==city_to_print)[0][0]]
        else:
            print(f'Sorry, {city_to_print} was not found in the data...')
    print(rankings.iloc[inds_to_print].transpose().to_string())