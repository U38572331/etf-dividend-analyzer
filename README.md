<div align="center">

# 📈 ETF Dividend Analyzer

**A Professional Tool for Visualizing and Backtesting ETF Dividend Reinvestment Strategies**

[![Release](https://img.shields.io/github/v/release/U38572331/etf-dividend-analyzer?color=blue&label=Latest%20Release)](https://github.com/U38572331/etf-dividend-analyzer/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

## 📖 Project Overview

**ETF Dividend Analyzer** is a quantitative dashboard designed to help investors visualize the compounding power of dividend reinvestment plans (DRIP) compared to taking cash dividends. Built with Python and modern web technologies, it fetches real-time historical data to simulate total returns, CAGR, and tax implications over any custom time horizon.

Whether you're exploring the long-term potential of `SPY`, `SCHD`, or any other dividend-paying asset, this tool provides a clear, data-driven comparison.

## ✨ Key Features

- **📊 DRIP vs. Non-DRIP Comparison**: Side-by-side performance charting for dividend reinvestment vs. cash payouts.
- **📈 Real-Time Data Integration**: Powered by `yfinance` to fetch accurate historical prices and dividend distributions.
- **💰 Tax Adjustments**: Configurable tax rates to simulate net real-world returns.
- **⚡ Standalone Executable**: No Python installation required! Run the app locally with a single click.
- **🖥️ Clean UI/UX**: Interactive charts and responsive financial metrics dashboard.

## 🚀 Quick Start (For General Users)

You don't need to be a developer to use this tool! We provide a standalone `.exe` file for Windows users.

1. **Download the App**: 
   👉 **[Download Latest Release (EXE)](https://github.com/U38572331/etf-dividend-analyzer/releases/latest)**
2. **Run it**: Double-click `etf-dividend-analyzer.exe`. (A local web server will start).
3. **Analyze**: Open your browser and navigate to `http://127.0.0.1:5000` to start analyzing.

## 💻 Installation (For Developers)

If you prefer to run the project from source or want to modify the code:

```bash
# 1. Clone the repository
git clone https://github.com/U38572331/etf-dividend-analyzer.git
cd etf-dividend-analyzer

# 2. Install dependencies
pip install -r requirements.txt
# (Dependencies include: flask, yfinance, pandas, numpy)

# 3. Run the application
python app.py
```
*The app will be available at `http://127.0.0.1:5000`.*

## 📸 Screenshots

![Screenshot](screenshot.png)

## 🏗️ Architecture & Methodology
- **Backend**: Python / Flask
- **Data Pipeline**: `yfinance`, `pandas`, `numpy` handling time-series alignment and dividend filtering.
- **Frontend**: Vanilla HTML/JS/CSS with charting libraries (served statically).
- **Packaging**: PyInstaller for seamless Windows distribution.

---
*Developed for Quantitative Research & Portfolio Analysis.*
