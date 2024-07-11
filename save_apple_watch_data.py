import os
from datetime import datetime
import logging
import pandas as pd

from read_apple_watch_data import *
# SHOW_ saveS = True

# create logger object
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# TODO: add requirements text file for python libraries needed and respective versions
# TODO: Add start and end dates to  save (sub)titles


def save_heart_rate(apple_watch):

    logger.info('Loading and  saveting Heart Rate Data')
    df = apple_watch.load_heart_rate_data()
 
    df['date'] = list(map(lambda dt: dt.strftime('%m/%d/%y'), df['start_timestamp']))
    df['time'] = list(map(lambda d: d.time(), df['start_timestamp']))
    df.to_csv('download/heart_rate.csv', index=False)

def save_heart_rate_variability(apple_watch):

    logger.info('Loading and  saveting Heart Rate Variability Data')
    df = apple_watch.load_heart_rate_variability_data()
 
    df['date'] = list(map(lambda d: d.strftime('%m/%d/%y'), df['start_timestamp']))
    df['time'] = list(map(lambda d: d.strftime('%H:%M:%S'), df['start_timestamp']))
    dates = list(df['date'].unique())

    # remove instantaneous data, bokeh doesn't not like dictionary format
    del df['instantaneous_bpm']
    df.to_csv('download/heart_rate_variability.csv', index=False)

def save_resting_heart_rate(apple_watch):

    logger.info('Loading and  saveting Resting Heart Rate Data')
    df = apple_watch.load_resting_heart_rate_data()
 
    df['date'] = list(map(lambda dt: dt.strftime('%m/%d/%y'), df['start_timestamp']))
    # save dataframe
    df.to_csv('download/resting_heart_rate.csv', index=False)

def save_walking_heart_rate(apple_watch):
    logger.info('Loading and  saveting Walking/Running Data')
    df = apple_watch.load_walking_heart_rate_data()
 
    df['date'] = list(map(lambda dt: dt.strftime('%m/%d/%y'), df['start_timestamp']))

    # save dataframe
    df.to_csv('download/walking_heart_rate.csv', index=False)

def save_distance(apple_watch):

    logger.info('Loading and  saveting Distance Walked/Ran Data')
    df = apple_watch.load_distance_data()
 
    df['date'] = list(map(lambda d: d.strftime('%m/%d/%y'), df['start_timestamp']))
    df['hour'] = list(map(lambda d: int(d.strftime('%H')), df['start_timestamp']))

    # group by hour and date and calculate sum of steps
    hourly_distance = df.groupby(['hour', 'date'])['distance_walk_run'].agg(['sum']).reset_index()
    hourly_distance.rename(columns={'sum': 'distance'}, inplace=True)

    # resort by date
    hourly_distance['datetime'] = pd.to_datetime(hourly_distance['date'])
    hourly_distance.sort_values(by=['datetime'], inplace=True)
    dates = hourly_distance['date'].unique()


    # save dataframe
    df.to_csv('download/distance_walked_ran.csv', index=False)

def save_basal_energy(apple_watch):

    logger.info('Generating Basal Energy  save')

    df = apple_watch.load_basal_energy_data()
 
    df['date'] = list(map(lambda d: d.strftime('%m/%d/%y'), df['start_timestamp']))
    df['hour'] = list(map(lambda d: int(d.strftime('%H')), df['start_timestamp']))

    # group by hour and date and calculate sum of steps
    basal_energy = df.groupby(['hour', 'date'])['energy_burned'].agg(['sum']).reset_index()
    basal_energy.rename(columns={'sum': 'energy_burned'}, inplace=True)

    # resort date
    basal_energy['datetime'] = pd.to_datetime(basal_energy['date'])
    basal_energy.sort_values(by=['datetime'], inplace=True)

    # save dataframe
    df.to_csv('download/basal_energy.csv', index=False)

def save_stand_hour(apple_watch):
    logger.info('Loading and Generating Stand Hour Heat Map')

    df = apple_watch.load_stand_hour_data()
 
    df['date'] = list(map(lambda d: d.strftime('%m/%d/%y'), df['start_timestamp']))
    df['hour'] = list(map(lambda d: int(d.strftime('%H')), df['start_timestamp']))
    df['stand_hour'] = list(map(lambda label: 1 if label == 'Stood' else 0, df['stand_hour']))
    # save dataframe
    df.to_csv('download/stand_hour.csv', index=False)

def save_steps(apple_watch):
    logger.info('Loading and Generating Steps Heat Map')
    df = apple_watch.load_step_data()
 
    df['date'] = list(map(lambda d: d.strftime('%m/%d/%y'), df['start_timestamp']))
    df['hour'] = list(map(lambda d: int(d.strftime('%H')), df['start_timestamp']))

    # save data frame
    df.to_csv('download/step_counts.csv', index=False)

def tocsv(apple_watch):

    try:
         save_heart_rate(apple_watch)
    except (IndexError, ValueError):
        logger.warning('Missing heart rate data!')

    try:
         save_heart_rate_variability(apple_watch)
    except (IndexError, ValueError):
        logger.warning('Missing heart rate variability data!')

    try:
         save_resting_heart_rate(apple_watch)
    except (IndexError, ValueError):
        logger.warning('Missing resting heart rate data!')

    try:
         save_walking_heart_rate(apple_watch)
    except (IndexError, ValueError):
        logger.warning('Missing walking heart rate data!')

    try:
         save_distance(apple_watch)
    except (IndexError, ValueError):
        logger.warning('Missing distance walked data!')

    try:
         save_basal_energy(apple_watch)
    except (IndexError, ValueError):
        logger.warning('Missing basal energy data!')

    try:
         save_stand_hour(apple_watch)
    except (IndexError, ValueError):
        logger.warning('Missing stand hour data!')

    try:
         save_steps(apple_watch)
    except (IndexError, ValueError):
        logger.warning('Missing step count data!')