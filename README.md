# 📊 DCF Analysis Suite

A comprehensive web-based financial analysis toolkit for Discounted Cash Flow (DCF) valuation. Built with Streamlit and powered by real-time data from Yahoo Finance.

![Python](https://img.shields.io/badge/python-3.13-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.51-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🚀 Features

### Phase 1: WACC Calculator
Calculate the Weighted Average Cost of Capital for any publicly traded company.

- **Capital Structure Analysis** - Market cap and debt breakdown
- **Beta Calculation** - OLS regression using 5 years of monthly data
- **Cost of Equity** - CAPM methodology with confidence intervals
- **Cost of Debt** - Credit spread lookup from Damodaran data
- **WACC Estimation** - Complete calculation with sensitivity analysis

### Phase 2: Historical Analysis
Analyze historical financial performance and key valuation metrics.

- **Revenue & EBIT Metrics** - Historical trends and growth rates
- **Profit Margins** - Gross, EBIT, and EBITDA margins over time
- **Working Capital** - NWC calculation and changes
- **Reinvestment Analysis** - CapEx, D&A, and reinvestment rates
- **Statistical Summary** - Comprehensive historical insights

### Phase 3: DCF Valuation Model
Complete DCF valuation with projected cash flows and share price estimation.

- **LTM Data Foundation** - Last twelve months revenue starting point
- **Flexible Projections** - 5-15 year customizable forecasts
- **Cash Flow Modeling** - Revenue → EBIT → NOPAT → FCF
- **Terminal Value** - Gordon Growth Model
- **Share Price Valuation** - Complete enterprise and equity value calculation
- **Sensitivity Analysis** - WACC-based price ranges with historical comparison

## 🎯 Live Demo

Access the application at: `http://localhost:8501` after installation

## 📦 Installation

### Prerequisites
- Python 3.13+ (or 3.8+)
- pip package manager

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/dcf-analysis-suite.git
cd dcf-analysis-suite
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the application**
```bash
streamlit run app.py
```

4. **Open in browser**
Navigate to `http://localhost:8501`

## 🛠️ Technology Stack

- **Framework**: Streamlit 1.51
- **Data Source**: Yahoo Finance (yfinance API)
- **Statistical Analysis**: statsmodels
- **Visualization**: matplotlib, seaborn
- **Data Processing**: pandas, numpy

## 📖 Usage

### Quick Start

1. **Navigate to a tool** using the sidebar menu
2. **Enter a ticker symbol** (e.g., MSFT, AAPL, GOOGL)
3. **Configure parameters** according to your analysis needs
4. **Click Calculate** to see results with interactive visualizations

### Example Workflow

1. Start with **WACC Calculator** to determine cost of capital
2. Review **Historical Analysis** to understand company trends
3. Use **DCF Model** with WACC from Phase 1 and insights from Phase 2
4. Get complete valuation with implied share price

## 📁 Project Structure

```
dcf-analysis-suite/
├── app.py                              # Home page
├── pages/
│   ├── 1_WACC_Calculator.py           # Phase 1: WACC
│   ├── 2_Historical_Analysis.py       # Phase 2: Historical
│   └── 3_DCF_Model.py                 # Phase 3: DCF
├── requirements.txt                    # Dependencies
├── .gitignore                          # Git ignore rules
├── README.md                           # This file
├── claude.md                           # Detailed documentation
└── dcf*.py                             # Original notebook files
```

## 🔬 Methodology

### WACC Formula
```
WACC = wE × kE + wD × kD × (1-t)
```

Where:
- **wE** = Equity weight
- **kE** = Cost of equity (CAPM: rf + β × EMRP)
- **wD** = Debt weight
- **kD** = Cost of debt (rf + credit spread)
- **t** = Tax rate

### DCF Valuation
```
Enterprise Value = Σ PV(FCF) + PV(Terminal Value)
Share Price = (EV - Net Debt) / Shares Outstanding
```

## 📊 Example Companies

Try these tickers to see the tools in action:
- **MSFT** - Microsoft (default)
- **AAPL** - Apple
- **GOOGL** - Alphabet
- **TSLA** - Tesla
- **JPM** - JPMorgan Chase

## ⚠️ Disclaimer

This tool is for educational and analytical purposes only. Always conduct thorough due diligence and consult with financial professionals before making investment decisions.

DCF models are sensitive to assumptions. Results should be:
- Compared with peer multiples
- Stress-tested with different scenarios
- Updated as new information becomes available

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Data**: Yahoo Finance via yfinance library
- **Credit Spreads**: Aswath Damodaran's dataset
- **Framework**: Streamlit team
- **Original Notebooks**: Pigford-Cody DCF Analysis

## 📞 Contact

For questions or feedback, please open an issue on GitHub.

---

**Built with ❤️ using Streamlit and Python**
