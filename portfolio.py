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
        country.append(security['country'])
        sector.append(security['sector'])
        close.append(security['currentPrice'])
        change.append((security['currentPrice']/security['previousClose']-1)*100)
        changeDollar.append(security['currentPrice']-security['previousClose'])
    
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
    princeChange = df['priceChange']*df['shares']
    princeChange = princeChange.sum()
    # daily change
    dailyChange = princeChange/totalValue*100
    ## winner
    winnnerDf = round(df.sort_values(by='chg',ascending=False),1)
    
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
    
    
    #st.dataframe(df)
    with st.container(border=True):
        
        with st.container(border=True):
            col1, col2,col3,col4 = st.columns(4)
            with col1:
                st.metric("Total Return","${:,.0f}".format(netValue),delta="{:,.2f}%".format((netValue/totalCost)*100))
            #with col2:
            #    st.metric("YTD Return","{:.1f}%".format(df_asset['ASSETS'].tail(1).values[0]*100), delta="SPY {:.1f}%".format(df_asset['SPY'].tail(1).values[0]*100))
            with col2:
                st.metric("Daily change","${:.0f}".format(princeChange), delta="{:.2f}%".format(dailyChange))
            with col3:
                st.metric("Top Gain", winnnerDf.head(1).ticker.values[0] ,delta=str(winnnerDf.head(1).chg.values[0])+"%")
            with col4:
                st.metric("Top Loss", winnnerDf.tail(1).ticker.values[0] ,delta=str(winnnerDf.tail(1).chg.values[0])+"%")
        
        ## winner and loser
        with st.container(border=True):
            col1, col2 = st.columns(2)
            with col1:
                st.subheader(":green[Gainers:] ",divider='green')
                top5 = [f"{row['ticker']}: {row['chg']}%" for index, row in winnnerDf.head(3).iterrows()]
                st.write(f":green[{top5}]")
            with col2:
                st.subheader(f":red[Losers:] ",divider='red')
                bottom5 = [f"{row['ticker']}: {row['chg']}%" for index, row in winnnerDf.sort_values(by='chg').head(3).iterrows()]
                st.write(f":red[{bottom5}]")
        
        ## Portfolio to Benchmark
        st.subheader(f'**YTD: :blue[Portfolio] ({round(df_asset.ASSETS.iloc[-1]*100,1)}%) :blue[vs] :gray[SPY] ({round(df_asset.SPY.iloc[-1]*100,1)}%)**',divider=True)
        #plot line chart
        st.line_chart(data=df_asset*100.00,color=["#67BCF5", "#7D7D85"], use_container_width=True)
        
        # tree of portfolio
        st.subheader('Allocation and Daily Changes 🔺🔻',divider=True)
        fig1= px.treemap(df, path=['country','sector','ticker'],values='value', color='chg',hover_name='ticker',color_continuous_scale='RdYlGn') #RdYlBu
        fig1.update_layout(margin=dict(l=0, r=0, t=10, b=50))
        st.plotly_chart(fig1, use_container_width=True)
               
        # plot my holdings line chart
        st.subheader('My Holdings - YTD Return',divider='rainbow')
        myHoldings = df_raw[tickers].copy()
        for col in myHoldings.columns:
            myHoldings[col] = myHoldings[col].apply(lambda x: round(x / myHoldings[col].head(1).values[0],4)-1)*100
        #st.dataframe(myHoldings)
        st.line_chart(myHoldings)        
        
        ## my holdings table
        with st.expander("MY Holdings Positions",icon="🚨"):
            st.subheader('Positions by Daily Change %',divider=True)
            st.dataframe(df.drop(columns=['shares','return']).sort_values(by='chg'),use_container_width=True,hide_index=True) #prints tickers dataframe   