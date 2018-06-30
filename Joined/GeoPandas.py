#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 28 17:55:50 2018

@author: Garrett
"""

#%% Packages

# %matplotlib inline #used for notebook grpahs

from __future__ import (absolute_import, division, print_function)
import matplotlib.pyplot as plt
from shapely.geometry import Point
import pandas as pd
import geopandas as gpd
from geopandas import GeoDataFrame
import datetime as dt

#%% Data
Windows = 'C:/Users/paperspace/Desktop'
Linux = '/home/sade/Desktop/Git Cloned Repos/lights-and-crime/Lights and Crime Garrett/Data'

choice = Windows

Lights = pd.read_excel(choice + '/Lights.xlsx')
NCR = pd.read_excel(choice + '/NCR.xlsx')

geometry = [Point(xy) for xy in zip(Lights['gpsX'], Lights['gpsY'])]
gLights = GeoDataFrame(Lights, geometry=geometry)
gLights = gLights.drop_duplicates(subset = ['WoID'])
geometry = [Point(xy) for xy in zip(NCR['gpsX'], NCR['gpsY'])]
gNCR = GeoDataFrame(NCR, geometry=geometry)

BUFFER = .0008 #4th a city block
#BUFFER = .00125 #4th a city block

gLights_Buff = gLights.assign(geometry = lambda x: x.geometry.buffer(BUFFER)) 
# Overwrites geometry variable with a buffer centered at the point of interest. A.k.a. applies the function geometry(x) to gNCR and saves it as geometry.

Matched_Lights = gpd.sjoin(gLights_Buff, gNCR, 'left')
# Left geojoin by buffer

#%% Filtering
Matched_Lights['Tdelta'] = [0]*len(Matched_Lights)

Matched_Lights = Matched_Lights.dropna(subset = ['WoCompleted'])
Matched_Lights = Matched_Lights.dropna(subset = ['REPORT_DAT'])
Matched_Lights = Matched_Lights.reset_index()

# Flagging possible lights that influenced crime:
for i in range(len(Matched_Lights)):
    try:
        if abs(Matched_Lights.loc[i, 'WoCompleted'] - Matched_Lights.loc[i, 'REPORT_DAT']).days <= 10:
            Matched_Lights.loc[i, 'Tdelta'] = 1
    except:
        Matched_Lights.loc[i, 'WoCompleted'] = dt.datetime.strptime(Matched_Lights.loc[i, 'WoCompleted'], '%Y-%m-%dT%H:%M:%S.%fZ') # Some values coded incorrectly.
        if abs(Matched_Lights.loc[i, 'WoCompleted'] - Matched_Lights.loc[i, 'REPORT_DAT']).days <= 10:
            Matched_Lights.loc[i, 'Tdelta'] = 1

sum(Matched_Lights['Tdelta'])/len(Matched_Lights) # Hit Ratio =  (Number of possible crimes to be linked with a light outage)

Matched_Lights0 = Matched_Lights[Matched_Lights['Tdelta'] == 0].drop_duplicates(subset = ['WoID'])
Matched_Lights1 = Matched_Lights[Matched_Lights['Tdelta'] == 1].drop_duplicates(subset = ['OBJECTID'])

#%% To excel

Matched_Lights.to_excel(choice + '/geoLights.xlsx')

#%% Play

#and (Matched_Lights.loc[i, 'WoCompleted'] - Matched_Lights.loc[i, 'REPORT_DAT']).days > 0