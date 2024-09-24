This Python script is designed to scrape financial data from the SEC's public APIs and calculate key financial ratios for publicly traded companies.

**Features**
Company Data Retrieval: Fetches company tickers and associated information from the SEC's company tickers JSON file.
Financial Data Extraction: Retrieves various financial metrics such as assets, liabilities, equity, revenue, and net income using the SEC's XBRL API.
Financial Ratio Calculation: Computes essential financial ratios, including:
 * Current Ratio
 * Debt to Equity Ratio
 * Gross Margin
 * Return on Equity (ROE)
 * Return on Assets (ROA)
 * Earnings per Share (EPS)
 * Price-to-Earnings (P/E) Ratio
 * Asset Turnover

**Usage**
* Run the script.
* Input the ticker symbol of the company you want to analyze.


**Dependencies**
requests: For making HTTP requests to the SEC API.
pandas: For data manipulation and analysis.

**Author**
Created by Natalie.

