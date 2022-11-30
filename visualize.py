# input: time series ==> output: smoothed time series
import numpy as np
import pandas as pd
from scipy import signal
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure


def visualize(X):
    ys = smooth(X)
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    xs = np.linspace(0, 24 , ys.shape[0])
    axis.plot(xs, ys)
    return fig



def smooth(day):
    L = 30  # L-point Moving Average filter
    b = (np.ones(L)) / L  # numerator co-effs of filter transfer function
    a = np.ones(1)  # denominator co-effs of filter transfer function
    x = day
    y = signal.lfilter(b, a, x)  # filter output using lfilter function
    return y