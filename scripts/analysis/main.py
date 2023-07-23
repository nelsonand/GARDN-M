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

# establish relative directories
repo = git.Repo('.', search_parent_directories=True)
os.chdir(repo.working_tree_dir)

def gardnm(
    cities_to_print = ['Atlanta', 'Boston', 'Memphis'],  
    noramlizeAll = True, 
    filename = 'gardnm', 
    verbose = False, 
):
    """Calculation of GARDN-M coefficients

    Args:
        cities_to_print: print the output of these cities to the console 
        noramlizeAll: normalize raw data from every source to span the full 0-10 scale
        filename: prefix for filename to use when saving this run
        verbose: some extra print statements that may be useful when debugging

    Returns:
        Nothing yet, but it saves stuff to a file
    """

    ## (1) Load all the data from GARDN-M/data/processed_data

     # set filename
    filename += '_algorithm_rework' # based on git commit for the moment

    if noramlizeAll:
        filename += '_normalized'

    with open('./data/utils/statename_to_abbr.json', 'r') as f:
        statename_to_abbr = json.load(f)

    with open('./data/sources/source_ratings.json', 'r') as f:
        source_ratings = json.load(f)

    with open('./data/sources/source_types.json', 'r') as f:
        source_types = json.load(f)

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



    ## (2) Normalize and process all availible data

    # Run standard analysis on each source
    for source, sdata in data.items():

        if 'City' not in sdata.keys():
            sdata['City'] = np.NaN
        sdata.City = sdata.City.fillna('')
        sdata = assign_CompScore(sdata, source)
        if noramlizeAll:
            sdata = nornalize_CompScore(sdata)
        sdata = assign_M(sdata, source, sources, source_ratings, source_types)



    # (3) Combine data arrays into subrankings arrays

    # get all states and initialize rankings
    states = np.unique(np.concatenate([sdata.State.values for sdata in data.values()]))
    subrankings = {}
    for source_type, st_list in source_types.items():
        st_list = [s for s in st_list if s in sources] # remove missing sources from st_list

        subrankings[source_type] = pd.DataFrame({'State':states}) 
        subrankings[source_type]['City'] = ''
        for sdata in [sd for source, sd in data.items() if source in st_list]:
            subrankings[source_type] = pd.concat([subrankings[source_type], sdata])
        subrankings[source_type] = subrankings[source_type].drop_duplicates(['State', 'City'])[['State', 'City']]

        # initialize results columns so that they appear in the beginning of the structure
        subrankings[source_type]['M'] = np.NaN 
        subrankings[source_type]['n'] = np.NaN 
        subrankings[source_type]['PSW'] = np.NaN # this will later hold the sum

        # combine individual metrics into rankings
        for source, sdata in [(source, sd) for source, sd in data.items() if source in st_list]:
            subrankings[source_type] = pd.merge(subrankings[source_type], sdata[['State', 'City', 'M', 'PSW']], on=['State', 'City'], how='left', suffixes=(None, f'_{source}'))

        # fill data from sets missing cities
        subrankings[source_type].sort_values(by=['State', 'City'], inplace=True) # sort so that fillna(method='ffil')  is appropriate
        subrankings[source_type] = subrankings[source_type].where(subrankings[source_type]['City']!='', subrankings[source_type].fillna('tmp')) # fill no-city entries with placeholders
        subrankings[source_type].fillna(method='ffill', inplace=True) # fill city-specific rows with no-city entries
        subrankings[source_type].replace('tmp', np.nan, inplace=True) # replace no-city placeholders

        # we need to divide by the sum of the weights for each city
        PSWi = [x for x in subrankings[source_type].keys() if 'PSW_' in x]
        nPSW = subrankings[source_type][PSWi].count(axis=1) # number of non null PSW entries
        subrankings[source_type]['PSW'] =  subrankings[source_type][PSWi].sum(axis=1) / nPSW # the average is 1/n sum(PSWi)
        for source in st_list: # divide each M by the average weight for a weighted average
            subrankings[source_type][f'M_{source}'] = subrankings[source_type][f'M_{source}'].divide(subrankings[source_type]['PSW']/10) # extra x10 comes from max(PSW)=10

        # sum and normalize M values
        Mi = [x for x in subrankings[source_type].keys() if 'M_' in x]
        subrankings[source_type]['n'] = subrankings[source_type][Mi].count(axis=1) # number of non null Mi entries
        subrankings[source_type]['M'] = subrankings[source_type][Mi].sum(axis=1) / subrankings[source_type]['n'] # the average is 1/n sum(Mi)

        if verbose:
            print(subrankings[source_type][['State', 'City', 'M', 'n']].sort_values('City', ascending=False))#.to_string())



    # (4) Combine subrankings into final rankings

    rankings = pd.DataFrame({'State':states}) 


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

def nornalize_CompScore(sdata):
    """Normalize composite scores 

    Args:
        sdata: source data

    Returns:
        sdata: source data, but normalized
    """
    minScore = min(sdata['CompScore'])
    maxScore = max(sdata['CompScore'])
    sdata['CompScore'] = (sdata['CompScore']-minScore) / (maxScore-minScore) * 10

    return sdata

def assign_M(sdata, source, sources, source_ratings, source_types): 
    """Assign individual measures, requires CompScore entry

    Args:
        sdata: source data
        source: source name
        sources: a list of all the source names
        source_ratings: a list of all the source ratings
        source_types: a list of all the source types

    Returns:
        sdata: source data, but with individual measures assigned
    """
    # normalized primacy hierarchy (P): scored from 1-5 (5 being lowest[best] on the hierarchy and 1 being highest[worst])
    sdata[f'P'] = source_ratings[source][0]

    # sensitivity index (S): Rank metric sensitivity and normalize from 1-2
    S_city = 2
    S_state = 1
    sdata[f'S'] = S_state
    sdata[f'S'].where(sdata.City == '', S_city, inplace=True)

    # repetition weight (W): Score of 0-1 depending on how many repeated entries there are for this branch
    source_type = [st for st, st_list in source_types.items() if source in st_list]
    if len(source_type) == 1: 
        W = 1 / len(source_types[source_type[0]])
    elif len(source_type) > 1:
        print(f' ---   WARNING: repitition weight for {source} is undefined... setting to 1...') 
        W = 1
    else:
        W = 1
    total_dataset_normalization = len(sources)/len(source_types)
    sdata['W'] = W * total_dataset_normalization

    # apply the weighting
    sdata['PSW'] = sdata['P'] * sdata['S'] * sdata['W']
    sdata['M'] = sdata['CompScore'] * sdata['PSW']

    # to get a true weighted average, we need to divide by the sum of the weights... this is done later...

    sdata['M'] /= 10 # final score should be out of 10

    return sdata

if __name__ == '__main__':
    gardnm()