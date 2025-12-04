import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import yfinance as yf

# Page configuration
st.set_page_config(
    page_title="Historical Analysis",
    page_icon="📊",
    layout="wide"
)

def get_financial_data(ticker_symbol):
    """
    Fetch all financial statement data from yfinance.

    Args:
        ticker_symbol (str): Stock ticker symbol

    Returns:
        tuple: (ticker, income_statement, balance_sheet, cash_flows, info)
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info

        # Get financial statements and transpose so dates are rows
        income_statement = ticker.financials.T.sort_index()
        balance_sheet = ticker.balance_sheet.T.sort_index()
        cash_flows = ticker.cashflow.T.sort_index()

        return ticker, income_statement, balance_sheet, cash_flows, info
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return None, None, None, None, None

def calculate_growth_and_margins(income_statement):
    """Calculate growth rates and margins from income statement."""
    df = income_statement.copy()

    # Calculate margins
    df['Gross Margin'] = df['Gross Profit'] / df['Total Revenue']
    df['EBIT Margin'] = df['EBIT'] / df['Total Revenue']
    df['EBITDA Margin'] = df['EBITDA'] / df['Total Revenue']

    # Calculate growth rates
    df['Revenue Growth'] = df['Total Revenue'].pct_change()
    df['EBIT Growth'] = df['EBIT'].pct_change()

    return df

def calculate_nwc(balance_sheet):
    """Calculate Net Working Capital and changes."""
    df = balance_sheet.copy()

    # Adjust Current Assets by subtracting Cash
    df['Adj Current Assets'] = df['Current Assets'] - df['Cash Cash Equivalents And Short Term Investments']

    # Adjust Current Liabilities by subtracting Current Debt
    df['Adj Current Liabilities'] = df['Current Liabilities'] - df['Current Debt And Capital Lease Obligation']

    # Calculate NWC
    df['NWC'] = df['Adj Current Assets'] - df['Adj Current Liabilities']

    # Calculate Change in NWC
    df['Change in NWC'] = df['NWC'].diff()

    return df

def calculate_reinvestment(cash_flows_df, nwc_df, income_df, tax_rate_col):
    """Calculate reinvestment metrics."""
    # Make CapEx positive
    cash_flows_df['Capital Expenditure'] = -cash_flows_df['Capital Expenditure']

    # Merge dataframes
    merged = pd.merge(cash_flows_df[['Capital Expenditure', 'Depreciation And Amortization']],
                      nwc_df[['NWC', 'Change in NWC']],
                      left_index=True, right_index=True, how='left')

    # Calculate Reinvestment
    merged['Reinvestment'] = (merged['Capital Expenditure'] -
                              merged['Depreciation And Amortization'] +
                              merged['Change in NWC'])

    # Calculate NOPAT
    merged['Tax Rate'] = income_df[tax_rate_col]
    merged['NOPAT'] = income_df['EBIT'] * (1 - merged['Tax Rate'])

    # Calculate Reinvestment Rate
    merged['Reinvestment Rate'] = merged['Reinvestment'] / merged['NOPAT']

    return merged

# Title
st.title("📊 Historical Financial Analysis")
st.markdown("Analyze historical performance and key valuation metrics")

# Sidebar for inputs
st.sidebar.header("Input Parameters")

ticker_symbol = st.sidebar.text_input("Ticker Symbol", value="MSFT").upper()

scale_option = st.sidebar.selectbox("Display Scale", ["Millions", "Billions"])
scale_factor = 1000000 if scale_option == "Millions" else 1000000000
scale_name = "M" if scale_option == "Millions" else "B"

analyze_button = st.sidebar.button("Analyze Company", type="primary")

if analyze_button:
    with st.spinner(f"Fetching financial data for {ticker_symbol}..."):
        ticker, income_stmt, balance_sheet, cash_flows, info = get_financial_data(ticker_symbol)

    if ticker is not None and income_stmt is not None:
        try:
            company_name = info.get('longName', ticker_symbol)
            st.success(f"Successfully loaded data for {company_name}")

            # Calculate all metrics
            income_with_metrics = calculate_growth_and_margins(income_stmt)
            balance_with_nwc = calculate_nwc(balance_sheet)

            # Create stats dataframe
            df_stats = income_with_metrics[['Revenue Growth', 'EBIT Growth', 'Gross Margin', 'EBIT Margin', 'EBITDA Margin']].copy()
            df_stats['Tax Rate'] = income_stmt['Tax Rate For Calcs']

            # Calculate reinvestment metrics
            reinvestment_df = calculate_reinvestment(
                cash_flows,
                balance_with_nwc,
                income_stmt,
                'Tax Rate For Calcs'
            )

            # Add Reinvestment Rate to stats
            df_stats['Reinvestment Rate'] = reinvestment_df['Reinvestment Rate']

            # SECTION 1: Revenue and Profitability
            st.header("1️⃣ Revenue and Profitability Metrics")

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Revenue Metrics")
                revenue_data = income_stmt['Total Revenue'] / scale_factor
                st.dataframe(
                    revenue_data.to_frame(f'Revenue (${scale_name})').style.format("{:,.2f}"),
                    use_container_width=True
                )

                # Revenue chart
                fig, ax = plt.subplots(figsize=(8, 5))
                ax.plot(revenue_data.index, revenue_data.values, marker='o', linewidth=2, markersize=8)
                ax.set_xlabel('Year')
                ax.set_ylabel(f'Revenue (${scale_name})')
                ax.set_title(f'{ticker_symbol} Revenue Trend')
                ax.grid(True, alpha=0.3)
                plt.xticks(rotation=45)
                st.pyplot(fig)

            with col2:
                st.subheader("EBIT Metrics")
                ebit_data = income_stmt['EBIT'] / scale_factor
                st.dataframe(
                    ebit_data.to_frame(f'EBIT (${scale_name})').style.format("{:,.2f}"),
                    use_container_width=True
                )

                # EBIT chart
                fig, ax = plt.subplots(figsize=(8, 5))
                ax.plot(ebit_data.index, ebit_data.values, marker='o', linewidth=2, markersize=8, color='#2E86AB')
                ax.set_xlabel('Year')
                ax.set_ylabel(f'EBIT (${scale_name})')
                ax.set_title(f'{ticker_symbol} EBIT Trend')
                ax.grid(True, alpha=0.3)
                plt.xticks(rotation=45)
                st.pyplot(fig)

            st.divider()

            # SECTION 2: Growth Rates
            st.header("2️⃣ Growth Rates")

            growth_df = df_stats[['Revenue Growth', 'EBIT Growth']].copy()
            growth_df_display = growth_df * 100  # Convert to percentage

            st.dataframe(
                growth_df_display.style.format("{:.2f}%"),
                use_container_width=True
            )

            # Growth chart
            fig, ax = plt.subplots(figsize=(10, 6))
            x = np.arange(len(growth_df.index))
            width = 0.35

            bars1 = ax.bar(x - width/2, growth_df['Revenue Growth'] * 100, width, label='Revenue Growth', alpha=0.8)
            bars2 = ax.bar(x + width/2, growth_df['EBIT Growth'] * 100, width, label='EBIT Growth', alpha=0.8)

            ax.set_xlabel('Year')
            ax.set_ylabel('Growth Rate (%)')
            ax.set_title(f'{ticker_symbol} Growth Rates')
            ax.set_xticks(x)
            ax.set_xticklabels([str(date.date()) for date in growth_df.index], rotation=45)
            ax.legend()
            ax.grid(True, alpha=0.3, axis='y')
            ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)

            st.pyplot(fig)

            st.divider()

            # SECTION 3: Margins Analysis
            st.header("3️⃣ Profit Margins")

            margins_df = df_stats[['Gross Margin', 'EBIT Margin', 'EBITDA Margin']].copy()
            margins_df_display = margins_df * 100

            st.dataframe(
                margins_df_display.style.format("{:.2f}%"),
                use_container_width=True
            )

            # Margins chart
            fig, ax = plt.subplots(figsize=(10, 6))

            for column in margins_df.columns:
                ax.plot(margins_df.index, margins_df[column] * 100, marker='o', label=column, linewidth=2)

            ax.set_xlabel('Year')
            ax.set_ylabel('Margin (%)')
            ax.set_title(f'{ticker_symbol} Profit Margins Over Time')
            ax.legend()
            ax.grid(True, alpha=0.3)
            plt.xticks(rotation=45)

            st.pyplot(fig)

            st.divider()

            # SECTION 4: Working Capital
            st.header("4️⃣ Net Working Capital")

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("NWC Values")
                nwc_display = balance_with_nwc[['NWC', 'Change in NWC']] / scale_factor
                st.dataframe(
                    nwc_display.style.format("{:,.2f}"),
                    use_container_width=True
                )

            with col2:
                st.subheader("NWC Trend")
                fig, ax = plt.subplots(figsize=(8, 5))
                nwc_values = balance_with_nwc['NWC'] / scale_factor
                ax.plot(nwc_values.index, nwc_values.values, marker='o', linewidth=2, markersize=8, color='#A23B72')
                ax.set_xlabel('Year')
                ax.set_ylabel(f'NWC (${scale_name})')
                ax.set_title(f'{ticker_symbol} Net Working Capital')
                ax.grid(True, alpha=0.3)
                plt.xticks(rotation=45)
                st.pyplot(fig)

            st.divider()

            # SECTION 5: Reinvestment Analysis
            st.header("5️⃣ Reinvestment Analysis")

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Reinvestment Components")
                reinvest_components = reinvestment_df[['Capital Expenditure', 'Depreciation And Amortization',
                                                       'Change in NWC', 'Reinvestment']] / scale_factor
                st.dataframe(
                    reinvest_components.style.format("{:,.2f}"),
                    use_container_width=True
                )

            with col2:
                st.subheader("NOPAT and Reinvestment Rate")
                nopat_display = reinvestment_df[['NOPAT', 'Reinvestment Rate']].copy()
                nopat_display['NOPAT'] = nopat_display['NOPAT'] / scale_factor

                # Format differently for each column
                styled_df = nopat_display.style.format({
                    'NOPAT': "{:,.2f}",
                    'Reinvestment Rate': "{:.2%}"
                })
                st.dataframe(styled_df, use_container_width=True)

            # Reinvestment chart
            fig, ax = plt.subplots(figsize=(10, 6))

            reinvest_values = reinvestment_df['Reinvestment'] / scale_factor
            nopat_values = reinvestment_df['NOPAT'] / scale_factor

            x = np.arange(len(reinvest_values.index))
            width = 0.35

            bars1 = ax.bar(x - width/2, nopat_values, width, label='NOPAT', alpha=0.8)
            bars2 = ax.bar(x + width/2, reinvest_values, width, label='Reinvestment', alpha=0.8)

            ax.set_xlabel('Year')
            ax.set_ylabel(f'Amount (${scale_name})')
            ax.set_title(f'{ticker_symbol} NOPAT vs Reinvestment')
            ax.set_xticks(x)
            ax.set_xticklabels([str(date.date()) for date in reinvest_values.index], rotation=45)
            ax.legend()
            ax.grid(True, alpha=0.3, axis='y')

            st.pyplot(fig)

            st.divider()

            # SECTION 6: Summary Statistics
            st.header("6️⃣ Complete Historical Summary")

            st.subheader("All Key Metrics")
            st.dataframe(
                df_stats.style.format({
                    'Revenue Growth': "{:.2%}",
                    'EBIT Growth': "{:.2%}",
                    'Gross Margin': "{:.2%}",
                    'EBIT Margin': "{:.2%}",
                    'EBITDA Margin': "{:.2%}",
                    'Tax Rate': "{:.2%}",
                    'Reinvestment Rate': "{:.2%}"
                }),
                use_container_width=True
            )

            # Summary statistics
            with st.expander("View Statistical Summary"):
                st.subheader("Average Metrics (Excluding First Year)")
                avg_stats = df_stats.iloc[1:].mean()  # Skip first year due to NaN growth rates

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Avg Revenue Growth", f"{avg_stats['Revenue Growth']:.2%}")
                    st.metric("Avg EBIT Growth", f"{avg_stats['EBIT Growth']:.2%}")

                with col2:
                    st.metric("Avg Gross Margin", f"{avg_stats['Gross Margin']:.2%}")
                    st.metric("Avg EBIT Margin", f"{avg_stats['EBIT Margin']:.2%}")
                    st.metric("Avg EBITDA Margin", f"{avg_stats['EBITDA Margin']:.2%}")

                with col3:
                    st.metric("Avg Tax Rate", f"{avg_stats['Tax Rate']:.2%}")
                    st.metric("Avg Reinvestment Rate", f"{avg_stats['Reinvestment Rate']:.2%}")

            # Key insights
            st.subheader("📌 Key Insights")

            latest_year = df_stats.index[-1].year
            latest_revenue_growth = df_stats['Revenue Growth'].iloc[-1]
            latest_ebit_margin = df_stats['EBIT Margin'].iloc[-1]
            latest_reinvest_rate = df_stats['Reinvestment Rate'].iloc[-1]

            col1, col2, col3 = st.columns(3)

            with col1:
                st.info(f"""
                **Latest Year ({latest_year})**

                Revenue Growth: {latest_revenue_growth:.2%}

                This represents the most recent year-over-year revenue change.
                """)

            with col2:
                st.info(f"""
                **Operating Efficiency**

                EBIT Margin: {latest_ebit_margin:.2%}

                Shows how much operating profit is generated per dollar of revenue.
                """)

            with col3:
                st.info(f"""
                **Reinvestment Strategy**

                Reinvestment Rate: {latest_reinvest_rate:.2%}

                Percentage of NOPAT reinvested back into the business.
                """)

        except Exception as e:
            st.error(f"Error in analysis: {str(e)}")
            st.exception(e)
    else:
        st.error("Unable to fetch financial data. Please check the ticker symbol and try again.")
else:
    st.info("👈 Enter a ticker symbol in the sidebar and click 'Analyze Company' to begin.")

    # Display instructions
    st.markdown("""
    ### How to Use This Tool

    1. **Enter Ticker Symbol**: Input the stock ticker (e.g., MSFT, AAPL, GOOGL)
    2. **Select Display Scale**: Choose between Millions or Billions
    3. **Click Analyze**: View comprehensive historical financial analysis

    ### What This Analysis Provides

    This tool performs backward-looking analysis to understand a company's historical performance:

    #### Key Metrics Analyzed:

    1. **Growth Rates**
       - Revenue growth over time
       - EBIT (Earnings Before Interest and Tax) growth

    2. **Profit Margins**
       - Gross Margin = Gross Profit / Revenue
       - EBIT Margin = EBIT / Revenue
       - EBITDA Margin = EBITDA / Revenue

    3. **Working Capital**
       - Net Working Capital (NWC) calculation
       - Changes in NWC over time

    4. **Reinvestment Metrics**
       - Capital Expenditures (CapEx)
       - Depreciation & Amortization (D&A)
       - Reinvestment = CapEx - D&A + Change in NWC
       - NOPAT = EBIT × (1 - Tax Rate)
       - Reinvestment Rate = Reinvestment / NOPAT

    ### Why This Matters

    Historical analysis helps understand:
    - Company growth trajectory
    - Operational efficiency trends
    - Capital allocation decisions
    - Foundation for future projections

    These metrics are crucial inputs for DCF valuation models.
    """)
