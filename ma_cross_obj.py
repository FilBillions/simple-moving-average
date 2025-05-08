import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
from datetime import date, timedelta

class MovingAverageTable():
    def __init__(self, ma1, ma2, ticker, start = str(date.today() - timedelta(59)), end = str(date.today() - timedelta(1)), interval = "1d"):
        df = yf.download(ticker, start, end, interval = interval, multi_level_index=False)
        self.df = df
        self.ticker = ticker
        self.ma1 = ma1
        self.ma2 = ma2

    def run_algo(self, print_table=True):    
#adding day count
        day_count = np.arange(1, len(self.df) + 1)
        self.df['Day Count'] = day_count
        #dropping unnecessary columns
        if 'Volume' in self.df.columns:
                self.df.drop(columns=['Volume'], inplace = True)
        if 'Capital Gains' in self.df.columns:
                self.df.drop(columns=['Capital Gains'], inplace = True)
        if 'Dividends' in self.df.columns:
                self.df.drop(columns=['Dividends'], inplace = True)
        if 'Stock Splits' in self.df.columns:
                self.df.drop(columns=['Stock Splits'], inplace = True)

        # --- INITIALISE THE DATAFRAME ---
        # ---
        self.df['Return %'] = (np.log(self.df['Close']).diff()) * 100
        self.df['Cumulative Return %'] = (np.exp(self.df['Return %'] / 100).cumprod() - 1) * 100

        # ---
        #we .shift() to push the moving average forward a day because the moving average cannot start until x days have finished
        self.df[f'{self.ma1}-day MA'] = self.df['Close'].rolling(int(self.ma1)).mean().shift()
        self.df[f'{self.ma2}-day MA'] = self.df['Close'].rolling(int(self.ma2)).mean().shift()

        #signal to long
        self.df['Signal'] = np.where(self.df[f'{self.ma1}-day MA'] > self.df[f'{self.ma2}-day MA'], 1, 0)

        #signal to short
        self.df['Signal'] = np.where(self.df[f'{self.ma1}-day MA'] < self.df[f'{self.ma2}-day MA'], -1, self.df['Signal'])

        # model return %, if our signal is - we are short and the daily return % is negative. vice versa
        self.df['MA Model Return %'] = self.df['Return %'] * self.df['Signal']

        #entry column for visualization
        self.df['Entry'] = self.df.Signal.diff()

        # drop rows
        self.df.dropna(inplace = True)
        #Cumulative Return %s
        self.df['Cumulative MA Model Return %'] = (np.exp(self.df['MA Model Return %'] / 100).cumprod() - 1) * 100

        #recalc return % and cumulative return % to include model return %s
        self.df['Return %'] = (np.log(self.df['Close']).diff()) * 100
        self.df['Cumulative Return %'] = (np.exp(self.df['Return %'] / 100).cumprod() - 1) * 100

        #formatting the table
        self.df = round((self.df[['Day Count', 'Open', 'High', 'Low', 'Close', f'{self.ma1}-day MA', f'{self.ma2}-day MA', 'Return %', 'Cumulative Return %', 'MA Model Return %', 'Cumulative MA Model Return %', 'Signal', 'Entry']]), 3)

        if print_table:
            #options to show all rows and columns
            #pd.set_option('display.max_rows', None)
            #pd.set_option('display.max_columns', None)
            #pd.set_option('display.width', None)
            #pd.set_option('display.max_colwidth', None)
            return self.df
        pass

    def gen_visual(self):
        model_days = self.df['Day Count'].iloc[-1] - self.df['Day Count'].iloc[0] + 1
        #parameters for grid size
        self.df.index = pd.to_datetime(self.df.index).strftime('%Y-%m-%d-%H:%M')
        fig = plt.figure(figsize=(12, 8))

        # Use the actual index for x-values
        x_values = range(len(self.df.iloc[-model_days:])) 

        #plot ticker closing prices and MAs, .iloc for integers
        plt.plot(x_values, self.df.iloc[-model_days:]['Close'])
        plt.plot(x_values, self.df.iloc[-model_days:][f'{self.ma1}-day MA'], label = f'{self.ma1}-day MA')
        plt.plot(x_values, self.df.iloc[-model_days:][f'{self.ma2}-day MA'], label = f'{self.ma2}-day MA')

        # Plot buy signals (Entry == 2)
        plt.scatter(
            [x_values[i] for i in range(len(self.df.iloc[-model_days:])) if self.df.iloc[-model_days:].iloc[i]['Entry'] == 2],
            self.df.iloc[-model_days:]['Close'][self.df.iloc[-model_days:]['Entry'] == 2],
            marker='^', color='g', s=100, label='Buy Signal'
        )

        # Plot sell signals (Entry == -2)
        plt.scatter(
            [x_values[i] for i in range(len(self.df.iloc[-model_days:])) if self.df.iloc[-model_days:].iloc[i]['Entry'] == -2],
            self.df.iloc[-model_days:]['Close'][self.df.iloc[-model_days:]['Entry'] == -2],
            marker='v', color='r', s=100, label='Sell Signal'
        )

        # Set x-axis to date values and make it so they dont spawn too many labels
        plt.xticks(ticks=x_values, labels=self.df.iloc[-model_days:].index, rotation=45)
        plt.locator_params(axis='x', nbins=10)

        # create grid
        plt.grid(True, alpha = .5)
        # plot legend
        plt.legend(['Close', f'{self.ma1}-day MA', f'{self.ma2}-day MA', 'Buy Signal', 'Sell Signal'], loc = 2)

        #print statements        
        print(f'from {self.df.index[-model_days]} to {self.df.index[-1]}')
        print(f'count of buy signals: {len(self.df[self.df["Entry"] == 2])}')
        print(f'count of sell signals: {len(self.df[self.df["Entry"] == -2])}')

    def gen_comp(self):
        labels = pd.to_datetime(self.df.index).strftime('%Y-%m-%d')
        fig1= plt.figure(figsize=(12, 6))
        x_values = range(len(self.df))

        # add buy/hold to legend if it doesn't exist
        if f'{self.ticker} Buy/Hold' not in [line.get_label() for line in plt.gca().get_lines()]:
            plt.plot(x_values, self.df['Cumulative Return %'], label=f'{self.ticker} Buy/Hold')
        # model plot
        plt.plot(x_values, self.df['Cumulative MA Model Return %'], label=f'{self.ticker} MA Model')

        # Set x-axis to date values and make it so they dont spawn too many labels
        plt.xticks(ticks=x_values, labels=labels, rotation=45)
        plt.locator_params(axis='x', nbins=10)

        # grid and legend
        plt.legend(loc=2)
        plt.grid(True, alpha=.5)
        # print cumulative return % if not already printed
        print(f"{self.ticker} Cumulative MA Model Return %:", round(self.df['Cumulative MA Model Return %'].iloc[-1], 2))
        print(f"{self.ticker} Cumulative Return %:", round(self.df['Cumulative Return %'].iloc[-1], 2))
        print(f" from {self.df.index[0]} to {self.df.index[-1]}")

    def sharpe(self):
        buyhold_avg_r = float((np.mean(self.df['Return %'])))
        buyhold_std = float((np.std(self.df['Return %'])))
        buyhold_sharpe = (buyhold_avg_r / buyhold_std) * 252 ** 0.5
        model_avg_r = float((np.mean(self.df['MA Model Return %'])))
        model_std = float((np.std(self.df['MA Model Return %'])))
        model_sharpe = (model_avg_r / model_std) * 252 ** 0.5
        print(f" Buy/Hold Sharpe {round(buyhold_sharpe, 3)}")
        print(f" Model Sharpe {round(model_sharpe, 3)}")