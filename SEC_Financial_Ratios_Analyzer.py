# -*- coding: utf-8 -*-
"""
Created on Thu Sep 19 11:11:11 2024
SEC Filing Scraper with Financial Ratios including Z-score

@author: Natalie
"""

# import modules
import requests
import pandas as pd
import yfinance as yf
from datetime import date

# create request header
headers = {'User-Agent': "email@address.com"}

# get all companies data
companyTickers = requests.get(
    "https://www.sec.gov/files/company_tickers.json",
    headers=headers
)

# dictionary to dataframe
companyData = pd.DataFrame.from_dict(companyTickers.json(), orient='index')

# add leading zeros to CIK
companyData['cik_str'] = companyData['cik_str'].astype(str).str.zfill(10)

# Function to check if ticker is in companyData
def check_ticker(company_ticker):
    return company_ticker in companyData['ticker'].values

def get_ticker_title(company_ticker, companyData):
    result = companyData[companyData['ticker'] == company_ticker]['title']
    return result.iloc[0] if not result.empty else None

# Function to fetch company financial data
def get_company_financial_data(cik, concept):
    url = f'https://data.sec.gov/api/xbrl/companyconcept/CIK{cik}/us-gaap/{concept}.json'
    response = requests.get(url, headers=headers)
    
    # Check if the request was successful
    if response.status_code == 200:
        return response.json()
    return None

# Function to safely extract the most recent value from financial data
def extract_most_recent_value(data, concept):
    try:
        # print(f"Data for concept '{concept}': {data}\n")
        if 'units' in data and 'USD' in data['units'] and len(data['units']['USD']) > 0:
            sorted_data = sorted(data['units']['USD'], key=lambda x: x['end'], reverse=True)
            most_recent_value = sorted_data[0]['val']
            return most_recent_value
        else:
            print(f"Missing or incorrect format for '{concept}'")
    except (KeyError, IndexError) as e:
        print(f"Error extracting value for '{concept}': {e}")
    return None

# Function to calculate Altman Z-score
def calculate_z_score(assets, liabilities, current_assets, current_liabilities, net_income, revenue, equity, shares_outstanding, stock_price):
    # Working Capital = Current Assets - Current Liabilities
    working_capital = current_assets - current_liabilities if current_assets is not None and current_liabilities is not None else None

    
    # Market Value of Equity = Stock Price * Shares Outstanding
    market_value_of_equity = stock_price * shares_outstanding if shares_outstanding is not None else None

    # Retained Earnings = Net Income (using as proxy for simplicity)
    retained_earnings = net_income if net_income is not None else None

    # Calculate Z-score components if the necessary data is available
    if all(v is not None for v in [assets, liabilities, working_capital, retained_earnings, net_income, revenue, market_value_of_equity]):
        A = working_capital / assets
        B = retained_earnings / assets
        C = net_income / assets  # Using net_income as EBIT for simplicity
        D = market_value_of_equity / liabilities
        E = revenue / assets

        # Calculate the Z-score
        Z = (1.2 * A) + (1.4 * B) + (3.3 * C) + (0.6 * D) + (1.0 * E)
        return Z
    else:
        print("\n\nSome data required for Z-score calculation is missing.")
        return None

# Function to calculate financial ratios
def calculate_financial_ratios(cik):
    # Get company financials from SEC API
    print(f"Fetching financial data for CIK {cik}...")
    
    # Fetch financial data for different concepts
    assets_data = get_company_financial_data(cik, 'Assets')
    liabilities_data = get_company_financial_data(cik, 'Liabilities')
    equity_data = get_company_financial_data(cik, 'StockholdersEquity')
    revenue_data = get_company_financial_data(cik, 'Revenues')
    net_income_data = get_company_financial_data(cik, 'NetIncomeLoss')
    current_assets_data = get_company_financial_data(cik, 'AssetsCurrent')
    current_liabilities_data = get_company_financial_data(cik, 'LiabilitiesCurrent')

    # Extract the most recent values from the financials
    stock_info = yf.Ticker(company_ticker)
    shares_outstanding = stock_info.info.get('sharesOutstanding')
    
    assets = extract_most_recent_value(assets_data, 'Assets')
    print(f"\nAssets: {assets}")
    current_assets = extract_most_recent_value(current_assets_data, 'AssetsCurrent')
    print(f"Current Assets: {current_assets}")
    liabilities = extract_most_recent_value(liabilities_data, 'Liabilities')
    print(f"Liabilities: {liabilities}")
    current_liabilities = extract_most_recent_value(current_liabilities_data, 'LiabilitiesCurrent')
    print(f"Current Liabilities: {current_liabilities}")
    equity = extract_most_recent_value(equity_data, 'StockholdersEquity')
    print(f"Equity: {equity}")
    revenue = extract_most_recent_value(revenue_data, 'Revenues')
    print(f"\nRevenue: {revenue}")
    net_income = extract_most_recent_value(net_income_data, 'NetIncomeLoss')
    print(f"Net Income: {net_income}")
    # print(type(shares_outstanding))
    print(f"Shares Outstanding: {shares_outstanding}\n")


    # Check if the essential data is available
    missing_data = []
    if assets is None: missing_data.append("Assets")
    if liabilities is None: missing_data.append("Liabilities")
    if equity is None: missing_data.append("Stockholders Equity")
    if revenue is None: missing_data.append("Revenues")
    if net_income is None: missing_data.append("Net Income")
    if current_assets is None: missing_data.append("Current Assets")
    if current_liabilities is None: missing_data.append("Current Liabilities")
    if shares_outstanding is None: missing_data.append("Shares Outstanding")

    if missing_data:
        print("Some essential financial data is missing:")
        for item in missing_data:
            print(f"- {item}")
    else:
        print("All essential financial data is available.")

    # Calculate ratios only when sufficient data is available
    ratios = {}

    # Current Ratio
    if current_assets is not None and current_liabilities is not None:
        ratios['Current Ratio'] = current_assets / current_liabilities
    else:
        ratios['Current Ratio'] = None
        
    # Quick Ratio (Current Assets minus Inventory divided by Current Liabilities)
    if current_assets is not None and current_liabilities is not None:
        ratios['Quick Ratio'] = current_assets / current_liabilities  # Placeholder
    else:
        ratios['Quick Ratio'] = None

    # Debt Ratio
    if liabilities is not None and assets is not None:
        ratios['Debt Ratio'] = liabilities / assets
    else:
        ratios['Debt Ratio'] = None

    # Debt to Equity Ratio
    if liabilities is not None and equity is not None:
        ratios['Debt to Equity'] = liabilities / equity
    else:
        ratios['Debt to Equity'] = None

    # Gross Margin
    if revenue is not None and net_income is not None:
        gross_margin = (revenue - (revenue - net_income)) / revenue
        ratios['Gross Margin'] = gross_margin
        ratios['Net Profit Margin'] = net_income / revenue
    else:
        ratios['Gross Margin'] = None
        ratios['Net Profit Margin'] = None

    # Return on Equity (ROE)
    if net_income is not None and equity is not None:
        ratios['Return on Equity (ROE)'] = net_income / equity
    else:
        ratios['Return on Equity (ROE)'] = None

    # Return on Assets (ROA)
    if net_income is not None and assets is not None:
        ratios['Return on Assets (ROA)'] = net_income / assets
    else:
        ratios['Return on Assets (ROA)'] = None

    # Earnings per Share (EPS)
    if net_income is not None and shares_outstanding is not None:
        ratios['Earnings per Share (EPS)'] = net_income / shares_outstanding
    else:
        ratios['Earnings per Share (EPS)'] = None

    # Get the stock price
    end_date = date.today()
    start_date = date(year=end_date.year, month=1, day=1)
    stock_current_data = yf.download(company_ticker, start_date, end_date)
    stock_price = stock_current_data['Close'].tail(1).iloc[0]  # Extract scalar value
    # stock_price = stock_current_data['Close'].tail(1)



    # Price-to-Earnings (P/E) Ratio (assuming a stock price is available)
    if ratios['Earnings per Share (EPS)'] is not None:
       ratios['Price-to-Earnings (P/E) Ratio'] = stock_price / ratios['Earnings per Share (EPS)']
    else:
        ratios['Price-to-Earnings (P/E) Ratio'] = None

    # Asset Turnover (Revenue / Total Assets)
    if revenue is not None and assets is not None:
        ratios['Asset Turnover'] = revenue / assets
    else:
        ratios['Asset Turnover'] = None

    # Calculate the Altman Z-score
    z_score = calculate_z_score(assets, liabilities, current_assets, current_liabilities, net_income, revenue, equity, shares_outstanding, stock_price)
    
    if z_score is not None:
        print(f"\nAltman Z-score: {z_score:.2f}")
    else:
        print("Z-score could not be calculated due to missing data.")
    
    return ratios

# Main loop for user interaction
while True:
    company_ticker = input("Enter the ticker of the company: ").strip().upper()
    company_title = get_ticker_title(company_ticker, companyData)

    if check_ticker(company_ticker):
        print(f"The ticker '{company_ticker}' is associated with '{company_title}'.")
        choice = input("Do you want to see financial ratios? (yes/no): ").strip().lower()

        if choice == 'yes':
            # Get CIK for the chosen ticker
            cik = companyData[companyData['ticker'] == company_ticker]['cik_str'].iloc[0]

            # Calculate financial ratios
            financial_ratios = calculate_financial_ratios(cik)

            if financial_ratios:
                print("\nFinancial Ratios:")
                for ratio, value in financial_ratios.items():
                    if value is not None:
                        print(f"{ratio}: {value:.2f}")
                    else:
                        print(f"{ratio}: Data not available")
            else:
                print("Financial data is not available for the selected company.")
            break
        elif choice == 'no':
            print("Please enter a new ticker.")
        else:
            print("Invalid choice. Please enter 'yes' or 'no'.")
    else:
        print("Incorrect ticker. Please try again.")
