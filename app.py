import streamlit as st

# Page configuration
st.set_page_config(
    page_title="DCF Analysis Suite",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .big-font {
        font-size:60px !important;
        font-weight: bold;
        text-align: center;
    }
    .medium-font {
        font-size:30px !important;
        text-align: center;
    }
    .card {
        padding: 20px;
        border-radius: 10px;
        background-color: #f0f2f6;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Title
st.markdown('<p class="big-font">📊 DCF Analysis Suite</p>', unsafe_allow_html=True)
st.markdown('<p class="medium-font">Complete Financial Valuation Toolkit</p>', unsafe_allow_html=True)

st.divider()

# Introduction
st.markdown("""
## Welcome to the DCF Analysis Suite

This comprehensive web application provides professional-grade financial analysis tools for
Discounted Cash Flow (DCF) valuation. Built with real-time data from Yahoo Finance, this suite
helps you analyze and value publicly traded companies.
""")

st.divider()

# Phase Cards
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="card">
    <h3>📈 Phase 1: WACC Calculator</h3>
    <p><strong>Status:</strong> ✅ Complete</p>
    <p>Calculate the Weighted Average Cost of Capital for any publicly traded company.</p>
    <br>
    <p><strong>Features:</strong></p>
    <ul>
        <li>Capital structure analysis</li>
        <li>Beta calculation via OLS regression</li>
        <li>Cost of equity (CAPM)</li>
        <li>Cost of debt with credit spreads</li>
        <li>WACC with confidence intervals</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="card">
    <h3>📊 Phase 2: Historical Analysis</h3>
    <p><strong>Status:</strong> ✅ Complete</p>
    <p>Analyze historical financial performance and key valuation metrics.</p>
    <br>
    <p><strong>Features:</strong></p>
    <ul>
        <li>Revenue and EBIT growth rates</li>
        <li>Profit margins analysis</li>
        <li>Working capital metrics</li>
        <li>Reinvestment calculations</li>
        <li>Historical trend visualizations</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="card">
    <h3>💰 Phase 3: DCF Model</h3>
    <p><strong>Status:</strong> ✅ Complete</p>
    <p>Complete DCF valuation with projected cash flows and terminal value.</p>
    <br>
    <p><strong>Features:</strong></p>
    <ul>
        <li>Cash flow projections</li>
        <li>Terminal value calculation</li>
        <li>Enterprise value estimation</li>
        <li>Share price valuation</li>
        <li>Sensitivity analysis</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# Getting Started
st.markdown("""
## 🚀 Getting Started

1. **Select a tool** from the sidebar on the left
2. **Enter a ticker symbol** for the company you want to analyze
3. **Configure parameters** according to your analysis needs
4. **Click Calculate** to see results with interactive visualizations

## 📖 About This Project

This project converts Python DCF analysis notebooks into an interactive web application.
It uses real-time financial data and professional valuation methodologies to provide
institutional-grade analysis accessible through a user-friendly interface.

### Data Sources
- **Stock Data**: Yahoo Finance (via yfinance API)
- **Credit Spreads**: Aswath Damodaran's dataset
- **Market Data**: Real-time market indices

### Technologies
- **Framework**: Streamlit
- **Data Analysis**: pandas, numpy
- **Statistical Analysis**: statsmodels
- **Visualizations**: matplotlib, seaborn

## 📬 Navigation

Use the sidebar menu to navigate between different analysis tools:
- **WACC Calculator** - Calculate cost of capital
- **Historical Analysis** - Review historical performance
- **DCF Model** - Full valuation with share price estimation
""")

st.divider()

# Footer
st.markdown("""
---
### 💡 Tips for Best Results

- Use current market data for the risk-free rate (10-year Treasury yield)
- Verify credit ratings from reputable sources (Moody's, S&P)
- Consider industry-specific factors when interpreting results
- Compare results across peer companies for context

### ⚠️ Disclaimer

This tool is for educational and analytical purposes. Always conduct thorough due diligence
and consult with financial professionals before making investment decisions.
""")
