import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import random
import streamlit as st
import plotly.express as px

def main():
    # set seed to ensure reproducibility 
    #random.seed(42) # Testing purpose only

    # generate a sample with probability n%
    def generate_samples(numTrades,winRate,profit,loss):
        trades = []
        results = 0
        cum_profit = []
        total_profit = 0

        # Find weigthed choice win or loss.
        def weigthed_choice(winRate):
            #loss_rate = 1 - winRate
            return random.choices([1,0], weights=[winRate, (1 - winRate)])[0]

        # Generate trades with index
        for i in range(numTrades):
            result = weigthed_choice(winRate)
            #trades.append(result)
            if result == 1:
                total_profit += profit  # add profit
                results += 1
            else:
                total_profit += loss  # add loss  
                results   
            cum_profit.append(total_profit)   
            trades.append(results)
        #return trades, cum_profit,total_profit
        return trades, cum_profit

    with st.container(border=True):
        # user input
        numTrades = st.number_input("Number of trades to run?", 10,2000, 500)
        winRate = st.number_input("Win rate % (Probability of winning)", 0.00,100.00, 30.00)
        risk = st.number_input("What is the $ Risk?", 1,10000000,100)
        winRatio = st.number_input("What is the win/loss ratio?", 0.00,100.00, 4.00)
        num_simulations = st.number_input("Number ofsimulations to run?", 1,20000, 200)
        submit = st.button(":running: Run Simulations :cook:",type="primary")

        # calculate the profit
        profit = winRatio*risk
        loss = -1*risk

        # Run the simulation N times
        df = pd.DataFrame(index=range(1,numTrades+1), columns=range(1,num_simulations+1))
        df_trades = pd.DataFrame(index=range(1,numTrades+1), columns=range(1,num_simulations+1))

        def monte_carlo(n):
            for i in range(1,n+1):
                # trades results
                winLossResults,tradeResults = generate_samples(numTrades, winRate/100, profit, loss)
                # profit results
                df[i] = tradeResults  
                # win or loss results
                df_trades[i] = winLossResults
            return df,df_trades
    
    with st.container(border=True):
        if submit:
            with st.spinner('Running simulations...'):
                df,df_trades = monte_carlo(num_simulations)
            #df,df_trades = monte_carlo(num_simulations)

            st.subheader("Simulation Results")
            # print the results from win or loss ratio
            final_trades =list(df_trades.tail(1).values[0]/numTrades)
            #print(final_trades)
            averageWinLoss = np.mean(final_trades)
            # create a dataframe to show the results
            final_retrun = list(df.tail(1).values[0])
            avgerageProfits = np.mean(final_retrun)
            with st.container(border=True):
                col1, col2 = st.columns(2,)
                with col1:
                    st.write(":red[**Win Rate%** 🎯:chart_with_upwards_trend:]")
                    st.text("Avg Win% : {:,.2f}%".format(averageWinLoss*100))
                    st.text("Max Win% : {:,.2f}%".format(max(final_trades)*100))
                    st.text("Min Win% : {:,.2f}%".format(min(final_trades)*100))
    
                with col2:
                    # create a dataframe to show the results
                    st.write(":red[**Total Return** $ :dollar: :moneybag:]")
                    st.text("Avg Return : ${:,.0f}".format(avgerageProfits))
                    st.text("Max Return : ${:,.0f}".format(max(final_retrun)))
                    st.text("Min Return : ${:,.0f}".format(min(final_retrun)))
            
            title = (f"{num_simulations:,} Simulations Results - ({winRate}% win rate | {winRatio} win/loss ratio.)")
            #st.line_chart(df,x_label=f'{numTrades:,} Trades',y_label='Return')
            with st.spinner('Plotting results...'):
                fig = px.line(df)
                fig.update(layout_showlegend=False)
                fig.update_layout(height=500,width=400,title=title,title_font_size=15,xaxis_title=f'{numTrades:,} Trades',yaxis_title='Return')
                st.plotly_chart(fig,use_container_width=True)

            # plot distribution 
            def plot_distribution(data):
                lower, upper = np.quantile(data, (0.025, 0.975))
                fig = px.histogram(data, nbins=20, histnorm='density', title="Distribution of Results")
                fig.add_vline(x=data.mean(), line_color='green')
                fig.add_vline(x=lower, line_color='red', line_dash='dash')
                fig.add_vline(x=upper, line_color='red', line_dash='dash')
                fig.update_layout(xaxis_title="")
                fig.update(layout_showlegend=False)
                st.plotly_chart(fig,use_container_width=True)
            
            st.subheader("Distribution within 95% confidence interval")
            left, right = st.tabs(["Win Rate % Distribution"," Total Return Distribution"])
            with left:
                # Plot distribution of win ratio
                winRate = (df_trades.tail(1)/numTrades).values[0]*100
                plot_distribution(winRate)

            with right:
                # plot distribution for total Return
                total_Return = (df.tail(1)).values[0]
                plot_distribution(total_Return)

    with st.container(border=True):
        st.subheader("Profitable Requirement Guidelines")
        st.write("**WinRate Needed!** :red[is the required winrate to pass the **Break Even** threshold.]")
        
        data = {'Risk:Reward Ratio': ['1:1', '1:2','1:3','1:4','1:5','1:6','1:7','1:8','1:9','1:10' ],
                'WinRate needed!': ['51%','34%','26%','21%','17%','15%','13%','12%','11%','10%']}

        df = pd.DataFrame(data)
        st.dataframe(df,hide_index=True)
    st.markdown("""#### Disclaimer:<br> - This is a simulation and not a real trading strategy. The results are not guaranteed and should be used for educational purposes only.""",unsafe_allow_html=True)