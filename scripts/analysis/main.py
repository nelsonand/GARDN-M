#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 19 13:57:23 2023

The main script for running the GARDN-M model.

@author: oaknelson
"""

from pathlib import Path
import pandas as pd
import os
import json
import numpy as np

# repository root; all data paths are built from here
REPO = Path(__file__).resolve().parents[2]

# Green/Amber/Red cutoffs on the composite metric M (from the original GARDN-M write-up)
GAR_CUTOFFS = {'Amber': 3.6, 'Green': 6.0}

# year that data ages are measured from when recency_half_life is used
REFERENCE_YEAR = 2026

SCORE_COLUMNS = ['Score', 'Rank', 'Processed'] # checked in this order by assign_CompScore
SCORE_RANGES = {'Score': (0, 100), 'Processed': (0, 10)}


def gardnm(
    cities_to_print = ['Atlanta', 'Boston', 'Memphis'],
    normalizeAll = True,
    filename = 'gardnm',
    ignore_subtypes = False,
    verbose = False,
    data_version = '2026',
    extended = False,
    absolute_scales = False,
    recency_half_life = None,
    recency_grace = 2,
    min_categories = None,
):
    """Calculation of GARDN-M coefficients

    Args:
        cities_to_print: print the output of these cities to the console ('City' or 'City, ST')
        normalizeAll: normalize raw data from every source to span the full 0-10 scale
        filename: prefix for filename to use when saving this run
        ignore_subtypes: ignore the repetition weight W (otherwise sources sharing a subtype within a
            category split one weight between them, W = 1/k)
        verbose: some extra print statements that may be useful when debugging
        data_version: '2026' for the Oct 2026 update (data/sources_2026, data/processed_data_2026) or
            '2023' for the original data (data/sources, data/processed_data)
        extended: also score the extra 2026 categories listed in source_types_extended.json
        absolute_scales: with normalizeAll, keep sources whose metadata marks their scale as 'absolute'
            on their native 0-10 scale instead of stretching them to span 0-10
        recency_half_life: if set (years), replace the manual stale_adjustment to P with an age-based
            discount P * 0.5**(max(0, age - recency_grace) / recency_half_life)
        recency_grace: data up to this many years old is not discounted when recency_half_life is set
        min_categories: if set, locations with data in fewer categories get no composite score

    Returns:
        rankings: the final rankings (also saved to data/outputs/)
    """

    sourcedir, datadir = data_dirs(data_version)
    inputs = load_inputs(sourcedir, datadir, extended=extended, strict=(data_version != '2023'), verbose=verbose)
    rankings = score(
        inputs, normalizeAll=normalizeAll, ignore_subtypes=ignore_subtypes, absolute_scales=absolute_scales,
        recency_half_life=recency_half_life, recency_grace=recency_grace, min_categories=min_categories,
        verbose=verbose,
    )

    # set filename
    filename += f'_{data_version}'
    if extended:
        filename += '_extended'
    if absolute_scales:
        filename += '_absolute'
    if recency_half_life is not None:
        filename += f'_halflife{recency_half_life:g}'
    if min_categories is not None:
        filename += f'_min{min_categories}'
    if normalizeAll:
        filename += '_normalized'

    # (5) Save the output and print results

    rankings.to_csv(REPO / 'data' / 'outputs' / f'{filename}.csv')
    if verbose:
        print(f'Data has been saved to data/outputs/{filename}.csv!')

    if len(cities_to_print):
        inds_to_print = []
        for city_to_print in cities_to_print: # 'City' or 'City, ST'
            city, _, state = [x.strip() for x in city_to_print.partition(',')]
            match = (rankings['City'] == city) & ((rankings['State'] == state) if state else True)
            if match.any():
                inds_to_print += list(np.where(match)[0]) # all states with a city of this name
            else:
                print(f'Sorry, {city_to_print} was not found in the data...')
        items_to_print = ['State','City','M','GAR'] + [f'M_{st}' for st in inputs['source_types']]
        print(rankings[items_to_print].iloc[inds_to_print].transpose().to_string())

    return rankings


def data_dirs(data_version):
    """Source-metadata and processed-data directories for a data version"""
    if data_version == '2023':
        return f'{REPO}/data/sources/', f'{REPO}/data/processed_data/'
    return f'{REPO}/data/sources_{data_version}/', f'{REPO}/data/processed_data_{data_version}/'


def load_inputs(sourcedir, datadir, extended=False, strict=True, verbose=False):
    """(1) Load and validate source metadata and processed data

    Args:
        sourcedir: directory with source_ratings.json, source_types[_extended].json, source_subtypes.json
            and (optionally) source_metadata.json
        datadir: directory with one processed <source>.csv per source
        extended: use source_types_extended.json instead of source_types.json
        strict: treat ambiguous scoring columns as errors rather than warnings
        verbose: some extra print statements that may be useful when debugging

    Returns:
        inputs: dict of data (one DataFrame per source), source_ratings, source_types, source_subtypes
            and source_metadata
    """
    with open(REPO / 'data' / 'utils' / 'statename_to_abbr.json', 'r') as f:
        statename_to_abbr = json.load(f)

    with open(sourcedir+'source_ratings.json', 'r') as f:
        source_ratings = json.load(f)

    with open(sourcedir+('source_types_extended.json' if extended else 'source_types.json'), 'r') as f:
        source_types = json.load(f)

    with open(sourcedir+'source_subtypes.json', 'r') as f:
        source_subtypes = json.load(f)

    source_metadata = {}
    if os.path.exists(sourcedir+'source_metadata.json'):
        with open(sourcedir+'source_metadata.json', 'r') as f:
            source_metadata = json.load(f)

    # get processed data for the sources used by the selected categories
    used = [s for st_list in source_types.values() for s in st_list]
    data = {}
    for source in [s for s in source_ratings if s in used]:
        if verbose:
            print(f'Reading data from {source}...')
        try:
            sdata = pd.read_csv(datadir+f'{source}.csv')
        except FileNotFoundError:
            print(f' ---   WARNING: processed data for {source}.csv was not found... skipping!')
            continue
        sdata['State'] = sdata['State'].replace(statename_to_abbr) # change to abbeviations
        if 'City' not in sdata.keys():
            sdata['City'] = np.nan
        sdata['City'] = sdata['City'].fillna('')
        data[source] = validate_source(sdata, source, set(statename_to_abbr.values()), strict)

    # remove fail-to-find sources from the category lists
    for source_type, st_list in source_types.items():
        unrated = [s for s in st_list if s not in source_ratings]
        if unrated:
            print(f' ---   WARNING: {source_type} sources without a rating in source_ratings.json: {unrated}')
        missing = [s for s in st_list if s not in data]
        if missing and verbose:
            print(f' ---   WARNING: {source_type} sources without data: {missing}')
        source_types[source_type] = [s for s in st_list if s in data]

    return {
        'data': data,
        'source_ratings': source_ratings,
        'source_types': source_types,
        'source_subtypes': source_subtypes,
        'source_metadata': source_metadata,
    }


def validate_source(sdata, source, valid_states, strict=True):
    """Check that a processed source file can be scored unambiguously

    Errors (always raised): no scoring column, unknown or missing states, duplicate locations, and scores
    outside the expected range. Several scoring columns is an error when strict (otherwise the first of
    SCORE_COLUMNS is used, as assign_CompScore does). Rows without a score are dropped with a warning.

    Args:
        sdata: source data, with State already converted to abbreviations and City filled with ''
        source: source name
        valid_states: allowed state abbreviations
        strict: treat several scoring columns as an error

    Returns:
        sdata: validated source data
    """
    problems = []
    score_cols = [c for c in SCORE_COLUMNS if c in sdata.keys()]
    if not score_cols:
        raise ValueError(f'{source}: no scoring column (one of {SCORE_COLUMNS})')
    if len(score_cols) > 1:
        message = f'{source}: several scoring columns {score_cols}; only {score_cols[0]} is used'
        if strict:
            problems.append(message)
        else:
            print(f' ---   WARNING: {message}')
    col = score_cols[0]

    values = pd.to_numeric(sdata[col], errors='coerce')
    non_numeric = sdata[col].notna() & values.isna()
    if non_numeric.any():
        problems.append(f'{source}: non-numeric {col} values {sdata.loc[non_numeric, col].tolist()}')
    if sdata[col].isna().any():
        dropped = sdata.loc[sdata[col].isna(), ['State', 'City']].values.tolist()
        print(f' ---   WARNING: {source}: dropping rows without a {col}: {dropped}')
        sdata = sdata[sdata[col].notna()].copy()
        values = values[sdata.index]
    sdata[col] = values

    bad_states = sorted(set(sdata['State'].astype(str)) - valid_states)
    if bad_states:
        problems.append(f'{source}: unrecognized states {bad_states}')
    duplicates = sdata.duplicated(['State', 'City'])
    if duplicates.any():
        problems.append(f'{source}: duplicate locations {sdata.loc[duplicates, ["State", "City"]].values.tolist()}')
    if col in SCORE_RANGES:
        low, high = SCORE_RANGES[col]
        if values.min() < low or values.max() > high:
            problems.append(f'{source}: {col} outside [{low}, {high}] ({values.min()} to {values.max()})')
    elif values.min() < 1:
        problems.append(f'{source}: Rank below 1')

    if problems:
        raise ValueError('Invalid processed data:\n  ' + '\n  '.join(problems))

    return sdata


def score(
    inputs,
    normalizeAll = True,
    ignore_subtypes = False,
    absolute_scales = False,
    recency_half_life = None,
    recency_grace = 2,
    min_categories = None,
    ratings = None,
    exclude = (),
    verbose = False,
):
    """(2)-(4) Weight, combine and rank the loaded data (see gardnm for the arguments)

    Args:
        inputs: output of load_inputs
        ratings: optional {source: P} overriding the perceived hierarchy P (used by sensitivity analysis)
        exclude: sources to leave out (used by sensitivity analysis)

    Returns:
        rankings: one row per state (City == '') and per city
    """
    source_types = {st: [s for s in st_list if s not in exclude] for st, st_list in inputs['source_types'].items()}
    source_subtypes = inputs['source_subtypes']
    metadata = inputs['source_metadata']
    data = {s: sd.copy() for s, sd in inputs['data'].items() if s not in exclude}
    sources = data.keys()

    # perceived hierarchy P, including the manual staleness adjustment or the age-based discount
    P = {}
    for source in sources:
        meta = metadata.get(source, {})
        P[source] = ratings[source] if ratings and source in ratings else inputs['source_ratings'][source][0]
        if recency_half_life is None:
            P[source] += meta.get('stale_adjustment', 0)
        else:
            if 'data_year' not in meta:
                raise ValueError(f'{source}: recency_half_life needs a data_year in source_metadata.json')
            age = max(0, REFERENCE_YEAR - meta['data_year'] - recency_grace)
            P[source] *= 0.5 ** (age / recency_half_life)

    # repetition weight W: sources sharing a subtype within one category split a single weight
    W = {}
    for st_list in source_types.values():
        for source in st_list:
            k = 1 if ignore_subtypes else sum(source_subtypes.get(s) == source_subtypes.get(source) for s in st_list)
            W[source] = 1 / k


    ## (2) Normalize and weight all availible data

    # Run standard analysis on each source
    for source, sdata in data.items():
        sdata = assign_CompScore(sdata, source, metadata.get(source, {}).get('n_ranked'))
        keep_native = absolute_scales and metadata.get(source, {}).get('scale') == 'absolute'
        if normalizeAll and not keep_native:
            sdata = normalize_CompScore(sdata)
        sdata = assign_PSW(sdata, P[source], W.get(source, 1))



    # (3) Combine data arrays into subrankings arrays

    # get all states and initialize rankings
    states = np.unique(np.concatenate([sdata.State.values for sdata in data.values()]))
    subrankings = {}
    for source_type, st_list in source_types.items():

        subrankings[source_type] = pd.DataFrame({'State':states})
        subrankings[source_type]['City'] = '' # initialize
        for sdata in [data[source] for source in st_list]:
            subrankings[source_type] = pd.concat([subrankings[source_type], sdata])
        subrankings[source_type] = subrankings[source_type].drop_duplicates(['State', 'City'])[['State', 'City']]

        # initialize results columns so that they appear in the beginning of the structure
        subrankings[source_type]['M'] = np.nan # initialize
        subrankings[source_type]['n'] = np.nan # initialize
        subrankings[source_type]['avgPSW'] = np.nan # this will later hold the average weight

        # combine individual metrics into rankings
        for source in st_list:
            sdata = data[source][['State', 'City', 'B', 'PSW']].rename(columns={'B': f'B_{source}', 'PSW': f'PSW_{source}'})
            subrankings[source_type] = pd.merge(subrankings[source_type], sdata, on=['State', 'City'], how='left')

        # city rows inherit state-level data from their own state (city-level sources stay city-specific)
        BPSWi = [f'{x}_{source}' for source in st_list for x in ('B', 'PSW')]
        subrankings[source_type] = fill_from_state(subrankings[source_type], BPSWi)

        # a source only counts towards the weights where it has a value
        for source in st_list:
            no_value = subrankings[source_type][f'B_{source}'].isna()
            subrankings[source_type].loc[no_value, f'PSW_{source}'] = np.nan

        # weighted average: sum(B*PSW) / sum(PSW), written as the mean of B*PSW/avgPSW
        PSWi = [f'PSW_{source}' for source in st_list]
        subrankings[source_type]['avgPSW'] = subrankings[source_type][PSWi].mean(axis=1)
        for source in st_list:
            subrankings[source_type][f'M_{source}'] = subrankings[source_type][f'B_{source}'] * subrankings[source_type][f'PSW_{source}']
            subrankings[source_type][f'M_{source}'] = subrankings[source_type][f'M_{source}'].divide(subrankings[source_type]['avgPSW'])

        # sum and average M values from each source
        Mi = [f'M_{source}' for source in st_list]
        subrankings[source_type]['n'] = subrankings[source_type][Mi].count(axis=1).astype(int) # number of non null Mi entries
        subrankings[source_type]['M'] = subrankings[source_type][Mi].mean(axis=1)

        subrankings[source_type].sort_values(by=['State', 'City'], inplace=True)

        if verbose:
            print(subrankings[source_type][['State', 'City', 'M', 'n']].sort_values('City', ascending=False))#.to_string())



    # (4) Combine subrankings into final rankings

    rankings = pd.DataFrame({'State':states})
    rankings['City'] = '' # initialize
    rankings['M'] = np.nan # initialize
    rankings['n'] = np.nan # initialize
    for source_type, stdata in subrankings.items():
        rankings = pd.merge(rankings, stdata[['State', 'City', 'M', 'n']], on=['State', 'City'], how='outer', suffixes=(None, f'_{source_type}'))

    # fill data from source_types missing cities with the state-level result for that source_type
    rankings.sort_values(by=['State', 'City'], inplace=True)
    rankings = fill_from_state(rankings, [f'{x}_{st}' for st in source_types for x in ('M', 'n')])

    Mst = [f'M_{st}' for st in source_types]
    rankings['n'] = rankings[[f'n_{st}' for st in source_types]].sum(axis=1).astype(int)
    rankings['M'] = rankings[Mst].mean(axis=1)

    # flag categories without data (the composite averages over the categories that are present)
    rankings['n_categories'] = rankings[Mst].notna().sum(axis=1)
    missing = rankings[Mst].isna().to_numpy()
    rankings['missing_categories'] = [', '.join(st for st, m in zip(source_types, row) if m) for row in missing]
    if min_categories is not None:
        rankings.loc[rankings['n_categories'] < min_categories, 'M'] = np.nan
    rankings.insert(rankings.columns.get_loc('M') + 1, 'GAR', gar_zone(rankings['M']))

    return rankings


def gar_zone(M, cutoffs=GAR_CUTOFFS):
    """Green/Amber/Red zone for composite scores M ('' where M is missing)"""
    M = pd.Series(M)
    return np.where(M.isna(), '', np.where(M >= cutoffs['Green'], 'Green', np.where(M >= cutoffs['Amber'], 'Amber', 'Red')))


def fill_from_state(df, cols):
    """Fill missing values in city rows with the values from the state-level (City == '') row of the same state

    Args:
        df: data with 'State' and 'City' columns, including one City == '' row per state
        cols: columns to fill

    Returns:
        df: data with city rows filled
    """
    state_rows = df[df['City'] == ''].drop_duplicates('State').set_index('State')[cols]
    is_city = df['City'] != ''
    inherited = state_rows.reindex(df.loc[is_city, 'State']).set_index(df.index[is_city])
    df.loc[is_city, cols] = df.loc[is_city, cols].fillna(inherited)

    return df

def assign_CompScore(sdata, source, n_ranked=None):
    """Assign composite scores

    Args:
        sdata: source data
        source: source name
        n_ranked: for Rank sources, the number of places the ranking covers when the file lists only
            some of them (n_ranked in source_metadata.json); otherwise the number of rows is used

    Returns:
        sdata: source data, but with composite scores assigned
    """
    if 'Score' in sdata.keys():
        sdata['B'] = sdata.Score / 10 # Score is on a 0-100 scale (checked by validate_source)
    elif 'Rank' in sdata.keys():
        nNorm = n_ranked or len(sdata.Rank) # this should be the number of states... (50, 51?)
        if sdata.Rank.max() > nNorm:
            print(f' ---   WARNING: {source} has ranks up to {sdata.Rank.max()} but only {nNorm} rows; set n_ranked in source_metadata.json if the list is partial')
            nNorm = sdata.Rank.max()
        compscore = (nNorm-(sdata.Rank-1)) / (nNorm/10) # normalized ranking (0-10)
        sdata['B'] = compscore
    elif 'Processed' in sdata.keys():
        sdata['B'] = sdata.Processed

    return sdata

def normalize_CompScore(sdata):
    """Normalize composite scores

    Args:
        sdata: source data

    Returns:
        sdata: source data, but normalized
    """
    minScore = sdata['B'].min()
    maxScore = sdata['B'].max()
    if maxScore == minScore:
        print(' ---   WARNING: a source has the same score everywhere, so it carries no information after normalization and is skipped')
        sdata['B'] = np.nan
        return sdata
    sdata['B'] = (sdata['B']-minScore) / (maxScore-minScore) * 10

    return sdata

def assign_PSW(sdata, P, W):
    """Assign individual weightings for each entry

    Args:
        sdata: source data
        P: perceived hierarchy for this source, scored from 1-5 (5 being most trusted)
        W: repetition weight for this source, 1/k for k sources of the same subtype in its category
    Returns:
        sdata: source data, but with individual measures assigned
    """
    sdata['P'] = P

    # sensitivity index (S): Rank metric sensitivity and normalize from 1-2
    S_city = 2
    S_state = 1
    sdata['S'] = np.where(sdata.City == '', S_state, S_city)

    sdata['W'] = W

    sdata['PSW'] = sdata['P'] * sdata['S']* sdata['W']

    # to get a true weighted average, we need to divide by the sum of the weights... this is done later...
    return sdata

if __name__ == '__main__':
    gardnm()
