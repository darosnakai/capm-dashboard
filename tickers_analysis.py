#file with all the analyses made by me (beta, capm, etc)

import numpy as np
import pandas as pd
import yfinance as yf
import time
from data_preprocessing import DataPreprocessor

start_time = time.time()

class analyzer:
    def __init__(self):
        #initializing DataPreprocessor part in the constructor to ensure saved settings
        self.index_processor = DataPreprocessor()
        
        #Storing important variables for future use (maintaining data)
        self.number_of_tickers = self.index_processor.number_of_tickers
        self.index_name = self.index_processor.get_index_name()
        self.period = self.index_processor.get_period()
        self.interval = self.index_processor.get_interval()

        self.returns_data = None
        self.ticker_names = []
        self.all_info = None
        self.beta_all_df = None
    
    #Creating a df with all the returns of all features (for the selected period and interval)
    def returns_all_tickers(self, selected_tickers=None):
        start_time = time.time()
        if selected_tickers:
            # Create a DataFrame with the selected tickers
            all_tickers = pd.DataFrame(selected_tickers, columns=["Ticker"])
        else:
            # Otherwise use the first N tickers from the S&P 500 (original behavior)
            all_stocks = pd.read_html("data/sp500_components.html")[0]
            all_tickers = pd.DataFrame([all_stocks.iloc[i, 0] for i in range(len(all_stocks))], columns=["Ticker"])
            all_tickers = all_tickers.head(self.number_of_tickers)

        #Give me the returns of the index (input by the user)
        index_returns = self.index_processor.index_returnsdf()

        #First ticker to have returns in the datafram is the index ticker (input by the user)
        returns_all_tickers = pd.DataFrame(index_returns["Date"])
        returns_all_tickers[f"{self.index_name} Returns"] = index_returns[f"{self.index_name} Returns"]

        for i in range(len(all_tickers)):
            #Selecting each ticker from the wikipedia df
            ticker = all_tickers.iloc[i,0]
            try:
                print(f"Processing {ticker}...")
                #Getting returns of the ticker using the function in the preprocessor part
                stock_returns = self.index_processor.stock_returnsdf(ticker)
                
                #Merging the newly created df with the returns_all_tickers df
                returns_all_tickers = pd.merge(
                    returns_all_tickers, 
                    stock_returns[["Date", f"{ticker} Returns"]], 
                    on="Date", 
                    how="left"
                )
                
            except Exception as e:
                print(f"Error with {ticker}: {e}")
    
        #Setting date as index of the data frame
        returns_all_tickers.set_index("Date", inplace=True)

        #Storing the DataFrame as instance variables
        self.returns_data = returns_all_tickers

        print("returns_all_tickers finished --- %s seconds ---" % (time.time() - start_time))
        return returns_all_tickers
    
    #Important to maintain consistency throughout the different analyses
    def get_stock_ticker_names(self):
        #Putting the stock ticker names into a list in case you just want to check what tickers we are using
        if self.returns_data is None:
            print("No return data available. Please run returns_all_tickers() first.")
            return []
       
        all_columns = list(self.returns_data.columns)
        ticker_names = []
        
        #Skipping the index column
        for column in all_columns:
            if self.index_name in column:
                continue
        
        #Column names are in format "[TICKER] Returns"
            ticker = column.replace(" Returns", "")
            ticker_names.append(ticker)
        
        #Saving the ticker_names into the instance
        self.ticker_names = ticker_names
    
        return ticker_names

    #Saving all returns into a file if desired
    def saving_all_returns(self):
        returns_filename = f'returns_{self.index_name}_{self.number_of_tickers}_tickers_{self.period}_{self.interval}.csv'

        self.returns_data.to_csv(returns_filename)

        print(f"Saved returns dataframe to {returns_filename}")
        
        return returns_filename

    def beta_calc_all(self):
        start_time = time.time()
        if not self.ticker_names:
            self.get_stock_ticker_names()
        
        if not self.ticker_names:
            print("No ticker names available. Cannot calculate betas.")
            return None

        #Creating dataframe only with the ticker names, 
        #This will be the df that I will add the future data (beta, mcap, etc.)
        self.beta_all_df = pd.DataFrame(self.ticker_names, columns=["Ticker"])

        for i in range(len(self.beta_all_df)):
            #Each ticker is in each row [i,0], so I am fetching each ticker in each iteration
            ticker = self.beta_all_df.iloc[i, 0]
            
            #Skipping the index column, since we don't calculate the beta of it
            if self.index_name in self.ticker_names:
                continue
            
            #Calculating ri (individual stock returns)
            ri = self.returns_data[f"{ticker} Returns"]
            
            #Calculating rm (market returns (standard is sp500))
            rm = self.returns_data[f"{self.index_name} Returns"]

            #Beta calculation
            beta = np.cov(ri, rm)[0,1]/np.var(rm)

            #Beta rounding
            rounded_beta = np.round(beta, decimals=3)

            #Adding beta to the df that initially only had the ticker names
            self.beta_all_df.at[i,f"Beta {self.period} {self.interval}"] = rounded_beta

        print("beta_calc_all finished --- %s seconds ---" % (time.time() - start_time))
        
        return self.beta_all_df
        #np.cov(ri,rm) will give me a covariance matrix. the [0,1] element is the covariance between...
        #... rm and r1 (is the same as [1,0])
    
    def capm_all(self):
        start_time = time.time()
        
        if not self.ticker_names:
            self.get_stock_ticker_names()
        
        if not self.ticker_names:
            print("No ticker names available. Cannot calculate betas.")
            return None
        
        capm_df = pd.DataFrame(self.ticker_names, columns=["Ticker"])

        market_returns = self.returns_data[f"{self.index_name} Returns"]
        expected_market_returns = market_returns.mean() #Arithmetic mean of the past 5y monthly returns - E[rm]

        annual_risk_free_rate = 0.042
        #Using the 5year treasury bill (^FVX), which is around 4,2% today

        monthly_risk_free_rate = (1 + annual_risk_free_rate)**(1/12) - 1

        #CAPM formula is: E[rA] = rf + βA × (E[rm] - rf)
        for i in range(len(capm_df)):
            beta_each_asset = self.beta_all_df.iloc[i,1]
            expected_return = (monthly_risk_free_rate + beta_each_asset*(expected_market_returns-monthly_risk_free_rate))*100
            rounded_capm = np.round(expected_return, decimals=3)
            capm_df.at[i,"Expected Monthly Returns (%)"] = rounded_capm
        
        print("capm_all finished --- %s seconds ---" % (time.time() - start_time))

        return capm_df
    
    def mcap_all(self):
        start_time = time.time()
        
        if not self.ticker_names:
            self.get_stock_ticker_names()
        
        if not self.ticker_names:
            print("No ticker names available. Cannot calculate betas.")
            return None
        
        mcap_df = pd.DataFrame(self.ticker_names, columns=["Ticker"])

        #Getting the market cap of the tickers
        for i in range(len(mcap_df)):
            ticker = mcap_df.iloc[i,0]
            ticker_info = yf.Ticker(ticker).info
            market_cap = ticker_info.get("marketCap",None)
            if market_cap is not None:
                mcap = yf.Ticker(ticker).info["marketCap"]/1000000000
                rounded_mcap = np.round(mcap, decimals=3)
                mcap_df.at[i,"Market Cap (in $B)"] = rounded_mcap
            else:
                mcap_df.at[i, "Market Cap (in $B)"] = None
        
        print("mcap_all finished --- %s seconds ---" % (time.time() - start_time))

        return mcap_df
    
    def run_all_analysis(self):
        start_time = time.time()
        
        if not self.ticker_names:
            self.get_stock_ticker_names()
        
        if not self.ticker_names:
            print("No ticker names available. Cannot calculate betas.")
            return None
        
        #Running all analyses methods
        beta_calculated = self.beta_calc_all()
        capm_calculated = self.capm_all()
        
        merged_df = pd.merge(capm_calculated,beta_calculated,on="Ticker",how="left")

        yfinance_beta_df = pd.DataFrame(self.ticker_names, columns=["Ticker"])
        
        for i in range(len(yfinance_beta_df)):
            ticker = yfinance_beta_df.iloc[i,0]
            ticker_info = yf.Ticker(ticker).info
            beta_yf = ticker_info.get("beta",None)
            yfinance_beta_df.at[i,"Beta YF"] = beta_yf

        merged_df.set_index("Ticker",inplace=True)

        self.all_info = merged_df

        print("run_all_analysis finished --- %s seconds ---" % (time.time() - start_time))

        return self.all_info
    
    def saving_all_analysis(self):
        start_time = time.time()
        
        all_info_filename = f"all_info_{self.number_of_tickers}_tickers_{self.index_name}_index.csv"

        self.all_info.to_csv(all_info_filename)

        print(f"Saved all analysis to {all_info_filename}")

        print("saving_all_analysis finished --- %s seconds ---" % (time.time() - start_time))
        
        return all_info_filename