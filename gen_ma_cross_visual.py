import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from gen_ma_cross_table import gen_ma_cross_table

def gen_ma_cross_visual(df, ma1, ma2, model_days, ticker):
    gen_ma_cross_table(df, ma1, ma2)
#parameters for grid size
    plt.rcParams['figure.figsize'] = 12, 8
#create grid
    plt.grid(True, alpha = .5)
#plot ticker closing prices and MAs, .iloc for integers
    plt.plot(df.iloc[-model_days:]['Close'], label = f'{ticker.upper()}')
    plt.plot(df.iloc[-model_days:][f'{ma1}-day MA'], label = f'{ma1}-day MA')
    plt.plot(df.iloc[-model_days:][f'{ma2}-day MA'], label = f'{ma2}-day MA')
#plotting entry points, .loc for labels
    plt.plot(df[-model_days:].loc[df.Entry == 2].index, df[-model_days:][f'{ma1}-day MA'][df.Entry == 2], '^', color = 'g', markersize = 10)
    plt.plot(df[-model_days:].loc[df.Entry == -2].index, df[-model_days:][f'{ma2}-day MA'][df.Entry == -2], 'v', color = 'r', markersize = 10)
#plot legend
    plt.legend(loc=2)