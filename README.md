# ETF Dividend Analyzer

[![Release](https://img.shields.io/github/v/release/U38572331/etf-dividend-analyzer?color=blue&label=Release)](https://github.com/U38572331/etf-dividend-analyzer/releases)

## Overview

ETF Dividend Analyzer is a quantitative application for evaluating the compounding effects of dividend reinvestment plans (DRIP) versus cash distribution strategies. The system integrates historical market data to calculate and compare total returns, Compound Annual Growth Rate (CAGR), and net asset values under configurable tax assumptions.

## Download

A pre-compiled Windows executable is available for deployment without a local Python environment.

[Download Latest Release (Executable)](https://github.com/U38572331/etf-dividend-analyzer/releases/latest)

## Core Functionality

- **Quantitative Comparison**: Side-by-side backtesting of DRIP and non-DRIP strategies.
- **Market Data Integration**: Real-time historical price and dividend distribution retrieval via `yfinance`.
- **Tax Adjusted Modeling**: Configurable dividend tax rate parameters for accurate net return simulation.
- **Data Visualization**: Interactive charting for historical portfolio valuation.

## System Requirements and Installation

For source code execution and development:

```bash
git clone https://github.com/U38572331/etf-dividend-analyzer.git
cd etf-dividend-analyzer
pip install -r requirements.txt
python app.py
```

## Architecture

- **Backend**: Python, Flask
- **Data Processing**: Pandas, NumPy, yfinance
- **Frontend**: HTML, CSS, JavaScript
- **Distribution**: PyInstaller

## Documentation

![System Interface](screenshot.png)

---
*Developed for Quantitative Research & Portfolio Analysis.*
