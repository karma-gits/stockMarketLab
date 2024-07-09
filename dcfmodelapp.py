import streamlit as st
import yfinance as yf
import pandas as pd

def main():
    # calculate discount rate form beta
    def cal_discountRate(n):
        beta_values = {0: 5.0, 1: 6.0, 1.1: 6.5, 1.2: 7.0, 1.3: 7.5, 1.4: 8.0, 1.5: 8.5, 1.6: 9.0}
        return beta_values.get(n, 10.0)
    
    ## Calculate the DCF
    def modelDCF(cashFlow,cashFlowGrowthRate5Years,GrowthRateNext10Years,option20Years,GrowthRateNext20Years):
        #initalzie 
        projected = cashFlow
        discountFactor = 0

        df = pd.DataFrame(index=range(0,period),columns=['year','projected_CF','dis_Value'])
        df['year'] = range(currentYear,currentYear+period)

        #calculate the DCF
        cashFlowProjected =[]
        discountValue = []
        for i in range(1,6):
            projected = projected+(projected*cashFlowGrowthRate5Years)
            cashFlowProjected.append(projected)
            discountFactor = projected/((1+discountRate)**i)
            discountValue.append(discountFactor)
        for i in range(6,11):
            projected = projected+(projected*GrowthRateNext10Years)
            cashFlowProjected.append(projected)
            discountFactor = projected/((1+discountRate)**i)
            discountValue.append(discountFactor)
        if option20Years:
            for i in range(11,21):
                projected = projected+(projected*GrowthRateNext20Years)
                cashFlowProjected.append(projected)
                discountFactor = projected/((1+discountRate)**i)
                discountValue.append(discountFactor)
        df['projected_CF'] = cashFlowProjected
        df['dis_Value'] = discountValue
        return round(df,2)
    
    ## Auto Data parsed
    def autoData(ticker):
        security = yf.Ticker(ticker)
        stockFCF = pd.DataFrame(security.quarterly_cashflow)
        
        freeCF= stockFCF[stockFCF.columns[0:4]].loc['Free Cash Flow'].sum() #TTM Free Cash Flow
        
        stockBAL = pd.DataFrame(security.quarterly_balance_sheet)
        totalCash = stockBAL[stockBAL.columns[0:1]].loc['Cash Cash Equivalents And Short Term Investments'].values[0]
        
        shortTerm = stockBAL[stockBAL.columns[0:1]].loc['Current Debt And Capital Lease Obligation'].values[0] 
        longTerm = stockBAL[stockBAL.columns[0:1]].loc['Long Term Debt And Capital Lease Obligation'].values[0]
        totalDebt = shortTerm + longTerm
        
        stockNetincome = pd.DataFrame(security.quarterly_income_stmt)
        netIncome = stockNetincome[stockNetincome.columns[0:4]].loc['Net Income From Continuing And Discontinued Operation'].sum()

        OutStandingShares = stockBAL[stockBAL.columns[0:1]].loc['Ordinary Shares Number'].values[0]
        
        return freeCF,totalDebt,totalCash,OutStandingShares,netIncome
    
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            ticker = st.text_input("Ticker",placeholder="Eg. META, SPY, AAPL").upper()
            closePrice = st.number_input("Current  Price")
            currentYear = st.number_input("Current Year",2024)
        with col2:
            beta = st.number_input("Beta (to calculate discount rate)")
            discountRate = cal_discountRate(round(beta,1))/100 #convert to decimal
            custom_beta = st.checkbox("Use custom Discount Rate!",value=False)
            if custom_beta:
                discountRate = st.number_input("Discount Rate",value=6.0)/100    
            
        st.warning("Enter Growth Rates. (from: finviz.com, seekingalpha.com...)")          
        col1, col2 = st.columns(2)
        with col1:
            cashFlowGrowthRate5Years = st.number_input("Growth Rate Next 5 Years")
            GrowthRateNext10Years = st.number_input("Growth Rate 5-10 Years")
        with col2:
            option20Years = st.checkbox("Project for 20 Years?",value=False)
            period = 10
            GrowthRateNext20Years = 0
            if option20Years:
                GrowthRateNext20Years = st.number_input("Growth Rate After 10 Years")
                period = 20
        auto_parsed = st.checkbox("Auto parse data from Yahoo Finance",value=False)
        if auto_parsed and ticker:
            try:
                with st.spinner("Parsing Data..."):
                    freeCF,totalDebt,totalCash,OutStandingShares,netIncome = autoData(ticker)
                    st.success("Data parsed successfully!")
                    cashFlow = freeCF/1000000
                    totalDebt = totalDebt/1000000
                    cashAndSTinvestment = totalCash/1000000
                    outstandingShares = round(OutStandingShares/1000000,0)
                    useNetIncome = st.checkbox("Use Net Income for Projection",value=False)
                    # show all the data
                    st.write(f"**Free Cash Flow:** ${cashFlow:,.0f}M")
                    st.write(f"**Total Debt:** ${totalDebt:,.0f}M")
                    st.write(f"**Cash and ST Investment:** ${cashAndSTinvestment:,.0f}M")
                    st.write(f"**Outstanding Shares:** {outstandingShares:,.0f}M")
                    
                    if useNetIncome:
                        cashFlow = netIncome/1000000
                        st.write(f"**Net Income:** ${cashFlow:,.0f}M")
            except:
                st.error("Data not found! | Please Enter Manually | No FUNDS/ETFS | Run Again!")    
        else:
            st.info("Enter ***Numbers🔢** in Millions | 📋Enter datas from: Recent 10K/10Q Statements")
            col1, col2= st.columns(2)
            with col1:
                cashFlow = st.number_input("Free Cash Flow/Net Income (TTM)")
                totalDebt = st.number_input("Total Debt (Long term + short term Debt) 10Q")
            with col2:
                cashAndSTinvestment = st.number_input("Cash and ST Investment - 10Q Balance Sheet 10Q")
                outstandingShares = st.number_input("Outstanding Shares")
               
        ## submit button
        select_button = st.button("Run DCF Model",type="primary")
        

    # Run the Model
    if select_button:
        try:
            with st.container(border=True):
                df_DCF = modelDCF(cashFlow,cashFlowGrowthRate5Years/100,GrowthRateNext10Years/100,option20Years,GrowthRateNext20Years/100)


                # Post Calculations
                presentValue = df_DCF.dis_Value.sum()
                # Calculation per share
                intrinsicValuePre = presentValue/outstandingShares
                debtPerShare = totalDebt/outstandingShares
                cashPerShare = cashAndSTinvestment/outstandingShares
                intrinsicValue = intrinsicValuePre - debtPerShare+cashPerShare
                
                ### Report
                st.subheader(f"Results for :red[{ticker}] | discouted rate :red[{round(discountRate*100,2)}%] :",divider='rainbow')
                st.success(f"Intrinsic Value per share : ${intrinsicValue.round(2)} " )
                discountedPrice = ( closePrice/intrinsicValue-1).round(2)*100
                if discountedPrice < 0:
                    st.success(f'**Under Valued! Discount: {discountedPrice}%**')
                else:
                    st.error(f'**Over Valued! By: {discountedPrice}%**')

                st.subheader(f":gray[ :moneybag: :red[{ticker}] - Projected Cash Flow for :red[{period} Years]]",divider=True)
                st.line_chart(df_DCF.set_index('year'),x_label='Year',y_label='Projected Cash Flow')

                with st.expander("Show Projected Cash Flow Table",icon="🚨",expanded=True):
                    st.write(f":red[{ticker}] Projected Cash Flow {period} Years")
                    st.table(df_DCF.set_index('year').T)
        except:
            st.error("🚨🚨🚨 Fill all the data  | Try Again! 🚨🚨🚨  ")

    
        
        



