'''
Visualizing Apple Watch Health Data w/ Plotly
'''
import os
from datetime import datetime
import logging
import pandas as pd
import plotly.graph_objects as go
from read_apple_watch_data import *

# create logger object
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def plot_heart_rate(apple_watch):
    """
    Superposition multiple time series plots of heart data

    :param apple_watch: data frame of heart rate data
    :return: Plotly graph object
    """
    logger.info('Loading and Plotting Heart Rate Data')
    df = apple_watch.load_heart_rate_data()
    df = df[(df['start_timestamp'] > START_DATE) & (df['start_timestamp'] < END_DATE)]
    df['date'] = list(map(lambda dt: dt.strftime('%m/%d/%y'), df['start_timestamp']))
    df['time'] = list(map(lambda d: d.time(), df['start_timestamp']))

    fig = go.Figure()

    # superpose time series plots for each date
    dates = df['date'].unique()
    for idx, dt in enumerate(dates):
        sub_df = df[df['date'] == dt][['time', 'heart_rate']]
        fig.add_trace(go.Scatter(x=sub_df['time'], y=sub_df['heart_rate'], mode='markers', name=dt))

    fig.update_layout(
        title='Apple Watch Heart Rate Data',
        xaxis_title='Hour',
        yaxis_title='Average Beats Per Minute',
        hovermode='closest'
    )

    return fig

def plot_heart_rate_variability(apple_watch):
    """
    Generate swarm-like plots of heart rate variability measures for multiple days

    :param apple_watch: data frame of heart rate variability data
    :return: Plotly graph object
    """
    logger.info('Loading and Plotting Heart Rate Variability Data')
    df = apple_watch.load_heart_rate_variability_data()
    df = df[(df['start_timestamp'] > START_DATE) & (df['start_timestamp'] < END_DATE)]
    df['date'] = list(map(lambda d: d.strftime('%m/%d/%y'), df['start_timestamp']))
    df['time'] = list(map(lambda d: d.strftime('%H:%M:%S'), df['start_timestamp']))
    dates = list(df['date'].unique())

    fig = go.Figure()

    for date in dates:
        sub_df = df[df['date'] == date]
        fig.add_trace(go.Box(x=sub_df['date'], y=sub_df['heart_rate_variability'], name=date))

    fig.update_layout(
        title='Apple Watch Heart Rate Variability (SDNN)',
        xaxis_title='Date',
        yaxis_title='Time Between Heart Beats (ms)',
        hovermode='closest'
    )

    return fig

def run(apple_watch, start_date, end_date, show_plots):
    global START_DATE, END_DATE
    SHOW_PLOTS = show_plots

    try:
        START_DATE = datetime.strptime(start_date, '%Y-%m-%d %H:%M')
        END_DATE = datetime.strptime(end_date, '%Y-%m-%d %H:%M')
    except ValueError:
        START_DATE = datetime.strptime(start_date, '%m/%d/%y %H:%M')
        END_DATE = datetime.strptime(end_date, '%m/%d/%y %H:%M')
    except Exception as e:
        logger.error('Unrecognized date format...raising ValueError.')
        raise ValueError()
