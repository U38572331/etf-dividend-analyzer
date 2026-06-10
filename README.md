# ETF Dividend Analyzer

[![Release](https://img.shields.io/github/v/release/U38572331/etf-dividend-analyzer?color=blue&label=Release)](https://github.com/U38572331/etf-dividend-analyzer/releases)

[English](#overview) | [繁體中文](#系統概述)

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

- **Frontend/GUI**: PyQt6
- **Data Processing**: Pandas, NumPy, yfinance
- **Visualization**: Matplotlib
- **Distribution**: PyInstaller

## Documentation

![System Interface](screenshot.png)

---

# ETF 股息分析系統 (ETF Dividend Analyzer)

## 系統概述

ETF Dividend Analyzer 是一個量化分析應用程式，專門用於評估股息再投資計畫 (DRIP) 與現金分配策略的複利效應。本系統整合歷史市場數據，在可設定的稅務假設下，計算並比較總報酬率、年化報酬率 (CAGR) 以及淨資產價值。

## 檔案下載

我們提供已編譯的 Windows 執行檔，無需在本地端建立 Python 環境即可部署。

[下載最新版本 (執行檔)](https://github.com/U38572331/etf-dividend-analyzer/releases/latest)

## 核心功能

- **量化比較**：並排回測 DRIP 與非 DRIP 策略的歷史績效。
- **市場數據整合**：透過 `yfinance` 即時獲取歷史價格與股息分配紀錄。
- **稅務調整模型**：提供可設定的股息稅率參數，以準確模擬淨報酬。
- **數據視覺化**：提供互動式圖表以呈現歷史投資組合估值。

## 系統需求與安裝

若需執行原始碼或進行二次開發：

```bash
git clone https://github.com/U38572331/etf-dividend-analyzer.git
cd etf-dividend-analyzer
pip install -r requirements.txt
python app.py
```

## 系統架構

- **前端介面**: PyQt6
- **資料處理**: Pandas, NumPy, yfinance
- **數據視覺化**: Matplotlib
- **封裝發佈**: PyInstaller

## 系統介面

![System Interface](screenshot.png)

---
*Developed for Quantitative Research & Portfolio Analysis.*
