import streamlit as st
import yfinance as yf
import pandas as pd

def main():  
    # calculate discount rate form beta
    def cal_discountRate(n):
        beta_values = {0: 5.0, 1: 6.0, 1.1: 6.5, 1.2: 7.0, 1.3: 7.5, 1.4: 8.0, 1.5: 8.5, 1.6: 9.0}
        return beta_values.get(n, 10.0)
    
    ## Calculate the DCF
    def modelDCF(cashFlow,cashFlowGrowthRate5Years,GrowthRateNext10Years,option20Years,GrowthRateNext20Years,discountRate):
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
        betaValue = security.info['beta']
        currentPrice = security.info['currentPrice']
        
        return freeCF,totalDebt,totalCash,OutStandingShares,netIncome,betaValue,currentPrice
    
    with st.container(border=True):
        st.write("Step 1: Enter Ticker, Current Year and Beta/Discount Rate")
        col1, col2 = st.columns(2)
        with col1:
            ticker = st.text_input("Ticker",placeholder="Eg. META, MSFT, AAPL").upper()
            currentYear = st.number_input("Current Year",2024)
        with col2:
            beta = st.number_input("Beta (Auto cal discount rate: for Manual)")
            discountRate = cal_discountRate(round(beta,1))/100 #convert to decimal
            custom_beta = st.toggle("For Manual: Use custom Discount Rate!",value=False)
            if custom_beta:
                discountRate = st.number_input("Enter Discount Rate: eg. 5, 9, 10...",value=10.0,step=.25)/100    
        #step 2
        st.divider()
        st.write("Step 2: Enter Financial Data / Auto Generate Data")
        # Check if want to auto parse data
        auto_parsed_data = st.toggle("Auto Generate data from Yahoo Finance",value=False)
        if auto_parsed_data:
            if ticker == "":
                st.error("Ticker required!")
                return
            try:
                with st.spinner("Parsing Data..."):
                    freeCF,totalDebt,totalCash,OutStandingShares,netIncome,betaValue,currentPrice = autoData(ticker)
                    st.success("Data parsed successfully!")
                    cashFlow = freeCF/1000000
                    totalDebt = totalDebt/1000000
                    cashAndSTinvestment = totalCash/1000000
                    outstandingShares = round(OutStandingShares/1000000,0)
                   
                    # show all the data
                    col1, col2 = st.columns(2)
                    with col1:
                        useNetIncome = st.toggle("Option: Use Net Income?",value=False)
                        st.write(f"**Free Cash Flow(TTM):** ${cashFlow:,.0f}M")
                        if useNetIncome:
                            cashFlow = netIncome/1000000
                            st.write(f"**:red[Net Income:](TTM)** ${cashFlow:,.0f}M")
                            if netIncome < 0:
                                st.error("Net Income is negative! Try Manually with Positive Value!",icon="⚠️")
                                return
                        st.write(f"**Total Debt:** ${totalDebt:,.0f}M")
                        st.write(f"**Cash and ST Investment:** ${cashAndSTinvestment:,.0f}M")
                        st.write(f"**Outstanding Shares:** {outstandingShares:,.0f}M")
                    with col2:
                        discOverwrite = st.toggle("Overwrite Discounted Rate",value=False)
                        st.write(f"**Beta Value:** {betaValue:.2f}")
                        st.write(f"**Based on Beta Discounted Rate:** {cal_discountRate(round(betaValue,1))}%")
                        st.write(f"**Current Price:** ${currentPrice:,.2f}")
                        discountRate = cal_discountRate(round(betaValue,1))/100 #convert to decimal
                        if discOverwrite:
                            discountRate = st.number_input("Enter Discount Rate: eg. 5, 9, 10...",value=10.0,step=.25)/100
                            st.write(f"**:red[New Discounted Rate:]** {round(discountRate*100,2)}%")                   
                    
                    ## Free Cash Flow and Net Income negative
                    if cashFlow < 0:
                        st.error("Free Cash Flow is negative! Try Net Income or Manually!",icon="⚠️")
                        return
     
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}",icon="⚠️") 
                st.error("Please Enter manually!",icon="⚠️",type="warning")
        else:
            st.info("Enter ***Numbers🔢** in Millions | 📋Use: Recent 10K/10Q Statements")
            col1, col2= st.columns(2)
            with col1:
                cashFlow = st.number_input(":green[Free Cash Flow/Net Income (TTM)]")
                totalDebt = st.number_input(":red[Total Debt (LT + ST Debt) 10Q]")
            with col2:
                cashAndSTinvestment = st.number_input(":green[Cash & ST Investment - Balance Sheet 10Q]")
                outstandingShares = st.number_input(":blue[Outstanding Shares]")
         
        # Enter Growth Rates
        st.divider()
        st.write(f"Step 3: Enter Growth Rates")
        auto_parsed_growth = st.toggle("Auto Calculate growth data",value=False)
        period = 10
        GrowthRateNext20Years = 0
        if auto_parsed_growth:
            option20Years = st.toggle("Project for 20 Years?",value=False)
            try:
                cashFlowGrowthRate5Years = yf.Ticker(ticker).info['trailingPE'] / yf.Ticker(ticker).info['pegRatio']
                GrowthRateNext10Years = cashFlowGrowthRate5Years /2
                st.write("Growth Rate Next 5 Years: ",round(cashFlowGrowthRate5Years,2))
                st.write("Growth Rate 6-10 Years: ",round(GrowthRateNext10Years,2))

                if option20Years:
                        GrowthRateNext20Years = max(GrowthRateNext10Years/2,4.0)
                        period = 20
                        st.write("Growth Rate After 10 Years: ",round(GrowthRateNext20Years,2))
                st.write('Calculating for ',period,' Years')
                st.success("Data parsed successfully!")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}",icon="⚠️")
                st.error("Please Calculate manually!",icon="⚠️",type="warning")
        else:
            st.info("Enter Growth Rates. (from: finviz.com, seekingalpha.com...)")  
            option20Years = st.toggle("Project for 20 Years?",value=False)
            col1, col2 = st.columns(2)
            with col1:
                cashFlowGrowthRate5Years = st.number_input("Growth Rate Next 5 Years")
                GrowthRateNext10Years = st.number_input("Growth Rate 6-10 Years")
            with col2:
                GrowthRateNext20Years = 0
                if option20Years:
                    GrowthRateNext20Years = st.number_input("Growth Rate After 10 Years")
                    period = 20
                              
        st.divider()
        ## submit button
        select_button = st.button("Run DCF Model",type="primary",use_container_width=True)
        
        # Validation rules
        validation_checks = [
        (ticker == "", "Ticker is required!"),
        (cashFlow < 0, "Free Cash Flow/Net Income must be greater than 0!"),
        (totalDebt < 0, "Total Debt must be 0 or greater!"),
        (cashAndSTinvestment < 0, "Cash and Short-term Investment must be 0 or greater!"),
        (outstandingShares <= 0, "Outstanding Shares must be greater than 0!"),
        (cashFlowGrowthRate5Years <= 0, "Growth Rate Next 5 Years must be non-negative!"),
        (GrowthRateNext10Years <= 0, "Growth Rate 6-10 Years must be non-negative!"),
        ]
        

    # Run the Model
    if select_button:
        # Input validation
        # Check for any validation failures
        for condition, message in validation_checks:
            if condition:
                st.error(message)
                break
        else:  # This else executes if the loop was not broken.
            # Run the Model when button is clicked
            try:
                with st.container(border=True):
                    df_DCF = modelDCF(cashFlow,cashFlowGrowthRate5Years/100,GrowthRateNext10Years/100,option20Years,GrowthRateNext20Years/100,discountRate)
                    # Post Calculations
                    presentValue = df_DCF.dis_Value.sum()
                    # Calculation per share
                    intrinsicValuePre = presentValue/outstandingShares
                    debtPerShare = totalDebt/outstandingShares
                    cashPerShare = cashAndSTinvestment/outstandingShares
                    intrinsicValue = intrinsicValuePre - debtPerShare+cashPerShare

                    ### Report
                    st.subheader(f"Results for :red[{ticker}] | Discouted rate :red[{round(discountRate*100,2)}%] ",divider='rainbow')
                    col1, col2 = st.columns(2)
                    with col1:
                        st.success(f"Intrinsic Value Price: ${intrinsicValue.round(2)} " )
                    with col2:
                        st.warning(f"Current Price: ${currentPrice:.2f}")
                    discountedPrice = round((currentPrice/intrinsicValue-1)*100,1)
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
            
    #display financial statements
    def financialStatements(statement):
        df = pd.DataFrame(statement.iloc[:,0:4])
        df = df/1000000
        df = df[(df.T != 0).any()]
        df.dropna(inplace=True)
        # Check if the columns are datetime type
        if pd.to_datetime(df.columns, errors='coerce').notnull().all():
            # If they can be converted to datetime, format them
            df.columns = pd.to_datetime(df.columns).strftime('%Y-%m-%d')
        else:
            # Else, just convert them to string
            df.columns = df.columns.astype(str)
        st.dataframe(df,use_container_width=True)

    # check is Ticker is entered:
    if ticker != "":
        with st.expander("View: Financial Statements - Quaterly (in millions)",icon="📈"):
            ta1, ta2, ta3 = st.tabs(["Balance Sheet","Income Statement","Cash Flow"])
            with ta1:
                financialStatements(yf.Ticker(ticker).quarterly_balance_sheet)
            with ta2:
                financialStatements(yf.Ticker(ticker).quarterly_income_stmt)
            with ta3:
                financialStatements(yf.Ticker(ticker).quarterly_cashflow)
            
 
    
    #display adam khoo's video
    with st.expander("Guide: Watch Adam khoo's YouTube Video",icon="📺"):
        #st.subheader("📺 Watch Adam khoo's Video 📺",divider=True)
        st.markdown("""<iframe  height="400" width="100%"
                    src="https://www.youtube-nocookie.com/embed/TaOfxnXQ3YE?si=sKVmNEXQxVzNxYeV&amp;start=923" 
                    title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; 
                    clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" 
                    referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>""", unsafe_allow_html=True)