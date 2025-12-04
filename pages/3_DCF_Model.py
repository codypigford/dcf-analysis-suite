import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf

# Page configuration
st.set_page_config(
    page_title="DCF Model",
    page_icon="💰",
    layout="wide"
)

def get_ltm_data(ticker_symbol):
    """
    Get Last Twelve Months (LTM) data from quarterly financials.

    Args:
        ticker_symbol (str): Stock ticker symbol

    Returns:
        tuple: (ticker, ltm_revenue, most_recent_date, shares_outstanding, info)
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info

        # Get quarterly income statement
        ltm_data = ticker.quarterly_income_stmt.T.sort_index()

        # Keep last 4 quarters
        ltm_data = ltm_data.iloc[-4:]

        # Sum revenue for LTM
        ltm_revenue = ltm_data['Total Revenue'].sum()

        # Get most recent date
        most_recent_date = ltm_data.index[-1]

        # Get shares outstanding
        shares_outstanding = info.get('sharesOutstanding', 0)

        return ticker, ltm_revenue, most_recent_date, shares_outstanding, info
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return None, None, None, None, None

def create_projection_dates(most_recent_date, num_years):
    """Create projection dates based on most recent date."""
    freq_dict = {1:'YE-JAN',2:'YE-FEB',3:'YE-MAR',4:'YE-APR', 5:'YE-MAY',6:'YE-JUN',
                 7:'YE-JUL',8:'YE-AUG', 9:'YE-SEP',10:'YE-OCT',11:'YE-NOV',12:'YE-DEC'}

    f = freq_dict[most_recent_date.month]
    new_dates = pd.date_range(start=most_recent_date, periods=num_years+1, freq=f)

    return new_dates[1:]  # Exclude T=0

def project_financials(ltm_revenue, growth_pattern, ebit_margin_pattern,
                       reinv_rate_pattern, tax_rate, projection_dates):
    """
    Project financial statements.

    Args:
        ltm_revenue: Last twelve months revenue
        growth_pattern: List of revenue growth rates
        ebit_margin_pattern: List of EBIT margins
        reinv_rate_pattern: List of reinvestment rates
        tax_rate: Effective tax rate
        projection_dates: Dates for projections

    Returns:
        DataFrame with projections
    """
    projection = pd.DataFrame(index=projection_dates, data={
        'Revenue Growth': growth_pattern,
        'EBIT Margin': ebit_margin_pattern,
        'Reinv Rate': reinv_rate_pattern
    })

    # Calculate Revenue projections
    projection['Revenue'] = ltm_revenue * (1 + projection['Revenue Growth']).cumprod()

    # Calculate EBIT
    projection['EBIT'] = projection['Revenue'] * projection['EBIT Margin']

    # Calculate NOPAT
    projection['NOPAT'] = projection['EBIT'] * (1 - tax_rate)

    # Calculate FCF
    projection['FCF'] = projection['NOPAT'] * (1 - projection['Reinv Rate'])

    return projection

def discount_cash_flows(projection, wacc):
    """Discount future cash flows to present value."""
    periods = np.arange(1, len(projection) + 1)
    projection['Discounted FCF'] = projection['FCF'] / (1 + wacc) ** periods
    return projection

def calculate_terminal_value(final_fcf, wacc, terminal_growth, num_periods):
    """Calculate terminal value using Gordon Growth Model."""
    terminal_value = final_fcf * (1 + terminal_growth) / (wacc - terminal_growth)
    pv_terminal = terminal_value / (1 + wacc) ** num_periods
    return terminal_value, pv_terminal

def calculate_share_price(pv_fcf_sum, pv_terminal, total_debt, total_cash, shares_outstanding):
    """Calculate implied share price."""
    firm_value = pv_fcf_sum + pv_terminal
    equity_value = firm_value - total_debt + total_cash
    share_price = equity_value / shares_outstanding
    return firm_value, equity_value, share_price

# Title
st.title("💰 DCF Valuation Model")
st.markdown("Complete Discounted Cash Flow valuation with projected cash flows and share price estimation")

# Sidebar for inputs
st.sidebar.header("Company Selection")
ticker_symbol = st.sidebar.text_input("Ticker Symbol", value="MSFT").upper()

st.sidebar.divider()

st.sidebar.header("Projection Settings")
num_years = st.sidebar.slider("Projection Period (Years)", min_value=5, max_value=15, value=10, step=1)

st.sidebar.divider()

st.sidebar.header("Growth Assumptions")

# Simple vs Advanced mode
projection_mode = st.sidebar.radio("Projection Mode", ["Simple", "Advanced"])

if projection_mode == "Simple":
    # Simple mode: single growth rate that declines
    initial_growth = st.sidebar.number_input("Initial Revenue Growth (%)", min_value=0.0, max_value=50.0, value=15.0, step=1.0) / 100
    final_growth = st.sidebar.number_input("Final Year Growth (%)", min_value=0.0, max_value=30.0, value=6.0, step=1.0) / 100

    # Create declining growth pattern
    growth_pattern = np.linspace(initial_growth, final_growth, num_years).tolist()

    ebit_margin_const = st.sidebar.number_input("EBIT Margin (%)", min_value=0.0, max_value=100.0, value=46.0, step=1.0) / 100
    ebit_margin_pattern = [ebit_margin_const] * num_years

    initial_reinv = st.sidebar.number_input("Initial Reinvestment Rate (%)", min_value=0.0, max_value=100.0, value=40.0, step=1.0) / 100
    final_reinv = st.sidebar.number_input("Final Reinvestment Rate (%)", min_value=0.0, max_value=100.0, value=20.0, step=1.0) / 100
    reinv_rate_pattern = np.linspace(initial_reinv, final_reinv, num_years).tolist()

else:
    # Advanced mode: custom patterns
    st.sidebar.info("📝 Enter comma-separated values for each year")

    growth_input = st.sidebar.text_area("Revenue Growth (%) per Year",
                                         value="20,15,15,15,10,10,10,8,8,6"[:num_years*3])
    ebit_input = st.sidebar.text_area("EBIT Margin (%) per Year",
                                       value="46,46,46,46,46,46,46,46,46,46"[:num_years*3])
    reinv_input = st.sidebar.text_area("Reinvestment Rate (%) per Year",
                                        value="40,40,30,20,20,20,20,20,20,20"[:num_years*3])

    try:
        growth_pattern = [float(x.strip())/100 for x in growth_input.split(',')][:num_years]
        ebit_margin_pattern = [float(x.strip())/100 for x in ebit_input.split(',')][:num_years]
        reinv_rate_pattern = [float(x.strip())/100 for x in reinv_input.split(',')][:num_years]

        # Pad with last value if needed
        while len(growth_pattern) < num_years:
            growth_pattern.append(growth_pattern[-1] if growth_pattern else 0.06)
        while len(ebit_margin_pattern) < num_years:
            ebit_margin_pattern.append(ebit_margin_pattern[-1] if ebit_margin_pattern else 0.46)
        while len(reinv_rate_pattern) < num_years:
            reinv_rate_pattern.append(reinv_rate_pattern[-1] if reinv_rate_pattern else 0.20)

    except Exception as e:
        st.sidebar.error("Invalid input format. Using defaults.")
        growth_pattern = [0.15] * num_years
        ebit_margin_pattern = [0.46] * num_years
        reinv_rate_pattern = [0.20] * num_years

st.sidebar.divider()

st.sidebar.header("Tax & Discount Rates")
tax_rate = st.sidebar.number_input("Effective Tax Rate (%)", min_value=0.0, max_value=50.0, value=19.0, step=1.0) / 100
terminal_growth = st.sidebar.number_input("Terminal Growth Rate (%)", min_value=0.0, max_value=10.0, value=3.0, step=0.5) / 100

# WACC input
st.sidebar.subheader("WACC (Cost of Capital)")
wacc_input_mode = st.sidebar.radio("WACC Input", ["Manual", "Use Phase 1 Estimates"])

if wacc_input_mode == "Manual":
    wacc_lower = st.sidebar.number_input("WACC Lower (%)  ", min_value=0.0, max_value=30.0, value=7.96, step=0.1) / 100
    wacc = st.sidebar.number_input("WACC Estimate (%)", min_value=0.0, max_value=30.0, value=9.25, step=0.1) / 100
    wacc_upper = st.sidebar.number_input("WACC Upper (%)  ", min_value=0.0, max_value=30.0, value=10.54, step=0.1) / 100
else:
    st.sidebar.info("📊 Use WACC Calculator (Phase 1) to get these values")
    wacc_lower = st.sidebar.number_input("WACC Lower (%)  ", min_value=0.0, max_value=30.0, value=7.96, step=0.1) / 100
    wacc = st.sidebar.number_input("WACC Estimate (%)", min_value=0.0, max_value=30.0, value=9.25, step=0.1) / 100
    wacc_upper = st.sidebar.number_input("WACC Upper (%)  ", min_value=0.0, max_value=30.0, value=10.54, step=0.1) / 100

st.sidebar.divider()

scale_option = st.sidebar.selectbox("Display Scale", ["Millions", "Billions"])
scale_factor = 1000000 if scale_option == "Millions" else 1000000000
scale_name = "M" if scale_option == "Millions" else "B"

calculate_button = st.sidebar.button("Calculate Valuation", type="primary")

if calculate_button:
    with st.spinner(f"Fetching data for {ticker_symbol}..."):
        ticker, ltm_revenue, most_recent_date, shares_outstanding, info = get_ltm_data(ticker_symbol)

    if ticker is not None and ltm_revenue is not None:
        try:
            company_name = info.get('longName', ticker_symbol)
            total_debt = info.get('totalDebt', 0)
            total_cash = info.get('totalCash', 0)

            st.success(f"Successfully loaded data for {company_name}")

            # SECTION 1: Starting Point
            st.header("1️⃣ Starting Point - LTM Data")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("LTM Revenue", f"${ltm_revenue/scale_factor:,.2f}{scale_name}")
                st.caption(f"Last Twelve Months ending {most_recent_date.date()}")

            with col2:
                st.metric("Shares Outstanding", f"{shares_outstanding/1000000:,.2f}M")
                st.caption("Current shares outstanding")

            with col3:
                st.metric("Net Debt", f"${(total_debt - total_cash)/scale_factor:,.2f}{scale_name}")
                st.caption(f"Debt: ${total_debt/scale_factor:,.2f}{scale_name} | Cash: ${total_cash/scale_factor:,.2f}{scale_name}")

            st.divider()

            # SECTION 2: Assumptions
            st.header("2️⃣ Projection Assumptions")

            # Create projection dates
            projection_dates = create_projection_dates(most_recent_date, num_years)

            # Show assumptions table
            assumptions_df = pd.DataFrame({
                'Year': range(1, num_years + 1),
                'Revenue Growth': [f"{g:.1%}" for g in growth_pattern],
                'EBIT Margin': [f"{m:.1%}" for m in ebit_margin_pattern],
                'Reinvestment Rate': [f"{r:.1%}" for r in reinv_rate_pattern]
            })

            st.dataframe(assumptions_df, use_container_width=True, hide_index=True)

            # Visualize assumptions
            fig, axes = plt.subplots(1, 3, figsize=(15, 4))

            years = range(1, num_years + 1)

            axes[0].plot(years, [g*100 for g in growth_pattern], marker='o', color='#2E86AB', linewidth=2)
            axes[0].set_title('Revenue Growth Rate')
            axes[0].set_xlabel('Year')
            axes[0].set_ylabel('Growth Rate (%)')
            axes[0].grid(True, alpha=0.3)

            axes[1].plot(years, [m*100 for m in ebit_margin_pattern], marker='o', color='#A23B72', linewidth=2)
            axes[1].set_title('EBIT Margin')
            axes[1].set_xlabel('Year')
            axes[1].set_ylabel('Margin (%)')
            axes[1].grid(True, alpha=0.3)

            axes[2].plot(years, [r*100 for r in reinv_rate_pattern], marker='o', color='#F77F00', linewidth=2)
            axes[2].set_title('Reinvestment Rate')
            axes[2].set_xlabel('Year')
            axes[2].set_ylabel('Rate (%)')
            axes[2].grid(True, alpha=0.3)

            plt.tight_layout()
            st.pyplot(fig)

            st.divider()

            # SECTION 3: Projections
            st.header("3️⃣ Financial Projections")

            # Project financials
            projection = project_financials(
                ltm_revenue, growth_pattern, ebit_margin_pattern,
                reinv_rate_pattern, tax_rate, projection_dates
            )

            # Display projections
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Projection Ratios")
                ratio_df = projection[['Revenue Growth', 'EBIT Margin', 'Reinv Rate']].copy()
                ratio_df_display = ratio_df * 100
                st.dataframe(
                    ratio_df_display.style.format("{:.2f}%"),
                    use_container_width=True
                )

            with col2:
                st.subheader("Projected Values")
                values_df = projection[['Revenue', 'EBIT', 'NOPAT', 'FCF']].copy() / scale_factor
                st.dataframe(
                    values_df.style.format("${:,.2f}"),
                    use_container_width=True
                )

            # Visualize projections
            fig, ax = plt.subplots(figsize=(12, 6))

            years_idx = range(len(projection))
            ax.plot(years_idx, projection['Revenue']/scale_factor, marker='o', label='Revenue', linewidth=2)
            ax.plot(years_idx, projection['EBIT']/scale_factor, marker='s', label='EBIT', linewidth=2)
            ax.plot(years_idx, projection['NOPAT']/scale_factor, marker='^', label='NOPAT', linewidth=2)
            ax.plot(years_idx, projection['FCF']/scale_factor, marker='d', label='FCF', linewidth=2)

            ax.set_xlabel('Year')
            ax.set_ylabel(f'Amount (${scale_name})')
            ax.set_title(f'{ticker_symbol} Financial Projections')
            ax.legend()
            ax.grid(True, alpha=0.3)
            ax.set_xticks(years_idx)
            ax.set_xticklabels([f"Y{i+1}" for i in years_idx])

            st.pyplot(fig)

            st.divider()

            # SECTION 4: Discounted Cash Flows
            st.header("4️⃣ Discounted Cash Flows")

            st.info(f"📊 Using WACC of {wacc:.2%} to discount future cash flows")

            # Discount cash flows
            projection = discount_cash_flows(projection, wacc)

            # Display DCF
            dcf_df = projection[['FCF', 'Discounted FCF']].copy() / scale_factor
            st.dataframe(
                dcf_df.style.format("${:,.2f}"),
                use_container_width=True
            )

            # Calculate totals
            total_pv_fcf = projection['Discounted FCF'].sum()

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total FCF (Undiscounted)", f"${projection['FCF'].sum()/scale_factor:,.2f}{scale_name}")
            with col2:
                st.metric("Total PV of FCF", f"${total_pv_fcf/scale_factor:,.2f}{scale_name}")

            # Visualize discounting effect
            fig, ax = plt.subplots(figsize=(12, 6))

            x = np.arange(len(projection))
            width = 0.35

            bars1 = ax.bar(x - width/2, projection['FCF']/scale_factor, width, label='FCF', alpha=0.8)
            bars2 = ax.bar(x + width/2, projection['Discounted FCF']/scale_factor, width, label='Discounted FCF', alpha=0.8)

            ax.set_xlabel('Year')
            ax.set_ylabel(f'Amount (${scale_name})')
            ax.set_title('Free Cash Flow vs Discounted FCF')
            ax.set_xticks(x)
            ax.set_xticklabels([f"Y{i+1}" for i in x])
            ax.legend()
            ax.grid(True, alpha=0.3, axis='y')

            st.pyplot(fig)

            st.divider()

            # SECTION 5: Terminal Value
            st.header("5️⃣ Terminal Value")

            final_fcf = projection['FCF'].iloc[-1]
            terminal_value, pv_terminal = calculate_terminal_value(
                final_fcf, wacc, terminal_growth, len(projection)
            )

            st.markdown(f"""
            **Terminal Value Calculation (Gordon Growth Model):**

            Using final year FCF of **${final_fcf/scale_factor:,.2f}{scale_name}** and terminal growth rate of **{terminal_growth:.1%}**
            """)

            st.latex(r"TV = \frac{FCF_{final} \times (1+g)}{WACC - g}")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Terminal Value", f"${terminal_value/scale_factor:,.2f}{scale_name}")

            with col2:
                st.metric("PV of Terminal Value", f"${pv_terminal/scale_factor:,.2f}{scale_name}")

            with col3:
                pct_of_value = pv_terminal / (total_pv_fcf + pv_terminal) * 100
                st.metric("% of Total Value", f"{pct_of_value:.1f}%")

            st.divider()

            # SECTION 6: Valuation
            st.header("6️⃣ Firm Valuation & Share Price")

            firm_value, equity_value, share_price = calculate_share_price(
                total_pv_fcf, pv_terminal, total_debt, total_cash, shares_outstanding
            )

            # Display valuation waterfall
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("PV of FCF", f"${total_pv_fcf/scale_factor:,.2f}{scale_name}")

            with col2:
                st.metric("PV of Terminal Value", f"${pv_terminal/scale_factor:,.2f}{scale_name}")

            with col3:
                st.metric("Enterprise Value", f"${firm_value/scale_factor:,.2f}{scale_name}")

            with col4:
                st.metric("Equity Value", f"${equity_value/scale_factor:,.2f}{scale_name}")

            # Share price with current comparison
            current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))

            st.subheader("💎 Implied Share Price")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("DCF Implied Price", f"${share_price:,.2f}")

            with col2:
                st.metric("Current Market Price", f"${current_price:,.2f}")

            with col3:
                if current_price > 0:
                    upside = (share_price - current_price) / current_price * 100
                    st.metric("Implied Upside/Downside", f"{upside:+.1f}%")
                else:
                    st.metric("Implied Upside/Downside", "N/A")

            # Valuation waterfall chart
            fig, ax = plt.subplots(figsize=(10, 6))

            waterfall_items = ['PV of FCF', 'PV of TV', 'Enterprise Value', '- Net Debt', 'Equity Value']
            waterfall_values = [
                total_pv_fcf/scale_factor,
                pv_terminal/scale_factor,
                firm_value/scale_factor,
                -(total_debt - total_cash)/scale_factor,
                equity_value/scale_factor
            ]

            colors = ['#2E86AB', '#A23B72', '#4ECDC4', '#FF6B6B', '#06D6A0']
            bars = ax.bar(waterfall_items, waterfall_values, color=colors, alpha=0.7)

            ax.set_ylabel(f'Value (${scale_name})')
            ax.set_title(f'{ticker_symbol} Valuation Waterfall')
            ax.grid(True, alpha=0.3, axis='y')
            plt.xticks(rotation=45, ha='right')

            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'${height:,.0f}',
                       ha='center', va='bottom' if height > 0 else 'top')

            plt.tight_layout()
            st.pyplot(fig)

            st.divider()

            # SECTION 7: Sensitivity Analysis
            st.header("7️⃣ Sensitivity Analysis")

            st.info("📊 Calculating share price range using WACC confidence intervals")

            # Calculate with three WACC values
            wacc_values = [wacc_lower, wacc, wacc_upper]
            wacc_labels = ['Lower CI', 'Estimate', 'Upper CI']
            share_prices = []

            for current_wacc in wacc_values:
                # Discount FCF
                current_projection = projection.copy()
                periods = np.arange(1, len(current_projection) + 1)
                current_projection['Discounted FCF'] = current_projection['FCF'] / (1 + current_wacc) ** periods

                # Calculate TV
                _, current_pv_terminal = calculate_terminal_value(
                    final_fcf, current_wacc, terminal_growth, len(current_projection)
                )

                # Calculate share price
                _, _, current_share_price = calculate_share_price(
                    current_projection['Discounted FCF'].sum(),
                    current_pv_terminal,
                    total_debt,
                    total_cash,
                    shares_outstanding
                )

                share_prices.append(current_share_price)

            # Display price range
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(f"Price @ WACC {wacc_lower:.2%}", f"${share_prices[0]:,.2f}")
                st.caption("Best case scenario")

            with col2:
                st.metric(f"Price @ WACC {wacc:.2%}", f"${share_prices[1]:,.2f}")
                st.caption("Base case estimate")

            with col3:
                st.metric(f"Price @ WACC {wacc_upper:.2%}", f"${share_prices[2]:,.2f}")
                st.caption("Conservative scenario")

            # Price range visualization with historical
            st.subheader("📈 DCF Valuation vs Historical Price")

            with st.spinner("Fetching historical price data..."):
                historical_data = yf.download(ticker_symbol, period="1y", progress=False)

            if not historical_data.empty:
                fig, ax = plt.subplots(figsize=(14, 7))

                # Plot historical price
                ax.plot(historical_data.index, historical_data['Close'],
                       label=f'{ticker_symbol} Historical Price', color='blue', linewidth=2)

                # Plot DCF estimates
                ax.axhline(share_prices[1], color='green', linestyle='--', linewidth=2,
                          label=f'DCF Estimate (${share_prices[1]:,.2f})')
                ax.axhline(share_prices[0], color='lightgreen', linestyle=':', linewidth=1.5,
                          label=f'Optimistic (${share_prices[0]:,.2f})')
                ax.axhline(share_prices[2], color='orange', linestyle=':', linewidth=1.5,
                          label=f'Conservative (${share_prices[2]:,.2f})')

                # Shade confidence interval
                ax.fill_between(historical_data.index, share_prices[2], share_prices[0],
                               color='gray', alpha=0.2, label='DCF Range')

                ax.set_xlabel('Date')
                ax.set_ylabel('Share Price ($)')
                ax.set_title(f'{ticker_symbol} DCF Valuation vs Historical Price (1 Year)')
                ax.legend(loc='best')
                ax.grid(True, alpha=0.3)

                plt.tight_layout()
                st.pyplot(fig)

            # Summary table
            st.subheader("📊 Valuation Summary")

            summary_df = pd.DataFrame({
                'Metric': [
                    'LTM Revenue',
                    'Projection Period',
                    'Terminal Growth Rate',
                    'WACC (Base)',
                    'Enterprise Value',
                    'Equity Value',
                    'Shares Outstanding',
                    'DCF Price (Low)',
                    'DCF Price (Base)',
                    'DCF Price (High)',
                    'Current Market Price',
                    'Implied Upside/Downside'
                ],
                'Value': [
                    f"${ltm_revenue/scale_factor:,.2f}{scale_name}",
                    f"{num_years} years",
                    f"{terminal_growth:.1%}",
                    f"{wacc:.2%}",
                    f"${firm_value/scale_factor:,.2f}{scale_name}",
                    f"${equity_value/scale_factor:,.2f}{scale_name}",
                    f"{shares_outstanding/1000000:,.2f}M",
                    f"${share_prices[2]:,.2f}",
                    f"${share_prices[1]:,.2f}",
                    f"${share_prices[0]:,.2f}",
                    f"${current_price:,.2f}",
                    f"{upside:+.1f}%" if current_price > 0 else "N/A"
                ]
            })

            st.dataframe(summary_df, use_container_width=True, hide_index=True)

            # Key insights
            with st.expander("📌 View Key Insights"):
                st.markdown(f"""
                ### Valuation Insights for {company_name}

                **Business Growth:**
                - Starting from LTM revenue of ${ltm_revenue/scale_factor:,.2f}{scale_name}
                - Projected to grow to ${projection['Revenue'].iloc[-1]/scale_factor:,.2f}{scale_name} in Year {num_years}
                - Average revenue growth: {np.mean(growth_pattern):.1%}

                **Profitability:**
                - Average EBIT margin: {np.mean(ebit_margin_pattern):.1%}
                - Average reinvestment rate: {np.mean(reinv_rate_pattern):.1%}
                - Tax rate: {tax_rate:.1%}

                **Value Breakdown:**
                - {total_pv_fcf/(total_pv_fcf+pv_terminal)*100:.1f}% from projected cash flows
                - {pv_terminal/(total_pv_fcf+pv_terminal)*100:.1f}% from terminal value

                **Investment Thesis:**
                - DCF base case suggests {'undervaluation' if upside > 0 else 'overvaluation'} of {abs(upside):.1f}%
                - Price range: ${share_prices[2]:,.2f} to ${share_prices[0]:,.2f}
                - Current price: ${current_price:,.2f}
                """)

        except Exception as e:
            st.error(f"Error in calculations: {str(e)}")
            st.exception(e)
    else:
        st.error("Unable to fetch data. Please check the ticker symbol and try again.")

else:
    st.info("👈 Configure your DCF model parameters in the sidebar and click 'Calculate Valuation' to begin.")

    # Instructions
    st.markdown("""
    ### 🎯 How to Use the DCF Model

    1. **Enter Ticker Symbol**: Input the company you want to value
    2. **Set Projection Period**: Choose how many years to project (5-15 years)
    3. **Choose Projection Mode**:
       - **Simple**: Enter initial and final growth rates (linear interpolation)
       - **Advanced**: Specify exact values for each year
    4. **Configure Assumptions**:
       - Revenue growth rates
       - EBIT margins
       - Reinvestment rates
       - Tax rate and terminal growth
    5. **Set WACC**: Enter manually or use values from Phase 1
    6. **Calculate**: See complete valuation with sensitivity analysis

    ### 📐 DCF Methodology

    This model follows the industry-standard DCF approach:

    **Step 1: Project Cash Flows**
    """)

    st.latex(r"Revenue_t = Revenue_{t-1} \times (1 + g_t)")
    st.latex(r"EBIT_t = Revenue_t \times EBIT\ Margin_t")
    st.latex(r"NOPAT_t = EBIT_t \times (1 - Tax\ Rate)")
    st.latex(r"FCF_t = NOPAT_t \times (1 - Reinvestment\ Rate_t)")

    st.markdown("**Step 2: Discount Cash Flows**")
    st.latex(r"PV(FCF_t) = \frac{FCF_t}{(1 + WACC)^t}")

    st.markdown("**Step 3: Calculate Terminal Value**")
    st.latex(r"TV = \frac{FCF_{final} \times (1+g_{terminal})}{WACC - g_{terminal}}")

    st.markdown("**Step 4: Calculate Share Price**")
    st.latex(r"Enterprise\ Value = \sum PV(FCF) + PV(TV)")
    st.latex(r"Equity\ Value = EV - Net\ Debt")
    st.latex(r"Share\ Price = \frac{Equity\ Value}{Shares\ Outstanding}")

    st.markdown("""
    ### 💡 Best Practices

    - **Growth Rates**: Start with recent historical growth, taper to industry average
    - **Margins**: Use historical averages or target margins based on business model
    - **Reinvestment**: Higher growth requires higher reinvestment
    - **Terminal Growth**: Typically 2-4%, not exceeding GDP growth
    - **WACC**: Use Phase 1 calculator for accurate cost of capital

    ### ⚠️ Important Considerations

    - DCF is sensitive to assumptions - always run sensitivity analysis
    - Terminal value often represents 60-80% of total value
    - Compare DCF results with peer multiples and market comps
    - Update assumptions as new information becomes available
    """)
