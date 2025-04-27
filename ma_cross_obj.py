import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from fin_table_obj import Table

class MovingAverageTable(Table):
        def __init__(self, df, ma1, ma2):
            super().__init__(df)
            self.__ma1 = ma1
            self.__ma2 = ma2
    
        def gen_table(self):    
            super().gen_table()
         #we .shift() to push the moving average forward a day because the moving average cannot start until x days have finished
            self.df[f'{self.__ma1}-day MA'] = self.df['Close'].rolling(int(self.__ma1)).mean().shift()
            self.df[f'{self.__ma2}-day MA'] = self.df['Close'].rolling(int(self.__ma2)).mean().shift()

        #signal to long
            self.df['Signal'] = np.where(self.df[f'{self.__ma1}-day MA'] > self.df[f'{self.__ma2}-day MA'], 1, 0)

        #signal to short
            self.df['Signal'] = np.where(self.df[f'{self.__ma1}-day MA'] < self.df[f'{self.__ma2}-day MA'], -1, self.df['Signal'])
            
        # model return, if our signal is - we are short and the daily return is negative. vice versa
            self.df['Model Return'] = self.df['Return'] * self.df['Signal']

        #entry column for visualization
            self.df['Entry'] = self.df.Signal.diff()

        # drop rows
            self.df.dropna(inplace = True)
        #Cumulative Returns
            self.df['Cumulative Model Return'] = (np.exp(self.df['Model Return'] / 100).cumprod() - 1) * 100

            #recalc return and cumulative return to include model returns
            self.df['Return'] = (np.log(self.df['Close']).diff()) * 100
            self.df['Cumulative Return'] = (np.exp(self.df['Return'] / 100).cumprod() - 1) * 100

        #formatting the table
            self.df = round((self.df[['Day Count', 'Open', 'High', 'Low', 'Close', f'{self.__ma1}-day MA', f'{self.__ma2}-day MA', 'Return', 'Cumulative Return', 'Model Return', 'Cumulative Model Return', 'Signal', 'Entry']]), 3)

            
            return self.df
        
        def gen_ma_cross_visual(self, model_days):
        #parameters for grid size
            plt.rcParams['figure.figsize'] = 12, 8
        #create grid
            plt.grid(True, alpha = .5)
        #plot ticker closing prices and MAs, .iloc for integers
            plt.plot(self.df.iloc[-model_days:]['Close'], label = f'{self.ticker.upper()}')
            plt.plot(self.df.iloc[-model_days:][f'{self.__ma1}-day MA'], label = f'{self.__ma1}-day MA')
            plt.plot(self.df.iloc[-model_days:][f'{self.__ma2}-day MA'], label = f'{self.__ma2}-day MA')
        #plotting entry points, .loc for labels
            plt.plot(self.df[-model_days:].loc[self.df.Entry == 2].index, self.df[-model_days:][f'{self.__ma1}-day MA'][self.df.Entry == 2], '^', color = 'g', markersize = 10)
            plt.plot(self.df[-model_days:].loc[self.df.Entry == -2].index, self.df[-model_days:][f'{self.__ma2}-day MA'][self.df.Entry == -2], 'v', color = 'r', markersize = 10)
        #plot legend
            plt.legend(['Close', f'{self.__ma1}-day MA', f'{self.__ma2}-day MA', 'Buy Signal', 'Sell Signal'], loc = 2)
       
        def gen_buyhold_comp(self):
        #buy/hold plot
            plt.plot(self.df['Cumulative Return'], label='Buy/Hold')
        #model plot
            plt.plot(self.df['Cumulative Model Return'], label='Model')
            plt.legend(loc=2)
            plt.grid(True, alpha=.5)
        #print returns
            print("Cumulative Buy/Hold Return:", round(self.df['Cumulative Return'].iloc[-1], 2))
            print("Cumulative Model Return:", round(self.df['Cumulative Model Return'].iloc[-1], 2))