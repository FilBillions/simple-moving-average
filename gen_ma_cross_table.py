import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# generates a table with moving averages and crossover signals

def gen_ma_cross_table(df, ma1, ma2):
#adding day count
    day_count = np.arange(1, len(df) + 1)
    df['Day Count'] = day_count

#dropping volume column
    if 'Volume' in df.columns:
        df.drop(columns=['Volume'], inplace = True)
    df[f'{ma1}-day MA'] = df['Close'].rolling(int(ma1)).mean().shift()
    df[f'{ma2}-day MA'] = df['Close'].rolling(int(ma2)).mean().shift()
#we .shift() to push the moving average forward a day because the moving average cannot start until x days have finished

#signal to long
    df['Signal'] = np.where(df[f'{ma1}-day MA'] > df[f'{ma2}-day MA'], 1, 0)

#signal to short
    df['Signal'] = np.where(df[f'{ma1}-day MA'] < df[f'{ma2}-day MA'], -1, df['Signal'])

#create returns and the model returns colummns
# the difference between the current row ln and previous row ln gives a daily return
    df['Daily Return'] = (np.log(df['Close']).diff()) * 100

# model return, if our signal is - we are short and the daily return is negative. vice versa
    df['Model Return'] = df['Daily Return'] * df['Signal']

#entry column for visualization
    df['Entry'] = df.Signal.diff()
    df.dropna(inplace=True)

#Cumulative Returns
    df['Cumulative Return'] = (np.exp(df['Daily Return'] / 100).cumprod() - 1) * 100
    df['Cumulative Model Return'] = (np.exp(df['Model Return'] / 100).cumprod() - 1) * 100

#formatting the table
    df = round((df[['Day Count', 'Open', 'High', 'Low', 'Close', f'{ma1}-day MA', f'{ma2}-day MA', 'Daily Return', 'Cumulative Return', 'Model Return', 'Cumulative Model Return', 'Signal', 'Entry']]), 3)
    return df.head()