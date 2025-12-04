# DCF Analysis Suite - Multi-Page Streamlit Web Application

## Project Overview

This project converts Python DCF (Discounted Cash Flow) analysis notebooks into an interactive, multi-page Streamlit web application. The implementation includes a home page for navigation and separate pages for each analysis phase.

## Source Files

The project is based on three Python notebook files:

1. **dcf1_wacc_pigford_cody.py** - WACC calculation (Weighted Average Cost of Capital)
2. **dcf2_historical_analysis_pigford_cody.py** - Historical financial analysis
3. **dcf3_dcf_model_pigford_cody.py** - Complete DCF valuation model

## Implementation Status

- ✅ **Phase 1**: WACC Calculator - Complete
- ✅ **Phase 2**: Historical Analysis - Complete
- ✅ **Phase 3**: DCF Model - Complete
- 📋 **Phase 4**: Integrated Dashboard - Future Enhancement

### Project Structure

```
website/
├── app.py                                      # Home page with navigation
├── pages/
│   ├── 1_WACC_Calculator.py                   # Phase 1: WACC Calculator
│   ├── 2_Historical_Analysis.py               # Phase 2: Historical Analysis
│   └── 3_DCF_Model.py                         # Phase 3: Placeholder
├── requirements.txt                            # Python dependencies
├── claude.md                                   # This documentation file
├── dcf1_wacc_pigford_cody.py                  # Original WACC notebook
├── dcf2_historical_analysis_pigford_cody.py   # Original historical analysis
└── dcf3_dcf_model_pigford_cody.py             # Original DCF model
```

### Navigation

The application uses Streamlit's multi-page architecture:
- **Home Page** (app.py): Landing page with project overview and phase descriptions
- **Page 1**: WACC Calculator - Cost of capital analysis
- **Page 2**: Historical Analysis - Financial performance metrics
- **Page 3**: DCF Model - Complete valuation with share price estimation

Users navigate between pages using the sidebar menu that Streamlit automatically generates.

## Phase 1: WACC Calculator

Located in `pages/1_WACC_Calculator.py`

### Features Implemented

#### 1. User Input Parameters (Sidebar)
- **Ticker Symbol**: Stock ticker (default: MSFT)
- **Risk-Free Rate**: User-inputted percentage (default: 4.5%)
- **Firm Credit Rating**: Credit rating string (default: Aaa/AAA)
- **Equity Market Risk Premium (EMRP)**: Percentage (default: 5.0%)
- **Marginal Tax Rate**: Percentage (default: 25.0%)
- **Market Index Symbol**: For beta calculation (default: ^GSPC)
- **Market Index Name**: Display name (default: S&P 500)
- **Display Scale**: Millions or Billions

#### 2. Main Display Sections

**Section 1: Debt & Equity Weights**
- Displays market capitalization and total debt
- Calculates and shows equity weight (wE) and debt weight (wD)
- Includes pie chart visualization of capital structure

**Section 2: Cost of Equity**
- Calculates beta using OLS regression (5 years of monthly data)
- Shows beta with 95% confidence interval
- Displays regression R-squared
- Calculates cost of equity using CAPM: kE = rf + β × EMRP
- Provides scatter plot with regression line
- Expandable section with full regression results

**Section 3: Cost of Debt**
- Looks up credit spread based on firm's credit rating
- Uses Damodaran credit spread table (updated data)
- Calculates cost of debt: kD = rf + credit spread
- Displays reference table of all credit spreads

**Section 4: WACC Results**
- Displays three WACC estimates: Lower CI, Estimate, Upper CI
- Shows formatted summary table
- Bar chart visualization of WACC estimates
- Expandable calculation breakdown showing the formula:
  - WACC = wE × kE + wD × kD × (1-t)

#### 3. Key Technical Features

- **Data Fetching**: Uses yfinance API to fetch real-time stock data
- **Beta Calculation**: OLS regression using statsmodels
- **Credit Spread Lookup**: Function-based lookup from Damodaran table
- **Number Formatting**: Proper formatting for currency and percentages
- **Error Handling**: Try-except blocks for data fetching
- **Visualizations**: Matplotlib charts for capital structure and WACC

### Credit Spreads Table

The application uses an updated credit spreads table with the following ratings:
- D2/D: 19.00%
- C2/C: 15.50%
- Ca2/CC: 10.10%
- Caa/CCC: 7.28%
- B3/B-: 4.42%
- B2/B: 3.00%
- B1/B+: 2.61%
- Ba2/BB: 1.83%
- Ba1/BB+: 1.55%
- Baa2/BBB: 1.20%
- A3/A-: 0.95%
- A2/A: 0.85%
- A1/A+: 0.77%
- Aa2/AA: 0.60%
- Aaa/AAA: 0.45%

## Dependencies

```
streamlit>=1.28.0
yfinance>=0.2.28
pandas>=2.0.0
numpy>=1.24.0
matplotlib>=3.7.0
seaborn>=0.12.0
statsmodels>=0.14.0
```

## Installation & Setup

### 1. Install Dependencies

```bash
cd "C:\Users\codye\OneDrive\MBA\Y2 MOD2\FDA\website"
python -m pip install -r requirements.txt
```

### 2. Run the Application

```bash
python -m streamlit run app.py
```

Or in headless mode:

```bash
python -m streamlit run app.py --server.headless=true
```

### 3. Access the Application

Once running, the app will be available at:
- **Local URL**: http://localhost:8501
- **Network URL**: http://[your-ip]:8501

## Key Modifications from Original Code

### 1. Removed FRED API
- Original code used FRED API for risk-free rate
- Modified to accept user input for risk-free rate
- Removed all Google Colab specific code

### 2. Removed Caching Issues
- Initially used `@st.cache_data` decorator
- Removed caching from `get_stock_data()` function
- Reason: yfinance Ticker objects are not pickle-serializable

### 3. Added Interactive Features
- Sidebar for all user inputs
- Real-time calculations on button click
- Interactive visualizations
- Expandable sections for detailed information

### 4. Enhanced Visualizations
- Pie chart for capital structure
- Scatter plot with regression line for beta
- Bar chart for WACC confidence intervals
- Formatted tables for results

## Troubleshooting

### Common Issues

**1. Installation Warnings**
```
WARNING: The script streamlit.exe is installed in '...' which is not on PATH.
```
- These are harmless warnings
- The application will work correctly
- They indicate scripts are installed in a user directory not on system PATH

**2. Caching Error**
```
UnserializableReturnValueError: Cannot serialize the return value
```
- This was fixed by removing `@st.cache_data` from `get_stock_data()`
- The error occurred because yfinance Ticker objects can't be pickled

**3. Python Not Found**
- Use `python -m streamlit run app.py` instead of just `streamlit run app.py`
- This ensures the correct Python interpreter is used

## Usage Instructions

1. **Launch the Application**: Run the streamlit command
2. **Enter Parameters**: Use the sidebar to input:
   - Ticker symbol (e.g., MSFT, AAPL, GOOGL)
   - Risk-free rate (current 10-year Treasury yield)
   - Credit rating
   - Other parameters (or use defaults)
3. **Calculate WACC**: Click the "Calculate WACC" button
4. **Review Results**:
   - Check debt/equity weights
   - Review beta calculation and cost of equity
   - Verify cost of debt and credit spread
   - See final WACC with confidence intervals

## WACC Formula

The application calculates WACC using the standard formula:

**WACC = wE × kE + wD × kD × (1-t)**

Where:
- **wE** = Equity weight = Market Cap / (Market Cap + Total Debt)
- **kE** = Cost of equity (CAPM) = rf + β × EMRP
- **wD** = Debt weight = Total Debt / (Market Cap + Total Debt)
- **kD** = Cost of debt = rf + Credit Spread
- **t** = Marginal tax rate

## Phase 2: Historical Analysis

Located in `pages/2_Historical_Analysis.py`

### Features Implemented

#### 1. User Input Parameters (Sidebar)
- **Ticker Symbol**: Stock ticker
- **Display Scale**: Millions or Billions

#### 2. Main Analysis Sections

**Section 1: Revenue and Profitability**
- Historical revenue data with trends
- Historical EBIT data with trends
- Line charts showing evolution over time

**Section 2: Growth Rates**
- Revenue growth year-over-year
- EBIT growth year-over-year
- Bar chart visualization comparing growth rates

**Section 3: Profit Margins**
- Gross Margin = Gross Profit / Revenue
- EBIT Margin = EBIT / Revenue
- EBITDA Margin = EBITDA / Revenue
- Multi-line chart showing margin trends

**Section 4: Net Working Capital**
- NWC calculation: (Current Assets - Cash) - (Current Liabilities - Current Debt)
- Change in NWC period over period
- Trend visualization

**Section 5: Reinvestment Analysis**
- Capital Expenditures (CapEx)
- Depreciation & Amortization (D&A)
- Reinvestment = CapEx - D&A + Change in NWC
- NOPAT = EBIT × (1 - Tax Rate)
- Reinvestment Rate = Reinvestment / NOPAT
- Bar chart comparing NOPAT vs Reinvestment

**Section 6: Complete Summary**
- All key metrics in single table
- Statistical summary with averages
- Key insights cards with latest year metrics

#### 3. Key Technical Features

- **Data Fetching**: yfinance API for all three financial statements
- **Calculations**: Automated computation of all derived metrics
- **Visualizations**: Multiple chart types (line, bar, trends)
- **Formatting**: Dynamic scale adjustment (millions/billions)
- **Error Handling**: Try-except blocks with user-friendly messages

## Phase 3: DCF Valuation Model

Located in `pages/3_DCF_Model.py`

### Features Implemented

#### 1. User Input Parameters (Sidebar)
- **Company Selection**: Ticker symbol
- **Projection Settings**: 5-15 year projection period
- **Projection Mode**: Simple (linear decline) or Advanced (custom per year)
- **Growth Assumptions**:
  - Revenue growth rates (per year)
  - EBIT margins (per year)
  - Reinvestment rates (per year)
- **Tax & Discount Rates**:
  - Effective tax rate
  - Terminal growth rate
  - WACC (manual input or from Phase 1)
- **Display Scale**: Millions or Billions

#### 2. Main Analysis Sections

**Section 1: Starting Point - LTM Data**
- Last Twelve Months (LTM) revenue from quarterly data
- Shares outstanding
- Net debt (Total Debt - Cash)

**Section 2: Projection Assumptions**
- Assumptions table for all years
- Visual charts for growth rates, margins, and reinvestment rates
- Simple mode: Linear interpolation between initial and final values
- Advanced mode: Custom values for each projection year

**Section 3: Financial Projections**
- Projected Revenue, EBIT, NOPAT, and FCF
- Formulas:
  - Revenue = Prior Revenue × (1 + Growth Rate)
  - EBIT = Revenue × EBIT Margin
  - NOPAT = EBIT × (1 - Tax Rate)
  - FCF = NOPAT × (1 - Reinvestment Rate)
- Multi-line chart showing all projected metrics

**Section 4: Discounted Cash Flows**
- Present value calculation using WACC
- Side-by-side comparison of FCF vs Discounted FCF
- Total PV of projected cash flows
- Bar chart visualization of discounting effect

**Section 5: Terminal Value**
- Gordon Growth Model calculation
- Terminal Value and PV of Terminal Value
- Percentage contribution to total enterprise value
- Formula: TV = FCF_final × (1+g) / (WACC - g)

**Section 6: Firm Valuation & Share Price**
- Enterprise Value = PV(FCF) + PV(Terminal Value)
- Equity Value = Enterprise Value - Net Debt
- Share Price = Equity Value / Shares Outstanding
- Valuation waterfall chart
- Comparison with current market price
- Implied upside/downside percentage

**Section 7: Sensitivity Analysis**
- Three WACC scenarios (Lower CI, Estimate, Upper CI)
- Share price range calculation
- Historical price chart (1 year) with DCF estimates overlaid
- Shaded confidence interval region
- Complete valuation summary table
- Key insights expandable section

#### 3. Key Technical Features

- **LTM Data Fetching**: Quarterly financial aggregation
- **Projection Dates**: Automatic date generation matching fiscal year-end
- **Dual Input Modes**: Simple and Advanced for different user needs
- **Real-time Calculations**: All metrics calculated dynamically
- **Multiple Visualizations**:
  - Assumption charts (3 subplots)
  - Projection trends (multi-line)
  - Discounting comparison (grouped bars)
  - Valuation waterfall (bar chart)
  - Historical comparison with DCF overlay
- **Comprehensive Summary**: Complete valuation metrics table
- **Investment Insights**: Automated analysis of results

### Calculations Implemented

**Cash Flow Projections:**
- Revenue_t = Revenue_{t-1} × (1 + g_t)
- EBIT_t = Revenue_t × Margin_t
- NOPAT_t = EBIT_t × (1 - Tax)
- FCF_t = NOPAT_t × (1 - ReinvRate_t)

**Discounting:**
- PV(FCF_t) = FCF_t / (1 + WACC)^t

**Terminal Value:**
- TV = FCF_final × (1+g) / (WACC - g)

**Share Price:**
- Price = (EV - Net Debt) / Shares

## Future Enhancements

### Phase 4: Integrated Dashboard (Optional Enhancement)
- Consolidated view of all analyses
- Interactive parameter adjustments
- Downloadable reports (CSV/Excel)
- Sensitivity analysis tables

## Technical Notes

### Data Sources
- **Stock Data**: Yahoo Finance (via yfinance library)
- **Credit Spreads**: Aswath Damodaran's dataset (manually updated)
- **Beta Calculation**: 5 years of monthly returns

### Calculation Methods
- **Beta**: OLS regression of excess stock returns vs excess market returns
- **Confidence Intervals**: Based on 95% CI of beta from regression
- **WACC Range**: Calculated using lower and upper beta confidence bounds

### Performance Considerations
- Data fetching occurs on button click (not cached)
- Each calculation makes fresh API calls to yfinance
- Typical response time: 5-10 seconds depending on network

## File Details

### app.py (Home Page)
- **Lines of Code**: ~160
- **Purpose**: Landing page with project overview and navigation
- **Components**: Phase cards, feature descriptions, getting started guide

### pages/1_WACC_Calculator.py
- **Lines of Code**: ~340
- **Key Functions**:
  - `get_credit_spread()`: Lookup credit spread by rating
  - `get_stock_data()`: Fetch data from yfinance
  - `calculate_beta()`: OLS regression for beta calculation
- **Streamlit Components**: Sidebar, metrics, dataframes, charts, expandable sections

### pages/2_Historical_Analysis.py
- **Lines of Code**: ~420
- **Key Functions**:
  - `get_financial_data()`: Fetch all financial statements
  - `calculate_growth_and_margins()`: Compute growth rates and margins
  - `calculate_nwc()`: Net working capital calculation
  - `calculate_reinvestment()`: Reinvestment metrics
- **Streamlit Components**: Multiple sections with charts, tables, and statistical summaries

### pages/3_DCF_Model.py
- **Lines of Code**: ~690
- **Key Functions**:
  - `get_ltm_data()`: Fetch last twelve months revenue from quarterly data
  - `create_projection_dates()`: Generate projection dates matching fiscal year-end
  - `project_financials()`: Project all financial metrics
  - `discount_cash_flows()`: Calculate present values
  - `calculate_terminal_value()`: Gordon Growth Model calculation
  - `calculate_share_price()`: Derive share price from enterprise value
- **Streamlit Components**: Comprehensive sidebar inputs, 7 analysis sections with multiple visualizations

### requirements.txt
- 7 main dependencies
- All dependencies properly versioned
- Compatible with Python 3.13

## Credits

- **Original Notebooks**: Pigford-Cody DCF Analysis
- **Framework**: Streamlit
- **Data Provider**: Yahoo Finance
- **Credit Spreads**: Aswath Damodaran
- **Statistical Analysis**: statsmodels

## Version History

- **v3.0** (2025-12-04): Complete DCF Analysis Suite - All Phases Implemented
  - Implemented Phase 3: DCF Valuation Model
  - Complete share price valuation with terminal value
  - Sensitivity analysis with WACC confidence intervals
  - Historical price comparison visualization
  - Simple and Advanced projection modes
  - Comprehensive valuation summary and insights

- **v2.0** (2025-12-04): Multi-page application with Phase 2
  - Restructured as multi-page Streamlit app
  - Added home page with navigation
  - Implemented Phase 2: Historical Analysis
  - Complete historical financial metrics
  - Growth rates, margins, and reinvestment analysis

- **v1.0** (2025-12-02): Initial WACC calculator implementation
  - Complete WACC calculation with confidence intervals
  - Interactive web interface
  - Real-time data fetching
  - Fixed caching serialization issue

## Contact & Support

For questions or issues with this application, refer to:
- Streamlit Documentation: https://docs.streamlit.io/
- yfinance Documentation: https://pypi.org/project/yfinance/
- Original notebook files in this directory
