import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
from gen_ma_cross_table import gen_ma_cross_table

def gen_buyhold_comp(df, ma1, ma2):
    gen_ma_cross_table(df, ma1, ma2)
#buy/hold plot
    plt.plot(df['Cumulative Return'], label='Buy/Hold')
#model plot
    plt.plot(df['Cumulative Model Return'], label='Model')
    plt.legend(loc=2)
    plt.grid(True, alpha=.5)
#print returns
    print("Cumulative Buy/Hold Return:", round(df['Cumulative Return'].iloc[-1], 2))
    print("Cumulative Model Return:", round(df['Cumulative Model Return'].iloc[-1], 2))