#import all the required packages 
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import pandas as pd
import seaborn as sns
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt
import yfinance as yf
from nrclex import NRCLex
from wordcloud import WordCloud, STOPWORDS #word clouds
import mplfinance as mpf
import streamlit as st
import datetime as dt
import plotly.express as px
import nltk_download
import corpora

def main(tickerHolder):
    #scrape data from finviz
    finviz_url = 'https://finviz.com/quote.ashx?t='
    news_tables = {}
    url = finviz_url + tickerHolder
    req = Request(url=url, headers={'user-agent': 'my-app'})
    response = urlopen(req)
    html = BeautifulSoup(response, features='html.parser')
    news_table = html.find(id='news-table')
    news_tables[tickerHolder] = news_table
    #turn data into clean table
    parsed_data = []

    for ticker, news_table in news_tables.items():
        for row in news_table.findAll('tr'):
            title_tag = row.find('a')
            if title_tag:
                title = title_tag.text
            date_data = row.td.text.split() #save all date datas
            if len(date_data) == 1 :
                time = date_data[0]
            else:
                date = date_data[0]
                time = date_data[1]
            parsed_data.append([ticker, date, time, title])
            
    df = pd.DataFrame(parsed_data, columns=['ticker', 'date', 'time', 'Headline'])
    df = df[df['date']=='Today'] #filter for current 'Today' data
    df['time'] = pd.to_datetime(df.time).dt.time ## convert to corrct time format
    from datetime import date
    date_when = date.today()# to save current date to save charts


    ### vader sentiment analysis
    ##vader sentiment analysis
    vader = SentimentIntensityAnalyzer()
    df['VaderSentiment'] = df['Headline'].apply(lambda title: vader.polarity_scores(title)['compound'])
    
    ## new columns with emoji 
    df['Sentiment'] = df['VaderSentiment'].apply(lambda x: "😀😀" if x > .4 else "🙂🙂" if x > .1 else "🙂" if x > .05 else "❔🤷" if x > -.05 else "😡" if x>-.4 else "😡😡")
    
    ### News headlines
    st.subheader(f':red[📰 News Headlines 📰-] {tickerHolder} | {dt.datetime.now().date()}',divider='red')
    #st.dataframe(df[['time','Headline','Emoji']].set_index('time'),use_container_width=True) #prints tickers dataframe
    with st.container(height=450,border=True):
        st.table(df[['time','Headline','Sentiment']].set_index('time')) #prints tickers dataframe
    
    st.subheader(':red[📰 Overall Headlines Analysis 😀😈]',divider='red')
    # Overall News Emotional Analysis
    # Concatenate all rows from the Headline column
    whole_text = df['Headline'].str.cat(sep='. ')
    col1, col2 = st.columns(2)
    with col1:
        # Word Cloud
        topWords = 50
        stopwords = set(STOPWORDS)
        wc = WordCloud(stopwords=stopwords,colormap='tab20c', max_words=topWords,width=800,height=700).generate(whole_text).to_image()
        fig = px.imshow(wc)
        fig.update_layout(height=410,title=f'{tickerHolder} - Word Cloud',xaxis_visible=False,yaxis_visible=False)
        st.plotly_chart(fig)
        
        
    with col2:
        def emotionAnalysis(whole_text):
            #Get the emotion frequencies
            emotions = NRCLex(whole_text).affect_frequencies
            #Filter and plot the non-zero emotions in one step
            y=[k for k, v in emotions.items() if v != 0]
            x=[v for k, v in emotions.items() if v != 0]
            df =pd.DataFrame({'Emotions':y,'Intensity':x})
            fig1 = px.bar(df,y='Intensity',x='Emotions',color='Emotions')
            fig1.update(layout_showlegend=False)
            fig1.update_layout(height=380,title=f'{ticker} - Emotion Analysis',xaxis_title='')
            st.plotly_chart(fig1,use_container_width=True)
        try:
            emotionAnalysis(whole_text)
        except ValueError as e:
            st.warning(f"No significant data to analyze: {e}")

        

    # Stock data from Yahoo Finance
    st.subheader(f":red[ 📈 {tickerHolder} - YTD Daily Chart 📉 ]",divider='red')
    security = yf.Ticker(tickerHolder)
    data  = security.history(period='ytd',interval='1d')
    data  = data [['Open', 'High', 'Low', 'Close', 'Volume']]
    highs = data['High'][:-1].max()
    lows = data['Low'][:-1].min()
    # Plot the candlestick chart
    #fig2,ax1 = mpf.plot(data, type='candle',style='charles', mav=(10,20,50), 
    #                   hlines=dict(hlines=[highs,(highs+lows)/2,lows],colors=['g','gray','r'],linestyle='--'),
    #                   volume=True, returnfig=True)
    
    fig2,ax1 = mpf.plot(data, type='candle',style='charles', mav=(10,20,50), 
                       hlines=dict(hlines=[highs,(highs+lows)/2,lows],colors=['g','gray','r'],linestyle='--'),
                       volume=True, returnfig=True)
    st.pyplot(fig2.figure)    # Show the plot in Streamlit
    st.divider()
    