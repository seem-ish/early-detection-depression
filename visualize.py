# input: time series ==> output: smoothed time series
import numpy as np
import pandas as pd
from scipy import signal
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure


def visualize(file_path):
    df = pd.read_csv(file_path, sep='\t')
    df.timestamp = df.timestamp.str.split(' ', expand=True)[[1]]
    df['hour'] = df.timestamp.str.split(':', expand=True)[[0]]
    ab = df.groupby(['date', 'hour'])['activity'].mean()
    df_aggr = pd.DataFrame(columns=('date', 'hour', 'activity'))
    date = ''
    for i in range(0, len(ab)):
        df_aggr = df_aggr.append({'date': ab.index[i][0], 'hour': ab.index[i][1], 'activity': ab[i]},
                                 ignore_index=True)
        date = ab.index[i][0]
    plt.figure()
    plt.plot(df_aggr['hour'], df_aggr['activity'])
    plt.xlabel('Hour')
    plt.ylabel('Activity')
    plt.ylim([0, 800])
    plt.title(f'Your Mean Activity chart for {date}')
    plt.savefig('static/img/fig1.png')
