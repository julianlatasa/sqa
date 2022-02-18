# -*- coding: utf-8 -*-
"""
Created on Mon Jan 24 14:50:11 2022

@author: U54979
"""
#pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org fitdecode

from zipfile import ZipFile
from datetime import datetime, timedelta
from typing import Dict, Union, Optional,Tuple


import pandas as pd
import os
import fitdecode

# The names of the columns we will use in our points DataFrame. For the data we will be getting
# from the FIT data, we use the same name as the field names to make it easier to parse the data.
POINTS_COLUMN_NAMES = ['latitude', 'longitude', 'lap', 'altitude', 'distance', 'timestamp', 'heart_rate', 'cadence', 'speed', 'power', 'Power']

# The names of the columns we will use in our laps DataFrame. 
LAPS_COLUMN_NAMES = ['number', 'start_time', 'total_distance', 'total_elapsed_time',
                     'max_speed', 'max_heart_rate', 'avg_heart_rate']

LENGTHS_COLUMN_NAMES = ['total_elapsed_time', 'swim_stroke', 'length_type', 'timestamp']


def get_fit_lap_data(frame: fitdecode.records.FitDataMessage) -> Dict[str, Union[float, datetime, timedelta, int]]:
    """Extract some data from a FIT frame representing a lap and return
    it as a dict.
    """
    
    data: Dict[str, Union[float, datetime, timedelta, int]] = {}
    
    for field in LAPS_COLUMN_NAMES[1:]:  # Exclude 'number' (lap number) because we don't get that
                                        # from the data but rather count it ourselves
        if frame.has_field(field):
            data[field] = frame.get_value(field)
    
    return data

def get_fit_point_data(frame: fitdecode.records.FitDataMessage) -> Optional[Dict[str, Union[float, int, str, datetime]]]:
    """Extract some data from an FIT frame representing a track point
    and return it as a dict.
    """
    
    data: Dict[str, Union[float, int, str, datetime]] = {}
    
    if not (frame.has_field('position_lat') and frame.has_field('position_long')):
        # Frame does not have any latitude or longitude data. We will ignore these frames in order to keep things
        # simple, as we did when parsing the TCX file.
        #return None
        data['latitude'] = 0
        data['longitude'] = 0
    elif (not(frame.get_value('position_lat') is None) and not(frame.get_value('position_long') is None)):
        data['latitude'] = frame.get_value('position_lat') / ((2**32) / 360)
        data['longitude'] = frame.get_value('position_long') / ((2**32) / 360)
    
    for field in POINTS_COLUMN_NAMES[3:]:
        if frame.has_field(field):
            data[field] = frame.get_value(field)
    
    return data
    
def get_fit_length_data(frame: fitdecode.records.FitDataMessage):
    """Extract some data from an FIT frame representing a track point
    and return it as a dict.
    """
    
    data: Dict[str, Union[float, int, str, datetime]] = {}
    
    for field in LENGTHS_COLUMN_NAMES:
        if frame.has_field(field):
            data[field] = frame.get_value(field)
    
    return data


def get_dataframes(fname: str): # -> Tuple[pd.DataFrame, pd.DataFrame, String]:
    """Takes the path to a FIT file (as a string) and returns two Pandas
    DataFrames: one containing data about the laps, and one containing
    data about the individual points.
    """

    points_data = []
    lengths_data = []
    laps_data = []
    sport = ''
    lap_no = 1
    with fitdecode.FitReader(fname) as fit_file:
        for frame in fit_file:
            if isinstance(frame, fitdecode.records.FitDataMessage):
                if frame.name == 'record':
                    single_point_data = get_fit_point_data(frame)
                    if single_point_data is not None:
                        single_point_data['lap'] = lap_no
                        points_data.append(single_point_data)
                elif frame.name == 'lap':
                    single_lap_data = get_fit_lap_data(frame)
                    single_lap_data['number'] = lap_no
                    laps_data.append(single_lap_data)
                    lap_no += 1
                elif frame.name == 'length':
                    single_length_data = get_fit_length_data(frame)
                    if single_length_data is not None:
                        single_length_data['lap'] = lap_no
                        lengths_data.append(single_length_data)
                elif frame.name == 'sport':
                    sport = frame.get_value('sport')
    
    # Create DataFrames from the data we have collected. If any information is missing from a particular lap or track
    # point, it will show up as a null value or "NaN" in the DataFrame.
    
    laps_df = pd.DataFrame(laps_data, columns=LAPS_COLUMN_NAMES)
    laps_df.set_index('number', inplace=True)
    points_df = pd.DataFrame(points_data, columns=POINTS_COLUMN_NAMES)
    lengths_df = pd.DataFrame(lengths_data, columns=LENGTHS_COLUMN_NAMES)
    return laps_df, points_df, lengths_df, sport

def extract_zip(input_zip):
    input_zip=ZipFile(input_zip)
    return {name: input_zip.read(name) for name in input_zip.namelist()}

def cycling_norm_power(Power):

    WindowSize = 30; # second rolling average

    NumberSeries = pd.Series(Power)
    NumberSeries = NumberSeries.dropna()
    Windows      = NumberSeries.rolling(WindowSize)
    Power_30s    = Windows.mean().dropna()

    PowerAvg     = round(Power_30s.mean(),0)

    NP = round((((Power_30s**4).mean())**0.25),0)

    return(NP,PowerAvg)

if __name__ == '__main__':
    
    #from sys import argv
    #fname = argv[1]  # Path to FIT file to be given as first argument to script
    
    #pepe = extract_zip("./8170934157.zip")
    #print(pepe['7753172614_ACTIVITY.fit'])
    #laps_df, points_df, sport = get_dataframes(pepe['8170934157_ACTIVITY.fit'])
    #laps_df, points_df = get_dataframes("./7753172614_ACTIVITY.fit")
    #print('LAPS:')
    #print(laps_df)
    #print('\nPOINTS:')
    #print(points_df)
    
    data_tss = []
    
    files = os.listdir()
    for file in files:
        if (file[-4:] == '.zip'):
            data: Dict[str, Union[float, int, str, datetime]] = {}
            data['file'] = file
            #print(file)
            pepe = extract_zip("./" + file)
            laps_df, points_df, lengths_df, sport = get_dataframes(pepe[file[:-4] + '_ACTIVITY.fit'])

            data['sport'] = sport
            if (sport == 'running') :
                points_df['dist'] = points_df['distance'] - points_df['distance'].shift()
                points_df['alt'] = points_df['altitude'] - points_df['altitude'].shift()
                points_df['grad'] = (points_df['alt'] / points_df['dist']) * 100
                points_df['ngp'] = points_df['dist']*(0.98462+(0.030266 * points_df['grad']) + (0.0018814 * points_df['grad'])**2 +(-0.0000033882 * points_df['grad'])**3+(-0.00000045704 * points_df['grad'])**4)
                points_df['speed'] = 1/(points_df['dist']/(1000/60))
                points_df['speedngp'] = 1/(points_df['ngp']/(1000/60))
                rFTP = 1/(257/1000)
                rTSS = ((points_df['ngp'].count() * points_df['ngp'].mean() * (points_df['ngp'].mean() / rFTP))/(rFTP * 3600)) * 100
                #rTSS =  (points_df['ngp'].mean() * rFTP)**2 * points_df['ngp'].count() / 3600
                data['timestamp'] = points_df['timestamp'].head(1)
                data['tss'] = rTSS
                #print('Run TSS: ')
                #print(rTSS)
            elif (sport == 'swimming') :
                total_time = lengths_df.query("length_type == 'active'")['total_elapsed_time'].sum() / 60
                total_dist = lengths_df.query("length_type == 'active'")['total_elapsed_time'].count() * 25
                sFTP = 1000 / ( (18 * 60 + 20 ) / 60) #es CSS o test 100 m/min
                NSS = total_dist/total_time #Expresar en m/min
                sTSS = (NSS/sFTP)**3 * (total_time / 60 ) * 100
                data['timestamp'] = lengths_df['timestamp'].head(1)
                data['tss'] = sTSS
                #print('Swim TSS: ')
                #print(sTSS)
            elif (sport == 'cycling') :
                #total_time = lengths_df.query("length_type == 'active'")['total_elapsed_time'].sum() / 60
                #total_dist = lengths_df.query("length_type == 'active'")['total_elapsed_time'].count() * 25
                #sFTP = 1000 / ( (18 * 60 + 20 ) / 60) #es CSS o test 100 m/min
                #NSS = total_dist/total_time #Expresar en m/min
                #sTSS = (NSS/sFTP)**3 * (total_time / 60 ) * 100
                np, avgpower = cycling_norm_power(points_df['power'])
                FTP = 219
                TSS = ((np * (np/FTP) * points_df['power'].count()) / (3600 * FTP)) * 100
                data['timestamp'] = points_df['timestamp'].head(1)
                data['tss'] = TSS
                #print('Cycling TSS: ')
                #print(TSS)
            data_tss.append(data)
    
    tss_df = pd.DataFrame(data_tss)


