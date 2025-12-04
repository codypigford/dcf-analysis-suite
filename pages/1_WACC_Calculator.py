import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
import yfinance as yf

# Page configuration
st.set_page_config(
    page_title="WACC Calculator",
    page_icon="📈",
    layout="wide"
)

# Credit spreads lookup table
credit_spreads = [
    {"GreaterThan": -100000, "LessThan": 0.199999, "Rating": "D2/D", "Spread": 19.00},
    {"GreaterThan": 0.2, "LessThan": 0.649999, "Rating": "C2/C", "Spread": 15.50},
    {"GreaterThan": 0.65, "LessThan": 0.799999, "Rating": "Ca2/CC", "Spread": 10.10},
    {"GreaterThan": 0.8, "LessThan": 1.249999, "Rating": "Caa/CCC", "Spread": 7.28},
    {"GreaterThan": 1.25, "LessThan": 1.499999, "Rating": "B3/B-", "Spread": 4.42},
    {"GreaterThan": 1.5, "LessThan": 1.749999, "Rating": "B2/B", "Spread": 3.00},
    {"GreaterThan": 1.75, "LessThan": 1.999999, "Rating": "B1/B+", "Spread": 2.61},
    {"GreaterThan": 2.0, "LessThan": 2.2499999, "Rating": "Ba2/BB", "Spread": 1.83},
    {"GreaterThan": 2.25, "LessThan": 2.49999, "Rating": "Ba1/BB+", "Spread": 1.55},
    {"GreaterThan": 2.5, "LessThan": 2.999999, "Rating": "Baa2/BBB", "Spread": 1.20},
    {"GreaterThan": 3.0, "LessThan": 4.249999, "Rating": "A3/A-", "Spread": 0.95},
    {"GreaterThan": 4.25, "LessThan": 5.499999, "Rating": "A2/A", "Spread": 0.85},
    {"GreaterThan": 5.5, "LessThan": 6.499999, "Rating": "A1/A+", "Spread": 0.77},
    {"GreaterThan": 6.5, "LessThan": 8.499999, "Rating": "Aa2/AA", "Spread": 0.60},
    {"GreaterThan": 8.5, "LessThan": 100000, "Rating": "Aaa/AAA", "Spread": 0.45}
]

def get_credit_spread(rating, credit_spreads):
    """
    Looks up the credit spread for a given credit rating.

    Args:
        rating (str): The credit rating of the firm.
        credit_spreads (list): A list of dictionaries containing credit spread data.

    Returns:
        float: The credit spread as a decimal, or NaN if no match is found.
    """
    for entry in credit_spreads:
        if entry["Rating"].strip().lower() == rating.strip().lower():
            return float(entry["Spread"]) / 100
    st.warning(f"Warning: No spread found for rating {rating}")
    return np.nan

def get_stock_data(ticker_symbol, index_symbol):
    """
    Fetch stock and index data from yfinance.

    Args:
        ticker_symbol (str): Stock ticker symbol
        index_symbol (str): Market index ticker symbol

    Returns:
        tuple: (ticker object, stock_data, index_data, info)
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info

        # Download historical data for beta calculation
        stock_data = yf.download(ticker_symbol, period='5y', interval='1mo', progress=False)['Close']
        index_data = yf.download(index_symbol, period='5y', interval='1mo', progress=False)['Close']

        return ticker, stock_data, index_data, info
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return None, None, None, None

def calculate_beta(stock_data, index_data, rf):
    """
    Calculate beta using OLS regression.

    Args:
        stock_data: Stock price data
        index_data: Index price data
        rf (float): Risk-free rate

    Returns:
        tuple: (beta, results, stock_returns, index_returns)
    """
    # Calculate monthly returns
    stock_returns = stock_data.pct_change().dropna() - rf
    index_returns = index_data.pct_change().dropna() - rf

    # Run OLS regression
    X = sm.add_constant(index_returns)
    model = sm.OLS(stock_returns, X)
    results = model.fit()

    # Get beta (coefficient on index returns)
    beta = results.params.iloc[1]

    return beta, results, stock_returns, index_returns

# Title
st.title("📈 WACC Calculator")
st.markdown("Calculate the Weighted Average Cost of Capital for any publicly traded company")

# Sidebar for inputs
st.sidebar.header("Input Parameters")

ticker_symbol = st.sidebar.text_input("Ticker Symbol", value="MSFT").upper()
rf = st.sidebar.number_input("Risk-Free Rate (%)", min_value=0.0, max_value=20.0, value=4.5, step=0.1) / 100
firm_rating = st.sidebar.text_input("Firm Credit Rating", value="Aaa/AAA")
emrp = st.sidebar.number_input("Equity Market Risk Premium (%)", min_value=0.0, max_value=20.0, value=5.0, step=0.1) / 100
marg_tax_rate = st.sidebar.number_input("Marginal Tax Rate (%)", min_value=0.0, max_value=100.0, value=25.0, step=1.0) / 100
index_symbol = st.sidebar.text_input("Market Index Symbol", value="^GSPC")
index_name = st.sidebar.text_input("Market Index Name", value="S&P 500")

scale_option = st.sidebar.selectbox("Display Scale", ["Millions", "Billions"])
scale_factor = 1000000 if scale_option == "Millions" else 1000000000
scale_name = "M" if scale_option == "Millions" else "B"

calculate_button = st.sidebar.button("Calculate WACC", type="primary")

if calculate_button:
    with st.spinner(f"Fetching data for {ticker_symbol}..."):
        ticker, stock_data, index_data, info = get_stock_data(ticker_symbol, index_symbol)

    if ticker is not None and info is not None:
        try:
            # Section 1: Debt and Equity Weights
            st.header("1️⃣ Debt and Equity Weights")

            col1, col2 = st.columns(2)

            market_cap = info.get('marketCap', 0) / scale_factor
            total_debt = info.get('totalDebt', 0) / scale_factor
            company_name = info.get('longName', ticker_symbol)

            with col1:
                st.metric("Company", company_name)
                st.metric(f"Market Capitalization (${scale_name})", f"{market_cap:,.2f}")
                st.metric(f"Total Debt (${scale_name})", f"{total_debt:,.2f}")

            # Calculate weights
            w_E = market_cap / (market_cap + total_debt)
            w_D = total_debt / (market_cap + total_debt)

            with col2:
                st.metric("Equity Weight (wE)", f"{w_E:.2%}")
                st.metric("Debt Weight (wD)", f"{w_D:.2%}")

                # Pie chart
                fig, ax = plt.subplots(figsize=(6, 4))
                ax.pie([w_E, w_D], labels=['Equity', 'Debt'], autopct='%1.1f%%',
                       colors=['#2E86AB', '#A23B72'], startangle=90)
                ax.set_title('Capital Structure')
                st.pyplot(fig)

            st.divider()

            # Section 2: Cost of Equity
            st.header("2️⃣ Cost of Equity")

            with st.spinner("Calculating beta..."):
                beta, results, stock_returns, index_returns = calculate_beta(stock_data, index_data, rf)

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Beta Calculation")
                st.metric("Beta", f"{beta:.4f}")

                # Get confidence interval for beta
                beta_ci = results.conf_int(alpha=0.05)
                beta_lower_ci = beta_ci.iloc[1, 0]
                beta_upper_ci = beta_ci.iloc[1, 1]

                st.write(f"**95% Confidence Interval:** [{beta_lower_ci:.4f}, {beta_upper_ci:.4f}]")
                st.write(f"**R-squared:** {results.rsquared:.4f}")

                # Calculate cost of equity
                cost_of_equity = rf + beta * emrp
                st.metric("Cost of Equity", f"{cost_of_equity:.2%}")

            with col2:
                st.subheader("Regression Analysis")
                # Scatter plot with regression line
                fig, ax = plt.subplots(figsize=(8, 6))
                ax.scatter(index_returns, stock_returns, alpha=0.5)

                # Add regression line
                x_line = np.linspace(index_returns.min(), index_returns.max(), 100)
                y_line = results.params[0] + results.params[1] * x_line
                ax.plot(x_line, y_line, 'r-', linewidth=2, label=f'Beta = {beta:.2f}')

                ax.set_xlabel(f'{index_name} Excess Returns')
                ax.set_ylabel(f'{ticker_symbol} Excess Returns')
                ax.set_title(f'{ticker_symbol} vs {index_name}')
                ax.legend()
                ax.grid(True, alpha=0.3)
                st.pyplot(fig)

            # Display regression summary in expander
            with st.expander("View Full Regression Results"):
                st.text(results.summary())

            st.divider()

            # Section 3: Cost of Debt
            st.header("3️⃣ Cost of Debt")

            col1, col2 = st.columns(2)

            with col1:
                credit_spread = get_credit_spread(firm_rating, credit_spreads)
                st.metric("Credit Rating", firm_rating)
                st.metric("Credit Spread", f"{credit_spread:.2%}")

                cost_of_debt = rf + credit_spread
                st.metric("Cost of Debt (kD)", f"{cost_of_debt:.2%}")

            with col2:
                st.subheader("Credit Spread Reference")
                # Display credit spreads table
                spreads_df = pd.DataFrame(credit_spreads)
                spreads_df['Spread'] = spreads_df['Spread'].apply(lambda x: f"{x:.2f}%")
                st.dataframe(spreads_df[['Rating', 'Spread']], hide_index=True)

            st.divider()

            # Section 4: WACC Results
            st.header("4️⃣ WACC Results")

            # Calculate WACC
            wacc = w_E * cost_of_equity + w_D * cost_of_debt * (1 - marg_tax_rate)

            # Calculate WACC with confidence intervals
            cost_of_equity_lower_ci = rf + beta_lower_ci * emrp
            cost_of_equity_upper_ci = rf + beta_upper_ci * emrp

            wacc_lower_ci = w_E * cost_of_equity_lower_ci + w_D * cost_of_debt * (1 - marg_tax_rate)
            wacc_upper_ci = w_E * cost_of_equity_upper_ci + w_D * cost_of_debt * (1 - marg_tax_rate)

            # Save WACC results to session state for Phase 3 DCF Model
            st.session_state.wacc_results = {
                'wacc_lower': wacc_lower_ci,
                'wacc': wacc,
                'wacc_upper': wacc_upper_ci,
                'ticker': ticker_symbol,
                'timestamp': pd.Timestamp.now()
            }

            # Display main WACC
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("WACC (Lower CI)", f"{wacc_lower_ci:.2%}")
            with col2:
                st.metric("WACC (Estimate)", f"{wacc:.2%}", help="Primary WACC estimate")
            with col3:
                st.metric("WACC (Upper CI)", f"{wacc_upper_ci:.2%}")

            # WACC Summary DataFrame
            wacc_summary = pd.DataFrame({
                'WACC': [wacc_lower_ci * 100, wacc * 100, wacc_upper_ci * 100]
            }, index=['Lower CI (95%)', 'Estimate', 'Upper CI (95%)'])

            st.subheader("WACC Summary")
            st.dataframe(wacc_summary.style.format("{:.2f}%"), use_container_width=True)

            # Notification that WACC was saved
            st.success(f"✅ WACC saved! You can now use these values in the DCF Model (Phase 3)")

            # Visualization
            fig, ax = plt.subplots(figsize=(10, 6))
            bars = ax.bar(['Lower CI', 'Estimate', 'Upper CI'],
                         [wacc_lower_ci * 100, wacc * 100, wacc_upper_ci * 100],
                         color=['#FF6B6B', '#4ECDC4', '#FF6B6B'])

            ax.set_ylabel('WACC (%)')
            ax.set_title(f'WACC Estimates for {ticker_symbol}')
            ax.grid(True, alpha=0.3, axis='y')

            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.2f}%',
                       ha='center', va='bottom')

            st.pyplot(fig)

            # WACC Formula breakdown
            with st.expander("View WACC Calculation Breakdown"):
                st.markdown("### WACC Formula")
                st.latex(r"WACC = w_E \times k_E + w_D \times k_D \times (1-t)")

                st.markdown("### Components:")
                breakdown_df = pd.DataFrame({
                    'Component': ['Equity Weight (wE)', 'Cost of Equity (kE)',
                                 'Debt Weight (wD)', 'Cost of Debt (kD)',
                                 'Tax Rate (t)', 'After-tax Cost of Debt'],
                    'Value': [f"{w_E:.4f}", f"{cost_of_equity:.4f}",
                             f"{w_D:.4f}", f"{cost_of_debt:.4f}",
                             f"{marg_tax_rate:.4f}", f"{cost_of_debt * (1 - marg_tax_rate):.4f}"]
                })
                st.dataframe(breakdown_df, hide_index=True, use_container_width=True)

                st.markdown(f"""
                **Calculation:**
                - Equity portion: {w_E:.4f} × {cost_of_equity:.4f} = {w_E * cost_of_equity:.4f}
                - Debt portion: {w_D:.4f} × {cost_of_debt:.4f} × (1 - {marg_tax_rate:.4f}) = {w_D * cost_of_debt * (1 - marg_tax_rate):.4f}
                - **Total WACC:** {wacc:.4f} or {wacc:.2%}
                """)

        except Exception as e:
            st.error(f"Error in calculations: {str(e)}")
            st.exception(e)
    else:
        st.error("Unable to fetch data. Please check the ticker symbol and try again.")
else:
    st.info("👈 Enter your parameters in the sidebar and click 'Calculate WACC' to begin.")

    # Display instructions
    st.markdown("""
    ### How to Use This Calculator

    1. **Enter Ticker Symbol**: Input the stock ticker (e.g., MSFT, AAPL, GOOGL)
    2. **Set Risk-Free Rate**: Enter the current risk-free rate (typically 10-year Treasury yield)
    3. **Credit Rating**: Enter the firm's credit rating (e.g., Aaa/AAA, A2/A)
    4. **Set Parameters**: Adjust EMRP, tax rate, and market index as needed
    5. **Calculate**: Click the "Calculate WACC" button to see results

    ### What is WACC?

    The Weighted Average Cost of Capital (WACC) represents the average rate a company must pay to finance its assets.
    It's calculated using the formula:

    """)
    st.latex(r"WACC = w_E \times k_E + w_D \times k_D \times (1-t)")

    st.markdown("""
    Where:
    - **wE** = Weight of equity in capital structure
    - **kE** = Cost of equity (calculated using CAPM)
    - **wD** = Weight of debt in capital structure
    - **kD** = Cost of debt (risk-free rate + credit spread)
    - **t** = Marginal tax rate
    """)
