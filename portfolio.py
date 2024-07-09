import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import yfinance as yf
import plotly.express as px
import gdown

def main():
    @st.cache_data()  # cache data for 24 hours
    def download_data():
        url = 'https://docs.google.com/spreadsheets/d/1yvGSBuv9TXe49AyOtx2lOV-vA5pchXAGp4_PKpne1Uw/edit?usp=sharing'
        output = 'stockPortfolio.xlsx'
        return gdown.download(url, output, quiet=False, fuzzy=True)
    #df = pd.read_excel(download_data())
    df = pd.read_excel("data/stockPortfolio.xlsx")
    
    #df.columns = ['ticker', 'entry',shares,value,'close','country','return','chg','princeChange]
    mylist = df['ticker'].unique().tolist()
    tickers = mylist+['SPY']
    
    # net value
    totalCost = df['value'].sum()
    totalValue = df['close']*df['shares']
    totalValue = totalValue.sum()
    netValue = totalValue - totalCost
    # daily prince change
    princeChange = df['priceChange']*df['shares']
    princeChange = princeChange.sum()
    # daily change
    dailyChange = princeChange/totalValue*100
    ## winner
    winnnerDf = df.sort_values(by='chg',ascending=False)
    
    ###
    dataset = {}
    for ticker in tickers:
        security = yf.Ticker(ticker)
        dataset[ticker] = security.history(period='ytd')['Close']
    df_raw = pd.DataFrame(dataset) 
    df_raw['ASSETS'] = df_raw[mylist].sum(axis=1)
    df_asset = df_raw[['ASSETS','SPY']]

    for col in df_asset.columns:
        df_asset[col] = df_asset[col].apply(lambda x: (x / df_asset[col].head(1).values[0])-1)    
    
    #st.dataframe(df)
    with st.container(border=True):

        col1, col2,col3,col4,col5 = st.columns(5)
        with col1:
            st.metric("Total Return","${:,.0f}".format(netValue),delta="{:,.2f}%".format((netValue/totalCost)*100))
        with col2:
            st.metric("YTD Return","{:.1f}%".format(df_asset['ASSETS'].tail(1).values[0]*100), delta="SPY {:.1f}%".format(df_asset['SPY'].tail(1).values[0]*100))
        with col3:
            st.metric("Daily change","${:.0f}".format(princeChange), delta="{:.2f}%".format(dailyChange))
        with col4:
            st.metric("Top Gain", winnnerDf.head(1).ticker.values[0] ,delta=str(winnnerDf.head(1).chg.values[0])+"%")
        with col5:
            st.metric("Top Loss", winnnerDf.tail(1).ticker.values[0] ,delta=str(winnnerDf.tail(1).chg.values[0])+"%")
                
        ## Portfolio to Benchmark
        st.subheader('**Portfolio VS Benchmark (SPY)**',divider=True)
        #plot line chart
        st.line_chart(df_asset,use_container_width=True)
        
        # tree of portfolio
        st.subheader('Allocation and Daily Changes 🔺🔻',divider=True)
        fig1= px.treemap(df, path=['country','ticker'],values='value', color='chg',hover_name='ticker',color_continuous_scale='RdYlGn') #RdYlBu
        fig1.update_layout(margin=dict(l=0, r=0, t=10, b=50))
        st.plotly_chart(fig1, use_container_width=True)
        
        # plot my holdings line chart
        st.subheader('My Holdings - YTD Cumulative Return',divider=True)
        myHoldings = df_raw[tickers].copy()
        for col in myHoldings.columns:
            myHoldings[col] = myHoldings[col].apply(lambda x: round(x / myHoldings[col].head(1).values[0],2)-1)
        st.line_chart(myHoldings)
        ## my holdings table
        with st.expander("MY Holdings Positions",icon="🚨"):
            st.subheader('Positions by Daily Change %',divider=True)
            st.dataframe(df.drop(columns=['shares','return']).sort_values(by='chg'),use_container_width=True,hide_index=True) #prints tickers dataframe   
        
        st.subheader('#',divider='rainbow')    

    

    
    
        
    
    
    