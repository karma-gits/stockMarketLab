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
import plotly.subplots as sp
import nltk
import nltk_download # dont delete this
import corpora # dont delete this
import textblob # dont delete this

def main():
    def emotionAnalysis(whole_text):
        # Get emotion frequencies
        emotions = NRCLex(whole_text).affect_frequencies
        # Define positive and negative emotion categories
        positive_emotions = ['joy', 'trust', 'anticipation', 'surprise']
        negative_emotions = ['anger', 'disgust', 'fear', 'sadness']

        # Calculate compound score
        positive_score = sum([emotions.get(emotion, 0) for emotion in positive_emotions])
        negative_score = sum([emotions.get(emotion, 0) for emotion in negative_emotions])
        compound_value = positive_score - negative_score

        # Prepare data for emotions plot
        y = [k for k, v in emotions.items() if v != 0]
        x = [v for k, v in emotions.items() if v != 0]
        df = pd.DataFrame({'Emotions': y, 'Intensity': x})

        # Create subplots
        fig = sp.make_subplots(rows=2, cols=1, subplot_titles=('Emotions', 'Overall Score'),
                               row_heights=[0.85, 0.15])

        # Top plot for emotion frequencies
        emotion_fig = px.bar(df.sort_values(by='Intensity', ascending=False), x='Emotions', y='Intensity', color='Emotions')
        emotion_fig.update_traces(width=.8)  # Making the bars thicker (where 1 is full width and 0 is no width)
        for trace in emotion_fig.data:
            fig.add_trace(trace, row=1, col=1)

        # Bottom plot for compound score
        compound_color = '#2a9d8f' if compound_value > 0 else '#e63946'
        compound_fig = px.bar(x=[compound_value], color_discrete_sequence=[compound_color])
        for trace in compound_fig.data:
            fig.add_trace(trace, row=2, col=1)

        # Update layout
        fig.update_layout(width=800, height=500,margin=dict(t=50, b=80), showlegend=False)#
        # Set x-axis limits for the compound score plot
        fig.update_xaxes(range=[-1, 1], row=2, col=1)  # Set x-axis limits from -1 to 1
        # Hide y-axis label and y-tick labels for compound score
        fig.update_yaxes(title_text='', row=2, col=1)  # Hide y-axis label
        fig.update_yaxes(showticklabels=False, row=2, col=1)  # Remove y-tick labels
        # Use Streamlit to display the plot
        st.plotly_chart(fig, use_container_width=True)
        
    #def emotionAnalysis(whole_text):
    #    #Get the emotion frequencies
    #    emotions = NRCLex(whole_text).affect_frequencies
    #    #Filter and plot the non-zero emotions in one step
    #    y=[k for k, v in emotions.items() if v != 0]
    #    x=[v for k, v in emotions.items() if v != 0]
    #    df =pd.DataFrame({'Emotions':y,'Intensity':x})
    #    fig1 = px.bar(df.sort_values(by='Intensity',ascending=False),y='Intensity',x='Emotions',color='Emotions')
    #    fig1.update(layout_showlegend=False)
    #    fig1.update_layout(height=380,title={'text': 'Overall Emotion Analysis', 'x': 0.5, 'xanchor': 'center'},xaxis_title='')
    #    st.plotly_chart(fig1,use_container_width=True)    
    def wordCloud(whole_text,topWords=100):
        # Word Cloud
        stopword = set(STOPWORDS)    
        wc = WordCloud(stopwords=stopword,colormap='tab20c', max_words=topWords,width=800,height=850,margin=1).generate(whole_text).to_image()
        #st.image(wc, use_column_width=True)
        fig = px.imshow(wc)
        fig.update_layout(width=800, height=500,xaxis_visible=False,yaxis_visible=False)#
        st.plotly_chart(fig,use_container_width=True)
        
    # overallAnalysis = emotionAnalysis + wordCloud
    def overallAnalysis(whole_text,topWords=70):
        col1, col2 = st.columns(2,gap="small",vertical_alignment="center")
        with col1:
            # display title with center alignment
            st.markdown("<h5 style='text-align: center;'>Most Mentioned</h5>",unsafe_allow_html=True)
            try:
                wordCloud(whole_text,topWords)
            except ValueError as e:
                st.warning(f"No significant data to analyze: {e}")   
        with col2:
            st.markdown("<h5 style='text-align: center;'>Emotion Analysis</h5>",unsafe_allow_html=True)
            try:
                emotionAnalysis(whole_text)
            except ValueError as e:
                st.warning(f"No significant data to analyze: {e}")    
    ## vader sentiment analysis
    vader = SentimentIntensityAnalyzer()
    
    # main brain Starts here
    tab1, tab2 = st.tabs(["📰 News Headlines Analysis","📰 Custom Text Analysis"])
    with tab2:
        # Custom Text Analysis
        st.subheader(f":red[ Custom Text Sentiment Analysis 😀😈]",divider='rainbow')
        with st.form("customTextForm"):
            customText = st.text_area("Enter your text here")
            if st.form_submit_button("Analyze", use_container_width=True,type='primary'):
                overallAnalysis(customText,topWords=100)
    with tab1:
        st.subheader("News Headlines Sentiment Analysis 😀🤬🤯",divider='rainbow')
        tickerHolder = str.upper(st.text_input("**Enter a Ticker to Analyze**",placeholder="Enter a Ticker Symbol! (*Not for otc stocks)"))
        if tickerHolder != "":
            #scrape data from finviz
            finviz_url = 'https://finviz.com/quote.ashx?t='
            news_tables = {}
            url = finviz_url + tickerHolder
            req = Request(url=url, headers={'user-agent': 'my-app'})
            try:
                response = urlopen(req)
                html = BeautifulSoup(response, features='html.parser')
                news_table = html.find(id='news-table')
                if not news_table:
                    st.warning("No News table found on the page.",icon="⚠️",type="warning")
            except Exception as e:
                st.error("Please try again! with a valid ticker! (Not for OTC stocks)",icon="⚠️")
                st.error(f"Failed to fetch data: {e}")
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
            
            if df.empty:
                st.warning(f"{tickerHolder} - No Major News available for today.",icon="⚠️")
            else:
                #apply vader sentiment to the headline
                df['VaderSentiment'] = df['Headline'].apply(lambda title: vader.polarity_scores(title)['compound'])
                ## new columns with emoji 
                df['Sentiment'] = df['VaderSentiment'].apply(lambda x: "😀😀" if x > .4 else "🙂🙂" if x > .1 else "🙂" if x > .05 else "❔" if x > -.05 else "😡" if x>-.4 else "😡😡")
                ### News headlines
                st.subheader(f":red[📰Today's Headlines for '{tickerHolder}'] | {dt.datetime.now().date()}",divider='red')
                #st.dataframe(df[['time','Headline','Emoji']].set_index('time'),use_container_width=True) #prints tickers dataframe
                with st.container(height=450,border=True):
                    st.table(df[['time','Headline','Sentiment']].set_index('time')) #prints tickers dataframe

                # Analyze Headlines
                st.subheader(':red[📰Overall Headlines Analysis 😀😈]',divider='red')
                # Overall News Emotional Analysis
                # Concatenate all rows from the Headline column
                whole_text = df['Headline'].str.cat(sep='. ')
                try:
                    overallAnalysis(whole_text)
                except Exception as e:
                     st.error(f"An unexpected error occurred: {e}",icon="⚠️")

            # Stock data from Yahoo Finance
            st.subheader(f":red[📉{tickerHolder}] - 6 Months Daily Chart",divider='red')
            security = yf.Ticker(tickerHolder)
            # display 6 months of data
            data  = security.history(period='6mo',interval='1d') #ytd
            data  = data [['Open', 'High', 'Low', 'Close', 'Volume']]
            highs = data['High'][:-1].max()
            lows = data['Low'][:-1].min()
            # Plot the candlestick chart
            fig2,ax1 = mpf.plot(data, type='candle',style='yahoo', mav=(10,20,50), 
                               hlines=dict(hlines=[highs,(highs+lows)/2,lows],colors=['r','gray','g'],linestyle=['-','--','-']),
                               volume=True, returnfig=True)
            st.pyplot(fig2.figure,use_container_width=True)    # Show the plot in Streamlit 