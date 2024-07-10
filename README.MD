# **Stock Market Lab Project**

### **Welcome to Stock Market Project!**
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://stockmarketlab.streamlit.app)

A web application for exploring and analyzing stocks, built with Streamlit.

![App Screenshot](/data/portfolio.png)

## Features

* **Portfolio**: View personalized portfolio and track its performance.
    - A personalized dashboard for users to track their current holdings, allocation, and performance compared to benchmarks.
    - Utilizes libraries like Streamlit, Pandas, NumPy, Seaborn, Matplotlib, and Plotly Express for data manipulation and visualization.
    - Features include:
        - Holdings statistics
        - Tree allocation chart
        - Chart comparison to benchmarks
* **News**: Run sentiment analysis on **News Headlines** for a given stock ticker.
    - A news aggregator and sentiment analysis tool that parses headlines from websites and analyzes sentiment using Natural Language Processing (NLP) techniques.
    - Employs libraries like BeautifulSoup, Pandas, Seaborn, Matplotlib, and Plotly Express for data scraping and visualization.
    - Features include:
        - News headlines with sentiment analysis
        - Word cloud representation of news sentiment
        - Year-to-date (YTD) chart of news sentiment
* **Monte Carlo Simulation**: Run simulations based on R:R and Winrate %.
    - A simulation tool that runs Monte Carlo simulations to estimate stock prices and portfolio performance.
    - Utilizes libraries like NumPy, Pandas, Matplotlib, Seaborn, and Plotly Express for data generation and visualization.
    - Features include:
        - Simulation results with statistical analysis
        - Charts displaying simulated stock prices and portfolio performance
* **DCF Model**: Calculate the discounted cash flow value | Intrintic value of a stock.
    - A tool for calculating the Discounted Cash Flow (DCF) of stocks, with an option to run in auto mode, which fetches financial data from Yahoo API and estimates the intrinsic value of a stock.
    - Employs libraries like Streamlit, Yahoo Finance, Pandas, and Plotly Express for data manipulation and visualization.
    - Features include:
        - DCF calculation with input parameters
        - Auto mode for fetching financial data and estimating intrinsic value
        - Charts displaying stock performance and intrinsic value

#### **Requirements**

This application requires the following modules:

* **Streamlit framework**: to deploy on web
* **mplfinance**: used for creating financial plots and charts, such as candlestick charts and line charts.
* **NRCLex**: used for natural language processing and text analysis in the news feature.
* **vaderSentimen**: used for sentiment analysis in the news feature.
* **wordcloud**: used to generate word clouds in the news feature.
* **yfinance**: used to retrieve financial data from Yahoo Finance API.
* **beautifulsoup42**: used to parse HTML and extract data from web pages in the news feature.
* **gdown**: used to download portfolio holding excel file from google drive

## Screenshots

![News Sentimenet Analysis](/data/sentiment.png)

![Monte Carlo Simulation](/data/monte.png)

![DCF Model](/data/dcf.png)


### **Disclaimer**

This application is for informational purposes only and should not be used as investment advice. Please consult a financial advisor before making any investment decisions.

## **Acknowledgments**

This project is built with Streamlit, a Python library for building custom web applications. Special thanks to the Streamlit team for their excellent work!

Feel free to explore and enjoy!



## 🚀 About Me
I'm a Data Science guy...

[LinkedIn](https://www.linkedin.com/in/karmag/) ||
[Github](https://github.com/karma-gits)

## Badges

![GitHub Created At](https://img.shields.io/github/created-at/karma-gits/stockmarketlab)
