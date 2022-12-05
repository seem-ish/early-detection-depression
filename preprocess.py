# Take a dataframe and then output the features
import numpy as np
import pandas as pd
import sympy as sym
from sympy import *


def preprocess(f_name):
    HH_MM, activity = gather_data(f_name)
    return feature_extract(activity)


def gather_data(f_name):  # bridge function: use rearrange_in_days and read_subject together
    HH_MM, activity = read_subject(f_name)
    #days = rearrange_in_days(HH_MM, activity)
    # return days
    return HH_MM, activity


def read_subject(f_name):  # read subject data from the folder;
    #filename = cohort+"_"+str(subj)+".csv"
    file = pd.read_csv(f_name, sep='\t')

    timestamps = file.iloc[:, [1]]
    dates = file.iloc[:, [2]]
    activity = file.iloc[:, [3]]
    HH_MM = convert_timestamps(timestamps)

    # convert dataframe to array
    activity = np.array(activity)
    activity = activity.reshape(-1)

    return HH_MM, activity


def convert_timestamps(timestamps):  # panda series ==to==> [Hours][Minutes] (list)
    from datetime import datetime
    HH_MM = [0]*len(timestamps)
    for i in range(len(timestamps)):
        t = timestamps.iloc[i][0]
        d = datetime.strptime(t, '%Y-%m-%d %H:%M:%S')
        h, m = d.hour, d.minute
        HH_MM[i] = h, m
    return HH_MM


def feature_extract(day):
    daylength = len(day)
    t = np.linspace(0, 360-(360/daylength), daylength)
    f1 = np.mean(day)
    f2 = np.std(day)
    f3 = np.max(day)
    f, f4, f5, f6 = cosinor(t, day)
    f8 = np.sum(day)**2
    return np.array([f1, f2, f3, f5, f6])


# cosinor function: doing the fit ourselves
def cosinor(t, y):
    t = t/360

    w = np.pi*2
    n = len(t)

    x = np.cos(w*t)
    z = np.sin(w*t)

    NE = sym.Matrix([[n,         np.sum(x),    np.sum(z),    np.sum(y)],
                     [np.sum(x), np.sum(x**2), np.sum(x*z),  np.sum(x*y)],
                     [np.sum(z), np.sum(x*z),  np.sum(z**2), np.sum(z*y)]])
    RNE = NE.rref()
    RNE = np.array(RNE[0])

    M = float(RNE[0][3])
    beta = float(RNE[1][3])
    gamma = float(RNE[2][3])

    import math
    Amp = math.sqrt((beta**2 + gamma**2))
    theta = np.arctan2(np.abs(gamma), np.abs(beta))

    # Calculate acrophase (phi) and convert from radians to degrees
    a = np.sign(beta)
    b = np.sign(gamma)
    if (a == 1 or a == 0) and b == 1:
        phi = -theta
    elif a == -1 and (b == 1 or b == 0):
        phi = -pi + theta
    elif (a == -1 or a == 0) and b == -1:
        phi = -pi - theta
    elif a == 1 and (b == -1 or b == 0):
        phi = -2*pi + theta

    phi = float(phi)

    f = M + Amp*np.cos(w*t+phi)

    return f, M, Amp, phi
