import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import random
import streamlit as st
import plotly.express as px

# Function to determine the outcome of a trade based on weighted win rate
def weighted_choice(win_rate):
    return random.choices([1, 0], weights=[win_rate, (1 - win_rate)])[0]

# Function to generate samples based on the number of trades, win rate, profit, and loss
def generate_samples(num_trades, win_rate, profit, loss):
    trades = []
    results = 0
    cumulative_profit = []
    total_profit = 0
    # Run the trades for num_trades times
    for _ in range(num_trades):
        result = weighted_choice(win_rate)
        total_profit += profit if result == 1 else loss
        results += result  # Increment results only for wins
        cumulative_profit.append(total_profit)
        trades.append(results)
    return trades, cumulative_profit # Return the trades and cumulative profit

# Function to plot distribution
def plot_distribution(data):
    lower, upper = np.quantile(data, (0.025, 0.975))
    fig = px.histogram(data, nbins=20, histnorm='density', title="Distribution of Results")

    # Adding lines for mean and 95% confidence interval
    fig.add_vline(x=data.mean(), line_color='green')
    fig.add_vline(x=lower, line_color='red', line_dash='dash')
    fig.add_vline(x=upper, line_color='red', line_dash='dash')
    fig.update_layout(
        title=dict(
            text=f"Distribution of Results (Mean: {data.mean():,.0f}, 95% CI: {lower:.0f} - {upper:.0f})",
            xanchor='center',
            x=0.5,  # Center the title horizontally
        ),
        xaxis_title="",
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

# Main function to run the Streamlit application
def main():
    # user input for simulation parameters
    with st.container(border=True):
        # User input for simulation parameters
        num_trades = st.number_input("Number of trades to run?", 10, 2000, 300)
        win_rate = st.number_input("Win rate % (Probability of winning)", 10.00, 100.00, 40.0) / 100  # converted to proportion
        risk = st.number_input("What is the $ Risk?", 1, 10_000_000, 100)
        win_loss_ratio = st.number_input("What is the win/loss ratio?", 0.50, 100.00, 3.00)
        num_simulations = st.number_input("Number of Simulations to Run?", 1, 15_000, 200)
        # Calculate profit and loss amounts
        profit = win_loss_ratio * risk
        loss = -risk
        # check if the user has filled in all the fields
        if win_loss_ratio >0 and risk > 0:
            st.write(f"Risk =  :red[${risk}] | Reward =:green[${round(win_loss_ratio * risk)}]")
        # Click to run the simulation
        submit = st.button(":running: Run Simulations :cook:", type="primary", use_container_width=True)

        # Monte Carlo simulation function
        def monte_carlo(n):
            df = pd.DataFrame(index=range(1, num_trades + 1), columns=range(1, n + 1))
            df_trades = pd.DataFrame(index=range(1, num_trades + 1), columns=range(1, n + 1))
            for i in range(1, n + 1):
                win_loss_results, trade_results = generate_samples(num_trades, win_rate, profit, loss)
                df[i] = trade_results
                df_trades[i] = win_loss_results
            return df, df_trades
    # Run the simulation N times and display the results
    with st.container(border=True):
        if submit:
            with st.spinner('Running simulations...'):
                df, df_trades = monte_carlo(num_simulations)

            # Display simulation results
            st.header(":green_heart: :green[**Simulation Results**]:sunglasses: :+1:",divider="green")
            # calculate the average win rate
            final_trades = list(df_trades.tail(1).values[0] / num_trades)
            average_win_loss = np.mean(final_trades)
            # Prepare final return data for display
            final_return = list(df.tail(1).values[0])
            average_profits = np.mean(final_return)
            # Display results
            with st.container(border=True):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(":red[**Win Rate%** 🎯:chart_with_upwards_trend:]")
                    st.text("Avg Win% : {:,.2f}%".format(average_win_loss * 100))
                    st.text("Max Win% : {:,.2f}%".format(max(final_trades) * 100))
                    st.text("Min Win% : {:,.2f}%".format(min(final_trades) * 100))
                with col2:
                    st.write(":red[**Total Return** $ :dollar: :moneybag:]")
                    st.text("Avg Return : ${:,.0f}".format(average_profits))
                    st.text("Max Return : ${:,.0f}".format(max(final_return)))
                    st.text("Min Return : ${:,.0f}".format(min(final_return)))

            # line chart 
            with st.container(border=True):
                title = f"{num_simulations:,} Simulations - ({win_rate * 100:.0f}% Win Rate | {win_loss_ratio} Win/Loss Ratio)"
                with st.spinner('Plotting results...'):
                    fig = px.line(df)
                    fig.update(layout_showlegend=False)
                    fig.update_layout(height=500, width=400, title=dict(text=title,
                                                                        font_size=15,
                                                                        xanchor='center',  # Center the title
                                                                        x=0.5,),
                                      title_font_size=18,
                                      xaxis_title=f'{num_trades:,} Trades', yaxis_title='Return')
                    st.plotly_chart(fig, use_container_width=True)

            # Plot distribution
            st.subheader(":orange[**Distribution within 95% confidence interval**]",divider="orange")
            with st.container(border=True):
                left, right = st.tabs(["Win Rate % Distribution", "Total Return Distribution"])
                with left:
                    win_rate_distribution = (df_trades.tail(1) / num_trades).values[0] * 100
                    plot_distribution(win_rate_distribution)

                with right:
                    total_return_distribution = df.tail(1).values[0]
                    plot_distribution(total_return_distribution)

    with st.container(border=True):
        st.subheader("Profitable Requirement Guidelines")
        st.write("**Win Rate Needed!** :red[is the required winrate to pass the :green[Break Even] threshold.]")
        
        data = {
            'Risk:Reward Ratio': ['1:1', '1:2', '1:3', '1:4', '1:5', '1:6', '1:7', '1:8', '1:9', '1:10'],
            'Win Rate needed!': ['51%', '34%', '26%', '21%', '17%', '15%', '13%', '12%', '11%', '10%']
        }
        st.dataframe(data, hide_index=True)