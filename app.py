import sys
import traceback
import yfinance as yf
import pandas as pd
from datetime import datetime, date, timedelta

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QDoubleSpinBox, QDateEdit, QPushButton, 
    QTextEdit, QSplitter, QMessageBox, QGroupBox, QFormLayout
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QDate
from PyQt6.QtGui import QFont

import matplotlib
matplotlib.use('qtagg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

class AnalyzerWorker(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, ticker, capital, tax_rate, start_date, end_date):
        super().__init__()
        self.ticker = ticker
        self.capital = capital
        self.tax_rate = tax_rate
        self.start_date = start_date
        self.end_date = end_date

    def run(self):
        try:
            ticker = self.ticker.strip().upper()
            if not ticker:
                self.error.emit("Please enter a valid ticker.")
                return

            t = yf.Ticker(ticker)
            hist = t.history(start=self.start_date, end=self.end_date)
            
            if hist.empty:
                self.error.emit(f"No data found for ticker {ticker} in the selected date range.")
                return

            divs = t.dividends

            if hist.index.tz is not None:
                hist.index = hist.index.tz_localize(None)

            if not divs.empty:
                if divs.index.tz is not None:
                    divs.index = divs.index.tz_localize(None)
                sd = pd.to_datetime(self.start_date)
                ed = pd.to_datetime(self.end_date)
                divs = divs[(divs.index >= sd) & (divs.index <= ed)]

            df = pd.DataFrame({'close': hist['Close']})
            div_series = pd.Series(dtype=float)
            if not divs.empty:
                divs.index = divs.index.normalize()
                div_series = divs

            df.index = df.index.normalize()
            df = df.groupby(df.index).last()
            
            if not div_series.empty:
                div_series = div_series.groupby(div_series.index).sum()

            df['dividend'] = div_series
            df['dividend'] = df['dividend'].fillna(0.0)
            df = df.sort_index()

            drip_shares = self.capital / df['close'].iloc[0]
            drip_value_history = []
            drip_dividends_total = 0.0
            drip_tax_total = 0.0

            nodrip_shares = self.capital / df['close'].iloc[0]
            nodrip_cash = 0.0
            nodrip_value_history = []
            nodrip_dividends_total = 0.0
            nodrip_tax_total = 0.0

            dates = []

            for dt, row in df.iterrows():
                price = row['close']
                div_per_share = row['dividend']

                if div_per_share > 0:
                    gross_div_drip = drip_shares * div_per_share
                    tax_drip = gross_div_drip * self.tax_rate
                    net_div_drip = gross_div_drip - tax_drip
                    drip_dividends_total += gross_div_drip
                    drip_tax_total += tax_drip
                    drip_shares += net_div_drip / price

                    gross_div_nodrip = nodrip_shares * div_per_share
                    tax_nodrip = gross_div_nodrip * self.tax_rate
                    net_div_nodrip = gross_div_nodrip - tax_nodrip
                    nodrip_dividends_total += gross_div_nodrip
                    nodrip_tax_total += tax_nodrip
                    nodrip_cash += net_div_nodrip

                drip_value = drip_shares * price
                drip_value_history.append(drip_value)

                nodrip_value = nodrip_shares * price + nodrip_cash
                nodrip_value_history.append(nodrip_value)

                dates.append(dt)

            years = (df.index[-1] - df.index[0]).days / 365.25
            if years <= 0: years = 1

            final_drip_value = drip_value_history[-1]
            drip_cagr = ((final_drip_value / self.capital) ** (1 / years)) - 1
            drip_avg_yield = (drip_dividends_total / years) / self.capital

            final_nodrip_value = nodrip_value_history[-1]
            nodrip_cagr = ((final_nodrip_value / self.capital) ** (1 / years)) - 1
            nodrip_avg_yield = (nodrip_dividends_total / years) / self.capital

            result = {
                "ticker": ticker,
                "dates": dates,
                "dripHistory": drip_value_history,
                "nodripHistory": nodrip_value_history,
                "drip_cagr": drip_cagr,
                "nodrip_cagr": nodrip_cagr,
                "drip_final": final_drip_value,
                "nodrip_final": final_nodrip_value,
                "drip_divs": drip_dividends_total,
                "nodrip_divs": nodrip_dividends_total,
                "drip_tax": drip_tax_total,
                "nodrip_tax": nodrip_tax_total,
                "years": years
            }
            self.finished.emit(result)

        except Exception as e:
            self.error.emit(str(e) + "\n" + traceback.format_exc())

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ETF Dividend Analyzer")
        self.resize(1000, 700)
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        
        # Left Panel (Inputs)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_panel.setFixedWidth(300)
        
        input_group = QGroupBox("Simulation Parameters")
        form_layout = QFormLayout(input_group)
        
        self.ticker_input = QLineEdit("SPY")
        
        self.capital_input = QDoubleSpinBox()
        self.capital_input.setRange(100, 100000000)
        self.capital_input.setValue(10000)
        self.capital_input.setPrefix("$ ")
        
        self.tax_input = QDoubleSpinBox()
        self.tax_input.setRange(0, 100)
        self.tax_input.setValue(30.0)
        self.tax_input.setSuffix(" %")
        
        self.start_date_input = QDateEdit()
        self.start_date_input.setCalendarPopup(True)
        self.start_date_input.setDate(QDate.currentDate().addYears(-5))
        
        self.end_date_input = QDateEdit()
        self.end_date_input.setCalendarPopup(True)
        self.end_date_input.setDate(QDate.currentDate())
        
        form_layout.addRow("Ticker Symbol:", self.ticker_input)
        form_layout.addRow("Initial Capital:", self.capital_input)
        form_layout.addRow("Dividend Tax Rate:", self.tax_input)
        form_layout.addRow("Start Date:", self.start_date_input)
        form_layout.addRow("End Date:", self.end_date_input)
        
        self.run_btn = QPushButton("Run Analysis")
        self.run_btn.setFixedHeight(40)
        self.run_btn.clicked.connect(self.run_analysis)
        
        left_layout.addWidget(input_group)
        left_layout.addWidget(self.run_btn)
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setFont(QFont("Consolas", 10))
        left_layout.addWidget(QLabel("Metrics:"))
        left_layout.addWidget(self.results_text)
        
        # Right Panel (Chart)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        self.canvas = MplCanvas(self, width=6, height=5, dpi=100)
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        right_layout.addWidget(self.toolbar)
        right_layout.addWidget(self.canvas)
        
        layout.addWidget(left_panel)
        layout.addWidget(right_panel)
        
        self.worker = None

    def run_analysis(self):
        ticker = self.ticker_input.text()
        capital = self.capital_input.value()
        tax_rate = self.tax_input.value() / 100.0
        start_date = self.start_date_input.date().toString("yyyy-MM-dd")
        end_date = self.end_date_input.date().toString("yyyy-MM-dd")
        
        self.run_btn.setEnabled(False)
        self.run_btn.setText("Fetching Data...")
        self.results_text.clear()
        
        self.worker = AnalyzerWorker(ticker, capital, tax_rate, start_date, end_date)
        self.worker.finished.connect(self.on_analysis_finished)
        self.worker.error.connect(self.on_analysis_error)
        self.worker.start()

    def on_analysis_finished(self, res):
        self.run_btn.setEnabled(True)
        self.run_btn.setText("Run Analysis")
        
        # Update Plot
        self.canvas.ax.clear()
        self.canvas.ax.plot(res["dates"], res["dripHistory"], label="DRIP (Reinvested)", color="blue", linewidth=2)
        self.canvas.ax.plot(res["dates"], res["nodripHistory"], label="Non-DRIP (Cash Out)", color="red", linewidth=2)
        
        self.canvas.ax.set_title(f"{res['ticker']} Dividend Reinvestment Analysis", fontsize=12)
        self.canvas.ax.set_xlabel("Date")
        self.canvas.ax.set_ylabel("Portfolio Value ($)")
        self.canvas.ax.legend()
        self.canvas.ax.grid(True, linestyle='--', alpha=0.7)
        
        self.canvas.fig.tight_layout()
        self.canvas.draw()
        
        # Update Metrics
        metrics = f"""
=== {res['ticker']} Analysis ===
Years Analyzed: {res['years']:.2f}

[ DRIP Strategy ]
Final Value: ${res['drip_final']:,.2f}
CAGR: {res['drip_cagr']*100:.2f}%
Gross Dividends: ${res['drip_divs']:,.2f}
Tax Paid: ${res['drip_tax']:,.2f}

[ Non-DRIP Strategy ]
Final Value: ${res['nodrip_final']:,.2f}
CAGR: {res['nodrip_cagr']*100:.2f}%
Gross Dividends: ${res['nodrip_divs']:,.2f}
Tax Paid: ${res['nodrip_tax']:,.2f}
"""
        self.results_text.setText(metrics.strip())

    def on_analysis_error(self, err_msg):
        self.run_btn.setEnabled(True)
        self.run_btn.setText("Run Analysis")
        QMessageBox.critical(self, "Error", f"Failed to analyze:\n{err_msg}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
