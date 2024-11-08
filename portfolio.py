import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import yfinance as yf
import plotly.express as px
import gdown

def main():
    df = pd.read_csv("data/test.csv")
    df = df[df['ticker'] != 'ALLCASH']
    mylist = df['ticker'].unique().tolist()
    tickers = mylist+['SPY']
    df['value'] = df.entry*df.shares
    country = []
    sector = []
    close = []
    change = []
    changeDollar = []
    for i in mylist:
        security = yf.Ticker(i).info
        country.append(security.get('country', 'N/A'))  # Defaults to 'N/A' if 'country' is not found
        sector.append(security.get('sector', 'N/A'))    # Defaults to 'N/A' if 'sector' is not found
        close.append(security.get('currentPrice', 0))   # Defaults to 0 if 'currentPrice' is not found
        change.append((security.get('currentPrice', 0) / security.get('previousClose', 1) - 1) * 100)  # Avoid division by zero
        changeDollar.append(security.get('currentPrice', 0) - security.get('previousClose', 0))  # Avoid differences with defaults
    
    df['country'] = country
    df['sector'] = sector
    df['close'] = close
    df['chg'] = change
    df['priceChange'] = changeDollar
    #calculate returns
    df['return'] = df.close/df.entry-1
    df = round(df,2) # rounding to 2 decimal places
    
    mylist = df['ticker'].unique().tolist()
    tickers = mylist+['SPY']
    
    # net value
    totalCost = df['value'].sum()
    totalValue = df['close']*df['shares']
    totalValue = totalValue.sum()
    netValue = totalValue - totalCost
    # daily prince change
    priceChange = df['priceChange']*df['shares']
    priceChange = priceChange.sum()
    # daily change
    dailyChange = priceChange/totalValue*100
    ## filteer change positive sort by chg but if rows are none then add none to the list
    #winnerDf = round(df.sort_values(by='chg',ascending=False),2)[df.chg>0]
    if df[df.chg > 0].empty:
        winnerDf = pd.DataFrame(columns=df.columns)
        winnerDf = winnerDf.append(pd.Series([None] * len(df.columns), index=df.columns), ignore_index=True)
    else:
        winnerDf = round(df.sort_values(by='chg', ascending=False), 2)[df.chg > 0]
    # filter chnage negative sort by chg
    if df[df.chg < 0].empty:
        losserDf = pd.DataFrame(columns=df.columns)
        losserDf = losserDf.append(pd.Series([None] * len(df.columns), index=df.columns), ignore_index=True)
    else:
        losserDf = round(df.sort_values(by='chg'), 2)[df.chg < 0]
    
    ###
    dataset = {}
    for ticker in tickers:
        security = yf.Ticker(ticker)
        dataset[ticker] = security.history(period='ytd')['Close']
    df_raw = pd.DataFrame(dataset) 
    df_raw['ASSETS'] = df_raw[mylist].sum(axis=1)
    df_asset = df_raw[['ASSETS','SPY']].copy()
    
    for col in df_asset.columns:
        df_asset[col] = df_asset[col].apply(lambda x: (x / df_asset[col].head(1).values[0])-1)        
    
    with st.container(border=True):
        # Metrics
        with st.container(border=True):
            col1, col2,col3,col4 = st.columns(4)
            with col1:
                st.metric("Total Return","${:,.0f}".format(netValue),delta="{:,.2f}%".format((netValue/totalCost)*100))
            with col2:
                st.metric("Daily change","${:.0f}".format(priceChange), delta="{:.2f}%".format(dailyChange))
            with col3:
                st.metric("Top Gain", winnerDf.head(1).ticker.values[0] ,delta=str(winnerDf.head(1).chg.values[0] if winnerDf.head(1).chg.values[0] else 0)+"%")
            with col4:
                st.metric("Top Loss", losserDf.head(1).ticker.values[0] ,delta=str(losserDf.head(1).chg.values[0] if losserDf.head(1).chg.values[0] else 0)+"%")
        ## winner and loser
        with st.container(border=True):
            col1, col2 = st.columns(2)
            with col1:
                st.subheader(":green[Gainers:] ",divider='green')
                top5 = [f"{row['ticker']}: {row['chg']}%" for index, row in winnerDf.head(3).iterrows()]
                st.write(f":green[{top5 if winnerDf.head(1).chg.values[0] else 'No Gainers'}]")
            with col2:
                st.subheader(f":red[Losers:] ",divider='red')
                bottom5 = [f"{row['ticker']}: {row['chg']}%" for index, row in losserDf.sort_values(by='chg').head(3).iterrows()]
                st.write(f":red[{bottom5 if losserDf.head(1).chg.values[0] else 'No Losers'}]")
        ## Portfolio to Benchmark
        with st.container(border=True):
            st.subheader(f'**YTD: :blue[Portfolio] ({round(df_asset.ASSETS.iloc[-1]*100,1)}%) :blue[vs] :gray[SPY] ({round(df_asset.SPY.iloc[-1]*100,1)}%)**',divider=True)
            #plot line chart
            st.line_chart(data=df_asset*100.00,color=["#67BCF5", "#7D7D85"], use_container_width=True)
        # tree of portfolio
        with st.container(border=True):
            st.subheader('Allocation and Daily Changes 🔺🔻',divider=True)
            fig1= px.treemap(df, path=['country','sector','ticker'],values='value', color='chg',hover_name='ticker',color_continuous_scale='RdYlGn',hover_data=['ticker', 'chg', 'country','sector']) #RdYlBu
            # Optionally format hover_data to show change in a more readable way
            fig1.update_traces(hovertemplate="Ticker: %{hovertext}<br>Change: %{customdata[1]:.1f}%<br>Country: %{customdata[2]}<br>Sector: %{customdata[3]}")
            fig1.update_layout(margin=dict(l=0, r=0, t=10, b=50))
            st.plotly_chart(fig1, use_container_width=True)       
        # plot my holdings line chart
        with st.container(border=True):
            st.subheader('YTD Return',divider='rainbow')
            myHoldings = df_raw[tickers].copy()
            for col in myHoldings.columns:
                myHoldings[col] = myHoldings[col].apply(lambda x: round(x / myHoldings[col].head(1).values[0],4)-1)*100
            #st.dataframe(myHoldings)
            st.line_chart(myHoldings)        
        
        ## my holdings table
        with st.expander(":blue[View Positions by Daily Change %]",icon="🚨"):
            st.subheader('Positions by Daily Change %',divider=True)
            st.dataframe(df.drop(columns=['shares','return']).sort_values(by='chg'),use_container_width=True,hide_index=True) #prints tickers dataframe   