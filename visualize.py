# input: time series ==> output: smoothed time series
import numpy as np
import pandas as pd
from scipy import signal
import matplotlib.pyplot as plt


def visualize(X):
    y = smooth(X)
    ax = np.linspace(0, 24 , y.shape[0])  # X-Axis to plot 0-24H
    print(ax.shape)
    print(y.shape)
    plt.plot(ax, y)
    plt.savefig('foo.png', bbox_inches='tight')



def smooth(day):
    L = 30  # L-point Moving Average filter
    b = (np.ones(L)) / L  # numerator co-effs of filter transfer function
    a = np.ones(1)  # denominator co-effs of filter transfer function
    x = day
    y = signal.lfilter(b, a, x)  # filter output using lfilter function
    return y