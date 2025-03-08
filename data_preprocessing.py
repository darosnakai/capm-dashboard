import numpy as np
import pandas as pd
import yfinance as yf
import time

start_time = time.time()

class DataPreprocessor():
    def __init__(self):
        self.period = "5y"
        self.interval = "1mo"
        self.index_name = "^GSPC"
        self.number_of_tickers = 30

    def period_selection(self, prompt="What period do you want to use? 1Y,2Y,3Y,4Y,5Y? (answer with integer) "):
        while True:
            try:
                period = int(input(prompt))
                if period == 1:
                    print(f"Program will use the period of {period} years")
                    self.period = "1y"
                    return self.period
                if period == 2:
                    print(f"Program will use the period of {period} years")
                    self.period = "2y"
                    return self.period
                if period == 3:
                    print(f"Program will use the period of {period} years")
                    self.period = "3y"
                    return self.period
                if period == 4:
                    print(f"Program will use the period of {period} years")
                    self.period = "4y"
                    return self.period
                if period == 5:
                    print(f"Program will use the period of {period} years")
                    self.period = "5y"
                    return self.period
                if period == 10:
                    print(f"Program will use the period of {period} years")
                    self.period = "10y"
                    return self.period
                if period == 20:
                    print(f"Program will use the period of {period} years")
                    self.period = "20y"
                    return self.period
                else: 
                    raise ValueError
            except ValueError:
                print("That's not a valid integer. Please enter a whole number.")
        

    def interval_selection(self, prompt="What interval do you want to use? daily or monthly? "):
        while True:
            try:
                interval = input(prompt)
                if interval == "daily":
                    print(f"Program will use the {interval} interval")
                    self.interval = "1d"
                    return self.interval
                """if interval == "weekly":
                    print(f"Program will use the {interval} interval")
                    self.interval = "1we" I DONT KNOW HOW THE YFINANCE MODULE INTERPRETS 1WEEEK INTERVAL
                    return self.interval"""
                if interval == "monthly":
                    print(f"Program will use the {interval} interval")
                    self.interval = "1mo"
                    return self.interval
                else:
                    raise ValueError
            except ValueError:
                print("That's not a valid interval. Please enter daily, weekly or monthly.")

    def get_number_of_tickers(self,prompt="How many tickers do you want to add? "):
        while True:
            try:
                number_of_tickers = int(input(prompt))
                print(f"You entered: {number_of_tickers}")
                self.number_of_tickers = number_of_tickers
                return number_of_tickers  
            except ValueError:
                print("That's not a valid integer. Please enter a whole number.")
    
    def standard_usage(self,prompt="Use 500 tickers, SP500 as index, period of 5y and monthly interval? (Y or N) "):
        while True:
            try:
                standard_usage = input(prompt).capitalize()
                if standard_usage == "Y":
                    print("Using standard settings: 500 tickers, SP500, 5y period, monthly interval")
                    return self.number_of_tickers, self.index_name, self.period, self.interval
                elif standard_usage == "N":
                    self.number_of_tickers = self.get_number_of_tickers()                                     
                    self.index_name = input("What index do you want to use?")
                    self.period_selection()
                    self.interval_selection()
                    return self.number_of_tickers, self.index_name, self.period, self.interval
                else: 
                    raise ValueError
            except ValueError:
                print("Not a valid answer, please answer Y or N")
    
    #Creating a df with the returns of the index
    #Doing the index_returnsdf is important because this will be the market used for the calculation of each beta
    def index_returnsdf(self):
    
        index_data = yf.Ticker(self.index_name)
        hist_index = pd.DataFrame(index_data.history(period = self.period,interval = self.interval))
        index_returns = hist_index["Close"].astype(float).pct_change()

        #converting (Series) to dataframe
        index_returns = index_returns.to_frame().dropna()
        
        #ranaming columns (from Close to Returns of the index)
        index_returns.rename(columns={"Close": f"{self.index_name} Returns"}, inplace=True)

        #reseting the index to organize the df
        index_returns.reset_index(inplace=True)
        
        return index_returns

    def stock_returnsdf(self, ticker):        
        
        #fetching data using yahoo finance library
        stock_data = yf.Ticker(ticker)
        hist_stock = pd.DataFrame(stock_data.history(period = self.period,interval = self.interval))
        stock_returns = hist_stock["Close"].astype(float).pct_change()

        #converting (Series) to dataframe
        stock_returns = stock_returns.to_frame().dropna()
        
        #renaming columns (from Close to Returns of the index)
        stock_returns.rename(columns={"Close": f"{ticker} Returns"}, inplace=True)

        #reseting the index to organize the df
        stock_returns.reset_index(inplace=True)

        return stock_returns
    
    def get_index_name(self):
        return self.index_name
    
    def get_period(self):
        return self.period
    
    def get_interval(self):
        return self.interval