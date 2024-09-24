# -*- coding: utf-8 -*-
"""
Created on Thu Sep 19 11:11:11 2024
SEC Filing Scraper with Financial Ratios

@author: Natalie
"""


# import modules
import requests
import pandas as pd

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
        # Print the raw response for debugging
        print(f"Data for concept '{concept}': {data}\n")
        
        # Check if 'units', 'USD', and 'value' exist in the JSON response
        if 'units' in data and 'USD' in data['units'] and len(data['units']['USD']) > 0:
            # Sort the entries by the 'end' date and get the most recent one
            sorted_data = sorted(data['units']['USD'], key=lambda x: x['end'], reverse=True)
            most_recent_value = sorted_data[0]['val']  # Get the 'val' of the most recent entry
            return most_recent_value
        else:
            print(f"Missing or incorrect format for '{concept}'")
    except (KeyError, IndexError) as e:
        print(f"Error extracting value for '{concept}': {e}")
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
    shares_outstanding_data = get_company_financial_data(cik, 'CommonStockSharesOutstanding')

    # Extract the most recent values from the financials
    assets = extract_most_recent_value(assets_data, 'Assets')
    liabilities = extract_most_recent_value(liabilities_data, 'Liabilities')
    equity = extract_most_recent_value(equity_data, 'StockholdersEquity')
    revenue = extract_most_recent_value(revenue_data, 'Revenues')
    net_income = extract_most_recent_value(net_income_data, 'NetIncomeLoss')
    current_assets = extract_most_recent_value(current_assets_data, 'AssetsCurrent')
    current_liabilities = extract_most_recent_value(current_liabilities_data, 'LiabilitiesCurrent')
    shares_outstanding = extract_most_recent_value(shares_outstanding_data, 'CommonStockSharesOutstanding')

   #    # Debugging: Print the values extracted
   #        print(f"Assets: {assets}, Liabilities: {liabilities}, Equity: {equity}")
   #        print(f"Revenue: {revenue}, Net Income: {net_income}")
   #        print(f"Current Assets: {current_assets}, Current Liabilities: {current_liabilities}")
   #        print(f"Shares Outstanding: {shares_outstanding}")
    
    # Check if the essential data is available and specify which data is missing
    missing_data = []
    if assets is None:
        missing_data.append("Assets")
    if liabilities is None:
        missing_data.append("Liabilities")
    if equity is None:
        missing_data.append("Stockholders Equity")
    if revenue is None:
        missing_data.append("Revenues")
    if net_income is None:
        missing_data.append("Net Income")
    if current_assets is None:
        missing_data.append("Current Assets")
    if current_liabilities is None:
        missing_data.append("Current Liabilities")
    if shares_outstanding is None:
        missing_data.append("Shares Outstanding")

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

    # Debt Ratio
    if liabilities is not None and assets is not None:
        ratios['Debt Ratio'] = liabilities / assets
    else:
        ratios['Debt Ratio'] = None

    # Quick Ratio (Current Assets minus Inventory divided by Current Liabilities)
    # Assuming inventory concept might need to be added similarly to fetch actual inventory data
    if current_assets is not None and current_liabilities is not None:
        ratios['Quick Ratio'] = current_assets / current_liabilities  # Placeholder; adjust with actual inventory data
    else:
        ratios['Quick Ratio'] = None

    # Earnings per Share (EPS)
    if net_income is not None and shares_outstanding is not None:
        ratios['Earnings per Share (EPS)'] = net_income / shares_outstanding
    else:
        ratios['Earnings per Share (EPS)'] = None

    # Price-to-Earnings (P/E) Ratio (You'd need the company's stock price for this)
    # Assuming you have a stock price available from another source
    stock_price = 100  # Placeholder value for stock price
    if ratios['Earnings per Share (EPS)'] is not None:
        ratios['Price-to-Earnings (P/E) Ratio'] = stock_price / ratios['Earnings per Share (EPS)']
    else:
        ratios['Price-to-Earnings (P/E) Ratio'] = None

    # Asset Turnover (Revenue / Total Assets)
    if revenue is not None and assets is not None:
        ratios['Asset Turnover'] = revenue / assets
    else:
        ratios['Asset Turnover'] = None

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
