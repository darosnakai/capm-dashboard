# CAPM Modeling Application

## Overview

This application provides a Capital Asset Pricing Model (CAPM) analysis tool for stocks that are listed in the S&P 500, allowing users to calculate beta values and expected returns based on historical data from Yahoo Finance. The interactive web application enables users to select stocks from the S&P 500 index and analyze their risk-return relationship.

## What is CAPM?
CAPM (Capital Asset Pricing Model) is a financial model developed to evaluate an asset's expected returns based on its risk relationship with a given market. In other words, the model evaluates how sensitive an asset is to non-diversifiable risk (systematic or market risk). 

<img width="1288" alt="dashboard" src="https://github.com/user-attachments/assets/ab954d06-59e8-44ba-ae3c-4ed344ee817a" />

**CAPM Formula:** *E(rA) = rf + βA × (E(rm) - rf)*

Where:

- **Beta (β):** Represents the asset's sensitivity to market movements (essentially showing its systematic risk). If an asset's beta is 2, then you expect the asset to have 2% if the market has 1% returns, or -2% returns if the market has -1% return
- **rf:** Risk-free rate (Treasury Bills 10yr interest rate, ~4.2% on the date of development)
- **E(rm):** Expected returns of the market. There are many ways to calculate this, but this application is using historical returns of the given asset and market. 

## Calculation Methdology
- **Beta (β):** Calculated using the covariance of stock returns with market returns, divided by the variance of market returns
- **CAPM:** Calculating using a risk-free rate of 4.2% (10-year Treasury yield) and the historical average market return

## Features
- Select any stocks from the S&P 500 index
- Choose analysis period (1, 2, 3, or 5 years)
- Select data interval (daily, weekly, or monthly)
- Calculate and visualize beta values
- Calculate expected returns using CAPM
- Interactive scatter plot showing the relationship between beta and expected returns

## Project Structure

- data_preprocessing.py: Handles data retrieval and preprocessing from Yahoo Finance
- tickers_analysis.py: Performs CAPM and beta calculations
- app.py: Main Dash web application entry point
- requirements.txt: List of Python dependencies
- assets/: CSS and other static files for the web application
