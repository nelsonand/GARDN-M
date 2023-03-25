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
import pandas
import os
import json

# establish relative directories
repo = git.Repo('.', search_parent_directories=True)
os.chdir(repo.working_tree_dir)

# get source data
with open('./data/sources/source_ratings.json', 'r') as f:
    source_ratings = json.load(f)
    
# get processed data
datadir = './data/processed_data/'

# for source in source_ratings.keys():
data = pandas.read_csv(datadir+'usnews_state_equality_rankings.csv')

print(source_ratings)    
 
