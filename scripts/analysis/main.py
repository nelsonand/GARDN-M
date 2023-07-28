#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 19 13:57:23 2023

The main script for running the GARDN-M model.

@author: oaknelson
"""

import git
import pandas as pd
import os
import json
import numpy as np

# establish relative directories (use pathlib)
repo = git.Repo('.', search_parent_directories=True)
os.chdir(repo.working_tree_dir)

def gardnm(
    cities_to_print = ['Atlanta', 'Boston', 'Memphis'],  
    noramlizeAll = True, 
    filename = 'gardnm', 
    ignore_subtypes = True, 
    verbose = False, 
):
    """Calculation of GARDN-M coefficients

    Args:
        cities_to_print: print the output of these cities to the console 
        noramlizeAll: normalize raw data from every source to span the full 0-10 scale
        filename: prefix for filename to use when saving this run
        ignore_subtypes: option to ignore the various subtypes in source_subtypes
        verbose: some extra print statements that may be useful when debugging

    Returns:
        Nothing yet, but it saves stuff to a file
    """

    # set filename
    filename += '_algorithm_rework' # based on git commit for the moment

    if noramlizeAll:
        filename += '_normalized'

    ## (1) Load all the data from GARDN-M/data/processed_data

    with open('./data/utils/statename_to_abbr.json', 'r') as f:
        statename_to_abbr = json.load(f)

    with open('./data/sources/source_ratings.json', 'r') as f:
        source_ratings = json.load(f)

    with open('./data/sources/source_types.json', 'r') as f:
        source_types = json.load(f)

    with open('./data/sources/source_subtypes.json', 'r') as f:
        source_subtypes = json.load(f)

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
            print(f' ---   WARNING: processed data for {source}.csv was not found... skipping!')  
            
    # we need to remove fail-to-find sources from the master list
    sources = data.keys()



    ## (2) Normalize and weight all availible data

    # Run standard analysis on each source
    for source, sdata in data.items():

        if 'City' not in sdata.keys():
            sdata['City'] = np.NaN
        sdata.City = sdata.City.fillna('')
        sdata = assign_CompScore(sdata, source)
        if noramlizeAll:
            sdata = normalize_CompScore(sdata)
        sdata = assign_PSW(sdata, source, source_ratings, source_subtypes, ignore_subtypes)



    # (3) Combine data arrays into subrankings arrays

    # get all states and initialize rankings
    states = np.unique(np.concatenate([sdata.State.values for sdata in data.values()]))
    subrankings = {}
    for source_type, st_list in source_types.items():
        st_list = [s for s in st_list if s in sources] # remove missing sources from st_list
        sb_list = np.unique([sbt for s, sbt in source_subtypes.items() if s in st_list]) # get unique subtypes in this source_type

        subrankings[source_type] = pd.DataFrame({'State':states}) 
        subrankings[source_type]['City'] = '' # initialize
        for sdata in [sd for source, sd in data.items() if source in st_list]:
            subrankings[source_type] = pd.concat([subrankings[source_type], sdata])
        subrankings[source_type] = subrankings[source_type].drop_duplicates(['State', 'City'])[['State', 'City']]

        # initialize results columns so that they appear in the beginning of the structure
        subrankings[source_type]['M'] = np.NaN # initialize
        subrankings[source_type]['n'] = np.NaN # initialize
        subrankings[source_type]['avgPSW'] = np.NaN # this will later hold the average weight

        # combine individual metrics into rankings
        subrankings[source_type]['B'] = '' # empty to force suffix on merge, will drop later
        subrankings[source_type]['PSW'] = '' # empty to force suffix on merge, will drop later
        for source in st_list:
            sdata = data[source]
            subrankings[source_type] = pd.merge(subrankings[source_type], sdata[['State', 'City', 'B', 'PSW']], on=['State', 'City'], how='left', suffixes=(None, f'_{source}'))
        subrankings[source_type].drop(columns=['B'], inplace=True)
        subrankings[source_type].drop(columns=['PSW'], inplace=True)

        if ignore_subtypes:
             # we need to divide by the sum of the weights for each city
            PSWi = [x for x in subrankings[source_type].keys() if 'PSW_' in x]
            subrankings[source_type]['avgPSW'] =  subrankings[source_type][PSWi].mean(axis=1) 

            # calculate individual M
            for source in st_list: # divide each M by the average weight for a weighted average
                subrankings[source_type][f'M_{source}'] = subrankings[source_type][f'B_{source}'] * subrankings[source_type][f'PSW_{source}']
                subrankings[source_type][f'M_{source}'] = subrankings[source_type][f'M_{source}'].divide(subrankings[source_type]['avgPSW']) 

        else: 
            pass #TODO, this will fail


        # sum and average M values from each source
        Mi = [x for x in subrankings[source_type].keys() if 'M_' in x]
        subrankings[source_type]['n'] = subrankings[source_type][Mi].count(axis=1).astype(int) # number of non null Mi entries
        subrankings[source_type]['M'] = subrankings[source_type][Mi].mean(axis=1) 

        # fill data from sets missing cities
        subrankings[source_type].sort_values(by=['State', 'City'], inplace=True) # sort so that fillna(method='ffil')  is appropriate
        subrankings[source_type] = subrankings[source_type].where(subrankings[source_type]['City']!='', subrankings[source_type].fillna('tmp')) # fill no-city entries with placeholders
        subrankings[source_type].fillna(method='ffill', inplace=True) # fill city-specific rows with no-city entries
        subrankings[source_type].replace('tmp', np.nan, inplace=True) # replace no-city placeholders

        if verbose:
            print(subrankings[source_type][['State', 'City', 'M', 'n']].sort_values('City', ascending=False))#.to_string())



    # (4) Combine subrankings into final rankings

    rankings = pd.DataFrame({'State':states}) 
    rankings['City'] = '' # initialize
    rankings['M'] = np.NaN # initialize
    rankings['n'] = np.NaN # initialize
    for source_type, stdata in subrankings.items():
        rankings = pd.merge(rankings, stdata[['State', 'City', 'M', 'n']], on=['State', 'City'], how='outer', suffixes=(None, f'_{source_type}'))
    
    # fill data from source_types missing cities
    rankings.sort_values(by=['State', 'City'], inplace=True) # sort so that fillna(method='ffil')  is appropriate
    rankings = rankings.where(rankings['City']!='', rankings.fillna('tmp')) # fill no-city entries with placeholders
    rankings.fillna(method='ffill', inplace=True) # fill city-specific rows with no-city entries
    rankings.replace('tmp', np.nan, inplace=True) # replace no-city placeholders

    rankings['n'] = rankings[[f'n_{st}' for st in source_types]].sum(axis=1).astype(int)
    rankings['M'] = rankings[[f'M_{st}' for st in source_types]].mean(axis=1)



    # (5) Save the output and print results

    rankings.to_csv(f'data/outputs/{filename}.csv')
    if verbose:
        print(f'Data has been saved to data/outputs/{filename}.csv!')

    if len(cities_to_print):
        inds_to_print = []
        for city_to_print in cities_to_print:
            if city_to_print in rankings['City'].values:
                inds_to_print += [np.where(rankings['City']==city_to_print)[0][0]]
            else:
                print(f'Sorry, {city_to_print} was not found in the data...')
        items_to_print = ['State','City','M'] + [f'M_{st}' for st in source_types] #+ [f'M_{s}' for s in sources]
        print(rankings[items_to_print].iloc[inds_to_print].transpose().to_string())
    

def assign_CompScore(sdata, source):
    """Assign composite scores 

    Args:
        sdata: source data
        source: source name

    Returns:
        sdata: source data, but with composite scores assigned
    """
    if 'Score' in sdata.keys():
        sdata['B'] = sdata.Score / 10 # TODO: Assumes score in percents
    elif 'Rank' in sdata.keys():
        nNorm = len(sdata.Rank) # this should be the number of states... (50, 51?)
        if source == 'statusWomen_bestWorstStates':
            nNorm = 50 # we know this dataset is incomplete, and expect it to be, but nNorm is still 50
        if nNorm != 50:
            print(f' ---   WARNING: nNorm for {source} was {nNorm}...')
        compscore = (nNorm-(sdata.Rank-1)) / (nNorm/10) # normalized ranking (0-10)
        sdata['B'] = compscore
    elif 'Processed' in sdata.keys():
        sdata['B'] = sdata.Processed
    else:
        print(f' ---   WARNING: unclear interpretation of composite score for {source}... this will break!') 

    return sdata

def normalize_CompScore(sdata):
    """Normalize composite scores 

    Args:
        sdata: source data

    Returns:
        sdata: source data, but normalized
    """
    minScore = min(sdata['B'])
    maxScore = max(sdata['B'])
    sdata['B'] = (sdata['B']-minScore) / (maxScore-minScore) * 10

    return sdata

def assign_PSW(sdata, source, source_ratings, source_subtypes, ignore_subtypes): 
    """Assign individual weightings for each entry

    Args:
        sdata: source data
        source: source name
        source_ratings: a list of all the source ratings
        source_subtypes: a list of all the source subtypes
        ignore_subtypes: option to ignore the various subtypes in source_subtypes
    Returns:
        sdata: source data, but with individual measures assigned
    """
    # normalized primacy hierarchy (P): scored from 1-5 (5 being lowest[best] on the hierarchy and 1 being highest[worst])
    sdata['P'] = source_ratings[source][0]

    # sensitivity index (S): Rank metric sensitivity and normalize from 1-2
    S_city = 2
    S_state = 1
    sdata['S'] = S_state
    sdata['S'].where(sdata.City == '', S_city, inplace=True)

    # repetition weight (W): Score of 0-1 depending on how many repeated entries there are for this branch
    if ignore_subtypes:
        sdata['W'] = 1
    else:
        subtype = source_subtypes[source]
        n_subtype = len([s for s, sbt in source_subtypes.items() if sbt == subtype])
        sdata['W'] = 1 / n_subtype 

    sdata['PSW'] = sdata['P'] * sdata['S']* sdata['W']

    # to get a true weighted average, we need to divide by the sum of the weights... this is done later...
    return sdata

if __name__ == '__main__':
    gardnm()